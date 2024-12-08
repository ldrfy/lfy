'设置'
from gettext import gettext as _

from PyQt6.QtCore import Qt, QUrl  # pylint: disable=E0611
from PyQt6.QtGui import (QClipboard, QDesktopServices,  # pylint: disable=E0611
                         QIcon)
from PyQt6.QtWidgets import (QCheckBox, QComboBox,  # pylint: disable=E0611
                             QGroupBox, QHBoxLayout, QLineEdit, QMainWindow,
                             QPushButton, QStyle, QSystemTrayIcon, QTabWidget,
                             QToolButton, QVBoxLayout, QWidget)

from lfy.api import (get_server_names_o, get_server_names_t_sk, get_servers_o,
                     get_servers_t, get_servers_t_sk)
from lfy.api.server.ocr import ServerOCR
from lfy.api.server.tra import ServerTra
from lfy.qt import CheckableComboBox, MyThread
from lfy.utils import clear_key
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

        self.cb = clipboard
        self.tray = tray

        tw = QTabWidget(self)
        self.setCentralWidget(tw)
        tw.addTab(self.get_ui_gen(), _("General"))
        tw.addTab(self.get_ui_other(), _("Other"))
        tw.setCurrentIndex(0)

        self.load_data()

    def get_ui_gen(self):
        """第一页

        Returns:
            _type_: _description_
        """
        tab_general = QWidget()
        vl_general = QVBoxLayout(tab_general)
        vl_general.setContentsMargins(8, 8, 8, 8)

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
        btn_q_t.clicked.connect(self._open_url_t)
        hl_t.addWidget(btn_q_t)

        self.btn_t_save = QPushButton(_("Save"))
        self.btn_t_save.clicked.connect(self._on_t_save)
        hl_t.addWidget(self.btn_t_save)

        self.le_t = QLineEdit()
        vl_t.addWidget(self.le_t)
        vl_t.addLayout(hl_t)
        gb_t.setLayout(vl_t)

        vl_general.addWidget(gb_t)

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
        btn_q_o.clicked.connect(self._open_url_o)
        hl_o.addWidget(btn_q_o)

        self.btn_o_save = QPushButton(_("Save"))
        self.btn_o_save.clicked.connect(self._on_o_save)
        hl_o.addWidget(self.btn_o_save)

        vl_o.addLayout(hl_o)
        gb_o.setLayout(vl_o)

        vl_general.addWidget(gb_o)
        return tab_general

    def get_ui_other(self):
        """第二页

        Returns:
            _type_: _description_
        """
        tab_other = QWidget()
        vl_normal = QVBoxLayout(tab_other)

        cb_auto_check_update = QCheckBox(_("auto check update"))
        cb_auto_check_update.stateChanged.connect(
            self._on_auto_check_update)

        cb_auto_check_update.setChecked(
            self.sg.g("auto-check-update", d=True, t=bool))
        vl_normal.addWidget(cb_auto_check_update)
        cb_notify = QCheckBox(_("Notify translation results"))
        cb_notify.setChecked(
            self.sg.g("notify-translation-results", d=True, t=bool))
        cb_notify.stateChanged.connect(
            self._on_cb_notify)
        vl_normal.addWidget(cb_notify)

        gb_c = QGroupBox(_("Compare model"))
        hl_c = QHBoxLayout()
        self.ccb = CheckableComboBox()
        self.ccb.lineEdit().textChanged.connect(
            lambda: self._cm_servers(self.ccb.checked_items_str()))

        hl_c.addWidget(self.ccb)
        gb_c.setLayout(hl_c)
        vl_normal.addWidget(gb_c)

        gb_vpn = QGroupBox(_("vpn addr and port"))
        hl_vpn = QHBoxLayout()
        self.le_vpn = QLineEdit()
        self.le_vpn.setPlaceholderText("http://127.0.0.1:7890")
        self.le_vpn.setToolTip("http://127.0.0.1:7890")
        hl_vpn.addWidget(self.le_vpn)
        btn_vpn_save = QPushButton(_("Save"))
        btn_vpn_save.clicked.connect(self._on_vpn_save)
        hl_vpn.addWidget(btn_vpn_save)

        gb_vpn.setLayout(hl_vpn)
        vl_normal.addWidget(gb_vpn)

        gb_json = QGroupBox(_("Software settings backup and restore"))

        hl_json = QHBoxLayout()
        btn_backup = QPushButton(_("backup"))
        s = _("Read the JSON configuration of the clipboard, then import it, "
              "and some of the configurations will take effect after reopening the software")
        btn_backup.setToolTip(s)
        btn_backup.clicked.connect(self._export_config)

        hl_json.addWidget(btn_backup)
        btn_restore = QPushButton(_("restore"))
        btn_restore.setToolTip(_("Export the configuration to the clipboard, "
                                 "then you can paste it into any file and edit it"))
        btn_restore.clicked.connect(self._import_config)

        hl_json.addWidget(btn_restore)

        gb_json.setLayout(hl_json)
        vl_normal.addWidget(gb_json)
        return tab_other

    def load_data(self):
        """初始化数据
        """

        sts = list(get_servers_t())[1:]
        keys_s = self.sg.g("compare-servers", [], t=list)
        if keys_s:
            for se in sts:
                keys_s.append(se.key)
        cs = []
        names = []
        for se in sts:
            cs.append(se.key in keys_s)
            names.append(se.name)
        self.ccb.add_checkable_items(names, cs)

        self.cb_t.addItems(get_server_names_t_sk())
        self.cb_o.addItems(get_server_names_o())

        sos = get_servers_o()
        sok = self.sg.g("server-ocr-selected-key", "easyocr")
        for i, so in enumerate(sos):
            if so.key == sok:
                self.cb_o.setCurrentIndex(i)
                break

        self.le_vpn.setText(self.sg.g("vpn-addr-port"))

    def _on_changed_t(self, i):
        if i < 0:
            return
        st: ServerTra = get_servers_t_sk()[i]
        # 保存时，去掉空格，但是显示时，保留
        conf_str = st.get_conf()
        if conf_str:
            conf_str = clear_key(conf_str, "  |  ")
        self.le_t.setText(conf_str)
        self.le_t.setToolTip(st.sk_placeholder_text)
        self.le_t.setPlaceholderText(st.sk_placeholder_text)
        self.btn_t_save.setIcon(QIcon())

    def _on_changed_o(self, i):
        if i < 0:
            return
        so: ServerOCR = get_servers_o()[i]
        # 保存时，去掉空格，但是显示时，保留
        conf_str = so.get_conf()
        if conf_str:
            conf_str = clear_key(conf_str, "  |  ")
        self.le_o.setText(conf_str)
        self.le_o.setToolTip(so.sk_placeholder_text)
        self.le_o.setPlaceholderText(so.sk_placeholder_text)
        self.tray.showMessage(_("OCR server"),
                              _("Using {} for text recognition").format(so.name),
                              QSystemTrayIcon.MessageIcon.Information, 3000)
        self.btn_o_save.setIcon(QIcon())

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
        self.sg.s("notify-translation-results", state != 0)

    def _on_auto_check_update(self, state):
        self.sg.s("auto-check-update", state != 0)

    def _on_vpn_save(self):
        self.sg.s("vpn-addr-port", self.le_vpn.text())

    def _on_btn_to_save(self, ocr=False):

        def notice_s(p):
            t, ok, m, le, api_key, btn_save = p
            btn_save: QPushButton = btn_save
            le: QLineEdit = le
            n = QSystemTrayIcon.MessageIcon.Information
            icon_id = QStyle.StandardPixmap.SP_DialogApplyButton
            if not ok:
                n = QSystemTrayIcon.MessageIcon.Critical
                icon_id = QStyle.StandardPixmap.SP_DialogCancelButton
            self.tray.showMessage(t, m, n, 3000)
            btn_save.setIcon(self.style().standardIcon(icon_id))
            my_thread.clean_up()
            # 保存时，去掉空格，但是显示时，保留
            le.setText(clear_key(api_key, "  |  "))

        def tt(p=None):
            le, api_key, btn_save = p
            if ocr:
                st: ServerOCR = get_servers_o()[self.cb_o.currentIndex()]
                _ok, _s = st.check_conf(api_key)
                if _ok:
                    self.sg.s("server-ocr-selected-key", st.key)
            else:
                st: ServerTra = get_servers_t_sk()[self.cb_t.currentIndex()]
                _ok, _s = st.check_conf(api_key)

            return (st.name, _ok, _s, le, api_key, btn_save)

        le: QLineEdit = self.le_t if not ocr else self.le_o
        btn_save: QPushButton = self.btn_t_save if not ocr else self.btn_o_save
        btn_save.setIcon(QIcon())
        if not le.text():
            print("empty")
            return
        # 保存时，去掉空格，但是显示时，保留

        my_thread = MyThread(tt, (le, clear_key(le.text()), btn_save))
        my_thread.signal.connect(notice_s)
        my_thread.start()

    def _on_t_save(self):
        self._on_btn_to_save(False)

    def _on_o_save(self):
        self._on_btn_to_save(True)

    def _open_url_t(self):
        url = get_servers_t_sk()[self.cb_t.currentIndex()].get_doc_url()
        QDesktopServices.openUrl(QUrl(url))

    def _open_url_o(self):
        url = get_servers_o()[self.cb_o.currentIndex()].get_doc_url()
        QDesktopServices.openUrl(QUrl(url))

    def _cm_servers(self, ns):
        self.sg.s("compare-servers",
                  [s.key for s in list(get_servers_t())[1:] if s.name in ns])
