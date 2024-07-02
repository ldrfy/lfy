'设置'

from gi.repository import Adw, Gio, Gtk

from lfy.api import get_servers_api_key, get_server_names_api_key
from lfy.api.server import Server
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
    auto_check_update: Gtk.Switch = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server: Server
        # pylint: disable=E1101
        self.acr_server.set_model(Gtk.StringList.new(get_server_names_api_key()))
        self.entry_vpn_addr.props.text = Settings.get().vpn_addr_port

        Settings.get().bind('auto-check-update',
                            self.auto_check_update, 'active',
                            Gio.SettingsBindFlags.DEFAULT)


    @Gtk.Template.Callback()
    def _open_server(self, _btn):
        page = ServerPreferences(self.server)
        self.present_subpage(page)

    @Gtk.Template.Callback()
    def _config_select_server(self, arc, _value):
        """Called on self.translator::notify::selected signal"""
        self.server = get_servers_api_key()[arc.get_selected()]

    @Gtk.Template.Callback()
    def _on_vpn_apply(self, _row):
        # pylint: disable=E1101
        self.entry_vpn_addr.props.sensitive = False

        vpn_addr = self.entry_vpn_addr.get_text().strip()
        self.entry_vpn_addr.props.text = vpn_addr
        Settings.get().vpn_addr_port = vpn_addr
        self.entry_vpn_addr.props.sensitive = True

        self.get_root().add_toast(Adw.Toast.new("已保存"))
