'翻译服务的基础类'
from gettext import gettext as _

import requests

from lfy.utils.settings import Settings

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


class Lang:
    """语言
    """

    def __init__(self, key: str, n: int):
        """初始化

        Args:
            key (str): 其实是翻译称某种语言时 需要传递到这个server的关键字
            n (int): 这个关键字在内置 LANGUAGE_NAMES 名单中是第几个
        """
        self.key = key
        self.n = n

    def get_name(self):
        """_summary_

        Args:
            t (str): _description_
        """
        return LANGUAGE_NAMES[self.n]

    def test(self, t):
        """_summary_

        Args:
            t (_type_): _description_
        """
        print(t)


class Server:
    """翻译基础类
    """

    def __init__(self, key: str, name: str):
        """初始化

        Args:
            key (str): _description_
            name (str, optional): 翻译服务名字，需要可以翻译_(). Defaults to "".
            lang_key_ns (dict): 支持哪些翻译语言
        """

        self.session = None
        self.sk_placeholder_text = None
        self.langs: list[Lang] = []

        self.key = key
        self.name = name

    def set_data(self, lang_key_ns: dict,
                 sk_placeholder_text: str = None,
                 session: requests.Session = None):
        """_summary_

        Args:
            session (requests.Session): _description_
        """
        if session is None:
            session = requests.Session()
        self.session = session

        if sk_placeholder_text:
            self.sk_placeholder_text = sk_placeholder_text

        for k, v in lang_key_ns.items():
            self.langs.append(Lang(k, v))

    def get_doc_url(self, d=""):
        """文档连接

        Returns:
            _type_: _description_
        """
        return f"https://github.com/ldrfy/docs/blob/main/servers/{d}/{self.key}.md"

    def get_lang_names(self):
        """获取某个翻译服务的所有翻译语言的名字

        Returns:
            list: 如 ["auto"]
        """
        return [lang.get_name() for lang in self.langs]

    def get_lang(self, j=0):
        """获取某个翻译服务的某个语言 Lang

        Args:
            j (int, optional): _description_. Defaults to 0.

        Returns:
            Lang: _description_
        """
        if j >= len(self.langs):
            return self.langs[0]
        return self.langs[j]

    def check_conf(self, conf_str: str):
        """保存前核对配置

        Args:
            conf_str (str): _description_

        Returns:
            _type_: _description_
        """
        if not self.sk_placeholder_text:
            return False, _("Developers, please set sk_placeholder_text")
        if "|" in self.sk_placeholder_text and "|" not in conf_str:
            return False, _("please input {} like: {}")\
                .format(self.sk_placeholder_text, "121343 | fdsdsdg")
        return True, f"success: {conf_str}"

    def set_conf(self, conf_str):
        """设置配置

        Args:
            conf_str (_type_): _description_

        Returns:
            _type_: _description_
        """
        Settings().s(self.get_conf_key(), conf_str)

    def get_conf_key(self, add=""):
        """配置保存时的key

        Args:
            add (str, optional): _description_. Defaults to "".

        Returns:
            _type_: _description_
        """
        sk = f"server-sk-{self.key}"
        if add:
            sk = f"{sk}-{add}"
        return sk

    def get_conf(self, add=""):
        """图片识别的字符串apikey

        Returns:
            _type_: _description_
        """
        return Settings().g(self.get_conf_key(add))
