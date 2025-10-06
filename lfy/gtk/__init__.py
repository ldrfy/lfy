"""gtk启动"""
import json
import os
import platform
import subprocess

import gi  # pylint: disable=E0401

from lfy import APP_ID, PKGDATA_DIR, SCHEMAS_DIR  # pylint: disable=E0401
from lfy.utils import get_os_release
from lfy.utils.bak import backup_gsettings
from lfy.utils.debug import get_log_handler

gi.require_version("Adw", "1")
gi.require_version('Gio', '2.0')
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')

from gi.repository import Adw, Gio, Gtk  # type: ignore

try:
    if "/usr/share/" in SCHEMAS_DIR:
        subprocess.run(["glib-compile-schemas",
                        f"{SCHEMAS_DIR}/glib-2.0/schemas"], check=True)
        os.environ["XDG_DATA_DIRS"] = f'{SCHEMAS_DIR}:' + \
                                      os.environ.get("XDG_DATA_DIRS", "")
except subprocess.CalledProcessError as e:
    print(e)

path_res = os.path.join(PKGDATA_DIR, f'{APP_ID}.gresource')
Gio.Resource._register(Gio.resource_load(path_res))  # pylint: disable=w0212


def get_gtk_msg(version):
    """gtk调试信息

    Args:
        version (str): _description_

    Returns:
        _type_: _description_
    """
    s = f"Version: {version}"
    s += f"\nSystem: {platform.system()}"
    s += f"\nRelease: {platform.release()}"

    gvs = Gtk.get_major_version(), Gtk.get_minor_version(), Gtk.get_micro_version()
    s += f"\nGTK Version: {gvs[0]}.{gvs[1]}.{gvs[2]}"

    avs = Adw.get_major_version(), Adw.get_minor_version(), Adw.get_micro_version()
    s += f"\nAdwaita Version: {avs[0]}.{avs[1]}.{avs[2]}"

    backup_data = json.loads(backup_gsettings())
    ss = {}
    # 隐藏敏感信息
    for k, v in backup_data.items():
        if "server-sk-" in k:
            v = "******"
        ss[k] = v
    s += "\n\n******* config *******\n"
    s += json.dumps(ss, indent=4, ensure_ascii=False)
    s += "\n************"

    s += "\n\n******* debug log *******\n"
    s += get_log_handler().get_logs()

    s += "\n\n******* other *******\n"
    s += get_os_release()
    return s
