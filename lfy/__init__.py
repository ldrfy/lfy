'初始信息'
import gettext
import locale

APP_NAME = '@APP_NAME@'
APP_ID = '@APP_ID@'
VERSION = '@VERSION@'
PACKAGE_URL_BUG = '@PACKAGE_URL_BUG@'
PACKAGE_URL = '@PACKAGE_URL@'
RES_PATH = '/cool/ldr/lfy'

PKGDATA_DIR = '@PKGDATA_DIR@'
SCHEMAS_DIR = '@SCHEMAS_DIR@'
PYTHON_DIR = '@PYTHON_DIR@'
LOCALE_DIR = '@LOCALE_DIR@'

print("LOCALE_DIR", LOCALE_DIR)

try:
    locale.bindtextdomain(APP_ID, LOCALE_DIR)
    locale.textdomain(APP_ID)
except AttributeError as e:
    print(f"Some gettext translations will not work. Error:\n{e}")

gettext.bindtextdomain(APP_ID, LOCALE_DIR)
gettext.textdomain(APP_ID)
