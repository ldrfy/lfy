'ocr本地'

from gettext import gettext as _

from lfy.api.server.ocr import ServerOCR
from lfy.utils import gen_img
from lfy.utils.debug import get_logger


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

    def ocr_image(self, img_path, conf_str=None):
        try:
            import pytesseract
            if conf_str is None:
                conf_str = self.get_conf()
                if not conf_str:
                    return False, _("please input `{sk}` for `{server}` in preference")\
                        .format(sk=self.sk_placeholder_text, server=self.name)
            lang = "+".join(conf_str.split("|"))
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

    def check_conf(self, conf_str):
        try:
            import pytesseract

            # 放在 import 后面，因为未安装 pytesseract 会引发异常
            path = gen_img("success")
            if path is None:
                return True, _("The Python library `Pillow` is not installed, you cannot test whether the setting is successful now, if the OCR reports an error in the future, please change this content")

            langs = pytesseract.get_languages()
            langs_no = []
            for lang in conf_str.split("|"):
                if lang not in langs:
                    langs_no.append(lang)
            if len(langs_no) > 0:
                return False, _("Tesseract OCR database {} is not installed")\
                    .format("-".join(langs_no))
        except ModuleNotFoundError as e:
            print(e)
            get_logger().error(e)
            s = _("please install python whl")
            s += str(e).replace("No module named", "")
            return False, s

        ok, text = self.ocr_image(path, conf_str)
        if not ok:
            return ok, text

        self.set_conf(conf_str)
        return ok, text
