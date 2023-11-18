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
    def lang_selected_key(self):
        return self.get_string('lang-selected-key')

    @lang_selected_key.setter
    def lang_selected_key(self, key):
        self.set_string('lang-selected-key', key)
