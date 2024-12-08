'ocr本地'

from gettext import gettext as _

from lfy.api.server.ocr import ServerOCR
from lfy.utils import gen_img


def _fun_check(so: ServerOCR, p):
    return so.ocr_image(gen_img(p))



def _fun_ocr(so: ServerOCR, img_path):

    import pytesseract  # pylint: disable=C0415

    if not so.get_conf():
        return False, _("please input `{sk}` for `{server}` in preference")\
            .format(sk=so.sk_placeholder_text, server=so.name)
    lang = "+".join(so.get_conf().split("|"))
    return True, pytesseract.image_to_string(img_path, lang=lang)


class PytesseractServer(ServerOCR):
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
        super().__init__("pytesseract", "pytesseract")
        self.set_data(lang_key_ns, "eng | chi_sim | ita | fra")

    def ocr_image(self, img_path, fun_ocr=_fun_ocr, py_libs=None):
        return super().ocr_image(img_path, fun_ocr, ["pytesseract"])

    def check_conf(self, conf_str, fun_check=_fun_check, py_libs=None):
        return super().check_conf(conf_str, fun_check, ["pytesseract", "pillow"])
