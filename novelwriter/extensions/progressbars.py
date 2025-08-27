"""
novelWriter – Custom Widget: Progress Bars
==========================================

File History:
Created: 2023-06-07 [2.1b1] NProgressCircle
Created: 2023-06-09 [2.1b1] NProgressSimple

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

from math import ceil

from PyQt6.QtCore import QRect
from PyQt6.QtGui import QBrush, QColor, QPainter, QPaintEvent, QPen
from PyQt6.QtWidgets import QProgressBar, QWidget

from novelwriter.types import (
    QtAlignCenter, QtPaintAntiAlias, QtRoundCap, QtSizeFixed, QtSolidLine,
    QtTransparent
)


class NProgressCircle(QProgressBar):
    """Extension: Circular Progress Widget.

    A custom widget that paints a circular progress indicator instead of
    a straight bar. It is also possible to set custom text for iṫ.
    """

    __slots__ = (
        "_bPen", "_cPen", "_cRect", "_dBrush", "_dPen", "_dRect", "_point",
        "_tColor", "_text",
    )

    def __init__(self, parent: QWidget, size: int, point: int) -> None:
        super().__init__(parent=parent)
        self._text = None
        self._point = point
        self._dRect = QRect(0, 0, size, size)
        self._cRect = QRect(point, point, size - 2*point, size - 2*point)
        self._dPen = QPen(QtTransparent)
        self._dBrush = QBrush(QtTransparent)
        self.setColors(
            track=self.palette().alternateBase().color(),
            bar=self.palette().highlight().color(),
            text=self.palette().text().color()
        )
        self.setSizePolicy(QtSizeFixed, QtSizeFixed)
        self.setFixedWidth(size)
        self.setFixedHeight(size)

    def setColors(
        self, back: QColor | None = None, track: QColor | None = None,
        bar: QColor | None = None, text: QColor | None = None
    ) -> None:
        """Set the colours of the widget."""
        if isinstance(back, QColor):
            self._dPen = QPen(back)
            self._dBrush = QBrush(back)
        if isinstance(bar, QColor):
            self._cPen = QPen(QBrush(bar), self._point, QtSolidLine, QtRoundCap)
        if isinstance(track, QColor):
            self._bPen = QPen(QBrush(track), self._point, QtSolidLine, QtRoundCap)
        if isinstance(text, QColor):
            self._tColor = text

    def setCentreText(self, text: str | None) -> None:
        """Replace the progress text with a custom string."""
        self._text = text
        self.setValue(self.value())  # Triggers a redraw

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the progress bar."""
        progress = 100.0*self.value()/self.maximum()
        angle = ceil(16*3.6*progress)
        painter = QPainter(self)
        painter.setRenderHint(QtPaintAntiAlias, True)
        painter.setPen(self._dPen)
        painter.setBrush(self._dBrush)
        painter.drawEllipse(self._dRect)
        painter.setPen(self._bPen)
        painter.drawArc(self._cRect, 0, 360*16)
        painter.setPen(self._cPen)
        painter.drawArc(self._cRect, 90*16, -angle)
        painter.setPen(self._tColor)
        painter.drawText(self._cRect, QtAlignCenter, self._text or f"{progress:.1f} %")


class NProgressSimple(QProgressBar):
    """Extension: Simple Progress Widget.

    A custom widget that paints a plain bar with no other styling.
    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the progress bar."""
        if (value := self.value()) > 0:
            progress = ceil(self.width()*float(value)/self.maximum())
            painter = QPainter(self)
            painter.setRenderHint(QtPaintAntiAlias, True)
            painter.setPen(self.palette().highlight().color())
            painter.setBrush(self.palette().highlight())
            painter.drawRect(0, 0, progress, self.height())
