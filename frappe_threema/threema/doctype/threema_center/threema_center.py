# Copyright (c) 2024, Centura AG and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from frappe_threema.api import send_message

NAME_SEPARATOR = " - "


class ThreemaCenter(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		message: DF.Text
		receiver_list: DF.Code
	# end: auto-generated types

	@frappe.whitelist()
	def send_message(self):
		if not self.message:
			frappe.msgprint(_("Please enter a message before sending"))
			return

		receivers = self._get_receivers()
		if not receivers:
			frappe.msgprint(_("Please enter at least one receiver"))
			return

		send_message(receivers, self.message)

	def _get_receivers(self) -> list[str]:
		return [
			line.rpartition(NAME_SEPARATOR)[2].strip()
			for line in (self.receiver_list or "").splitlines()
			if line.strip()
		]
