"""阿里云
"""
import base64
import hashlib
import hmac
import random
import string
from datetime import datetime, timezone
from gettext import gettext as _
from urllib.parse import quote, quote_plus

from lfy.api.server import TIME_OUT
from lfy.api.server.tra import ServerTra
from lfy.utils import s2ks


def _compose_string_to_sign(method, queries):
    sorted_key = sorted(list(queries.keys()))
    canonical_query_string = ''
    for key in sorted_key:
        canonical_query_string += \
            f'&{quote_plus(key)}={quote_plus(queries.get(key))}'

    return f"{method}&{quote_plus('/')}&{quote_plus(canonical_query_string[1:])}"


def _encode_rfc3986_uri_component(s):
    return quote(s, safe='~')


def _sign_string(sign, secret):
    hash_val = hmac.new(secret.encode("UTF-8"), sign.encode(
        "UTF-8"), hashlib.sha1).digest()
    signature = base64.encodebytes(hash_val).decode("UTF-8")
    return signature.rstrip('\n')


def _random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


def _get_iso_8061_date():
    return datetime.now(timezone.utc).isoformat()


def _translate(p: ServerTra, s, lang_to="en"):
    """翻译

    Args:
        s (str): 待翻译字符串
        api_key_s (str): 输入的原始字符串
        lang_to (str, optional): 字符串翻译为xx语言. Defaults to "auto".

    Returns:
        _type_: _description_
    """
    # .strip()
    access_key_id, access_key_secret = s2ks(p.get_conf())

    encoded_body = {
        "AccessKeyId": access_key_id,
        "Action": "TranslateGeneral",
        "Format": "JSON",
        "FormatType": "text",
        "SignatureMethod": "HMAC-SHA1",
        "SignatureNonce": quote(_random_string(12)),
        "SignatureVersion": "1.0",
        "SourceLanguage": "auto",
        "SourceText": _encode_rfc3986_uri_component(s),
        "TargetLanguage": lang_to,
        "Timestamp": _get_iso_8061_date(),
        "Version": "2018-10-12"
    }

    string_to_sign = _compose_string_to_sign("POST", encoded_body)
    signature = _sign_string(string_to_sign,
                             access_key_secret + "&")

    encoded_body["Signature"] = signature

    response = p.session.post("https://mt.aliyuncs.com/",
                              headers={"Content-Type":
                                       "application/x-www-form-urlencoded"},
                              data=encoded_body, timeout=TIME_OUT)
    result = response.json()
    if result["Code"] == "200":
        return True, result["Data"]["Translated"]

    return False, _("something error: {}")\
        .format(f'{result["Code"]}: {result["Message"]}')


class AliYunServer(ServerTra):
    """阿里云翻译
    """

    def __init__(self):

        # Development documentation
        # https://help.aliyun.com/zh/machine-translation/developer-reference/machine-translation-language-code-list
        lang_key_ns = {
            "zh": 1,
            "en": 3,
            "ja": 4,
            "ko": 5,
            "de": 6,
            "fr": 7,
            "it": 8
        }
        super().__init__("aliyun", _("aliyun"))
        self.set_data(lang_key_ns, "AccessKey ID | AccessKey Secret")

    def check_conf(self, conf_str, fun_check=_translate, py_libs=None):
        return super().check_conf(conf_str, fun_check)

    def main(self, *args, **kwargs):
        return super().main(*args, fun_main=_translate)
