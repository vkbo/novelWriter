"""
novelWriter – GUI Components Module
===================================
A module of various small GUI components

File History:
Created: 2020-05-17 [0.5.1] StatusLED

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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

from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QAbstractButton

logger = logging.getLogger(__name__)


class StatusLED(QAbstractButton):

    S_NONE = 0
    S_BAD  = 1
    S_GOOD = 2

    def __init__(self, colNone, colGood, colBad, sW, sH, parent=None):
        super().__init__(parent=parent)

        self._colNone = colNone
        self._colGood = colGood
        self._colBad = colBad
        self._theCol = colNone

        self.setFixedWidth(sW)
        self.setFixedHeight(sH)

        return

    ##
    #  Setters
    ##

    def setState(self, theState):
        """Set the colour state.
        """
        if theState == self.S_GOOD:
            self._theCol = self._colGood
        elif theState == self.S_BAD:
            self._theCol = self._colBad
        else:
            self._theCol = self._colNone

        self.update()

        return

    ##
    #  Events
    ##

    def paintEvent(self, _):
        """Drawing the LED.
        """
        qPalette = self.palette()
        qPaint = QPainter(self)
        qPaint.setRenderHint(QPainter.Antialiasing, True)
        qPaint.setPen(qPalette.dark().color())
        qPaint.setBrush(self._theCol)
        qPaint.setOpacity(1.0)
        qPaint.drawEllipse(1, 1, self.width() - 2, self.height() - 2)
        return

# END Class StatusLED
