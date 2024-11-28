'自定义部件'
import os
import time

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QComboBox, QLineEdit

from lfy import APP_ID

os.environ[f'{APP_ID}.ui'] = 'qt'


class MyThread(QThread):
    """异步线程

    Args:
        QThread (_type_): _description_
    """
    signal = pyqtSignal(tuple)

    def __init__(self, fun, param=None):
        self.fun = fun
        self.param = param
        super().__init__()

    def run(self):
        """_summary_
        """
        start_ = time.time()
        result = self.fun(self.param)

        span = 0.5 - (time.time() - start_)
        if span > 0:
            time.sleep(span)
        self.signal.emit(result)

    def clean_up(self):
        """放置内存泄漏
        """
        self.quit()  # 确保线程正常退出
        self.wait()   # 等待线程结束
        self.deleteLater()  # 删除线程，释放资源


class CheckableComboBox(QComboBox):
    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)

        # 设置 LineEdit 为只读，显示选中项
        self.setLineEdit(QLineEdit())
        self.lineEdit().setReadOnly(True)
        self.view().pressed.connect(self.handleItemPressed)  # 监听按下事件

    def addCheckableItems(self, texts, cs=None):
        """添加带复选框的条目

        Args:
            texts (_type_): _description_
            cs (_type_, optional): _description_. Defaults to None.
        """
        if cs is None or len(cs) != len(texts):
            cs = [False] * len(texts)
        for c, text in zip(cs, texts):
            super().addItem(text)
            item = self.model().item(self.count() - 1, 0)
            item.setFlags(Qt.ItemFlag.ItemIsUserCheckable |
                          Qt.ItemFlag.ItemIsEnabled)
            if c:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)  # 默认未选中
            item.setToolTip(text)
        self.updateLineEdit()

    def handleItemPressed(self, index):
        """处理点击事件，切换复选框的状态"""
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Unchecked)
        else:
            item.setCheckState(Qt.CheckState.Checked)
        self.updateLineEdit()

    def updateLineEdit(self):
        """更新 QLineEdit 显示内容"""
        self.lineEdit().setText(self.checkedItemsStr())

    def checkedItems(self):
        """获取选中条目的文本列表"""
        return [self.itemText(i) for i in range(self.count()) if self.ifChecked(i)]

    def checkedItemsStr(self):
        """获取选中条目的拼接字符串"""
        return ';'.join(self.checkedItems()).strip(';')

    def ifChecked(self, index):
        """判断某条目是否被选中"""
        item = self.model().item(index, 0)
        return item.checkState() == Qt.CheckState.Checked
