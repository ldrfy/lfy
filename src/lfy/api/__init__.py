"""翻译接口

Returns:
    _type_: _description_
"""
import os
from gettext import gettext as _

from requests.exceptions import ConnectTimeout

from lfy.api.server import baidu, google, tencent, youdao
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
        text (_type_): _description_
        server (_type_): _description_
        lang_to (_type_): _description_
        lang_from (str, optional): _description_. Defaults to "auto".

    Returns:
        _type_: _description_
    """
    try:
        print(server_key, lang_to)
        if len(text.strip()) == 0:
            return _("Copy automatic translation, it is recommended to pin this window to the top")

        if server_key == youdao.SERVER.key:
            return youdao.translate_text(text, lang_to, lang_from)
        elif server_key == google.SERVER.key:
            return google.translate_text(text, lang_to, lang_from)
        elif server_key == baidu.SERVER.key:
            return baidu.translate_text(text, lang_to, lang_from)
        elif server_key == tencent.SERVER.key:
            return tencent.translate_text(text, lang_to, lang_from)
        else:
            return f"暂不支持：{server_key}"

    except ConnectTimeout as e:
        s = _("The connection timed out. Maybe there is a network problem")
        return f"{s}: \n\n {e}"
    except Exception as e:
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
    print("check_translate", server_key, api_key)
    ok = False
    text = _("Not supported This Server!")

    if server_key == baidu.SERVER.key:
        ok, text = baidu.check_translate(api_key)
    if server_key == tencent.SERVER.key:
        ok, text = tencent.check_translate(api_key)
    if ok:
        text = _("save success!")
    return ok, text

def get_api_key_s(server_key):
    """_summary_

    Args:
        server_key (_type_): _description_

    Returns:
        _type_: _description_
    """
    if server_key == baidu.SERVER.key:
        return baidu.get_api_key_s()
    if server_key == tencent.SERVER.key:
        return tencent.get_api_key_s()
    else:
        return _("Not supported This Server!")
