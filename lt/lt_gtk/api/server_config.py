"""_summary_

"""

from gettext import gettext as _


class TranslateEngine:
    """翻译信息
    """

    def __init__(self, key: str, name: str, langs: list, lang_ids: list):
        self.key = _(key)
        self.name = name

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


tes = [
    TranslateEngine("baidu", _("baidu"), [
                    "auto", "zh", "wyw", "en", "jp", "kor", "de", "fra"], range(8)),
    TranslateEngine("tencent", _("tencent"), [
                    "zh", "en", "jp", "kr", "de", "fr"], [1, 3, 4, 5, 6, 7]),
    TranslateEngine("google", _("google"), [
                    "zh", "en", "ja", "ko", "de", "fr"], [1, 3, 4, 5, 6, 7]),
    TranslateEngine("youdao", _("youdao"), ["auto"], [0]),
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


def get_lang_names(i=0):
    """_summary_

    Returns:
        _type_: _description_
    """
    return tes[i].lang_names
