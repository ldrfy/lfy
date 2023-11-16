import re
from gettext import gettext as _

from requests.exceptions import ConnectTimeout

from lfy.api.server import (TE_BAIDU, TE_GOOGLE, TE_YOUDAO, baidu, google,
                            youdao)


def translate_by_server(text, server_key, lang_to, lang_from="auto"):
    """翻译

    Args:
        text (_type_): _description_
        server (_type_): _description_
        lang_to (_type_): _description_
        lang_from (str, optional): _description_. Defaults to "auto".

    Returns:
        _type_: _description_
    """
    try:
        print(server_key)
        if len(text.strip()) == 0:
            return _("Copy automatic translation, it is recommended to pin this window to the top")

        if server_key == TE_YOUDAO.key:
            return youdao.translate_text(text, lang_to, lang_from)
        elif server_key == TE_GOOGLE.key:
            return google.translate_text(text, lang_to, lang_from)
        elif server_key == TE_BAIDU.key:
            return baidu.translate_text(text, lang_to, lang_from)
        else:
            return "暂不支持"

    except ConnectTimeout as e:
        s = _("The connection timed out. Maybe there is a network problem")
        return f"{s}: \n\n {e}"
    except Exception as e:
        s = _("something error, try other translate engine?")
        return f"{s}：\n\n {e}"

def process_text(text):
    """文本预处理

    Args:
        text (str): _description_

    Returns:
        str: _description_
    """
    # 删除空行
    s_from = re.sub(r'\n\s*\n', '\n', text)
    # 删除多余空格
    s_from = re.sub(r' +', ' ', s_from)
    # 删除所有换行，除了句号后面的换行
    s_from = re.sub(r"-[\n|\r]+", "", s_from)
    s_from = re.sub(r"(?<!\.|-|。)[\n|\r]+", " ", s_from)
    return s_from
