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

from tools import SimpleDialog

from PyQt5.QtGui import QWheelEvent
from PyQt5.QtCore import QPoint, QPointF, Qt

from novelwriter.extensions.modified import NComboBox, NDoubleSpinBox, NSpinBox


class MockWheelEvent(QWheelEvent):

    def __init__(self):
        super().__init__(
            QPointF(0, 0), QPointF(0, 0), QPoint(0, 0), QPoint(0, 0),
            Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier,
            Qt.ScrollPhase.ScrollUpdate, False
        )
        self.ignored = False
        return

    def ignore(self):
        super().ignore()
        self.ignored = True
        return

# END Class MockWheelEvent


@pytest.mark.gui
def testExtModified_NComboBox(qtbot, monkeypatch):
    """Test the NComboBox class."""
    widget = NComboBox()
    widget.addItem("Item 1", 1)
    widget.addItem("Item 2", 2)

    dialog = SimpleDialog(widget)
    dialog.show()

    with monkeypatch.context() as mp:
        mp.setattr(NComboBox, "hasFocus", lambda *a: True)
        event = MockWheelEvent()
        widget.wheelEvent(event)
        assert event.ignored is False

    with monkeypatch.context() as mp:
        mp.setattr(NComboBox, "hasFocus", lambda *a: False)
        event = MockWheelEvent()
        widget.wheelEvent(event)
        assert event.ignored is True

    # qtbot.stop()

# END Test testExtModified_NComboBox


@pytest.mark.gui
def testExtModified_NSpinBox(qtbot, monkeypatch):
    """Test the NSpinBox class."""
    widget = NSpinBox()
    widget.setMinimum(0)
    widget.setMaximum(100)
    widget.setValue(42)

    dialog = SimpleDialog(widget)
    dialog.show()

    with monkeypatch.context() as mp:
        mp.setattr(NSpinBox, "hasFocus", lambda *a: True)
        event = MockWheelEvent()
        widget.wheelEvent(event)
        assert event.ignored is False

    with monkeypatch.context() as mp:
        mp.setattr(NSpinBox, "hasFocus", lambda *a: False)
        event = MockWheelEvent()
        widget.wheelEvent(event)
        assert event.ignored is True

    # qtbot.stop()

# END Test testExtModified_NSpinBox


@pytest.mark.gui
def testExtModified_NDoubleSpinBox(qtbot, monkeypatch):
    """Test the NDoubleSpinBox class."""
    widget = NDoubleSpinBox()
    widget.setMinimum(0.0)
    widget.setMaximum(100.0)
    widget.setValue(42.0)

    dialog = SimpleDialog(widget)
    dialog.show()

    with monkeypatch.context() as mp:
        mp.setattr(NDoubleSpinBox, "hasFocus", lambda *a: True)
        event = MockWheelEvent()
        widget.wheelEvent(event)
        assert event.ignored is False

    with monkeypatch.context() as mp:
        mp.setattr(NDoubleSpinBox, "hasFocus", lambda *a: False)
        event = MockWheelEvent()
        widget.wheelEvent(event)
        assert event.ignored is True

    # qtbot.stop()

# END Test testExtModified_NDoubleSpinBox
