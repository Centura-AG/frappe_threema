import json
import re

import frappe
import requests
from frappe import _
from frappe.utils import now_datetime, sbool

_RECIPIENT_STRIP_CHARS = str.maketrans("", "", " -()")
_IDENTITY_RE = re.compile(r"[A-Za-z0-9]{8}")
_PHONE_RE = re.compile(r"\+?\d{1,15}")
_EMAIL_RE = re.compile(r"[\w.\-]+@[\w.\-]+\.\w+")


@frappe.whitelist()
def send_message(receiver_list: list[str] | str, msg: str, success_msg: bool = True) -> None:
	"""Send `msg` to each receiver (Threema ID, phone number or email) and log the delivered ones."""
	if isinstance(receiver_list, str):
		receiver_list = json.loads(receiver_list)
	if not isinstance(receiver_list, list):
		receiver_list = [receiver_list]

	receivers = _clean_receivers(receiver_list)

	if not frappe.db.get_single_value("Threema Settings", "gateway_url"):
		frappe.msgprint(_("Please update Threema Settings"))
		return

	_send_via_gateway(receivers, frappe.safe_decode(msg), sbool(success_msg))


def _clean_receivers(receiver_list: list[str]) -> list[str]:
	cleaned = [_clean_receiver(r) for r in receiver_list if r]
	cleaned = [r for r in cleaned if r]
	if not cleaned:
		frappe.throw(_("Please enter at least one valid Threema recipient"))
	return cleaned


def _clean_receiver(receiver: str) -> str:
	receiver = receiver.strip()
	if "@" in receiver:
		return receiver
	return receiver.translate(_RECIPIENT_STRIP_CHARS)


def _send_via_gateway(receivers: list[str], message: str, success_msg: bool) -> None:
	settings = frappe.get_single("Threema Settings")
	headers = {"Accept": "text/plain, text/html, */*"}

	base_payload = {"text": message}
	if settings.get("from"):
		base_payload["from"] = settings.get("from")
	if settings.get("secret"):
		base_payload["secret"] = settings.get_password("secret")

	delivered, failed = [], []
	for contact in receivers:
		try:
			specifier = _get_recipient_specifier(contact)
		except frappe.ValidationError:
			frappe.log_error(
				title="Threema invalid recipient", message=f"Skipping invalid contact: {contact}"
			)
			failed.append((contact, "invalid recipient, not sent to the gateway"))
			continue

		error = _send_request(settings.gateway_url, {**base_payload, specifier: contact}, headers)
		if error:
			failed.append((contact, error))
		else:
			delivered.append(contact)

	not_delivered = ", ".join(contact for contact, _error in failed)
	if not delivered:
		frappe.log_error(
			title="Threema send failed: no recipient received the message",
			message="\n".join(f"{contact}: {error}" for contact, error in failed),
		)
		if success_msg:
			frappe.msgprint(
				_("Threema message could not be sent to: {0}. The cause is in the Error Log.").format(
					not_delivered
				),
				indicator="red",
			)
		return

	_create_log(message, delivered)
	if success_msg:
		frappe.msgprint(_("Threema message sent to: {0}").format(", ".join(delivered)))
		if failed:
			frappe.msgprint(
				_("Threema message could not be sent to: {0}. The cause is in the Error Log.").format(
					not_delivered
				),
				indicator="orange",
			)


def _send_request(gateway_url: str, payload: dict, headers: dict) -> str | None:
	try:
		response = requests.post(gateway_url, data=payload, headers=headers, timeout=30)
		response.raise_for_status()
	except requests.RequestException as e:
		frappe.log_error(title="Threema send failed", message=str(e))
		return str(e)
	return None


def _get_recipient_specifier(contact: str) -> str:
	if _IDENTITY_RE.fullmatch(contact):
		return "to"
	if _PHONE_RE.fullmatch(contact):
		return "phone"
	if _EMAIL_RE.fullmatch(contact):
		return "email"
	raise frappe.ValidationError(
		_("{0} is not a valid Threema ID, phone number or email address").format(contact)
	)


def _create_log(message: str, sent_to: list[str]) -> None:
	log = frappe.new_doc("Threema Message Log")
	log.sent_at = now_datetime()
	log.message = message
	log.sender = frappe.session.user
	log.recipient = "\n".join(sent_to)
	log.insert(ignore_permissions=True)
