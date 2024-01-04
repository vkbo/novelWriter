"""
novelWriter – Lorem Ipsum Tool Tester
=====================================

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

from tools import C, getGuiItem, buildTestProject

from PyQt5.QtWidgets import QAction

from novelwriter.tools.lipsum import GuiLipsum


@pytest.mark.gui
def testToolLipsum_Main(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test the Lorem Ipsum tool."""
    # Check that we cannot open when there is no project
    nwGUI.mainMenu.aLipsumText.activate(QAction.Trigger)
    assert getGuiItem("GuiLipsum") is None

    buildTestProject(nwGUI, projPath)
    nwLipsum = GuiLipsum(nwGUI)

    # Generate paragraphs
    nwGUI.docEditor.setCursorPosition(100)  # End of document
    nwLipsum.paraCount.setValue(2)
    nwLipsum._doInsert()
    assert "Lorem ipsum" in nwLipsum.lipsumText

    # Generate random paragraph
    nwGUI.docEditor.setCursorPosition(1000)  # End of document
    nwLipsum.randSwitch.setChecked(True)
    nwLipsum.paraCount.setValue(1)
    nwLipsum._doInsert()
    assert len(nwLipsum.lipsumText) > 0

    nwLipsum.setObjectName("")
    nwLipsum.close()

    # Trigger insertion in document
    assert nwGUI.openDocument(C.hSceneDoc) is True
    nwGUI.docEditor.setCursorLine(3)
    with monkeypatch.context() as mp:
        mp.setattr(GuiLipsum, "exec_", lambda *a: None)
        mp.setattr(GuiLipsum, "lipsumText", "FooBar")
        nwGUI.mainMenu.aLipsumText.activate(QAction.Trigger)
        assert nwGUI.docEditor.getText() == "### New Scene\n\nFooBar"

    # qtbot.stop()

# END Test testToolLipsum_Main
