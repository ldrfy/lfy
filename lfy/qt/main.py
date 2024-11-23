import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from lfy import APP_ID
from lfy.qt.translate import TranslateWindow
from lfy.qt.tray import TrayIcon
from lfy.utils.code import parse_lfy


def main():
    """_summary_
    """
    os.environ[f'{APP_ID}.ui'] = 'qt'

    parse_lfy()

    app = QApplication(sys.argv)


    icon = QIcon.fromTheme(APP_ID)
    window = TranslateWindow()
    window.setWindowIcon(icon)
    tray = TrayIcon(window, app, icon)
    tray.show()
    window.tray = tray
    window.show()
    sys.exit(app.exec())
