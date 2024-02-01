"""
novelWriter – Custom Widget: Status LED
=======================================

File History:
Created: 2020-05-17 [0.5.1]

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

from typing import Literal

from PyQt5.QtGui import QColor, QPaintEvent, QPainter
from PyQt5.QtWidgets import QAbstractButton, QWidget

logger = logging.getLogger(__name__)


class StatusLED(QAbstractButton):

    S_NONE = 0
    S_BAD  = 1
    S_GOOD = 2

    def __init__(self, colNone: QColor, colGood: QColor, colBad: QColor,
                 sW: int, sH: int, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)

        self._colNone = colNone
        self._colGood = colGood
        self._colBad = colBad
        self._theCol = colNone

        self.setFixedWidth(sW)
        self.setFixedHeight(sH)

        return

    def setState(self, state: Literal[0, 1, 2]) -> None:
        """Set the colour state."""
        if state == self.S_GOOD:
            self._theCol = self._colGood
        elif state == self.S_BAD:
            self._theCol = self._colBad
        else:
            self._theCol = self._colNone
        self.update()
        return

    def paintEvent(self, event: QPaintEvent) -> None:
        """Draw the LED."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(self.palette().dark().color())
        painter.setBrush(self._theCol)
        painter.setOpacity(1.0)
        painter.drawEllipse(1, 1, self.width() - 2, self.height() - 2)
        return

# END Class StatusLED
