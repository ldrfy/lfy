'终端翻译'
import os
import traceback
from gettext import gettext as _

from gi.repository import Gdk

from lfy.api import (create_server_o, create_server_t, get_servers_o,
                     get_servers_t, server_key2i)
from lfy.api.constant import CODE_SERVER_N_DEFAULT, CODE_SERVER_N_HELP
from lfy.api.server import Server
from lfy.api.utils.debug import get_logger
from lfy.settings import Settings


def get_help_lang(server: Server):
    """某个服务的lang key

    Args:
        server (Server): _description_
        j (int, optional): _description_. Defaults to -1.

    Returns:
        _type_: _description_
    """
    # 每个翻译对应的key
    return {lang.get_name(): j for j, lang in enumerate(server.langs)}


def get_help_server(is_ocr=False):
    """某个服务的lang key

    Args:
        server (Server): _description_
        j (int, optional): _description_. Defaults to -1.

    Returns:
        _type_: _description_
    """
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


def req_text(s=None, key_server=None, lang_j=-1):
    """子线程翻译

    Args:
        s (str): _description_
        server (Server): _description_
    """
    print(s)
    set_vpn()

    try:
        if key_server is None:
            return get_help_server(False)
        server = create_server_t(key_server)
        if lang_j < 0:
            return get_help_lang(server)

        key_lang = server.get_lang(lang_j).key
        print("tra", server.name, key_lang)
        _ok, text = server.translate_text(s, key_lang)
        return text

    except Exception as e:  # pylint: disable=W0718
        get_logger().error(e)
        error_msg = _("something error:")
        error_msg2 = f"{str(e)}\n\n{traceback.format_exc()}"
        return f"{error_msg}{server.name}\n\n{error_msg2}"


def req_ocr(s=None, key_server=None, ocr_key=None):
    """子线程翻译

    Args:
        s (str): _description_
        server (Server): _description_
    """
    set_vpn()

    try:
        if key_server is None:
            return get_help_server(True)

        server = create_server_o(key_server)
        print("ocr", server.name, ocr_key)
        _ok, text = server.ocr_image(s, ocr_key)
        return text

    except Exception as e:  # pylint: disable=W0718
        get_logger().error(e)
        error_msg = _("something error:")
        error_msg2 = f"{str(e)}\n\n{traceback.format_exc()}"
        return f"{error_msg}{server.name}\n\n{error_msg2}"


def req_clip():
    """获取截剪贴板
    """
    print("req_clip")

    def on_active_copy(cb2, res):
        req_text(cb2.read_text_finish(res))

    cb = Gdk.Display().get_default().get_clipboard()
    cb.read_text_async(None, on_active_copy)
