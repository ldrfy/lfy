"""谷歌翻译接口
"""
import random
import re
from gettext import gettext as _

import requests

from lfy.api.base import TIME_OUT, Server


class BingServer(Server):
    """bing翻译，无需apikey

    Args:
        Server (_type_): _description_
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
        super().__init__("bing",  _("bing"), lang_key_ns)

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

    def translate_text(self, text, lang_to="zh-cn", lang_from="auto"):
        """翻译

        Args:
            text (str): 待翻译字符
            to_lang_code (str, optional): 翻译成什么语言. Defaults to "zh-cn".
            from_lang (str, optional): 文本是什么语言. Defaults to "auto".

        Returns:
            str: _description_
        """
        hs = self._get_session().headers
        url = f'https://www.bing.com/ttranslatev3?isVertical=1&&IG={
            hs["IG"]}&IID=translator.{random.randint(5019, 5026)}.{random.randint(1, 3)}'
        data = {'': '', 'text': text, 'to': lang_to,
                'token': hs['token'], 'key': hs['key'], "fromLang": lang_from}
        if "auto" == lang_from:
            data['fromLang'] = "auto-detect"
            data['tryFetchingGenderDebiasedTranslations'] = True

        response = self._get_session().post(url, data=data, timeout=TIME_OUT).json()
        if isinstance(response, dict):
            if 'ShowCaptcha' in response.keys():
                self.session = None
                return self.translate_text(text, lang_to, lang_from)

            if 'statusCode' in response.keys():
                if response['statusCode'] == 400:
                    response['errorMessage'] = f'1000 characters limit! You send {
                        len(text)} characters.'
        else:
            if "auto" != lang_from:
                return response[0]

            return response[0]["translations"][0]["text"]

        return response
