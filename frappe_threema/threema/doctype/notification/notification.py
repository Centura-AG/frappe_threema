# Copyright (c) 2024, Centura AG and contributors
# For license information, please see license.txt

import frappe


class ThreemaNotificationMixin:
	def send_notification_by_channel(self, doc, context):
		if self.channel == "Threema":
			try:
				self._send_threema_msg(doc, context)
			except Exception:
				self.log_error("Failed to send Threema Notification")
			if self.send_system_notification:
				self.create_system_notification(doc, context)
		else:
			super().send_notification_by_channel(doc, context)

	def _send_threema_msg(self, doc, context):
		from frappe_threema.api import send_message

		send_message(
			receiver_list=self.get_receiver_list(doc, context),
			msg=frappe.render_template(self.message, context),
			success_msg=False,
		)
