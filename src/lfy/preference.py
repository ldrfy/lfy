# window.py
#
# Copyright 2023 Unknown

from gi.repository import Adw, Gtk

from lfy.api.server import (Server, get_server_names_api_key,
                            get_servers_api_key)
from lfy.server_preferences import ServerPreferences


@Gtk.Template(resource_path='/cool/ldr/lfy/preference.ui')
class PreferenceWindow(Adw.PreferencesWindow):
    """设置

    Args:
        Adw (_type_): _description_
    """
    __gtype_name__ = 'PreferencesWindow'

    acr_server: Adw.ComboRow = Gtk.Template.Child()


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server: Server
        self.acr_server.set_model(Gtk.StringList.new(get_server_names_api_key()))


    @Gtk.Template.Callback()
    def _open_server(self, btn):
        page = ServerPreferences(self.server)
        self.present_subpage(page)

    @Gtk.Template.Callback()
    def _config_select_server(self, arc, _value):
        """Called on self.translator::notify::selected signal"""
        self.server = get_servers_api_key()[arc.get_selected()]
        print(self.server.name)
