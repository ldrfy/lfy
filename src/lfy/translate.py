'''翻译主窗口'''

import threading
import time

from gi.repository import Adw, GLib, Gtk

from lfy.api import process_text, translate_by_server
from lfy.api.server import (get_lang, get_lang_names, get_server_name,
                            get_server_names, server_key2i)
from lfy.settings import Settings


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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 可能包含上次的追加内容
        self.last_text = ""
        # 这次复制的
        self.last_text_one = ""
        # 是不是软件内复制的，这种可能是想粘贴到其他地方，不响应即可
        self.is_tv_copy = False
        i = server_key2i(Settings.get().lang_selected_key)
        self._set_model(self.dd_server, get_server_names(), i)

    @Gtk.Template.Callback()
    def _on_translate_clicked(self, btn):
        self.update(self.last_text, True)

    @Gtk.Template.Callback()
    def _on_server_changed(self, drop_down, a):
        print(drop_down, a)
        self._set_model(self.dd_lang, get_lang_names(drop_down.get_selected()))

    @Gtk.Template.Callback()
    def _on_lang_changed(self, drop_down, a):
        print(drop_down, a)
        self.update(self.last_text, True)
        return drop_down.get_selected()

    @Gtk.Template.Callback()
    def _set_tv_copy(self, a):
        self.is_tv_copy = True

    def _set_model(self, drop_down, data, i=0):
        """设置选项

        Args:
            drop_down (_type_): _description_
            data (_type_): _description_
            i (int, optional): _description_. Defaults to 0.
        """
        print(drop_down, data, i)
        sl = Gtk.StringList()
        for d in data:
            sl.append(d)
        drop_down.set_model(sl)
        drop_down.set_selected(i)

    def update(self, text, reload=False):
        """翻译

        Args:
            text (_type_): _description_
            reload (bool, optional): _description_. Defaults to False.
        """
        print(text)
        buffer_from = self.tv_from.get_buffer()
        if not reload:
            if self.last_text_one == text or self.is_tv_copy:
                return
            self.last_text_one = text
            if self.cbtn_add_old.get_active():
                text = f"{self.last_text} {text}"
            if self.cbtn_del_wrapping.get_active():
                text = process_text(text)
            self.last_text = text
            buffer_from.set_text(text)

        start_iter, end_iter = buffer_from.get_bounds()
        text = buffer_from.get_text(start_iter, end_iter, False)

        threading.Thread(target=self.request_text, daemon=True, args=(
            text, self.dd_server.get_selected(), self.dd_lang.get_selected(),)).start()

    def request_text(self, text, i, j):
        """子线程翻译

        Args:
            text (str): _description_
            i (server_key_i): _description_
            j (lang_key_j): _description_
        """
        GLib.idle_add(self.update_ui, "")

        start_ = time.time()
        sk = get_server_name(i)
        lk = get_lang(i, j)

        text_translated = translate_by_server(text, sk, lk)

        span = 0.1 - (time.time() - start_)
        if span > 0:
            time.sleep(span)
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
