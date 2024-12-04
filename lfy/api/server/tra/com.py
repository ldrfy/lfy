"""比较翻译接口
"""
import time
import traceback
from gettext import gettext as _
from multiprocessing import Pool

from lfy.api.constant import get_servers_t
from lfy.api.server.tra import ServerTra
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
    server, text, lang_to = args
    server: ServerTra
    try:
        a, b = server.translate_text(text, lang_to)
        return a, b, server, time.time()-st
    except Exception as e:  # pylint: disable=W0718
        em = _("something error: {}")\
            .format(f"{server.name}\n\n{str(e)}\n\n{traceback.format_exc()}")
        get_logger().error(e)
        return False, em, server, time.time()-st


class AllServer(ServerTra):
    """翻译集合
    """

    def __init__(self):

        super().__init__("compare", _("compare"))

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
        all_servers = {}
        for server in get_servers_t():
            all_servers[server.key] = server
        keys = Settings().g("compare-servers")

        # 初始化 self.servers
        if not keys:  # 如果 keys 为空，则选择所有服务器
            self.servers = list(all_servers.values())
        else:
            # 仅选择在 keys 列表中的服务器，并且按照顺序！
            self.servers = [all_servers[key] for key in keys
                            if key in all_servers]

        self.set_data(lang_key_ns)

    def translate_text(self, text, lang_to="1", fun_tra=None):
        args = []
        for server in self.servers:
            server: ServerTra
            lang_to_ = "en"
            for lang in server.langs:
                if lang.n == int(lang_to):
                    lang_to_ = lang.key
                    break
            args.append((server, text, lang_to_))
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
