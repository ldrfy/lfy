'easyocr'
from gettext import gettext as _

from lfy.api.server.ocr import ServerOCR
from lfy.utils import gen_img


def _fun_check(so: ServerOCR, p):
    return so.ocr_image(gen_img(p))


def _fun_ocr(so: ServerOCR, img_path):

    import easyocr  # pylint: disable=C0415

    if not so.get_conf():
        return False, _("please input `{sk}` for `{server}` in preference")\
            .format(sk=so.sk_placeholder_text, server=so.name)
    reader = easyocr.Reader(so.get_conf().split("|"))
    s = " ".join(reader.readtext(img_path, detail=0))
    return True, s.strip()


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

    def ocr_image(self, img_path, fun_ocr=_fun_ocr, py_libs=None):
        return super().ocr_image(img_path, fun_ocr, ["easyocr"])

    def check_conf(self, conf_str, fun_check=_fun_check, py_libs=None):
        return super().check_conf(conf_str, fun_check, ["easyocr", "pillow"])
