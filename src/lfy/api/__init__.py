from gettext import gettext as _

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
