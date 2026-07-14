"""
novelWriter – Custom Widget: Switch Box
=======================================

This file is a part of novelWriter
Copyright (C) 2023 Veronica Berglyd Olsen and novelWriter contributors

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
"""  # noqa

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QScrollArea, QWidget

from novelwriter import SHARED
from novelwriter.extensions.modified import NClipLabel
from novelwriter.extensions.switch import NSwitch
from novelwriter.types import QtAlignLeft, QtAlignRight, QtSizeExpanding, QtSizeMinimum


class NSwitchBox(QScrollArea):
    """Extension: Switch Box Widget.

    A widget that can hold a list of switches with labels and optional
    icons. The switch toggles emits a common signal with a switch key.
    """

    switchToggled = pyqtSignal(str, bool)

    def __init__(self, parent: QWidget, baseSize: int) -> None:
        super().__init__(parent=parent)
        self._index = 0
        self._hSwitch = baseSize
        self._wSwitch = 2 * self._hSwitch
        self._size = baseSize
        self._icons = {}
        self._labels = {}
        self._pixmaps = {}
        self._switches = {}
        self.clear()
        self.setFrameStyle(QFrame.Shape.NoFrame)

    ##
    #  State Methods
    ##

    def setSwitchState(self, state: dict[str, bool]) -> None:
        """Set the state of the switches in the box."""
        if isinstance(state, dict):  # pragma: no branch
            for identifier, value in state.items():
                if isinstance(switch := self._switches.get(identifier), NSwitch):  # pragma: no branch
                    switch.setChecked(bool(value))

    def getSwitchState(self) -> dict[str, bool]:
        """Get the state of the switches in the box."""
        state = {}
        for identifier, switch in self._switches.items():
            if isinstance(switch, NSwitch):  # pragma: no branch
                state[identifier] = switch.isChecked()
        return state

    def updateTheme(self) -> None:
        """Update the theme of the switches in the box."""
        for pix, name, color in self._icons.values():
            icon = SHARED.theme.getIcon(name, color)
            pix.setFixedSize(self._size, self._size)
            pix.setPixmap(icon.pixmap(self._size, self._size))

    ##
    #  Builder Methods
    ##

    def clear(self) -> None:
        """Rebuild the content of the core widget."""
        self._index = 0
        self._switches.clear()
        self._icons.clear()
        self._labels.clear()
        self._pixmaps.clear()

        self._content = QGridLayout()
        self._content.setColumnStretch(1, 1)

        self._widget = QWidget(self)
        self._widget.setSizePolicy(QtSizeExpanding, QtSizeMinimum)
        self._widget.setLayout(self._content)

        self.setWidgetResizable(True)
        self.setWidget(self._widget)

    def addLabel(self, text: str) -> None:
        """Add a header label to the content box."""
        label = NClipLabel(text, self)
        label.setFont(SHARED.theme.guiFontB)
        self._content.addWidget(label, self._index, 0, 1, 3, QtAlignLeft)
        self._bumpIndex()

    def addItem(
        self,
        text: str,
        identifier: str,
        *,
        icon: str | None = None,
        color: str = "default",
        default: bool = False,
    ) -> None:
        """Add an item to the content box. If the identifier is already
        in use, the existing entry is updated in place instead, which
        keeps its position and current switch state.
        """
        if switch := self._switches.get(identifier):
            if label := self._labels.get(identifier):  # pragma: no branch
                label.setText(text)
            if icon and (pixmap := self._pixmaps.get(identifier)):  # pragma: no branch
                qIcon = SHARED.theme.getIcon(icon, color)
                pixmap.setPixmap(qIcon.pixmap(self._size, self._size))
                self._icons[identifier] = (pixmap, icon, color)
            return

        if icon:  # pragma: no branch
            pixmap = QLabel("", self)
            qIcon = SHARED.theme.getIcon(icon, color)
            pixmap.setFixedSize(self._size, self._size)
            pixmap.setPixmap(qIcon.pixmap(self._size, self._size))
            self._icons[identifier] = (pixmap, icon, color)
            self._pixmaps[identifier] = pixmap
            self._content.addWidget(pixmap, self._index, 0, QtAlignLeft)

        label = NClipLabel(text, self)
        self._content.addWidget(label, self._index, 1, QtAlignLeft)
        self._labels[identifier] = label

        switch = NSwitch(self, height=self._hSwitch)
        switch.setChecked(default)
        switch.toggled.connect(lambda state: self._emitSwitchSignal(identifier, state))
        self._content.addWidget(switch, self._index, 2, QtAlignRight)

        label.setBuddy(switch)
        self._switches[identifier] = switch
        self._bumpIndex()

    def removeItem(self, identifier: str) -> None:
        """Remove an item from the content box, if it exists."""
        if switch := self._switches.pop(identifier, None):
            self._content.removeWidget(switch)
            switch.setParent(None)
        if label := self._labels.pop(identifier, None):
            self._content.removeWidget(label)
            label.setParent(None)
        if pixmap := self._pixmaps.pop(identifier, None):
            self._content.removeWidget(pixmap)
            pixmap.setParent(None)
        self._icons.pop(identifier, None)

    def addSeparator(self) -> None:
        """Add a blank entry in the content box."""
        spacer = QWidget(self)
        spacer.setFixedHeight(int(0.5 * self._size))
        self._content.addWidget(spacer, self._index, 0, 1, 3, QtAlignLeft)
        self._bumpIndex()

    ##
    #  Internal Functions
    ##

    def _emitSwitchSignal(self, identifier: str, state: bool) -> None:
        """Emit a signal for a switch toggle."""
        self.switchToggled.emit(identifier, state)

    def _bumpIndex(self) -> None:
        """Increase the index counter and make sure only the last
        columns is stretching.
        """
        self._content.setRowStretch(self._index, 0)
        self._content.setRowStretch(self._index + 1, 1)
        self._index += 1
