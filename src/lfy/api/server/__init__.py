"""_summary_

"""

from gettext import gettext as _

TIME_OUT = 3

LANGUAGE_NAMES = [
    # 0
    _("Automatic"),
    # 1
    _("Chinese"),
    # 2
    _("Classical Chinese"),
    # 3
    _("English"),
    # 4
    _("Japanese"),
    # 5
    _("Korean"),
    # 6
    _("German"),
    # 7
    _("French")
]


class Lang():
    """语言
    """

    def __init__(self, key: str, n: int):
        """初始化

        Args:
            key (str): 其实是翻译称某种语言时 需要传递到这个server的关键字
            n (int): 这个关键字在内置 LANGUAGE_NAMES 名单中是第几个
            name (str): LANGUAGE_NAMES 中的名字，方便翻译
        """
        self.key = key
        self.n = n
        self.name = LANGUAGE_NAMES[n]


class Server:
    """翻译信息
    """

    def __init__(self, key: str, name: str, is_api_key=False, doc_url="", lang_keys=None, lang_ns=None):
        self.key = key
        self.doc_url = doc_url
        self.is_api_key = is_api_key
        self.name = _(name)
        if lang_keys is None:
            lang_keys = [""]
        if lang_ns is None:
            lang_keys = [0]

        self.langs: list[Lang] = []
        for i, n in enumerate(lang_ns):
            self.langs.append(Lang(lang_keys[i], n))


SERVER_BAIDU = Server("baidu", _("baidu"), True, "", [
    "auto", "zh", "wyw", "en", "jp", "kor", "de", "fra"], range(8))

SERVER_TENCENT = Server("tencent", _("tencent"), True, "", [
    "zh", "en", "jp", "kr", "de", "fr"], [1, 3, 4, 5, 6, 7])

SERVER_GOOGLE = Server("google", _("google"), False, "", [
    "zh", "en", "ja", "ko", "de", "fr"], [1, 3, 4, 5, 6, 7])

SERVER_YOUDAO = Server("youdao", _("youdao"), False, "", ["auto"], [0])


servers = [
    SERVER_YOUDAO,
    SERVER_GOOGLE,
    SERVER_BAIDU,
    SERVER_TENCENT,
]


def get_server_names():
    """获取所有翻译服务的名字

    Returns:
        list: ["百度", "腾讯", ...]
    """
    sns = []
    for server in servers:
        sns.append(server.name)
    return sns


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
    lang_names = []
    server = get_server(i)
    for lang in server.langs:
        lang_names.append(lang.name)
    return lang_names


def get_lang(i=0, j=0):
    """获取某个翻译服务的所有翻译语言的名字

    Returns:
        list: 如 ["auto"]
    """
    te = get_server(i)
    if i >= len(te.langs):
        return te.langs[0]
    return te.langs[j]


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
