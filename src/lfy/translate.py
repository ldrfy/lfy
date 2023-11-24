'''翻译主窗口'''

import re
import threading
import time

from gi.repository import Adw, GLib, Gtk

from lfy.api import translate_by_server
from lfy.api.server import (get_lang, get_lang_names, get_server,
                            get_server_names, lang_n2j, server_key2i)
from lfy.settings import Settings
from lfy.widgets.theme_switcher import ThemeSwitcher


@Gtk.Template(resource_path='/cool/ldr/lfy/translate.ui')
class TranslateWindow(Adw.ApplicationWindow):
    """翻译窗口

    Args:
        Adw (_type_): _description_

    Returns:
        _type_: _description_
    """
    __gtype_name__ = 'TranslateWindow'

    # btn_translate: Gtk.Button = Gtk.Template.Child()
    tv_from: Gtk.TextView = Gtk.Template.Child()
    tv_to: Gtk.TextView = Gtk.Template.Child()
    dd_server: Gtk.DropDown = Gtk.Template.Child()
    dd_lang: Gtk.DropDown = Gtk.Template.Child()
    cbtn_add_old: Gtk.CheckButton = Gtk.Template.Child()
    cbtn_del_wrapping: Gtk.CheckButton = Gtk.Template.Child()
    sp_translate: Gtk.Spinner = Gtk.Template.Child()
    menu_btn: Gtk.MenuButton = Gtk.Template.Child()

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
        n = self.setting.lang_selected_n
        i = server_key2i(self.setting.server_selected_key)

        self.dd_server.set_model(Gtk.StringList.new(get_server_names()))
        self.dd_server.set_selected(i)
        self.dd_lang.set_model(Gtk.StringList.new(get_lang_names(i)))
        self.dd_lang.set_selected(lang_n2j(i, n))

        # Theme Switcher
        theme_switcher = ThemeSwitcher()
        self.menu_btn.props.popover.add_child(theme_switcher, 'theme')

        # Save settings on close
        self.connect('unrealize', self.save_settings)


    def save_settings(self, *args, **kwargs):
        if not self.is_maximized():
            size = self.get_default_size()
            Settings.get().window_size = (size.width, size.height)

        i = self.dd_server.get_selected()
        j = self.dd_lang.get_selected()
        self.setting.server_selected_key = get_server(i).key
        self.setting.lang_selected_n = get_lang(i, j).n


    @Gtk.Template.Callback()
    def _on_translate_clicked(self, btn):
        self.update(self.last_text, True)

    @Gtk.Template.Callback()
    def _on_server_changed(self, drop_down, a):
        # 初始化，会不断调用这个
        if time.time() - self.creat_time > 1:
            i = drop_down.get_selected()
            n = self.setting.lang_selected_n
            self.dd_lang.set_model(Gtk.StringList.new(get_lang_names(i)))
            self.dd_lang.set_selected(lang_n2j(i, n))

    @Gtk.Template.Callback()
    def _on_lang_changed(self, drop_down, a):
        self.update(self.last_text, True)

    @Gtk.Template.Callback()
    def _set_tv_copy(self, a):
        self.is_tv_copy = True

    def update(self, text, reload=False):
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
            if self.cbtn_del_wrapping.get_active():
                text = self.process_text(text)
            self.last_text = text
            buffer_from.set_text(text)

        start_iter, end_iter = buffer_from.get_bounds()
        text = buffer_from.get_text(start_iter, end_iter, False)

        i = self.dd_server.get_selected()
        sk = get_server(i).key
        lk = get_lang(i, self.dd_lang.get_selected()).key

        threading.Thread(target=self.request_text, daemon=True,
                         args=(text, sk, lk,)).start()

    def request_text(self, text, sk, lk):
        """子线程翻译

        Args:
            text (str): _description_
            i (server_key_i): _description_
            j (lang_key_j): _description_
        """
        GLib.idle_add(self.update_ui, "")
        text_translated = translate_by_server(text, sk, lk)
        GLib.idle_add(self.update_ui, text_translated)

    def update_ui(self, s=""):
        """更新界面

        Args:
            s (bool, optional): 翻译以后的文本. Defaults to True.
        """
        if len(s) == 0:
            # 开始翻译
            self.sp_translate.start()
            self.tv_to.get_buffer().set_text("翻译中……")
        else:
            # 翻译完成
            self.tv_to.get_buffer().set_text(s)
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

    def set_splice_text(self):
        """拼接
        """
        print("111")
        print(self.cbtn_add_old.get_active())
        self.cbtn_add_old.set_active(not self.cbtn_add_old.get_active())
