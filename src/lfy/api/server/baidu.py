import base64
import hashlib
import random
import urllib
from gettext import gettext as _

import requests

from lfy.api.server import TIME_OUT

HOW_GET_URL_TRANSLATE = "https://doc.tern.1c7.me/zh/folder/setting/#%E7%99%BE%E5%BA%A6"
HOW_GET_URL_OCR = "https://cloud.baidu.com/doc/OCR/s/dk3iqnq51"

URL_TRANSLATE = "https://api.fanyi.baidu.com/api/trans/vip/translate"

SERVER_KEY = "baidu"


def translate_text(s, lang_to="auto", lang_from="auto"):
    """翻译

    Args:
        text (_type_): _description_
        lang_from (str, optional): _description_. Defaults to "auto".
        lang_to (str, optional): _description_. Defaults to "auto".

    Returns:
        _type_: _description_
    """
    sk = "|"

    app_id = sk.split("|")[0]
    secret_key = sk.split("|")[1]

    if len(app_id) == 0 or len(secret_key) == 0:
        no_sk = _("please set baidu app_id and secret_key like this:")
        return f'{no_sk}\n\n{HOW_GET_URL_TRANSLATE}'

    s1, ok = translate(s, app_id, secret_key, lang_to)
    print(ok, s, lang_from, lang_to)
    return s1


def check_translate(app_id, secret_key):
    """_summary_

    Args:
        app_id (_type_): _description_
        secret_key (_type_): _description_

    Returns:
        _type_: _description_
    """
    text, ok = translate("test", app_id, secret_key)
    print(text)
    return ok


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

    ok = True

    salt = random.randint(32768, 65536)
    sign = app_id + s + str(salt) + secret_key
    sign = hashlib.md5(sign.encode()).hexdigest()
    url = f"{URL_TRANSLATE}?appid=%s&q=%s&from=%s&to=%s&salt=%s&sign=%s"
    url = url % (app_id, urllib.parse.quote(s), lang_from, lang_to, salt, sign)
    s1 = ""

    request = requests.get(url, timeout=TIME_OUT)
    result = request.json()

    s1 = ""
    if "error_code" in result:
        ok = False
        s1 = f'{result["error_code"]}: {result["error_msg"]}'
    else:
        for trans_result in result["trans_result"]:
            s1 += f'{trans_result["dst"]}\n'

    return s1, ok
