import gettext
import locale
import sys
from gettext import gettext as _

from PyQt6.QtGui import QIcon  # 从 QtGui 导入 QAction
from PyQt6.QtWidgets import QApplication
from translate import TranslateWindow
from tray import TrayIcon

from lfy import APP_ID

SCHEMAS_DIR = '/usr/share'
PYTHON_DIR = '/usr/lib'

LOCALE_DIR = '/usr/share/locale'
PKGDATA_DIR = '/usr/share/cool.ldr.lfy'


def set_internationalization():
    """Sets application internationalization."""
    try:
        locale.bindtextdomain(APP_ID, LOCALE_DIR)
        locale.textdomain(APP_ID)
    except AttributeError as e:
        from lfy.api.utils.debug import get_logger
        get_logger().error(e)
        print(f"Some gettext translations will not work. Error:\n{e}")

    gettext.bindtextdomain(APP_ID, LOCALE_DIR)
    gettext.textdomain(APP_ID)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置语言
    set_internationalization()
    icon = QIcon.fromTheme(APP_ID)
    window = TranslateWindow()
    window.setWindowIcon(icon)
    # 显示托盘图标
    TrayIcon(window, app, icon).show()

    window.show()
    sys.exit(app.exec())
