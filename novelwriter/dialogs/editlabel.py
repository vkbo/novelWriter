"""
novelWriter – Edit Label Dialog
===============================

File History:
Created: 2022-06-11 [2.0rc1] GuiEditLabel

This file is a part of novelWriter
Copyright (C) 2022 Veronica Berglyd Olsen and novelWriter contributors

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

from PyQt6.QtWidgets import QDialogButtonBox, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from novelwriter.extensions.modified import NDialog
from novelwriter.types import QtAccepted, QtDialogCancel, QtDialogOk

logger = logging.getLogger(__name__)


class GuiEditLabel(NDialog):

    def __init__(self, parent: QWidget, text: str = "") -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiEditLabel")
        self.setObjectName("GuiEditLabel")
        self.setWindowTitle(self.tr("Item Label"))

        # Item Label
        self.edtValue = QLineEdit(self)
        self.edtValue.setMinimumWidth(220)
        self.edtValue.setMaxLength(200)
        self.edtValue.setText(text)
        self.edtValue.selectAll()

        self.lblValue = QLabel(self.tr("Label"), self)
        self.lblValue.setBuddy(self.lblValue)

        # Buttons
        self.buttonBox = QDialogButtonBox(QtDialogOk | QtDialogCancel, self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # Assemble
        self.innerBox = QHBoxLayout()
        self.innerBox.addWidget(self.lblValue, 0)
        self.innerBox.addWidget(self.edtValue, 1)
        self.innerBox.setSpacing(12)

        self.outerBox = QVBoxLayout()
        self.outerBox.setSpacing(12)
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
        return self.edtValue.text()

    @classmethod
    def getLabel(cls, parent: QWidget, text: str) -> tuple[str, bool]:
        """Pop the dialog and return the result."""
        dialog = cls(parent, text=text)
        dialog.exec()
        label = dialog.itemLabel
        accepted = dialog.result() == QtAccepted
        dialog.softDelete()
        return label, accepted
