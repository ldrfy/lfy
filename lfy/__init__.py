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

PKGDATA_DIR = '@PKGDATA_DIR@'
SCHEMAS_DIR = '@SCHEMAS_DIR@'
PYTHON_DIR = '@PYTHON_DIR@'
LOCALE_DIR = '@LOCALE_DIR@'

if not os.path.exists(f"{LOCALE_DIR}/zh_CN/LC_MESSAGES/{APP_ID}.mo"):
    LOCALE_DIR = os.path.join(os.path.dirname(__file__),
                              "resources/locale/")
    print("new LOCALE_DIR", LOCALE_DIR)

try:
    locale.bindtextdomain(APP_ID, LOCALE_DIR)
    locale.textdomain(APP_ID)
except AttributeError as e:
    print(f"Some gettext/locale translations will not work. Error:\n{e}")

try:
    gettext.bindtextdomain(APP_ID, LOCALE_DIR)
    gettext.textdomain(APP_ID)
except AttributeError as e:
    print(f"Some gettext translations will not work. Error:\n{e}")

APP_DES = gettext.gettext(
    'Translation software designed for reading scientific research literature')
