'ocr'
from gettext import gettext as _

from lfy.api.server.ocr import ServerOCR
from lfy.utils import gen_img
from lfy.utils.debug import get_logger


def _fun_check(so: ServerOCR, p):
    try:
        import easyocr

        # 放在 import 后面，因为未安装 pytesseract 会引发异常
        path = gen_img(p)
        if path is None:
            return True, _("The Python library `Pillow` is not installed, you cannot test whether the setting is successful now, if the OCR reports an error in the future, please change this content")
        return so.ocr_image(path)

    except ModuleNotFoundError as e:
        print(e)
        get_logger().error(e)
        s = _("please install python whl")
        s += str(e).replace("No module named", "")
        return False, s


class EasyOcrServer(ServerOCR):
    """EasyOcr文字识别
    """

    def __init__(self):
        # https://www.jaided.ai/easyocr/
        lang_key_ns = {
            "ch_sim": 1,
            "ch_tra": 2,
            "en": 3,
            "ja": 4,
            "ko": 5,
            "de": 6,
            "fr": 7,
            "it": 8,
            "es": 9,
        }
        super().__init__("easyocr", "easyocr")
        self.set_data(lang_key_ns, "ch_sim | en | it | fr")

    def ocr_image(self, img_path):
        try:
            import easyocr

            if not self.get_conf():
                return False, _("please input `{sk}` for `{server}` in preference")\
                    .format(sk=self.sk_placeholder_text, server=self.name)
            reader = easyocr.Reader(self.get_conf().split("|"))
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

    def check_conf(self, conf_str, fun_check=None, fun_args=None):
        return super().check_conf(conf_str, _fun_check)
