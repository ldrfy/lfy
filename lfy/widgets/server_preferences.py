# Copyright 2023 Mufeed Ali
# Copyright 2023 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import re
import threading
from gettext import gettext as _

from gi.repository import Adw, GLib, Gtk

from lfy.api import check_translate, get_api_key_s
from lfy.api.base import Server


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

    def __init__(self, server: Server, **kwargs):
        super().__init__(**kwargs)
        self.server = server
        self.title.props.subtitle = server.name
        # Load saved values
        self.api_key_entry.props.text = get_api_key_s(server.key)
        self.api_key_link.set_uri(server.get_doc_url())

    @Gtk.Template.Callback()
    def _on_back(self, _button):
        """ Called on self.back_btn::clicked signal """
        self.get_root().close_subpage()

    @Gtk.Template.Callback()
    def _on_api_key_apply(self, _row):
        """ Called on self.api_key_entry::apply signal """

        api_key = self.api_key_entry.get_text()
        api_key = re.sub(r'\s*\|\s*', "  |  ", api_key.strip())
        self.api_key_entry.props.text = api_key
        self.api_key_entry.props.sensitive = False
        self.api_key_stack.props.visible_child_name = 'spinner'
        self.api_key_spinner.start()

        threading.Thread(target=self.request_text, daemon=True,
                         args=(self.server.key, api_key)).start()

    def update_ui(self, valid):
        """更新

        Args:
            valid (_type_): _description_
        """
        ok, text = valid
        if ok:
            self.api_key_entry.remove_css_class('error')
        else:
            self.api_key_entry.add_css_class('error')
        self.api_key_entry.props.sensitive = True

        toast = Adw.Toast.new(text.replace("\n", ""))
        self.get_root().add_toast(toast)
        self.api_key_spinner.stop()

    def request_text(self, server, api_key):
        """验证服务api是否靠谱

        Args:
            server (_type_): _description_
            api_key (_type_): _description_
        """
        valid = False
        try:
            valid = check_translate(server, api_key)
        except Exception as exc:  # pylint: disable=W0718
            logging.error(exc)

        GLib.idle_add(self.update_ui, valid)
