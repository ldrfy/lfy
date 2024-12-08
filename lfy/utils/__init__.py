'工具'
import hashlib
import os
import re
import sys
from gettext import gettext as _

from lfy import APP_ID, APP_NAME
from lfy.utils.debug import get_logger


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


def s2ks(sk):
    """_summary_

    Args:
        s (_type_): _description_

    Returns:
        _type_: _description_
    """
    if not sk or "|" not in sk:
        return None, None
    if r'\s+\|\s+' in sk:
        sk = clear_key(sk)

    [app_id, secret_key] = sk.split("|")
    return app_id, secret_key


def clear_key(sk, str_new="|"):
    """清楚设置中的空格

    Args:
        s (_type_): _description_

    Returns:
        _type_: _description_
    """
    return re.sub(r'\s*\|\s*', str_new, sk.strip())


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


def get_cache_dir():
    """缓存目录

    Raises:
        EnvironmentError: _description_

    Returns:
        _type_: _description_
    """
    # 判断操作系统是否为Windows
    if sys.platform.startswith('win'):
        # 如果是Windows，使用环境变量获取缓存目录
        cache_dir = os.getenv('LOCALAPPDATA') or os.getenv('APPDATA')
        if cache_dir is None:
            raise EnvironmentError(
                "Cannot determine the cache directory for Windows.")
        cache_dir = os.path.join(cache_dir, APP_ID)
    else:
        # 对于其他操作系统，例如Linux和macOS，通常使用XDG Base Directory Specification
        xdg_cache_home = os.getenv('XDG_CACHE_HOME')
        if xdg_cache_home is None:
            home = os.path.expanduser("~")
            xdg_cache_home = os.path.join(home, '.cache')
        cache_dir = os.path.join(xdg_cache_home, APP_ID)

    # 确保缓存目录存在
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    return cache_dir


def get_cache_img_path():
    """_summary_
    """
    return os.path.join(get_cache_dir(), f"{APP_NAME}.png")


def gen_img(text="success"):
    """生成图片，TODO:这里应该生成需要语言字体的文字，现在有问题

    Args:
        text (str, optional): _description_. Defaults to "success".
    """
    from PIL import Image, ImageDraw, ImageFont  # pylint: disable=C0415

    w, h = 256, 128
    # 创建一个白色背景的图片 (宽1024px，高1024px)
    img = Image.new('RGB', (w, h), color='white')

    # 创建一个绘图对象
    d = ImageDraw.Draw(img)

    # 使用 Pillow 自带的默认字体
    font = ImageFont.load_default(60)

    # 定义文本
    text = "success"

    # 使用 textbbox 计算文本的边界框，返回 (left, top, right, bottom)
    text_bbox = d.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # 将文本居中
    position = ((w - text_width) // 2, (h - text_height) // 2)

    # 在图片上添加文本，设置颜色为绿色
    d.text(position, text, fill=(0, 128, 0), font=font)

    # 保存图片
    path = get_cache_img_path()
    img.save(path)
    return path


def check_lib_installed(library_name):
    """某个库是否被安装

    Args:
        library_name (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        __import__(library_name)
        return True
    except ImportError:
        return False


def check_libs(py_libs):
    """_summary_

    Args:
        py_libs (_type_): _description_

    Returns:
        _type_: _description_
    """
    if not py_libs:
        return None
    no_libs = [py_lib for py_lib in py_libs
               if not check_lib_installed(py_lib)]
    if no_libs:
        s = _("please install python whl: {}")\
            .format(",".join(no_libs))
        get_logger().error(s)
        return s
    return None
