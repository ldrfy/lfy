'ocr本地'

from lfy.api.server import Server
from lfy.api.utils.debug import get_logger
from lfy.settings import Settings


class PytesseractServer(Server):
    """Pytesseract文字识别
    """

    def __init__(self):

        # 获取系统默认语言，英语添加

        super().__init__("pytesseract", "pytesseract", {})
        self.can_ocr = True

    def ocr_image(self, img_path: str):
        try:
            import pytesseract
            s = self.get_api_key_s_ocr()
            return True, pytesseract.image_to_string(img_path, lang=s)
        except ModuleNotFoundError as e:
            print(e)
            get_logger().error(e)
            return False, "请安装 pytesseract\n" + str(e)

    def get_api_key_s_ocr(self):
        """图片识别的字符串apikey

        Returns:
            _type_: _description_
        """
        return Settings.get().server_sk_pytesseract_ocr

    def check_ocr(self, api_key_ocr_s):
        Settings.get().server_sk_pytesseract_ocr = api_key_ocr_s
        return True, "success"
