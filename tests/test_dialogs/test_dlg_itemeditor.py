"""
novelWriter – Item Editor Dialog Class Tester
=============================================

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

from tools import getGuiItem, buildTestProject

from PyQt5.QtWidgets import QAction, QDialog, QMessageBox

from novelwriter.gui import GuiProjectTree
from novelwriter.enum import nwItemLayout, nwItemType
from novelwriter.dialogs import GuiItemEditor
from novelwriter.core.tree import NWTree

statusKeys = ["s000000", "s000001", "s000002", "s000003"]
importKeys = ["i000004", "i000005", "i000006", "i000007"]


@pytest.mark.gui
def testDlgItemEditor_Dialog(qtbot, monkeypatch, nwGUI, fncProj, mockRnd):
    """Test launching the item editor dialog from GuiMain.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)

    # Block Dialog exec_
    monkeypatch.setattr(GuiItemEditor, "exec_", lambda *a: None)

    # Open Editor wo/Project
    assert nwGUI.editItem() is False

    # Create and Open Project
    buildTestProject(nwGUI, fncProj)
    tHandle = "000000000000f"

    # No Selection
    nwGUI.treeView.clearSelection()
    assert nwGUI.editItem() is False

    # Force opening from editor
    assert nwGUI.openDocument(tHandle)
    nwGUI.isFocusMode = True

    # Block Tree Lookup
    with monkeypatch.context() as mp:
        mp.setattr(NWTree, "__getitem__", lambda *a: None)
        assert nwGUI.editItem() is False

    # Invalid Type
    nwGUI.theProject.projTree[tHandle]._type = nwItemType.NO_TYPE
    assert nwGUI.editItem() is False
    nwGUI.theProject.projTree[tHandle]._type = nwItemType.FILE

    # Open Properly
    assert nwGUI.editItem() is True
    qtbot.waitUntil(lambda: getGuiItem("GuiItemEditor") is not None, timeout=1000)
    itemEdit = getGuiItem("GuiItemEditor")
    assert itemEdit is not None
    itemEdit.close()

    # Open Via Menu
    with monkeypatch.context() as mp:
        mp.setattr(GuiItemEditor, "result", lambda *a: QDialog.Accepted)
        nwGUI.mainMenu.aEditItem.activate(QAction.Trigger)
        qtbot.waitUntil(lambda: getGuiItem("GuiItemEditor") is not None, timeout=1000)
        itemEdit = getGuiItem("GuiItemEditor")
        assert itemEdit is not None
        itemEdit.close()

    nwGUI.isFocusMode = False

# END Test testDlgItemEditor_Dialog


