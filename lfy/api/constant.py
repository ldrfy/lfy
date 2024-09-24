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

# 翻译服务
SERVERS_T = [
    GoogleServer(),
    BingServer(),
    BaiduServer(),
    TencentServer(),
    AliYunServer(),
    HuoShanServer(),
]

# OCR文本识别服务
SERVERS_O = [
    BaiduOCRServer(),
    PytesseractServer(),
    EasyOcrServer(),
]


NO_TRANSLATED_TXTS = [
    "\"server-sk-",
]
