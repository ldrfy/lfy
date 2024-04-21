"""翻译接口

Returns:
    _type_: _description_
"""
import os
from gettext import gettext as _

from requests.exceptions import ConnectTimeout

from lfy.api.utils import create_server
from lfy.settings import Settings

# 设置代理地址和端口号
PROXY_ADDRESS = Settings.get().vpn_addr_port
if len(PROXY_ADDRESS) > 0:
    # 设置环境变量
    os.environ['http_proxy'] = PROXY_ADDRESS
    os.environ['https_proxy'] = PROXY_ADDRESS


def translate_by_server(text, server_key, lang_to, lang_from="auto"):
    """翻译

    Args:
        text (str): _description_
        server (str): _description_
        lang_to (str): _description_
        lang_from (str, optional): _description_. Defaults to "auto".

    Returns:
        _type_: _description_
    """
    try:
        if len(text.strip()) == 0:
            return _("Copy automatic translation, it is recommended to pin this window to the top")

        print("翻译服务", server_key, lang_to)
        return create_server(server_key).translate_text(text, lang_to, lang_from)

    except ConnectTimeout as e:
        s = _("The connection timed out. Maybe there is a network problem")
        return f"{s}: \n\n {e}"
    except Exception as e:  # pylint: disable=W0718
        s = _("something error, try other translate engine?")
        return f"{s}：\n\n {e}"


def check_translate(server_key, api_key):
    """_summary_

    Args:
        server_key (_type_): _description_
        api_key (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        return create_server(server_key).check_translate(api_key)
    except ConnectTimeout as e:
        s = _("The connection timed out. Maybe there is a network problem")
        return f"{s}: \n\n {e}"
    except Exception as e:  # pylint: disable=W0718
        s = _("something error, open it again and try again?")
        return f"{s}：\n\n {e}"


def get_api_key_s(server_key):
    """通过设置获取api相关的字符串

    Args:
        server_key (_type_): _description_

    Returns:
        _type_: _description_
    """
    return create_server(server_key).get_api_key_s()
