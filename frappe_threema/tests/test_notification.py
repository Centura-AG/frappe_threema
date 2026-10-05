from unittest.mock import patch

import frappe
from frappe.email.doctype.notification.notification import Notification
from frappe.tests import IntegrationTestCase

from frappe_threema.setup import after_install, after_migrate
from frappe_threema.setup.notification import add_threema_notification_channel


def channel_options():
	return frappe.get_meta("Notification").get_field("channel").options.split("\n")


class TestThreemaNotification(IntegrationTestCase):
	def notification(self, channel="Threema", system_notification=0):
		doc = frappe.new_doc("Notification")
		doc.channel = channel
		doc.message = "Hello {{ doc.name }}"
		doc.send_system_notification = system_notification
		return doc

	def test_threema_channel_sends_rendered_message(self):
		doc = self.notification()
		with (
			patch.object(type(doc), "get_receiver_list", return_value=["ABCD1234"]),
			patch("frappe_threema.api.send_message") as send,
		):
			doc.send_notification_by_channel(frappe._dict(name="X-1"), {"doc": frappe._dict(name="X-1")})
		send.assert_called_once_with(receiver_list=["ABCD1234"], msg="Hello X-1", success_msg=False)

	def test_threema_errors_are_logged_and_system_notification_created(self):
		doc = self.notification(system_notification=1)
		with (
			patch.object(type(doc), "_send_threema_msg", side_effect=Exception("down")),
			patch.object(type(doc), "log_error") as log_error,
			patch.object(type(doc), "create_system_notification") as system_notification,
		):
			doc.send_notification_by_channel(frappe._dict(), {})
		log_error.assert_called_once()
		system_notification.assert_called_once()

	def test_other_channels_use_core_behaviour(self):
		doc = self.notification(channel="Email")
		with patch.object(Notification, "send_notification_by_channel") as core:
			doc.send_notification_by_channel(frappe._dict(), {})
		core.assert_called_once()


class TestNotificationChannelSetup(IntegrationTestCase):
	def test_adds_threema_channel_once(self):
		frappe.db.delete("Property Setter", {"doc_type": "Notification", "field_name": "channel"})
		frappe.clear_cache(doctype="Notification")
		self.assertNotIn("Threema", channel_options())

		after_install()
		frappe.clear_cache(doctype="Notification")
		self.assertIn("Threema", channel_options())

		after_migrate()
		add_threema_notification_channel()
		self.assertEqual(
			frappe.db.count("Property Setter", {"doc_type": "Notification", "field_name": "channel"}), 1
		)
