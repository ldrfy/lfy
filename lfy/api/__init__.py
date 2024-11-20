"""翻译服务集合

"""

from lfy.api.constant import SERVERS_O, SERVERS_T
from lfy.api.server import Lang, Server
from lfy.api.server.tra.com import AllServer


def get_servers_t():
    """翻译的服务

    Returns:
        dict: _description_
    """
    s = [AllServer()]
    s += SERVERS_T

    return s


def get_servers_o():
    """OCR的服务

    Returns:
        dict: _description_
    """
    return SERVERS_O


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
    return [s.name for s in ss]


def get_servers_api_key():
    """哪些需要填写api

    Returns:
        list: ["百度", "腾讯", ...]
    """

    return [s for s in get_servers_t() if s.get_api_key_s() is not None]


def get_server_names_api_key():
    """哪些需要填写api

    Returns:
        list: ["百度", "腾讯", ...]
    """
    return get_server_names(get_servers_api_key())


def get_server(i: int, ss) -> Server:
    """_summary_

    Args:
        i (int): _description_

    Returns:
        _type_: _description_
    """
    if i >= len(ss):
        return ss[0]
    return ss[i]


def get_server_t(i: int) -> Server:
    """_summary_

    Args:
        i (int): _description_

    Returns:
        _type_: _description_
    """
    return get_server(i, get_servers_t())


def get_server_o(i: int) -> Server:
    """_summary_

    Args:
        i (int): _description_

    Returns:
        _type_: _description_
    """
    return get_server(i, get_servers_o())


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
    return get_server_t(i).get_lang_names()


def get_lang(i=0, j=0) -> Lang:
    """获取某个翻译服务的所有翻译语言的名字

    Args:
        i (int, optional): 第几个. Defaults to 0.
        j (int, optional): _description_. Defaults to 0.

    Returns:
        Lang: _description_
    """
    return get_server_t(i).get_lang(j)


def server_key2i(key: str, is_ocr=False):
    """分辨是哪个服务的唯一标识符

    Returns:
        int: 在 servers 是第几个
    """
    if is_ocr:
        ss = get_servers_o()
    else:
        ss = get_servers_t()
    for i, te in enumerate(ss):
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
    for j, lang in enumerate(get_server_t(i).langs):
        if lang.n == n:
            return j
    return 0


def lang_n2key(server: Server, n: int):
    """不同server的langs真正唯一的是n，不同server的key不一样

    Args:
        server (Server): _description_
        n (int): _description_

    Returns:
        Lang: 语言类
    """

    for lang in server.langs:
        if lang.n == n:
            return lang
    return None
