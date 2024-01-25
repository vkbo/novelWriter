"""
novelWriter – Wheel Event Filter Tester
=======================================

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

import pytest

from PyQt5.QtGui import QKeyEvent, QWheelEvent
from PyQt5.QtCore import QEvent, QObject, QPoint, Qt
from PyQt5.QtWidgets import QWidget

from novelwriter.extensions.eventfilters import WheelEventFilter


class MockWidget(QWidget):

    def __init__(self):
        super().__init__(None)
        self.count = 0
        return

    def wheelEvent(self, event: QWheelEvent) -> None:
        self.count += 1
        return


@pytest.mark.gui
def testExtEventFilters_WheelEventFilter():
    """Test the WheelEventFilter class."""
    obj = QObject()
    widget = MockWidget()
    eFilter = WheelEventFilter(widget)
    assert widget.count == 0

    # Sending a key event does nothing
    event = QKeyEvent(QEvent.KeyPress, 1, Qt.ShiftModifier)
    eFilter.eventFilter(obj, event)
    assert widget.count == 0

    # Sending a mouse wheel event forwards it
    pos = QPoint(0, 0)
    event = QWheelEvent(pos, pos, pos, pos, Qt.NoButton, Qt.NoModifier, Qt.NoScrollPhase, False)
    eFilter.eventFilter(obj, event)
    assert widget.count == 1

    # But ignore if we're locked
    eFilter._locked = True
    eFilter.eventFilter(obj, event)
    assert widget.count == 1

# END Test testExtEventFilters_WheelEventFilter
