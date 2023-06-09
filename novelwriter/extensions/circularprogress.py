"""
novelWriter – Custom Widget: Progress Circle
============================================

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
from __future__ import annotations

from math import ceil

from PyQt5.QtGui import QBrush, QColor, QPaintEvent, QPainter, QPen
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import QProgressBar, QSizePolicy, QWidget


class NProgressCircle(QProgressBar):
    """Extension: Circular Progress Widget

    A custom widget that paints a circular progress indicator instead of
    a straight bar. It is also possible to set custom text for iṫ.
    """

    __slots__ = (
        "_text", "_point", "_dRect", "_cRect", "_dPen", "_dBrush",
        "_cPen", "_bPen", "_tColor"
    )

    def __init__(self, parent: QWidget, size: int, point: int):
        super().__init__(parent=parent)
        self._text = None
        self._point = point
        self._dRect = QRect(0, 0, size, size)
        self._cRect = QRect(point, point, size - 2*point, size - 2*point)
        self._dPen = QPen(Qt.transparent)
        self._dBrush = QBrush(Qt.transparent)
        self.setColours(
            track=self.palette().alternateBase().color(),
            bar=self.palette().highlight().color(),
            text=self.palette().text().color()
        )
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedWidth(size)
        self.setFixedHeight(size)
        return

    def setColours(
        self, back: QColor | None = None, track: QColor | None = None,
        bar: QColor | None = None, text: QColor | None = None
    ):
        """Set the colours of the widget."""
        if isinstance(back, QColor):
            self._dPen = QPen(back)
            self._dBrush = QBrush(back)
        if isinstance(bar, QColor):
            self._cPen = QPen(QBrush(bar), self._point, Qt.SolidLine, Qt.RoundCap)
        if isinstance(track, QColor):
            self._bPen = QPen(QBrush(track), self._point, Qt.SolidLine, Qt.RoundCap)
        if isinstance(text, QColor):
            self._tColor = text
        return

    def setCentreText(self, text: str | None):
        """Replace the progress text with a custom string."""
        self._text = text
        self.setValue(self.value())  # Triggers a redraw
        return

    def paintEvent(self, event: QPaintEvent):
        """Custom painter for the progress bar."""
        progress = 100.0*self.value()/self.maximum()
        angle = ceil(16*3.6*progress)
        qPaint = QPainter(self)
        qPaint.setRenderHint(QPainter.Antialiasing, True)
        qPaint.setPen(self._dPen)
        qPaint.setBrush(self._dBrush)
        qPaint.drawEllipse(self._dRect)
        qPaint.setPen(self._bPen)
        qPaint.drawArc(self._cRect, 0, 360*16)
        qPaint.setPen(self._cPen)
        qPaint.drawArc(self._cRect, 90*16, -angle)
        qPaint.setPen(self._tColor)
        qPaint.drawText(self._cRect, Qt.AlignCenter, self._text or f"{progress:.1f} %")
        return

# END Class NProgressCircle
