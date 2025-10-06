"""设置api key"""
import threading
from gettext import gettext as _

from gi.repository import Adw, GLib, Gtk  # type: ignore

from lfy.api.server import Server
from lfy.utils import clear_key
from lfy.utils.debug import get_logger


# pylint: disable=E1101
@Gtk.Template(resource_path='/cool/ldr/lfy/server-preferences.ui')
class ServerPreferences(Adw.NavigationPage):
    """设置api

    Args:
        Adw (_type_): _description_
    """
    __gtype_name__ = 'ServerPreferencesPage'

    # Child widgets
    title: Adw.WindowTitle = Gtk.Template.Child()

    api_key_entry: Adw.EntryRow = Gtk.Template.Child()
    api_key_stack: Gtk.Stack = Gtk.Template.Child()
    api_key_spinner: Gtk.Spinner = Gtk.Template.Child()

    api_key_link: Gtk.LinkButton = Gtk.Template.Child()

    def __init__(self, server: Server, is_ocr=False, dialog=None, **kwargs):
        super().__init__(**kwargs)
        self.server = server
        self.dialog: Adw.PreferencesDialog = dialog
        self.is_ocr = is_ocr
        s = _("Text translate")
        if is_ocr:
            s = _("Text recognition")

        self.title.set_title(s)
        self.title.set_subtitle(server.name)

        conf_str = server.get_conf()
        if conf_str:
            self.api_key_entry.set_text(clear_key(conf_str, "  |  "))
        self.api_key_entry.set_title(server.sk_placeholder_text)
        self.api_key_entry.set_tooltip_text(server.sk_placeholder_text)

        self.api_key_link.set_uri(server.get_doc_url())

    @Gtk.Template.Callback()
    def _on_api_key_apply(self, _row):

        api_key = self.api_key_entry.get_text().strip()
        self.api_key_entry.set_sensitive(False)
        self.api_key_spinner.start()

        threading.Thread(target=self.request_text, daemon=True,
                         args=(self.server.check_conf, api_key)).start()

    def update_ui(self, ok, text, api_key):
        """更新

        Args:
            ok (bool): _description_
            text (str): _description_
            api_key (str): _description_
        """

        self.api_key_entry.set_sensitive(True)
        self.api_key_entry.set_text(clear_key(api_key, "  |  "))
        self.api_key_spinner.stop()

        if ok:
            self.api_key_entry.remove_css_class('error')
            self.dialog.add_toast(Adw.Toast.new(text.strip()))
        else:
            self.api_key_entry.add_css_class('error')

            dialog = Adw.AlertDialog.new(_("error message"))
            dialog.set_body(text)
            dialog.add_response("confirm", _("Confirm"))
            dialog.present(self.get_root())

    def request_text(self, fun, api_key):
        """验证服务api是否靠谱

        Args:
            fun (_type_): _description_
            api_key (_type_): _description_
        """
        ok = False
        try:
            ok, text = fun(api_key)
        except Exception as exc:  # pylint: disable=W0718
            get_logger().error(exc)
            text = str(exc)

        GLib.idle_add(self.update_ui, ok, text, api_key)
