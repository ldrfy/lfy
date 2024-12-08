'备份和恢复配置'
import json
import os
from gettext import gettext as _

from lfy import APP_ID  # pylint: disable=E0611
from lfy.utils.debug import get_logger
from lfy.utils.settings import Settings


def backup_gsettings(qt=None):
    """备份数据
    """

    if qt is None:
        qt = os.environ.get(f'{APP_ID}.ui') == 'qt'

    backup_data = {}
    sg = Settings()

    if qt:
        sg.init_sg()
        keys = sg.ss.allKeys()
    else:
        from gi.repository import Gio  # pylint: disable=C0415
        keys = Gio.SettingsSchemaSource.get_default()\
            .lookup(APP_ID, True).list_keys()

    backup_data = {key: sg.g(key) for key in keys}

    # indent自动格式化
    # ensure_ascii 中文显示没问题
    return json.dumps(backup_data, indent=4, ensure_ascii=False)


def restore_gsettings(s, qt=None):
    """载入数据

    Args:
        path (str, optional): _description_. Defaults to path_config_path.
    """

    try:
        if qt is None:
            qt = os.environ.get(f'{APP_ID}.ui') == 'qt'
        backup_data = json.loads(s)
        ss = Settings()

        if not qt:
            from gi.repository import Gio  # pylint: disable=C0415
            keys = Gio.SettingsSchemaSource.get_default()\
                .lookup(APP_ID, True).list_keys()
            error_keys = ""
            for key in backup_data.keys():
                if key not in keys:
                    error_keys += key + " "
            if len(error_keys) > 0:
                return _("error with keys: ") + error_keys

        for key, value in backup_data.items():
            ss.s(key, value)
        return ""

    except Exception as e:  # pylint: disable=W0718
        get_logger().error(e)
        return _('Please copy the configuration data in json format first')
