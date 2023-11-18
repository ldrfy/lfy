"""_summary_

"""

from gettext import gettext as _

TIME_OUT = 3

class TranslateEngine:
    """翻译信息
    """

    def __init__(self, key: str, name: str, langs: list, lang_ids: list):
        self.key = key
        self.name = _(name)

        self.langs = langs
        self.lang_names = []
        for i in lang_ids:
            self.lang_names.append(lgs[i])


lgs = [
    # 0
    _("Automatic"),
    # 1
    _("Chinese"),
    # 2
    _("Classical Chinese"),
    # 3
    _("English"),
    # 4
    _("Japanese"),
    # 5
    _("Korean"),
    # 6
    _("German"),
    # 7
    _("French")
]

TE_BAIDU = TranslateEngine("baidu", _("baidu"), [
                    "auto", "zh", "wyw", "en", "jp", "kor", "de", "fra"], range(8))

TE_TENCENT = TranslateEngine("tencent", _("tencent"), [
                    "zh", "en", "jp", "kr", "de", "fr"], [1, 3, 4, 5, 6, 7])

TE_GOOGLE = TranslateEngine("google", _("google"), [
                    "zh", "en", "ja", "ko", "de", "fr"], [1, 3, 4, 5, 6, 7])

TE_YOUDAO = TranslateEngine("youdao", _("youdao"), ["auto"], [0])


tes = [
    TE_YOUDAO,
    TE_GOOGLE,
    TE_BAIDU,
    TE_TENCENT,
]


def get_server_names():
    """_summary_

    Returns:
        _type_: _description_
    """
    sns = []
    for te in tes:
        sns.append(te.name)
    return sns


def get_server_key(i: int):
    """_summary_

    Returns:
        _type_: _description_
    """
    if i >= len(tes):
        i = 0
    return tes[i].key


def get_server_name(i: int):
    """_summary_

    Returns:
        _type_: _description_
    """
    if i >= len(tes):
        i = 0
    return tes[i].name

def get_lang(i: int, j: int):
    """_summary_

    Returns:
        _type_: _description_
    """
    if i >= len(tes):
        i = 0
    return tes[i].langs[j]


def get_lang_names(i=0):
    """_summary_

    Returns:
        _type_: _description_
    """
    if i >= len(tes):
        i = 0
    return tes[i].lang_names


def server_key2i(key: str):
    """_summary_

    Returns:
        _type_: _description_
    """
    for i, te in enumerate(tes):
        if te.key == key:
            return i
    return 0