@pytest.mark.gui
def testDlgItemEditor_Novel(qtbot, monkeypatch, nwGUI, fncProj, mockRnd):
    """Test the item editor dialog for a novel document.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: True)

    # Create Project and Open Document
    buildTestProject(nwGUI, fncProj)
    tHandle = "000000000000f"

    assert nwGUI.theProject.statusItems.name(statusKeys[0]) == "New"
    assert nwGUI.theProject.statusItems.name(statusKeys[1]) == "Note"

    assert nwGUI.openDocument(tHandle) is True

    # Check that an invalid handle is managed
    itemEdit = GuiItemEditor(nwGUI, "whatever")
    itemEdit.show()
    itemEdit._doClose()

    # Edit a Document
    itemEdit = GuiItemEditor(nwGUI, tHandle)
    itemEdit.show()

    # Check Existing Settings
    assert itemEdit.editName.text() == "New Scene"
    assert itemEdit.editStatus.currentData() == statusKeys[0]
    assert itemEdit.editLayout.currentData() == nwItemLayout.DOCUMENT
    assert itemEdit.editExport.isChecked() is True

    # Change Settings
    layoutIdx = itemEdit.editLayout.findData(nwItemLayout.NOTE)
    itemEdit.editName.setText("Great Scene")
    itemEdit.editStatus.setCurrentIndex(1)
    itemEdit.editLayout.setCurrentIndex(layoutIdx)
    itemEdit.editExport.setChecked(False)

    # Check New Settings
    itemEdit._doSave()
    assert itemEdit.theItem.itemName == "Great Scene"
    assert itemEdit.theItem.itemStatus == statusKeys[1]
    assert itemEdit.theItem.itemLayout == nwItemLayout.NOTE
    assert itemEdit.theItem.isExported is False

    # Check that the editor header is updated
    nwGUI.docEditor.updateDocInfo(tHandle)
    assert nwGUI.docEditor.docHeader.theTitle.text() == "Novel  ›  New Chapter  ›  Great Scene"

    itemEdit.close()
    del itemEdit
    # qtbot.stopForInteraction()

# END Test testDlgItemEditor_Dialog


@pytest.mark.gui
def testDlgItemEditor_Note(qtbot, monkeypatch, nwGUI, fncProj, mockRnd):
    """Test the item editor dialog for a project note.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: True)

    # Create Project and Open Document
    buildTestProject(nwGUI, fncProj)
    assert nwGUI.theProject.statusItems.name(statusKeys[0]) == "New"
    assert nwGUI.theProject.statusItems.name(statusKeys[1]) == "Note"
    assert nwGUI.theProject.importItems.name(importKeys[0]) == "New"
    assert nwGUI.theProject.importItems.name(importKeys[1]) == "Minor"

    # Create Note
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem("000000000000a").setSelected(True)
    nwGUI.treeView.newTreeItem(nwItemType.FILE, None)

    # Open Note
    assert nwGUI.openDocument("0000000000010")

    # Edit a Document
    itemEdit = GuiItemEditor(nwGUI, "0000000000010")
    itemEdit.show()

    # Check Existing Settings
    assert itemEdit.editName.text() == "New Note"
    assert itemEdit.editStatus.currentData() == importKeys[0]
    assert itemEdit.editLayout.currentData() == nwItemLayout.NOTE
    assert itemEdit.editExport.isChecked() is True

    # Change Settings
    itemEdit.editName.setText("New Character")
    itemEdit.editStatus.setCurrentIndex(1)
    itemEdit.editExport.setChecked(False)
    itemEdit._doSave()

    # Check New Settings
    assert itemEdit.theItem.itemName == "New Character"
    assert itemEdit.theItem.itemStatus == statusKeys[0]
    assert itemEdit.theItem.itemImport == importKeys[1]
    assert itemEdit.theItem.itemLayout == nwItemLayout.NOTE
    assert itemEdit.theItem.isExported is False

    itemEdit.close()
    del itemEdit
    # qtbot.stopForInteraction()

# END Test testDlgItemEditor_Note


@pytest.mark.gui
def testDlgItemEditor_Folder(qtbot, monkeypatch, nwGUI, fncProj, mockRnd):
    """Test the item editor dialog for a folder.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: True)

    # Create Project and Open Document
    buildTestProject(nwGUI, fncProj)

    # Edit a Folder
    itemEdit = GuiItemEditor(nwGUI, "000000000000d")
    itemEdit.show()

    assert nwGUI.theProject.statusItems.name(statusKeys[0]) == "New"
    assert nwGUI.theProject.statusItems.name(statusKeys[1]) == "Note"

    # Check Existing Settings
    assert itemEdit.editName.text() == "New Chapter"
    assert itemEdit.editStatus.currentData() == statusKeys[0]
    assert itemEdit.editLayout.currentData() == nwItemLayout.NO_LAYOUT
    assert itemEdit.editExport.isChecked() is False

    assert itemEdit.editLayout.isEnabled() is False
    assert itemEdit.editExport.isEnabled() is False

    # Change Settings
    itemEdit.editName.setText("Chapter One")
    itemEdit.editStatus.setCurrentIndex(1)

    # Check New Settings
    itemEdit._doSave()
    assert itemEdit.theItem.itemName == "Chapter One"
    assert itemEdit.theItem.itemStatus == statusKeys[1]
    assert itemEdit.theItem.itemLayout == nwItemLayout.NO_LAYOUT
    assert itemEdit.theItem.isExported is False

    itemEdit.close()
    del itemEdit
    # qtbot.stopForInteraction()

# END Test testDlgItemEditor_Folder
