'提示'
from gi.repository import Gio

from lfy.settings import Settings


def nf_t(app, title, txt, id_str="translate_end"):
    """翻译以后提示

    Args:
        app (_type_): _description_
        title (str): _description_
        txt (str): _description_
        id_str (str, optional): _description_. Defaults to "translate_end".
    """
    if not Settings.get().notify_translation_results:
        return

    # 创建并发送通知
    notification = Gio.Notification.new(title)
    notification.set_body(txt)
    notification.set_icon(Gio.ThemedIcon.new("cool.ldr.lfy"))

    app.send_notification(id_str, notification)
