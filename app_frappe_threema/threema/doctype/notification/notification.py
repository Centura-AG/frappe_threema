# Copyright (c) 2024, Centura AG and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.email.doctype.notification.notification import Notification
from app_frappe_threema.threema.doctype.threema_settings.threema_settings import send_message

class CustomNotification(Notification):
	def send_threema_msg(self, doc, context):
		send_message(
			receiver_list=self.get_receiver_list(doc, context),
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

