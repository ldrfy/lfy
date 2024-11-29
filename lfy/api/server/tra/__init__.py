'翻译'
from lfy.api.server import Server


class ServerTra(Server):
    """翻译基础类
    """

    def translate_text(self, text: str, lang_to: str, lang_from: str = "auto"):
        """实现文本翻译的逻辑

        Args:
            text (str): _description_
            lang_to (str): _description_
            lang_from (str): _description_

        Returns:
            str: _description_
        """
        print(f"lang_to={lang_to} lang_from={lang_from} text={text}")
        return True, "test"


    def get_doc_url(self, d="t"):
        """文档连接

        Returns:
            _type_: _description_
        """
        return super().get_doc_url(d)
