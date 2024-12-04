'翻译'
from gettext import gettext as _

from lfy.api.server import Server
from lfy.utils import s2ks


class ServerTra(Server):
    """翻译基础类
    """

    def translate_text(self, text: str, lang_to: str, fun_tra=None):
        """实现文本翻译的逻辑

        Args:
            text (str): _description_
            lang_to (str): _description_
            lang_from (str): _description_

        Returns:
            str: _description_
        """
        if not self.get_conf():
            return False, _("please input `{sk}` for `{server}` in preference")\
                .format(sk=self.sk_placeholder_text, server=self.name)

        return fun_tra(self, text, lang_to)

    def get_doc_url(self, d="t"):
        """文档连接

        Returns:
            _type_: _description_
        """
        return super().get_doc_url(d)
