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

import logging
import novelwriter

from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGridLayout, QHBoxLayout, QLabel, QLineEdit, QSizePolicy, QVBoxLayout,
    QWidget
)

logger = logging.getLogger(__name__)


class NConfigLayout(QGridLayout):

    def __init__(self):
        super().__init__()

        self._nextRow = 0
        self._helpCol = QColor(0, 0, 0)
        self._fontScale = 0.9

        self._itemMap = {}

        wSp = novelwriter.CONFIG.pxInt(8)
        self.setHorizontalSpacing(wSp)
        self.setVerticalSpacing(wSp)
        self.setColumnStretch(0, 1)

        return

    ##
    #  Getters and Setters
    ##

    def setHelpTextStyle(self, helpCol, fontScale=0.9):
        """Set the text color for the help text.
        """
        if isinstance(helpCol, QColor):
            self._helpCol = helpCol
        else:
            self._helpCol = QColor(*helpCol)
        self._fontScale = fontScale
        return

    def setHelpText(self, intRow, theText):
        """Set the text for the help label.
        """
        if intRow in self._itemMap:
            self._itemMap[intRow]["help"].setText(theText)
        return

    def setLabelText(self, intRow, theText):
        """Set the text for the main label.
        """
        if intRow in self._itemMap:
            self._itemMap[intRow]["label"].setText(theText)
        return

    ##
    #  Class Methods
    ##

    def addGroupLabel(self, theLabel):
        """Adds a text label to separate groups of settings.
        """
        if isinstance(theLabel, QLabel):
            qLabel = theLabel
        elif isinstance(theLabel, str):
            qLabel = QLabel("<b>%s</b>" % theLabel)
        else:
            qLabel = None
            raise ValueError("theLabel must be a QLabel")

        hM = novelwriter.CONFIG.pxInt(4)
        qLabel.setContentsMargins(0, hM, 0, hM)
        self.addWidget(qLabel, self._nextRow, 0, 1, 2, Qt.AlignLeft)

        self.setRowStretch(self._nextRow, 0)
        self.setRowStretch(self._nextRow + 1, 1)

        self._nextRow += 1

        return

    def addRow(self, theLabel, theWidget, helpText=None, theUnit=None, theButton=None):
        """Add a label and a widget as a new row of the grid.
        """
        thisEntry = {
            "label": None,
            "help": None,
            "widget": None,
        }

        if isinstance(theLabel, QLabel):
            qLabel = theLabel
        elif isinstance(theLabel, str):
            qLabel = QLabel(theLabel)
        else:
            qLabel = None
            raise ValueError("theLabel must be a QLabel")

        if isinstance(theWidget, QWidget):
            qWidget = theWidget
        else:
            qWidget = None
            raise ValueError("theWidget must be a QWidget")

        wSp = novelwriter.CONFIG.pxInt(8)
        qLabel.setIndent(wSp)
        if helpText is not None:
            qHelp = NHelpLabel(str(helpText), self._helpCol, self._fontScale)
            qHelp.setIndent(wSp)

            labelBox = QVBoxLayout()
            labelBox.addWidget(qLabel)
            labelBox.addWidget(qHelp)
            labelBox.setSpacing(0)
            labelBox.addStretch(1)

            thisEntry["help"] = qHelp
            self.addLayout(labelBox, self._nextRow, 0, 1, 1, Qt.AlignLeft | Qt.AlignTop)

        else:
            self.addWidget(qLabel, self._nextRow, 0, 1, 1, Qt.AlignLeft | Qt.AlignTop)

        if theUnit is not None:
            controlBox = QHBoxLayout()
            controlBox.addWidget(qWidget, 0, Qt.AlignVCenter)
            controlBox.addWidget(QLabel(theUnit), 0, Qt.AlignVCenter)
            controlBox.setSpacing(wSp)
            self.addLayout(controlBox, self._nextRow, 1, 1, 1, Qt.AlignRight | Qt.AlignTop)

        elif theButton is not None:
            controlBox = QHBoxLayout()
            controlBox.addWidget(qWidget, 0, Qt.AlignVCenter)
            controlBox.addWidget(theButton, 0, Qt.AlignVCenter)
            controlBox.setSpacing(wSp)
            self.addLayout(controlBox, self._nextRow, 1, 1, 1, Qt.AlignRight | Qt.AlignTop)

        else:
            if isinstance(theWidget, QLineEdit):
                qLayout = QHBoxLayout()
                qLayout.addWidget(theWidget)
                self.addLayout(qLayout, self._nextRow, 1, 1, 1, Qt.AlignRight | Qt.AlignTop)
            else:
                self.addWidget(qWidget, self._nextRow, 1, 1, 1, Qt.AlignRight | Qt.AlignTop)

        qLabel.setBuddy(qWidget)

        self.setRowStretch(self._nextRow, 0)
        self.setRowStretch(self._nextRow+1, 1)

        thisEntry["label"] = qLabel
        thisEntry["widget"] = qWidget

        self._itemMap[self._nextRow] = thisEntry

        self._nextRow += 1

        return self._nextRow - 1

# END Class NConfigLayout


class NHelpLabel(QLabel):

    def __init__(self, theText, textCol, fontSize=0.9):
        super().__init__(theText)

        if isinstance(textCol, QColor):
            qCol = textCol
        else:
            qCol = QColor(*textCol)

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
