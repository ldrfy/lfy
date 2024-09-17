"""翻译服务集合

"""
from gi.repository import Gtk

from lfy.api.constant import SERVERS
from lfy.api.server import Lang, Server

servers_t = None
servers_o = None


def get_servers_t():
    """翻译的服务

    Returns:
        dict: _description_
    """
    global servers_t  # pylint:disable=W0603
    if servers_t is None:
        servers_t = [s for s in SERVERS if s.can_translate]
    return servers_t


def get_servers_o():
    """OCR的服务

    Returns:
        dict: _description_
    """
    global servers_o  # pylint:disable=W0603
    if servers_o is None:
        servers_o = [s for s in SERVERS if s.can_ocr]
    return servers_o


def get_server_names_t():
    """翻译的服务名字

    Returns:
        list: _description_
    """
    return get_server_names(get_servers_t())


def get_server_names_o():
    """OCR的服务名字

    Returns:
        _type_: _description_
    """
    return get_server_names(get_servers_o())


def get_server_names(ss):
    """获取所给服务的名字

    Returns:
        list: ["百度", "腾讯", ...]
    """
    return Gtk.StringList.new([s.name for s in ss])


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
    return get_server_names(get_servers_api_key())


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


def create_server_t(key) -> Server:
    """引擎字典

    Returns:
        _type_: _description_
    """

    for s in get_servers_t():
        if s.key == key:
            return s

    return get_servers_t()[0]


def create_server_o(key) -> Server:
    """引擎字典

    Returns:
        _type_: _description_
    """
    for s in get_servers_o():
        if s.key == key:
            return s

    return get_servers_o()[0]


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
