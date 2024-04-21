"""_summary_

"""
from gettext import gettext as _

from lfy.api.base import Server
from lfy.api.server import baidu, google, tencent

SERVERS: list[Server] = [
    baidu.BaiduServer(),
    tencent.TencentServer(),
    google.GoogleServer(),
]
