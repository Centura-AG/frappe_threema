from .notification import add_threema_notification_channel


def after_install():
    add_threema_notification_channel()


def after_migrate():
    add_threema_notification_channel()