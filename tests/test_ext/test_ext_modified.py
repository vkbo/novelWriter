"""
novelWriter – Modified Widgets Tester
=====================================

This file is a part of novelWriter
Copyright (C) 2024 Veronica Berglyd Olsen and novelWriter contributors

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

from PyQt6.QtCore import QEvent, QPoint, QPointF, Qt
from PyQt6.QtGui import QKeyEvent, QMouseEvent, QStandardItem, QStandardItemModel, QWheelEvent
from PyQt6.QtWidgets import QWidget

from novelwriter.extensions.modified import (
    NClickableLabel, NComboBox, NDialog, NDoubleSpinBox, NSpinBox, NTreeView
)
from novelwriter.types import QtModNone, QtMouseLeft, QtMouseMiddle, QtRejected

from tests.tools import SimpleDialog


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


@pytest.mark.gui
def testExtModified_NDialog(qtbot, monkeypatch):
    """Test the NDialog class."""
    widget = QWidget()
    dialog = NDialog(widget)
    assert dialog.parent() is widget

    dialog.softDelete()
    assert dialog.parent() is None

    with qtbot.waitSignal(dialog.rejected, timeout=1000):
        dialog.keyPressEvent(QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Escape, QtModNone))
        assert dialog.result() == QtRejected


@pytest.mark.gui
def testExtModified_NTreeView(qtbot, monkeypatch):
    """Test the NTreeView class."""
    model = QStandardItemModel(1, 1)
    model.insertRow(0, QStandardItem("Hello World"))

    widget = NTreeView()
    widget.setModel(model)
    dialog = SimpleDialog(widget)
    dialog.show()

    vPort = widget.viewport()
    item = model.item(0, 0)
    assert vPort is not None
    assert item is not None

    position = QPointF(widget.visualRect(model.createIndex(0, 0)).center())
    event = QMouseEvent(
        QEvent.Type.MouseButtonPress, position, QtMouseMiddle, QtMouseMiddle, QtModNone
    )
    with qtbot.waitSignal(widget.middleClicked):
        widget.mousePressEvent(event)

    # qtbot.stop()


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


@pytest.mark.gui
def testExtModified_NClickableLabel(qtbot, monkeypatch):
    """Test the NClickableLabel class."""
    widget = NClickableLabel()
    dialog = SimpleDialog(widget)
    dialog.show()

    position = QPointF(widget.rect().center())
    event = QMouseEvent(
        QEvent.Type.MouseButtonPress, position, QtMouseLeft, QtMouseLeft, QtModNone
    )

    with qtbot.waitSignal(widget.mouseClicked):
        widget.mousePressEvent(event)
