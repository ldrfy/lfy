'托盘图标'
import time
from gettext import gettext as _

from PyQt6.QtGui import QAction, QClipboard, QIcon
from PyQt6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon

from lfy import APP_NAME, PACKAGE_URL, PACKAGE_URL_BUG, VERSION
from lfy.qt import MyThread
from lfy.qt.preference import PreferenceWindow
from lfy.qt.translate import TranslateWindow
from lfy.utils import cal_md5
from lfy.utils.check_update import main as check_update
from lfy.utils.settings import Settings


class TrayIcon(QSystemTrayIcon):
    """托盘图标

    Args:
        QSystemTrayIcon (_type_): _description_
    """

    def __init__(
        self,
        parent: TranslateWindow,
        app: QApplication,
        icon: QIcon
    ) -> None:
        QSystemTrayIcon.__init__(self, icon, parent)
        self.w = parent
        self.sg = Settings()
        self.cb: QClipboard = app.clipboard()

        # 创建托盘菜单
        tray_menu = QMenu(parent)
        open_action = QAction(_("Open"), self)
        open_action.triggered.connect(self.w.show)
        tray_menu.addAction(open_action)

        fu_action = QAction(_("Check for updates"), self)
        fu_action.triggered.connect(self.find_update)
        tray_menu.addAction(fu_action)

        self.auto_action = QAction(
            _('Copy to translate'), triggered=self.copy2translate)
        self.auto_action.setEnabled(True)
        self.auto_action.setCheckable(True)
        self.auto_action.setChecked(
            self.sg.g("copy-auto-translate", d=True, t=bool))
        self.copy2translate()
        tray_menu.addAction(self.auto_action)

        pf_action = QAction(_("Preference") + " Ctrl+,", self)
        pf_action.triggered.connect(self.open_prf)
        tray_menu.addAction(pf_action)

        about_action = QAction(_("About"), self)
        about_action.triggered.connect(self.show_about_window)
        tray_menu.addAction(about_action)

        quit_action = QAction(_("Quit") + " Ctrl+Q", self)
        quit_action.triggered.connect(app.quit)
        tray_menu.addAction(quit_action)

        self.setContextMenu(tray_menu)

        self.img_md5 = ""
        self.text_last = ""
        self.my_thread = None
        if self.sg.g("auto-check-update"):
            self.find_update()

        # 绑定托盘单击事件
        self.activated.connect(self._tray_icon_clicked)

    def _tray_icon_clicked(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.w.show()

    def _on_clipboard_data_changed(self):

        if self.cb.mimeData().hasImage():
            # 如果是图片，处理图片
            image = self.cb.image()
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
        elif self.cb.mimeData().hasText():
            text = self.cb.text()
            if text == self.text_last:
                return
            self.text_last = text

            if not self.w.isVisible():
                self.w.show()
            self.w.translate_text(text)

    def open_prf(self):
        """_summary_
        """
        PreferenceWindow(self.cb, self).show()

    def show_about_window(self):
        """关于窗口
        """
        s = f'''<h3>{_(APP_NAME)}</h3>
            <p>{VERSION}</p>
            <p><a href="{PACKAGE_URL}">Home</a> < /p >
            <p><a href="{PACKAGE_URL_BUG}">Bug Report</a></p>
            <p>&copy; 2024 yuhldr</p>
            <p>'''
        s += _("Translation software for read paper")
        s += "</p>"
        QMessageBox.about(
            self.w,
            _("About"),
            s
        )

    def copy2translate(self):
        """复制即翻译可以选择暂停，并且会记住选择
        """
        auto_translate = self.auto_action.isChecked()
        self.sg.s("copy-auto-translate", auto_translate)
        if auto_translate:
            t = _("Copy to translate")
            m = _("Copy detected, translate immediately")
            n = QSystemTrayIcon.MessageIcon.Warning
            self.cb.dataChanged.connect(self._on_clipboard_data_changed)
        else:
            self.cb.disconnect()
            t = _("Stop copy to translate")
            m = _("Copy detected, not automatically translated")
            n = QSystemTrayIcon.MessageIcon.Critical

        self.showMessage(t, m, n, 2000)

    def update_app(self, p):
        """显示更新信息

        Args:
            update_msg (_type_): _description_
        """
        t, update_msg, n = p
        if update_msg is None:
            return
        # pylint: disable=E1101
        self.my_thread.clean_up()
        self.w.translate_text(update_msg)
        self.showMessage(t, update_msg, n, 2000)

    def find_update(self, auto=True):
        """查找更新
        """

        def fu(_p=None):
            """更新子线程
            """
            update_msg = check_update()
            if update_msg is not None:
                time.sleep(2)
                return (_("New version available!"),
                        update_msg, QSystemTrayIcon.MessageIcon.Warning)

            if not auto:
                # 手动更新
                s = _("There is no new version.\
                      \nThe current version is {}.\
                      \nYou can go to {} to view the beta version.")\
                    .format(VERSION, PACKAGE_URL)
                return (_("No new version!"), s,
                        QSystemTrayIcon.MessageIcon.Critical)
            return (None, None, None)

        self.my_thread = MyThread(fu)
        self.my_thread.signal.connect(self.update_app)
        self.my_thread.start()

        if not auto:
            self.w.te_from.setPlainText(_("Check for updates") + "...")
