"""
novelWriter – Lorem Ipsum Tool Tester
=====================================

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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

import pytest

from tools import getGuiItem

from PyQt5.QtWidgets import QAction, QMessageBox

from novelwriter.tools import GuiLipsum


@pytest.mark.gui
def testToolLipsum_Main(qtbot, monkeypatch, nwGUI, fncProj):
    """Test the Lorem Ipsum tool.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)

    # Check that we cannot open when there is no project
    nwGUI.mainMenu.aLipsumText.activate(QAction.Trigger)
    assert getGuiItem("GuiLipsum") is None

    # Create a new project
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": fncProj}) is True
    assert nwGUI.openDocument("0e17daca5f3e1") is True
    assert len(nwGUI.docEditor.getText()) == 15

    # Open the tool
    nwGUI.mainMenu.aLipsumText.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiLipsum") is not None, timeout=1000)

    nwLipsum = getGuiItem("GuiLipsum")
    assert isinstance(nwLipsum, GuiLipsum)

    # Insert paragraphs
    nwGUI.docEditor.setCursorPosition(100)  # End of document
    nwLipsum.paraCount.setValue(2)
    nwLipsum._doInsert()
    theText = nwGUI.docEditor.getText()
    assert "Lorem ipsum" in theText
    assert len(theText) == 965

    # Insert random paragraph
    nwGUI.docEditor.setCursorPosition(1000)  # End of document
    nwLipsum.randSwitch.setChecked(True)
    nwLipsum.paraCount.setValue(1)
    nwLipsum._doInsert()
    theText = nwGUI.docEditor.getText()
    assert len(theText) > 965

    # Close
    nwLipsum._doClose()

    # qtbot.stopForInteraction()

# END Test testToolLipsum_Main
