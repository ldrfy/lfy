'ocr'
from gettext import gettext as _

from lfy.api.server.ocr import ServerOCR
from lfy.utils import gen_img
from lfy.utils.debug import get_logger


class EasyOcrServer(ServerOCR):
    """EasyOcr文字识别
    """

    def __init__(self):
        super().__init__("easyocr", "easyocr")

    def ocr_image(self, img_path, conf_str=None):
        try:
            import easyocr
            if conf_str is None:
                conf_str = self.get_conf()
            lang_keys = conf_str.split("|")
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

    def check_conf(self, conf_str):
        try:
            import easyocr

            # 放在 import 后面，因为未安装 pytesseract 会引发异常
            path = gen_img("success")
            if path is None:
                return True, _("The Python library `Pillow` is not installed, you cannot test whether the setting is successful now, if the OCR reports an error in the future, please change this content")
            ok, text = self.ocr_image(path)
            if ok:
                self.set_conf(conf_str)
            return ok, text

        except ModuleNotFoundError as e:
            print(e)
            get_logger().error(e)
            s = _("please install python whl")
            s += str(e).replace("No module named", "")
            return False, s
