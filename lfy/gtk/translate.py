'''翻译主窗口'''

import threading
import traceback
from gettext import gettext as _

from gi.repository import Adw, Gdk, GLib, Gtk

from lfy.api import (create_server_o, create_server_t, get_lang,
                     get_lang_names, get_server_names_t, get_server_t,
                     lang_n2j, server_key2i)
from lfy.api.constant import NO_TRANSLATED_TXTS
from lfy.api.server import Server
from lfy.api.server.ocr import ServerOCR
from lfy.api.server.tra import ServerTra
from lfy.gtk.notify import nf_t
from lfy.gtk.widgets.theme_switcher import ThemeSwitcher
from lfy.utils import process_text
from lfy.utils.debug import get_logger
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.app = self.get_application()

        self.sg = Settings()

        self.tra_server = None
        self.ocr_server = None
        # 翻译的key
        self.lang_t = None

        self.jn = False
        # 可能包含上次的追加内容
        self.last_text = ""
        # 是不是软件内复制的，这种可能是想粘贴到其他地方，不响应即可
        self.is_tv_copy = False
        # 放置初始化时，不断调用误以为选择
        self.toast = Adw.Toast.new("")
        self.toast.set_timeout(2)

        self.dd_server.set_model(Gtk.StringList.new([_("Loading")]))
        self.dd_lang.set_model(Gtk.StringList.new([_("Loading")]))

        self.menu_btn.props.popover.add_child(ThemeSwitcher(), 'theme')

        self.connect('unrealize', self.save_settings)

        # 创建键盘事件控制器
        controller = Gtk.EventControllerKey()
        controller.connect("key-pressed", self.on_key_pressed)
        # 将控制器添加到文本视图中
        self.tv_from.add_controller(controller)

        threading.Thread(target=self._get_data, daemon=True).start()

    def _get_data(self):
        """异步获取数据
        """
        server_key_t = self.sg.g("server-selected-key")
        i = server_key2i(server_key_t)

        self.tra_server = create_server_t(server_key_t)
        self.ocr_server = create_server_o(self.sg.g("server-ocr-selected-key"))

        data_s = Gtk.StringList.new(get_server_names_t())

        GLib.idle_add(self._set_data, data_s, i)

    def _set_data(self, data_s, i):
        """异步初始化
        """
        self.dd_server.set_model(data_s)
        self.jn = True
        self.dd_server.set_selected(i)

    def on_key_pressed(self, _, keyval, _keycode, _state):
        """文本回车，直接翻译

        Args:
            _ (controller): _description_
            keyval (keyval): _description_
            _keycode (keycode): _description_
            _state (state): _description_

        Returns:
            bool: 继续执行默认行为
        """
        if keyval == Gdk.KEY_Return:
            # 加上下面的 可以是ctrl return
            #  and (state & Gdk.ModifierType.CONTROL_MASK)
            self.update("reload", True)
        return False  # 返回 False 以继续执行默认行为

    def save_settings(self, _a):
        """保存设置

        Args:
            _a (TranslateWindow): _description_
        """

        self.sg.s("server-selected-key", self.tra_server.key)
        self.sg.s("lang-selected-n", self.lang_t.n)

    @Gtk.Template.Callback()
    def _on_server_changed(self, drop_down, _a):

        if not self.jn:
            return

        i = drop_down.get_selected()

        lang_select_index = lang_n2j(i, self.sg.g("lang-selected-n"))
        self.jn = False
        self.dd_lang.set_model(Gtk.StringList.new(get_lang_names(i)))
        self.jn = True
        self.dd_lang.set_selected(lang_select_index)

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
        self.update(self.last_text, True)

    @Gtk.Template.Callback()
    def _set_tv_copy(self, _a):
        self.is_tv_copy = True

    def update_ocr(self, path):
        """执行ocr文本识别

        Args:
            path (str): _description_
        """

        _k = self.sg.g("server-ocr-selected-key")
        if _k != self.ocr_server.key:
            self.ocr_server = create_server_o(_k)

        threading.Thread(target=self.request_text, daemon=True,
                         args=(path, self.ocr_server, None,)).start()

    def update(self, text, reload=False, del_wrapping=True):
        """翻译

        Args:
            text (str): _description_
            reload (bool, optional): _description_. Defaults to False.
        """
        buffer_from = self.tv_from.get_buffer()

        if len(text) == 0:
            return

        # 导出或者导入的配置包含密钥，不翻译
        s_ntt = _(
            "This time the content contains private information and is not translated")
        ss_ntt = []
        for ntt in NO_TRANSLATED_TXTS:
            if ntt in text:
                ss_ntt.append(ntt)
        if len(ss_ntt) > 0:
            buffer_from.set_text(f"{s_ntt}:\n{str(ss_ntt)}")
            return

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
        print("======", text)

        threading.Thread(target=self.request_text, daemon=True,
                         args=(text, self.tra_server, self.lang_t.key,)).start()

    def request_text(self, s, server, lk=None):
        """子线程翻译

        Args:
            s (str): _description_
            server (Server): _description_
        """
        is_ocr = lk is None
        GLib.idle_add(self.update_ui, "", is_ocr, server.name)

        try:
            if is_ocr:
                server: ServerOCR = server
                _ok, text = server.ocr_image(s)
                if self.cbtn_del_wrapping.get_active():
                    text = process_text(text)
            else:
                server: ServerTra = server
                _ok, text = server.translate_text(s, lk)

        except Exception as e:  # pylint: disable=W0718
            get_logger().error(e)
            text = _("something error: {}")\
                .format(f"{server.name}\n\n{str(e)}\n\n{traceback.format_exc()}")
        GLib.idle_add(self.update_ui, text, is_ocr)

    def update_ui(self, s="", ocr=False, name=""):
        """更新界面

        Args:
            s (str, optional): 翻译以后的文本. Defaults to True.
            ocr (bool, optional): OCR. Defaults to False.
        """
        if len(s) == 0:
            # 开始翻译
            self.sp_translate.start()
            if ocr:
                self.tv_from.get_buffer().set_text(_("{} OCRing...").format(name))
            else:
                self.tv_to.get_buffer().set_text(_("Translating..."))
            return

        # 翻译完成
        try:
            if ocr:
                self.tv_from.get_buffer().set_text(s)
                self.update(s)
                return

            self.tv_to.get_buffer().set_text(s)
            nf_t(self.app, f"{self.tra_server.name} " +
                 _("Translation completed"), s)
        except TypeError as e:
            get_logger().error(e)
            em = _("something error: {}")\
                .format(f"\n\n{str(e)}\n\n{traceback.format_exc()}")
            self.tv_to.get_buffer().set_text(em)
        self.sp_translate.stop()

    def notice_action(self, cbtn: Gtk.CheckButton, text_ok, text_no):
        """_summary_

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
        """_summary_

        Args:
            toast_msg (str): _description_
        """
        self.toast.dismiss()
        self.toast.set_title(toast_msg)
        self.ato_translate.add_toast(self.toast)
