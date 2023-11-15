from lt_gtk.api.server import baidu


def translate(text, server, lang_to, lang_from="auto"):
    print(server)
    return baidu.translate_text(text, lang_to, lang_from)
