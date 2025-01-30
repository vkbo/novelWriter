"""
novelWriter – Custom Widget: Status LED
=======================================

File History:
Created: 2020-05-17 [0.5.1]

This file is a part of novelWriter
Copyright (C) 2020 Veronica Berglyd Olsen and novelWriter contributors

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

from PyQt5.QtGui import QColor, QPainter, QPaintEvent
from PyQt5.QtWidgets import QAbstractButton, QWidget

from novelwriter import CONFIG
from novelwriter.types import QtBlack, QtPaintAntiAlias

logger = logging.getLogger(__name__)


class StatusLED(QAbstractButton):

    __slots__ = (
        "_neutral", "_postitve", "_negative", "_color", "_state", "_bPx"
    )

    def __init__(self, sW: int, sH: int, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self._neutral = QtBlack
        self._postitve = QtBlack
        self._negative = QtBlack
        self._color = QtBlack
        self._state = None
        self._bPx = CONFIG.pxInt(1)
        self.setFixedWidth(sW)
        self.setFixedHeight(sH)
        return

    @property
    def state(self) -> bool | None:
        """The current state of the LED."""
        return self._state

    def setColors(self, neutral: QColor, positive: QColor, negative: QColor) -> None:
        """Set the three colours for the status values."""
        self._neutral = neutral
        self._postitve = positive
        self._negative = negative
        self.setState(self._state)
        return

    def setState(self, state: bool | None) -> None:
        """Set the colour state."""
        if state is True:
            self._color = self._postitve
        elif state is False:
            self._color = self._negative
        else:
            self._color = self._neutral
        self._state = state
        self.update()
        return

    def paintEvent(self, event: QPaintEvent) -> None:
        """Draw the LED."""
        painter = QPainter(self)
        painter.setRenderHint(QtPaintAntiAlias, True)
        painter.setPen(self.palette().windowText().color())
        painter.setBrush(self._color)
        painter.setOpacity(1.0)
        painter.drawEllipse(
            self._bPx, self._bPx,
            self.width() - 2*self._bPx,
            self.height() - 2*self._bPx
        )
        return
