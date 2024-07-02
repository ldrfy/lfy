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

import requests

from lfy.api.base import TIME_OUT, Server
from lfy.settings import Settings


class AliYunServer(Server):
    """百度翻译

    Args:
        Server (_type_): _description_
    """

    def __init__(self):

        # Development documentation
        # https://help.aliyun.com/zh/machine-translation/developer-reference/machine-translation-language-code-list
        lang_key_ns = {
            "auto": 0,
            "zh": 1,
            "en": 3,
            "ja": 4,
            "ko": 5,
            "de": 6,
            "fr": 7,
            "it": 8
        }
        self.session = None
        super().__init__("aliyun", _("aliyun"), lang_key_ns)

    def check_translate(self, api_key_s):
        """保存时核对 api_key_s

        Args:
            api_key (str): 保存api_key

        Returns:
            bool: _description_
        """
        access_key_id = "AccessKey ID"
        access_key_secret = "AccessKey Secret"
        error_msg_template = _("please input {} and {} like:")
        error_msg = error_msg_template.format(access_key_id, access_key_secret)
        if "|" not in api_key_s:
            return False, error_msg + " LTAI5tQiXnC6ffwfe | rWPiBuk1xdwwdfafwefwef"
        ok, text = self._translate("success", api_key_s)
        if ok:
            Settings.get().server_sk_aliyun = api_key_s
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
        _ok, text = self._translate(
            text, self.get_api_key_s(), lang_to, lang_from)
        return text

    def get_api_key_s(self):
        """设置自动加载保存的api

        Returns:
            _type_: _description_
        """
        return Settings.get().server_sk_aliyun

    def _get_session(self):
        """初始化请求
        """
        if self.session is None:
            self.session = requests.Session()
        return self.session

    def _translate(self, s, api_key_s, lang_to="en", lang_from="auto"):
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
        [access_key_id, access_key_secret] = api_key_s.split("|")
        access_key_id = access_key_id.strip()
        access_key_secret = access_key_secret.strip()

        if access_key_id == "AccessKey ID" or access_key_secret == "AccessKey Secret":
            return False, _("please input API Key in preference")

        encoded_body = {
            "AccessKeyId": access_key_id,
            "Action": "TranslateGeneral",
            "Format": "JSON",
            "FormatType": "text",
            "SignatureMethod": "HMAC-SHA1",
            "SignatureNonce": quote(self._random_string(12)),
            "SignatureVersion": "1.0",
            "SourceLanguage": lang_from,
            "SourceText": self._encode_rfc3986_uri_component(s),
            "TargetLanguage": lang_to,
            "Timestamp": self._get_iso_8061_date(),
            "Version": "2018-10-12"
        }

        string_to_sign = self._compose_string_to_sign("POST", encoded_body)
        signature = self._sign_string(
            string_to_sign, access_key_secret + "&")

        encoded_body["Signature"] = signature

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = requests.post("https://mt.aliyuncs.com/",
                                 headers=headers, data=encoded_body, timeout=TIME_OUT)
        result = response.json()
        if result["Code"] == "200":
            return True, result["Data"]["Translated"]

        error_msg = _("something error:")
        return False, f'{error_msg}\n\n{result["Code"]}: {result["Message"]}'

    def _get_iso_8061_date(self):
        return datetime.now(timezone.utc).isoformat()

    def _base64_encode(self, buffer):
        return base64.b64encode(buffer).decode('utf-8')

    def _random_string(self, length):
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for _ in range(length))

    def _sign_string(self, sign, secret):
        hash_val = hmac.new(secret.encode("UTF-8"), sign.encode(
            "UTF-8"), hashlib.sha1).digest()
        signature = base64.encodebytes(hash_val).decode("UTF-8")
        return signature.rstrip('\n')

    def _compose_string_to_sign(self, method, queries):
        sorted_key = sorted(list(queries.keys()))
        canonicalized_query_string = ''
        for key in sorted_key:
            canonicalized_query_string += \
                f'&{quote_plus(key)}={quote_plus(queries.get(key))}'

        string_to_sign = method + "&" + \
            quote_plus('/') + "&" + \
            quote_plus(canonicalized_query_string[1:])
        return string_to_sign

    def _encode_rfc3986_uri_component(self, s):
        return quote(s, safe='~')
