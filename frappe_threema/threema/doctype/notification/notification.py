# Copyright (c) 2024, Centura AG and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.core.doctype.role.role import get_info_based_on_role, get_user_info
from frappe.email.doctype.notification.notification import Notification
from frappe_threema.threema.doctype.threema_settings.threema_settings import send_message

class CustomNotification(Notification):
	def send_threema_msg(self, doc, context):
		send_message(
			receiver_list=super().get_receiver_list(doc, context, "mobile_no", super().get_mobile_no),
			msg=frappe.render_template(self.message, context),
		)

	def send(self, doc):
		if self.channel != "Threema":
			return super().send(doc)

		context = {"doc": doc, "alert": self, "comments": None}
		if doc.get("_comments"):
			context["comments"] = json.loads(doc.get("_comments"))

		self.send_threema_msg(doc, context)


