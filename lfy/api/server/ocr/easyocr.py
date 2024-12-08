'easyocr'
from gettext import gettext as _

from lfy.api.server.ocr import ServerOCR
from lfy.utils import gen_img


def _fun_check(so: ServerOCR, p):
    return so.main(gen_img(p))


def _fun_ocr(so: ServerOCR, img_path, ocr_p=""):

    import easyocr  # pylint: disable=C0415

    if not ocr_p:
        ocr_p = so.get_conf()

    reader = easyocr.Reader(ocr_p.split("|"))
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

    def main(self, *args, **kwargs):
        return super().main(*args, fun_main=_fun_ocr, py_libs=["easyocr"])

    def check_conf(self, conf_str, fun_check=_fun_check, py_libs=None):
        return super().check_conf(conf_str, fun_check, ["easyocr", "PIL"])
