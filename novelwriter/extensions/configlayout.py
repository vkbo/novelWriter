"""
novelWriter – Custom Widget: Config Layout
==========================================
A custom grid layout for config pages

File History:
Created: 2020-05-03 [0.4.5]

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
from __future__ import annotations

from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAbstractButton, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QSizePolicy,
    QVBoxLayout, QWidget
)

from novelwriter import CONFIG

FONT_SCALE = 0.9


class NConfigLayout(QGridLayout):

    def __init__(self):
        super().__init__()

        self._nextRow = 0
        self._helpCol = QColor(0, 0, 0)
        self._fontScale = FONT_SCALE
        self._itemMap = {}

        wSp = CONFIG.pxInt(8)
        self.setHorizontalSpacing(wSp)
        self.setVerticalSpacing(wSp)
        self.setColumnStretch(0, 1)

        return

    ##
    #  Getters and Setters
    ##

    def setHelpTextStyle(self, color: QColor | list | tuple, fontScale: float = FONT_SCALE):
        """Set the text color for the help text."""
        if isinstance(color, QColor):
            self._helpCol = color
        else:
            self._helpCol = QColor(*color)
        self._fontScale = fontScale
        return

    def setHelpText(self, row: int, text: str):
        """Set the text for the help label."""
        if row in self._itemMap:
            qHelp = self._itemMap[row][1]
            if isinstance(qHelp, NHelpLabel):
                qHelp.setText(text)
        return

    def setLabelText(self, row: int, text: str):
        """Set the text for the main label."""
        if row in self._itemMap:
            self._itemMap[row](0).setText(text)
        return

    ##
    #  Class Methods
    ##

    def addGroupLabel(self, label: str):
        """Add a text label to separate groups of settings."""
        hM = CONFIG.pxInt(4)
        qLabel = QLabel("<b>%s</b>" % label)
        qLabel.setContentsMargins(0, hM, 0, hM)
        self.addWidget(qLabel, self._nextRow, 0, 1, 2, Qt.AlignLeft)
        self.setRowStretch(self._nextRow, 0)
        self.setRowStretch(self._nextRow + 1, 1)
        self._nextRow += 1
        return

    def addRow(
        self, label: str, widget: QWidget, helpText: str | None = None,
        unit: str | None = None, button: QWidget | None = None
    ) -> int:
        """Add a label and a widget as a new row of the grid."""
        wSp = CONFIG.pxInt(8)
        qLabel = QLabel(label)
        qLabel.setIndent(wSp)
        qLabel.setBuddy(widget)

        qHelp = None
        if helpText is not None:
            qHelp = NHelpLabel(str(helpText), self._helpCol, self._fontScale)
            qHelp.setIndent(wSp)
            labelBox = QVBoxLayout()
            labelBox.addWidget(qLabel)
            labelBox.addWidget(qHelp)
            labelBox.setSpacing(0)
            labelBox.addStretch(1)
            self.addLayout(labelBox, self._nextRow, 0, 1, 1, Qt.AlignLeft | Qt.AlignTop)
        else:
            self.addWidget(qLabel, self._nextRow, 0, 1, 1, Qt.AlignLeft | Qt.AlignTop)

        if isinstance(unit, str):
            controlBox = QHBoxLayout()
            controlBox.addWidget(widget, 0, Qt.AlignVCenter)
            controlBox.addWidget(QLabel(unit), 0, Qt.AlignVCenter)
            controlBox.setSpacing(wSp)
            self.addLayout(controlBox, self._nextRow, 1, 1, 1, Qt.AlignRight | Qt.AlignTop)

        elif isinstance(button, QAbstractButton):
            controlBox = QHBoxLayout()
            controlBox.addWidget(widget, 0, Qt.AlignVCenter)
            controlBox.addWidget(button, 0, Qt.AlignVCenter)
            controlBox.setSpacing(wSp)
            self.addLayout(controlBox, self._nextRow, 1, 1, 1, Qt.AlignRight | Qt.AlignTop)

        else:
            if isinstance(widget, QLineEdit):
                qLayout = QHBoxLayout()
                qLayout.addWidget(widget)
                self.addLayout(qLayout, self._nextRow, 1, 1, 1, Qt.AlignRight | Qt.AlignTop)
            else:
                self.addWidget(widget, self._nextRow, 1, 1, 1, Qt.AlignRight | Qt.AlignTop)

        self.setRowStretch(self._nextRow, 0)
        self.setRowStretch(self._nextRow+1, 1)

        self._itemMap[self._nextRow] = (qLabel, qHelp, widget)
        self._nextRow += 1

        return self._nextRow - 1

# END Class NConfigLayout


class NSimpleLayout(QGridLayout):
    """Similar to NConfigLayout, but only has a label + widget two
    column layout.
    """

    def __init__(self):
        super().__init__()
        self._nextRow = 0

        wSp = CONFIG.pxInt(8)
        self.setHorizontalSpacing(wSp)
        self.setVerticalSpacing(wSp)
        self.setColumnStretch(0, 1)

        return

    ##
    #  Methods
    ##

    def addGroupLabel(self, label: str):
        """Add a text label to separate groups of settings."""
        hM = CONFIG.pxInt(4)
        qLabel = QLabel("<b>%s</b>" % label)
        qLabel.setContentsMargins(0, hM, 0, hM)
        self.addWidget(qLabel, self._nextRow, 0, 1, 2, Qt.AlignLeft)
        self.setRowStretch(self._nextRow, 0)
        self.setRowStretch(self._nextRow + 1, 1)
        self._nextRow += 1
        return

    def addRow(self, label: str, widget: QWidget):
        """Add a label and a widget as a new row of the grid."""
        wSp = CONFIG.pxInt(8)
        qLabel = QLabel(label)
        qLabel.setIndent(wSp)
        self.addWidget(qLabel, self._nextRow, 0, 1, 1, Qt.AlignLeft | Qt.AlignTop)

        if isinstance(widget, QLineEdit):
            qLayout = QHBoxLayout()
            qLayout.addWidget(widget)
            self.addLayout(qLayout, self._nextRow, 1, 1, 1, Qt.AlignRight | Qt.AlignTop)
        else:
            self.addWidget(widget, self._nextRow, 1, 1, 1, Qt.AlignRight | Qt.AlignTop)

        qLabel.setBuddy(widget)

        self.setRowStretch(self._nextRow, 0)
        self.setRowStretch(self._nextRow+1, 1)
        self._nextRow += 1

        return

# END Class NSimpleLayout


class NHelpLabel(QLabel):

    def __init__(self, text: str, color: QColor | list | tuple, fontSize: float = FONT_SCALE):
        super().__init__(text)

        if isinstance(color, QColor):
            qCol = color
        else:
            qCol = QColor(*color)

        lblCol = self.palette()
        lblCol.setColor(QPalette.WindowText, qCol)
        self.setPalette(lblCol)

        lblFont = self.font()
        lblFont.setPointSizeF(fontSize*lblFont.pointSizeF())
        self.setFont(lblFont)

        self.setWordWrap(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return

# END Class NHelpLabel
