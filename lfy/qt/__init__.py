import time

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QPlainTextEdit


class MyPlainTextEdit(QPlainTextEdit):
    """禁止复制响应

    Args:
        QPlainTextEdit (_type_): _description_
    """
    def keyPressEvent(self, event):
        """内部的ctrl c不要响应

        Args:
            event (_type_): _description_
        """
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_C:
            print("no copy")
            event.accept()  # 阻止事件传播，防止触发 QClipboard 的复制
        else:
            super().keyPressEvent(event)


class MyThread(QThread):
    signal = pyqtSignal(tuple)

    def __init__(self, fun, param=None):
        self.fun = fun
        self.param = param
        super().__init__()

    def run(self):
        start_ = time.time()
        result = self.fun(self.param)

        span = 0.5 - (time.time() - start_)
        if span > 0:
            time.sleep(span)
        print(result)
        self.signal.emit(result)
