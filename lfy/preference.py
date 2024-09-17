'设置'

from gettext import gettext as _

from gi.repository import Adw, Gdk, Gio, Gtk

from lfy.api import (get_server_names_api_key, get_server_names_o,
                     get_servers_api_key, get_servers_o, get_servers_t)
from lfy.api.server import Server
from lfy.api.utils import is_text
from lfy.api.utils.bak import backup_gsettings, restore_gsettings
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
    acr_server_ocr: Adw.ComboRow = Gtk.Template.Child()
    entry_vpn_addr: Adw.EntryRow = Gtk.Template.Child()
    auto_check_update: Adw.SwitchRow = Gtk.Template.Child()
    notify_translation_results: Adw.SwitchRow = Gtk.Template.Child()

    gbtn_compare: Gtk.MenuButton = Gtk.Template.Child()
    aar_compare: Adw.ActionRow = Gtk.Template.Child()
    gp_compare: Gtk.Popover = Gtk.Template.Child()
    glb_compare: Gtk.ListBox = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        sg = Settings.get()
        self.server: Server
        # pylint: disable=E1101
        self.acr_server.set_model(get_server_names_api_key())
        self.acr_server_ocr.set_model(get_server_names_o())
        self.entry_vpn_addr.props.text = sg.vpn_addr_port

        sg.bind('auto-check-update', self.auto_check_update,
                'active', Gio.SettingsBindFlags.DEFAULT)

        sg.bind('notify-translation-results', self.notify_translation_results,
                'active', Gio.SettingsBindFlags.DEFAULT)
        self._init_pop_compare()
        self.cb = Gdk.Display.get_default().get_clipboard()

    def _init_pop_compare(self):
        """初始化compare弹出菜单
        """
        # pylint:disable=E1101
        # ui中无法设置gbtn_compare翻译
        self.gbtn_compare.set_label(_("compare"))
        names = []
        ss = list(get_servers_t())[1:]
        keys_s = Settings.get().compare_servers
        if len(keys_s) == 0:
            for se in ss:
                keys_s.append(se.key)

        self.check_items = []
        for se in ss:
            check_button = Gtk.CheckButton(label=se.name)
            if se.key in keys_s:
                check_button.set_active(True)
                names.append(se.name)
            self.check_items.append(check_button)
            self.glb_compare.append(Gtk.ListBoxRow(child=check_button))

        self.aar_compare.set_subtitle(", ".join(names))

    @Gtk.Template.Callback()
    def _import_config(self, _b):

        def on_active_copy(cb2, res):
            s = cb2.read_text_finish(res)
            print(s)
            s = restore_gsettings(s)
            if len(s) == 0:
                s = _("It takes effect when you restart lfy")
            self.get_root().add_toast(Adw.Toast.new(s))

        cf = self.cb.get_formats()

        if is_text(cf):
            self.cb.read_text_async(None, on_active_copy)
        else:
            notice_s = _("The clipboard format is incorrect")
            self.get_root().add_toast(Adw.Toast.new(notice_s))

    @Gtk.Template.Callback()
    def _export_config(self, _b):
        s = backup_gsettings()
        print(f"\n\n{s}\n\n")
        self.cb.set(s)
        notice_s = _("Configuration data has been exported to the clipboard")
        self.get_root().add_toast(Adw.Toast.new(notice_s))

    @Gtk.Template.Callback()
    def _on_popover_closed(self, _popover):
        """关闭时保存

        Args:
            _popover (_type_): _description_
        """
        # pylint:disable=E1101
        keys = []
        names = []
        ss = list(get_servers_t())[1:]

        for i, check_button in enumerate(self.check_items):
            if check_button.get_active():
                keys.append(ss[i].key)
                names.append(ss[i].name)

        if Settings.get().compare_servers != keys:
            Settings.get().compare_servers = keys
            self.aar_compare.set_subtitle(", ".join(names))
            self.get_root().add_toast(
                Adw.Toast.new(_("It takes effect when you restart lfy")))

    @Gtk.Template.Callback()
    def _open_server(self, _btn):
        page = ServerPreferences(self.server)
        self.present_subpage(page)

    @Gtk.Template.Callback()
    def _config_select_server_ocr(self, arc, _value):
        _k = get_servers_o()[arc.get_selected()].key
        Settings.get().server_ocr_selected_key = _k

    @Gtk.Template.Callback()
    def _config_select_server(self, arc, _value):
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
