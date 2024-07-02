"""谷歌翻译接口
"""
import base64
import random
import time
from gettext import gettext as _

import requests

from lfy.api.server import Server, TIME_OUT


class GoogleServer(Server):
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
        }
        self.session = None
        super().__init__("google", _("google"), lang_key_ns)

    def get_session(self):
        """初始化请求
        """
        if self.session is None:
            r1 = random.randint(10, 100)
            r2 = random.randint(111111111, 999999999)
            r3 = random.randint(5, 11)
            r4 = base64.b64encode(str(random.random())[2:].encode()).decode()

            self.session = requests.Session()
            self.session.headers = {
                'User-Agent': f'GoogleTranslate/6.{r1}.0.06.{r2} (Linux; U; Android {r3}; {r4})'
            }
        return self.session

    def translate_text(self, text, lang_to="zh-cn", lang_from="auto"):
        """翻译

        Args:
            text (str): 待翻译字符
            lang_to (str, optional): 翻译成什么语言. Defaults to "zh-cn".
            lang_from (str, optional): 文本是什么语言. Defaults to "auto".

        Returns:
            str: _description_
        """
        text = text.replace("#", "")
        url = 'https://translate.google.com/translate_a/t'
        params = {'tl': lang_to, 'sl': lang_from, 'ie': 'UTF-8',
                  'oe': 'UTF-8', 'client': 'at', 'dj': '1',
                  'format': "html", 'v': "1.0"}

        for i in range(1, 4):
            response = self.get_session().post(url, params=params,
                                               data={'q': text}, timeout=TIME_OUT)
            if response.status_code == 429:
                time.sleep(5 * i)
                continue
            break

        result = response.json()

        s = ""
        for res in result:
            s += res[0]

        return True, s
