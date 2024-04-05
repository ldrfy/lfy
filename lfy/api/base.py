
from gettext import gettext as _

TIME_OUT = 3


# select language name
LANGUAGE_NAMES = [
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
    _("French"),
    # 8
    _("Italian"),
]


class Lang():
    """语言
    """

    def __init__(self, key: str, n: int):
        """初始化

        Args:
            key (str): 其实是翻译称某种语言时 需要传递到这个server的关键字
            n (int): 这个关键字在内置 LANGUAGE_NAMES 名单中是第几个
            name (str): LANGUAGE_NAMES 中的名字，方便翻译
        """
        self.key = key
        self.n = n
        self.name = LANGUAGE_NAMES[n]


class Server:
    """翻译信息
    """

    def __init__(self, key: str, name: str, lang_key_ns: dict, is_api_key=False, doc_url=""):
        self.key = key
        self.doc_url = doc_url
        self.is_api_key = is_api_key
        self.name = _(name)

        self.langs: list[Lang] = []

        for k, v in lang_key_ns.items():
            self.langs.append(Lang(k, v))

    def get_lang_names(self):
        """获取某个翻译服务的所有翻译语言的名字

        Returns:
            list: 如 ["auto"]
        """
        return [lang.name for lang in self.langs]

    def get_lang(self, j=0):
        """获取某个翻译服务的某个语言 Lang

        Args:
            j (int, optional): _description_. Defaults to 0.

        Returns:
            _type_: _description_
        """
        if j >= len(self.langs):
            return self.langs[0]
        return self.langs[j]
