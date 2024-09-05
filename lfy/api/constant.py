'常量，尽可能不引用其他文件'
from lfy.api.server import (Server, aliyun, baidu, bing, com, google, huoshan,
                            tencent)

SERVERS: list[Server] = [
    com.AllServer(),
    google.GoogleServer(),
    bing.BingServer(),
    baidu.BaiduServer(),
    tencent.TencentServer(),
    aliyun.AliYunServer(),
    huoshan.HuoShanServer(),
]


NO_TRANSLATED_TXTS = [
    "\"server-sk-",
]
