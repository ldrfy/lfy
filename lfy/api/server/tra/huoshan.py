"""火山：https://www.volcengine.com/docs/4640/127684
"""
import hashlib
import hmac
import json
from datetime import datetime, timezone
from gettext import gettext as _

from lfy.api.server import TIME_OUT, Server
from lfy.utils import s2ks
from lfy.utils.settings import Settings


def hex_digest(input_bytes):
    return input_bytes.hex()


def sha256_digest(input_str):
    return hashlib.sha256(input_str.encode()).digest()


def hmac_sha256_digest(key, msg):
    return hmac.new(key, msg.encode(), hashlib.sha256).digest()


def get_date_time_now():
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def get_signing_key(sk, meta_data):
    k_date = hmac_sha256_digest(sk.encode(), meta_data['date'])
    k_region = hmac_sha256_digest(k_date, meta_data['region'])
    k_service = hmac_sha256_digest(k_region, meta_data['service'])
    return hmac_sha256_digest(k_service, "request")


def get_string_headers(header):
    str_headers = ""
    keys = sorted(header.keys())
    for key in keys:
        str_headers += f"{key.lower()}:{header[key]}\n"
    return str_headers


def get_signed_headers(header):
    keys = sorted(header.keys())
    header_list = [v.lower() for v in keys]
    return ";".join(header_list)


def _translate(session, s, api_key_s, lang_to="en", lang_from="auto"):
    """翻译

    Args:
        s (str): 待翻译字符串
        api_key_s (str): 密钥
        lang_to (str, optional): 字符串翻译为xx语言. Defaults to "auto".
        lang_from (str, optional): 待翻译字符串语言. Defaults to "auto".

    Returns:
        _type_: _description_
    """

    ak, sk = s2ks(api_key_s)

    if ak is None or ak == "Access Key ID":
        return False, _("please input API Key in preference")

    # 签名算法
    # https://www.volcengine.com/docs/6369/67269
    # 文档
    # https://www.volcengine.com/docs/4640/65067
    curr_time = get_date_time_now()

    data = {
        "method": "POST",
        "url": "/",
        "param": "Action=TranslateText&Version=2020-06-01",
        "service": "translate",
        "region": "cn-north-1",
        "version": "2020-06-01",
        "date": curr_time,
        "algorithm": "HMAC-SHA256"
    }

    request_body = {
        "TargetLanguage": lang_to,
        "TextList": [s]
    }
    if "auto" != lang_from:
        request_body["SourceLanguage"] = lang_from

    x_content_sha256 = hex_digest(sha256_digest(json.dumps(request_body)))

    header = {
        "Content-Type": "application/json",
        "X-Date": curr_time,
        "X-Content-Sha256": x_content_sha256
    }

    canonical_request = "\n".join([
        data["method"],
        data["url"],
        data["param"],
        get_string_headers(header),
        get_signed_headers(header),
        header["X-Content-Sha256"]
    ])

    hash_canonical_request = hex_digest(sha256_digest(canonical_request))
    credential_scope = f"{curr_time}/{data['region']}/{data['service']}/request"

    signing_str = "\n".join([
        data["algorithm"],
        curr_time,
        credential_scope,
        hash_canonical_request
    ])

    signing_key = get_signing_key(sk, data)
    sign = hex_digest(hmac_sha256_digest(signing_key, signing_str))

    authorization = ", ".join([
        f"{data['algorithm']} Credential={ak}/{credential_scope}",
        "SignedHeaders=" + get_signed_headers(header),
        f"Signature={sign}"
    ])

    header["Authorization"] = authorization

    res = session.post(
        "https://translate.volcengineapi.com/?Action=TranslateText&Version=2020-06-01",
        headers=header, data=json.dumps(request_body), timeout=TIME_OUT
    ).json()

    if "Error" in res["ResponseMetadata"]:
        rmd = res["ResponseMetadata"]["Error"]
        return False, _("something error: {}").format(f'\n\n{rmd["Code"]}: {rmd["Message"]}')

    translation_list = res.get("TranslationList", [])
    if translation_list:
        return True, translation_list[0]['Translation']

    return False, f"{error_msg} unknown"


class HuoShanServer(Server):
    """火山翻译 https://www.volcengine.com/docs/4640/65067
    """

    def __init__(self):

        # Development documentation
        # https://www.volcengine.com/docs/4640/35107
        lang_key_ns = {
            "zh": 1,
            "en": 3,
            "ja": 4,
            "ko": 5,
            "de": 6,
            "fr": 7,
            "it": 8
        }
        super().__init__("huoshan", _("huoshan"), lang_key_ns)
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
            "Access Key ID", "Secret Access Key")
        if "|" not in api_key_s:
            return False, error_msg + " LTAI5tQiXnC6ffwfe | rWPiBuk1xdwwdfafwefwef"
        ok, text = _translate(self.session, "success", api_key_s)
        if ok:
            Settings().s("server-sk-huoshan", api_key_s)
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
        return Settings().g("server-sk-huoshan")
        # Access Key ID|Secret Access Key
