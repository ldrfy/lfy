#!@PYTHON@

# lt
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
    LOCALE_DIR = os.path.abspath(f"{SCHEMAS_DIR}/locale/")
    subprocess.run(
        ["glib-compile-schemas", f"{SCHEMAS_DIR}/glib-2.0/schemas"], check=True)

    os.environ["XDG_DATA_DIRS"] = f'{SCHEMAS_DIR}:' + \
        os.environ.get("XDG_DATA_DIRS", "")
    print(SCHEMAS_DIR)

# python lib
sys.path.append(PYTHON_DIR)


if __name__ == '__main__':
    os.environ[f'{APP_ID}.ui'] = 'gtk'

    from lfy import set_internationalization
    set_internationalization(APP_ID, LOCALE_DIR)

    from lfy.utils.code import parse_lfy
    parse_lfy()

    from gi.repository import Gio  # pylint: disable=c0415

    # pylint: disable=w0212
    Gio.Resource._register(Gio.resource_load(
        os.path.join(PKGDATA_DIR, f'{APP_ID}.gresource')))

    from lfy.gtk.main import LfyApplication

    sys.exit(LfyApplication(APP_ID, VERSION).run(sys.argv))
