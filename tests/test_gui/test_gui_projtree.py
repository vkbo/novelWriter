"""
novelWriter – Main GUI Project Tree Class Tester
================================================

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

import os
import pytest

from tools import buildTestProject

from PyQt5.QtWidgets import QMessageBox, QMenu

from novelwriter.enum import nwItemLayout, nwItemType, nwItemClass
from novelwriter.dialogs import GuiEditLabel
from novelwriter.gui.projtree import GuiProjectTree


@pytest.mark.gui
def testGuiProjTree_NewItems(qtbot, caplog, monkeypatch, nwGUI, fncDir, mockRnd):
    """Test adding and removing items from the project tree.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    projView = nwGUI.projView
    projTree = nwGUI.projView.projTree
    theProject = nwGUI.theProject

    # Try to add item with no project
    assert projView.projTree.newTreeItem(nwItemType.FILE) is False

    # Create a project
    prjDir = os.path.join(fncDir, "project")
    buildTestProject(nwGUI, prjDir)

    # No itemType set
    projView.projTree.clearSelection()
    assert projView.projTree.newTreeItem(None) is False

    # Root Items
    # ==========

    # No class set
    assert projView.projTree.newTreeItem(nwItemType.ROOT) is False

    # Create root item
    assert projView.projTree.newTreeItem(nwItemType.ROOT, nwItemClass.WORLD) is True
    assert "0000000000010" in theProject.tree

    # File/Folder Items
    # =================

    # No location selected for new item
    projView.projTree.clearSelection()
    caplog.clear()
    assert projView.projTree.newTreeItem(nwItemType.FILE) is False
    assert projView.projTree.newTreeItem(nwItemType.FOLDER) is False
    assert "Did not find anywhere" in caplog.text

    # Create new folder as child of Novel folder
    projView.setSelectedHandle("0000000000008")
    assert projView.projTree.newTreeItem(nwItemType.FOLDER) is True
    assert theProject.tree["0000000000011"].itemParent == "0000000000008"
    assert theProject.tree["0000000000011"].itemRoot == "0000000000008"
    assert theProject.tree["0000000000011"].itemClass == nwItemClass.NOVEL

    # Add a new file in the new folder
    projView.setSelectedHandle("0000000000011")
    assert projView.projTree.newTreeItem(nwItemType.FILE) is True
    assert theProject.tree["0000000000012"].itemParent == "0000000000011"
    assert theProject.tree["0000000000012"].itemRoot == "0000000000008"
    assert theProject.tree["0000000000012"].itemClass == nwItemClass.NOVEL

    # Add a new chapter next to the other new file
    projView.setSelectedHandle("0000000000012")
    assert projView.projTree.newTreeItem(nwItemType.FILE, hLevel=2) is True
    assert theProject.tree["0000000000013"].itemParent == "0000000000011"
    assert theProject.tree["0000000000013"].itemRoot == "0000000000008"
    assert theProject.tree["0000000000013"].itemClass == nwItemClass.NOVEL
    assert nwGUI.openDocument("0000000000013")
    assert nwGUI.docEditor.getText() == "## New Chapter\n\n"

    # Add a new scene next to the other new file
    projView.setSelectedHandle("0000000000012")
    assert projView.projTree.newTreeItem(nwItemType.FILE, hLevel=3) is True
    assert theProject.tree["0000000000014"].itemParent == "0000000000011"
    assert theProject.tree["0000000000014"].itemRoot == "0000000000008"
    assert theProject.tree["0000000000014"].itemClass == nwItemClass.NOVEL
    assert nwGUI.openDocument("0000000000014")
    assert nwGUI.docEditor.getText() == "### New Scene\n\n"

    # Add a new file to the characters folder
    projView.setSelectedHandle("000000000000a")
    assert projView.projTree.newTreeItem(nwItemType.FILE, hLevel=1, isNote=True) is True
    assert theProject.tree["0000000000015"].itemParent == "000000000000a"
    assert theProject.tree["0000000000015"].itemRoot == "000000000000a"
    assert theProject.tree["0000000000015"].itemClass == nwItemClass.CHARACTER
    assert nwGUI.openDocument("0000000000015")
    assert nwGUI.docEditor.getText() == "# New Note\n\n"

    # Make sure the sibling folder bug trap works
    projView.setSelectedHandle("0000000000013")
    theProject.tree["0000000000013"].setParent(None)  # This should not happen
    caplog.clear()
    assert projView.projTree.newTreeItem(nwItemType.FILE) is False
    assert "Internal error" in caplog.text
    theProject.tree["0000000000013"].setParent("0000000000011")

    # Cancel during creation
    with monkeypatch.context() as mp:
        mp.setattr(GuiEditLabel, "getLabel", lambda *a, **k: ("", False))
        projView.setSelectedHandle("0000000000013")
        assert projView.projTree.newTreeItem(nwItemType.FILE) is False

    # Get the trash folder
    projView.projTree._addTrashRoot()
    trashHandle = theProject.trashFolder()
    projView.setSelectedHandle(trashHandle)
    assert projView.projTree.newTreeItem(nwItemType.FILE) is False
    assert "Cannot add new files or folders to the Trash folder" in caplog.text

    # Rename Item
    # ===========

    # Rename plot folder
    with monkeypatch.context() as mp:
        mp.setattr(GuiEditLabel, "getLabel", lambda *a, **k: ("Stuff", True))
        projTree.renameTreeItem("0000000000009") is True
        assert theProject.tree["0000000000009"].itemName == "Stuff"

    # Rename invalid folder
    projTree.renameTreeItem("0000000000000") is False

    # Other Checks
    # ============

    # Also check error handling in reveal function
    assert projView.revealNewTreeItem("abc") is False

    # Add an item that cannot be displayed in the tree
    nHandle = theProject.newFile("Test", None)
    assert projView.revealNewTreeItem(nHandle) is False

    # Clean up
    # qtbot.stop()
    nwGUI.closeProject()

