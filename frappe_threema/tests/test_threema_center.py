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
		doc = self.center(None, "Hello")
		with (
			patch.object(threema_center, "send_message") as send,
			patch.object(frappe, "msgprint") as msgprint,
		):
			doc.send_message()
		send.assert_not_called()
		msgprint.assert_called_once()
