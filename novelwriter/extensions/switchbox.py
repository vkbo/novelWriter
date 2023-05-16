"""
novelWriter – Custom Widget: Switch Box
=======================================
A box of icons, labels and switches

File History:
Created: 2023-04-16 [2.1b1]

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

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QGridLayout, QLabel, QScrollArea, QSizePolicy, QWidget

from novelwriter.extensions.switch import NSwitch


class NSwitchBox(QScrollArea):

    switchToggled = pyqtSignal(str, bool)

    def __init__(self, parent, baseSize):
        super().__init__(parent=parent)

        self._index = 0
        self._hSwitch = baseSize
        self._wSwitch = 2*self._hSwitch
        self._sIcon = baseSize

        self.clear()

        return

    def clear(self):
        """Rebuild the content of the core widget.
        """
        self._content = QGridLayout()
        self._content.setColumnStretch(1, 1)

        self._widget = QWidget()
        self._widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self._widget.setLayout(self._content)

        self.setWidgetResizable(True)
        self.setWidget(self._widget)

        return

    def addLabel(self, text):
        """Add a header label to the content box.
        """
        label = QLabel(text)
        font = label.font()
        font.setBold(True)
        label.setFont(font)
        self._content.addWidget(label, self._index, 0, 1, 3, Qt.AlignLeft)
        self._bumpIndex()
        return

    def addItem(self, qIcon, text, identifier, default=False):
        """Add an item to the content box.
        """
        icon = QLabel("")
        icon.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        icon.setPixmap(qIcon.pixmap(self._sIcon, self._sIcon))
        self._content.addWidget(icon, self._index, 0, Qt.AlignLeft)

        label = QLabel(text)
        self._content.addWidget(label, self._index, 1, Qt.AlignLeft)

        switch = NSwitch(width=self._wSwitch, height=self._hSwitch)
        switch.setChecked(default)
        switch.toggled.connect(lambda state: self._emitSwitchSignal(identifier, state))
        self._content.addWidget(switch, self._index, 2, Qt.AlignRight)

        self._bumpIndex()

        return

    def addSeparator(self):
        """Add a blank entry in the content box.
        """
        spacer = QWidget()
        spacer.setFixedHeight(int(0.5*self._sIcon))
        self._content.addWidget(spacer, self._index, 0, 1, 3, Qt.AlignLeft)
        self._bumpIndex()
        return

    ##
    #  Internal Functions
    ##

    def _emitSwitchSignal(self, identifier, state):
        """Emit a signal for a switch toggle.
        """
        self.switchToggled.emit(identifier, state)
        return

    def _bumpIndex(self):
        """Increase the index counter and make sure only the last
        columns is stretcing.
        """
        self._content.setRowStretch(self._index, 0)
        self._content.setRowStretch(self._index + 1, 1)
        self._index += 1
        return

# END Class NSwitchBox
