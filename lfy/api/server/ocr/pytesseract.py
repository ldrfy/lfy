'ocr本地'

from gettext import gettext as _

from lfy.api.server import Server
from lfy.api.server.ocr import gen_img
from lfy.utils.debug import get_logger
from lfy.utils.settings import Settings


class PytesseractServer(Server):
    """Pytesseract文字识别
    """

    def __init__(self):

        # 获取系统默认语言，英语添加
        lang_key_ns = {
            "chi_sim": 1,
            "eng": 3,
            "fra": 7,
            "ita": 8
        }
        super().__init__("pytesseract", "pytesseract", lang_key_ns)
        self.can_ocr = True

    def ocr_image(self, img_path: str, lang_str=None):
        try:
            import pytesseract
            if lang_str is None:
                lang_str = self.get_api_key_s_ocr()
            lang = "+".join(lang_str.split("|"))
            print(lang)
            return True, pytesseract.image_to_string(img_path, lang=lang)
        except ModuleNotFoundError as e:
            print(e)
            get_logger().error(e)
            s = _("please install python whl")
            s += str(e).replace("No module named", "")
            return False, s
        except Exception as e:  # pylint: disable=W0718
            print(e)
            get_logger().error(e)
            return False, str(e)

    def get_api_key_s_ocr(self):
        """图片识别的字符串apikey

        Returns:
            _type_: _description_
        """
        return Settings().g("server-sk-pytesseract-ocr")

    def check_ocr(self, api_key_ocr_s):
        """ocr环境

        Args:
            api_key_ocr_s (str): _description_

        Returns:
            _type_: _description_
        """
        path = gen_img("success")
        lang_str = "+".join(api_key_ocr_s.split("|"))
        try:
            import pytesseract
            langs = pytesseract.get_languages()
            langs_ = []
            for lang in lang_str.split("+"):
                if lang not in langs:
                    langs_.append(lang)
            if len(langs_) > 0:
                return False, _("Tesseract OCR database {} is not installed").format("-".join(langs_))
        except ModuleNotFoundError as e:
            print(e)
            get_logger().error(e)
            s = _("please install python whl")
            s += str(e).replace("No module named", "")
            return False, s

        ok, text = self.ocr_image(path, api_key_ocr_s)
        if not ok:
            return ok, text

        Settings().s("server-sk-pytesseract-ocr", api_key_ocr_s)
        return ok, text
