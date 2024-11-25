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

from lfy.api.server import TIME_OUT, Server
from lfy.utils import s2ks
from lfy.utils.settings import Settings


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


def _base64_encode(buffer):
    return base64.b64encode(buffer).decode('utf-8')


def _get_iso_8061_date():
    return datetime.now(timezone.utc).isoformat()


def _translate(session, s, api_key_s, lang_to="en", lang_from="auto"):
    """翻译

    Args:
        s (str): 待翻译字符串
        api_key_s (str): 输入的原始字符串
        lang_to (str, optional): 字符串翻译为xx语言. Defaults to "auto".
        lang_from (str, optional): 待翻译字符串语言. Defaults to "auto".

    Returns:
        _type_: _description_
    """
    # .strip()
    access_key_id, access_key_secret = s2ks(api_key_s)

    if access_key_secret is None or access_key_id == "AccessKey ID":
        return False, _("please input API Key in preference")

    encoded_body = {
        "AccessKeyId": access_key_id,
        "Action": "TranslateGeneral",
        "Format": "JSON",
        "FormatType": "text",
        "SignatureMethod": "HMAC-SHA1",
        "SignatureNonce": quote(_random_string(12)),
        "SignatureVersion": "1.0",
        "SourceLanguage": lang_from,
        "SourceText": _encode_rfc3986_uri_component(s),
        "TargetLanguage": lang_to,
        "Timestamp": _get_iso_8061_date(),
        "Version": "2018-10-12"
    }

    string_to_sign = _compose_string_to_sign("POST", encoded_body)
    signature = _sign_string(
        string_to_sign, access_key_secret + "&")

    encoded_body["Signature"] = signature

    response = session.post("https://mt.aliyuncs.com/",
                            headers={
                                "Content-Type": "application/x-www-form-urlencoded"},
                            data=encoded_body, timeout=TIME_OUT)
    result = response.json()
    if result["Code"] == "200":
        return True, result["Data"]["Translated"]

    return False, _("something error: {}")\
        .format(f'{result["Code"]}: {result["Message"]}')


class AliYunServer(Server):
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
        super().__init__("aliyun", _("aliyun"), lang_key_ns)
        self.can_translate = True

    def check_translate(self, api_key_s):
        """保存时核对 api_key_s

        Args:
            api_key_s (str): 保存api_key

        Returns:
            bool: _description_
        """
        error_msg_template = _("please input {} and {} like:")
        error_msg = error_msg_template.format(
            "AccessKey ID", "AccessKey Secret")
        if "|" not in api_key_s:
            return False, error_msg + " XXXX | XXXX"
        ok, text = _translate(self.session, "success", api_key_s)
        if ok:
            Settings().s("server-sk-aliyun", api_key_s)
        return ok, text

    def translate_text(self, text, lang_to="en", lang_from="auto"):
        """翻译接口

        Args:
            text (_type_): 待翻译字符串
            lang_from (str, optional): _description_. Defaults to "auto".
            lang_to (str, optional): _description_. Defaults to "auto".

        Returns:
            _type_: _description_
        """
        return _translate(self.session, text, self.get_api_key_s(), lang_to, lang_from)

    def get_api_key_s(self):
        """设置自动加载保存的api

        Returns:
            _type_: _description_
        """
        return Settings().g("server-sk-aliyun")
