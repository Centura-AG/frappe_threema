# Copyright (c) 2024, Centura AG and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe import _, msgprint
from app_frappe_threema.threema.doctype.threema_settings.threema_settings import send_message
from frappe.model.document import Document
from frappe.utils import cstr



class ThreemaCenter(Document):
	def get_receiver_nos(self):
		receiver_nos = []
		if self.receiver_list:
			for d in self.receiver_list.split("\n"):
				receiver_no = d
				if "-" in d:
					receiver_no = receiver_no.split("-")[1]
				if receiver_no.strip():
					receiver_nos.append(cstr(receiver_no).strip())
		else:
			msgprint(_("Receiver List is empty. Please create Receiver List"))

		return receiver_nos

	@frappe.whitelist()
	def send_message(self):
		receiver_list = []
		if not self.message:
			msgprint(_("Please enter message before sending"))
		else:
			receiver_list = self.get_receiver_nos()
		if receiver_list:
			send_message(receiver_list, cstr(self.message))

