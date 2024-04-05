"""百度翻译接口
"""
import hashlib
import random
import urllib
from gettext import gettext as _

import requests

from lfy.api.base import TIME_OUT, Server
from lfy.settings import Settings

URL_HOW_GET_TRANSLATE = "https://doc.tern.1c7.me/zh/folder/setting/#%E7%99%BE%E5%BA%A6"

URL_TRANSLATE = "https://api.fanyi.baidu.com/api/trans/vip/translate"


# Development documentation
# https://fanyi-api.baidu.com/doc/21
lang_key_ns = {
    "auto": 0,
    "zh": 1,
    "wyw": 2,
    "en": 3,
    "jp": 4,
    "kor": 5,
    "de": 6,
    "fra": 7,
    "it": 8
}

SERVER = Server("baidu", _("baidu"), lang_key_ns,
                True, URL_HOW_GET_TRANSLATE)


def get_api_key_s():
    """设置自动加载保存的api

    Returns:
        _type_: _description_
    """
    return Settings.get().server_sk_baidu


def check_translate(api_key):
    """保存时核对api

    Args:
        api_key (str): 保存api_key

    Returns:
        bool: _description_
    """
    error_msg = _("please input app_id and secret_key like:")
    if "|" not in api_key:
        return False, error_msg + " 121343 | fdsdsdg"
    app_id, secret_key = get_api_key(api_key)
    ok, text = translate("success", app_id, secret_key)
    if ok:
        Settings.get().server_sk_baidu = api_key
    return ok, text


def translate_text(s, lang_to="auto", lang_from="auto"):
    """翻译接口

    Args:
        text (_type_): _description_
        lang_from (str, optional): _description_. Defaults to "auto".
        lang_to (str, optional): _description_. Defaults to "auto".

    Returns:
        _type_: _description_
    """
    app_id, secret_key = get_api_key(get_api_key_s())
    if app_id == "app_id" or secret_key == "secret_key":
        return _("please input API Key in preference")

    ok, text = translate(s, app_id, secret_key, lang_to, lang_from)
    return text


def get_api_key(api_key):
    """_summary_

    Args:
        api_key (_type_): _description_

    Returns:
        _type_: _description_
    """
    [app_id, secret_key] = api_key.split("|")
    return app_id.strip(), secret_key.strip()


def translate(s, app_id, secret_key, lang_to="auto", lang_from="auto"):
    """翻译

    Args:
        s (_type_): _description_
        app_id (_type_): _description_
        secret_key (_type_): _description_
        lang_to (str, optional): _description_. Defaults to "auto".
        lang_from (str, optional): _description_. Defaults to "auto".

    Returns:
        _type_: _description_
    """

    salt = random.randint(32768, 65536)
    sign = app_id + s + str(salt) + secret_key
    sign = hashlib.md5(sign.encode()).hexdigest()
    url = f"{URL_TRANSLATE}?appid=%s&q=%s&from=%s&to=%s&salt=%s&sign=%s"
    url = url % (app_id, urllib.parse.quote(s), lang_from, lang_to, salt, sign)

    request = requests.get(url, timeout=TIME_OUT)
    result = request.json()
    error_msg = _("something error:")
    if "error_code" in result:
        return False, f'{error_msg}\n\n{result["error_code"]}: {result["error_msg"]}'
    else:
        s1 = ""
        for trans_result in result["trans_result"]:
            s1 += f'{trans_result["dst"]}\n'
        return True, s1
