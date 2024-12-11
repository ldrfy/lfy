'qt入口'
import os
import sys
from gettext import gettext as _

from PyQt6.QtGui import QIcon  # pylint: disable=E0611
from PyQt6.QtWidgets import QApplication  # pylint: disable=E0611

from lfy import APP_ID, APP_NAME
from lfy.qt.translate import TranslateWindow
from lfy.qt.tray import TrayIcon
from lfy.utils.code import parse_lfy, set_vpn

set_vpn()


def main():
    """qt版本入口
    """

    s = parse_lfy()
    if s:
        print(s)
        return

    app = QApplication(sys.argv)

    icon = QIcon.fromTheme(APP_ID)
    if icon.isNull():
        # 如果图标未加载成功，使用默认图标
        icon = QIcon(os.path.join(os.path.dirname(__file__),
                                  f"../resources/{APP_ID}.svg"))
    app.setWindowIcon(icon)
    app.setApplicationName(_(APP_NAME))
    app.setDesktopFileName(APP_ID)

    # windows阻止最后一个窗口关闭时退出应用tray
    app.setQuitOnLastWindowClosed(False)
    window = TranslateWindow(app)
    tray = TrayIcon(window, app, icon)
    tray.show()
    window.tray = tray
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
