# main.py
from gettext import gettext as _

from gi.repository import Adw, Gdk, Gio

from lfy import PACKAGE_URL, PACKAGE_URL_BUG
from lfy.preference import PreferenceWindow
from lfy.settings import Settings
from lfy.translate import TranslateWindow


class LfyApplication(Adw.Application):
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
            width, height = Settings.get().window_size
            win = TranslateWindow(application=self,
                                  default_height=height,
                                  default_width=width,)
        win.present()
        win.update(text)


    def on_about_action(self, widget, w):
        """Callback for the app.about action."""
        Adw.AboutWindow(transient_for=self.props.active_window,
                        application_name=_('lfy'),
                        application_icon=self._application_id,
                        version=self._version,
                        developers=['yuh'],
                        designers=['yuh'],
                        documenters=['yuh'],
                        translator_credits=_('translator_credits'),
                        comments=_("A translation app for GNOME."),
                        website=PACKAGE_URL,
                        issue_url=PACKAGE_URL_BUG,
                        copyright='© 2023 yuh').present()

    def on_preferences_action(self, widget, w):
        """Callback for the app.preferences action."""
        PreferenceWindow(transient_for=self.props.active_window).present()

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
