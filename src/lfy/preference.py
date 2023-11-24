# window.py
#
# Copyright 2023 Unknown

from gi.repository import Adw, Gtk

from lfy.api.base import Server
from lfy.api.server import get_server_names_api_key, get_servers_api_key
from lfy.settings import Settings
from lfy.widgets.server_preferences import ServerPreferences


@Gtk.Template(resource_path='/cool/ldr/lfy/preference.ui')
class PreferenceWindow(Adw.PreferencesWindow):
    """设置

    Args:
        Adw (_type_): _description_
    """
    __gtype_name__ = 'PreferencesWindow'

    acr_server: Adw.ComboRow = Gtk.Template.Child()
    entry_vpn_addr: Adw.EntryRow = Gtk.Template.Child()


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server: Server
        self.acr_server.set_model(Gtk.StringList.new(get_server_names_api_key()))
        self.entry_vpn_addr.props.text = Settings.get().vpn_addr_port


    @Gtk.Template.Callback()
    def _open_server(self, btn):
        page = ServerPreferences(self.server)
        self.present_subpage(page)

    @Gtk.Template.Callback()
    def _config_select_server(self, arc, _value):
        """Called on self.translator::notify::selected signal"""
        self.server = get_servers_api_key()[arc.get_selected()]

    @Gtk.Template.Callback()
    def _on_vpn_apply(self, _row):
        self.entry_vpn_addr.props.sensitive = False

        vpn_addr = self.entry_vpn_addr.get_text().strip()
        self.entry_vpn_addr.props.text = vpn_addr
        Settings.get().vpn_addr_port = vpn_addr
        self.entry_vpn_addr.props.sensitive = True

        self.get_root().add_toast(Adw.Toast.new("已保存"))
