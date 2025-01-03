"""
novelWriter – Switch Tester
===========================

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

from PyQt5.QtCore import QEvent, QPoint
from PyQt5.QtGui import QMouseEvent

from novelwriter.extensions.switch import NSwitch
from novelwriter.types import QtModNone, QtMouseLeft

from tests.tools import SimpleDialog


@pytest.mark.gui
def testExtSwitch_Main(qtbot):
    """Test the NSwitch class. This is mostly a check that all the calls
    work as the result is visual.
    """
    dialog = SimpleDialog()
    switch = NSwitch(dialog, 40)

    with qtbot.waitExposed(dialog):
        # This ensures the paint event is executed
        dialog.show()

    dialog.resize(200, 100)

    switch.setEnabled(False)
    switch.setChecked(False)
    switch.repaint()
    qtbot.wait(20)

    switch.setChecked(True)
    switch.repaint()
    qtbot.wait(20)

    switch.setEnabled(True)
    switch.setChecked(False)
    switch.repaint()
    qtbot.wait(20)

    switch.setChecked(True)
    switch.repaint()
    qtbot.wait(20)

    button = QtMouseLeft
    modifier = QtModNone
    event = QMouseEvent(QEvent.Type.MouseButtonRelease, QPoint(), button, button, modifier)
    switch.mouseReleaseEvent(event)

    event = QEvent(QEvent.Type.Enter)
    switch.enterEvent(event)

    # qtbot.stop()
