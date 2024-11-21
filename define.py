'初始信息'
import gettext
import locale
import os

APP_NAME = '@APP_NAME@'
APP_ID = '@APP_ID@'
VERSION = '@VERSION@'
PACKAGE_URL_BUG = '@PACKAGE_URL_BUG@'
PACKAGE_URL = '@PACKAGE_URL@'
RES_PATH = '/cool/ldr/lfy'


THIS_DIR, THIS_FILENAME = os.path.split(__file__)


def set_internationalization(appid, locale_dir):
    """Sets application internationalization."""
    try:
        locale.bindtextdomain(appid, locale_dir)
        locale.textdomain(appid)
    except AttributeError as e:
        from lfy.api.utils.debug import get_logger
        get_logger().error(e)
        print(f"Some gettext translations will not work. Error:\n{e}")

    gettext.bindtextdomain(appid, locale_dir)
    gettext.textdomain(appid)
