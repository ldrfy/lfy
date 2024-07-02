"""比较翻译接口
"""
import traceback
from gettext import gettext as _
from multiprocessing import Pool

from lfy.api.base import Server
from lfy.api.server import aliyun, baidu, bing, google, tencent


class AllServer(Server):
    """bing翻译，无需apikey

    Args:
        Server (_type_): _description_
    """

    def __init__(self):

        # https://learn.microsoft.com/zh-cn/azure/ai-services/translator/language-support
        lang_key_ns = {
            "1": 1,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
        }
        # 这里不能直接引用
        # from lfy.api.server import SERVERS
        # 会导致循环

        self.servers: list[Server] = [bing.BingServer(), google.GoogleServer(),
                                      aliyun.AliYunServer(), baidu.BaiduServer(),
                                      tencent.TencentServer()]
        super().__init__("compare",  _("compare"), lang_key_ns)

    def translate_text(self, text, lang_to="1", lang_from="auto"):
        """翻译集成

        Args:
            text (str): 待翻译字符
            to_lang_code (str, optional): 翻译成什么语言. Defaults to "zh-cn".
            from_lang (str, optional): 文本是什么语言. Defaults to "auto".

        Returns:
            str: _description_
        """
        args = []
        for server in self.servers:
            lang_to_ = "en"
            for lang in server.langs:
                if lang.n == int(lang_to):
                    lang_to_ = lang.key
                    break
            args.append((server, text, lang_to_, lang_from))
        with Pool(len(args)) as p:
            rs = p.map(self._translate, args)
            s_ok = ""
            for i, tt in enumerate(rs):
                s_ok += f"***** {self.servers[i].name} *****\n{tt}\n\n"
            return s_ok

    def _translate(self, args):
        """翻译pool，不要让一个错误影响所有

        Args:
            args (_type_): _description_

        Returns:
            _type_: _description_
        """
        try:
            server, text, lang_to, lang_from = args
            server.translate_text(text, lang_to, lang_from)
        except Exception as e:  # pylint: disable=W0718
            error_msg = _("something error:")
            error_msg = f"{error_msg}\n\n{str(e)}\n\n{traceback.format_exc()}"
            return str(e)
