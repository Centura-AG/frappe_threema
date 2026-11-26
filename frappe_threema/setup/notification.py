import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

THREEMA_SYSTEM_NOTIFICATION = "doc.channel == 'Threema' && doc.send_system_notification"


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


def setup_threema_system_notification_title() -> None:
	"""Show the subject on Threema rules once the system notification takes its title from there."""
	meta = frappe.get_meta("Notification")
	if meta.has_field("notification_title"):
		return

	standard = frappe.db.get_value(
		"DocField", {"parent": "Notification", "fieldname": "subject"}, "depends_on"
	)
	if standard:
		expression = standard.strip().removeprefix("eval:").strip()
		depends_on = f"eval: ({expression}) || ({THREEMA_SYSTEM_NOTIFICATION})"
		if meta.get_field("subject").depends_on != depends_on:
			make_property_setter("Notification", "subject", "depends_on", depends_on, "Code")

	if frappe.db.has_column("Notification", "notification_title"):
		notification = frappe.qb.DocType("Notification")
		frappe.qb.update(notification).set(notification.subject, notification.notification_title).where(
			(notification.channel == "Threema")
			& (notification.subject.isnull() | (notification.subject == ""))
			& notification.notification_title.isnotnull()
			& (notification.notification_title != "")
		).run()
