# Copyright (c) 2024, Centura AG and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr

from frappe_threema.api import send_message


class ThreemaCenter(Document):
	def _get_receiver_nos(self) -> list[str]:
		if not self.receiver_list:
			frappe.msgprint(_("Receiver List is empty. Please create Receiver List"))
			return []
		return [
			cstr(d.split("-")[1]).strip() if "-" in d else cstr(d).strip()
			for d in self.receiver_list.split("\n")
			if d.strip()
		]

	@frappe.whitelist()
	def send_message(self):
		if not self.message:
			frappe.msgprint(_("Please enter message before sending"))
			return
		receiver_list = self._get_receiver_nos()
		if receiver_list:
			send_message(receiver_list, cstr(self.message))
