
from lfy.api.server import Server


def lib_ok():
    """_summary_

    Returns:
        _type_: _description_
    """
    try:
        import pytesseract
        return True
    except ModuleNotFoundError as e:
        print(e)
        return False


def main(img_path):

    if lib_ok():
        import pytesseract
        return True, pytesseract.image_to_string(img_path, lang='chi_sim+eng')
    return False, None


class PytesseractServer(Server):
    """Pytesseract文字识别
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
            import pytesseract
            s = "en"
            if lang_keys is None:
                s = '+'.join(lang_keys)
            return True, pytesseract.image_to_string(img_path, lang=s)
        except ModuleNotFoundError as e:
            print(e)
            return False, "请安装 pytesseract\n" + str(e)
