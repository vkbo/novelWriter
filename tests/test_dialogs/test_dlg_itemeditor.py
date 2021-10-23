"""
novelWriter – Item Editor Dialog Class Tester
=============================================

This file is a part of novelWriter
Copyright 2018–2021, Veronica Berglyd Olsen

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

from PyQt5.QtWidgets import QAction, QDialog, QMessageBox

from novelwriter.gui import GuiProjectTree
from novelwriter.enum import nwItemLayout, nwItemType
from novelwriter.dialogs import GuiItemEditor
from novelwriter.core.tree import NWTree


@pytest.mark.gui
def testDlgItemEditor_Dialog(qtbot, monkeypatch, nwGUI, fncProj):
    """Test launching the item editor dialog from GuiMain.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)

    # Block Dialog exec_
    monkeypatch.setattr(GuiItemEditor, "exec_", lambda *a: None)

    # Open Editor wo/Project
    assert nwGUI.editItem() is False

    # Create and Open Project
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": fncProj})

    # No Selection
    nwGUI.treeView.clearSelection()
    assert nwGUI.editItem() is False

    # Force opening from editor
    assert nwGUI.openDocument("0e17daca5f3e1")
    nwGUI.isFocusMode = True

    # Block Tree Lookup
    with monkeypatch.context() as mp:
        mp.setattr(NWTree, "__getitem__", lambda *a: None)
        assert nwGUI.editItem() is False

    # Invalid Type
    nwGUI.theProject.projTree["0e17daca5f3e1"].itemType = nwItemType.NO_TYPE
    assert nwGUI.editItem() is False
    nwGUI.theProject.projTree["0e17daca5f3e1"].itemType = nwItemType.FILE

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
def testDlgItemEditor_Novel(qtbot, monkeypatch, nwGUI, fncProj):
    """Test the item editor dialog for a novel document.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: True)

    # Create Project and Open Document
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": fncProj})
    assert nwGUI.openDocument("0e17daca5f3e1")

    # Check that an invalid handle is managed
    itemEdit = GuiItemEditor(nwGUI, "whatever")
    itemEdit.show()
    itemEdit._doClose()

    # Edit a Document
    itemEdit = GuiItemEditor(nwGUI, "0e17daca5f3e1")
    itemEdit.show()

    # Check Existing Settings
    assert itemEdit.editName.text() == "New Scene"
    assert itemEdit.editStatus.currentData() == "New"
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
    assert itemEdit.theItem.itemStatus == "Note"
    assert itemEdit.theItem.itemLayout == nwItemLayout.NOTE
    assert itemEdit.theItem.isExported is False

    # Check that the editor header is updated
    nwGUI.docEditor.updateDocInfo("0e17daca5f3e1")
    assert nwGUI.docEditor.docHeader.theTitle.text() == "Novel  ›  New Chapter  ›  Great Scene"

    itemEdit.close()
    del itemEdit
    # qtbot.stopForInteraction()

# END Test testDlgItemEditor_Dialog


@pytest.mark.gui
def testDlgItemEditor_Note(qtbot, monkeypatch, nwGUI, fncProj):
    """Test the item editor dialog for a project note.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: True)

    # Create Project and Open Document
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": fncProj})

    # Create Note
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem("71ee45a3c0db9").setSelected(True)
    nwGUI.treeView.newTreeItem(nwItemType.FILE, None)

    # Open Note
    assert nwGUI.openDocument("1a6562590ef19")

    # Edit a Document
    itemEdit = GuiItemEditor(nwGUI, "1a6562590ef19")
    itemEdit.show()

    # Check Existing Settings
    assert itemEdit.editName.text() == "New File"
    assert itemEdit.editStatus.currentData() == "New"
    assert itemEdit.editLayout.currentData() == nwItemLayout.NOTE
    assert itemEdit.editExport.isChecked() is True

    # Change Settings
    itemEdit.editName.setText("New Character")
    itemEdit.editStatus.setCurrentIndex(1)
    itemEdit.editExport.setChecked(False)

    # Check New Settings
    itemEdit._doSave()
    assert itemEdit.theItem.itemName == "New Character"
    assert itemEdit.theItem.itemStatus == "Minor"
    assert itemEdit.theItem.itemLayout == nwItemLayout.NOTE
    assert itemEdit.theItem.isExported is False

    itemEdit.close()
    del itemEdit
    # qtbot.stopForInteraction()

# END Test testDlgItemEditor_Note


@pytest.mark.gui
def testDlgItemEditor_Folder(qtbot, monkeypatch, nwGUI, fncProj):
    """Test the item editor dialog for a folder.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: True)

    # Create Project and Open Document
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": fncProj})

    # Edit a Folder
    itemEdit = GuiItemEditor(nwGUI, "31489056e0916")
    itemEdit.show()

    # Check Existing Settings
    assert itemEdit.editName.text() == "New Chapter"
    assert itemEdit.editStatus.currentData() == "New"
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
    assert itemEdit.theItem.itemStatus == "Note"
    assert itemEdit.theItem.itemLayout == nwItemLayout.NO_LAYOUT
    assert itemEdit.theItem.isExported is False

    itemEdit.close()
    del itemEdit
    # qtbot.stopForInteraction()

# END Test testDlgItemEditor_Folder
