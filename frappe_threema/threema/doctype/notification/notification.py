# Copyright (c) 2024, Centura AG and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.core.doctype.role.role import get_info_based_on_role, get_user_info
from frappe.email.doctype.notification.notification import Notification
from frappe_threema.threema.doctype.threema_settings.threema_settings import send_message

class CustomNotification(Notification):
	def get_threema_receiver_list(self, doc, context):
		"""return receiver list based on the doc field and role specified"""
		receiver_list = []
		recipients = frappe.db.get_list("Notification Recipient", filters={ "parent": self.name})
		for recipient_name in recipients:
			recipient = frappe.get_doc('Notification Recipient', recipient_name)
			if recipient.condition:
				if not frappe.safe_eval(recipient.condition, None, context):
					continue
			# For sending messages to the owner's mobile phone number
			if recipient.receiver_by_document_field == "owner":
				owner = [dict(user_name=doc.get("owner"))]
				mobile_info = get_user_info(owner, "mobile_no")
				email_info = get_user_info(owner, "email")

				if len(mobile_info) > 0 and bool(mobile_info[0].strip()):
					receiver_list.append(mobile_info[0])
				# Check if email_info has at least one element
				elif len(email_info) > 0 and bool(email_info[0].strip()):
					receiver_list.append(email_info[0])

			# For sending messages to the contact specified in the receiver field
			elif recipient.receiver_by_document_field:
				receiver_list.append(doc.get(recipient.receiver_by_document_field))

			# For sending messages to specified role
			if recipient.receiver_by_role:
				mobile_no = get_info_based_on_role(
					recipient.receiver_by_role, "mobile_no", ignore_permissions=True
				)[0]
				email = get_info_based_on_role(
					recipient.receiver_by_role, "email", ignore_permissions=True
				)[0]

				if bool(mobile_no and mobile_no.strip()):
					receiver_list.append(mobile_no)
				elif bool(email and email.strip()):
					receiver_list.append(email)

		return receiver_list

	def send_threema_msg(self, doc, context):
		send_message(
			receiver_list=self.get_threema_receiver_list(doc, context),
			msg=frappe.render_template(self.message, context),
		)

	def send(self, doc):
		if self.channel != "Threema":
			return super().send(doc)

		context = {"doc": doc, "alert": self, "comments": None}
		if doc.get("_comments"):
			context["comments"] = json.loads(doc.get("_comments"))

		self.send_threema_msg(doc, context)


