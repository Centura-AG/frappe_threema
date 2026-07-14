app_name = "frappe_threema"
app_title = "Frappe Threema"
app_publisher = "Centura AG"
app_description = "Threema Gateway API Integration for Frappe"
app_email = "info@centura.ch"
app_license = "mit"

after_install = "frappe_threema.setup.after_install"
after_migrate = "frappe_threema.setup.after_migrate"

doctype_js = {"Notification": "threema/doctype/notification/notification.js"}

extend_doctype_class = {
	"Notification": ["frappe_threema.threema.doctype.notification.notification.ThreemaNotificationMixin"]
}
