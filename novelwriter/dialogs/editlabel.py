"""
novelWriter – Edit Label Dialog
===============================

File History:
Created: 2022-06-11 [2.0rc1] GuiEditLabel

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

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
from __future__ import annotations

import logging

from PyQt5.QtWidgets import QDialogButtonBox, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from novelwriter import CONFIG
from novelwriter.extensions.modified import NDialog
from novelwriter.types import QtAccepted, QtDialogCancel, QtDialogOk

logger = logging.getLogger(__name__)


class GuiEditLabel(NDialog):

    def __init__(self, parent: QWidget, text: str = "") -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiEditLabel")
        self.setObjectName("GuiEditLabel")
        self.setWindowTitle(self.tr("Item Label"))

        mVd = CONFIG.pxInt(220)
        mSp = CONFIG.pxInt(12)

        # Item Label
        self.labelValue = QLineEdit(self)
        self.labelValue.setMinimumWidth(mVd)
        self.labelValue.setMaxLength(200)
        self.labelValue.setText(text)
        self.labelValue.selectAll()

        # Buttons
        self.buttonBox = QDialogButtonBox(QtDialogOk | QtDialogCancel, self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # Assemble
        self.innerBox = QHBoxLayout()
        self.innerBox.addWidget(QLabel(self.tr("Label"), self), 0)
        self.innerBox.addWidget(self.labelValue, 1)
        self.innerBox.setSpacing(mSp)

        self.outerBox = QVBoxLayout()
        self.outerBox.setSpacing(mSp)
        self.outerBox.addLayout(self.innerBox, 1)
        self.outerBox.addWidget(self.buttonBox, 0)

        self.setLayout(self.outerBox)

        logger.debug("Ready: GuiEditLabel")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiEditLabel")
        return

    @property
    def itemLabel(self) -> str:
        return self.labelValue.text()

    @classmethod
    def getLabel(cls, parent: QWidget, text: str) -> tuple[str, bool]:
        """Pop the dialog and return the result."""
        cls = GuiEditLabel(parent, text=text)
        cls.exec()
        label = cls.itemLabel
        accepted = cls.result() == QtAccepted
        cls.softDelete()
        return label, accepted
