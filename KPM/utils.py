from PySide6.QtCore import QSettings


def get_app_settings():
    return QSettings("KPM", "KPM")