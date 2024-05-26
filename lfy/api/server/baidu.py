"""百度翻译接口
"""
import hashlib
import random
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
        _ok, text = self._translate(text, self.get_api_key_s(), lang_to, lang_from)
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