# END Test testGuiProjTree_NewItems


@pytest.mark.gui
def testGuiProjTree_MoveItems(qtbot, monkeypatch, nwGUI, fncDir, mockRnd):
    """Test adding and removing items from the project tree.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    nwTree = nwGUI.projView

    # Try to move item with no project
    assert nwTree.projTree.moveTreeItem(1) is False

    # Create a project
    prjDir = os.path.join(fncDir, "project")
    buildTestProject(nwGUI, prjDir)

    # Move Documents
    # ==============

    # Add some files
    nwTree.setSelectedHandle("000000000000d")
    assert nwTree.projTree.newTreeItem(nwItemType.FILE) is True
    assert nwTree.projTree.newTreeItem(nwItemType.FILE) is True
    assert nwTree.projTree.newTreeItem(nwItemType.FILE) is True
    assert nwTree.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000e", "000000000000f",
        "0000000000010", "0000000000011", "0000000000012",
    ]

    # Move with no selections
    nwTree.projTree.clearSelection()
    assert nwTree.projTree.moveTreeItem(1) is False

    # Move second item up twice (should give same result)
    nwTree.setSelectedHandle("000000000000f")
    assert nwTree.projTree.moveTreeItem(-1) is True
    assert nwTree.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000f", "000000000000e",
        "0000000000010", "0000000000011", "0000000000012",
    ]
    assert nwTree.projTree.moveTreeItem(-1) is False
    assert nwTree.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000f", "000000000000e",
        "0000000000010", "0000000000011", "0000000000012",
    ]

    # Restore
    assert nwTree.projTree.moveTreeItem(1) is True
    assert nwTree.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000e", "000000000000f",
        "0000000000010", "0000000000011", "0000000000012",
    ]

    # Move fifth item down twice (should give same result)
    nwTree.setSelectedHandle("0000000000011")
    assert nwTree.projTree.moveTreeItem(1) is True
    assert nwTree.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000e", "000000000000f",
        "0000000000010", "0000000000012", "0000000000011",
    ]
    assert nwTree.projTree.moveTreeItem(1) is False
    assert nwTree.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000e", "000000000000f",
        "0000000000010", "0000000000012", "0000000000011",
    ]

    # Restore
    assert nwTree.projTree.moveTreeItem(-1) is True
    assert nwTree.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000e", "000000000000f",
        "0000000000010", "0000000000011", "0000000000012",
    ]

    # Move down again, and restore via undo
    nwTree.setSelectedHandle("0000000000011")
    assert nwTree.projTree.moveTreeItem(1) is True
    assert nwTree.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000e", "000000000000f",
        "0000000000010", "0000000000012", "0000000000011",
    ]
    assert nwTree.projTree.undoLastMove() is True
    assert nwTree.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000e", "000000000000f",
        "0000000000010", "0000000000011", "0000000000012",
    ]

    # Root Folder
    # ===========

    nwTree.setSelectedHandle("0000000000008")
    assert nwGUI.theProject.tree._treeOrder.index("0000000000008") == 0

    # Move novel folder up
    assert nwTree.projTree.moveTreeItem(-1) is False
    assert nwGUI.theProject.tree._treeOrder.index("0000000000008") == 0

    # Move novel folder down
    assert nwTree.projTree.moveTreeItem(1) is True
    assert nwGUI.theProject.tree._treeOrder.index("0000000000008") == 1

    # Move novel folder up again
    assert nwTree.projTree.moveTreeItem(-1) is True
    assert nwGUI.theProject.tree._treeOrder.index("0000000000008") == 0

    # Clean up
    # qtbot.stopForInteraction()
    nwGUI.closeProject()

# END Test testGuiProjTree_MoveItems


@pytest.mark.gui
def testGuiProjTree_RequestDeleteItem(qtbot, caplog, monkeypatch, nwGUI, fncDir, mockRnd):
    """Test external requests for removing items from project tree.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    nwView = nwGUI.projView

    # Try to run with no project
    assert nwView.requestDeleteItem() is False

    # Create a project
    prjDir = os.path.join(fncDir, "project")
    buildTestProject(nwGUI, prjDir)

    # Try emptying the trash already now, when there is no trash folder
    assert nwView.emptyTrash() is False

    # Add some files
    nwView.setSelectedHandle("000000000000d")
    assert nwView.projTree.newTreeItem(nwItemType.FILE) is True
    assert nwView.projTree.newTreeItem(nwItemType.FILE) is True
    assert nwView.projTree.newTreeItem(nwItemType.FILE) is True
    assert nwView.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000e", "000000000000f",
        "0000000000010", "0000000000011", "0000000000012",
    ]

    # Delete item without focus -> blocked
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: False)
    nwView.setSelectedHandle("0000000000012")
    assert nwView.requestDeleteItem() is False
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: True)

    # No selection made
    nwView.projTree.clearSelection()
    caplog.clear()
    assert nwView.requestDeleteItem() is False
    assert "no item to delete" in caplog.text

    # Not a valid handle
    nwView.projTree.clearSelection()
    caplog.clear()
    assert nwView.requestDeleteItem("0000000000000") is False
    assert "No tree item with handle '0000000000000'" in caplog.text

    # Delete Root Folders
    # ===================

    assert nwView.requestDeleteItem("0000000000008") is False  # Novel Root is blocked
    assert nwView.requestDeleteItem("000000000000a") is True   # Character Root

    # Delete File
    # ===========

    # Block adding trash folder
    funcPointer = nwView.projTree._addTrashRoot
    nwView.projTree._addTrashRoot = lambda *a: None
    assert nwView.requestDeleteItem("0000000000012") is False
    nwView.projTree._addTrashRoot = funcPointer

    # Delete last two documents, which also adds the trash folder
    assert nwView.requestDeleteItem("0000000000012") is True
    assert nwView.requestDeleteItem("0000000000011") is True
    assert nwView.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000e", "000000000000f",
        "0000000000010"
    ]
    trashHandle = nwGUI.theProject.tree.trashRoot()
    assert nwView.getTreeFromHandle(trashHandle) == [
        trashHandle, "0000000000012", "0000000000011"
    ]

    # Try to delete the trash folder
    caplog.clear()
    assert nwView.requestDeleteItem("0000000000013") is False
    assert "Cannot delete the Trash folder" in caplog.text

    nwGUI.closeProject()

