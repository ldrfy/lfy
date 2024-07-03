'设置'

from gettext import gettext as _

from gi.repository import Adw, Gio, Gtk

from lfy.api import get_server_names_api_key, get_servers_api_key
from lfy.api.constant import SERVERS
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
    gbtn_compare: Gtk.Button = Gtk.Template.Child()
    gl_compare: Gtk.Label = Gtk.Template.Child()
    notify_translation_results: Gtk.Switch = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        sg = Settings.get()
        self.server: Server
        # pylint: disable=E1101
        self.acr_server.set_model(
            Gtk.StringList.new(get_server_names_api_key()))
        self.entry_vpn_addr.props.text = sg.vpn_addr_port

        sg.bind('auto-check-update', self.auto_check_update,
                'active', Gio.SettingsBindFlags.DEFAULT)

        sg.bind('notify-translation-results', self.notify_translation_results,
                'active', Gio.SettingsBindFlags.DEFAULT)

        # Create a ListBox for the dropdown menu
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)

        # Add items with check buttons to the ListBox
        names = []
        keys_s = sg.compare_servers
        if len(keys_s) == 0:
            for se in SERVERS[1:]:
                keys_s.append(se.key)

        self.check_items = []

        for se in SERVERS[1:]:
            check_button = Gtk.CheckButton(label=se.name)
            if se.key in keys_s:
                check_button.set_active(True)
                names.append(se.name)
            self.check_items.append(check_button)

            row = Gtk.ListBoxRow()
            row.set_child(check_button)
            self.listbox.append(row)

        self.gl_compare.set_label(", ".join(names))
        # Create a popover to hold the ListBox
        self.popover = Gtk.PopoverMenu()
        self.popover.set_child(self.listbox)

        self.popover.set_autohide(True)
        self.popover.connect("closed", self.on_popover_closed)

    def get_selected_items(self):
        selected_items = []
        for i, check_button in enumerate(self.check_items):
            if check_button.get_active():
                selected_items.append(i)
        return selected_items

    def on_popover_closed(self, _popover):
        # Get selected items and update button label
        selected_items = self.get_selected_items()
        keys = []
        names = []
        for i in selected_items:
            keys.append(SERVERS[1:][i].key)
            names.append(SERVERS[1:][i].name)
        Settings.get().compare_servers = keys
        self.gl_compare.set_label(", ".join(names))

        self.get_root().add_toast(
            Adw.Toast.new(_("It takes effect when you restart lfy")))

    @Gtk.Template.Callback()
    def on_gbtn_compare_clicked(self, button):
        self.popover.set_parent(button)
        self.popover.popup()

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

        self.get_root().add_toast(
            Adw.Toast.new(_("It takes effect when you restart lfy")))
