'gtk版本入口'
import os
import sys
import threading
import time
from datetime import datetime
from gettext import gettext as _

from gi.repository import Adw, Gdk, Gio, GLib  # pylint: disable=E0401,C0413

from lfy import APP_ID, PACKAGE_URL, RES_PATH, VERSION
from lfy.gtk import get_gtk_msg
from lfy.gtk.preference import PreferencesDialog
from lfy.gtk.translate import TranslateWindow
from lfy.utils import cal_md5, is_text
from lfy.utils.check_update import main as check_update
from lfy.utils.code import parse_lfy
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
        self.sg = Settings()
        self.win: TranslateWindow = None
        self.cb = Gdk.Display().get_default().get_clipboard()
        self.img_md5 = ""
        self.text_last = ""
        self.copy_id = None

        action_trans_now = Gio.SimpleAction.new_stateful('copy2translate', None,
                                                         GLib.Variant.new_boolean(
                                                             self.sg.g("copy-auto-translate")))
        action_trans_now.connect('change-state', self.on_action_trans_now)
        self.add_action(action_trans_now)
        self.set_accels_for_action("app.copy2translate", ['<alt>t'])

        self.create_actions()

        threading.Thread(target=self.do_startup0, daemon=True).start()
        self.connect('activate', self.on_activate)

    def on_activate(self, _app):

        width, height = self.sg.g("window-size")
        self.win = TranslateWindow(application=self,
                                   default_height=int(height),
                                   default_width=int(width), )
        self.win.present()

    def do_startup0(self):
        """异步
        """
        for _i in range(100):
            time.sleep(0.1)
            if self.win and self.win.ocr_server:
                break
        GLib.idle_add(self.do_startup1)

    def do_startup1(self):
        """异步
        """
        if self.sg.g("copy-auto-translate"):
            self.copy_id = self.cb.connect("changed", self._get_copy)
            self._get_copy(self.cb)
        else:
            self.update_tr("Copy to translate? Try `<Alt>+T`")

        self.find_update()

    def update_tr(self, s="", ocr=False):
        """翻译

        Args:
            s (str, optional): _description_. Defaults to "".
            ocr (bool, optional): _description_. Defaults to False.
        """

        if ocr:
            self.win.update_ocr(s)
        else:
            self.win.update(s)

    def on_about_action(self, _widget, _w):
        """_summary_

        Args:
            widget (_type_): _description_
            w (_type_): _description_
        """
        path = f'{RES_PATH}/{self._application_id}.appdata.xml'
        year = datetime.now().year

        ad = Adw.AboutDialog.new_from_appdata(path, VERSION)
        ad.set_developers(['yuh <yuhldr@qq.com>, 2023-{year}'])
        ad.set_designers(['yuh <yuhldr@qq.com>, 2023-{year}'])
        ad.set_documenters(['yuh <yuhldr@qq.com>, 2023-{year}'])
        ad.set_translator_credits(_('translator_credits'))
        ad.set_comments(_('A translation app for GNOME.'))
        ad.set_copyright(f'© 2023-{year} yuh')

        ad.set_debug_info(get_gtk_msg(VERSION))

        ad.present(self.win)

    def on_preferences_action(self, _widget, _w):
        """打开设置

        Args:
            widget (_type_): _description_
            w (_type_): _description_
        """
        PreferencesDialog().present(self.win)

    def on_action_trans_now(self, action: Gio.SimpleAction, value: GLib.Variant):
        """临时设置不相应复制行为

        Args:
            action (_type_): _description_
            value (_type_): _description_
        """

        if value:
            text = _("Copy detected, translate immediately")
            self.copy_id = self.cb.connect("changed", self._get_copy)
        else:
            text = _("Copy detected, not automatically translated")
            self.cb.disconnect(self.copy_id)

        self.sg.s("copy-auto-translate", value.unpack())
        action.set_state(value)
        self.win.toast_msg(text)

    def create_actions(self):
        """创建菜单

        Args:
            name (_type_): _description_
            callback (function): _description_
            shortcuts (_type_, optional): _description_. Defaults to None.
        """

        names = ['preferences', 'quit', 'about',
                 'find_update', 'del_wrapping', 'splice_text',
                 'translate', 'gp_reset_restore', 'gp_up',
                 'gp_down']
        callbacks = [self.on_preferences_action, self.quit, self.on_about_action,
                     self.find_update, self.on_del_wrapping_action, self.on_splice_text_action,
                     self.set_translate_action, self.gp_reset_action, self.gp_up_action,
                     self.gp_down_action]
        shortcuts = ['<Ctrl>comma', '<primary>q', None,
                     None, '<alt>d', '<alt>c',
                     '<primary>t', '<primary>r', '<primary>u',
                     '<primary>d']

        for name, fun, shortcut in zip(names, callbacks, shortcuts):
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", fun)
            self.add_action(action)
            if shortcut:
                self.set_accels_for_action(f"app.{name}", [shortcut])

    def on_del_wrapping_action(self, _widget, _w):
        """删除换行
        """
        # pylint: disable=E1101
        self.win.notice_action(self.win.cbtn_del_wrapping,
                               _("Next translation not remove line breaks"),
                               _("Next translation remove line breaks"))

    def on_splice_text_action(self, _widget, _w):
        """拼接文本

        Args:
            f (_type_): _description_
        """
        self.win.notice_action(self.win.cbtn_add_old,
                               _("Next translation without splicing text"),
                               _("Next translation splicing text"))

    def set_translate_action(self, _widget, _w):
        """快捷键翻译

        Args:
            f (_type_): _description_
        """
        self.win.update("reload", True)

    def gp_reset_action(self, _widget, _w):
        """分割线恢复

        Args:
            f (_type_): _description_
        """
        # pylint: disable=E1101
        self.win.reset_paned_position()

    def gp_up_action(self, _widget, _w):
        """分割线向上

        Args:
            f (_type_): _description_
        """
        # pylint: disable=E1101
        self.win.up_paned_position()

    def gp_down_action(self, _widget, _w):
        """分割线向下

        Args:
            f (_type_): _description_
        """
        # pylint: disable=E1101
        self.win.down_paned_position()

    def _get_copy(self, cb: Gdk.Clipboard):
        """翻译

        Args:
            cb (Gdk.Clipboard): _description_
        """
        def on_active_copy(cb2: Gdk.Clipboard, res):
            text = cb2.read_text_finish(res)
            if text == self.text_last:
                return
            self.text_last = text
            self.update_tr(text)

        def save_img(cb2: Gdk.Clipboard, res):
            texture = cb2.read_texture_finish(res)
            pixbuf = Gdk.pixbuf_get_from_texture(texture)

            path = "/tmp/lfy.png"
            pixbuf.savev(path, "png", (), ())

            md5_hash = cal_md5(path)
            # 防止wayland多次识别
            if self.img_md5 == md5_hash:
                return
            self.img_md5 = md5_hash

            self.update_tr(path, ocr=True)

        cf = cb.get_formats()
        # https://docs.gtk.org/gdk4/struct.ContentFormats.html
        # 重复的不要，尤其是x11下，有些空白的，也不要
        if len(cf.get_mime_types()) == 0:
            return

        if is_text(cf):
            cb.read_text_async(None, on_active_copy)
        elif cf.contain_mime_type('image/png'):
            cb.read_texture_async(None, save_img)

    def update_app(self, update_msg):
        """显示更新信息

        Args:
            update_msg (_type_): _description_
        """
        # pylint: disable=E1101
        self.win.tv_from.get_buffer().set_text(update_msg)

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
                s = _("There is no new version.\
                      \nThe current version is {}.\
                      \nYou can go to {} to view the beta version.")\
                    .format(VERSION, PACKAGE_URL)
                GLib.idle_add(self.update_app, s)

        if Settings().g("auto-check-update"):
            threading.Thread(target=fu, daemon=True).start()


def main():
    """gtk版本入口
    """
    os.environ[f'{APP_ID}.ui'] = 'gtk'

    s = parse_lfy()
    if s:
        print(s)
        return

    sys.exit(LfyApplication(APP_ID, VERSION).run(sys.argv))
