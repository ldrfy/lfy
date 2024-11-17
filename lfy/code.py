'终端翻译'
import os
import traceback
from gettext import gettext as _

from gi.repository import Gdk

from lfy.api import (create_server_o, create_server_t, get_servers_o,
                     get_servers_t, lang_n2key)
from lfy.api.server import Server
from lfy.api.utils import is_text
from lfy.api.utils.debug import get_logger
from lfy.settings import Settings


def req_clip(key_server, key_lang_n):
    """读取剪贴板，此方法暂时无效

    Args:
        key_server (str): _description_
        key_lang (str): _description_
    """
    def on_active_copy(cb2, res):
        return req_text(cb2.read_text_finish(res), key_server, key_lang_n)

    def save_img(cb2, res):
        texture = cb2.read_texture_finish(res)
        pixbuf = Gdk.pixbuf_get_from_texture(texture)

        path = "/tmp/lfy.png"
        pixbuf.savev(path, "png", (), ())
        return req_ocr(path, key_server, key_lang_n)

    cb = Gdk.Display().get_default().get_clipboard()
    cf = cb.get_formats()
    if is_text(cf):
        cb.read_text_async(None, on_active_copy)
    elif cf.contain_mime_type('image/png'):
        cb.read_texture_async(None, save_img)
    return "no text or image"

def get_help_lang(server: Server):
    """某个服务的lang key

    Args:
        server (Server): _description_

    Returns:
        _type_: _description_
    """
    # 每个翻译对应的key
    print('please add "-l number", number like:')
    return {lang.get_name(): lang.n for lang in server.langs}


def get_help_server(is_ocr=False):
    """某个服务的lang key

    Args:
        is_ocr (bool): _description_

    Returns:
        _type_: _description_
    """
    print('please add "-s server", server like:')
    if is_ocr:
        return {s.name: s.key for s in get_servers_o()}
    return {s.name: s.key for s in get_servers_t()}


def set_vpn():
    """_summary_
    """
    setting = Settings.get()

    # 设置代理地址和端口号
    proxy_address = setting.vpn_addr_port
    if len(proxy_address) > 0:
        # 设置环境变量
        os.environ['http_proxy'] = proxy_address
        os.environ['https_proxy'] = proxy_address


def req_text(s, key_server="", key_lang_n=-1):
    """子线程翻译

    Args:
        s (str): _description_
        key_server (str): _description_
        key_lang_n (int): _description_
    """

    try:
        if not key_server:
            return get_help_server(False)
        server: Server = create_server_t(key_server)

        lang_selected = lang_n2key(server, key_lang_n)

        if not lang_selected:
            return get_help_lang(server)
        print("translate", server.name, lang_selected.get_name())

        if not s:
            return _("no text")
        print(s)
        set_vpn()

        _ok, text = server.translate_text(s, lang_selected.key)
        return text

    except Exception as e:  # pylint: disable=W0718
        get_logger().error(e)
        error_msg = _("something error:")
        error_msg2 = f"{str(e)}\n\n{traceback.format_exc()}"
        return f"{error_msg}{server.name}\n\n{error_msg2}"


def req_ocr(s=None, key_server=None, key_lang_n=-1):
    """子线程翻译

    Args:
        s (str): _description_
        key_server (str): _description_
        key_lang_n (int): _description_
    """

    try:
        if not key_server:
            return get_help_server(True)
        server = create_server_o(key_server)

        lang_selected = lang_n2key(server, key_lang_n)

        if not lang_selected:
            return get_help_lang(server)

        if not s or not os.path.exists(s):
            return _("the file does not exist") + "\n" + s
        print("ocr", server.name, lang_selected.get_name())
        set_vpn()

        _ok, text = server.ocr_image(s, lang_selected.key)
        return text

    except Exception as e:  # pylint: disable=W0718
        get_logger().error(e)
        error_msg = _("something error:")
        error_msg2 = f"{str(e)}\n\n{traceback.format_exc()}"
        return f"{error_msg}{server.name}\n\n{error_msg2}"
