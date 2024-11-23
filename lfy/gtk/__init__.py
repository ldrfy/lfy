import os
import subprocess

import gi  # pylint: disable=E0401

from lfy import APP_ID, PKGDATA_DIR, SCHEMAS_DIR  # pylint: disable=E0401

gi.require_version("Adw", "1")
gi.require_version('Gio', '2.0')
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')

from gi.repository import Gio

try:
    subprocess.run(["glib-compile-schemas",
                    f"{SCHEMAS_DIR}/glib-2.0/schemas"], check=True)
    os.environ["XDG_DATA_DIRS"] = f'{SCHEMAS_DIR}:' + \
        os.environ.get("XDG_DATA_DIRS", "")
except Exception as e:
    print(e)

# pylint: disable=w0212
Gio.Resource._register(Gio.resource_load(
    os.path.join(PKGDATA_DIR, f'{APP_ID}.gresource')))
