'ocr'
from lfy.api.server import Server
from lfy.api.utils.debug import get_logger


class EasyOcrServer(Server):
    """EasyOcr文字识别
    """

    def __init__(self):

        # Development documentation
        # https://fanyi-api.baidu.com/doc/21
        lang_key_ns = {
            "auto": 0,
            "zh": 1,
            "wyw": 2,
            "en": 3,
            "jp": 4,
            "kor": 5,
            "de": 6,
            "fra": 7,
            "it": 8
        }
        super().__init__("easyocr", "easyocr", lang_key_ns)
        self.can_ocr = True

    def ocr_image(self, img_path: str, lang_keys=None):
        try:
            import easyocr
            if lang_keys is None:
                lang_keys = ['ch_sim', 'en']
            reader = easyocr.Reader(lang_keys)
            list_ = reader.readtext(img_path, detail=0)
            s = ""
            for s_ in list_:
                s += s_ + " "
            return True, s.strip()
        except ModuleNotFoundError as e:
            print(e)
            get_logger().error(e)
            return False, "请安装 easyocr\n" + str(e)
