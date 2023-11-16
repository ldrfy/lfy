# window.py
#
# Copyright 2023 Unknown

import threading
import time

from gi.repository import Adw, GLib, Gtk

from lfy.api import process_text, translate_by_server
from lfy.api.server import (get_lang, get_lang_names, get_server_key,
                            get_server_names)


@Gtk.Template(resource_path='/cool/ldr/lfy/ui/translate.ui')
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
    dd_server: Gtk.ComboBoxText = Gtk.Template.Child()
    dd_lang: Gtk.ComboBoxText = Gtk.Template.Child()
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
        self._set_model(self.dd_server, get_server_names())

    @Gtk.Template.Callback()
    def _on_translate_clicked(self, btn):
        self.update(self.last_text, True)

    @Gtk.Template.Callback()
    def _on_server_changed(self, drop_down):
        self._set_model(self.dd_lang, get_lang_names(drop_down.get_active()))

    @Gtk.Template.Callback()
    def _on_lang_changed(self, drop_down):
        self.update(self.last_text, True)
        return drop_down.get_active()

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
        drop_down.remove_all()
        for d in data:
            drop_down.append_text(d)
        drop_down.set_active(i)

    def update(self, text, reload=False):
        """翻译

        Args:
            text (_type_): _description_
            reload (bool, optional): _description_. Defaults to False.
        """
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
            text, self.dd_server.get_active(), self.dd_lang.get_active(),)).start()

    def request_text(self, text, i, j):
        """子线程翻译

        Args:
            text (str): _description_
            i (server_key_i): _description_
            j (lang_key_j): _description_
        """
        GLib.idle_add(self.update_ui, "")

        start_ = time.time()
        sk = get_server_key(i)
        lk = get_lang(i, j)

        text_translated = translate_by_server(text, sk, lk)

        span = 0.1 - (time.time() - start_)
        if span > 0:
            time.sleep(span)
        GLib.idle_add(self.update_ui, text_translated)

    def update_ui(self, s=True):
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
