import json
import re

import frappe
from frappe import _
from frappe.utils import now_datetime, sbool


_RECIPIENT_STRIP_CHARS = str.maketrans("", "", " -()")
_IDENTITY_RE = re.compile(r"[A-Za-z0-9]{8}")
_PHONE_RE = re.compile(r"\+?\d{1,15}")
_EMAIL_RE = re.compile(r"^[\w.\-]+@[\w.\-]+\.\w+$")


@frappe.whitelist()
def send_message(
    receiver_list: list[str] | str, msg: str, success_msg: bool = True
) -> None:
    if isinstance(receiver_list, str):
        receiver_list = json.loads(receiver_list)
    if not isinstance(receiver_list, list):
        receiver_list = [receiver_list]

    receiver_list = _validate_receivers(receiver_list)

    if not frappe.db.get_single_value("Threema Settings", "gateway_url"):
        frappe.msgprint(_("Please update Threema Settings"))
        return

    _send_via_gateway(receiver_list, frappe.safe_decode(msg), sbool(success_msg))


def _validate_receivers(receiver_list: list[str]) -> list[str]:
    cleaned = [r.translate(_RECIPIENT_STRIP_CHARS) for r in receiver_list if r]
    cleaned = [r for r in cleaned if r]
    if not cleaned:
        frappe.throw(_("Please enter valid threema nos"))
    return cleaned


def _send_via_gateway(receivers: list[str], message: str, success_msg: bool) -> None:
    ts = frappe.get_doc("Threema Settings", "Threema Settings")
    headers = {"Accept": "text/plain, text/html, */*"}

    base_payload: dict = {"text": message}
    if ts.get("from"):
        base_payload["from"] = ts.get("from")
    if ts.get("secret"):
        base_payload["secret"] = ts.get_password("secret")

    success_list = []
    for contact in receivers:
        try:
            specifier = _get_recipient_specifier(contact)
        except frappe.ValidationError:
            frappe.log_error(
                title="Threema invalid recipient",
                message=f"Skipping invalid contact: {contact}",
            )
            continue
        payload = {**base_payload, specifier: contact}
        if _send_request(ts.gateway_url, payload, headers):
            success_list.append(contact)

    if success_list:
        _create_log(message, success_list)
        if success_msg:
            frappe.msgprint(
                _("Threema Message sent to : {0}").format(", ".join(success_list))
            )


def _send_request(gateway_url: str, payload: dict, headers: dict) -> bool:
    import requests

    try:
        response = requests.post(gateway_url, data=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        frappe.log_error(title="Threema send failed", message=str(e))
        return False


def _get_recipient_specifier(contact: str) -> str:
    if _IDENTITY_RE.fullmatch(contact):
        return "to"
    if _PHONE_RE.fullmatch(contact):
        return "phone"
    if _EMAIL_RE.match(contact):
        return "email"
    raise frappe.ValidationError(
        _("This is not a valid identity nor phone number nor email: {0}").format(
            contact
        )
    )


def _create_log(message: str, sent_to: list[str]) -> None:
    doc = frappe.new_doc("Threema Message Log")
    doc.sent_at = now_datetime()
    doc.message = message
    doc.sender = frappe.session.user
    doc.recipient = "\n".join(sent_to)
    doc.flags.ignore_permissions = True
    doc.save()
