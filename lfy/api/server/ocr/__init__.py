'OCR'
from lfy.api.server import Server


class ServerOCR(Server):
    """翻译基础类
    """

    def ocr_image(self, img_path: str, conf_str=None):
        """图片识别

        Args:
            img_path (str): _description_

        Returns:
            str: _description_
        """
        ok = True
        text = f"{img_path}, {conf_str}"
        return ok, text

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
