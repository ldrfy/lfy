"""_summary_

"""
from gettext import gettext as _

from lfy.api.base import Server
from lfy.api.server import baidu, bing, google, tencent

SERVERS: list[Server] = [
    google.GoogleServer(),
    bing.BingServer(),
    baidu.BaiduServer(),
    tencent.TencentServer(),
]
