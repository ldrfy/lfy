'设置'
import re
from gettext import gettext as _

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QClipboard, QDesktopServices
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QGroupBox, QHBoxLayout,
                             QLineEdit, QMainWindow, QPushButton, QStyle,
                             QSystemTrayIcon, QTabWidget, QToolButton,
                             QVBoxLayout, QWidget)

from lfy.api import (get_server_names_api_key, get_server_names_o,
                     get_servers_api_key, get_servers_o, get_servers_t)
from lfy.qt import CheckableComboBox, MyThread
from lfy.utils.bak import backup_gsettings, restore_gsettings
from lfy.utils.settings import Settings


class PreferenceWindow(QMainWindow):
    """设置

    Args:
        QMainWindow (_type_): _description_
    """

    def __init__(self, clipboard: QClipboard, tray: QSystemTrayIcon):
        super().__init__()
        self.sg = Settings()

        self.resize(500, 300)
        self.setWindowFlags(self.windowFlags() |
                            Qt.WindowType.WindowStaysOnTopHint)

        tw = QTabWidget(self)
        self.cb = clipboard
        self.tray = tray

        self.tab_general = QWidget()
        self.vl_general = QVBoxLayout(self.tab_general)
        self.vl_general.setContentsMargins(8, 8, 8, 8)

        gb_t = QGroupBox(_("Translation keys"))

        vl_t = QVBoxLayout()

        hl_t = QHBoxLayout()
        self.cb_t = QComboBox()
        self.cb_t.currentIndexChanged.connect(self._on_changed_t)
        hl_t.addWidget(self.cb_t)

        btn_q_t = QToolButton(self)
        btn_q_t.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_TitleBarContextHelpButton))
        btn_q_t.setToolTip(_("how to get API Key"))
        btn_q_t.clicked.connect(self.open_url_t)
        hl_t.addWidget(btn_q_t)

        btn_t_save = QPushButton(_("Save"))
        btn_t_save.clicked.connect(self._on_t_save)
        hl_t.addWidget(btn_t_save)

        self.le_t = QLineEdit()
        vl_t.addWidget(self.le_t)
        vl_t.addLayout(hl_t)
        gb_t.setLayout(vl_t)

        self.vl_general.addWidget(gb_t)

        gb_o = QGroupBox(_("OCR server"))
        vl_o = QVBoxLayout()

        self.le_o = QLineEdit()
        vl_o.addWidget(self.le_o)

        hl_o = QHBoxLayout()
        self.cb_o = QComboBox()
        self.cb_o.currentIndexChanged.connect(self._on_changed_o)
        hl_o.addWidget(self.cb_o)

        btn_q_o = QToolButton(self)
        btn_q_o.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_TitleBarContextHelpButton))
        btn_q_o.setToolTip(_("how to get API Key"))
        btn_q_o.clicked.connect(self.open_url_o)
        hl_o.addWidget(btn_q_o)

        btn_o_save = QPushButton(_("Save"))
        btn_o_save.clicked.connect(self._on_o_save)
        hl_o.addWidget(btn_o_save)

        vl_o.addLayout(hl_o)
        gb_o.setLayout(vl_o)

        self.vl_general.addWidget(gb_o)

        tw.addTab(self.tab_general, _("General"))

        self.tab_other = QWidget()
        self.vl_normal = QVBoxLayout(self.tab_other)

        cb_auto_check_update = QCheckBox(_("auto check update"))
        cb_auto_check_update.stateChanged.connect(
            self._on_auto_check_update)

        cb_auto_check_update.setChecked(
            self.sg.g("auto-check-update", d=True, t=bool))
        self.vl_normal.addWidget(cb_auto_check_update)
        cb_notify = QCheckBox(_("Notify translation results"))
        cb_notify.setChecked(
            self.sg.g("notify-translation-results", d=True, t=bool))
        cb_notify.stateChanged.connect(
            self._on_cb_notify)
        self.vl_normal.addWidget(cb_notify)

        gb_c = QGroupBox(_("Compare model"))
        hl_c = QHBoxLayout()
        self.ccb = CheckableComboBox()
        self.ccb.lineEdit().textChanged.connect(
            lambda: self._cm_servers(self.ccb.checkedItemsStr()))

        hl_c.addWidget(self.ccb)
        gb_c.setLayout(hl_c)
        self.vl_normal.addWidget(gb_c)

        gb_vpn = QGroupBox(_("vpn addr and port"))
        hl_vpn = QHBoxLayout()
        self.le_vpn = QLineEdit()
        self.le_vpn.setPlaceholderText("http://127.0.0.1:7890")
        hl_vpn.addWidget(self.le_vpn)
        btn_vpn_save = QPushButton(_("Save"))
        btn_vpn_save.clicked.connect(self._on_vpn_save)
        hl_vpn.addWidget(btn_vpn_save)

        gb_vpn.setLayout(hl_vpn)
        self.vl_normal.addWidget(gb_vpn)

        gb_json = QGroupBox(_("Software settings backup and restore"))

        hl_json = QHBoxLayout()
        btn_backup = QPushButton(_("backup"))
        btn_backup.setToolTip(
            _("Read the JSON configuration of the clipboard, then import it, and some of the configurations will take effect after reopening the software"))
        btn_backup.clicked.connect(self._export_config)

        hl_json.addWidget(btn_backup)
        btn_restore = QPushButton(_("restore"))
        btn_restore.setToolTip(
            _("Export the configuration to the clipboard, then you can paste it into any file and edit it"))
        btn_restore.clicked.connect(self._import_config)

        hl_json.addWidget(btn_restore)

        gb_json.setLayout(hl_json)
        self.vl_normal.addWidget(gb_json)

        tw.addTab(self.tab_other, _("Other"))

        self.setCentralWidget(tw)

        tw.setCurrentIndex(0)

        self.load_data()

    def load_data(self):
        """初始化数据
        """

        ss = list(get_servers_t())[1:]
        keys_s = self.sg.g("compare-servers", [], t=list)
        print(keys_s)
        if len(keys_s) == 0:
            for se in ss:
                keys_s.append(se.key)
        cs = []
        names = []
        for se in ss:
            cs.append(se.key in keys_s)
            names.append(se.name)
        self.ccb.addCheckableItems(names, cs)

        # xx
        self.cb_t.addItems(get_server_names_api_key())

        self.cb_o.addItems(get_server_names_o())
        sso = get_servers_o()
        for i, so in enumerate(sso):
            if so.key == self.sg.g("server-ocr-selected-key"):
                self.cb_o.setCurrentIndex(i)
                self.server_ocr = so
                break

        self.le_vpn.setText(self.sg.g("vpn-addr-port"))

    def _on_changed_t(self, i):
        if i < 0:
            return
        self.le_t.setText(get_servers_api_key()[i].get_api_key_s())

    def _on_changed_o(self, i):
        if i < 0:
            return

        self.le_o.setText(get_servers_o()[i].get_api_key_s_ocr())

    def _import_config(self):
        if self.cb.mimeData().hasText():
            s = restore_gsettings(self.cb.text())
            if len(s) == 0:
                self.tray.showMessage(_("Import successful!"),
                                      _("It takes effect when you restart lfy."),
                                      QSystemTrayIcon.MessageIcon.Information, 2000)
                return

        self.tray.showMessage(_("Import failed!"),
                              _("No configuration data in the clipboard."),
                              QSystemTrayIcon.MessageIcon.Critical, 3000)

    def _export_config(self):
        self.cb.setText(backup_gsettings())
        self.tray.showMessage(_("Export successful!"),
                              _("Configuration data has been exported to the clipboard."),
                              QSystemTrayIcon.MessageIcon.Information, 3000)

    def _on_cb_notify(self, state):
        self.sg.s("notify-translation-results", state)

    def _on_auto_check_update(self, state):
        self.sg.s("auto-check-update", state)

    def _on_vpn_save(self):
        self.sg.s("vpn-addr-port", self.le_vpn.text())

    def _on_btn_to_save(self, ocr=False):

        def notice_s(p):
            t, ok, m = p
            n = QSystemTrayIcon.MessageIcon.Information
            if not ok:
                n = QSystemTrayIcon.MessageIcon.Critical
            self.tray.showMessage(t, m, n, 3000)
            my_thread.clean_up()

        def tt(_p=None):
            if ocr:
                api_key = re.sub(r'\s*\|\s*', "  |  ",
                                 self.le_o.text().strip())
                st = get_servers_o()[self.cb_o.currentIndex()]
                _ok, _s = st.check_ocr(api_key)
                if _ok:
                    self.sg.s("server-ocr-selected-key", st.key)
            else:
                api_key = re.sub(r'\s*\|\s*', "  |  ",
                                 self.le_t.text().strip())
                st = get_servers_api_key()[self.cb_t.currentIndex()]
                _ok, _s = st.check_translate(api_key)

            return (st.name, _ok, _s)

        my_thread = MyThread(tt)
        my_thread.signal.connect(notice_s)
        my_thread.start()

    def _on_t_save(self):
        self._on_btn_to_save(False)

    def _on_o_save(self):
        self._on_btn_to_save(True)

    def open_url_t(self):
        url = get_servers_api_key()[self.cb_t.currentIndex()].get_doc_url()
        QDesktopServices.openUrl(QUrl(url))

    def open_url_o(self):
        url = get_servers_o()[self.cb_o.currentIndex()].get_doc_url()
        QDesktopServices.openUrl(QUrl(url))

    def _cm_servers(self, ns):
        ss = list(get_servers_t())[1:]
        self.sg.s("compare-servers", [s.key for s in ss if s.name in ns])
