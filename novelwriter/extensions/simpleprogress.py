"""
novelWriter – Custom Widget: Progress Simple
============================================

File History:
Created: 2023-06-09 [2.1b1]

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

from math import ceil

from PyQt5.QtGui import QPaintEvent, QPainter
from PyQt5.QtWidgets import QProgressBar, QWidget


class NProgressSimple(QProgressBar):
    """Extension: Simple Progress Widget

    A custom widget that paints a plain bar with no other styling.
    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        return

    def paintEvent(self, event: QPaintEvent) -> None:
        """Custom painter for the progress bar."""
        if (value := self.value()) > 0:
            progress = ceil(self.width()*float(value)/self.maximum())
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setPen(self.palette().highlight().color())
            painter.setBrush(self.palette().highlight())
            painter.drawRect(0, 0, progress, self.height())
        return

# END Class NProgressSimple
