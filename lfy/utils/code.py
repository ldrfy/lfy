'终端翻译'
import argparse
import os
import traceback
from gettext import gettext as _

from lfy.api import (create_server_o, create_server_t, get_servers_o,
                     get_servers_t, lang_n2key)
from lfy.api.server import Server
from lfy.utils.debug import get_logger
from lfy.utils.settings import Settings


def get_help_lang(server: Server):
    """某个服务的lang key

    Args:
        server (Server): _description_

    Returns:
        _type_: _description_
    """
    # 每个翻译对应的key
    print('please add "-l number", number like:')
    return {lang.get_name(): lang.n for lang in server.langs}


def get_help_server(is_ocr=False):
    """某个服务的lang key

    Args:
        is_ocr (bool): _description_

    Returns:
        _type_: _description_
    """
    print('please add "-s server", server like:')
    if is_ocr:
        return {s.name: s.key for s in get_servers_o()}
    return {s.name: s.key for s in get_servers_t()}


def set_vpn():
    """_summary_
    """

    # 设置代理地址和端口号
    proxy_address = Settings().g("vpn-addr-port")
    if len(proxy_address) > 0:
        # 设置环境变量
        os.environ['http_proxy'] = proxy_address
        os.environ['https_proxy'] = proxy_address


def req_text(s, key_server="", key_lang_n=-1):
    """子线程翻译

    Args:
        s (str): _description_
        key_server (str): _description_
        key_lang_n (int): _description_
    """

    try:
        if not key_server:
            return get_help_server(False)
        server: Server = create_server_t(key_server)

        lang_selected = lang_n2key(server, key_lang_n)

        if not lang_selected:
            return get_help_lang(server)
        print("translate", server.name, lang_selected.get_name())

        if not s:
            return _("no text")
        print(s)
        set_vpn()

        _ok, text = server.translate_text(s, lang_selected.key)
        return text

    except Exception as e:  # pylint: disable=W0718
        get_logger().error(e)
        return _("something error: {}")\
            .format(f"{server.name}\n\n{str(e)}\n\n{traceback.format_exc()}")


def req_ocr(s=None, key_server=None, key_lang_n=-1):
    """子线程翻译

    Args:
        s (str): _description_
        key_server (str): _description_
        key_lang_n (int): _description_
    """

    try:
        if not key_server:
            return get_help_server(True)
        server = create_server_o(key_server)

        lang_selected = lang_n2key(server, key_lang_n)

        if not lang_selected:
            return get_help_lang(server)

        if not s or not os.path.exists(s):
            return _("the file does not exist: {}").format(s)
        print("ocr", server.name, lang_selected.get_name())
        set_vpn()

        _ok, text = server.ocr_image(s, lang_selected.key)
        return text

    except Exception as e:  # pylint: disable=W0718
        get_logger().error(e)
        return _("something error: {}")\
            .format(f"{server.name}\n\n{str(e)}\n\n{traceback.format_exc()}")


def parse_lfy():
    """设置
    """
    des = _('Command line translation or text recognition, such as {} or {}')\
        .format('lfy -t "who am i" -s bing -l 1', 'lfy -o "/tmp/xxx.png" -s baidu -l 1')
    parser = argparse.ArgumentParser(description=des)

    parser.add_argument('-t', type=str,
                        help=_('Translate, followed by text'))
    parser.add_argument('-o', type=str,
                        help=_('Recognize image, followed by file path'))

    parser.add_argument('-s', type=str, default="", nargs='?',
                        help=_('Which service engine to use, if -s is not entered, help will be provided based on -t or -o'))
    parser.add_argument('-l', type=int, default=-1, nargs='?',
                        help=_('The language to be translated/recognized, if -l is not entered, corresponding help will be provided based on the input of -s'))

    args = parser.parse_args()

    if args.t:
        return req_text(args.t, args.s, args.l)
    if args.o:
        return req_ocr(args.o, args.s, args.l)
    return None
