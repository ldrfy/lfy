import json
import os
import shutil
from pathlib import Path

CONFIG_DATA = None
CONFIG_FILE_NAME = "config.json"

HOME_PATH = os.getenv("SUDO_HOME")
if HOME_PATH is None:
    HOME_PATH = os.getenv("HOME")

DESKTOP_NAME = "ldr-translate.desktop"

DIR_CONFIG = HOME_PATH + "/.config"

AUTOSTART_DIR = DIR_CONFIG + '/autostart'

DESKTOP_PATH = ""
AUTOSTART_PATH = f"{AUTOSTART_DIR}/cool.ldr.lt.desktop"

APP_USER_DIR = DIR_CONFIG + "/ldr-translate"
CONFIG_HOME_PATH = APP_USER_DIR + "/" + CONFIG_FILE_NAME


CONFIG_SECTIONS_SETTING = "setting"


def get_this_config_data():
    """_summary_

    Returns:
        _type_: _description_
    """
    return json.load(open(CONFIG_HOME_PATH, "r", encoding='utf-8'))


def get_config_data():
    """_summary_

    Returns:
        _type_: _description_
    """
    global CONFIG_DATA
    if CONFIG_DATA is None:
        if not os.path.exists(CONFIG_HOME_PATH):
            CONFIG_DATA = json.load(
                open(CONFIG_FILE_NAME, "r", encoding='utf-8'))
        else:
            CONFIG_DATA = json.load(
                open(CONFIG_HOME_PATH, "r", encoding='utf-8'))
    return CONFIG_DATA


def get_value(section, key):
    """_summary_

    Args:
        section (_type_): _description_
        key (_type_): _description_

    Returns:
        _type_: _description_
    """
    get_config_data()
    try:
        if section not in CONFIG_DATA:
            return get_this_config_data()[section][key]
        if key not in CONFIG_DATA[section]:
            return get_this_config_data()[section][key]
        return CONFIG_DATA[section][key]
    except KeyError as ex:
        print(ex)
        return None


def get_config_setting(key):
    """_summary_

    Args:
        key (_type_): _description_

    Returns:
        _type_: _description_
    """
    return get_value(CONFIG_SECTIONS_SETTING, key)


def set_config(section, key, value):
    """_summary_

    Args:
        section (_type_): _description_
        key (_type_): _description_
        value (_type_): _description_
    """
    global CONFIG_DATA
    get_config_data()
    CONFIG_DATA[section][key] = value
    check_dir(APP_USER_DIR)
    with open(CONFIG_HOME_PATH, 'w', encoding='utf8') as file:
        json.dump(CONFIG_DATA, file, ensure_ascii=False)


def check_dir(path):
    """核对文件夹

    Args:
        path (_type_): _description_
    """
    if not Path(path).exists():
        os.makedirs(path)


def set_del_wrapping(b: bool):
    """删除换行

    Args:
        b (bool): _description_

    Returns:
        _type_: _description_
    """
    return set_config(CONFIG_SECTIONS_SETTING, "del_wrapping", b)


def update_autostart(autostart):
    """开机自启

    Args:
        autostart (_type_): _description_
    """
    if not autostart:
        try:
            os.remove(AUTOSTART_PATH)
        except FileExistsError as e:
            print(e)
    else:
        try:
            if not os.path.exists(AUTOSTART_DIR):
                os.makedirs(AUTOSTART_DIR)
            shutil.copy(DESKTOP_PATH, AUTOSTART_PATH)
        except FileExistsError as ex:
            print(ex)


def get_autostart():
    """_summary_

    Returns:
        _type_: _description_
    """
    return os.path.exists(AUTOSTART_PATH)
