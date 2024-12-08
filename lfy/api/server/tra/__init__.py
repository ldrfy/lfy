'翻译'
from gettext import gettext as _

from lfy.api.server import Server


class ServerTra(Server):
    """翻译基础类
    """

    def get_doc_url(self, d="t"):
        """文档连接

        Returns:
            _type_: _description_
        """
        return super().get_doc_url(d)

    def main(self, *args, **kwargs):
        if len(args) != 2:
            raise ValueError("args: text, lang_to")
        return super().main(*args, **kwargs)
