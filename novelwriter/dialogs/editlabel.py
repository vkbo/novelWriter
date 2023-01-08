"""
novelWriter – Edit Label Dialog
===============================
A simple dialog for editing a label

File History:
Created: 2022-06-11 [2.0rc1]

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import novelwriter

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel, QDialogButtonBox, QHBoxLayout
)

logger = logging.getLogger(__name__)


class GuiEditLabel(QDialog):

    def __init__(self, parent, text=""):
        super().__init__(parent=parent)

        self.setObjectName("GuiEditLabel")
        self.setWindowTitle(self.tr("Item Label"))

        mVd = novelwriter.CONFIG.pxInt(220)
        mSp = novelwriter.CONFIG.pxInt(12)

        # Item Label
        self.labelValue = QLineEdit()
        self.labelValue.setMinimumWidth(mVd)
        self.labelValue.setMaxLength(200)
        self.labelValue.setText(text)
        self.labelValue.selectAll()

        # Buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # Assemble
        self.innerBox = QHBoxLayout()
        self.innerBox.addWidget(QLabel(self.tr("Label")), 0)
        self.innerBox.addWidget(self.labelValue, 1)
        self.innerBox.setSpacing(mSp)

        self.outerBox = QVBoxLayout()
        self.outerBox.setSpacing(mSp)
        self.outerBox.addLayout(self.innerBox, 1)
        self.outerBox.addWidget(self.buttonBox, 0)

        self.setLayout(self.outerBox)

        return

    @property
    def itemLabel(self):
        return self.labelValue.text()

    @classmethod
    def getLabel(cls, parent, text):
        cls = GuiEditLabel(parent, text=text)
        cls.exec_()
        return cls.itemLabel, cls.result() == QDialog.Accepted

# END Class GuiEditLabel
