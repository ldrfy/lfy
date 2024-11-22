'工具'
import hashlib
import re


# pylint: disable=E1101
def process_text(text):
    """文本预处理

    Args:
        text (str): _description_

    Returns:
        str: _description_
    """
    # 删除空行
    s_from = re.sub(r'\n\s*\n', '\n', text)
    # 删除多余空格
    s_from = re.sub(r' +', ' ', s_from)
    # 删除所有换行，除了句号后面的换行
    s_from = re.sub(r"-[\n|\r]+", "", s_from)
    s_from = re.sub(r"(?<!\.|-|。)[\n|\r]+", " ", s_from)
    return s_from


def s2ks(s):
    """_summary_

    Args:
        s (_type_): _description_

    Returns:
        _type_: _description_
    """
    if "|" not in s:
        return None, None

    [app_id, secret_key] = s.split("|")
    a = app_id.strip()
    b = secret_key.strip()
    return a, b


def is_text(cf):
    """cb.get_formats()

    Args:
        cf (GdkContentFormats): Gdk.Clipboard.get_formats

    Returns:
        _type_: _description_
    """
    if cf.contain_mime_type("text/plain") \
        or cf.contain_mime_type("text/html") \
            or cf.contain_mime_type("text/plain;charset=utf-8"):
        return True
    return False


def cal_md5(file_path):
    """md5测试

    Args:
        file_path (_type_): _description_

    Returns:
        _type_: _description_
    """
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as file:
        # 以二进制方式读取文件内容
        # 较大的文件可以分块读取，以避免一次性加载整个文件到内存中
        for chunk in iter(lambda: file.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def get_os_release():
    """版本信息

    Returns:
        _type_: _description_
    """
    try:
        with open("/etc/os-release", "r", encoding="utf8") as f:
            return f.read()
    except FileNotFoundError:
        return "OS release info not found"
