import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from lfy import APP_ID
from lfy.qt.translate import TranslateWindow
from lfy.qt.tray import TrayIcon
from lfy.utils.code import parse_lfy
from lfy.utils.settings import Settings

# 设置代理地址和端口号
PROXY_ADDRESS = Settings().g("vpn-addr-port")
if len(PROXY_ADDRESS) > 0:
    # 设置环境变量
    os.environ['http_proxy'] = PROXY_ADDRESS
    os.environ['https_proxy'] = PROXY_ADDRESS


def main():
    """_summary_
    """

    parse_lfy()

    app = QApplication(sys.argv)

    icon = QIcon.fromTheme(APP_ID)
    if icon.isNull():
        # 如果图标未加载成功，使用默认图标
        icon = QIcon(os.path.join(os.path.dirname(
            __file__), f"../resources/{APP_ID}.svg"))

    window = TranslateWindow()
    window.setWindowIcon(icon)
    tray = TrayIcon(window, app, icon)
    tray.show()
    window.tray = tray
    window.show()
    sys.exit(app.exec())
