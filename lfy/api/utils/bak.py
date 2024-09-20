'备份和恢复配置'
import json
from gettext import gettext as _

from gi.repository import Gio, GLib

from lfy import APP_ID  # pylint: disable=E0611
from lfy.api.utils.debug import get_logger
from lfy.settings import Settings


def backup_gsettings():
    """备份数据
    """
    no_keys = []
    schema_source = Gio.SettingsSchemaSource.get_default()
    schema = schema_source.lookup(APP_ID, True)

    keys = schema.list_keys()
    settings = Settings.new()
    backup_data = {}

    for key in keys:
        if key in no_keys:
            continue
        value = settings.get_value(key).unpack()
        backup_data[key] = value

    # indent自动格式化
    # ensure_ascii 中文显示没问题
    return json.dumps(backup_data, indent=4, ensure_ascii=False)


def restore_gsettings(s):
    """载入数据

    Args:
        path (str, optional): _description_. Defaults to path_config_path.
    """

    try:
        backup_data = json.loads(s)
        settings = Settings.new()

        schema_source = Gio.SettingsSchemaSource.get_default()
        schema = schema_source.lookup(APP_ID, True)
        keys = schema.list_keys()
        error_keys = ""
        for key in backup_data.keys():
            if key not in keys:
                error_keys += key + " "
        if len(error_keys) > 0:
            return _("error with keys: ") + error_keys

        for key, value in backup_data.items():
            variant_type = settings.get_value(key).get_type_string()
            settings.set_value(key, GLib.Variant(variant_type, value))
        return ""

    except Exception as e:  # pylint: disable=W0718
        print(e)
        get_logger().error(e)
        return _('Please copy the configuration data in json format first')
