'常量，尽可能不引用其他文件'
from lfy.api.server.aliyun import AliYunServer
from lfy.api.server.baidu import BaiduServer
from lfy.api.server.bing import BingServer
from lfy.api.server.com import AllServer
from lfy.api.server.google import GoogleServer
from lfy.api.server.huoshan import HuoShanServer
from lfy.api.server.tencent import TencentServer

SERVERS = [
    AllServer(),
    GoogleServer(),
    BingServer(),
    BaiduServer(),
    TencentServer(),
    AliYunServer(),
    HuoShanServer(),
]


NO_TRANSLATED_TXTS = [
    "\"server-sk-",
]
