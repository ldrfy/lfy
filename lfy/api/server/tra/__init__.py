'翻译'
import traceback
from gettext import gettext as _

from lfy.api.server import Server
from lfy.utils.debug import get_logger


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

        if self.sk_placeholder_text and not self.get_conf():
            return False, _("please input `{sk}` for `{server}` in preference")\
                .format(sk=self.sk_placeholder_text, server=self.name)

        try:
            return fun_tra(self, text, lang_to)
        except Exception as e:  # pylint: disable=W0718
            text = _("something error: {}")\
                .format(f"{self.name}\n\n{str(e)}\n\n{traceback.format_exc()}")
            get_logger().error(text)
            print(text)
        return False, text

    def get_doc_url(self, d="t"):
        """文档连接

        Returns:
            _type_: _description_
        """
        return super().get_doc_url(d)
