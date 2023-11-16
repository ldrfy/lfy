import json

import requests

from lfy.api.server import TIME_OUT


def translate_text(text, to_lang_code="zh-cn", from_lang="auto"):
    text = text.replace("#", "")
    print("谷歌" + to_lang_code)
    url = 'https://translate.googleapis.com/translate_a/single?'
    param = f'client=gtx&dt=t&sl={from_lang}&tl={to_lang_code}&q={text}'
    response = requests.get(url + param, timeout=TIME_OUT)
    result = json.loads(response.text)

    s = ""
    for ss in result[0]:
        s += ss[0]
    return s
