'翻译'
from gettext import gettext as _

from lfy.api.server import Server

NO_TRANSLATED_TXTS = [
    "\"server-sk-",
]


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

        ss_ntt = []
        for ntt in NO_TRANSLATED_TXTS:
            if ntt in args[0]:
                ss_ntt.append(ntt)
        if ss_ntt:
            return False, _("This time the content contains "
                            "private information and is not translated")
        if len(args) != 2:
            raise ValueError("args: text, lang_to")
        return super().main(*args, **kwargs)
