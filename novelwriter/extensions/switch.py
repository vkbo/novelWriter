"""
novelWriter – Custom Widget: Switch
===================================

File History:
Created: 2020-05-03 [0.4.5]

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
"""  # noqa
from __future__ import annotations

from PyQt6.QtCore import QPropertyAnimation, Qt, pyqtProperty, pyqtSlot  # pyright: ignore
from PyQt6.QtGui import QEnterEvent, QPainter, QPaintEvent, QResizeEvent
from PyQt6.QtWidgets import QAbstractButton, QWidget

from novelwriter import SHARED
from novelwriter.types import QtNoPen, QtPaintAntiAlias, QtSizeFixed


class NSwitch(QAbstractButton):
    """Custom: Toggle Switch."""

    __slots__ = ("_cOff", "_cOn", "_offset", "_rH", "_rR", "_xH", "_xR", "_xW")

    def __init__(self, parent: QWidget, height: int = 0) -> None:
        super().__init__(parent=parent)

        self._xH = height or SHARED.theme.baseButtonHeight
        self._xW = 2*self._xH
        self._xR = int(self._xH*0.5)
        self._rH = self._xH - 4
        self._rR = self._xR - 2

        self._cOn = SHARED.theme.accentCol
        self._cOff = self.palette().alternateBase()

        self.setCheckable(True)
        self.setSizePolicy(QtSizeFixed, QtSizeFixed)
        self.setFixedWidth(self._xW)
        self.setFixedHeight(self._xH)
        self._offset = self._xR

        self.clicked.connect(self._onClick)

    ##
    #  Properties
    ##

    @pyqtProperty(int)
    def offset(self) -> int:  # type: ignore
        return self._offset

    @offset.setter  # type: ignore
    def offset(self, offset: int) -> None:
        self._offset = offset
        self.update()

    ##
    #  Getters and Setters
    ##

    def setChecked(self, checked: bool) -> None:
        """Overload setChecked to also alter the offset."""
        super().setChecked(checked)
        self._offset = (self._xW - self._xR) if checked else self._xR

    ##
    #  Events
    ##

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Overload resize to ensure correct offset."""
        super().resizeEvent(event)
        self._offset = (self._xW - self._xR) if self.isChecked() else self._xR

    def paintEvent(self, event: QPaintEvent) -> None:
        """Drawing the switch itself."""
        palette = self.palette()

        painter = QPainter(self)
        painter.setRenderHint(QtPaintAntiAlias, True)
        painter.setOpacity(1.0 if self.isEnabled() else 0.5)

        painter.setPen(palette.highlight().color() if self.hasFocus() else palette.mid().color())
        painter.setBrush(self._cOn if self.isChecked() else self._cOff)
        painter.drawRoundedRect(0, 0, self._xW, self._xH, self._xR, self._xR)

        painter.setPen(QtNoPen)
        painter.setBrush(palette.highlightedText())
        painter.drawEllipse(self._offset - self._rR, 2, self._rH, self._rH)

        painter.end()

    def enterEvent(self, event: QEnterEvent) -> None:
        """Change the cursor when hovering the button."""
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().enterEvent(event)

    @pyqtSlot(bool)
    def _onClick(self, checked: bool) -> None:
        """Animate the toggle action."""
        anim = QPropertyAnimation(self, b"offset", self)
        anim.setDuration(120)
        anim.setStartValue(self._offset)
        anim.setEndValue((self._xW - self._xR) if checked else self._xR)
        anim.start()
