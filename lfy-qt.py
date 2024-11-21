#!@PYTHON@
import os
import subprocess
import sys
from gettext import gettext as _

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

APP_ID = '@APP_ID@'
VERSION = '@VERSION@'

SCHEMAS_DIR = '@SCHEMAS_DIR@'
PYTHON_DIR = '@PYTHON_DIR@'

LOCALE_DIR = '@LOCALE_DIR@'
PKGDATA_DIR = '@PKGDATA_DIR@'

if not os.path.exists(PKGDATA_DIR):
    # 说明是pip这一类的
    print(f"路径修正：{SCHEMAS_DIR}")
    THIS_DIR, THIS_FILENAME = os.path.split(__file__)
    PYTHON_DIR = os.path.abspath(f"{THIS_DIR}/../lib/")
    SCHEMAS_DIR = os.path.abspath(f"{THIS_DIR}/../share/")
    LOCALE_DIR = os.path.abspath(f"{SCHEMAS_DIR}/locale/")
    subprocess.run(
        ["glib-compile-schemas", f"{SCHEMAS_DIR}/glib-2.0/schemas"], check=True)

    os.environ["XDG_DATA_DIRS"] = f'{SCHEMAS_DIR}:' + \
        os.environ.get("XDG_DATA_DIRS", "")
    print(SCHEMAS_DIR)

# python lib
sys.path.append(PYTHON_DIR)


if __name__ == "__main__":
    os.environ[f'{APP_ID}.ui'] = 'qt'

    from lfy import set_internationalization
    set_internationalization(APP_ID, LOCALE_DIR)

    from lfy.code import parse_lfy
    parse_lfy()

    app = QApplication(sys.argv)

    from lfy.qt.translate import TranslateWindow
    from lfy.qt.tray import TrayIcon

    icon = QIcon.fromTheme(APP_ID)
    window = TranslateWindow()
    window.setWindowIcon(icon)
    tray = TrayIcon(window, app, icon)
    tray.show()
    window.tray = tray
    window.show()
    sys.exit(app.exec())
