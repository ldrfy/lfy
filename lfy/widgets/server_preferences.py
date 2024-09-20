# Copyright 2023 Mufeed Ali
# Copyright 2023 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

import re
import threading
from gettext import gettext as _

from gi.repository import Adw, GLib, Gtk

from lfy.api.server import Server
from lfy.api.utils.debug import get_logger


# pylint: disable=E1101
@Gtk.Template(resource_path='/cool/ldr/lfy/server-preferences.ui')
class ServerPreferences(Adw.Bin):
    """设置api

    Args:
        Adw (_type_): _description_
    """
    __gtype_name__ = 'ServerPreferences'

    # Child widgets
    title = Gtk.Template.Child()
    page = Gtk.Template.Child()
    api_key_entry = Gtk.Template.Child()
    api_key_stack = Gtk.Template.Child()
    api_key_spinner = Gtk.Template.Child()

    api_key_link = Gtk.Template.Child()

    def __init__(self, server: Server, is_ocr=False, **kwargs):
        super().__init__(**kwargs)
        self.server = server
        self.is_ocr = is_ocr
        s = _("Text translate")
        if is_ocr:
            s = _("Text recognition")

        self.title.set_title(s)
        self.title.set_subtitle(server.name)

        if not self.is_ocr:
            self.api_key_entry.set_text(server.get_api_key_s())
        else:
            self.api_key_entry.set_text(server.get_api_key_s_ocr())

        self.api_key_link.set_uri(server.get_doc_url())

    @Gtk.Template.Callback()
    def _on_back(self, _button):
        """ Called on self.back_btn::clicked signal """
        self.get_root().close_subpage()

    @Gtk.Template.Callback()
    def _on_api_key_apply(self, _row):

        api_key = self.api_key_entry.get_text()
        api_key = re.sub(r'\s*\|\s*', "  |  ", api_key.strip())
        self.api_key_entry.set_text(api_key)
        self.api_key_entry.set_sensitive(False)
        self.api_key_stack.set_visible_child_name('spinner')
        self.api_key_spinner.start()

        check_ot = self.server.check_translate
        if self.is_ocr:
            check_ot = self.server.check_ocr

        threading.Thread(target=self.request_text, daemon=True,
                         args=(check_ot, api_key,
                               self.api_key_entry,
                               self.api_key_spinner)).start()

    def update_ui(self, valid, entry, spinner):
        """更新

        Args:
            valid (_type_): _description_
        """
        ok, text = valid
        if ok:
            entry.remove_css_class('error')
        else:
            entry.add_css_class('error')
        entry.props.sensitive = True

        toast = Adw.Toast.new(text.replace("\n", ""))
        self.get_root().add_toast(toast)
        spinner.stop()

    def request_text(self, fun, api_key, entry, spinner):
        """验证服务api是否靠谱

        Args:
            server (_type_): _description_
            api_key (_type_): _description_
        """
        valid = False
        try:
            valid = fun(api_key)
        except Exception as exc:  # pylint: disable=W0718
            get_logger().error(exc)

        GLib.idle_add(self.update_ui, valid, entry, spinner)
