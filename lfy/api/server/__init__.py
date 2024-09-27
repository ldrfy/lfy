'翻译服务的基础类'
from gettext import gettext as _

import requests

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

    def __init__(self, key: str, name, lang_key_ns: dict, session: requests.Session = None):
        """初始化

        Args:
            key (str): _description_
            name (str, optional): 翻译服务名字，需要可以翻译_(). Defaults to "".
            lang_key_ns (dict): 支持哪些翻译语言
        """

        self.can_ocr = False
        self.can_translate = False

        self.key = key
        self.name = name
        self.langs: list[Lang] = []
        for k, v in lang_key_ns.items():
            self.langs.append(Lang(k, v))

        if session is None:
            session = requests.Session()
        self.session = session

    def get_doc_url(self):
        """文档连接

        Returns:
            _type_: _description_
        """
        return f"https://github.com/ldrfy/docs/blob/main/servers/{self.key}.md"

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

    def check_translate(self, api_key_s: str):
        """实现检查翻译的参数

        Args:
            api_key_s (str): _description_

        Returns:
            bool: _description_
        """
        print(api_key_s)
        return True, "success"

    def translate_text(self, text: str, lang_to: str, lang_from: str = "auto"):
        """实现文本翻译的逻辑

        Args:
            text (str): _description_
            lang_to (str): _description_
            lang_from (str): _description_

        Returns:
            str: _description_
        """
        print(f"lang_to={lang_to} text={text}")
        return True, "test"

    def get_api_key_s(self):
        """字符串apikey，翻译的

        Returns:
            _type_: _description_
        """
        return None

    def ocr_image(self, img_path: str, lang_str=None):
        """图片识别

        Args:
            img_path (str): _description_

        Returns:
            str: _description_
        """
        ok = True
        text = ""
        return ok, text

    def check_ocr(self, api_key_ocr_s):
        """_summary_

        Args:
            api_key_ocr_s (_type_): _description_

        Returns:
            _type_: _description_
        """
        return True, "success"

    def get_api_key_s_ocr(self):
        """图片识别的字符串apikey

        Returns:
            _type_: _description_
        """
        return None


TIME_OUT = 3
