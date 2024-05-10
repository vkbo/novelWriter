"""
novelWriter – Custom Widget: Switch Box
=======================================

File History:
Created: 2023-04-16 [2.1b1]

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

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QGridLayout, QLabel, QScrollArea, QWidget

from novelwriter.extensions.switch import NSwitch
from novelwriter.types import (
    QtAlignLeft, QtAlignRight, QtAlignRightMiddle, QtSizeMinimum,
    QtSizeMinimumExpanding
)


class NSwitchBox(QScrollArea):
    """Extension: Switch Box Widget

    A widget that can hold a list of switches with labels and optional
    icons. The switch toggles emits a common signal with a switch key.
    """

    switchToggled = pyqtSignal(str, bool)

    def __init__(self, parent: QWidget, baseSize: int) -> None:
        super().__init__(parent=parent)
        self._index = 0
        self._hSwitch = baseSize
        self._wSwitch = 2*self._hSwitch
        self._sIcon = baseSize
        self._widgets = []
        self.clear()
        return

    def clear(self) -> None:
        """Rebuild the content of the core widget."""
        self._index = 0
        self._widgets = []

        self._content = QGridLayout()
        self._content.setColumnStretch(1, 1)

        self._widget = QWidget(self)
        self._widget.setSizePolicy(QtSizeMinimumExpanding, QtSizeMinimum)
        self._widget.setLayout(self._content)

        self.setWidgetResizable(True)
        self.setWidget(self._widget)

        return

    def addLabel(self, text: str) -> None:
        """Add a header label to the content box."""
        label = QLabel(text, self)
        font = label.font()
        font.setBold(True)
        label.setFont(font)
        self._content.addWidget(label, self._index, 0, 1, 3, QtAlignLeft)
        self._widgets.append(label)
        self._bumpIndex()
        return

    def addItem(self, qIcon: QIcon, text: str, identifier: str, default: bool = False) -> None:
        """Add an item to the content box."""
        icon = QLabel("", self)
        icon.setAlignment(QtAlignRightMiddle)
        icon.setPixmap(qIcon.pixmap(self._sIcon, self._sIcon))
        self._content.addWidget(icon, self._index, 0, QtAlignLeft)

        label = QLabel(text, self)
        self._content.addWidget(label, self._index, 1, QtAlignLeft)

        switch = NSwitch(self, height=self._hSwitch)
        switch.setChecked(default)
        switch.toggled.connect(lambda state: self._emitSwitchSignal(identifier, state))
        self._content.addWidget(switch, self._index, 2, QtAlignRight)

        self._widgets.append(switch)
        self._bumpIndex()

        return

    def addSeparator(self) -> None:
        """Add a blank entry in the content box."""
        spacer = QWidget(self)
        spacer.setFixedHeight(int(0.5*self._sIcon))
        self._content.addWidget(spacer, self._index, 0, 1, 3, QtAlignLeft)
        self._widgets.append(spacer)
        self._bumpIndex()
        return

    ##
    #  Internal Functions
    ##

    def _emitSwitchSignal(self, identifier: str, state: bool) -> None:
        """Emit a signal for a switch toggle."""
        self.switchToggled.emit(identifier, state)
        return

    def _bumpIndex(self) -> None:
        """Increase the index counter and make sure only the last
        columns is stretching.
        """
        self._content.setRowStretch(self._index, 0)
        self._content.setRowStretch(self._index + 1, 1)
        self._index += 1
        return
