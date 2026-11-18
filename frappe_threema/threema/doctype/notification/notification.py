# Copyright (c) 2024, Centura AG and contributors
# For license information, please see license.txt

import frappe


class ThreemaNotificationMixin:
	"""Sends Notifications with the channel "Threema" through the Threema Gateway."""

	def send_notification_by_channel(self, doc, context) -> None:
		if self.channel == "Threema":
			try:
				self._send_threema_msg(doc, context)
			except Exception:
				self.log_error("Failed to send Threema Notification")
			if self.send_system_notification:
				self.create_system_notification(doc, context)
		else:
			super().send_notification_by_channel(doc, context)

	def _send_threema_msg(self, doc, context) -> None:
		from frappe_threema.api import send_message

		send_message(
			receiver_list=self.get_receiver_list(doc, context),
			# written by a System Manager and rendered with the safe globals, like Frappe's own channels
			msg=frappe.render_template(  # nosemgrep: frappe-semgrep-rules.rules.security.frappe-ssti
				self.message, context, restrict_globals=True
			),
			success_msg=False,
		)
