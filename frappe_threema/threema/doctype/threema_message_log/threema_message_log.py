# Copyright (c) 2024, Centura AG and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class ThreemaMessageLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		message: DF.Text | None
		recipient: DF.Code | None
		sender: DF.Link | None
		sent_at: DF.Datetime | None
	# end: auto-generated types
