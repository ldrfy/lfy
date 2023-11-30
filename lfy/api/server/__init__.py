"""_summary_

"""
from gettext import gettext as _

from gi.repository import Gtk

from lfy.api.server import baidu, google, tencent

servers = [
    baidu.SERVER,
    tencent.SERVER,
    google.SERVER,
]


def get_server_names():
    """获取所有翻译服务的名字

    Returns:
        list: ["百度", "腾讯", ...]
    """
    return Gtk.StringList.new([server.name for server in servers])

def get_servers_api_key():
    """哪些需要填写api

    Returns:
        list: ["百度", "腾讯", ...]
    """

    return [server for server in servers if server.is_api_key]


def get_server_names_api_key():
    """哪些需要填写api

    Returns:
        list: ["百度", "腾讯", ...]
    """
    return [server.name for server in get_servers_api_key()]


def get_server(i: int):
    """_summary_

    Args:
        i (int): _description_

    Returns:
        _type_: _description_
    """
    if i >= len(servers):
        return servers[0]
    return servers[i]


def get_lang_names(i=0):
    """获取某个翻译服务的所有翻译语言的名字

    Returns:
        list: 如 ["auto"]
    """
    return Gtk.StringList.new(get_server(i).get_lang_names())


def get_lang(i=0, j=0):
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
    for i, te in enumerate(servers):
        if te.key == key:
            return i
    return 0


def lang_n2j(i: int, n: int):
    """分辨是翻译成哪个语言的唯一标识符

    Returns:
        int: 在当前server中是第一个lang
    """
    for j, lang in enumerate(get_server(i).langs):
        if lang.n == n:
            return j
    return 0
