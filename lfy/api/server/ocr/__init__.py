'OCR'
import os
from gettext import gettext as _

from lfy.api.server import Server


class ServerOCR(Server):
    """翻译基础类
    """

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

    def main(self, *args, **kwargs):
        if not os.path.exists(args[0]):
            return False, "file not exists"
        if len(args) != 1 and len(args) != 2:
            raise ValueError("args: img_path, (conf_str)")
        return super().main(*args, **kwargs)
