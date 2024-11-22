"""谷歌翻译接口
"""
import base64
import random
from gettext import gettext as _

import requests
from requests import ConnectTimeout, RequestException

from lfy.api.server import TIME_OUT, Server
from lfy.utils.debug import get_logger


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
        super().__init__("google", _("google"), lang_key_ns, session=_get_session())
        self.can_translate = True

    def translate_text(self, text, lang_to="zh-cn", lang_from="auto", n=0):
        """翻译

        Args:
            text (str): 待翻译字符
            lang_to (str, optional): 翻译成什么语言. Defaults to "zh-cn".
            lang_from (str, optional): 文本是什么语言. Defaults to "auto".

        Returns:
            str: _description_
        """

        if n > 3:
            raise ValueError(_("something error, try other translate engine?"))

        text = text.replace("#", "")
        url = 'https://translate.google.com/translate_a/t'
        params = {'tl': lang_to, 'sl': lang_from, 'ie': 'UTF-8',
                  'oe': 'UTF-8', 'client': 'at', 'dj': '1',
                  'format': "html", 'v': "1.0"}

        try:
            response = self.session.post(url, params=params, data={'q': text}, timeout=TIME_OUT)
        except ConnectTimeout as e0:
            print("google0", n, type(e0), e0)
            get_logger().error(e0)
            return False, _("The connection timed out. Maybe there is a network problem")
        except RequestException as e:
            print("google", n, type(e), e)
            get_logger().error(e)
            return self.translate_text(text, lang_to, lang_from, n + 1)

        s = ""
        for res in response.json():
            s += res[0]

        return True, s