# END Test testGuiProjTree_RequestDeleteItem


@pytest.mark.gui
def testGuiProjTree_MoveItemToTrash(qtbot, caplog, monkeypatch, nwGUI, fncDir, mockRnd):
    """Test moving items to Trash.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    theProject = nwGUI.theProject
    projTree = nwGUI.projView.projTree

    # Create a project
    prjDir = os.path.join(fncDir, "project")
    buildTestProject(nwGUI, prjDir)

    hInvalid   = "0000000000000"
    hNovelRoot = "0000000000008"
    hTitlePage = "000000000000c"

    # Invalid item
    caplog.clear()
    assert projTree.moveItemToTrash(hInvalid) is False
    assert "Could not find tree item for deletion" in caplog.text

    # Root folders cannot be moved to Trash
    caplog.clear()
    assert projTree.moveItemToTrash(hNovelRoot) is False
    assert "Root folders cannot be moved to Trash" in caplog.text

    # Block adding trash folder
    funcPointer = projTree._addTrashRoot
    projTree._addTrashRoot = lambda *a: None

    caplog.clear()
    assert projTree.moveItemToTrash(hTitlePage) is False
    assert theProject.tree.isTrash(hTitlePage) is False
    assert "Could not delete item" in caplog.text

    projTree._addTrashRoot = funcPointer

    # User cancels action
    with monkeypatch.context() as mp:
        mp.setattr(QMessageBox, "question", lambda *a: QMessageBox.No)
        assert projTree.moveItemToTrash(hTitlePage) is False
        assert theProject.tree.isTrash(hTitlePage) is False

    # Move a document to Trash
    assert projTree.moveItemToTrash(hTitlePage) is True
    assert theProject.tree.isTrash(hTitlePage) is True

    # Cannot be moved again
    caplog.clear()
    assert projTree.moveItemToTrash(hTitlePage) is False
    assert "Item is already in the Trash folder" in caplog.text

    nwGUI.closeProject()

# END Test testGuiProjTree_MoveItemToTrash


@pytest.mark.gui
def testGuiProjTree_PermanentlyDeleteItem(qtbot, caplog, monkeypatch, nwGUI, fncDir, mockRnd):
    """Test permanently deleting items.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    theProject = nwGUI.theProject
    projTree = nwGUI.projView.projTree

    # Create a project
    prjDir = os.path.join(fncDir, "project")
    buildTestProject(nwGUI, prjDir)

    hInvalid    = "0000000000000"
    hNovelRoot  = "0000000000008"
    hPlotRoot   = "0000000000009"
    hTitlePage  = "000000000000c"
    hChapterDir = "000000000000d"
    hChapterDoc = "000000000000e"
    hSceneDoc   = "000000000000f"

    # Invalid item
    caplog.clear()
    assert projTree.permanentlyDeleteItem(hInvalid) is False
    assert "Could not find tree item for deletion" in caplog.text

    # Not deleting root item in use
    caplog.clear()
    assert projTree.permanentlyDeleteItem(hNovelRoot) is False
    assert "Root folders can only be deleted when they are empty" in caplog.text
    assert hNovelRoot in theProject.tree

    # Deleting unused root item is allowed
    caplog.clear()
    assert projTree.permanentlyDeleteItem(hPlotRoot) is True
    assert hPlotRoot not in theProject.tree

    # User cancels action
    with monkeypatch.context() as mp:
        mp.setattr(QMessageBox, "question", lambda *a: QMessageBox.No)
        assert projTree.permanentlyDeleteItem(hTitlePage) is False
        assert hTitlePage in theProject.tree

    # Deleting file is OK, and if it is open, it should close
    assert nwGUI.openDocument(hTitlePage) is True
    assert nwGUI.docEditor.docHandle() == hTitlePage
    assert projTree.permanentlyDeleteItem(hTitlePage) is True
    assert hTitlePage not in theProject.tree
    assert nwGUI.docEditor.docHandle() is None

    # Deleting folder + files recursiely is ok
    assert projTree.permanentlyDeleteItem(hChapterDir) is True
    assert hChapterDir not in theProject.tree
    assert hChapterDoc not in theProject.tree
    assert hSceneDoc not in theProject.tree

    nwGUI.closeProject()

