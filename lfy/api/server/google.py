"""谷歌翻译接口
"""
from gettext import gettext as _

import requests

from lfy.api.base import TIME_OUT, Server

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

SERVER = Server("google", _("google"),
                lang_key_ns, False, "")


def translate_text(text, to_lang_code="zh-cn", from_lang="auto"):
    """翻译

    Args:
        text (str): 待翻译字符
        to_lang_code (str, optional): 翻译成什么语言. Defaults to "zh-cn".
        from_lang (str, optional): 文本是什么语言. Defaults to "auto".

    Returns:
        str: _description_
    """
    text = text.replace("#", "")
    url = 'https://translate.googleapis.com/translate_a/single?'
    param = f'client=gtx&dt=t&sl={from_lang}&tl={to_lang_code}&q={text}'
    response = requests.get(url + param, timeout=TIME_OUT)
    result = response.json()

    s = ""
    for ss in result[0]:
        s += ss[0]
    return s
