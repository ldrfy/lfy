'ocr'
from lfy.api.server import Server
from lfy.api.utils.debug import get_logger
from lfy.settings import Settings


class EasyOcrServer(Server):
    """EasyOcr文字识别
    """

    def __init__(self):
        super().__init__("easyocr", "easyocr", {})
        self.can_ocr = True

    def ocr_image(self, img_path: str):
        try:
            import easyocr
            lang_keys = self.get_api_key_s_ocr().split('+')
            reader = easyocr.Reader(lang_keys)
            s = " ".join(reader.readtext(img_path, detail=0))
            return True, s.strip()
        except ModuleNotFoundError as e:
            print(e)
            get_logger().error(e)
            return False, "请安装 easyocr\n" + str(e)

    def get_api_key_s_ocr(self):
        """图片识别的字符串apikey

        Returns:
            _type_: _description_
        """
        return Settings.get().server_sk_easyocr_ocr

    def check_ocr(self, api_key_ocr_s):
        Settings.get().server_sk_easyocr_ocr = api_key_ocr_s
        return True, "success"
