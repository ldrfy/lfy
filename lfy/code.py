import os
import traceback
from gettext import gettext as _

from gi.repository import Gdk

from lfy.api import create_server, get_lang, server_key2i
from lfy.settings import Settings


def req_text(s):
    """子线程翻译

    Args:
        s (str): _description_
        server (Server): _description_
    """
    print(s)
    setting = Settings.get()

    # 设置代理地址和端口号
    proxy_address = setting.vpn_addr_port
    if len(proxy_address) > 0:
        # 设置环境变量
        os.environ['http_proxy'] = proxy_address
        os.environ['https_proxy'] = proxy_address
    tran_server = create_server(setting.server_selected_key)

    try:

        i = server_key2i(setting.server_selected_key)

        gl = get_lang(i, setting.lang_selected_n)
        print(tran_server.name, gl.get_name())

        _ok, text = tran_server.translate_text(s, gl.key)
        print(text)

    except Exception as e:  # pylint: disable=W0718
        error_msg = _("something error:")
        error_msg2 = f"{str(e)}\n\n{traceback.format_exc()}"
        text = f"{error_msg}{tran_server.name}\n\n{error_msg2}"

def req_clip():
    print("req_clip")
    def on_active_copy(cb2, res):
        req_text(cb2.read_text_finish(res))

    cb = Gdk.Display().get_default().get_clipboard()
    cb.read_text_async(None, on_active_copy)
