# window.py
#
# Copyright 2023 Unknown

from gi.repository import Adw, Gtk


@Gtk.Template(resource_path='/cool/ldr/lfy/ui/preference.ui')
class PreferenceWindow(Adw.PreferencesWindow):
    __gtype_name__ = 'PreferencesWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
