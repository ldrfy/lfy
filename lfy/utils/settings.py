import os

from lfy import APP_ID, APP_NAME


class Settings:
    """qt gtk 设置
    """
    def __init__(self, qt=None):
        if qt is None:
            qt = os.environ.get(f'{APP_ID}.ui') == 'qt'

        self.qt = qt
        self.ss = None

        super().__init__()

    def init_sg(self):
        if self.ss is not None:
            return
        if not self.qt:
            from gi.repository import Gio
            self.ss = Gio.Settings.new(APP_ID)
            return

        from PyQt6.QtCore import QSettings
        self.ss = QSettings(APP_ID, APP_NAME)

    def g(self, key, d=None, t=None):
        """读取

        Args:
            key (_type_): _description_
            d (_type_, optional): 默认. Defaults to None.

        Returns:
            _type_: _description_
        """

        self.init_sg()
        if not self.qt:
            return self.ss.get_value(key).unpack()
        if t is not None:
            return self.ss.value(key, d, type=t)

        v = self.ss.value(key, d)

        if v is None or not isinstance(v, str):
            return v
        if v in ["true", "True"]:
            return True
        if v in ["false", "False"]:
            return False
        try:
            return int(v)
        except ValueError:
            try:
                # 尝试转换为小数
                return float(v)
            except ValueError:
                return v

    def s(self, key, value):
        """保存

        Args:
            key (_type_): _description_
            value (_type_): _description_

        Raises:
            ValueError: _description_
        """
        self.init_sg()

        if not self.qt:
            from gi.repository import GLib

            if isinstance(value, str):
                self.ss.set_string(key, value)
            elif isinstance(value, bool):
                self.ss.set_boolean(key, value)
            elif isinstance(value, int):
                self.ss.set_int(key, value)
            elif isinstance(value, float):
                self.ss.set_double(key, value)
            elif isinstance(value, list):
                if all(isinstance(v, str) for v in value):
                    self.ss.set_value(key, GLib.Variant("as", value))
                elif all(isinstance(v, int) for v in value):
                    self.ss.set_value(key, GLib.Variant("ai", value))
                elif all(isinstance(v, float) for v in value):
                    self.ss.set_value(key, GLib.Variant("ad", value))
                else:
                    raise ValueError(
                        "Unsupported list type. Only list[str], list[int], and list[float].")
            else:
                # 对于其他类型，打包成 GLib.Variant 再存储
                self.ss.set_value(key, GLib.Variant.new_variant(value))
            return

        self.ss.setValue(key, value)
