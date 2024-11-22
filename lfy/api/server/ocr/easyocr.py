'ocr'
from gettext import gettext as _

from lfy.api.server import Server
from lfy.api.server.ocr import gen_img
from lfy.utils.debug import get_logger
from lfy.utils.settings import Settings


class EasyOcrServer(Server):
    """EasyOcr文字识别
    """

    def __init__(self):
        super().__init__("easyocr", "easyocr", {})
        self.can_ocr = True

    def ocr_image(self, img_path: str, lang_str=None):
        try:
            import easyocr
            if lang_str is None:
                lang_str = self.get_api_key_s_ocr()
            lang_keys = lang_str.split("|")
            reader = easyocr.Reader(lang_keys)
            s = " ".join(reader.readtext(img_path, detail=0))
            return True, s.strip()
        except ModuleNotFoundError as e:
            print(e)
            get_logger().error(e)
            s = _("please install python whl")
            s += str(e).replace("No module named", "")
            return False, s

        except Exception as e:  # pylint: disable=W0718
            get_logger().error(e)
            return False, str(e)

    def get_api_key_s_ocr(self):
        """图片识别的字符串apikey

        Returns:
            _type_: _description_
        """
        return Settings().g("server-sk-easyocr-ocr")

    def check_ocr(self, api_key_ocr_s):
        path = gen_img("success")
        ok, text = self.ocr_image(path)
        if ok:
            Settings().s("server-sk-easyocr-ocr", api_key_ocr_s)
        return ok, text
