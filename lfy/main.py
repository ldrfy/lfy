# main.py
import os
import threading
import time
from gettext import gettext as _

from gi.repository import Adw, Gdk, Gio, GLib, Gtk, Notify

from lfy import PACKAGE_URL, PACKAGE_URL_BUG
from lfy.api.utils.check_update import main as check_update
from lfy.preference import PreferenceWindow
from lfy.settings import Settings
from lfy.translate import TranslateWindow

# 设置代理地址和端口号
PROXY_ADDRESS = Settings.get().vpn_addr_port
if len(PROXY_ADDRESS) > 0:
    # 设置环境变量
    os.environ['http_proxy'] = PROXY_ADDRESS
    os.environ['https_proxy'] = PROXY_ADDRESS


class LfyApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self, app_id, version):
        super().__init__(application_id=app_id,
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

        self._version = version
        self._application_id = app_id
        self.translate_now = GLib.Variant.new_boolean(True)
        Notify.init(_('lfy'))

        action_trans_now = Gio.SimpleAction.new_stateful(
            'copy2translate', None, self.translate_now)
        action_trans_now.connect('change-state', self.on_action_trans_now)
        self.add_action(action_trans_now)
        self.set_accels_for_action("app.copy2translate", ['<alt>t'])

        self.create_action('preferences', self.on_preferences_action)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('del_wrapping',
                           lambda *_: self.on_del_wrapping_action(),
                           ['<alt>d'])
        self.create_action('splice_text',
                           lambda *_: self.on_splice_text_action(),
                           ['<alt>c'])
        self.create_action('translate',
                           lambda *_: self.set_translate_action(),
                           ['<primary>t'])
        self.create_action('gp_reset_restore',
                           lambda *_: self.gp_reset_action(),
                           ['<primary>r'])

        self.create_action('gp_up',
                           lambda *_: self.gp_up_action(),
                           ['<primary>u'])

        self.create_action('gp_down',
                           lambda *_: self.gp_down_action(),
                           ['<primary>d'])
        self.last_clip = 0

        self.cb = Gdk.Display().get_default().get_clipboard()
        self.copy_change_id = self.cb.connect("changed", self.copy)

        if Settings.get().auto_check_update:
            threading.Thread(target=self.find_update, daemon=True).start()

    def do_activate(self, s="", ocr=False):
        """_summary_

        Args:
            s (str, optional): _description_. Defaults to "".
            ocr (bool, optional): _description_. Defaults to False.
        """
        win = self.props.active_window  # pylint: disable=E1101
        if not win:
            width, height = Settings.get().window_size
            win = TranslateWindow(
                application=self, default_height=height, default_width=width, )
        win.present()
        if ocr:
            win.update_ocr(s)
        else:
            win.update(s)

    def on_about_action(self, _widget, _w):
        """_summary_

        Args:
            widget (_type_): _description_
            w (_type_): _description_
        """
        # pylint: disable=E1101
        Adw.AboutWindow(transient_for=self.props.active_window,
                        application_name=_('lfy'),
                        application_icon=self._application_id,
                        version=self._version,
                        developers=['yuh <yuhldr@qq.com>, 2023-2023'],
                        designers=['yuh <yuhldr@qq.com>, 2023-2023'],
                        documenters=['yuh <yuhldr@qq.com>, 2023-2023'],
                        translator_credits=_('translator_credits'),
                        comments=_("A translation app for GNOME."),
                        website=PACKAGE_URL,
                        issue_url=PACKAGE_URL_BUG,
                        license_type=Gtk.License.GPL_3_0,
                        copyright='© 2023 yuh').present()

    def on_preferences_action(self, _widget, _w):
        """打开设置

        Args:
            widget (_type_): _description_
            w (_type_): _description_
        """
        # pylint: disable=E1101
        PreferenceWindow(transient_for=self.props.active_window).present()

    def on_action_trans_now(self, action, value):
        """临时设置不相应复制行为

        Args:
            action (_type_): _description_
            value (_type_): _description_
        """
        action.props.state = value
        if value:
            text = _("Copy detected, translate immediately")
            self.copy_change_id = self.cb.connect("changed", self.copy)
        else:
            text = _("Copy detected, not automatically translated")
            self.cb.disconnect(self.copy_change_id)
        # pylint: disable=E1101
        self.props.active_window.toast_msg(text)

    def create_action(self, name, callback, shortcuts=None):
        """创建菜单

        Args:
            name (_type_): _description_
            callback (function): _description_
            shortcuts (_type_, optional): _description_. Defaults to None.
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

    def on_del_wrapping_action(self):
        """删除换行
        """
        # pylint: disable=E1101
        self.props.active_window.notice_action(self.props.active_window.cbtn_del_wrapping,
                                               _("Next translation not remove line breaks"),
                                               _("Next translation remove line breaks"))

    def on_splice_text_action(self):
        """拼接文本

        Args:
            f (_type_): _description_
        """
        # pylint: disable=E1101
        self.props.active_window.notice_action(self.props.active_window.cbtn_add_old,
                                               _("Next translation without splicing text"),
                                               _("Next translation splicing text"))

    def set_translate_action(self):
        """快捷键翻译

        Args:
            f (_type_): _description_
        """
        # pylint: disable=E1101
        self.props.active_window.update("reload", True)

    def gp_reset_action(self):
        """快捷键翻译

        Args:
            f (_type_): _description_
        """
        # pylint: disable=E1101
        self.props.active_window.reset_paned_position()

    def gp_up_action(self):
        """快捷键翻译

        Args:
            f (_type_): _description_
        """
        # pylint: disable=E1101
        self.props.active_window.up_paned_position()

    def gp_down_action(self):
        """快捷键翻译

        Args:
            f (_type_): _description_
        """
        # pylint: disable=E1101
        self.props.active_window.down_paned_position()

    def copy(self, cb):
        """翻译

        Args:
            cb (function): _description_
        """

        def on_active_copy(cb2, res):
            self.do_activate(cb2.read_text_finish(res))

        def save_img(cb2, res):
            texture = cb2.read_texture_finish(res)
            pixbuf = Gdk.pixbuf_get_from_texture(texture)
            path = "/tmp/lfy.png"
            pixbuf.savev(path, "png", (), ())
            self.do_activate(path, ocr=True)

        span = time.time() - self.last_clip
        cf = cb.get_formats()
        # https://docs.gtk.org/gdk4/struct.ContentFormats.html
        # 重复的不要，尤其是x11下，有些空白的，也不要
        if span < 1 or len(cf.get_mime_types()) == 0:
            return

        if cf.contain_mime_type("text/plain"):
            self.last_clip = time.time()
            cb.read_text_async(None, on_active_copy)
        elif cf.contain_mime_type('image/png'):
            self.last_clip = time.time()
            cb.read_texture_async(None, save_img)

    def update_app(self, update_msg):
        """显示更新信息

        Args:
            update_msg (_type_): _description_
        """
        # pylint: disable=E1101
        self.props.active_window.tv_from.get_buffer().set_text(update_msg)

    def find_update(self):
        """查找更新
        """

        update_msg = check_update()
        if update_msg is not None:
            time.sleep(2)
            print(update_msg)
            GLib.idle_add(self.update_app, update_msg)
