'''翻译主窗口'''
# pylint: disable=E1101
import threading
from gettext import gettext as _

from gi.repository import Adw, Gdk, GLib, Gtk

from lfy.api import (create_server_o, create_server_t, get_lang,
                     get_lang_names, get_server_names_t, get_server_t,
                     lang_n2j, server_key2i)
from lfy.api.server import Server
from lfy.gtk.notify import nf_t
from lfy.gtk.widgets.theme_switcher import ThemeSwitcher
from lfy.utils import process_text
from lfy.utils.settings import Settings


@Gtk.Template(resource_path='/cool/ldr/lfy/translate.ui')
class TranslateWindow(Adw.ApplicationWindow):
    """翻译窗口

    Args:
        Adw (_type_): _description_

    Returns:
        _type_: _description_
    """
    __gtype_name__ = 'TranslateWindow'

    tv_from: Gtk.TextView = Gtk.Template.Child()
    tv_to: Gtk.TextView = Gtk.Template.Child()
    dd_server: Gtk.DropDown = Gtk.Template.Child()
    dd_lang: Gtk.DropDown = Gtk.Template.Child()
    cbtn_add_old: Gtk.CheckButton = Gtk.Template.Child()
    cbtn_del_wrapping: Gtk.CheckButton = Gtk.Template.Child()
    sp_translate: Gtk.Spinner = Gtk.Template.Child()
    menu_btn: Gtk.MenuButton = Gtk.Template.Child()
    ato_translate: Adw.ToastOverlay = Gtk.Template.Child()
    gp_translate: Gtk.Paned = Gtk.Template.Child()
    header_bar: Adw.HeaderBar = Gtk.Template.Child()

    def __init__(self, application):

        self.app = application

        self.sg = Settings()

        super().__init__(
            application=application,
            default_width=self.sg.g("window-width"),
            default_height=self.sg.g("window-height")
        )

        # 翻译的key
        self.lang_t = None

        self.jn = False
        # 可能包含上次的追加内容
        self.last_text = ""
        # 是不是软件内复制的，这种可能是想粘贴到其他地方，不响应即可
        self.is_tv_copy = False

        server_key_t = self.sg.g("server-selected-key")
        i = server_key2i(server_key_t)

        self.tra_server = create_server_t(server_key_t)
        self.ocr_server = create_server_o(self.sg.g("server-ocr-selected-key"))

        self.dd_server.set_expression(Gtk.PropertyExpression.new(Gtk.StringObject, None, "string"))
        self.dd_lang.set_expression(Gtk.PropertyExpression.new(Gtk.StringObject, None, "string"))

        # 0的再设置也无效
        self.jn = i == 0
        self.dd_server.set_model(Gtk.StringList.new(get_server_names_t()))
        self.jn = True
        self.dd_server.set_selected(i)

        self.menu_btn.props.popover.add_child(ThemeSwitcher(), 'theme')

        self.connect('unrealize', self.save_settings)

        # 创建键盘事件控制器
        controller = Gtk.EventControllerKey()
        controller.connect("key-pressed", self.on_key_pressed)
        # 将控制器添加到文本视图中
        self.tv_from.add_controller(controller)

    def on_key_pressed(self, _, keyval, _keycode, state):
        """文本回车，直接翻译

        Args:
            _ (controller): _description_
            keyval (keyval): _description_
            _keycode (keycode): _description_
            _state (state): _description_

        Returns:
            bool: 继续执行默认行为
        """
        if keyval == Gdk.KEY_Return and (state & Gdk.ModifierType.CONTROL_MASK):
            self.translate_text("reload", True)
        return False  # 返回 False 以继续执行默认行为

    def save_settings(self, _a):
        """保存设置

        Args:
            _a (TranslateWindow): _description_
        """
        if not self.is_maximized():
            size = self.get_default_size()
            self.sg.s("window-width", size.width)
            self.sg.s("window-height", size.height)

        self.sg.s("server-selected-key", self.tra_server.key)
        self.sg.s("lang-selected-n", self.lang_t.n)

    @Gtk.Template.Callback()
    def _on_server_changed(self, drop_down, _a):

        if not self.jn:
            return

        i = drop_down.get_selected()

        j = lang_n2j(i, self.sg.g("lang-selected-n"))
        # 0的再设置也无效
        self.jn = j == 0
        self.dd_lang.set_model(Gtk.StringList.new(get_lang_names(i)))
        self.jn = True
        self.dd_lang.set_selected(j)

    @Gtk.Template.Callback()
    def _on_lang_changed(self, _drop_down, _a):
        if not self.jn:
            return

        i = self.dd_server.get_selected()
        j = self.dd_lang.get_selected()

        server: Server = get_server_t(i)
        if server.key != self.tra_server.key:
            self.tra_server = server
        self.lang_t = get_lang(i, j)

        self.save_settings("")
        self.translate_text(self.last_text, True)

    @Gtk.Template.Callback()
    def _set_tv_copy(self, _a):
        self.is_tv_copy = True

    def ocr_image(self, path):
        """执行ocr文本识别

        Args:
            path (str): _description_
        """

        _k = self.sg.g("server-ocr-selected-key")
        if _k != self.ocr_server.key:
            self.ocr_server = create_server_o(_k)

        threading.Thread(target=self.req_ocr, daemon=True,
                         args=(path,)).start()

    def translate_text(self, text, reload=False, del_wrapping=True):
        """翻译

        Args:
            text (str): _description_
            reload (bool, optional): _description_. Defaults to False.
        """

        if not text:
            return

        buffer_from = self.tv_from.get_buffer()

        if not reload:
            if self.is_tv_copy:
                self.is_tv_copy = False
                return

            if self.cbtn_add_old.get_active():
                text = f"{self.last_text} {text}"
            if self.cbtn_del_wrapping.get_active() and del_wrapping:
                text = process_text(text)
            self.last_text = text
            buffer_from.set_text(text)

        start_iter, end_iter = buffer_from.get_bounds()
        text = buffer_from.get_text(start_iter, end_iter, False)

        threading.Thread(target=self.req_tra, daemon=True,
                         args=(text,)).start()

    def req_tra(self, s):
        """子线程翻译

        Args:
            s (str): _description_
            server (Server): _description_
        """

        def _ing():
            self.sp_translate.start()
            self.tv_to.get_buffer().set_text(_("Translating..."))

        def _ed(s):
            self.tv_to.get_buffer().set_text(s)
            nf_t(self.app, f"{self.tra_server.name} " +
                 _("Translation completed"), s)
            self.sp_translate.stop()

        GLib.idle_add(_ing)
        _ok, text = self.tra_server.main(s, self.lang_t.key)
        GLib.idle_add(_ed, text)

    def req_ocr(self, s):
        """子线程翻译

        Args:
            s (str): _description_
            server (Server): _description_
        """

        def _ing(name):
            self.sp_translate.start()
            self.tv_from.get_buffer().set_text(_("{} OCRing...").format(name))

        def _ed(s):
            self.tv_from.get_buffer().set_text(s)
            self.translate_text(s)

        GLib.idle_add(_ing, self.ocr_server.name)

        _ok, text = self.ocr_server.main(s)
        if _ok and self.cbtn_del_wrapping.get_active():
            text = process_text(text)
        GLib.idle_add(_ed, text)

    def notice_action(self, cbtn: Gtk.CheckButton, text_ok, text_no):
        """在 main.py 中的通知

        Args:
            ok (_type_): _description_
            text_ok (_type_): _description_
            text_no (_type_): _description_
        """

        cbtn.set_active(not cbtn.get_active())
        if not cbtn.get_active():
            self.toast_msg(text_ok)
        else:
            self.toast_msg(text_no)

    def toast_msg(self, toast_msg):
        """在 main.py 中的通知

        Args:
            toast_msg (str): _description_
        """
        # 放置初始化时，不断调用误以为选择
        toast = Adw.Toast.new("")
        toast.set_timeout(2)
        toast.dismiss()
        toast.set_title(toast_msg)
        self.ato_translate.add_toast(toast)
