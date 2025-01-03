"""
novelWriter – Progress Bar Tester
=================================

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

from time import sleep

import pytest

from PyQt5.QtGui import QColor

from novelwriter.extensions.progressbars import NProgressCircle, NProgressSimple

from tests.tools import SimpleDialog


@pytest.mark.gui
def testExtProgressBars_NProgressCircle(qtbot):
    """Test the NProgressCircle class."""
    dialog = SimpleDialog()
    progress = NProgressCircle(dialog, 200, 16)

    with qtbot.waitExposed(dialog):
        # This ensures the paint event is executed
        dialog.show()

    dialog.resize(200, 200)
    progress.setColours(
        QColor(255, 255, 255), QColor(255, 192, 192),
        QColor(255, 0, 0), QColor(0, 0, 0),
    )

    progress.setMaximum(100)
    for i in range(1, 101):
        progress.setValue(i)
        sleep(0.0025)
        assert progress.value() == i

    progress.setCentreText("Done!")
    assert progress._text == "Done!"

    # qtbot.stop()


@pytest.mark.gui
def testExtProgressBars_NProgressSimple(qtbot):
    """Test the NProgressSimple class."""
    dialog = SimpleDialog()
    progress = NProgressSimple(dialog)

    with qtbot.waitExposed(dialog):
        # This ensures the paint event is executed
        dialog.show()

    progress.setMaximum(100)
    for i in range(1, 101):
        progress.setValue(i)
        sleep(0.0025)
        assert progress.value() == i

    # qtbot.stop()
