'翻译主窗口'
from gettext import gettext as _

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QHBoxLayout, QMainWindow,
                             QPushButton, QSplitter, QTextEdit, QVBoxLayout,
                             QWidget)

from lfy import APP_NAME
from lfy.api import (create_server_o, create_server_t, get_lang,
                     get_lang_names, get_server_names_t, get_server_t,
                     lang_n2j, server_key2i)
from lfy.api.server import Server
from lfy.api.utils.settings import Settings
from lfy.qt.utils import MyThread


class TranslateWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(_(APP_NAME))
        self.setGeometry(100, 100, 600, 400)
        # 创建中心部件
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        bottom_widget = QWidget(self)
        bottom_layout = QVBoxLayout(bottom_widget)
        splitter = QSplitter(Qt.Orientation.Vertical, self)

        # 上面的文本编辑框
        self.te_from = QTextEdit(self)

        # 中间的布局（包含选择按钮和普通按钮）
        middle_widget = QWidget(self)
        middle_layout = QHBoxLayout(middle_widget)

        # 左边的两个下拉框（QComboBox）
        self.cb_server = QComboBox(self)
        self.cb_server.currentIndexChanged.connect(self._on_server_changed)

        self.cb_lang = QComboBox(self)
        self.cb_lang.setEditable(True)
        self.cb_lang.currentIndexChanged.connect(self._on_lang_changed)

        # 右边的两个选择按钮
        self.cb_del_wrapping = QCheckBox("", self)
        self.cb_add_old = QCheckBox("", self)
        # 普通按钮
        self.btn_translate = QPushButton(_("translate"), self)

        middle_layout.addWidget(self.cb_server)
        middle_layout.addWidget(self.cb_lang)
        middle_layout.addStretch(1)  # 用来拉伸中间部分
        middle_layout.addWidget(self.cb_del_wrapping)
        middle_layout.addWidget(self.cb_add_old)
        middle_layout.addWidget(self.btn_translate)

        # 下面的文本编辑框
        self.te_to = QTextEdit(self)

        bottom_layout.addWidget(middle_widget)
        bottom_layout.addWidget(self.te_to)

        splitter.addWidget(self.te_from)
        splitter.addWidget(bottom_widget)

        main_layout.addWidget(splitter)

        self.jn = False
        self.server_t = None
        self.lang_t = None
        self.thread = None

        self.set_data()

    def set_data(self):
        self.s = Settings()

        self.btn_translate.clicked.connect(self.translate_text)
        self.cb_add_old.setToolTip(_(
            "Alt + C: Splice the next copied text with the previous text"))

        self.cb_del_wrapping.setToolTip(_(
            "Alt + D: Remove symbols such as line breaks"))

        server_key_t = self.s.g("server-selected-key", "bing")
        server_key_o = self.s.g("server_ocr_selected_key", "baidu")

        self.server_t = create_server_t(server_key_t)
        self.server_o = create_server_o(server_key_o)

        self.cb_server.addItems(get_server_names_t())
        i = server_key2i(server_key_t)
        self.cb_server.setCurrentIndex(i)
        n = self.s.g("lang-selected-n", 0, int)
        j = lang_n2j(i, n)
        self.lang_t = get_lang(i, j)
        self.cb_lang.setCurrentIndex(j)

    def _on_server_changed(self):
        i = self.cb_server.currentIndex()
        j = lang_n2j(i, self.s.g("lang-selected-n", 0, int))
        self.jn = False
        self.cb_lang.clear()
        self.cb_lang.addItems(get_lang_names(i))
        self.jn = True
        self.cb_lang.setCurrentIndex(j)

        self.s.s("server-selected-key", get_server_t(i).key)

    def _on_lang_changed(self):
        if not self.jn:
            return
        i = self.cb_server.currentIndex()
        j = self.cb_lang.currentIndex()
        n = get_lang(i, j).n
        self.s.s("lang-selected-n", n)
        n = self.s.g("lang-selected-n", 0, int)

        server: Server = get_server_t(i)
        if server.key != self.server_t.key:
            self.server_t = server
        self.lang_t = get_lang(i, j)
        self.translate_text()

    def ocr_image(self, img_path):
        def oo(p=None):
            print(p)
            _ok, text_from = self.server_o.ocr_image(
                img_path, self.lang_t.key)
            return (_ok, text_from)
        def next_(param):
            _ok, s = param
            if not _ok:
                self.set_ui((s, "文本识别失败！"))
                return
            self.set_ui((s, "文本识别成功！"))
            self.translate_text()

        self.set_ui(("识别中", "..."))
        self.thread = MyThread(oo)
        self.thread.signal.connect(next_)
        self.thread.start()

    def set_text_from_to(self, text):
        text_from, text_to = text
        self.te_from.setPlainText(text_from)
        self.te_to.setPlainText(text_to)
        self.thread = None


    def translate_text(self):
        text_from = self.te_from.toPlainText()
        if not text_from:
            print("no")
            return

        def tt(p=None):
            print(p)
            _ok, text_to = self.server_t.translate_text(
                text_from, self.lang_t.key)
            return (text_from, text_to)

        self.set_text_from_to((text_from, "翻译中..."))

        self.thread = MyThread(tt)
        self.thread.signal.connect(self.set_text_from_to)
        self.thread.start()
