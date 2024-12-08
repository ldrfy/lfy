"""谷歌翻译接口
"""
import random
import re
from gettext import gettext as _
from urllib.parse import urlparse

import requests
from requests import RequestException

from lfy.api.server import TIME_OUT
from lfy.api.server.tra import ServerTra
from lfy.utils.debug import get_logger


def _init_session():
    session = requests.Session()
    url = 'https://www.bing.com/translator'
    headers = {
        'User-Agent': '',
        'Referer': url
    }
    session.headers.update(headers)
    response = session.get(url, timeout=TIME_OUT)
    session.headers.update({'my_host': urlparse(response.url).hostname})

    content = response.text

    params_pattern = re.compile(
        r'params_AbusePreventionHelper\s*=\s*(\[.*?]);', re.DOTALL)
    match = params_pattern.search(content)
    if match:
        params = match.group(1)
        key, token, _time = [p.strip('"').replace('[', '')
                             .replace(']', '') for p in params.split(',')]
        session.headers.update({'key': key, 'token': token})
    match = re.search(r'IG:"(\w+)"', content)

    if match:
        ig_value = match.group(1)
        session.headers.update({'IG': ig_value})

    return session


def g_iid():
    """_summary_

    Returns:
        _type_: _description_
    """
    return f"translator.{random.randint(5019, 5026)}.{random.randint(1, 3)}"


def g_url(host, hs):
    """_summary_

    Args:
        host (_type_): _description_
        hs (_type_): _description_

    Returns:
        _type_: _description_
    """
    return f'https://{host}/ttranslatev3?isVertical=1&&IG={hs["IG"]}&IID={hs["my_iid"]}'


def _get_data(st: ServerTra, text, lang_to, n=0):

    if n > 5:
        return False, _("something error, try other translate engine?")

    hs = st.session.headers
    if "IG" not in hs:
        try:
            st.session = _init_session()
            hs = st.session.headers
            print(hs["my_host"])
        except RequestException as e:
            get_logger().error(e)
            return _translate(st, text, lang_to, n=n + 1)

    # 自动重定向的新url，注意辨别
    host = hs["my_host"]
    if "my_iid" not in hs:
        st.session.headers.update({'my_iid': g_iid()})
        hs = st.session.headers

    data = {'': '', 'text': text, "fromLang": "auto-detect",
            'to': lang_to, 'token': hs['token'], 'key': hs['key'],
            'tryFetchingGenderDebiasedTranslations': True}
    return host, data, hs


def _translate(st: ServerTra, text, lang_to, n=0):

    if st.session is None:
        st.session = _init_session()

    host, data, hs = _get_data(st, text, lang_to, n)

    try:
        url = g_url(host, hs)
        response = st.session.post(url, data=data, timeout=TIME_OUT)
    except RequestException as e:
        get_logger().error(e)
        return _translate(st, text, lang_to, n=n + 1)

    # 没有代理时，中国区出现这个
    if len(response.text.strip()) == 0:
        return _translate(st, text, lang_to, n=n + 1)

    res = response.json()

    if isinstance(res, list):
        return True, res[0]["translations"][0]["text"]

    if isinstance(res, dict):
        if 'ShowCaptcha' in res.keys():
            st.session = _init_session()
            return _translate(st, text, lang_to, n=n + 1)

        if 'statusCode' in res.keys():
            if res['statusCode'] == 400:
                res['errorMessage'] \
                    = _('1000 characters limit! You send {len_text} characters.') \
                    .format(len_text=len(text))
            return False, res["errorMessage"]

    return False, str(res)


class BingServer(ServerTra):
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
        super().__init__("bing", _("bing"))
        self.set_data(lang_key_ns)

    def main(self, *args, **kwargs):
        return super().main(*args, fun_main=_translate)
