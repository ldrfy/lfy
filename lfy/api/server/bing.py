"""谷歌翻译接口
"""
import random
import re
from gettext import gettext as _

import requests

from lfy.api.server import Server, TIME_OUT


class BingServer(Server):
    """bing翻译，无需apikey
    """

    def __init__(self):

        # https://learn.microsoft.com/zh-cn/azure/ai-services/translator/language-support
        lang_key_ns = {
            "zh-Hans": 1,
            "en": 3,
            "ja": 4,
            "ko": 5,
            "de": 6,
            "fr": 7,
            "it": 8,
        }
        self.session = None
        super().__init__("bing", _("bing"), lang_key_ns)

    def _get_session(self):
        if self.session is not None:
            return self.session

        session = requests.Session()
        url = 'https://www.bing.com/translator'
        headers = {
            'User-Agent': '',
            'Referer': url
        }
        session.headers.update(headers)
        response = session.get(url, timeout=TIME_OUT)
        content = response.text

        params_pattern = re.compile(
            r'params_AbusePreventionHelper\s*=\s*(\[.*?\]);', re.DOTALL)
        match = params_pattern.search(content)
        if match:
            params = match.group(1)
            key, token, _time = [p.strip('"').replace(
                '[', '').replace(']', '') for p in params.split(',')]
            session.headers.update({'key': key, 'token': token})
        match = re.search(r'IG:"(\w+)"', content)

        if match:
            ig_value = match.group(1)
            session.headers.update({'IG': ig_value})

        self.session = session
        return session

    def error_check(self, response, text, lang_to, lang_from, n):
        """错误处理

        Args:
            response (_type_): _description_
            text (_type_): _description_
            lang_to (_type_): _description_
            lang_from (_type_): _description_
            n (_type_): _description_

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
        """
        if n > 5:
            raise ValueError(_("something error, try other translate engine?"))

        if 'ShowCaptcha' in response.keys():
            self.session = None
            return self.translate_text(text, lang_to, lang_from, n + 1)

        if 'statusCode' in response.keys() and response['statusCode'] == 400:
            response['errorMessage'] = _(
                '1000 characters limit! You send {len_text} characters.').format(len_text=len(text))

    def translate_text(self, text, lang_to="zh-cn", lang_from="auto", n=0):
        """翻译

        Args:
            text (str): 待翻译字符
            lang_to (str, optional): 翻译成什么语言. Defaults to "zh-cn".
            lang_from (str, optional): 文本是什么语言. Defaults to "auto".

        Returns:
            str: _description_
        """
        hs = self._get_session().headers
        iid = f"translator.{random.randint(5019, 5026)}.{random.randint(1, 3)}"
        url = "https://www.bing.com/ttranslatev3"
        url = f'{url}?isVertical=1&&IG={hs["IG"]}&IID={iid}'
        data = {'': '', 'text': text, 'to': lang_to,
                'token': hs['token'], 'key': hs['key'], "fromLang": lang_from}
        if "auto" == lang_from:
            data['fromLang'] = "auto-detect"
            data['tryFetchingGenderDebiasedTranslations'] = True

        response = self._get_session().post(url, data=data, timeout=TIME_OUT).json()
        if isinstance(response, dict):
            self.error_check(response, text, lang_to, lang_from, n)
            if 'statusCode' in response.keys():
                return False, response["errorMessage"]
        else:
            if "auto" != lang_from:
                return True, response[0]

            return True, response[0]["translations"][0]["text"]

        return False, response
