"""谷歌翻译接口
"""
import base64
import random
from gettext import gettext as _

import requests

from lfy.api.server import TIME_OUT
from lfy.api.server.tra import ServerTra


def _get_session():
    """初始化请求
    """
    r1 = random.randint(10, 100)
    r2 = random.randint(111111111, 999999999)
    r3 = random.randint(5, 11)
    r4 = base64.b64encode(str(random.random())[2:].encode()).decode()

    session = requests.Session()
    session.headers = {
        'User-Agent': f'GoogleTranslate/6.{r1}.0.06.{r2} (Linux; U; Android {r3}; {r4})'
    }
    return session


def _translate(st: ServerTra, text: str, lang_to):
    url = 'https://translate.google.com/translate_a/t'
    params = {'tl': lang_to, 'sl': "auto", 'ie': 'UTF-8',
              'oe': 'UTF-8', 'client': 'at', 'dj': '1',
              'format': "html", 'v': "1.0"}

    response = st.session.post(url, params=params,
                               data={'q': text},
                               timeout=TIME_OUT)

    s = ""
    for res in response.json():
        s += res[0]

    return True, s


class GoogleServer(ServerTra):
    """google翻译
    """

    def __init__(self):
        # https://cloud.google.com/translate/docs/languages
        lang_key_ns = {
            "zh": 1,
            "en": 3,
            "ja": 4,
            "ko": 5,
            "de": 6,
            "fr": 7,
            "it": 8,
            "es": 9,
            "pt-pt": 10,
            "pt": 11,
        }
        super().__init__("google", _("google"))
        self.set_data(lang_key_ns, session=_get_session())

    def main(self, *args, **kwargs):
        return super().main(*args, fun_main=_translate)
