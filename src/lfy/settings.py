# Copyright 2021-2022 Mufeed Ali
# Copyright 2021-2022 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gio, GLib, GObject

from lfy import APP_ID


class Settings(Gio.Settings):
    """
    Dialect settings handler
    """

    instance = None

    def __init__(self, *args):
        super().__init__(*args)

    @staticmethod
    def new():
        """Create a new instance of Settings."""
        g_settings = Settings(APP_ID)
        return g_settings

    @staticmethod
    def get():
        """Return an active instance of Settings."""
        if Settings.instance is None:
            Settings.instance = Settings.new()
        return Settings.instance

    @property
    def server_selected_key(self):
        """选择翻译的服务的key

        Returns:
            str: 如：baidu
        """
        return self.get_string('server-selected-key')

    @server_selected_key.setter
    def server_selected_key(self, key):
        self.set_string('server-selected-key', key)

    @property
    def lang_selected_n(self):
        """选择翻译语言的n：0

        Returns:
            int: 如 3
        """
        return self.get_int('lang-selected-n')

    @lang_selected_n.setter
    def lang_selected_n(self, n):
        print("lang_selected_n", n)
        self.set_int('lang-selected-n', n)
