"""
novelWriter – Merge and Split Dialog Classes Tester
===================================================

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

from tools import buildTestProject, C

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

from novelwriter.dialogs import GuiDocMerge


@pytest.mark.gui
def testDlgMerge_Main(qtbot, monkeypatch, nwGUI, fncProj, mockRnd):
    """Test the merge documents tool.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Ok)

    # Create a new project
    buildTestProject(nwGUI, fncProj)

    # Check that the dialog kan handle invalid items
    nwMerge = GuiDocMerge(nwGUI, C.hInvalid, [C.hInvalid])
    qtbot.addWidget(nwMerge)
    nwMerge.show()
    assert nwMerge.listBox.count() == 0
    nwMerge.reject()

    # Load items from chapter dir
    nwMerge = GuiDocMerge(nwGUI, C.hChapterDir, [C.hChapterDir, C.hChapterDoc, C.hSceneDoc])
    qtbot.addWidget(nwMerge)
    nwMerge.show()

    assert nwMerge.listBox.count() == 2

    itemOne = nwMerge.listBox.item(0)
    itemTwo = nwMerge.listBox.item(1)

    assert itemOne.data(Qt.UserRole) == C.hChapterDoc
    assert itemTwo.data(Qt.UserRole) == C.hSceneDoc

    assert itemOne.checkState() == Qt.Checked
    assert itemTwo.checkState() == Qt.Checked

    data = nwMerge.getData()
    assert data["sHandle"] == C.hChapterDir
    assert data["origItems"] == [C.hChapterDir, C.hChapterDoc, C.hSceneDoc]
    assert data["moveToTrash"] is False
    assert data["finalItems"] == [C.hChapterDoc, C.hSceneDoc]

    # Uncheck second item and toggle trash switch
    itemTwo.setCheckState(Qt.Unchecked)
    nwMerge.trashSwitch.setChecked(True)

    data = nwMerge.getData()
    assert data["sHandle"] == C.hChapterDir
    assert data["origItems"] == [C.hChapterDir, C.hChapterDoc, C.hSceneDoc]
    assert data["moveToTrash"] is True
    assert data["finalItems"] == [C.hChapterDoc]

    # Restore default values
    nwMerge._resetList()

    data = nwMerge.getData()
    assert data["sHandle"] == C.hChapterDir
    assert data["origItems"] == [C.hChapterDir, C.hChapterDoc, C.hSceneDoc]
    assert data["moveToTrash"] is True
    assert data["finalItems"] == [C.hChapterDoc, C.hSceneDoc]

    # qtbot.stop()

# END Test testDlgMerge_Main
