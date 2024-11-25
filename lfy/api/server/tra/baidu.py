"""百度翻译接口
"""
import hashlib
import random
from gettext import gettext as _
from urllib.parse import quote

from lfy.api.server import TIME_OUT, Server
from lfy.utils import s2ks
from lfy.utils.settings import Settings


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

    if "error_code" not in result:
        s1 = ""
        for trans_result in result["trans_result"]:
            s1 += f'{trans_result["dst"]}\n'
        return True, s1.strip()

    return False, _("something error: {}")\
        .format(f'\n\n{result["error_code"]}: {result["error_msg"]}')


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
        self.can_translate = True

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
            Settings().s("server-sk-baidu", api_key_s)
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
        return Settings().g("server-sk-baidu")
