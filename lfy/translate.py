'''翻译主窗口'''

import re
import threading
import time
import traceback
from gettext import gettext as _

from gi.repository import Adw, GLib, Gtk

from lfy.api import translate_by_server
from lfy.api.base import Server
from lfy.api.utils import (create_server, get_lang, get_lang_names, get_server,
                           get_server_names, lang_n2j, server_key2i)
from lfy.settings import Settings
from lfy.widgets.theme_switcher import ThemeSwitcher


# pylint: disable=E1101
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setting = Settings.get()
        # 可能包含上次的追加内容
        self.last_text = ""
        # 这次复制的
        self.last_text_one = ""
        # 是不是软件内复制的，这种可能是想粘贴到其他地方，不响应即可
        self.is_tv_copy = False
        # 放置初始化时，不断调用误以为选择
        self.creat_time = time.time()
        self.toast = Adw.Toast.new("")
        self.toast.set_timeout(2)

        i = server_key2i(self.setting.server_selected_key)
        self.tran_server = create_server(self.setting.server_selected_key)
        self.jn = True

        self.dd_server.set_model(get_server_names())
        self.dd_server.set_selected(i)

        self.dd_lang.set_model(get_lang_names(i))
        self.dd_lang.set_selected(lang_n2j(i, self.setting.lang_selected_n))

        self.menu_btn.props.popover.add_child(ThemeSwitcher(), 'theme')

        self.connect('unrealize', self.save_settings)

    def save_settings(self, _a):
        """_summary_

        Args:
            a (TranslateWindow): _description_
        """
        if not self.is_maximized():
            size = self.get_default_size()
            Settings.get().window_size = (size.width, size.height)

        i = self.dd_server.get_selected()
        j = self.dd_lang.get_selected()
        self.setting.server_selected_key = get_server(i).key
        n = get_lang(i, j).n
        self.setting.lang_selected_n = n
        print("保存", i, j, n)

    @Gtk.Template.Callback()
    def _on_server_changed(self, drop_down, _a):
        # 初始化，会不断调用这个
        if time.time() - self.creat_time > 1:
            i = drop_down.get_selected()
            lang_select_index = lang_n2j(i, self.setting.lang_selected_n)
            # 等于0时_on_lang_changed不会相应多次
            self.jn = lang_select_index == 0

            self.dd_lang.set_model(get_lang_names(i))
            # 如果不是0,这时候_on_lang_changed还会被调用
            self.dd_lang.set_selected(lang_select_index)

    @Gtk.Template.Callback()
    def _on_lang_changed(self, _drop_down, _a):
        if time.time() - self.creat_time > 1:
            # 改变 _on_server_changed 时，这个函数会被调用两次
            if self.jn:
                self.save_settings("")
                self.update(self.last_text, True)
            self.jn = True

    @Gtk.Template.Callback()
    def _set_tv_copy(self, _a):
        self.is_tv_copy = True

    def update(self, text, reload=False, del_wrapping=True):
        """翻译

        Args:
            text (_type_): _description_
            reload (bool, optional): _description_. Defaults to False.
        """
        if len(text) == 0:
            return

        buffer_from = self.tv_from.get_buffer()
        if not reload:
            if self.last_text_one == text or self.is_tv_copy:
                self.is_tv_copy = False
                return
            self.last_text_one = text
            if self.cbtn_add_old.get_active():
                text = f"{self.last_text} {text}"
            if self.cbtn_del_wrapping.get_active() and del_wrapping:
                text = self.process_text(text)
            self.last_text = text
            buffer_from.set_text(text)

        start_iter, end_iter = buffer_from.get_bounds()
        text = buffer_from.get_text(start_iter, end_iter, False)

        i = self.dd_server.get_selected()
        server: Server = get_server(i)
        if server.key != self.tran_server.key:
            print(f"翻译服务器改变:{self.tran_server.key}->{server.key}")
            self.tran_server = server
        lk = get_lang(i, self.dd_lang.get_selected()).key

        threading.Thread(target=self.request_text, daemon=True,
                         args=(text, self.tran_server, lk,)).start()

    def request_text(self, text, server, lk):
        """子线程翻译

        Args:
            text (str): _description_
            i (server_key_i): _description_
            j (lang_key_j): _description_
        """
        GLib.idle_add(self.update_ui, "")
        text_translated = translate_by_server(text, server, lk)
        GLib.idle_add(self.update_ui, text_translated)

    def update_ui(self, s=""):
        """更新界面

        Args:
            s (bool, optional): 翻译以后的文本. Defaults to True.
        """
        if len(s) == 0:
            # 开始翻译
            self.sp_translate.start()
            self.tv_to.get_buffer().set_text(_("Translating.."))
        else:
            # 翻译完成
            try:
                self.tv_to.get_buffer().set_text(s)
            except TypeError as e:
                error_msg = _("something error:")
                error_msg = f"{error_msg}\n\n{str(e)}\n\n{traceback.format_exc()}"
                self.tv_to.get_buffer().set_text(error_msg)

            self.sp_translate.stop()

    def process_text(self, text):
        """文本预处理

        Args:
            text (str): _description_

        Returns:
            str: _description_
        """
        # 删除空行
        s_from = re.sub(r'\n\s*\n', '\n', text)
        # 删除多余空格
        s_from = re.sub(r' +', ' ', s_from)
        # 删除所有换行，除了句号后面的换行
        s_from = re.sub(r"-[\n|\r]+", "", s_from)
        s_from = re.sub(r"(?<!\.|-|。)[\n|\r]+", " ", s_from)
        return s_from

    def notice_action(self, cbtn: Gtk.CheckButton, text_ok, text_no):
        """_summary_

        Args:
            ok (_type_): _description_
            text_ok (_type_): _description_
            text_no (_type_): _description_
        """
        if time.time() - self.creat_time > 1:
            cbtn.set_active(not cbtn.get_active())
            if not cbtn.get_active():
                self.toast_msg(text_ok)
            else:
                self.toast_msg(text_no)

    def toast_msg(self, toast_msg):
        """_summary_

        Args:
            text (str): _description_
        """
        self.toast.dismiss()
        self.toast.set_title(toast_msg)
        self.ato_translate.add_toast(self.toast)
