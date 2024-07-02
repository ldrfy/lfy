"""翻译服务集合

"""
from lfy.api.base import Server
from lfy.api.server import aliyun, baidu, bing, google, tencent

SERVERS: list[Server] = [
    google.GoogleServer(),
    bing.BingServer(),
    baidu.BaiduServer(),
    tencent.TencentServer(),
    aliyun.AliYunServer(),
]
