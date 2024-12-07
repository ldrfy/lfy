"""更新
"""

from gettext import gettext as _

import requests

from lfy import PACKAGE_URL, VERSION  # pylint: disable=E0611
from lfy.api.server import TIME_OUT
from lfy.utils.debug import get_logger


def get_by_url(url, bz=""):
    """通过url获取更新信息

    Args:
        url (str): url
        bz (str, optional): 备注. Defaults to "".

    Returns:
        dict: 更新信息
    """
    try:
        request = requests.get(url, timeout=TIME_OUT)
        if request.status_code == 200:
            get_logger().info("%s update msg ok", bz)
            return request.json()
    except requests.exceptions.ConnectTimeout as e:
        get_logger().error(e)
        return {}
    except requests.exceptions.ProxyError as e:
        get_logger().error(e)
        return {}
    except Exception as e:  # pylint: disable=W0718
        get_logger().error(e)
    return None


def get_by_gitee():
    """gitee

    Returns:
        _type_: _description_
    """
    url = "https://gitee.com/yuhldr/lfy/raw/main/data/version.json"

    return get_by_url(url, "gitee")


def get_by_github():
    """github

    Returns:
        _type_: _description_
    """
    url = "https://raw.githubusercontent.com/ldrfy/lfy/main/data/version.json"

    return get_by_url(url, "github")


def compare_versions(v_new, v_old):
    """比较版本号

    Args:
        v_new (str): 新的版本号
        v_old (str): 旧的版本号

    Returns:
        bool: 如果新的确实更新，返回True，否则False
    """
    v1 = list(map(int, v_new.split('.')))
    v2 = list(map(int, v_old.split('.')))
    print(v1, v2)

    for a, b in zip(v1, v2):
        if a < b:
            return False
        if a > b:
            return True

    if len(v1) < len(v2):
        return False
    if len(v1) > len(v2):
        return True

    return False


def main():
    """更新

    Returns:
        str: 更新信息或None
    """
    s = "Please update. There is a problem with the current version configuration.\n\n"
    s += PACKAGE_URL
    try:
        data = get_by_github()
        if data is None or "version" not in data:
            data = get_by_gitee()
        if data is None or "version" not in data:
            return s

        v = data["version"]
        if compare_versions(v, VERSION):
            return f'New version: {v}\n\nplease upgrade it:\n{data["url"]}\n\n{data["msg"]}'
        return None
    # pylint: disable=W0718
    except Exception as e:
        get_logger().error(e)
        return s
