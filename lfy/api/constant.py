'常量，尽可能不引用其他文件'
from lfy.api.server.ocr.baidu import BaiduServer as BaiduOCRServer
from lfy.api.server.ocr.easyocr import EasyOcrServer
from lfy.api.server.ocr.pytesseract import PytesseractServer
from lfy.api.server.tra.aliyun import AliYunServer
from lfy.api.server.tra.baidu import BaiduServer
from lfy.api.server.tra.bing import BingServer
from lfy.api.server.tra.google import GoogleServer
from lfy.api.server.tra.huoshan import HuoShanServer
from lfy.api.server.tra.tencent import TencentServer

SERVERS_TRA = []
SERVERS_OCR = []

# 翻译服务
def get_servers_t():
    global SERVERS_TRA
    if not SERVERS_TRA:
        SERVERS_TRA = [
            GoogleServer(),
            BingServer(),
            BaiduServer(),
            TencentServer(),
            AliYunServer(),
            HuoShanServer(),
        ]

    return SERVERS_TRA

def get_servers_o():
    # OCR文本识别服务
    global SERVERS_OCR
    if not SERVERS_OCR:

        SERVERS_OCR = [
            BaiduOCRServer(),
            PytesseractServer(),
            EasyOcrServer(),
        ]
    return SERVERS_OCR


NO_TRANSLATED_TXTS = [
    "\"server-sk-",
]
