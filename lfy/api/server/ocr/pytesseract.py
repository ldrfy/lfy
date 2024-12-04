'ocr本地'

from gettext import gettext as _

from lfy.api.server.ocr import ServerOCR
from lfy.utils import gen_img
from lfy.utils.debug import get_logger


def _fun_check(so: ServerOCR, p):

    try:
        import pytesseract

        # 放在 import 后面，因为未安装 pytesseract 会引发异常
        path = gen_img(p)
        if path is None:
            return True, _("The Python library `Pillow` is not installed, you cannot test whether the setting is successful now, if the OCR reports an error in the future, please change this content")

        langs_no = []
        for lang in so.get_conf().split("|"):
            if lang not in pytesseract.get_languages():
                langs_no.append(lang)
        if langs_no:
            return False, _("Tesseract OCR database {} is not installed")\
                .format("-".join(langs_no))
    except ModuleNotFoundError as e:
        print(e)
        get_logger().error(e)
        s = _("please install python whl")
        s += str(e).replace("No module named", "")
        return False, s

    return so.ocr_image(path)


def _fun_ocr(so: ServerOCR, img_path):
    try:
        import pytesseract

        if not so.get_conf():
            return False, _("please input `{sk}` for `{server}` in preference")\
                .format(sk=so.sk_placeholder_text, server=so.name)
        lang = "+".join(so.get_conf().split("|"))
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

    def ocr_image(self, img_path, fun_ocr=_fun_ocr):
        return super().ocr_image(img_path, fun_ocr)

    def check_conf(self, conf_str, fun_check=_fun_check):
        return super().check_conf(conf_str, fun_check)
