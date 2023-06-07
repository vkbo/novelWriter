"""
novelWriter – Custom Widget: ProgressCircle
===========================================

File History:
Created: 2023-06-07 [2.1b1]

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

from math import ceil

from PyQt5.QtGui import QPaintEvent, QPainter, QPen
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import QProgressBar, QSizePolicy, QWidget


class NProgressCircle(QProgressBar):

    __slots__ = ("_mPx", "_bPen", "_cPen", "_cRect", "_tColor")

    def __init__(self, parent: QWidget, size: int, point: int):
        super().__init__(parent=parent)
        self._mPx = point
        self._bPen = QPen(self.palette().alternateBase(), point, Qt.SolidLine, Qt.RoundCap)
        self._cPen = QPen(self.palette().highlight(), point, Qt.SolidLine, Qt.RoundCap)
        self._cRect = QRect(point, point, size - 2*point, size - 2*point)
        self._tColor = self.palette().text().color()
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedWidth(size)
        self.setFixedHeight(size)
        return

    def paintEvent(self, event: QPaintEvent):
        """Custom painter for the progress bar."""
        progress = 100.0*self.value()/self.maximum()
        angle = ceil(16*3.6*progress)
        qPaint = QPainter(self)
        qPaint.setRenderHint(QPainter.Antialiasing, True)
        qPaint.setPen(self._bPen)
        qPaint.drawArc(self._cRect, 0, 360*16)
        qPaint.setPen(self._cPen)
        qPaint.drawArc(self._cRect, 90*16, -angle)
        qPaint.setPen(self._tColor)
        qPaint.drawText(self._cRect, Qt.AlignCenter, f"{progress:.1f} %")
        return

# END Class NProgressCircle
