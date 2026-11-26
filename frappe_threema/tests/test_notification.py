from unittest.mock import patch

import frappe
from frappe.email.doctype.notification.notification import Notification
from frappe.tests import IntegrationTestCase

from frappe_threema.setup import after_install, after_migrate
from frappe_threema.setup.notification import (
	THREEMA_SYSTEM_NOTIFICATION,
	add_threema_notification_channel,
	setup_threema_system_notification_title,
)


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

	def test_threema_message_is_rendered_with_restricted_globals(self):
		doc = self.notification()
		with (
			patch.object(type(doc), "get_receiver_list", return_value=["ABCD1234"]),
			patch("frappe_threema.api.send_message"),
			patch("frappe.render_template", return_value="Hello") as render,
		):
			doc.send_notification_by_channel(frappe._dict(name="X-1"), {"doc": frappe._dict(name="X-1")})
		self.assertIs(render.call_args.kwargs.get("restrict_globals"), True)

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

	def test_system_notification_title_comes_from_subject(self):
		doc = self.notification(system_notification=1)
		doc.subject = "Order {{ doc.name }}"
		target = frappe.get_doc({"doctype": "ToDo", "description": "Muster Handels AG"})
		target.name = "X-1"
		with (
			patch.object(type(doc), "_send_threema_msg"),
			patch.object(type(doc), "get_list_of_recipients", return_value=(["Administrator"], [], [])),
			patch("frappe.email.doctype.notification.notification.enqueue_create_notification") as enqueue,
		):
			doc.send_notification_by_channel(target, {"doc": target})
		self.assertEqual(enqueue.call_args.args[1]["title"], "Order X-1")

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


def subject_depends_on_setters():
	return frappe.db.count(
		"Property Setter", {"doc_type": "Notification", "field_name": "subject", "property": "depends_on"}
	)


def drop_notification_title_column():
	frappe.db.sql_ddl("alter table `tabNotification` drop column `notification_title`")
	frappe.client_cache.delete_value("table_columns::tabNotification")


class TestThreemaSystemNotificationTitle(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		cls.title_field_removed = not frappe.get_meta("Notification").has_field("notification_title")
		if cls.title_field_removed and not frappe.db.has_column("Notification", "notification_title"):
			frappe.db.sql_ddl("alter table `tabNotification` add column `notification_title` varchar(140)")
			frappe.client_cache.delete_value("table_columns::tabNotification")
			cls.addClassCleanup(drop_notification_title_column)
		super().setUpClass()

	def test_subject_shown_for_threema_system_notification(self):
		frappe.db.delete("Property Setter", {"doc_type": "Notification", "field_name": "subject"})
		frappe.clear_cache(doctype="Notification")

		setup_threema_system_notification_title()
		setup_threema_system_notification_title()
		frappe.clear_cache(doctype="Notification")

		depends_on = frappe.get_meta("Notification").get_field("subject").depends_on or ""
		if self.title_field_removed:
			self.assertIn(THREEMA_SYSTEM_NOTIFICATION, depends_on)
			self.assertEqual(subject_depends_on_setters(), 1)
		else:
			self.assertNotIn(THREEMA_SYSTEM_NOTIFICATION, depends_on)
			self.assertEqual(subject_depends_on_setters(), 0)

	def test_old_notification_title_is_copied_into_empty_subject(self):
		if not self.title_field_removed:
			self.skipTest("Notification still has notification_title")

		names = {}
		for channel, subject in (("Threema", ""), ("Threema", "Kept"), ("Email", "")):
			doc = frappe.new_doc("Notification")
			doc.name = f"Threema title test {len(names)}"
			doc.update({"channel": channel, "subject": subject, "document_type": "ToDo", "event": "New"})
			doc.db_insert()
			names[doc.name] = subject
		frappe.db.sql(
			"update `tabNotification` set notification_title = 'Muster Handels AG' where name in %s",
			(tuple(names),),
		)

		setup_threema_system_notification_title()

		subjects = [frappe.db.get_value("Notification", name, "subject") or "" for name in names]
		self.assertEqual(subjects, ["Muster Handels AG", "Kept", ""])
