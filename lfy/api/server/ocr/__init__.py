'OCR'
from gettext import gettext as _

from lfy.api.server import Server


class ServerOCR(Server):
    """翻译基础类
    """

    def ocr_image(self, img_path: str, fun_ocr=None):
        """图片识别

        Args:
            img_path (str): _description_

        Returns:
            str: _description_
        """
        if not self.get_conf():
            return False, _("please input `{sk}` for `{server}` in preference")\
                .format(sk=self.sk_placeholder_text, server=self.name)

        return fun_ocr(self, img_path)

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
