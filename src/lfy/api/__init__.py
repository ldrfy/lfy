from lfy.api.server import baidu


def translate_by_server(text, server, lang_to, lang_from="auto"):
    print(server)
    return baidu.translate_text(text, lang_to, lang_from)
