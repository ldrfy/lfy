# Copyright 2023 Mufeed Ali
# Copyright 2023 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import re
import threading

from gi.repository import Adw, GLib, Gtk

from lfy.api.server import Server


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

    api_key_ocr_entry = Gtk.Template.Child()
    api_key_ocr_stack = Gtk.Template.Child()
    api_key_ocr_spinner = Gtk.Template.Child()

    api_key_link = Gtk.Template.Child()

    def __init__(self, server: Server, **kwargs):
        super().__init__(**kwargs)
        self.server = server
        self.title.props.subtitle = server.name
        # Load saved values
        self.api_key_entry.props.text = server.get_api_key_s()

        ocr_enable = server.get_ocr_api_key_s() is not None
        if ocr_enable:
            # print(server.get_ocr_api_key_s())
            self.api_key_ocr_entry.set_text(server.get_ocr_api_key_s())
        self.api_key_ocr_entry.set_visible(ocr_enable)

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
                         args=(self.server.check_translate, api_key,
                               self.api_key_entry,
                               self.api_key_spinner)).start()

    @Gtk.Template.Callback()
    def _on_api_key_ocr_apply(self, _row):
        """ Called on self.api_key_entry::apply signal """

        api_key = self.api_key_ocr_entry.get_text()
        api_key = re.sub(r'\s*\|\s*', "  |  ", api_key.strip())
        self.api_key_ocr_entry.set_text(api_key)
        self.api_key_ocr_entry.set_sensitive(False)
        self.api_key_ocr_stack.set_visible_child_name('spinner')
        self.api_key_ocr_spinner.start()

        threading.Thread(target=self.request_text, daemon=True,
                         args=(self.server.check_ocr, api_key,
                               self.api_key_ocr_entry,
                               self.api_key_ocr_spinner)).start()

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
            logging.error(exc)

        GLib.idle_add(self.update_ui, valid, entry, spinner)
