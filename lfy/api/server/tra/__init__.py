'翻译'
from gettext import gettext as _
import html
from lfy.api.server import Server

NO_TRANSLATED_TXTS = [
    "\"server-sk-",
]


def normalize_translation_text(s: str) -> str:
    s = s.strip()
    # 1. 确保是字符串
    if not isinstance(s, str):
        s = str(s)

    # 2. 把 HTML 实体解码一次（避免重复解码）
    s = html.unescape(s)

    return s


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
        ok, text = super().main(*args, **kwargs)
        text = normalize_translation_text(text.strip())

        return ok, text
