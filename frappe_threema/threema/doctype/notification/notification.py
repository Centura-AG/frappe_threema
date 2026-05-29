# Copyright (c) 2024, Centura AG and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ThreemaNotificationMixin(Document):
    def send_notification_by_channel(self, doc, context):
        if self.channel == "Threema":
            try:
                self._send_threema_msg(doc, context)
            except Exception:
                self.log_error("Failed to send Threema Notification")
        else:
            super().send_notification_by_channel(doc, context)

    def _send_threema_msg(self, doc, context):
        from frappe_threema.api import send_message

        send_message(
            receiver_list=self.get_receiver_list(doc, context),
            msg=frappe.render_template(self.message, context),
        )
