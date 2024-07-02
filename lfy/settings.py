'设置保存'
from gi.repository import Gio, GLib

from lfy import APP_ID  # pylint: disable=E0611


class Settings(Gio.Settings):
    """
    Dialect settings handler
    """

    instance = None

    def __init__(self, *args):
        super().__init__(*args)

    @staticmethod
    def new():
        """Create a new instance of Settings."""
        g_settings = Settings(APP_ID)
        return g_settings

    @staticmethod
    def get():
        """Return an active instance of Settings."""
        if Settings.instance is None:
            Settings.instance = Settings.new()
        return Settings.instance

    @property
    def server_selected_key(self):
        """选择翻译的服务的key

        Returns:
            str: 如：baidu
        """
        return self.get_string('server-selected-key')

    @server_selected_key.setter
    def server_selected_key(self, key):
        self.set_string('server-selected-key', key)

    @property
    def lang_selected_n(self):
        """选择翻译语言的n：0

        Returns:
            int: 如 3
        """
        return self.get_int('lang-selected-n')

    @lang_selected_n.setter
    def lang_selected_n(self, n):
        self.set_int('lang-selected-n', n)

    @property
    def server_sk_baidu(self):
        """选择翻译的服务密钥，只是一个字符串，自己解析和保存用 | 分割

        Returns:
            str: 如：baidu
        """
        return self.get_string('server-sk-baidu')

    @server_sk_baidu.setter
    def server_sk_baidu(self, key):
        self.set_string('server-sk-baidu', key)

    @property
    def server_sk_aliyun(self):
        """选择翻译的服务密钥，只是一个字符串，自己解析和保存用 | 分割

        Returns:
            str: 如：aliyun
        """
        return self.get_string('server-sk-aliyun')

    @server_sk_aliyun.setter
    def server_sk_aliyun(self, key):
        self.set_string('server-sk-aliyun', key)


    @property
    def server_sk_tencent(self):
        """选择翻译的服务密钥，只是一个字符串，自己解析和保存用 | 分割

        Returns:
            str: 如：tencent
        """
        return self.get_string('server-sk-tencent')

    @server_sk_tencent.setter
    def server_sk_tencent(self, key):
        self.set_string('server-sk-tencent', key)

    @property
    def vpn_addr_port(self):
        """代理地址

        Returns:
            str: 如：127.0.0.1:7890
        """
        return self.get_string('vpn-addr-port')

    @vpn_addr_port.setter
    def vpn_addr_port(self, key):
        self.set_string('vpn-addr-port', key)

    @property
    def window_size(self):
        """窗口大小

        Returns:
            _type_: _description_
        """
        value = self.get_value('window-size')
        return (value[0], value[1])

    @window_size.setter
    def window_size(self, size):
        width, height = size
        self.set_value('window-size', GLib.Variant('ai', [width, height]))

    @property
    def auto_check_update(self):
        """自动核对更新

        Returns:
            _type_: _description_
        """
        return self.get_boolean('auto-check-update')

    @property
    def color_scheme(self):
        """主题

        Returns:
            _type_: _description_
        """
        return self.get_string('color-scheme')

    @color_scheme.setter
    def color_scheme(self, scheme):
        self.set_string('color-scheme', scheme)
