"""火山：https://www.volcengine.com/docs/4640/127684
"""
import hashlib
import hmac
import json
from datetime import datetime, timezone
from gettext import gettext as _

from lfy.api.server import TIME_OUT
from lfy.api.server.tra import ServerTra
from lfy.utils import s2ks


def _hex_digest(input_bytes):
    return input_bytes.hex()


def _sha256_digest(input_str):
    return hashlib.sha256(input_str.encode()).digest()


def _hmac_sha256_digest(key, msg):
    return hmac.new(key, msg.encode(), hashlib.sha256).digest()


def _get_date_time_now():
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def _get_signing_key(sk, meta_data):
    k_date = _hmac_sha256_digest(sk.encode(), meta_data['date'])
    k_region = _hmac_sha256_digest(k_date, meta_data['region'])
    k_service = _hmac_sha256_digest(k_region, meta_data['service'])
    return _hmac_sha256_digest(k_service, "request")


def _get_string_headers(header):
    str_headers = ""
    keys = sorted(header.keys())
    for key in keys:
        str_headers += f"{key.lower()}:{header[key]}\n"
    return str_headers


def _get_signed_headers(header):
    keys = sorted(header.keys())
    header_list = [v.lower() for v in keys]
    return ";".join(header_list)


def _get_data(request_body, sk, ak):

    # 签名算法
    # https://www.volcengine.com/docs/6369/67269
    # 文档
    # https://www.volcengine.com/docs/4640/65067
    curr_time = _get_date_time_now()

    d = {
        "method": "POST",
        "url": "/",
        "param": "Action=TranslateText&Version=2020-06-01",
        "service": "translate",
        "region": "cn-north-1",
        "version": "2020-06-01",
        "date": curr_time,
        "algorithm": "HMAC-SHA256"
    }

    x_content_sha256 = _hex_digest(_sha256_digest(json.dumps(request_body)))

    header = {
        "Content-Type": "application/json",
        "X-Date": curr_time,
        "X-Content-Sha256": x_content_sha256
    }

    canonical_request = "\n".join([
        d["method"],
        d["url"],
        d["param"],
        _get_string_headers(header),
        _get_signed_headers(header),
        header["X-Content-Sha256"]
    ])

    hash_canonical_request = _hex_digest(_sha256_digest(canonical_request))
    credential_scope = f"{curr_time}/{d['region']}/{d['service']}/request"

    signing_str = "\n".join([
        d["algorithm"],
        curr_time,
        credential_scope,
        hash_canonical_request
    ])

    signing_key = _get_signing_key(sk, d)
    sign = _hex_digest(_hmac_sha256_digest(signing_key, signing_str))

    header["Authorization"] = ", ".join([
        f"{d['algorithm']} Credential={ak}/{credential_scope}",
        "SignedHeaders=" + _get_signed_headers(header),
        f"Signature={sign}"
    ])

    return header


def _translate(p: ServerTra, s, lang_to="en"):
    """翻译

    Args:
        s (str): 待翻译字符串
        api_key_s (str): 密钥
        lang_to (str, optional): 字符串翻译为xx语言. Defaults to "auto".

    Returns:
        _type_: _description_
    """

    ak, sk = s2ks(p.get_conf())

    request_body = {
        # "SourceLanguage": "auto",
        "TargetLanguage": lang_to,
        "TextList": [s]
    }
    header = _get_data(request_body, sk, ak)

    res: dict = p.session.post(
        "https://translate.volcengineapi.com/?Action=TranslateText&Version=2020-06-01",
        headers=header, data=json.dumps(request_body), timeout=TIME_OUT
    ).json()

    if "Error" in res["ResponseMetadata"]:
        rmd = res["ResponseMetadata"]["Error"]
        return False, _("something error: {}").format(f'\n\n{rmd["Code"]}: {rmd["Message"]}')

    translation_list = res.get("TranslationList", [])
    if translation_list:
        return True, translation_list[0]['Translation']

    return False, "unknown"


class HuoShanServer(ServerTra):
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
        super().__init__("huoshan", _("huoshan"))
        # https://www.volcengine.com/docs/4640/127684
        self.set_data(lang_key_ns, "Access Key ID | Secret Access Key")

    def check_conf(self, conf_str, fun_check=_translate, py_libs=None):
        return super().check_conf(conf_str, fun_check)

    def main(self, *args, **kwargs):
        return super().main(*args, fun_main=_translate)
