'常量，尽可能不引用其他文件'
from lfy.api.server.ocr import ServerOCR
from lfy.api.server.ocr.baidu import BaiduServer as BaiduOCRServer
from lfy.api.server.ocr.easyocr import EasyOcrServer
from lfy.api.server.ocr.pytesseract import PytesseractServer
from lfy.api.server.tra import ServerTra
from lfy.api.server.tra.aliyun import AliYunServer
from lfy.api.server.tra.baidu import BaiduServer
from lfy.api.server.tra.bing import BingServer
from lfy.api.server.tra.google import GoogleServer
from lfy.api.server.tra.huoshan import HuoShanServer
from lfy.api.server.tra.tencent import TencentServer
from lfy.utils.settings import Settings

SERVERS_TRA: list[ServerTra] = [
    GoogleServer(),
    BingServer(),
    BaiduServer(),
    TencentServer(),
    AliYunServer(),
    HuoShanServer(),
]
SERVERS_OCR: list[ServerOCR] = [
    BaiduOCRServer(),
    PytesseractServer(),
    EasyOcrServer(),
]


def get_ass():
    """翻译服务

    Returns:
        _type_: _description_
    """
    # 只对比设置中修改的
    all_servers = {}
    for server in SERVERS_TRA:
        all_servers[server.key] = server
    keys = Settings().g("compare-servers")

    # 初始化 self.servers
    if not keys:  # 如果 keys 为空，则选择所有服务器
        return list(all_servers.values())

    # 仅选择在 keys 列表中的服务器，并且按照顺序！
    return [all_servers[key] for key in keys
            if key in all_servers]


ALL_SELECT_SERVERS: list[ServerTra] = get_ass()
