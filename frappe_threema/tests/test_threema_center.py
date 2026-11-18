from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase

from frappe_threema.threema.doctype.threema_center import threema_center


class TestThreemaCenter(IntegrationTestCase):
	def center(self, receiver_list=None, message=None):
		doc = frappe.get_single("Threema Center")
		doc.receiver_list = receiver_list
		doc.message = message
		return doc

	def test_sends_to_parsed_receivers(self):
		doc = self.center("Max - ABCD1234\n\n+41791234567 \n", "Hello")
		with patch.object(threema_center, "send_message") as send:
			doc.send_message()
		send.assert_called_once_with(["ABCD1234", "+41791234567"], "Hello")

	def test_keeps_dashes_inside_phone_numbers_and_emails(self):
		doc = self.center("+41 79 123-45-67\nanne-marie@example.com\nMax Muster - +41 79 765-43-21", "Hello")
		with patch.object(threema_center, "send_message") as send:
			doc.send_message()
		send.assert_called_once_with(
			["+41 79 123-45-67", "anne-marie@example.com", "+41 79 765-43-21"], "Hello"
		)

	def test_requires_message(self):
		doc = self.center("ABCD1234")
		with (
			patch.object(threema_center, "send_message") as send,
			patch.object(frappe, "msgprint") as msgprint,
		):
			doc.send_message()
		send.assert_not_called()
		msgprint.assert_called_once()

	def test_requires_receivers(self):
		doc = self.center(" \n ", "Hello")
		with (
			patch.object(threema_center, "send_message") as send,
			patch.object(frappe, "msgprint") as msgprint,
		):
			doc.send_message()
		send.assert_not_called()
		msgprint.assert_called_once()
