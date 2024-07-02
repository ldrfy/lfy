"""比较翻译接口
"""
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
        self.servers: list[Server] = [aliyun.AliYunServer(), baidu.BaiduServer(),
                                      bing.BingServer(), google.GoogleServer(),
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
            print(server.name, lang_to, lang_to_)
            args.append((server, text, lang_to_, lang_from))
        with Pool(len(args)) as p:
            rs = p.map(self._translate, args)
            s_ok = ""
            for i, tt in enumerate(rs):
                s_ok += f"{self.servers[i].name}: {tt}\n\n*****\n\n"
            return s_ok

    def _translate(self, args):
        server, text, lang_to, lang_from = args
        return server.translate_text(text, lang_to, lang_from)
