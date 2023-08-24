"""
novelWriter – Main GUI Project Tree Class Tester
================================================

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

from pathlib import Path

from tools import C, buildTestProject
from mocked import causeOSError

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QMenu, QTreeWidgetItem, QDialog

from novelwriter import CONFIG, SHARED
from novelwriter.enum import nwItemLayout, nwItemType, nwItemClass
from novelwriter.guimain import GuiMain
from novelwriter.gui.projtree import GuiProjectTree, GuiProjectView
from novelwriter.dialogs.docmerge import GuiDocMerge
from novelwriter.dialogs.docsplit import GuiDocSplit
from novelwriter.dialogs.editlabel import GuiEditLabel


@pytest.mark.gui
def testGuiProjTree_NewItems(qtbot, caplog, monkeypatch, nwGUI, projPath, mockRnd):
    """Test adding and removing items from the project tree."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    projView = nwGUI.projView
    projTree = nwGUI.projView.projTree
    theProject = SHARED.project

    # Try to add item with no project
    assert projView.projTree.newTreeItem(nwItemType.FILE) is False

    # Create a project
    buildTestProject(nwGUI, projPath)

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
    projView.setSelectedHandle(C.hNovelRoot)
    assert projView.projTree.newTreeItem(nwItemType.FOLDER) is True
    assert theProject.tree["0000000000011"].itemParent == C.hNovelRoot
    assert theProject.tree["0000000000011"].itemRoot == C.hNovelRoot
    assert theProject.tree["0000000000011"].itemClass == nwItemClass.NOVEL

    # Add a new file in the new folder
    projView.setSelectedHandle("0000000000011")
    assert projView.projTree.newTreeItem(nwItemType.FILE) is True
    assert theProject.tree["0000000000012"].itemParent == "0000000000011"
    assert theProject.tree["0000000000012"].itemRoot == C.hNovelRoot
    assert theProject.tree["0000000000012"].itemClass == nwItemClass.NOVEL

    # Add a new chapter next to the other new file
    projView.setSelectedHandle("0000000000012")
    assert projView.projTree.newTreeItem(nwItemType.FILE, hLevel=2) is True
    assert theProject.tree["0000000000013"].itemParent == "0000000000011"
    assert theProject.tree["0000000000013"].itemRoot == C.hNovelRoot
    assert theProject.tree["0000000000013"].itemClass == nwItemClass.NOVEL
    assert nwGUI.openDocument("0000000000013")
    assert nwGUI.docEditor.getText() == "## New Chapter\n\n"

    # Add a new scene next to the other new file
    projView.setSelectedHandle("0000000000012")
    assert projView.projTree.newTreeItem(nwItemType.FILE, hLevel=3) is True
    assert theProject.tree["0000000000014"].itemParent == "0000000000011"
    assert theProject.tree["0000000000014"].itemRoot == C.hNovelRoot
    assert theProject.tree["0000000000014"].itemClass == nwItemClass.NOVEL
    assert nwGUI.openDocument("0000000000014")
    assert nwGUI.docEditor.getText() == "### New Scene\n\n"

    # Add a new file to the characters folder
    projView.setSelectedHandle(C.hCharRoot)
    assert projView.projTree.newTreeItem(nwItemType.FILE, hLevel=1, isNote=True) is True
    assert theProject.tree["0000000000015"].itemParent == C.hCharRoot
    assert theProject.tree["0000000000015"].itemRoot == C.hCharRoot
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
        projTree.renameTreeItem(C.hPlotRoot) is True
        assert theProject.tree[C.hPlotRoot].itemName == "Stuff"

    # Rename invalid folder
    projTree.renameTreeItem("0000000000000") is False

    # Other Checks
    # ============

    # Also check error handling in reveal function
    assert projView.projTree.revealNewTreeItem("abc") is False

    # Add an item that cannot be displayed in the tree
    nHandle = theProject.newFile("Test", None)
    assert projView.projTree.revealNewTreeItem(nHandle) is False

    # Adding an invalid item directly to the tree should also fail
    assert projView.projTree._addTreeItem(None) is None

    # Clean up
    # qtbot.stop()
    nwGUI.closeProject()

# END Test testGuiProjTree_NewItems


