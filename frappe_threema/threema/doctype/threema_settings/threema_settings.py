# Copyright (c) 2024, Centura AG and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint, throw
from frappe.model.document import Document
from frappe.utils import now_datetime
import re

class ThreemaSettings(Document):
	pass

def validate_receiver_nos(receiver_list):
	validated_receiver_list = []

	for contact in receiver_list:
		if not contact:
			continue

		# remove invalid character
		for x in [" ", "-", "(", ")"]:
			contact = contact.replace(x, "")

		validated_receiver_list.append(contact)

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


	success_list = []
	for contact in arg.get("receiver_list"):
		threema_args = {"text": message}
		if ts.get("from"):
			threema_args["from"] = ts.get("from")

		if ts.get("secret"):
			threema_args["secret"] = ts.get_password("secret")

		threema_args[get_recipient_specifier(contact)] = contact
		status = send_request(ts.gateway_url, threema_args, headers)
		if 200 <= status < 300:
			success_list.append(contact)

	if len(success_list) > 0:
		threema_args.update(arg)
		create_log(threema_args, success_list)
		if arg.get("success_msg"):
			frappe.msgprint(_("Threema Message sent to : {0}").format(", ".join(success_list)))


def get_headers():
	headers = {"Accept": "text/plain, text/html, */*"}
	return headers

def send_request(gateway_url, threema_args, headers=None):
	import requests

	if not headers:
		headers = get_headers()
	kwargs = {"headers": headers}
	kwargs["data"] = threema_args
	response = requests.post(gateway_url, **kwargs)

	response.raise_for_status()
	return response.status_code


def get_recipient_specifier(contact):
	if is_valid_recipient_identity(contact):
		return "to"
	elif is_valid_phone_number(contact):
		return "phone"
	elif is_valid_email_address(contact):
		return "email"
	else:
		msgprint(_("This is not a valid indetity, phone number or email: " + contact))

def is_valid_recipient_identity(identity):
	# Check if the identity is exactly 8 alphanumeric characters
	return bool(re.fullmatch(r'[A-Za-z0-9]{8}', identity))

def is_valid_phone_number(phone):
	# Check if the phone number is in E.164 format, allowing an optional leading "+"
	return bool(re.fullmatch(r'\+?\d{1,15}', phone))

def is_valid_email_address(email):
	# Basic regular expression for validating an Email
	pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
	return bool(re.match(pattern, email))


def create_log(args, sent_to):
	sl = frappe.new_doc("Threema Message Log")
	sl.sent_at = now_datetime()
	sl.message = args["text"]
	sl.sender = frappe.session.user
	sl.recipient = "\n".join(args["receiver_list"])
	sl.flags.ignore_permissions = True
	sl.save()

