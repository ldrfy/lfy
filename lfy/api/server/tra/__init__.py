"""翻译"""
import html
from gettext import gettext as _

from lfy.api.server import Server

NO_TRANSLATED_TXTS = [
    "\"server-sk-",
]


def normalize_translation_text(s: str) -> str:
    s = s.strip()
    # 1. 确保是字符串
    if not isinstance(s, str):
        s = str(s)

    # 2. 把 HTML 实体解码一次（避免重复解码）
    s = html.unescape(s)

    return s


class ServerTra(Server):
    """翻译基础类
    """
    supports_image = False

    def _main_common(self, *args, **kwargs):
        """通用翻译流程。

        Args:
            args (tuple): 调用参数
            kwargs (dict): 调用参数

        Returns:
            tuple: (是否成功, 翻译结果或错误信息)
        """
        ok, text = super().main(*args, **kwargs)
        text = normalize_translation_text(text.strip())
        return ok, text

    def _validate_text_args(self, *args):
        """校验文本翻译参数。

        Args:
            args (tuple): 调用参数
        """
        if len(args) != 3:
            raise ValueError("args: text, lang_to, lang_from")

    def _validate_image_args(self, *args, **kwargs):
        """校验图片翻译参数。

        Args:
            args (tuple): 调用参数
            kwargs (dict): 调用参数

        Returns:
            bool: 是否支持图片翻译
        """
        if not self.supports_image:
            return False
        if len(args) != 3:
            raise ValueError("args: img_path, lang_to, lang_from")
        return "fun_main" in kwargs

    def get_doc_url(self, d="t"):
        """文档连接

        Returns:
            _type_: _description_
        """
        return super().get_doc_url(d)

    def main(self, *args, **kwargs):
        self._validate_text_args(*args)
        ss_ntt = []
        for ntt in NO_TRANSLATED_TXTS:
            if ntt in args[0]:
                ss_ntt.append(ntt)
        if ss_ntt:
            return False, _("This time the content contains "
                            "private information and is not translated")
        return self._main_common(*args, **kwargs)

    def main_image(self, *args, **kwargs):
        """图片翻译。

        Args:
            args (tuple): 图片路径、目标语言、源语言
            kwargs (dict): 额外参数

        Returns:
            tuple: (是否成功, 翻译结果或错误信息)
        """
        if not self._validate_image_args(*args, **kwargs):
            return False, _("This server does not support image translation")
        return self._main_common(*args, **kwargs)
