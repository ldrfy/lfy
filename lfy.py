#!@PYTHON@

# lt
import argparse
import gettext
import locale
import os
import subprocess
import sys
from gettext import gettext as _

import gi

gi.require_version("Adw", "1")
gi.require_version('Gio', '2.0')
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')

APP_ID = '@APP_ID@'
VERSION = '@VERSION@'

SCHEMAS_DIR = '@SCHEMAS_DIR@'
PYTHON_DIR = '@PYTHON_DIR@'

LOCALE_DIR = '@LOCALE_DIR@'
PKGDATA_DIR = '@PKGDATA_DIR@'

if not os.path.exists(PKGDATA_DIR):
    # 说明是pip这一类的
    print(f"路径修正：{SCHEMAS_DIR}")
    THIS_DIR, THIS_FILENAME = os.path.split(__file__)
    PYTHON_DIR = os.path.abspath(f"{THIS_DIR}/../lib/")
    SCHEMAS_DIR = os.path.abspath(f"{THIS_DIR}/../share/")
    PKGDATA_DIR = os.path.abspath(f"{SCHEMAS_DIR}/{APP_ID}/")
    LOCALE_DIR = os.path.abspath(f"{SCHEMAS_DIR}/locale/")
    subprocess.run(
        ["glib-compile-schemas", f"{SCHEMAS_DIR}/glib-2.0/schemas"], check=True)

    os.environ["XDG_DATA_DIRS"] = f'{SCHEMAS_DIR}:' + \
        os.environ.get("XDG_DATA_DIRS", "")
    print(SCHEMAS_DIR)

# python lib
sys.path.append(PYTHON_DIR)


def set_internationalization():
    """Sets application internationalization."""
    try:
        locale.bindtextdomain(APP_ID, LOCALE_DIR)
        locale.textdomain(APP_ID)
    except AttributeError as e:
        from lfy.api.utils.debug import get_logger
        get_logger().error(e)
        print(f"Some gettext translations will not work. Error:\n{e}")

    gettext.bindtextdomain(APP_ID, LOCALE_DIR)
    gettext.textdomain(APP_ID)


def set_resources():
    """Sets application ressource file."""
    from gi.repository import Gio  # pylint: disable=c0415

    # pylint: disable=w0212
    Gio.Resource._register(Gio.resource_load(
        os.path.join(PKGDATA_DIR, f'{APP_ID}.gresource')))


def run_application():
    """运行

    Returns:
        _type_: _description_
    """
    from lfy.main import LfyApplication  # pylint: disable=c0415
    return LfyApplication(APP_ID, VERSION).run(sys.argv)


def main():
    """主入口

    Returns:
        _type_: _description_
    """
    set_internationalization()

    parser = argparse.ArgumentParser(description=_('Command line translation or text recognition, such as {} or {}').format('lfy -t "who am i" -s bing -l 1', 'lfy -o "/tmp/xxx.png" -s baidu -l 1'))

    parser.add_argument('-t', type=str, help=_('Translate, followed by text'))
    parser.add_argument('-o', type=str, help=_('Recognize image, followed by file path'))
    parser.add_argument('-c', action='store_true', help=_('Automatically translate clipboard, temporarily invalid'))

    parser.add_argument('-s', type=str, help=_('Which service engine to use, if -s is not entered, help will be provided based on -t or -o'), default="", nargs='?')
    parser.add_argument('-l', type=int, help=_('The language to be translated/recognized, if -l is not entered, corresponding help will be provided based on the input of -s'), default=-1, nargs='?')

    args = parser.parse_args()

    if args.c:
        from lfy.code import req_clip
        print(req_clip(args.s, args.l))
        return
    if args.t:
        from lfy.code import req_text
        print(req_text(args.t, args.s, args.l))
        return
    if args.o:
        from lfy.code import req_ocr
        print(req_ocr(args.o, args.s, args.l))
        return

    set_resources()
    return sys.exit(run_application())


if __name__ == '__main__':
    main()
