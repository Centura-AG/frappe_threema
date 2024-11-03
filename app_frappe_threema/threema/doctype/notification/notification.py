# Copyright (c) 2024, Centura AG and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.core.doctype.role.role import get_info_based_on_role, get_user_info
from frappe.email.doctype.notification.notification import Notification
from app_frappe_threema.threema.doctype.threema_settings.threema_settings import send_message

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
				threema_id = get_user_info(owner, "threema_id")[0]
				mobile_no = get_user_info(owner, "mobile_no")[0]
				email = get_user_info(owner, "email")[0]

				if bool(threema_id and threema_id.strip()):
					receiver_list.append(threema_id)
				elif bool(mobile_no and mobile_no.strip()):
					receiver_list.append(mobile_no)
				elif bool(email and email.strip()):
					receiver_list.append(email)

			# For sending messages to the contact specified in the receiver field
			elif recipient.receiver_by_document_field:
				receiver_list.append(doc.get(recipient.receiver_by_document_field))

			# For sending messages to specified role
			if recipient.receiver_by_role:
				threema_id = get_info_based_on_role(
					recipient.receiver_by_role, "threema_id", ignore_permissions=True
				)[0]
				mobile_no = get_info_based_on_role(
					recipient.receiver_by_role, "mobile_no", ignore_permissions=True
				)[0]
				email = get_info_based_on_role(
					recipient.receiver_by_role, "email", ignore_permissions=True
				)[0]

				if bool(threema_id and threema_id.strip()):
					receiver_list.append(threema_id)
				elif bool(mobile_no and mobile_no.strip()):
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
		context = {"doc": doc, "alert": self, "comments": None}
		if doc.get("_comments"):
			context["comments"] = json.loads(doc.get("_comments"))

		if self.is_standard:
			self.load_standard_properties(context)

		try:
			if self.channel == "Email":
				self.send_an_email(doc, context)

			if self.channel == "Slack":
				self.send_a_slack_msg(doc, context)

			if self.channel == "SMS":
				self.send_sms(doc, context)

			if self.channel == "Threema":
				self.send_threema_msg(doc, context)

			if self.channel == "System Notification" or self.send_system_notification:
				self.create_system_notification(doc, context)

		except Exception:
			self.log_error("Failed to send Notification")

		if self.set_property_after_alert:
			allow_update = True
			if (
					doc.docstatus.is_submitted()
					and not doc.meta.get_field(self.set_property_after_alert).allow_on_submit
			):
				allow_update = False
			try:
				if allow_update and not doc.flags.in_notification_update:
					fieldname = self.set_property_after_alert
					value = self.property_value
					if doc.meta.get_field(fieldname).fieldtype in frappe.model.numeric_fieldtypes:
						value = frappe.utils.cint(value)

					doc.reload()
					doc.set(fieldname, value)
					doc.flags.updater_reference = {
						"doctype": self.doctype,
						"docname": self.name,
						"label": _("via Notification"),
					}
					doc.flags.in_notification_update = True
					doc.save(ignore_permissions=True)
					doc.flags.in_notification_update = False
			except Exception:
				self.log_error("Document update failed")

