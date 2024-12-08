"""比较翻译接口
"""
import time
import traceback
from gettext import gettext as _
from multiprocessing import Pool

from lfy.api.constant import ALL_SELECT_SERVERS as ALL_SERVERS
from lfy.api.server.tra import ServerTra
from lfy.utils.debug import get_logger


def _translate0(args):
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
        a, b = server.main(text, lang_to)
        return a, b, server, time.time()-st
    except Exception as e:  # pylint: disable=W0718
        em = _("something error: {}")\
            .format(f"{server.name}\n\n{str(e)}\n\n{traceback.format_exc()}")
        get_logger().error(e)
        return False, em, server, time.time()-st


def get_args(text, lang_to):
    """_summary_

    Args:
        text (_type_): _description_
        lang_to (_type_): _description_

    Returns:
        _type_: _description_
    """
    args = []
    for server in ALL_SERVERS:
        server: ServerTra
        lang_to_ = "en"
        for lang in server.langs:
            if lang.n == int(lang_to):
                lang_to_ = lang.key
                break
        args.append((server, text, lang_to_))
    return args


def _translate(_st: ServerTra, text, lang_to):
    args = get_args(text, lang_to)

    with Pool(len(args)) as p:
        s_ok = ""
        s_error = ""
        for i, tt in enumerate(p.map(_translate0, args)):
            ok, text_, se, user_time = tt
            # 防止session每次刷新
            ALL_SERVERS[i] = se
            if ok:
                s_ok += f"***** {ALL_SERVERS[i].name}"
                s_ok += f":{user_time:.2f}s *****\n{text_}\n\n"
            else:
                s_error += f"***** {ALL_SERVERS[i].name}"
                s_error += f":{user_time:.2f}s *****\n{text_}\n\n"
        return True, s_ok + s_error


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

        self.set_data(lang_key_ns)

    def main(self, *args, **kwargs):
        return super().main(*args, fun_main=_translate)
