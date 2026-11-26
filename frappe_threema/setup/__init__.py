from .notification import add_threema_notification_channel, setup_threema_system_notification_title


def after_install():
	add_threema_notification_channel()
	setup_threema_system_notification_title()


def after_migrate():
	add_threema_notification_channel()
	setup_threema_system_notification_title()
