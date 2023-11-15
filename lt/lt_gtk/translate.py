# window.py
#
# Copyright 2023 Unknown

from gi.repository import Adw, Gio, GObject, Gtk
from lt_gtk.api.server_config import get_lang_names, get_server_names


@Gtk.Template(resource_path='/lt/ldr/cool/ui/translate.ui')
class TranslateWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'TranslateWindow'

    # btn_translate: Gtk.Button = Gtk.Template.Child()
    tv_from: Gtk.TextView = Gtk.Template.Child()
    tv_to: Gtk.TextView = Gtk.Template.Child()
    dd_server: Gtk.ComboBoxText = Gtk.Template.Child()
    dd_lang: Gtk.ComboBoxText = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_model(self.dd_server, get_server_names())

    @Gtk.Template.Callback()
    def _on_translate_clicked(self, btn):
        print(self.tv_from)
        print(btn)

        buffer = self.tv_from.get_buffer()
        start_iter, end_iter = buffer.get_bounds()
        text = buffer.get_text(start_iter, end_iter, False)

        print(text)
        self.tv_to.get_buffer().set_text(text)

    @Gtk.Template.Callback()
    def _on_server_changed(self, drop_down):
        print(drop_down)
        i = drop_down.get_active()
        print(i)
        self.set_model(self.dd_lang, get_lang_names(i))

    @Gtk.Template.Callback()
    def _on_lang_changed(self, drop_down):
        i = drop_down.get_active()
        return i

    @Gtk.Template.Callback()
    def _on_test(self, a, b):
        print(a)
        print(b)

    def set_model(self, drop_down, data, i=0):
        # sl = Gtk.StringList()
        # for d in data:
        #     sl.append(d)
        # drop_down.set_model(sl)
        # drop_down.set_selected(i)
        drop_down.remove_all()
        print(drop_down)
        for d in data:
            drop_down.append_text(d)
        drop_down.set_active(i)
        print(i, data)
