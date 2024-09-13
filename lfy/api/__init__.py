"""翻译服务集合

"""
from gi.repository import Gtk

from lfy.api.constant import SERVERS
from lfy.api.server import Lang, Server
from lfy.api.server.ocr import ocr


def get_server_names():
    """获取所有翻译服务的名字

    Returns:
        list: ["百度", "腾讯", ...]
    """
    return Gtk.StringList.new([s.name for s in SERVERS])


def get_servers_api_key():
    """哪些需要填写api

    Returns:
        list: ["百度", "腾讯", ...]
    """

    return [s for s in SERVERS if s.get_api_key_s() is not None]


def get_server_names_api_key():
    """哪些需要填写api

    Returns:
        list: ["百度", "腾讯", ...]
    """
    return [s.name for s in get_servers_api_key()]


def get_server(i: int) -> Server:
    """_summary_

    Args:
        i (int): _description_

    Returns:
        _type_: _description_
    """
    if i >= len(SERVERS):
        return SERVERS[0]
    return SERVERS[i]


def create_server(key) -> Server:
    """引擎字典

    Returns:
        _type_: _description_
    """
    ss = {s.key: s for s in SERVERS if s.can_translate}

    if key not in ss.keys():
        return ss["google"]
    return ss[key]


def create_server_ocr(key) -> Server:
    """引擎字典

    Returns:
        _type_: _description_
    """
    ss = {s.key: s for s in SERVERS if s.can_ocr}

    if key not in ss.keys():
        return ss["baidu"]
    return ss[key]


def get_lang_names(i=0):
    """获取某个翻译服务的所有翻译语言的名字

    Returns:
        list: 如 ["auto"]
    """
    return Gtk.StringList.new(get_server(i).get_lang_names())


def get_lang(i=0, j=0) -> Lang:
    """获取某个翻译服务的所有翻译语言的名字

    Returns:
        list: 如 ["auto"]
    """
    return get_server(i).get_lang(j)


def server_key2i(key: str):
    """分辨是哪个服务的唯一标识符

    Returns:
        int: 在 servers 是第几个
    """
    for i, te in enumerate(SERVERS):
        if te.key == key:
            return i
    return 0


def lang_n2j(i: int, n: int):
    """分辨是翻译成哪个语言的唯一标识符

    Args:
        i (int): _description_
        n (int): _description_

    Returns:
        int: 在当前server中是第一个lang
    """
    for j, lang in enumerate(get_server(i).langs):
        if lang.n == n:
            return j
    return 0
