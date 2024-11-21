from gettext import gettext as _

from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDialog, QHBoxLayout, QMenu,
                             QTextEdit, QVBoxLayout)


class PreferenceWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(_("Settings"))
        self.setGeometry(200, 200, 400, 300)
        self.setModal(True)
        text_edit = QTextEdit(self)
        text_edit.setText(
            _("This is the settings window where you can configure application parameters."))
        text_edit.setReadOnly(False)
        layout = QVBoxLayout(self)
        layout.addWidget(text_edit)
