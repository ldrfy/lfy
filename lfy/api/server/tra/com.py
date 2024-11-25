"""比较翻译接口
"""
import time
import traceback
from gettext import gettext as _
from multiprocessing import Pool

from lfy.api.constant import SERVERS_T
from lfy.api.server import Server
from lfy.utils.debug import get_logger
from lfy.utils.settings import Settings


def _translate(args):
    """翻译pool，不要让一个错误影响所有

    Args:
        args (_type_): _description_

    Returns:
        _type_: _description_
    """
    st = time.time()
    server, text, lang_to, lang_from = args
    try:
        a, b = server.translate_text(text, lang_to, lang_from)
        return a, b, server, time.time()-st
    except Exception as e:  # pylint: disable=W0718
        em = _("something error: {}")\
            .format(f"{server.name}\n\n{str(e)}\n\n{traceback.format_exc()}")
        get_logger().error(e)
        return False, em, server, time.time()-st


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

        # 只对比设置中修改的
        all_servers = {
            server.key: server for server in SERVERS_T
        }
        keys = Settings().g("compare-servers")

        # 初始化 self.servers
        if not keys:  # 如果 keys 为空，则选择所有服务器
            self.servers = list(all_servers.values())
        else:
            # 仅选择在 keys 列表中的服务器，并且按照顺序！
            self.servers = [all_servers[key]
                            for key in keys if key in all_servers]

        super().__init__("compare", _("compare"), lang_key_ns)
        self.can_translate = True

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
            s_ok = ""
            s_error = ""
            for i, tt in enumerate(p.map(_translate, args)):
                ok, text_, se, user_time = tt
                # 防止session每次刷新
                self.servers[i] = se
                if ok:
                    s_ok += f"***** {self.servers[i].name}"
                    s_ok += f":{user_time:.2f}s *****\n{text_}\n\n"
                else:
                    s_error += f"***** {self.servers[i].name}"
                    s_error += f":{user_time:.2f}s *****\n{text_}\n\n"
            return True, s_ok + s_error
