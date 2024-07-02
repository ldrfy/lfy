from lfy.api.server import aliyun, baidu, bing, com, google, tencent, Server

SERVERS: list[Server] = [
    com.AllServer(),
    google.GoogleServer(),
    bing.BingServer(),
    baidu.BaiduServer(),
    tencent.TencentServer(),
    aliyun.AliYunServer(),
]
