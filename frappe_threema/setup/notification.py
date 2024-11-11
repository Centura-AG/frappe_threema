import frappe


def add_threema_notification_channel():
    """
    This will add Threema to existing list of Channels.
    This will not overwrite other custom channels that came in via custom-apps
    """
    meta = frappe.get_meta('Notification')
    channels = meta.get_field("channel").options.split("\n")
    if "Threema" in channels:
        return

    channels.append("Threema")
    frappe.get_doc({
        "doctype": "Property Setter",
        "doctype_or_field": "DocField",
        "doc_type": "Notification",
        "field_name": "channel",
        "property": "options",
        "value": "\n".join(channels),
        "property_type": "Small Text"
    }).insert()