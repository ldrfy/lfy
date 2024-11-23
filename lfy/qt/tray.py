'托盘图标'
from gettext import gettext as _

from PyQt6.QtGui import QAction, QClipboard
from PyQt6.QtWidgets import (QApplication, QDialog, QMenu, QMessageBox,
                             QSystemTrayIcon, QTextEdit, QVBoxLayout)

from lfy import APP_NAME
from lfy.qt.preference import PreferenceWindow
from lfy.qt.translate import TranslateWindow
from lfy.utils import cal_md5


class TrayIcon(QSystemTrayIcon):
    def __init__(
        self,
        parent,
        app,
        icon
    ) -> None:
        QSystemTrayIcon.__init__(self, icon, parent)
        # QSystemTrayIcon also tries to save parent info but it screws up the type info
        self.w: TranslateWindow = parent
        self.app: QApplication = app
        self.setToolTip(APP_NAME)

        # 创建托盘菜单
        tray_menu = QMenu(parent)
        open_action = QAction(_("Open"), self)
        open_action.triggered.connect(self.w.show)
        tray_menu.addAction(open_action)

        hide_action = QAction(_("Hide"), self)
        hide_action.triggered.connect(self.w.close)
        tray_menu.addAction(hide_action)

        pf_action = QAction(_("preference"), self)
        pf_action.triggered.connect(self.show_setting_window)
        tray_menu.addAction(pf_action)

        about_action = QAction(_("about"), self)
        about_action.triggered.connect(self.show_about_window)
        tray_menu.addAction(about_action)

        quit_action = QAction(_("Quit"), self)
        # quit_action.triggered.connect(parent.close)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)

        self.setContextMenu(tray_menu)

        self.clipboard: QClipboard = self.app.clipboard()
        self.clipboard.dataChanged.connect(self._on_clipboard_data_changed)

        self.img_md5 = ""
        self.text_last = ""

    def _on_clipboard_data_changed(self):

        if self.clipboard.mimeData().hasImage():
            # 如果是图片，处理图片
            image = self.clipboard.image()
            if not image.isNull():
                file_path = "/tmp/lfy.png"
                image.save(file_path, "PNG")

                md5_hash = cal_md5(file_path)
                if self.img_md5 == md5_hash:
                    return
                self.img_md5 = md5_hash

                if not self.w.isVisible():
                    self.w.show()
                self.w.ocr_image(file_path)
        elif self.clipboard.mimeData().hasText():
            text = self.clipboard.text()
            if text == self.text_last:
                return
            self.text_last = text

            if not self.w.isVisible():
                self.w.show()
            self.w.translate_text(text)


    def quit_app(self):
        re = QMessageBox.warning(self.w, _("warn"), _("quit?"),
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                 QMessageBox.StandardButton.No)
        if re == QMessageBox.StandardButton.Yes:
            self.setVisible(False)  # 隐藏托盘控件，托盘图标刷新不及时，提前隐藏
            self.app.quit()  # 退出程序

    def show_about_window(self):
        AboutWindow().exec()

    def show_setting_window(self):
        PreferenceWindow().exec()

    def show_msg(self, title, msg):
        self.showMessage(
            title, msg, QSystemTrayIcon.MessageIcon.Information, 2000)


class AboutWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(_("About"))
        self.setGeometry(150, 150, 400, 200)
        self.setModal(True)
        text_edit = QTextEdit(self)
        text_edit.setText(
            _("This is the About window, displaying application information."))
        text_edit.setReadOnly(True)
        layout = QVBoxLayout(self)
        layout.addWidget(text_edit)
