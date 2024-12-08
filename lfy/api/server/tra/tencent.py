"""腾讯翻译接口
"""
import base64
import hashlib
import hmac
import random
import time
from gettext import gettext as _

from lfy.api.server import TIME_OUT
from lfy.api.server.tra import ServerTra
from lfy.utils import s2ks


def _get_string_to_sign(method, endpoint, params):
    """_summary_

    Args:
        method (_type_): _description_
        endpoint (_type_): _description_
        params (_type_): _description_

    Returns:
        _type_: _description_
    """
    query_str = "&".join(f"{k}={params[k]}" for k in sorted(params))
    return f"{method}{endpoint}/?{query_str}"


def _sign_str(key, s, method):
    """_summary_

    Args:
        key (_type_): _description_
        s (_type_): _description_
        method (_type_): _description_

    Returns:
        _type_: _description_
    """
    hmac_str = hmac.new(key.encode("utf8"),
                        s.encode("utf8"), method).digest()
    return base64.b64encode(hmac_str)


def _translate(p: ServerTra, query_text, lang_to="en"):
    """腾讯翻译接口

    Args:
        query_text (str): _description_
        api_key_s (str): secret_id|secret_key
        lang_to (str, optional): _description_. Defaults to "zh".

    Returns:
        _type_: _description_
    """

    secret_id, secret_key = s2ks(p.get_conf())

    data = {
        "Action": "TextTranslate",
        "Region": "ap-beijing",
        "SecretId": secret_id,
        "Timestamp": int(time.time()),
        "Nonce": random.randint(1, int(1e6)),
        "Version": "2018-03-21",
        "ProjectId": 0,
        "Source": "auto",
        "SourceText": query_text,
        "Target": lang_to
    }
    endpoint = "tmt.tencentcloudapi.com"
    s = _get_string_to_sign("GET", endpoint, data)

    data["Signature"] = _sign_str(secret_key, s, hashlib.sha1)
    request = p.session.get(f"https://{endpoint}",
                            params=data, timeout=TIME_OUT)

    result = request.json()["Response"]
    if "Error" in result:
        return False, _("something error: {}")\
            .format(f'\n\n{result["Error"]["Code"]}: {result["Error"]["Message"]}')

    return True, result["TargetText"]


class TencentServer(ServerTra):
    """tencent翻译
    """

    def __init__(self):
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
        super().__init__("tencent", _("tencent"))
        # https://cloud.tencent.com/document/product/551/104415
        self.set_data(lang_key_ns, "Secretid | Secretkey")

    def check_conf(self, conf_str, fun_check=_translate, py_libs=None):
        return super().check_conf(conf_str, fun_check)

    def main(self, *args, **kwargs):
        return super().main(*args, fun_main=_translate)
