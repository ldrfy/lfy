"""比较翻译接口
"""
import traceback
from gettext import gettext as _
from multiprocessing import Pool

from lfy.api.server import Server, aliyun, baidu, bing, google, tencent


def _translate(args):
    """翻译pool，不要让一个错误影响所有

    Args:
        args (_type_): _description_

    Returns:
        _type_: _description_
    """
    server, text, lang_to, lang_from = args
    try:
        return server.translate_text(text, lang_to, lang_from)
    except Exception as e:  # pylint: disable=W0718
        error_msg = _("something error:")
        return False, f"{error_msg}{server.name}\n\n{str(e)}\n\n{traceback.format_exc()}"


class AllServer(Server):
    """翻译集合
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
        super().__init__("compare", _("compare"), lang_key_ns)

    def translate_text(self, text, lang_to="1", lang_from="auto"):
        """翻译集成

        Args:
            text (str): 待翻译字符
            lang_to (str, optional): 翻译成什么语言. Defaults to "zh-cn".
            lang_from (str, optional): 文本是什么语言. Defaults to "auto".

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
            rs = p.map(_translate, args)
            s_ok = ""
            s_error = ""
            for i, tt in enumerate(rs):
                ok, t = tt
                if ok:
                    s_ok += f"***** {self.servers[i].name} *****\n{t}\n\n"
                else:
                    s_error += f"***** {self.servers[i].name} *****\n{t}\n\n"
            return True, s_ok + s_error
