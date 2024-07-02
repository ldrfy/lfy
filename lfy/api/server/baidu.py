"""百度翻译接口
"""
import base64
import hashlib
import random
import time
import urllib
from gettext import gettext as _

import requests

from lfy.api.base import TIME_OUT, Server
from lfy.settings import Settings


class BaiduServer(Server):
    """百度翻译

    Args:
        Server (_type_): _description_
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
        self.session = None
        super().__init__("baidu", _("baidu"), lang_key_ns)

    def check_translate(self, api_key_s):
        """保存时核对 api_key_s

        Args:
            api_key (str): 保存api_key

        Returns:
            bool: _description_
        """
        error_msg = _("please input app_id and secret_key like:")
        if "|" not in api_key_s:
            return False, error_msg + " 121343 | fdsdsdg"
        ok, text = self._translate("success", api_key_s)
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
        _ok, text = self._translate(
            text, self.get_api_key_s(), lang_to, lang_from)
        return text

    def get_api_key_s(self):
        """设置自动加载保存的api

        Returns:
            _type_: _description_
        """
        return Settings.get().server_sk_baidu

    def _get_session(self):
        """初始化请求
        """
        if self.session is None:
            self.session = requests.Session()
        return self.session

    def _translate(self, s, api_key_s, lang_to="auto", lang_from="auto"):
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
        [app_id, secret_key] = api_key_s.split("|")
        app_id = app_id.strip()
        secret_key = secret_key.strip()

        if app_id == "app_id" or secret_key == "secret_key":
            return False, _("please input API Key in preference")

        url = "https://api.fanyi.baidu.com/api/trans/vip/translate"

        url = f"{url}?from={lang_from}&to={lang_to}"
        url = f"{url}&appid={app_id}&q={urllib.parse.quote(s)}"

        salt = random.randint(32768, 65536)
        sign = app_id + s + str(salt) + secret_key
        sign = hashlib.md5(sign.encode()).hexdigest()
        url = f"{url}&salt={salt}&sign={sign}"

        result = self._get_session().get(url, timeout=TIME_OUT).json()

        error_msg = _("something error:")
        if "error_code" not in result:
            s1 = ""
            for trans_result in result["trans_result"]:
                s1 += f'{trans_result["dst"]}\n'
            return True, s1

        return False, f'{error_msg}\n\n{result["error_code"]}: {result["error_msg"]}'

    def get_ocr_api_key_s(self):
        """图片识别的字符串apikey

        Returns:
            _type_: _description_
        """
        return Settings.get().server_sk_baidu_ocr.split("|")

    def ocr_image(self, img_path):
        img_data = open(img_path, 'rb').read()
        img = base64.b64encode(img_data)

        # open('./images/lt.png', 'rb').read()
        s = ""
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/"

        request_url += "general_basic"

        ok, token = self._get_token()
        if not ok:
            return False, token
        params = {"image": img}
        request_url = request_url + "?access_token=" + token
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        res = requests.post(request_url,
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

    def check_ocr(self, api_key, secret_key):
        """OCR测试

        Args:
            api_key (_type_): _description_
            secret_key (_type_): _description_

        Returns:
            _type_: _description_
        """
        ok, _, _ = self._get_token_by_url(api_key, secret_key)
        return ok

    def _get_token_by_url(self, api_key, secret_key):
        """获取token

        Args:
            api_key (_type_): _description_
            secret_key (_type_): _description_

        Returns:
            _type_: _description_
        """
        ok = False
        access_token = ""
        expires_in_date = -1

        # client_id 为官网获取的AK， client_secret 为官网获取的SK
        host = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={
            api_key}&client_secret={secret_key}'

        request = requests.get(host, timeout=TIME_OUT)

        jsons = request.json()
        if "access_token" not in jsons:
            access_token = "错误：" + jsons["error_description"]
        else:
            access_token = jsons["access_token"]
            expires_in_date = time.time() + jsons["expires_in"]
            ok = True

        return ok, str(access_token), expires_in_date

    def _get_token(self):
        """https://ai.baidu.com/ai-doc/REFERENCE/Ck3dwjhhu

        Returns:
            _type_: _description_
        """
        ok = False
        access_token = ""

        sg = Settings.get()

        expires_in_date = sg.ocr_baidu_token_expires_date

        if expires_in_date - time.time() > 0:
            access_token = sg.ocr_baidu_token
            if len(access_token) != 0:
                return True, access_token

        [api_key, secret_key] = self.get_ocr_api_key_s().split("|")
        api_key = api_key.strip()
        secret_key = secret_key.strip()
        # API Key | Secret Key
        if api_key == "API Key" or secret_key == "Secret Key":
            return False, _("please input API Key in preference") + ": OCR"

        ok, access_token, expires_in_date = self._get_token_by_url(
            api_key, secret_key)

        if ok:
            sg.ocr_baidu_token = access_token
            sg.ocr_baidu_token_expires_date = expires_in_date

        return ok, access_token
