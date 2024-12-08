"""百度翻译接口
"""
import hashlib
import random
from gettext import gettext as _
from urllib.parse import quote

from lfy.api.server import TIME_OUT
from lfy.api.server.tra import ServerTra
from lfy.utils import s2ks


def _translate(p: ServerTra, s, lang_to="auto"):
    """翻译

    Args:
        s (str): 待翻译字符串
        api_key_s (str): 输入的原始字符串
        lang_to (str, optional): 字符串翻译为xx语言. Defaults to "auto".

    Returns:
        _type_: _description_
    """

    app_id, secret_key = s2ks(p.get_conf())

    url = "https://api.fanyi.baidu.com/api/trans/vip/translate"
    url = f"{url}?from=auto&to={lang_to}&appid={app_id}&q={quote(s)}"

    salt = random.randint(32768, 65536)
    sign = app_id + s + str(salt) + secret_key
    sign = hashlib.md5(sign.encode()).hexdigest()
    url = f"{url}&salt={salt}&sign={sign}"

    result = p.session.get(url, timeout=TIME_OUT).json()

    if "error_code" not in result:
        s1 = ""
        for trans_result in result["trans_result"]:
            s1 += f'{trans_result["dst"]}\n'
        return True, s1.strip()

    return False, _("something error: {}")\
        .format(f'\n\n{result["error_code"]}: {result["error_msg"]}')


class BaiduServer(ServerTra):
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
        super().__init__("baidu", _("baidu"))
        self.set_data(lang_key_ns, "APP ID | secret key")

    def check_conf(self, conf_str, fun_check=_translate, py_libs=None):
        return super().check_conf(conf_str, fun_check)

    def main(self, *args, **kwargs):
        return super().main(*args, fun_main=_translate)
