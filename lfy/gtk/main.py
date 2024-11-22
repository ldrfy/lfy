# main.py
import json
import os
import platform
import threading
import time
from datetime import datetime
from gettext import gettext as _

from gi.repository import Adw, Gdk, Gio, GLib, Gtk

from lfy import PACKAGE_URL, RES_PATH, VERSION
from lfy.gtk.preference import PreferencesDialog
from lfy.gtk.translate import TranslateWindow
from lfy.utils import get_os_release, is_text
from lfy.utils.bak import backup_gsettings
from lfy.utils.check_update import main as check_update
from lfy.utils.debug import get_log_handler
from lfy.utils.settings import Settings

# 设置代理地址和端口号
PROXY_ADDRESS = Settings().g("vpn-addr-port")
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
        self.img_w = 0
        self.img_h = 0

        action_trans_now = Gio.SimpleAction.new_stateful(
            'copy2translate', None, self.translate_now)
        action_trans_now.connect('change-state', self.on_action_trans_now)
        self.add_action(action_trans_now)
        self.set_accels_for_action("app.copy2translate", ['<alt>t'])

        self.create_action('preferences', self.on_preferences_action,
                           ["<Ctrl>comma"])
        self.create_action('quit', lambda *_: self.quit(),
                           ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('find_update', self.find_update)

        self.create_action('del_wrapping', self.on_del_wrapping_action,
                           ['<alt>d'])
        self.create_action('splice_text', self.on_splice_text_action,
                           ['<alt>c'])
        self.create_action('translate', self.set_translate_action,
                           ['<primary>t'])

        self.create_action('gp_reset_restore', self.gp_reset_action,
                           ['<primary>r'])
        self.create_action('gp_up', self.gp_up_action,
                           ['<primary>u'])
        self.create_action('gp_down', self.gp_down_action,
                           ['<primary>d'])
        self.last_clip = 0

        self.cb = Gdk.Display().get_default().get_clipboard()
        self.copy_change_id = self.cb.connect("changed", self.copy)

        self.find_update()

    def get_translate_win(self):
        """翻译窗口

        Returns:
            _type_: _description_
        """
        win = self.props.active_window  # pylint: disable=E1101
        if not win:
            width, height = Settings().g("window-size")
            print(width, height)
            win = TranslateWindow(
                application=self, default_height=int(height), default_width=int(width), )
        win.present()
        return win

    def do_activate(self, s="", ocr=False):
        """翻译

        Args:
            s (str, optional): _description_. Defaults to "".
            ocr (bool, optional): _description_. Defaults to False.
        """
        win = self.get_translate_win()
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
        path = f'{RES_PATH}/{self._application_id}.appdata.xml'

        ad = Adw.AboutDialog.new_from_appdata(path, VERSION)
        ad.set_developers(['yuh <yuhldr@qq.com>, 2023-2023'])
        ad.set_designers(['yuh <yuhldr@qq.com>, 2023-2023'])
        ad.set_documenters(['yuh <yuhldr@qq.com>, 2023-2023'])
        ad.set_translator_credits(_('translator_credits'))
        ad.set_comments(_('A translation app for GNOME.'))
        ad.set_copyright(f'© 2023-{datetime.now().year} yuh')

        s = f"Version: {VERSION}"
        s += f"\nSystem: {platform.system()}"
        s += f"\nRelease: {platform.release()}"

        gvs = Gtk.get_major_version(), Gtk.get_minor_version(), Gtk.get_micro_version()
        s += f"\nGTK Version: {gvs[0]}.{gvs[1]}.{gvs[2]}"

        avs = Adw.get_major_version(), Adw.get_minor_version(), Adw.get_micro_version()
        s += f"\nAdwaita Version: {avs[0]}.{avs[1]}.{avs[2]}"

        backup_data = json.loads(backup_gsettings())
        ss = {}
        for k, v in backup_data.items():
            if "server-sk-" in k and ("key" not in v or "Key" not in v):
                v = "******"
            ss[k] = v
        s += "\n\n******* config *******\n"
        s += json.dumps(ss, indent=4, ensure_ascii=False)
        s += "\n************"

        s += "\n\n******* debug log *******\n"
        s += get_log_handler().get_logs()

        s += "\n\n******* other *******\n"
        s += get_os_release()

        ad.set_debug_info(s)

        ad.present(self.props.active_window)

    def on_preferences_action(self, _widget, _w):
        """打开设置

        Args:
            widget (_type_): _description_
            w (_type_): _description_
        """
        # pylint: disable=E1101
        PreferencesDialog().present(self.props.active_window)

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

    def on_del_wrapping_action(self, _widget, _w):
        """删除换行
        """
        # pylint: disable=E1101
        self.props.active_window.notice_action(self.props.active_window.cbtn_del_wrapping,
                                               _("Next translation not remove line breaks"),
                                               _("Next translation remove line breaks"))

    def on_splice_text_action(self, _widget, _w):
        """拼接文本

        Args:
            f (_type_): _description_
        """
        # pylint: disable=E1101
        self.props.active_window.notice_action(self.props.active_window.cbtn_add_old,
                                               _("Next translation without splicing text"),
                                               _("Next translation splicing text"))

    def set_translate_action(self, _widget, _w):
        """快捷键翻译

        Args:
            f (_type_): _description_
        """
        # pylint: disable=E1101
        self.props.active_window.update("reload", True)

    def gp_reset_action(self, _widget, _w):
        """分割线恢复

        Args:
            f (_type_): _description_
        """
        # pylint: disable=E1101
        self.props.active_window.reset_paned_position()

    def gp_up_action(self, _widget, _w):
        """分割线向上

        Args:
            f (_type_): _description_
        """
        # pylint: disable=E1101
        self.props.active_window.up_paned_position()

    def gp_down_action(self, _widget, _w):
        """分割线向下

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

            if self.img_w == pixbuf.get_width() and \
                    self.img_h == pixbuf.get_height():
                return

            self.img_w = pixbuf.get_width()
            self.img_h = pixbuf.get_height()

            path = "/tmp/lfy.png"
            pixbuf.savev(path, "png", (), ())

            self.do_activate(path, ocr=True)

        span = time.time() - self.last_clip
        cf = cb.get_formats()
        # https://docs.gtk.org/gdk4/struct.ContentFormats.html
        # 重复的不要，尤其是x11下，有些空白的，也不要
        if span < 1 or len(cf.get_mime_types()) == 0:
            return

        if is_text(cf):
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

    def find_update(self, _widget=None, _w=None):
        """查找更新
        """

        def fu():
            """更新子线程
            """
            update_msg = check_update()
            if update_msg is not None:
                time.sleep(2)
                print(update_msg)
                GLib.idle_add(self.update_app, update_msg)
            elif _widget is not None:
                # 手动更新
                s = _("There is no new version. The current version is {}.").format(
                    VERSION)
                s += "\n"
                s += _("You can go to {} to view the beta version.").format(PACKAGE_URL)
                GLib.idle_add(self.update_app, s)

        if Settings().g("auto-check-update"):
            threading.Thread(target=fu, daemon=True).start()
