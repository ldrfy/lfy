'提示'
from gi.repository import Gio

from lfy import APP_ID
from lfy.api.utils.settings import Settings


def nf_t(app, title, txt, id_str="translate_end"):
    """翻译以后提示

    Args:
        app (_type_): _description_
        title (str): _description_
        txt (str): _description_
        id_str (str, optional): _description_. Defaults to "translate_end".
    """
    if not Settings().g("notify-translation-results"):
        return

    # 创建并发送通知
    notification = Gio.Notification.new(title)
    notification.set_body(txt)
    notification.set_icon(Gio.ThemedIcon.new(APP_ID))

    app.send_notification(id_str, notification)
