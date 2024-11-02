# Copyright (c) 2024, Centura AG and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint, throw
from frappe.model.document import Document
from frappe.utils import now_datetime


class ThreemaSettings(Document):
	pass

def validate_receiver_nos(receiver_list):
	validated_receiver_list = []
	for d in receiver_list:
		if not d:
			continue

		# remove invalid character
		for x in [" ", "-", "(", ")"]:
			d = d.replace(x, "")

		validated_receiver_list.append(d)

	if not validated_receiver_list:
		throw(_("Please enter valid threema nos"))

	return validated_receiver_list


@frappe.whitelist()
def send_message(receiver_list, msg, success_msg=True):
		import json

		if isinstance(receiver_list, str):
			receiver_list = json.loads(receiver_list)
			if not isinstance(receiver_list, list):
				receiver_list = [receiver_list]

		receiver_list = validate_receiver_nos(receiver_list)

		arg = {
			"receiver_list": receiver_list,
			"message": frappe.safe_decode(msg).encode("utf-8"),
			"success_msg": success_msg,
		}

		if frappe.db.get_single_value("Threema Settings", "gateway_url"):
			send_via_gateway(arg)
		else:
			msgprint(_("Please Update Threema Settings"))

def send_via_gateway(arg):
	ts = frappe.get_doc("Threema Settings", "Threema Settings")
	headers = get_headers()

	message = frappe.safe_decode(arg.get("message"))
	args = {"text": message}
	if ts.get("from"):
		args["from"] = ts.get("from")

	if ts.get("secret"):
		args["secret"] = ts.get_password("secret")

	success_list = []
	for d in arg.get("receiver_list"):
		args["phone"] = d
		status = send_request(ts.gateway_url, args, headers)
		if 200 <= status < 300:
			success_list.append(d)

	if len(success_list) > 0:
		args.update(arg)
		create_log(args, success_list)
		if arg.get("success_msg"):
			frappe.msgprint(_("Threema Message sent to : {0}").format("\n" + "\n".join(success_list)))


def get_headers():
	headers = {"Accept": "text/plain, text/html, */*"}
	return headers

def send_request(gateway_url, args, headers=None):
	import requests

	if not headers:
		headers = get_headers()
	kwargs = {"headers": headers}
	kwargs["data"] = args
	response = requests.post(gateway_url, **kwargs)

	response.raise_for_status()
	return response.status_code


# Create Log
# =========================================================
def create_log(args, sent_to):
	sl = frappe.new_doc("Threema Message Log")
	sl.sent_at = now_datetime()
	sl.message = args["text"]
	sl.sender = frappe.session.user
	sl.recipient = "\n".join(args["receiver_list"])
	sl.flags.ignore_permissions = True
	sl.save()

