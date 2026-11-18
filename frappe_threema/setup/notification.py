import frappe


def add_threema_notification_channel() -> None:
	"""Add "Threema" to the Notification channels, keeping channels added by other apps."""
	meta = frappe.get_meta("Notification")
	channels = meta.get_field("channel").options.split("\n")
	if "Threema" in channels:
		return

	channels.append("Threema")
	frappe.get_doc(
		{
			"doctype": "Property Setter",
			"doctype_or_field": "DocField",
			"doc_type": "Notification",
			"field_name": "channel",
			"property": "options",
			"value": "\n".join(channels),
			"property_type": "Small Text",
		}
	).insert()
