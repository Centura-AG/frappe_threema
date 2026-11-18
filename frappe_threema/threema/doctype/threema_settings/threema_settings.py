# Copyright (c) 2024, Centura AG and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class ThreemaSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		gateway_url: DF.Data
		secret: DF.Password
	# end: auto-generated types