# END Test testGuiProjTree_PermanentlyDeleteItem


@pytest.mark.gui
def testGuiProjTree_EmptyTrash(qtbot, caplog, monkeypatch, nwGUI, fncDir, mockRnd):
    """Test emptying Trash.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    theProject = nwGUI.theProject
    projTree = nwGUI.projView.projTree

    # No project open
    caplog.clear()
    assert projTree.emptyTrash() is False
    assert "No project open" in caplog.text

    # Create a project
    prjDir = os.path.join(fncDir, "project")
    buildTestProject(nwGUI, prjDir)

    hTitlePage  = "000000000000c"
    hChapterDir = "000000000000d"
    hChapterDoc = "000000000000e"
    hSceneDoc   = "000000000000f"

    # No Trash folder
    assert projTree.emptyTrash() is False

    # Move some documents to Trash
    assert projTree.moveItemToTrash(hTitlePage) is True
    assert projTree.moveItemToTrash(hChapterDir) is True

    assert theProject.tree.isTrash(hTitlePage) is True
    assert theProject.tree.isTrash(hChapterDir) is True
    assert theProject.tree.isTrash(hChapterDoc) is True
    assert theProject.tree.isTrash(hSceneDoc) is True

    # User cancels
    with monkeypatch.context() as mp:
        mp.setattr(QMessageBox, "question", lambda *a: QMessageBox.No)
        assert projTree.emptyTrash() is False
        assert hTitlePage in theProject.tree
        assert hChapterDir in theProject.tree
        assert hChapterDoc in theProject.tree
        assert hSceneDoc in theProject.tree

    # Run again to empty all items
    assert projTree.emptyTrash() is True
    assert hTitlePage not in theProject.tree
    assert hChapterDir not in theProject.tree
    assert hChapterDoc not in theProject.tree
    assert hSceneDoc not in theProject.tree

    # Running Emtpy Trash again is cancelled due to empty folder
    assert projTree.emptyTrash() is False

    nwGUI.closeProject()

# END Test testGuiProjTree_EmptyTrash


@pytest.mark.gui
def testGuiProjTree_ContextMenu(qtbot, monkeypatch, nwGUI, fncDir, mockRnd):
    """Test the building of the project tree context menu. All this does
    is test that the menu builds. It doesn't open the actual menu,
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))
    monkeypatch.setattr(QMenu, "exec_", lambda *a: None)

    nwTree = nwGUI.projView

    # Create a project
    prjDir = os.path.join(fncDir, "project")
    buildTestProject(nwGUI, prjDir)

    # Handles for new objects
    hNovelRoot   = "0000000000008"
    hTitlePage   = "000000000000c"
    hChapterDir  = "000000000000d"
    hChapterFile = "000000000000e"
    hCharRoot    = "000000000000a"
    hCharNote    = "0000000000011"
    hNovelNote   = "0000000000012"

    projTree = nwGUI.projView.projTree
    projTree.setExpandedFromHandle(None, True)

    projTree._addTrashRoot()
    hTrashRoot = projTree.theProject.tree.trashRoot()

    projTree.setSelectedHandle(hCharRoot)
    projTree.newTreeItem(nwItemType.FILE)
    projTree.setSelectedHandle(hNovelRoot)
    projTree.newTreeItem(nwItemType.FILE, isNote=True)

    def itemPos(tHandle):
        return projTree.visualItemRect(projTree._getTreeItem(tHandle)).center()

    # No item under menu
    assert projTree._openContextMenu(projTree.viewport().rect().bottomRight()) is False

    # Generate the possible menu combinarions
    assert projTree._openContextMenu(itemPos(hTrashRoot)) is True
    assert projTree._openContextMenu(itemPos(hNovelRoot)) is True
    assert projTree._openContextMenu(itemPos(hNovelNote)) is True
    assert projTree._openContextMenu(itemPos(hTitlePage)) is True
    assert projTree._openContextMenu(itemPos(hChapterDir)) is True
    assert projTree._openContextMenu(itemPos(hChapterFile)) is True
    assert projTree._openContextMenu(itemPos(hCharRoot)) is True
    assert projTree._openContextMenu(itemPos(hCharNote)) is True

    # Check the keyboard shortcut handler as well
    projTree.setSelectedHandle(hNovelRoot)
    assert projTree.openContextOnSelected() is True
    projTree.clearSelection()
    assert projTree.openContextOnSelected() is False

    # Direct Edit Functions
    # =====================
    # Trigger the dedicated functions the menu entries connect to
    nwItem = projTree.theProject.tree[hNovelNote]

    # Toggle exported flag
    assert nwItem.isExported is True
    projTree._toggleItemExported(hNovelNote)
    assert nwItem.isExported is False

    # Change item status
    assert nwItem.itemStatus == "s000000"
    projTree._changeItemStatus(hNovelNote, "s000001")
    assert nwItem.itemStatus == "s000001"

    # Change item importance
    assert nwItem.itemImport == "i000004"
    projTree._changeItemImport(hNovelNote, "i000005")
    assert nwItem.itemImport == "i000005"

    # Change item layout
    assert nwItem.itemLayout == nwItemLayout.NOTE
    projTree._changeItemLayout(hNovelNote, nwItemLayout.DOCUMENT)
    assert nwItem.itemLayout == nwItemLayout.DOCUMENT
    projTree._changeItemLayout(hNovelNote, nwItemLayout.NOTE)
    assert nwItem.itemLayout == nwItemLayout.NOTE

    # Convert Folders to Documents
    # ============================

    hNewFolderOne = "0000000000013"
    hNewFolderTwo = "0000000000015"

    nwTree.setSelectedHandle(hNovelNote)
    assert nwTree.projTree.newTreeItem(nwItemType.FOLDER) is True
    nwTree.setSelectedHandle(hNewFolderOne)
    assert nwTree.projTree.newTreeItem(nwItemType.FILE) is True

    nwTree.setSelectedHandle(hNovelNote)
    assert nwTree.projTree.newTreeItem(nwItemType.FOLDER) is True
    nwTree.setSelectedHandle(hNewFolderTwo)
    assert nwTree.projTree.newTreeItem(nwItemType.FILE, isNote=True) is True

    # Click no on the dialog
    with monkeypatch.context() as mp:
        mp.setattr(QMessageBox, "question", lambda *a: QMessageBox.No)
        projTree._covertFolderToFile(hNewFolderOne, nwItemLayout.DOCUMENT)
        assert nwGUI.theProject.tree[hNewFolderOne].isFolderType()

    # Convert the first folder to a document
    projTree._covertFolderToFile(hNewFolderOne, nwItemLayout.DOCUMENT)
    assert nwGUI.theProject.tree[hNewFolderOne].isFileType()
    assert nwGUI.theProject.tree[hNewFolderOne].isDocumentLayout()

    # Convert the second folder to a note
    projTree._covertFolderToFile(hNewFolderTwo, nwItemLayout.NOTE)
    assert nwGUI.theProject.tree[hNewFolderTwo].isFileType()
    assert nwGUI.theProject.tree[hNewFolderTwo].isNoteLayout()

    # qtbot.stop()

# END Test testGuiProjTree_ContextMenu
