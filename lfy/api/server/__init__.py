'翻译服务的基础类'
import traceback
from gettext import gettext as _

import requests

from lfy.utils import check_libs, clear_key
from lfy.utils.debug import get_logger
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
    # 9
    _("Spanish"),
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
        """

        self.session = None
        self.sk_placeholder_text = None
        self._conf_str = None
        self.langs: list[Lang] = []

        self.key = key
        self.name = name

    def main(self, *args, **kwargs):
        """_summary_

        Returns:
            _type_: _description_
        """
        try:

            if self.sk_placeholder_text and not self.get_conf():
                return False, _("please input `{sk}` for `{server}` in preference")\
                    .format(sk=self.sk_placeholder_text, server=self.name)
            if "py_libs" in kwargs:
                s = check_libs(kwargs.get("py_libs"))
                if s:
                    return False, s

            return kwargs["fun_main"](self, *args)
        except Exception as e:  # pylint: disable=W0718
            text = _("something error: {}")\
                .format(f"{self.name}\n\n{str(e)}\n\n{traceback.format_exc()}")
            get_logger().error(text)
        return False, text

    def set_data(self, lang_key_ns: dict,
                 sk_placeholder_text: str = None,
                 session: requests.Session = None):
        """_summary_

        Args:
            lang_key_ns (dict): _description_
            sk_placeholder_text (str, optional): 密钥提示语言，有密钥的tra或需要参数的ocr的必须设置. Defaults to None.
            session (requests.Session, optional): _description_. Defaults to None.
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

    def check_conf(self, conf_str: str, fun_check, py_libs=None):
        """保存前核对配置

        Args:
            conf_str (str): _description_

        Returns:
            _type_: _description_
        """
        s = check_libs(py_libs)
        if s:
            return False, s

        self._conf_str = clear_key(conf_str.strip())

        if not self.sk_placeholder_text:
            self._conf_str = None
            return False, _("Developers, please set sk_placeholder_text")

        sk_no = not self.get_conf() \
            or (self.sk_placeholder_text.count("|") == 1
                and self.get_conf().count("|") != 1) \
            or self.get_conf()[0] == "|" \
            or self.get_conf()[-1] == "|"

        if sk_no:
            self._conf_str = None
            return False, _("please input `{sk}` for `{server}` in preference")\
                .format(sk=self.sk_placeholder_text, server=self.name)

        try:
            ok, text = fun_check(self, "success")
            if ok:
                self.set_conf()
            else:
                self._conf_str = None

            return ok, text
        except Exception as e:  # pylint: disable=W0718
            get_logger().error(_("something error: {}")
                               .format(f"{self.name}\n\n{str(e)}\n\n{traceback.format_exc()}"))
        return False, text

    def set_conf(self):
        """设置配置

        Args:
            conf_str (_type_): _description_

        Returns:
            _type_: _description_
        """
        Settings().s(self.get_conf_key(), self._conf_str)

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
        if self._conf_str is None:
            self._conf_str = Settings().g(self.get_conf_key(add))
        return self._conf_str
