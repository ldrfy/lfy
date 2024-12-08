'OCR'
import traceback
from gettext import gettext as _

from lfy.api.server import Server
from lfy.utils import check_libs
from lfy.utils.debug import get_logger


class ServerOCR(Server):
    """翻译基础类
    """

    def ocr_image(self, img_path: str, fun_ocr=None, py_libs=None):
        """图片识别

        Args:
            img_path (str): _description_

        Returns:
            str: _description_
        """
        s = check_libs(py_libs)
        if s:
            return False, s

        if not self.get_conf():
            return False, _("please input `{sk}` for `{server}` in preference")\
                .format(sk=self.sk_placeholder_text, server=self.name)

        return super().main(fun_ocr, img_path)

    def get_doc_url(self, d="o"):
        """文档连接

        Returns:
            _type_: _description_
        """
        return super().get_doc_url(d)

    def get_conf(self, add="ocr"):
        return super().get_conf(add)

    def get_conf_key(self, add="ocr"):
        return super().get_conf_key(add)
