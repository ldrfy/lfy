'翻译主窗口'
import traceback
from gettext import gettext as _

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QHBoxLayout,
                             QMainWindow, QMessageBox, QPlainTextEdit,
                             QPushButton, QSplitter, QSystemTrayIcon,
                             QVBoxLayout, QWidget)

from lfy.api import (create_server_o, create_server_t, get_lang,
                     get_lang_names, get_server_names_t, get_server_t,
                     lang_n2j, server_key2i)
from lfy.api.constant import NO_TRANSLATED_TXTS
from lfy.api.server import Server
from lfy.qt import MyThread
from lfy.utils import process_text
from lfy.utils.debug import get_logger
from lfy.utils.settings import Settings


class TranslateWindow(QMainWindow):
    """翻译主窗口

    Args:
        QMainWindow (_type_): _description_
    """

    def __init__(self, app):
        super().__init__()
        self.app: QApplication = app

        self.setWindowFlags(self.windowFlags() |
                            Qt.WindowType.WindowStaysOnTopHint)

        self.setGeometry(100, 100, 600, 400)
        # 创建中心部件
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        bottom_widget = QWidget(self)
        bottom_layout = QVBoxLayout(bottom_widget)
        splitter = QSplitter(Qt.Orientation.Vertical, self)

        # 上面的文本编辑框
        self.te_from = QPlainTextEdit(self)

        # 中间的布局（包含选择按钮和普通按钮）
        middle_widget = QWidget(self)
        middle_layout = QHBoxLayout(middle_widget)

        # 左边的两个下拉框（QComboBox）
        self.cb_server = QComboBox(self)
        self.cb_server.currentIndexChanged.connect(self._on_server_changed)

        self.cb_lang = QComboBox(self)
        self.cb_lang.currentIndexChanged.connect(self._on_lang_changed)

        # 右边的两个选择按钮
        self.cb_del_wrapping = QCheckBox(_("Remove line breaks"), self)
        self.cb_del_wrapping.setToolTip(_(
            "Alt + D: Remove symbols such as line breaks"))

        self.cb_add_old = QCheckBox(_("Splice Text"), self)
        self.cb_add_old.setToolTip(_(
            "Alt + C: Splice the next copied text with the previous text"))

        btn_translate = QPushButton(_("Translate"), self)
        btn_translate.clicked.connect(self.update_translate)
        btn_translate.setToolTip(_("Translate") + ": `Ctrl+T`")

        middle_layout.addWidget(self.cb_server)
        middle_layout.addWidget(self.cb_lang)
        middle_layout.addStretch(1)  # 用来拉伸中间部分
        middle_layout.addWidget(self.cb_del_wrapping)
        middle_layout.addWidget(self.cb_add_old)
        middle_layout.addWidget(btn_translate)
        # 下面的文本编辑框
        self.te_to = QPlainTextEdit(self)

        bottom_layout.addWidget(middle_widget)
        bottom_layout.addWidget(self.te_to)

        splitter.addWidget(self.te_from)
        splitter.addWidget(bottom_widget)

        main_layout.addWidget(splitter)

        middle_layout.setContentsMargins(1, 5, 1, 5)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)

        self.jn = False
        self.server_t = None
        self.lang_t = None
        self.my_thread = None
        self.tray: QSystemTrayIcon = None
        self.text_last = ""
        self.translate_next = True

        self.set_data()

    def set_data(self):
        """_summary_
        """
        self.sg = Settings()
        self.cb_server.setEditable(True)
        self.cb_lang.setEditable(True)

        server_key_t = self.sg.g("server-selected-key", "bing")
        server_key_o = self.sg.g("server-ocr-selected-key", "baidu")

        self.server_t = create_server_t(server_key_t)
        self.server_o = create_server_o(server_key_o)

        i = server_key2i(server_key_t)
        self.jn = i == 0
        self.cb_server.addItems(get_server_names_t())
        self.jn = True
        self.cb_server.setCurrentIndex(i)
        n = self.sg.g("lang-selected-n", 0, int)
        j = lang_n2j(i, n)
        self.lang_t = get_lang(i, j)
        self.cb_lang.setCurrentIndex(j)
        self.cb_del_wrapping.setChecked(True)

        tt = _("Select text and use the shortcut key '{}' to copy, the copied text will not be automatically translated") \
            .format("Ctrl+Shift+C")
        self.te_from.setToolTip(tt)
        self.te_to.setToolTip(tt)

        self.sts(["Ctrl+Shift+C", "Alt+D", "Alt+C", "Ctrl+T",
                  "Ctrl+,", "Ctrl+Q", "Ctrl+H"],
                 [self._copy_text, self._del_wrapping, self._add_old,
                  self.update_translate, self._open_prf, self._quit_app,
                  self.hide])

    def _copy_text(self):
        """复制，但是不进行翻译
        """
        if self.te_from.hasFocus() and self.te_from.textCursor().hasSelection():
            self.translate_next = False
            self.te_from.copy()
        elif self.te_to.hasFocus() and self.te_to.textCursor().hasSelection():
            self.translate_next = False
            self.te_to.copy()

    def sts(self, keys, fs):
        """批量快捷键

        Args:
            keys (_type_): _description_
            fs (_type_): _description_
        """
        for k, f in zip(keys, fs):
            QShortcut(QKeySequence(k), self).activated.connect(f)

    def _quit_app(self):

        re = QMessageBox.warning(self, _("warn"), _("quit?"),
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                 QMessageBox.StandardButton.No)
        if re == QMessageBox.StandardButton.Yes:
            self.setVisible(False)
            self.app.quit()

    def _add_old(self):
        self.cb_add_old.setChecked(not self.cb_add_old.isChecked())

    def _del_wrapping(self):
        self.cb_del_wrapping.setChecked(not self.cb_del_wrapping.isChecked())

    def _open_prf(self):
        self.tray.open_prf()

    def _on_server_changed(self):
        if not self.jn:
            # 初始化时
            return
        i = self.cb_server.currentIndex()
        j = lang_n2j(i, self.sg.g("lang-selected-n", 0, int))

        self.jn = j == 0
        self.cb_lang.clear()
        self.cb_lang.addItems(get_lang_names(i))
        self.jn = True
        if j != 0:
            # 新设置会是0，无需再设置
            self.cb_lang.setCurrentIndex(j)

        self.sg.s("server-selected-key", get_server_t(i).key)

    def _on_lang_changed(self):
        if not self.jn:
            return
        j = self.cb_lang.currentIndex()

        if j < 0:
            # self.cb_lang.clear()
            return
        i = self.cb_server.currentIndex()
        n = get_lang(i, j).n
        self.sg.s("lang-selected-n", n)
        n = self.sg.g("lang-selected-n", 0, int)

        server: Server = get_server_t(i)
        if server.key != self.server_t.key:
            self.server_t = server
        self.lang_t = get_lang(i, j)
        self.update_translate()

    def ocr_image(self, img_path):
        """_summary_

        Args:
            img_path (str): _description_

        Returns:
            _type_: _description_
        """
        def oo(_p=None):
            try:
                _ok, text_from = self.server_o.ocr_image(img_path)
            except Exception as e:  # pylint: disable=W0718
                get_logger().error(e)
                text_from = f"OCR error: {self.server_o.name}\
                    \n\n{str(e)}\n\n{traceback.format_exc()}"
                _ok = False
            return (_ok, text_from)

        def next_(param):
            _ok, s = param
            self.translate_text(s)

        self.set_text_from_to((_("OCRing..."), _("OCRing...")), True)
        self.my_thread = MyThread(oo)
        self.my_thread.signal.connect(next_)
        self.my_thread.start()

    def set_text_from_to(self, text, loading=False):
        """_summary_

        Args:
            text (_type_): _description_
        """
        text_from, text_to = text
        self.te_from.setPlainText(text_from)
        self.te_to.setPlainText(text_to)

        if not loading:
            if self.sg.g("notify-translation-results", d=True, t=bool):
                self.tray.showMessage(_("Translation completed"), text_to,
                                      QSystemTrayIcon.MessageIcon.Information, 2000)

            self.text_last = text_from
            self.my_thread.clean_up()

    def update_translate(self):
        """无参数翻译
        """
        self.translate_text(self.te_from.toPlainText())

    def translate_text(self, text_from):
        """翻译

        Returns:
            _type_: _description_
        """
        if not self.translate_next:
            self.translate_next = True
            return
        self.translate_next = True

        s_ntt = _(
            "This time the content contains private information and is not translated")
        ss_ntt = []
        for ntt in NO_TRANSLATED_TXTS:
            if ntt in text_from:
                ss_ntt.append(ntt)
        if len(ss_ntt) > 0:
            self.tray.showMessage(_("Not translated this time!"),
                                  f"{s_ntt}:\n{str(ss_ntt)}",
                                  QSystemTrayIcon.MessageIcon.Warning, 3000)

            return

        if self.cb_del_wrapping.isChecked():
            text_from = process_text(text_from)

        if self.cb_add_old.isChecked():
            text_from = self.text_last + " " + text_from

        if not text_from:
            return

        def tt(_p=None):
            try:
                _ok, text_to = self.server_t.translate_text(
                    text_from, self.lang_t.key)
            except Exception as e:  # pylint: disable=W0718
                get_logger().error(e)
                text_to = _("something error: {}")\
                    .format(f"{self.server_t.name}\n\n{str(e)}\n\n{traceback.format_exc()}")
            return (text_from, text_to)

        self.set_text_from_to((text_from, _("Translating...")), True)

        self.my_thread = MyThread(tt)
        self.my_thread.signal.connect(self.set_text_from_to)
        self.my_thread.start()