@pytest.mark.gui
def testGuiProjTree_MoveItems(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test adding and removing items from the project tree."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    projView = nwGUI.projView
    projTree = nwGUI.projView.projTree

    # Try to move item with no project
    assert projView.projTree.moveTreeItem(1) is False

    # Create a project
    buildTestProject(nwGUI, projPath)

    # Move Documents
    # ==============

    # Add some files
    projView.setSelectedHandle(C.hChapterDir)
    assert projTree.newTreeItem(nwItemType.FILE) is True
    assert projTree.newTreeItem(nwItemType.FILE) is True
    assert projTree.newTreeItem(nwItemType.FILE) is True
    assert projTree.getTreeFromHandle(C.hChapterDir) == [
        C.hChapterDir, C.hChapterDoc, C.hSceneDoc,
        "0000000000010", "0000000000011", "0000000000012",
    ]

    # Move with no selections
    projTree.clearSelection()
    assert projTree.moveTreeItem(1) is False

    # Move second item up twice (should give same result)
    projView.setSelectedHandle(C.hSceneDoc)
    assert projTree.moveTreeItem(-1) is True
    assert projTree.getTreeFromHandle(C.hChapterDir) == [
        C.hChapterDir, C.hSceneDoc, C.hChapterDoc,
        "0000000000010", "0000000000011", "0000000000012",
    ]
    assert projTree.moveTreeItem(-1) is False
    assert projTree.getTreeFromHandle(C.hChapterDir) == [
        C.hChapterDir, C.hSceneDoc, C.hChapterDoc,
        "0000000000010", "0000000000011", "0000000000012",
    ]

    # Restore
    assert projTree.moveTreeItem(1) is True
    assert projTree.getTreeFromHandle(C.hChapterDir) == [
        C.hChapterDir, C.hChapterDoc, C.hSceneDoc,
        "0000000000010", "0000000000011", "0000000000012",
    ]

    # Move fifth item down twice (should give same result)
    projView.setSelectedHandle("0000000000011")
    assert projTree.moveTreeItem(1) is True
    assert projTree.getTreeFromHandle(C.hChapterDir) == [
        C.hChapterDir, C.hChapterDoc, C.hSceneDoc,
        "0000000000010", "0000000000012", "0000000000011",
    ]
    assert projTree.moveTreeItem(1) is False
    assert projTree.getTreeFromHandle(C.hChapterDir) == [
        C.hChapterDir, C.hChapterDoc, C.hSceneDoc,
        "0000000000010", "0000000000012", "0000000000011",
    ]

    # Restore
    assert projTree.moveTreeItem(-1) is True
    assert projTree.getTreeFromHandle(C.hChapterDir) == [
        C.hChapterDir, C.hChapterDoc, C.hSceneDoc,
        "0000000000010", "0000000000011", "0000000000012",
    ]

    # Move down again, and restore via undo
    projView.setSelectedHandle("0000000000011")
    assert projTree.moveTreeItem(1) is True
    assert projTree.getTreeFromHandle(C.hChapterDir) == [
        C.hChapterDir, C.hChapterDoc, C.hSceneDoc,
        "0000000000010", "0000000000012", "0000000000011",
    ]
    assert projTree.undoLastMove() is True
    assert projTree.getTreeFromHandle(C.hChapterDir) == [
        C.hChapterDir, C.hChapterDoc, C.hSceneDoc,
        "0000000000010", "0000000000011", "0000000000012",
    ]

    # Root Folder
    # ===========

    projView.setSelectedHandle(C.hNovelRoot)
    assert SHARED.project.tree._order.index(C.hNovelRoot) == 0

    # Move novel folder up
    assert projTree.moveTreeItem(-1) is False
    assert SHARED.project.tree._order.index(C.hNovelRoot) == 0

    # Move novel folder down
    assert projTree.moveTreeItem(1) is True
    assert SHARED.project.tree._order.index(C.hNovelRoot) == 1

    # Move novel folder up again
    assert projTree.moveTreeItem(-1) is True
    assert SHARED.project.tree._order.index(C.hNovelRoot) == 0

    # Clean up
    # qtbot.stop()
    nwGUI.closeProject()

# END Test testGuiProjTree_MoveItems


@pytest.mark.gui
def testGuiProjTree_RequestDeleteItem(qtbot, caplog, monkeypatch, nwGUI, projPath, mockRnd):
    """Test external requests for removing items from project tree."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    projView = nwGUI.projView
    projTree = nwGUI.projView.projTree

    # Try to run with no project
    assert projView.requestDeleteItem() is False

    # Create a project
    buildTestProject(nwGUI, projPath)

    # Try emptying the trash already now, when there is no trash folder
    assert projView.emptyTrash() is False

    # Add some files
    projView.setSelectedHandle(C.hChapterDir)
    assert projTree.newTreeItem(nwItemType.FILE) is True
    assert projTree.newTreeItem(nwItemType.FILE) is True
    assert projTree.newTreeItem(nwItemType.FILE) is True
    assert projTree.getTreeFromHandle(C.hChapterDir) == [
        C.hChapterDir, C.hChapterDoc, C.hSceneDoc,
        "0000000000010", "0000000000011", "0000000000012",
    ]

    # Delete item without focus -> blocked
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: False)
    projView.setSelectedHandle("0000000000012")
    assert projView.requestDeleteItem() is False
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: True)

    # No selection made
    projTree.clearSelection()
    caplog.clear()
    assert projView.requestDeleteItem() is False
    assert "no item to delete" in caplog.text

    # Not a valid handle
    projTree.clearSelection()
    caplog.clear()
    assert projView.requestDeleteItem("0000000000000") is False
    assert "No tree item with handle '0000000000000'" in caplog.text

    # Delete Root Folders
    # ===================

    assert projView.requestDeleteItem(C.hNovelRoot) is False  # Novel Root is blocked
    assert projView.requestDeleteItem(C.hCharRoot) is True   # Character Root

    # Delete File
    # ===========

    # Block adding trash folder
    funcPointer = projTree._addTrashRoot
    projTree._addTrashRoot = lambda *a: None
    assert projView.requestDeleteItem("0000000000012") is False
    projTree._addTrashRoot = funcPointer

    # Delete last two documents, which also adds the trash folder
    assert projView.requestDeleteItem("0000000000012") is True
    assert projView.requestDeleteItem("0000000000011") is True
    assert projTree.getTreeFromHandle(C.hChapterDir) == [
        C.hChapterDir, C.hChapterDoc, C.hSceneDoc,
        "0000000000010"
    ]
    trashHandle = SHARED.project.tree.trashRoot
    assert projTree.getTreeFromHandle(trashHandle) == [
        trashHandle, "0000000000012", "0000000000011"
    ]

    # Try to delete the trash folder
    caplog.clear()
    assert projView.requestDeleteItem("0000000000013") is False
    assert "Cannot delete the Trash folder" in caplog.text

    nwGUI.closeProject()

# END Test testGuiProjTree_RequestDeleteItem


@pytest.mark.gui
def testGuiProjTree_MoveItemToTrash(qtbot, caplog, monkeypatch, nwGUI, projPath, mockRnd):
    """Test moving items to Trash."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    theProject = SHARED.project
    projTree = nwGUI.projView.projTree

    # Create a project
    buildTestProject(nwGUI, projPath)

    # Invalid item
    caplog.clear()
    assert projTree.moveItemToTrash(C.hInvalid) is False
    assert "Could not find tree item for deletion" in caplog.text

    # Root folders cannot be moved to Trash
    caplog.clear()
    assert projTree.moveItemToTrash(C.hNovelRoot) is False
    assert "Root folders cannot be moved to Trash" in caplog.text

    # Block adding trash folder
    funcPointer = projTree._addTrashRoot
    projTree._addTrashRoot = lambda *a: None

    caplog.clear()
    assert projTree.moveItemToTrash(C.hTitlePage) is False
    assert theProject.tree.isTrash(C.hTitlePage) is False
    assert "Could not delete item" in caplog.text

    projTree._addTrashRoot = funcPointer

    # User cancels action
    with monkeypatch.context() as mp:
        mp.setattr(QMessageBox, "result", lambda *a: QMessageBox.No)
        assert projTree.moveItemToTrash(C.hTitlePage) is False
        assert theProject.tree.isTrash(C.hTitlePage) is False

    # Move a document to Trash
    assert projTree.moveItemToTrash(C.hTitlePage) is True
    assert theProject.tree.isTrash(C.hTitlePage) is True

    # Cannot be moved again
    caplog.clear()
    assert projTree.moveItemToTrash(C.hTitlePage) is False
    assert "Item is already in the Trash folder" in caplog.text

    nwGUI.closeProject()

# END Test testGuiProjTree_MoveItemToTrash


@pytest.mark.gui
def testGuiProjTree_PermanentlyDeleteItem(qtbot, caplog, monkeypatch, nwGUI, projPath, mockRnd):
    """Test permanently deleting items."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    theProject = SHARED.project
    projTree = nwGUI.projView.projTree

    # Create a project
    buildTestProject(nwGUI, projPath)

    # Invalid item
    caplog.clear()
    assert projTree.permDeleteItem(C.hInvalid) is False
    assert "Could not find tree item for deletion" in caplog.text

    # Not deleting root item in use
    caplog.clear()
    assert projTree.permDeleteItem(C.hNovelRoot) is False
    assert "Root folders can only be deleted when they are empty" in caplog.text
    assert C.hNovelRoot in theProject.tree

    # Deleting unused root item is allowed
    caplog.clear()
    assert projTree.permDeleteItem(C.hPlotRoot) is True
    assert C.hPlotRoot not in theProject.tree

    # User cancels action
    with monkeypatch.context() as mp:
        mp.setattr(QMessageBox, "result", lambda *a: QMessageBox.No)
        assert projTree.permDeleteItem(C.hTitlePage) is False
        assert C.hTitlePage in theProject.tree

    # Deleting file is OK, and if it is open, it should close
    assert nwGUI.openDocument(C.hTitlePage) is True
    assert nwGUI.docEditor.docHandle == C.hTitlePage
    assert projTree.permDeleteItem(C.hTitlePage) is True
    assert C.hTitlePage not in theProject.tree
    assert nwGUI.docEditor.docHandle is None

    # Deleting folder + files recursively is ok
    assert projTree.permDeleteItem(C.hChapterDir) is True
    assert C.hChapterDir not in theProject.tree
    assert C.hChapterDoc not in theProject.tree
    assert C.hSceneDoc not in theProject.tree

    nwGUI.closeProject()

# END Test testGuiProjTree_PermanentlyDeleteItem


@pytest.mark.gui
def testGuiProjTree_EmptyTrash(qtbot, caplog, monkeypatch, nwGUI, projPath, mockRnd):
    """Test emptying Trash."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    theProject = SHARED.project
    projTree = nwGUI.projView.projTree

    # No project open
    caplog.clear()
    assert projTree.emptyTrash() is False
    assert "No project open" in caplog.text

    # Create a project
    buildTestProject(nwGUI, projPath)

    # No Trash folder
    assert projTree.emptyTrash() is False

    # Move some documents to Trash
    assert projTree.moveItemToTrash(C.hTitlePage) is True
    assert projTree.moveItemToTrash(C.hChapterDir) is True

    assert theProject.tree.isTrash(C.hTitlePage) is True
    assert theProject.tree.isTrash(C.hChapterDir) is True
    assert theProject.tree.isTrash(C.hChapterDoc) is True
    assert theProject.tree.isTrash(C.hSceneDoc) is True

    # User cancels
    with monkeypatch.context() as mp:
        mp.setattr(QMessageBox, "result", lambda *a: QMessageBox.No)
        assert projTree.emptyTrash() is False
        assert C.hTitlePage in theProject.tree
        assert C.hChapterDir in theProject.tree
        assert C.hChapterDoc in theProject.tree
        assert C.hSceneDoc in theProject.tree

    # Run again to empty all items
    assert projTree.emptyTrash() is True
    assert C.hTitlePage not in theProject.tree
    assert C.hChapterDir not in theProject.tree
    assert C.hChapterDoc not in theProject.tree
    assert C.hSceneDoc not in theProject.tree

    # Running Empty Trash again is cancelled due to empty folder
    assert projTree.emptyTrash() is False

    nwGUI.closeProject()

# END Test testGuiProjTree_EmptyTrash


@pytest.mark.gui
def testGuiProjTree_ContextMenu(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test the building of the project tree context menu. All this does
    is test that the menu builds. It doesn't open the actual menu,
    """
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))
    monkeypatch.setattr(QMenu, "exec_", lambda *a: None)

    # Create a project
    buildTestProject(nwGUI, projPath)

    # Handles for new objects
    hCharNote     = "0000000000011"
    hNovelNote    = "0000000000012"
    hSubNote      = "0000000000013"
    hNewFolderOne = "0000000000014"
    hNewFolderTwo = "0000000000016"

    projView = nwGUI.projView
    projTree = nwGUI.projView.projTree
    projTree.setExpandedFromHandle(None, True)

    projTree._addTrashRoot()
    hTrashRoot = SHARED.project.tree.trashRoot

    projTree.setSelectedHandle(C.hCharRoot)
    projTree.newTreeItem(nwItemType.FILE)
    projTree.setSelectedHandle(C.hNovelRoot)
    projTree.newTreeItem(nwItemType.FILE, isNote=True)

    SHARED.project.newFile("SubNote", hNovelNote)
    projTree.revealNewTreeItem(hSubNote)
    assert SHARED.project.tree[hSubNote].itemParent == hNovelNote

    def itemPos(tHandle):
        return projTree.visualItemRect(projTree._getTreeItem(tHandle)).center()

    # No item under menu
    assert projTree._openContextMenu(projTree.viewport().rect().bottomRight()) is False

    # Generate the possible menu combinations
    assert projTree._openContextMenu(itemPos(hTrashRoot)) is True
    assert projTree._openContextMenu(itemPos(C.hNovelRoot)) is True
    assert projTree._openContextMenu(itemPos(hNovelNote)) is True
    assert projTree._openContextMenu(itemPos(C.hTitlePage)) is True
    assert projTree._openContextMenu(itemPos(C.hChapterDir)) is True
    assert projTree._openContextMenu(itemPos(C.hChapterDoc)) is True
    assert projTree._openContextMenu(itemPos(C.hCharRoot)) is True
    assert projTree._openContextMenu(itemPos(hCharNote)) is True
    assert projTree._openContextMenu(itemPos(hNovelNote)) is True

    # Check the keyboard shortcut handler as well
    projTree.setSelectedHandle(C.hNovelRoot)
    assert projTree.openContextOnSelected() is True
    projTree.clearSelection()
    assert projTree.openContextOnSelected() is False

    # Direct Edit Functions
    # =====================
    # Trigger the dedicated functions the menu entries connect to
    nwItem = SHARED.project.tree[hNovelNote]

    # Toggle active flag
    assert nwItem.isActive is True
    projTree._toggleItemActive(hNovelNote)
    assert nwItem.isActive is False

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

    projView.setSelectedHandle(hNovelNote)
    assert projView.projTree.newTreeItem(nwItemType.FOLDER) is True
    projView.setSelectedHandle(hNewFolderOne)
    assert projView.projTree.newTreeItem(nwItemType.FILE) is True

    projView.setSelectedHandle(hNovelNote)
    assert projView.projTree.newTreeItem(nwItemType.FOLDER) is True
    projView.setSelectedHandle(hNewFolderTwo)
    assert projView.projTree.newTreeItem(nwItemType.FILE, isNote=True) is True

    # Click no on the dialog
    with monkeypatch.context() as mp:
        mp.setattr(QMessageBox, "result", lambda *a: QMessageBox.No)
        projTree._covertFolderToFile(hNewFolderOne, nwItemLayout.DOCUMENT)
        assert SHARED.project.tree[hNewFolderOne].isFolderType()

    # Convert the first folder to a document
    projTree._covertFolderToFile(hNewFolderOne, nwItemLayout.DOCUMENT)
    assert SHARED.project.tree[hNewFolderOne].isFileType()
    assert SHARED.project.tree[hNewFolderOne].isDocumentLayout()

    # Convert the second folder to a note
    projTree._covertFolderToFile(hNewFolderTwo, nwItemLayout.NOTE)
    assert SHARED.project.tree[hNewFolderTwo].isFileType()
    assert SHARED.project.tree[hNewFolderTwo].isNoteLayout()

    # qtbot.stop()

# END Test testGuiProjTree_ContextMenu


@pytest.mark.gui
def testGuiProjTree_MergeDocuments(qtbot, monkeypatch, nwGUI, projPath, mockRnd, ipsumText):
    """Test the merge document function."""
    mergeData = {}

    monkeypatch.setattr(GuiDocMerge, "__init__", lambda *a: None)
    monkeypatch.setattr(GuiDocMerge, "exec_", lambda *a: None)
    monkeypatch.setattr(GuiDocMerge, "result", lambda *a: QDialog.Accepted)
    monkeypatch.setattr(GuiDocMerge, "getData", lambda *a: mergeData)

    # Create a project
    buildTestProject(nwGUI, projPath)

    theProject = SHARED.project
    projTree = nwGUI.projView.projTree

    mergedDoc1 = "0000000000014"

    # Create File to Merge
    hChapter1 = theProject.newFile("Chapter 1", C.hNovelRoot)
    hSceneOne11 = theProject.newFile("Scene 1.1", hChapter1)
    hSceneOne12 = theProject.newFile("Scene 1.2", hChapter1)
    hSceneOne13 = theProject.newFile("Scene 1.3", hChapter1)

    docText1 = "\n\n".join(ipsumText[0:2]) + "\n\n"
    docText2 = "\n\n".join(ipsumText[1:3]) + "\n\n"
    docText3 = "\n\n".join(ipsumText[2:4]) + "\n\n"
    docText4 = "\n\n".join(ipsumText[3:5]) + "\n\n"

    lenText1 = len(docText1)
    lenText2 = len(docText2)
    lenText3 = len(docText3)
    lenText4 = len(docText4)
    lenAll = lenText1 + lenText2 + lenText3 + lenText4

    theProject.writeNewFile(hChapter1, 2, True, docText1)
    theProject.writeNewFile(hSceneOne11, 3, True, docText2)
    theProject.writeNewFile(hSceneOne12, 3, True, docText3)
    theProject.writeNewFile(hSceneOne13, 3, True, docText4)

    projTree.revealNewTreeItem(hChapter1)
    projTree.revealNewTreeItem(hSceneOne11)
    projTree.revealNewTreeItem(hSceneOne12)
    projTree.revealNewTreeItem(hSceneOne13)

    # Invalid file handle
    assert projTree._mergeDocuments(C.hInvalid, False) is False

    # Cannot merge root item
    assert projTree._mergeDocuments(C.hNovelRoot, False) is False

    # Merge to new file, but there is now merge data
    mergeData.clear()
    assert projTree._mergeDocuments(hChapter1, True) is False

    # Merge to New Doc
    # ================

    # Set merge job for new documents
    mergeData["finalItems"] = [hChapter1, hSceneOne11, hSceneOne12, hSceneOne13]
    mergeData["moveToTrash"] = False

    # User cancels merge
    with monkeypatch.context() as mp:
        mp.setattr(GuiDocMerge, "result", lambda *a: QDialog.Rejected)
        assert projTree._mergeDocuments(hChapter1, True) is False

    # The merge goes through
    assert projTree._mergeDocuments(hChapter1, True) is True
    assert len(theProject.storage.getDocument(mergedDoc1).readDocument()) > lenAll

    # Merge to Existing Doc
    # =====================

    # Set merge job for parent document
    mergeData["finalItems"] = [hSceneOne11, hSceneOne12, hSceneOne13]
    mergeData["moveToTrash"] = False

    # Merging to a folder is not allowed
    assert projTree._mergeDocuments(C.hChapterDir, False) is False

    # Block writing and check error handling
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert projTree._mergeDocuments(hChapter1, False) is False

    # Successful merge, and move to trash
    mergeData["moveToTrash"] = True
    assert len(theProject.storage.getDocument(hChapter1).readDocument()) < lenAll
    assert projTree._mergeDocuments(hChapter1, False) is True
    assert len(theProject.storage.getDocument(hChapter1).readDocument()) > lenAll

    assert theProject.tree.isTrash(hSceneOne11)
    assert theProject.tree.isTrash(hSceneOne12)
    assert theProject.tree.isTrash(hSceneOne13)

    # qtbot.stop()

# END Test testGuiProjTree_MergeDocuments


@pytest.mark.gui
def testGuiProjTree_SplitDocument(qtbot, monkeypatch, nwGUI, projPath, mockRnd, ipsumText):
    """Test the split document function."""
    splitData = {}
    splitText = []

    monkeypatch.setattr(GuiDocSplit, "__init__", lambda *a: None)
    monkeypatch.setattr(GuiDocSplit, "exec_", lambda *a: None)
    monkeypatch.setattr(GuiDocSplit, "result", lambda *a: QDialog.Accepted)
    monkeypatch.setattr(GuiDocSplit, "getData", lambda *a: (splitData, splitText))

    # Create a project
    buildTestProject(nwGUI, projPath)

    theProject = SHARED.project
    projTree = nwGUI.projView.projTree

    docText = (
        "Text\n\n"
        "##! Prologue\n\nText\n\n"
        "## Chapter One\n\nText\n\n"
        "### Scene One\n\nText\n\n"
        "### Scene Two\n\nText\n\n"
        "## Chapter Two\n\nText\n\n"
        "### Scene Three\n\nText\n\n"
        "### Scene Four\n\nText\n\n"
        "#! New Title\n\nText\n\n"
        "## New Chapter\n\nText\n\n"
        "### New Scene\n\nText\n\n"
        "#### New Section\n\nText\n\n"
    )

    hSplitDoc = theProject.newFile("Split Doc", C.hNovelRoot)
    theProject.writeNewFile(hSplitDoc, 1, True, docText)
    projTree.revealNewTreeItem(hSplitDoc, nHandle=C.hNovelRoot, wordCount=True)

    docText = f"# Split Doc\n\n{docText}"
    splitData["headerList"] = [
        (0, 1, "Split Doc"),
        (4, 2, "Prologue"),
        (8, 2, "Chapter One"),
        (12, 3, "Scene One"),
        (16, 3, "Scene Two"),
        (20, 2, "Chapter Two"),
        (24, 3, "Scene Three"),
        (28, 3, "Scene Four"),
        (32, 1, "New Title"),
        (36, 2, "New Chapter"),
        (40, 3, "New Scene"),
        (44, 4, "New Section"),
    ]

    fstSet = [
        "0000000000011", "0000000000012", "0000000000013", "0000000000014",
        "0000000000015", "0000000000016", "0000000000017", "0000000000018",
        "0000000000019", "000000000001a", "000000000001b", "000000000001c",
    ]
    sndSet = [
        "000000000001d", "000000000001e", "000000000001f", "0000000000020",
        "0000000000021", "0000000000022", "0000000000023", "0000000000024",
        "0000000000025", "0000000000026", "0000000000027", "0000000000028",
    ]
    trdSet = [
        "000000000002a", "000000000002b", "000000000002c", "000000000002d",
        "000000000002e", "000000000002f", "0000000000030", "0000000000031",
        "0000000000032", "0000000000033", "0000000000034", "0000000000035",
    ]

    # Try to split an invalid document and a non-document
    assert projTree._splitDocument(C.hInvalid) is False
    assert projTree._splitDocument(C.hNovelRoot) is False

    # Split into same root folder
    splitData["intoFolder"] = False

    # Writing fails
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert projTree._splitDocument(hSplitDoc) is True
        for tHandle in fstSet:
            assert tHandle in theProject.tree
            assert not (projPath / "content" / f"{tHandle}.nwd").is_file()

    # Writing succeeds
    assert projTree._splitDocument(hSplitDoc) is True
    for tHandle in sndSet:
        assert tHandle in theProject.tree
        assert (projPath / "content" / f"{tHandle}.nwd").is_file()

    # Add to a folder and move source to trash
    splitData["intoFolder"] = True
    splitData["moveToTrash"] = True
    assert projTree._splitDocument(hSplitDoc) is True
    assert "0000000000029" in theProject.tree  # The folder
    for tHandle in trdSet:
        assert tHandle in theProject.tree
        assert (projPath / "content" / f"{tHandle}.nwd").is_file()

    assert theProject.tree.isTrash(hSplitDoc) is True

    # Cancelled by user
    with monkeypatch.context() as mp:
        mp.setattr(GuiDocSplit, "result", lambda *a: QDialog.Rejected)
        assert projTree._splitDocument(hSplitDoc) is False

    # qtbot.stop()

# END Test testGuiProjTree_SplitDocument


@pytest.mark.gui
def testGuiProjTree_Duplicate(qtbot, monkeypatch, nwGUI: GuiMain, projPath, mockRnd):
    """Test the duplicate items function."""
    # Create a project
    buildTestProject(nwGUI, projPath)
    assert len(SHARED.project.tree) == 8

    projTree = nwGUI.projView.projTree
    projTree._getTreeItem(C.hNovelRoot).setExpanded(True)  # type: ignore
    projTree._getTreeItem(C.hChapterDir).setExpanded(True)  # type: ignore

    # Nothing to do
    assert projTree._duplicateFromHandle(C.hInvalid) is False
    assert len(SHARED.project.tree) == 8

    # Duplicate title page, but select no
    with monkeypatch.context() as mp:
        mp.setattr(QMessageBox, "result", lambda *a: QMessageBox.No)
        assert projTree._duplicateFromHandle(C.hTitlePage) is False
        assert len(SHARED.project.tree) == 8

    # Duplicate title page
    assert projTree._duplicateFromHandle(C.hTitlePage) is True
    assert len(SHARED.project.tree) == 9

    # Duplicate folder
    assert projTree._duplicateFromHandle(C.hChapterDir) is True
    assert len(SHARED.project.tree) == 12

    # Duplicate novel root
    assert projTree._duplicateFromHandle(C.hNovelRoot) is True
    assert len(SHARED.project.tree) == 21

    # Check tree order that all items are next to eachother
    assert SHARED.project.tree._order == [
        C.hNovelRoot, C.hTitlePage, "0000000000010", C.hChapterDir, C.hChapterDoc, C.hSceneDoc,
        "0000000000011", "0000000000012", "0000000000013", "0000000000014", "0000000000015",
        "0000000000016", "0000000000017", "0000000000018", "0000000000019", "000000000001a",
        "000000000001b", "000000000001c", C.hPlotRoot, C.hCharRoot, C.hWorldRoot,
    ]

    # Make the duplicator stop early
    content = SHARED.project.storage.contentPath
    assert isinstance(content, Path)
    (content / "000000000001e.nwd").touch()
    assert (content / "000000000001e.nwd").exists()

    # Should only create the folder, and skip the two files because the
    # next handle is already a file
    assert projTree._duplicateFromHandle(C.hChapterDir) is True
    assert len(SHARED.project.tree) == 22

    # qtbot.stop()

# END Test testGuiProjTree_Duplicate


@pytest.mark.gui
def testGuiProjTree_Other(qtbot, monkeypatch, nwGUI: GuiMain, projPath, mockRnd):
    """Test various parts of the project tree class not covered by
    other tests.
    """
    # Create a project
    buildTestProject(nwGUI, projPath)

    projView: GuiProjectView = nwGUI.projView
    projTree: GuiProjectTree = nwGUI.projView.projTree

    # Method: initSettings
    # ====================

    # Test that the scrollbar setting works
    CONFIG.hideVScroll = True
    CONFIG.hideHScroll = True
    projView.initSettings()
    assert projTree.verticalScrollBarPolicy() == Qt.ScrollBarAlwaysOff
    assert projTree.horizontalScrollBarPolicy() == Qt.ScrollBarAlwaysOff

    CONFIG.hideVScroll = False
    CONFIG.hideHScroll = False
    projView.initSettings()
    assert projTree.verticalScrollBarPolicy() == Qt.ScrollBarAsNeeded
    assert projTree.horizontalScrollBarPolicy() == Qt.ScrollBarAsNeeded

    # Method: revealNewTreeItem
    # =========================

    # Send invalid handle
    assert projTree.revealNewTreeItem(C.hInvalid) is False

    # Try to add an orphaned file to the tree
    nHandle = SHARED.project.newFile("Test", C.hNovelRoot)
    SHARED.project.tree[nHandle].setParent(None)  # type: ignore
    assert projTree.revealNewTreeItem(nHandle) is False

    # Try to add an item with unknown parent to the tree
    nHandle = SHARED.project.newFile("Test", C.hNovelRoot)
    SHARED.project.tree[nHandle].setParent(C.hInvalid)  # type: ignore
    assert projTree.revealNewTreeItem(nHandle) is False

    # Method: undoLastMove
    # ====================

    # Nothing to move
    assert projTree.undoLastMove() is False

    projTree._lastMove["item"] = QTreeWidgetItem()
    projTree._lastMove["parent"] = QTreeWidgetItem()
    projTree._lastMove["index"] = 0
    assert projTree.undoLastMove() is False

    projTree._lastMove["item"] = projTree._treeMap[C.hTitlePage]
    projTree._lastMove["parent"] = QTreeWidgetItem()
    projTree._lastMove["index"] = 0
    assert projTree.undoLastMove() is False

    # Slot: _treeDoubleClick
    # ======================

    # Try to open a file with nothings selected
    projTree.clearSelection()
    projTree._treeDoubleClick(QTreeWidgetItem(), 0)
    assert nwGUI.docEditor.docHandle is None

    # When the item cannot be found
    projTree._getTreeItem(C.hTitlePage).setSelected(True)  # type: ignore
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.tree.NWTree.__getitem__", lambda *a: None)
        projTree._treeDoubleClick(QTreeWidgetItem(), 0)
        assert nwGUI.docEditor.docHandle is None

    # Successfully open a file
    projTree._treeDoubleClick(projTree._getTreeItem(C.hTitlePage), 0)
    assert nwGUI.docEditor.docHandle == C.hTitlePage
    projTree._getTreeItem(C.hTitlePage).setSelected(False)  # type: ignore

    # A non-file item should be expanded instead
    projTree._getTreeItem(C.hNovelRoot).setExpanded(False)  # type: ignore
    projTree._getTreeItem(C.hNovelRoot).setSelected(True)  # type: ignore
    projTree._treeDoubleClick(projTree._getTreeItem(C.hNovelRoot), 1)
    assert nwGUI.docEditor.docHandle == C.hTitlePage
    assert projTree._getTreeItem(C.hNovelRoot).isExpanded() is True  # type: ignore

    # Navigate the Tree
    # =================

    # Expand handles
    projTree.setExpandedFromHandle(C.hNovelRoot, True)
    projTree.setSelectedHandle(C.hSceneDoc)
    assert projTree.getSelectedHandle() == C.hSceneDoc

    # Move between documents in that folder
    projTree.moveToNextItem(-1)
    assert projTree.getSelectedHandle() == C.hChapterDoc
    projTree.moveToNextItem(-1)  # Can't move further up
    assert projTree.getSelectedHandle() == C.hChapterDoc
    projTree.moveToNextItem(1)
    assert projTree.getSelectedHandle() == C.hSceneDoc
    projTree.moveToNextItem(1)  # Can't move further down
    assert projTree.getSelectedHandle() == C.hSceneDoc

    # Move up/down the parent/child hierarchy
    projTree.moveToLevel(-1)
    assert projTree.getSelectedHandle() == C.hChapterDir
    projTree.moveToLevel(-1)
    assert projTree.getSelectedHandle() == C.hNovelRoot
    projTree.moveToLevel(-1)  # Can't move further up
    assert projTree.getSelectedHandle() == C.hNovelRoot
    projTree.moveToLevel(1)
    assert projTree.getSelectedHandle() == C.hTitlePage
    projTree.moveToLevel(1)  # Can't move further down
    assert projTree.getSelectedHandle() == C.hTitlePage

    # Move between roots
    projTree.setSelectedHandle(C.hNovelRoot)
    projTree.moveToNextItem(1)
    assert projTree.getSelectedHandle() == C.hPlotRoot
    projTree.moveToNextItem(1)
    assert projTree.getSelectedHandle() == C.hCharRoot
    projTree.moveToNextItem(1)
    assert projTree.getSelectedHandle() == C.hWorldRoot
    projTree.moveToNextItem(1)  # Can't move further down
    assert projTree.getSelectedHandle() == C.hWorldRoot

    # When nothing is selected, nothing happens
    projTree.clearSelection()
    assert projTree.getSelectedHandle() is None
    projTree.moveToNextItem(-1)
    assert projTree.getSelectedHandle() is None
    projTree.moveToNextItem(1)
    assert projTree.getSelectedHandle() is None
    projTree.moveToLevel(-1)
    assert projTree.getSelectedHandle() is None
    projTree.moveToLevel(1)
    assert projTree.getSelectedHandle() is None

    # qtbot.stop()

# END Test testGuiProjTree_Other
