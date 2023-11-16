"""谷歌翻译

Returns:
    _type_: _description_
"""
import requests

from lfy.api.server import TIME_OUT


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
