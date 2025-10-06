"""设置"""
# pylint: disable=E1101

import time
from gettext import gettext as _

from gi.repository import Adw, Gdk, Gio, Gtk  # type: ignore

from lfy import APP_ID
from lfy.api import (get_server_names_o, get_server_names_t_sk, get_servers_o,
                     get_servers_t, get_servers_t_sk)
from lfy.api.server import Server
from lfy.gtk.widgets.server_preferences import ServerPreferences
from lfy.utils import is_text
from lfy.utils.bak import backup_gsettings, restore_gsettings
from lfy.utils.settings import Settings


@Gtk.Template(resource_path='/cool/ldr/lfy/preference.ui')
class PreferencesDialog(Adw.PreferencesDialog):
    """设置

    Args:
        Adw (_type_): _description_
    """
    __gtype_name__ = 'PreferencesDialog'

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
        self.sg = Settings()
        self.server: Server
        self.server_ocr: Server
        self.acr_server.set_model(
            Gtk.StringList.new(get_server_names_t_sk()))

        self.ocr_s_time = time.time()
        self.acr_server_ocr.set_model(Gtk.StringList.new(get_server_names_o()))
        sso = get_servers_o()
        sok = self.sg.g("server-ocr-selected-key", "easyocr")

        for i, so in enumerate(sso):
            if so.key == sok:
                self.acr_server_ocr.set_selected(i)
                self.server_ocr = so
                break

        self.entry_vpn_addr.props.text = self.sg.g("vpn-addr-port")
        self.sg0 = Gio.Settings(APP_ID)
        self.sg0.bind('auto-check-update', self.auto_check_update,
                      'active', Gio.SettingsBindFlags.DEFAULT)

        self.sg0.bind('notify-translation-results', self.notify_translation_results,
                      'active', Gio.SettingsBindFlags.DEFAULT)
        self._init_pop_compare()
        self.cb = Gdk.Display.get_default().get_clipboard()

    def _init_pop_compare(self):
        """初始化compare弹出菜单
        """
        # ui中无法设置gbtn_compare翻译
        self.gbtn_compare.set_label(_("compare"))
        names = []
        ss = list(get_servers_t())[1:]
        keys_s = self.sg.g("compare-servers")
        if not keys_s:
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
            s = restore_gsettings(s)
            if len(s) == 0:
                s = _("It takes effect when you restart lfy")
            self.add_toast(Adw.Toast.new(s))

        cf = self.cb.get_formats()

        if is_text(cf):
            self.cb.read_text_async(None, on_active_copy)
        else:
            notice_s = _("The clipboard format is incorrect")
            self.add_toast(Adw.Toast.new(notice_s))

    @Gtk.Template.Callback()
    def _export_config(self, _b):
        self.cb.set(backup_gsettings())
        self.add_toast(Adw.Toast.new(
            _("Configuration data has been exported to the clipboard")))

    @Gtk.Template.Callback()
    def _on_popover_closed(self, _popover):
        """关闭时保存

        Args:
            _popover (_type_): _description_
        """
        keys = []
        names = []
        ss = list(get_servers_t())[1:]

        for i, check_button in enumerate(self.check_items):
            if check_button.get_active():
                keys.append(ss[i].key)
                names.append(ss[i].name)

        if self.sg.g("compare-servers") != keys:
            self.sg.s("compare-servers", keys)
            self.aar_compare.set_subtitle(", ".join(names))
            self.add_toast(Adw.Toast.new(
                _("It takes effect when you restart lfy")))

    @Gtk.Template.Callback()
    def _open_server(self, _btn):
        self.push_subpage(ServerPreferences(self.server, dialog=self))

    @Gtk.Template.Callback()
    def _open_server_ocr(self, _btn):
        self.push_subpage(ServerPreferences(
            self.server_ocr, True, dialog=self))

    @Gtk.Template.Callback()
    def _config_select_server_ocr(self, arc, _value):
        if time.time() - self.ocr_s_time > 0.5:
            self.server_ocr = get_servers_o()[arc.get_selected()]
            self.sg.s("server-ocr-selected-key", self.server_ocr.key)

            s = _("Using {} for text recognition").format(self.server_ocr.name)
            self.add_toast(Adw.Toast.new(s))

    @Gtk.Template.Callback()
    def _config_select_server(self, arc, _value):
        self.server = get_servers_t_sk()[arc.get_selected()]

    @Gtk.Template.Callback()
    def _on_vpn_apply(self, _row):
        self.entry_vpn_addr.props.sensitive = False

        vpn_addr = self.entry_vpn_addr.get_text().strip()
        self.entry_vpn_addr.props.text = vpn_addr
        self.sg.s("vpn-addr-port", vpn_addr)
        self.entry_vpn_addr.props.sensitive = True

        self.add_toast(Adw.Toast.new(
            _("It takes effect when you restart lfy")))
