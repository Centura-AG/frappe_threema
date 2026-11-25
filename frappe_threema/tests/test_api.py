import json
from unittest.mock import patch

import frappe
import requests
from frappe.tests import IntegrationTestCase

from frappe_threema import api


class ThreemaTestCase(IntegrationTestCase):
	def setUp(self):
		self.settings(
			gateway_url="https://msgapi.example.com/send_simple", sender="*CENTURA", secret="s3cret"
		)
		post = patch.object(requests, "post")
		self.post = post.start()
		self.addCleanup(post.stop)
		log_error = patch.object(frappe, "log_error")
		self.log_error = log_error.start()
		self.addCleanup(log_error.stop)

	def settings(self, gateway_url=None, sender=None, secret=None):
		if sender and secret:
			ts = frappe.get_single("Threema Settings")
			ts.update({"gateway_url": gateway_url, "from": sender, "secret": secret})
			ts.save(ignore_permissions=True)
			return
		frappe.db.set_single_value(
			"Threema Settings", {"gateway_url": gateway_url, "from": sender, "secret": secret}
		)

	def sent_payloads(self):
		return [c.kwargs["data"] for c in self.post.call_args_list]


class TestSendMessage(ThreemaTestCase):
	def test_sends_to_identity_phone_and_email_and_logs(self):
		api.send_message(
			json.dumps(["ABCD1234", "+41 79 123-45-67", "max@example.com"]), "Hello", success_msg=False
		)

		payloads = self.sent_payloads()
		self.assertEqual(
			[(p.get("to"), p.get("phone"), p.get("email")) for p in payloads],
			[("ABCD1234", None, None), (None, "+41791234567", None), (None, None, "max@example.com")],
		)
		self.assertTrue(all(p["from"] == "*CENTURA" and p["secret"] == "s3cret" for p in payloads))
		self.assertEqual(self.post.call_args.args[0], "https://msgapi.example.com/send_simple")

		log = frappe.get_last_doc("Threema Message Log")
		self.assertEqual(log.message, "Hello")
		self.assertEqual(log.recipient.split("\n"), ["ABCD1234", "+41791234567", "max@example.com"])
		self.assertEqual(log.sender, "Administrator")

	def test_email_keeps_its_dashes(self):
		api.send_message(["anne-marie@example.com"], "Hi", success_msg=False)
		self.assertEqual(self.sent_payloads()[0]["email"], "anne-marie@example.com")

	def test_success_message_lists_recipients(self):
		with patch.object(frappe, "msgprint") as msgprint:
			api.send_message(["ABCD1234"], "Hi")
		self.assertIn("ABCD1234", msgprint.call_args.args[0])

	def test_single_string_receiver_is_wrapped(self):
		api.send_message(json.dumps("ABCD1234"), "Hi", success_msg=False)
		self.assertEqual(self.sent_payloads()[0]["to"], "ABCD1234")

	def test_without_from_and_secret(self):
		self.settings(gateway_url="https://msgapi.example.com/send_simple")
		api.send_message(["ABCD1234"], "Hi", success_msg=False)
		self.assertEqual(self.sent_payloads(), [{"text": "Hi", "to": "ABCD1234"}])

	def test_empty_receivers_throw(self):
		with self.assertRaises(frappe.ValidationError):
			api.send_message(["", " - "], "Hi")
		self.post.assert_not_called()

	def test_missing_gateway_url_asks_for_settings(self):
		self.settings()
		with patch.object(frappe, "msgprint") as msgprint:
			api.send_message(["ABCD1234"], "Hi")
		msgprint.assert_called_once()
		self.post.assert_not_called()

	def summary_logs(self):
		return [
			c.kwargs
			for c in self.log_error.call_args_list
			if c.kwargs["title"] == "Threema send failed: no recipient received the message"
		]

	def test_invalid_recipient_is_skipped(self):
		count = frappe.db.count("Threema Message Log")
		api.send_message(["not valid!"], "Hi", success_msg=False)
		self.post.assert_not_called()
		self.assertEqual(self.log_error.call_args_list[0].kwargs["title"], "Threema invalid recipient")
		self.assertEqual(
			[s["message"] for s in self.summary_logs()],
			["notvalid!: invalid recipient, not sent to the gateway"],
		)
		self.assertEqual(frappe.db.count("Threema Message Log"), count)

	def test_gateway_errors_are_logged_and_skipped(self):
		self.post.return_value.raise_for_status.side_effect = [requests.HTTPError("401"), None]
		with patch.object(frappe, "msgprint") as msgprint:
			api.send_message(["ABCD1234", "EFGH5678"], "Hi")
		self.assertEqual(self.log_error.call_args.kwargs, {"title": "Threema send failed", "message": "401"})
		self.assertEqual(self.summary_logs(), [])
		self.assertEqual(frappe.get_last_doc("Threema Message Log").recipient, "EFGH5678")
		sent, not_sent = msgprint.call_args_list
		self.assertIn("EFGH5678", sent.args[0])
		self.assertNotIn("ABCD1234", sent.args[0])
		self.assertIn("ABCD1234", not_sent.args[0])
		self.assertNotIn("EFGH5678", not_sent.args[0])
		self.assertEqual(not_sent.kwargs["indicator"], "orange")

	def test_full_success_shows_no_failure_message(self):
		with patch.object(frappe, "msgprint") as msgprint:
			api.send_message(["ABCD1234", "EFGH5678"], "Hi")
		msgprint.assert_called_once()

	def test_no_accepted_recipient_is_reported_and_logged(self):
		self.post.return_value.raise_for_status.side_effect = requests.HTTPError("401")
		count = frappe.db.count("Threema Message Log")
		with patch.object(frappe, "msgprint") as msgprint:
			api.send_message(["ABCD1234", "EFGH5678"], "Hi")
		self.assertIn("ABCD1234, EFGH5678", msgprint.call_args.args[0])
		self.assertEqual(msgprint.call_args.kwargs["indicator"], "red")
		self.assertEqual([s["message"] for s in self.summary_logs()], ["ABCD1234: 401\nEFGH5678: 401"])
		self.assertEqual(frappe.db.count("Threema Message Log"), count)

	def test_no_accepted_recipient_stays_silent_for_notifications(self):
		self.post.return_value.raise_for_status.side_effect = requests.HTTPError("401")
		with patch.object(frappe, "msgprint") as msgprint:
			api.send_message(["ABCD1234"], "Hi", success_msg=False)
		msgprint.assert_not_called()
		self.assertEqual([s["message"] for s in self.summary_logs()], ["ABCD1234: 401"])

	def test_recipient_specifier(self):
		self.assertEqual(api._get_recipient_specifier("ABCD1234"), "to")
		self.assertEqual(api._get_recipient_specifier("+41791234567"), "phone")
		self.assertEqual(api._get_recipient_specifier("a.b@example.ch"), "email")
		with self.assertRaises(frappe.ValidationError):
			api._get_recipient_specifier("abc")
