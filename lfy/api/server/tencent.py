"""腾讯翻译接口
"""
import base64
import hashlib
import hmac
import random
import time
from gettext import gettext as _

import requests

from lfy.api.base import TIME_OUT, Server
from lfy.settings import Settings

URL_HOW_GET_TRANSLATE = "https://doc.tern.1c7.me/zh/folder/setting/#%E8%85%BE%E8%AE%AF%E4%BA%91"


# Development documentation
# https://cloud.tencent.com/document/product/551/15619
lang_key_ns = {
    "zh": 1,
    "en": 3,
    "jp": 4,
    "kr": 5,
    "de": 6,
    "fr": 7,
    "it": 8,
}

SERVER = Server("tencent", _("tencent"), lang_key_ns,
                True, URL_HOW_GET_TRANSLATE)


public_params = {}

error_msg2zh = {"FailedOperation.NoFreeAmount": "t_NoFreeAmount"}


def get_api_key_s():
    """设置自动加载保存的api

    Returns:
        str: _description_
    """
    return Settings.get().server_sk_tencent


def check_translate(api_key):
    """保存时核对api

    Args:
        api_key (_type_): _description_

    Returns:
        _type_: _description_
    """
    error = _("please input secret_id and secret_key like:")
    if "|" not in api_key:
        return False, error + " a121343 | fdsdsdg"
    secret_id, secret_key = get_api_key(api_key)
    ok, text = translate("success", secret_id, secret_key, "en")
    if ok:
        Settings.get().server_sk_tencent = api_key
    return ok, text


def translate_text(s, lang_to="auto", lang_from="auto"):
    """翻译接口

    Args:
        s (_type_): _description_
        lang_to (str, optional): _description_. Defaults to "auto".
        lang_from (str, optional): _description_. Defaults to "auto".

    Returns:
        _type_: _description_
    """
    secret_id, secret_key = get_api_key(get_api_key_s())

    if secret_id == "secret_id" or secret_key == "secret_key":
        return _("please input API Key in preference")

    _ok, text = translate(s, secret_id, secret_key, lang_to, lang_from)
    return text


def translate(query_text,
              secret_id,
              secret_key,
              lang_to="zh",
              lang_from="auto"):
    """_summary_

    Args:
        query_text (_type_): _description_
        secret_id (_type_): _description_
        secret_key (_type_): _description_
        lang_from (str, optional): _description_. Defaults to "auto".
        lang_to (str, optional): _description_. Defaults to "zh".

    Returns:
        _type_: _description_
    """

    data = {
        "Action": "TextTranslate",
        "Region": "ap-beijing",
        "SecretId": secret_id,
        "Timestamp": int(time.time()),
        "Nonce": random.randint(1, 1e6),
        "Version": "2018-03-21",
        "ProjectId": 0,
        "Source": lang_from,
        "SourceText": query_text,
        "Target": lang_to
    }
    ENDPOINT = "tmt.tencentcloudapi.com"
    s = get_string_to_sign("GET", ENDPOINT, data)

    data["Signature"] = sign_str(secret_key, s, hashlib.sha1)
    request = requests.get("https://" + ENDPOINT,
                           params=data,
                           timeout=TIME_OUT)

    result = request.json()["Response"]
    if "Error" in result:
        error_msg = _("something error:")
        print(result)
        return False, f'{error_msg}\n\n{result["Error"]["Code"]}: {result["Error"]["Message"]}'

    return True, result["TargetText"]


def get_string_to_sign(method, endpoint, params):
    """_summary_

    Args:
        method (_type_): _description_
        endpoint (_type_): _description_
        params (_type_): _description_

    Returns:
        _type_: _description_
    """
    s = method + endpoint + "/?"
    query_str = "&".join("%s=%s" % (k, params[k]) for k in sorted(params))
    return s + query_str


def sign_str(key, s, method):
    """_summary_

    Args:
        key (_type_): _description_
        s (_type_): _description_
        method (_type_): _description_

    Returns:
        _type_: _description_
    """
    hmac_str = hmac.new(key.encode("utf8"), s.encode("utf8"), method).digest()
    return base64.b64encode(hmac_str)


def get_api_key(api_key):
    """_summary_

    Args:
        api_key (_type_): _description_

    Returns:
        _type_: _description_
    """
    [secret_id, secret_key] = api_key.split("|")
    return secret_id.strip(), secret_key.strip()
