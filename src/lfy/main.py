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
        self.create_action(
            'splice_text', lambda *_: self.set_splice_text_action(), ['<alt>c'])
        self.create_action(
            'translate', lambda *_: self.set_translate_action(), ['<primary>t'])

        self.cb = Gdk.Display().get_default().get_clipboard()
        self.copy()


    def do_activate(self, text=""):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        print(win)
        if not win:
            print("111")
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


    def set_splice_text_action(self):
        """拼接文本

        Args:
            f (_type_): _description_
        """
        print("set_splice_text_action")
        win = self.props.active_window
        if win is not None:
            win.set_splice_text()

    def set_translate_action(self):
        """快捷键翻译

        Args:
            f (_type_): _description_
        """
        win = self.props.active_window
        if win is not None:
            win.update("reload", True)


    def on_active_copy2(self, cb):
        def on_active_copy(cb, res):
            self.do_activate(cb.read_text_finish(res))
        cb.read_text_async(None, on_active_copy)


    def copy(self):
        """复制监听
        """

        self.cb.connect("changed", self.on_active_copy2)
