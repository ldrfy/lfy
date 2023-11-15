# window.py
#
# Copyright 2023 Unknown

import threading
import time

from gi.repository import Adw, Gtk
from lt_gtk import api
from lt_gtk.api.server import (get_lang, get_lang_names, get_server_key,
                               get_server_names)


@Gtk.Template(resource_path='/lt/ldr/cool/ui/translate.ui')
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
        print(drop_down)
        i = drop_down.get_active()
        print(i)
        self._set_model(self.dd_lang, get_lang_names(i))

    @Gtk.Template.Callback()
    def _on_lang_changed(self, drop_down):
        i = drop_down.get_active()
        return i

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
        print(drop_down)
        for d in data:
            drop_down.append_text(d)
        drop_down.set_active(i)
        print(i, data)

    def update(self, text, reload=False):
        """翻译

        Args:
            text (_type_): _description_
            reload (bool, optional): _description_. Defaults to False.
        """
        buffer = self.tv_from.get_buffer()
        if not reload:
            if (self.last_text_one == text) or self.is_tv_copy:
                print(f"重复，不复制：\n{text}")
                return
            self.last_text_one = text
            if self.cbtn_add_old.get_active():
                text = f"{self.last_text} {text}"
            self.last_text = text
            buffer.set_text(text)

        start_iter, end_iter = buffer.get_bounds()
        text = buffer.get_text(start_iter, end_iter, False)

        buffer_to = self.tv_to.get_buffer()
        buffer_to.set_text("翻译中……")
        self.translate_by_s(text)

    def translate_by_s(self, text):
        """异步

        Args:
            text (_type_): _description_
        """
        def request_text(text):
            start_ = time.time()
            i = self.dd_server.get_active()
            j = self.dd_lang.get_active()

            text_translated = api.translate(
                text, get_server_key(i), get_lang(i, j))
            span = 0.5 - (time.time() - start_)
            if span > 0:
                time.sleep(span)
            self.tv_to.get_buffer().set_text(text_translated)
            self.sp_translate.stop()

        self.sp_translate.start()
        tt = threading.Thread(target=request_text, args=(text,))
        tt.start()
