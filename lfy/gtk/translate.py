"""翻译主窗口"""
import threading
from gettext import gettext as _

from gi.repository import Adw, Gdk, GLib, Gtk # type: ignore

from lfy.api import (create_server_o, create_server_t, get_lang,
                     get_lang_names, get_server_names_t, get_server_t,
                     lang_n2j, server_key2i)
from lfy.api.server import Server, Lang
from lfy.gtk.notify import nf_t
from lfy.gtk.widgets.theme_switcher import ThemeSwitcher
from lfy.utils import process_text
from lfy.utils.settings import Settings


@Gtk.Template(resource_path='/cool/ldr/lfy/translate.ui')
class TranslateWindow(Adw.ApplicationWindow):
    """
    翻译窗口
    """
    __gtype_name__ = 'TranslateWindow'

    tv_from: Gtk.TextView = Gtk.Template.Child()
    tv_to: Gtk.TextView = Gtk.Template.Child()
    dd_server: Gtk.DropDown = Gtk.Template.Child()
    dd_lang: Gtk.DropDown = Gtk.Template.Child()
    dd_lang_from: Gtk.DropDown = Gtk.Template.Child()
    cb_add_old: Gtk.CheckButton = Gtk.Template.Child()
    cb_del_wrapping: Gtk.CheckButton = Gtk.Template.Child()
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
        self.lang_t:Lang = None
        self.lang_from_t:Lang = None

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
        self.dd_lang_from.set_expression(Gtk.PropertyExpression.new(Gtk.StringObject, None, "string"))

        # 0的再设置也无效
        self.jn = i == 0
        self.dd_server.set_model(Gtk.StringList.new(get_server_names_t()))
        self.jn = True
        self.dd_server.set_selected(i)

        self.menu_btn.props.popover.add_child(ThemeSwitcher(), 'theme')

        self.connect('unrealize', self._save_settings)

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
            state (state): _description_

        Returns:
            bool: 继续执行默认行为
        """
        if keyval == Gdk.KEY_Return and (state & Gdk.ModifierType.CONTROL_MASK):
            self.translate_text("reload", True)
        return False  # 返回 False 以继续执行默认行为

    def _save_settings(self, _a):
        """保存设置
        """
        if not self.is_maximized():
            size = self.get_default_size()
            self.sg.s("window-width", size.width)
            self.sg.s("window-height", size.height)

        self.sg.s("server-selected-key", self.tra_server.key)
        self.sg.s("lang-selected-n", self.lang_t.n)
        self.sg.s("lang-from-selected-n", self.lang_from_t.n)

    @Gtk.Template.Callback()
    def _on_server_changed(self, drop_down, _a):
        """
        翻译服务选择
        Args:
            drop_down:
            _a:

        Returns:

        """
        if not self.jn:
            return

        i = drop_down.get_selected()

        j = lang_n2j(i, self.sg.g("lang-selected-n"))
        j_from = lang_n2j(i, self.sg.g("lang-from-selected-n"))

        self.jn = False
        # 手动调用 _on_lang_changed
        self.dd_lang.set_model(Gtk.StringList.new(get_lang_names(i)))
        self.dd_lang_from.set_model(Gtk.StringList.new(get_lang_names(i)))
        self.dd_lang.set_selected(j)
        self.dd_lang_from.set_selected(j_from)
        self.jn = True
        self._on_lang_changed(None, None)

    @Gtk.Template.Callback()
    def _on_lang_changed(self, _drop_down, _a):
        if not self.jn:
            return

        i = self.dd_server.get_selected()
        j = self.dd_lang.get_selected()
        j_from = self.dd_lang_from.get_selected()

        server: Server = get_server_t(i)
        if server.key != self.tra_server.key:
            self.tra_server = server
        self.lang_t = get_lang(i, j)
        self.lang_from_t = get_lang(i, j_from)

        self._save_settings(None)
        self.translate_text(self.last_text, True)

    @Gtk.Template.Callback()
    def _set_tv_copy(self, _a):
        """
        快捷键复制剪贴时触发，防止翻译
        Args:
            _a:

        Returns:

        """
        self.is_tv_copy = True

    def ocr_image(self, path: str):


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
            del_wrapping (bool, optional): _description_. Defaults to True.
        """

        if not text:
            return

        buffer_from = self.tv_from.get_buffer()

        if not reload:
            if self.is_tv_copy:
                self.is_tv_copy = False
                return

            if self.cb_add_old.get_active():
                text = f"{self.last_text} {text}"
            if self.cb_del_wrapping.get_active() and del_wrapping:
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
        """

        def _ing():
            self.sp_translate.start()
            self.tv_to.get_buffer().set_text(_("Translating..."))

        def _ed(s2):
            self.tv_to.get_buffer().set_text(s2)
            nf_t(self.app, f"{self.tra_server.name} " +
                 _("Translation completed"), s2)
            self.sp_translate.stop()

        GLib.idle_add(_ing)
        _ok, text = self.tra_server.main(s, self.lang_t.key, self.lang_from_t.key)
        GLib.idle_add(_ed, text)

    def req_ocr(self, s):
        """子线程翻译

        Args:
            s (str): _description_
        """

        def _ing(name):
            self.sp_translate.start()
            self.tv_from.get_buffer().set_text(_("{} OCRing...").format(name))

        def _ed(s2):
            self.tv_from.get_buffer().set_text(s2)
            self.translate_text(s2)

        GLib.idle_add(_ing, self.ocr_server.name)

        _ok, text = self.ocr_server.main(s)
        if _ok and self.cb_del_wrapping.get_active():
            text = process_text(text)
        GLib.idle_add(_ed, text)

    def notice_action(self, cb: Gtk.CheckButton, text_ok, text_no):
        """在 main.py 中的通知

        Args:
            cb (Gtk.CheckButton): _description_:
            text_ok (_type_): _description_
            text_no (_type_): _description_
        """

        cb.set_active(not cb.get_active())
        if not cb.get_active():
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
