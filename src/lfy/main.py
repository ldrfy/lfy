# main.py
from gettext import gettext as _

from gi.repository import Adw, Gdk, Gio

from .preference import PreferenceWindow
from .translate import TranslateWindow


class LtApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self, app_id, version):
        super().__init__(application_id=app_id,
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

        self._version = version
        self._application_id = app_id

        self.create_action('preferences', self.on_preferences_action)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)

        self.copy()

    def do_activate(self, text=""):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = TranslateWindow(application=self)
        win.present()
        win.update(text)


    def on_about_action(self, widget, w):
        """Callback for the app.about action."""
        about = Adw.AboutWindow(transient_for=self.props.active_window,
                                application_name=_('lfy'),
                                application_icon=self._application_id,
                                developer_name='yuh',
                                version=self._version,
                                developers=['yuh'],
                                copyright='© 2023 yuh')
        about.present()

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        win = PreferenceWindow(application=self)
        win.present()

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


    def copy(self):
        """复制监听
        """
        def on_active_copy(cb, res):
            text = cb.read_text_finish(res)
            self.do_activate(text)

        def on_active_copy2(cb):
            cb.read_text_async(None, on_active_copy)

        clip_copy = Gdk.Display().get_default().get_clipboard()
        clip_copy.connect("changed", on_active_copy2)
