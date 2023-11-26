"""有道翻译

Returns:
    _type_: _description_
"""
import urllib
from gettext import gettext as _

import requests

from lfy.api.base import TIME_OUT, Server

lang_key_ns = {
    "auto": 0
}

SERVER = Server("youdao", _("youdao"), lang_key_ns, False, "")


def translate_text(text, lang_to="", lang_from="auto"):
    """翻译接口

    Args:
        text (_type_): _description_
        lang_to (str, optional): _description_. Defaults to "".
        lang_from (str, optional): _description_. Defaults to "auto".

    Returns:
        _type_: _description_
    """

    url = "http://fanyi.youdao.com/translate?&doctype=json&type=%s&i=%s"
    url = url % (lang_from + "2" + lang_to, urllib.parse.quote(text))
    error_msg = _("something error, try other translate engine?")

    request = requests.get(url, timeout=TIME_OUT)
    if request.status_code == 200:
        result = request.json()
        if "errorCode" in result and result["errorCode"] != 0:
            return f"{error_msg}\n\n{result}"
        else:
            s1 = ""
            for line in result["translateResult"]:
                for sentence in line:
                    s1 += sentence["tgt"]
                s1 += '\n'
            return s1
    else:
        return f"{error_msg}\n\n{request.content}"

if __name__ == "__main__":
    s = translate_text("Flow")
    print(s)
