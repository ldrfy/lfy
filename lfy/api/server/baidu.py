"""百度翻译接口
"""
import base64
import hashlib
import random
import time
from gettext import gettext as _
from urllib.parse import quote

from lfy.api.server import TIME_OUT, Server
from lfy.api.utils import s2ks
from lfy.settings import Settings


def _translate(session, s, api_key_s, lang_to="auto", lang_from="auto"):
    """翻译

    Args:
        s (str): 待翻译字符串
        api_key_s (str): 输入的原始字符串
        lang_to (str, optional): 字符串翻译为xx语言. Defaults to "auto".
        lang_from (str, optional): 待翻译字符串语言. Defaults to "auto".

    Returns:
        _type_: _description_
    """

    app_id, secret_key = s2ks(api_key_s)
    if app_id is None or app_id == "app_id":
        return False, _("please input API Key in preference")

    url = "https://api.fanyi.baidu.com/api/trans/vip/translate"
    url = f"{url}?from={lang_from}&to={lang_to}&appid={app_id}&q={quote(s)}"

    salt = random.randint(32768, 65536)
    sign = app_id + s + str(salt) + secret_key
    sign = hashlib.md5(sign.encode()).hexdigest()
    url = f"{url}&salt={salt}&sign={sign}"

    result = session.get(url, timeout=TIME_OUT).json()

    error_msg = _("something error:")
    if "error_code" not in result:
        s1 = ""
        for trans_result in result["trans_result"]:
            s1 += f'{trans_result["dst"]}\n'
        return True, s1.strip()

    return False, f'{error_msg}\n\n{result["error_code"]}: {result["error_msg"]}'


def _get_token(session, ocr_api_key_s):
    """https://ai.baidu.com/ai-doc/REFERENCE/Ck3dwjhhu

    Returns:
        _type_: _description_
    """
    sg = Settings.get()

    expires_in_date = sg.ocr_baidu_token_expires_date

    if expires_in_date - time.time() > 0:
        access_token = sg.ocr_baidu_token
        if len(access_token) != 0:
            return True, access_token

    api_key, secret_key = s2ks(ocr_api_key_s)
    # API Key | Secret Key
    if api_key is None or api_key == "API Key":
        return False, _("please input API Key in preference") + ": OCR"

    ok, access_token, expires_in_date = \
        _get_token_by_url(session, api_key, secret_key)

    if ok:
        sg.ocr_baidu_token = access_token
        sg.ocr_baidu_token_expires_date = expires_in_date

    return ok, access_token


def _get_token_by_url(session, api_key, secret_key):
    """获取token

    Args:
        api_key (_type_): _description_
        secret_key (_type_): _description_

    Returns:
        _type_: _description_
    """
    ok = False
    expires_in_date = -1

    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    url0 = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials"
    url = f'{url0}&client_id={api_key}&client_secret={secret_key}'

    request = session.get(url, timeout=TIME_OUT)

    jsons = request.json()
    if "access_token" not in jsons:
        access_token = "错误：" + jsons["error_description"]
    else:
        access_token = jsons["access_token"]
        expires_in_date = time.time() + jsons["expires_in"]
        ok = True

    return ok, str(access_token), expires_in_date


class BaiduServer(Server):
    """百度翻译
    """

    def __init__(self):

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
        super().__init__("baidu", _("baidu"), lang_key_ns)

    def check_translate(self, api_key_s):
        """保存时核对 api_key_s

        Args:
            api_key_s (str): 保存api_key

        Returns:
            bool: _description_
        """
        error_msg = _("please input app_id and secret_key like:")
        if "|" not in api_key_s:
            return False, error_msg + " 121343 | fdsdsdg"
        ok, text = _translate(self.session, "success", api_key_s)
        if ok:
            Settings.get().server_sk_baidu = api_key_s
        return ok, text

    def translate_text(self, text, lang_to="auto", lang_from="auto"):
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
        return Settings.get().server_sk_baidu

    def get_ocr_api_key_s(self):
        """图片识别的字符串apikey

        Returns:
            _type_: _description_
        """
        return Settings.get().server_sk_baidu_ocr

    def ocr_image(self, img_path):
        img_data = open(img_path, 'rb').read()
        img = base64.b64encode(img_data)

        # open('./images/lt.png', 'rb').read()
        s = ""
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/"

        request_url += "general_basic"

        ok, token = _get_token(self.session, self.get_ocr_api_key_s())
        if not ok:
            return False, token
        params = {"image": img}
        request_url = request_url + "?access_token=" + token
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        res = self.session.post(request_url,
                                data=params,
                                headers=headers,
                                timeout=TIME_OUT).json()

        if "error_code" in res:
            if 110 == res["error_code"]:
                Settings.get().ocr_baidu_token = ""
            error_msg = _("something error:")
            return False, f'{error_msg}\n\n{res["error_code"]}: {res["error_msg"]}'

        for word in res["words_result"]:
            s += word["words"] + '\n'

            s_ = word["words"]
            if s_[len(s_) - 1:len(s_)] != "-":
                s += " "

        return ok, s

    def check_ocr(self, api_key_ocr_s):
        """OCR测试

        Args:
            api_key_ocr_s (str): _description_

        Returns:
            _type_: _description_
        """
        api_key, secret_key = s2ks(api_key_ocr_s)
        if api_key is None or api_key == "API Key":
            error_msg = _("please input API Key and Secret Key like:")
            return False, error_msg + " 121343 | fdsdsdg"

        ok, access_token, expires_in_date = \
            _get_token_by_url(self.session, api_key, secret_key)
        if ok:
            sg = Settings.get()
            sg.server_sk_baidu_ocr = api_key_ocr_s
            sg.ocr_baidu_token = access_token
            sg.ocr_baidu_token_expires_date = expires_in_date
        return ok, "success"
