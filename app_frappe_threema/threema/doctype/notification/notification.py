# Copyright (c) 2024, Centura AG and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.email.doctype.notification.notification import Notification


class CustomNotification(Notification):
	def send(self, doc):
		context = {"doc": doc, "alert": self, "comments": None}
		if doc.get("_comments"):
			context["comments"] = json.loads(doc.get("_comments"))

		if super.is_standard:
			super.load_standard_properties(context)
		try:
			if super.channel == "Email":
				super.send_an_email(doc, context)

			if super.channel == "Slack":
				super.send_a_slack_msg(doc, context)

			if super.channel == "SMS":
				super.send_sms(doc, context)

			if super.channel == "System Notification" or super.send_system_notification:
				super.create_system_notification(doc, context)

		except Exception:
			super.log_error("Failed to send Notification")

		if super.set_property_after_alert:
			allow_update = True
			if (
					doc.docstatus.is_submitted()
					and not doc.meta.get_field(self.set_property_after_alert).allow_on_submit
			):
				allow_update = False
			try:
				if allow_update and not doc.flags.in_notification_update:
					fieldname = super.set_property_after_alert
					value = super.property_value
					if doc.meta.get_field(fieldname).fieldtype in frappe.model.numeric_fieldtypes:
						value = frappe.utils.cint(value)

					doc.reload()
					doc.set(fieldname, value)
					doc.flags.updater_reference = {
						"doctype": super.doctype,
						"docname": super.name,
						"label": _("via Notification"),
					}
					doc.flags.in_notification_update = True
					doc.save(ignore_permissions=True)
					doc.flags.in_notification_update = False
			except Exception:
				super.log_error("Document update failed")

