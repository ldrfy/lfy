# window.py
#
# Copyright 2023 Unknown

from gi.repository import Adw, Gtk

from lfy.api.server import (get_lang, get_lang_names, get_server_key,
                            get_server_names)
from lfy.server_preferences import ServerPreferences


@Gtk.Template(resource_path='/cool/ldr/lfy/preference.ui')
class PreferenceWindow(Adw.PreferencesWindow):
    __gtype_name__ = 'PreferencesWindow'

    acr_server: Adw.ComboRow = Gtk.Template.Child()


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        sl = Gtk.StringList()
        for sn in get_server_names():
            sl.append(sn)
        self.acr_server.set_model(sl)


    @Gtk.Template.Callback()
    def _open_server(self, a):
        print("_open_server", a)
        page = ServerPreferences("test", a)
        self.present_subpage(page)

    @Gtk.Template.Callback()
    def _config_select_server(self, arc, _value):
        """Called on self.translator::notify::selected signal"""
        s = arc.get_selected_item().get_string()
        print(s)
        s1 = arc.get_selected()
        print(s1)

