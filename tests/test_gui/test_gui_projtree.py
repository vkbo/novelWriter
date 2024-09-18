"""
novelWriter – Main GUI Project Tree Class Tester
================================================

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

from pathlib import Path

import pytest

from PyQt5.QtCore import QEvent, QMimeData, QPoint, Qt, QTimer
from PyQt5.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent, QMouseEvent
from PyQt5.QtWidgets import QMenu, QMessageBox, QTreeWidget, QTreeWidgetItem

from novelwriter import CONFIG, SHARED
from novelwriter.core.item import NWItem
from novelwriter.core.project import NWProject
from novelwriter.dialogs.docmerge import GuiDocMerge
from novelwriter.dialogs.docsplit import GuiDocSplit
from novelwriter.dialogs.editlabel import GuiEditLabel
from novelwriter.enum import nwFocus, nwItemClass, nwItemLayout, nwItemType
from novelwriter.gui.projtree import GuiProjectTree, GuiProjectView, _TreeContextMenu
from novelwriter.guimain import GuiMain
from novelwriter.types import QtAccepted, QtModNone, QtMouseLeft, QtMouseMiddle, QtRejected

from tests.mocked import causeOSError
from tests.tools import C, buildTestProject


@pytest.mark.gui
def testGuiProjTree_NewItems(qtbot, caplog, monkeypatch, nwGUI, projPath, mockRnd):
    """Test adding and removing items from the project tree."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    projView = nwGUI.projView
    projTree = nwGUI.projView.projTree
    project = SHARED.project

    # Try to add item with no project
    assert projTree.newTreeItem(nwItemType.FILE) is False

    # Create a project
    buildTestProject(nwGUI, projPath)

    # No itemType set
    projTree.clearSelection()
    assert projTree.newTreeItem(None) is False

    # Root Items
    # ==========

    # No class set
    assert projTree.newTreeItem(nwItemType.ROOT) is False

    # Create root item
    assert projTree.newTreeItem(nwItemType.ROOT, nwItemClass.WORLD) is True
    assert "0000000000010" in project.tree

    # File/Folder Items
    # =================

    # No location selected for new item
    projTree.clearSelection()
    caplog.clear()
    assert projTree.newTreeItem(nwItemType.FILE) is False
    assert projTree.newTreeItem(nwItemType.FOLDER) is False
    assert "Did not find anywhere" in caplog.text

    # Create new folder as child of Novel folder
    projView.setSelectedHandle(C.hNovelRoot)
    assert projTree.newTreeItem(nwItemType.FOLDER) is True
    assert project.tree["0000000000011"].itemParent == C.hNovelRoot  # type: ignore
    assert project.tree["0000000000011"].itemRoot == C.hNovelRoot  # type: ignore
    assert project.tree["0000000000011"].itemClass == nwItemClass.NOVEL  # type: ignore

    # Add a new file in the new folder
    projView.setSelectedHandle("0000000000011")
    assert projTree.newTreeItem(nwItemType.FILE) is True
    assert project.tree["0000000000012"].itemParent == "0000000000011"  # type: ignore
    assert project.tree["0000000000012"].itemRoot == C.hNovelRoot  # type: ignore
    assert project.tree["0000000000012"].itemClass == nwItemClass.NOVEL  # type: ignore

    # Add a new chapter next to the other new file
    projView.setSelectedHandle("0000000000012")
    assert projTree.newTreeItem(nwItemType.FILE, hLevel=2) is True
    assert project.tree["0000000000013"].itemParent == "0000000000011"  # type: ignore
    assert project.tree["0000000000013"].itemRoot == C.hNovelRoot  # type: ignore
    assert project.tree["0000000000013"].itemClass == nwItemClass.NOVEL  # type: ignore
    assert nwGUI.openDocument("0000000000013")
    assert nwGUI.docEditor.getText() == "## New Chapter\n\n"
    assert projTree._getItemWordCount("0000000000013") == 2

    # Add a new scene next to the other new file
    projView.setSelectedHandle("0000000000012")
    assert projTree.newTreeItem(nwItemType.FILE, hLevel=3) is True
    assert project.tree["0000000000014"].itemParent == "0000000000011"  # type: ignore
    assert project.tree["0000000000014"].itemRoot == C.hNovelRoot  # type: ignore
    assert project.tree["0000000000014"].itemClass == nwItemClass.NOVEL  # type: ignore
    assert nwGUI.openDocument("0000000000014")
    assert nwGUI.docEditor.getText() == "### New Scene\n\n"
    assert projTree._getItemWordCount("0000000000014") == 2

    # Add a new scene with the content copied from the previous
    assert nwGUI.openDocument("0000000000014")
    nwGUI.docEditor.setPlainText("### New Scene\n\nWith Stuff\n\n")
    nwGUI.saveDocument()
    projView.setSelectedHandle("0000000000014")
    assert projTree.newTreeItem(nwItemType.FILE, copyDoc="0000000000014") is True
    assert project.tree["0000000000015"].itemParent == "0000000000011"  # type: ignore
    assert project.tree["0000000000015"].itemRoot == C.hNovelRoot  # type: ignore
    assert project.tree["0000000000015"].itemClass == nwItemClass.NOVEL  # type: ignore
    assert nwGUI.openDocument("0000000000015")
    assert nwGUI.docEditor.getText() == "### New Scene\n\nWith Stuff\n\n"
    assert projTree._getItemWordCount("0000000000015") == 4

    # Add a new file to the characters folder
    projView.setSelectedHandle(C.hCharRoot)
    assert projTree.newTreeItem(nwItemType.FILE, hLevel=1, isNote=True) is True
    assert project.tree["0000000000016"].itemParent == C.hCharRoot  # type: ignore
    assert project.tree["0000000000016"].itemRoot == C.hCharRoot  # type: ignore
    assert project.tree["0000000000016"].itemClass == nwItemClass.CHARACTER  # type: ignore
    assert nwGUI.openDocument("0000000000016")
    assert nwGUI.docEditor.getText() == "# New Note\n\n"
    assert projTree._getItemWordCount("0000000000016") == 2

    # Make sure the sibling folder bug trap works
    projView.setSelectedHandle("0000000000013")
    project.tree["0000000000013"].setParent(None)  # This should not happen  # type: ignore
    caplog.clear()
    assert projTree.newTreeItem(nwItemType.FILE) is False
    assert "Internal error" in caplog.text
    project.tree["0000000000013"].setParent("0000000000011")  # type: ignore

    # Cancel during creation
    with monkeypatch.context() as mp:
        mp.setattr(GuiEditLabel, "getLabel", lambda *a, **k: ("", False))
        projView.setSelectedHandle("0000000000013")
        assert projTree.newTreeItem(nwItemType.FILE) is False

    # Get the trash folder
    with monkeypatch.context() as mp:
        mp.setattr(NWProject, "trashFolder", lambda *a: None)
        assert projTree._addTrashRoot() is None

    assert isinstance(projTree._addTrashRoot(), QTreeWidgetItem)
    trashHandle = project.trashFolder()
    projView.setSelectedHandle(trashHandle)
    assert projTree.newTreeItem(nwItemType.FILE) is False
    assert "Cannot add new files or folders to the Trash folder" in caplog.text

    # Rename Item
    # ===========

    # Rename plot folder
    with monkeypatch.context() as mp:
        mp.setattr(GuiEditLabel, "getLabel", lambda *a, **k: ("Stuff", True))
        projTree.renameTreeItem(C.hPlotRoot)
        assert project.tree[C.hPlotRoot].itemName == "Stuff"  # type: ignore

    # Other Checks
    # ============

    # Also check error handling in reveal function
    assert projTree.revealNewTreeItem("abc") is False

    # Add an item that cannot be displayed in the tree
    nHandle = project.newFile("Test", None)  # type: ignore
    assert projTree.revealNewTreeItem(nHandle) is False

    # Adding an invalid item directly to the tree should also fail
    assert projTree._addTreeItem(None) is None

    # Setting values for a non-existing tree item should be handled
    projTree.setTreeItemValues(None)
    projTree.setTreeItemValues(C.hInvalid)  # The function used to take handles

    # Clean up
    # qtbot.stop()
    nwGUI.closeProject()


@pytest.mark.gui
def testGuiProjTree_MoveItems(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test adding and removing items from the project tree."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    projView = nwGUI.projView
    projTree = nwGUI.projView.projTree

    # Try to move item with no project
    assert projTree.moveTreeItem(1) is False

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

    # Move down again
    projView.setSelectedHandle("0000000000011")
    assert projTree.moveTreeItem(1) is True
    assert projTree.getTreeFromHandle(C.hChapterDir) == [
        C.hChapterDir, C.hChapterDoc, C.hSceneDoc,
        "0000000000010", "0000000000012", "0000000000011",
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


@pytest.mark.gui
def testGuiProjTree_MoveItemToTrash(qtbot, caplog, monkeypatch, nwGUI, projPath, mockRnd):
    """Test moving items to Trash."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    project = SHARED.project
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
    assert project.tree.isTrash(C.hTitlePage) is False
    assert "Could not delete item" in caplog.text

    projTree._addTrashRoot = funcPointer

    # User cancels action
    with monkeypatch.context() as mp:
        mp.setattr(QMessageBox, "result", lambda *a: QMessageBox.StandardButton.No)
        assert projTree.moveItemToTrash(C.hTitlePage) is False
        assert project.tree.isTrash(C.hTitlePage) is False

    # Move a document to Trash
    assert projTree.moveItemToTrash(C.hTitlePage) is True
    assert project.tree.isTrash(C.hTitlePage) is True

    # Cannot be moved again
    caplog.clear()
    assert projTree.moveItemToTrash(C.hTitlePage) is False
    assert "Item is already in the Trash folder" in caplog.text

    nwGUI.closeProject()


@pytest.mark.gui
def testGuiProjTree_PermanentlyDeleteItem(qtbot, caplog, monkeypatch, nwGUI, projPath, mockRnd):
    """Test permanently deleting items."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    project = SHARED.project
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
    assert C.hNovelRoot in project.tree

    # Deleting unused root item is allowed
    caplog.clear()
    assert projTree.permDeleteItem(C.hPlotRoot) is True
    assert C.hPlotRoot not in project.tree

    # User cancels action
    with monkeypatch.context() as mp:
        mp.setattr(QMessageBox, "result", lambda *a: QMessageBox.StandardButton.No)
        assert projTree.permDeleteItem(C.hTitlePage) is False
        assert C.hTitlePage in project.tree

    # Deleting file is OK, and if it is open, it should close
    assert nwGUI.openDocument(C.hTitlePage) is True
    assert nwGUI.docEditor.docHandle == C.hTitlePage
    assert projTree.permDeleteItem(C.hTitlePage) is True
    assert C.hTitlePage not in project.tree
    assert nwGUI.docEditor.docHandle is None

    # Deleting folder + files recursively is ok
    assert projTree.permDeleteItem(C.hChapterDir) is True
    assert C.hChapterDir not in project.tree
    assert C.hChapterDoc not in project.tree
    assert C.hSceneDoc not in project.tree

    nwGUI.closeProject()


@pytest.mark.gui
def testGuiProjTree_EmptyTrash(qtbot, caplog, monkeypatch, nwGUI, projPath, mockRnd):
    """Test emptying Trash."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    project = SHARED.project
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

    assert project.tree.isTrash(C.hTitlePage) is True
    assert project.tree.isTrash(C.hChapterDir) is True
    assert project.tree.isTrash(C.hChapterDoc) is True
    assert project.tree.isTrash(C.hSceneDoc) is True

    # User cancels
    with monkeypatch.context() as mp:
        mp.setattr(QMessageBox, "result", lambda *a: QMessageBox.StandardButton.No)
        assert projTree.emptyTrash() is False
        assert C.hTitlePage in project.tree
        assert C.hChapterDir in project.tree
        assert C.hChapterDoc in project.tree
        assert C.hSceneDoc in project.tree

    # Run again to empty all items
    assert projTree.emptyTrash() is True
    assert C.hTitlePage not in project.tree
    assert C.hChapterDir not in project.tree
    assert C.hChapterDoc not in project.tree
    assert C.hSceneDoc not in project.tree

    # Running Empty Trash again is cancelled due to empty folder
    assert projTree.emptyTrash() is False

    nwGUI.closeProject()


@pytest.mark.gui
def testGuiProjTree_MergeDocuments(qtbot, monkeypatch, nwGUI, projPath, mockRnd, ipsumText):
    """Test the merge document function."""
    mergeData = {}

    monkeypatch.setattr(GuiDocMerge, "__init__", lambda *a: None)
    monkeypatch.setattr(GuiDocMerge, "exec", lambda *a: None)
    monkeypatch.setattr(GuiDocMerge, "softDelete", lambda *a: None)
    monkeypatch.setattr(GuiDocMerge, "result", lambda *a: QtAccepted)
    monkeypatch.setattr(GuiDocMerge, "data", lambda *a: mergeData)

    buildTestProject(nwGUI, projPath)

    project = SHARED.project
    projTree = nwGUI.projView.projTree

    mergedDoc1 = "0000000000014"

    # Create File to Merge
    hChapter1 = project.newFile("Chapter 1", C.hNovelRoot)
    hSceneOne11 = project.newFile("Scene 1.1", hChapter1)  # type: ignore
    hSceneOne12 = project.newFile("Scene 1.2", hChapter1)  # type: ignore
    hSceneOne13 = project.newFile("Scene 1.3", hChapter1)  # type: ignore

    docText1 = "\n\n".join(ipsumText[0:2]) + "\n\n"
    docText2 = "\n\n".join(ipsumText[1:3]) + "\n\n"
    docText3 = "\n\n".join(ipsumText[2:4]) + "\n\n"
    docText4 = "\n\n".join(ipsumText[3:5]) + "\n\n"

    lenText1 = len(docText1)
    lenText2 = len(docText2)
    lenText3 = len(docText3)
    lenText4 = len(docText4)
    lenAll = lenText1 + lenText2 + lenText3 + lenText4

    project.writeNewFile(hChapter1, 2, True, docText1)  # type: ignore
    project.writeNewFile(hSceneOne11, 3, True, docText2)  # type: ignore
    project.writeNewFile(hSceneOne12, 3, True, docText3)  # type: ignore
    project.writeNewFile(hSceneOne13, 3, True, docText4)  # type: ignore

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
        mp.setattr(GuiDocMerge, "result", lambda *a: QtRejected)
        assert projTree._mergeDocuments(hChapter1, True) is False

    # The merge goes through
    assert projTree._mergeDocuments(hChapter1, True) is True
    assert len(project.storage.getDocument(mergedDoc1).readDocument()) > lenAll  # type: ignore

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
    assert len(project.storage.getDocument(hChapter1).readDocument()) < lenAll  # type: ignore
    assert projTree._mergeDocuments(hChapter1, False) is True
    assert len(project.storage.getDocument(hChapter1).readDocument()) > lenAll  # type: ignore

    assert project.tree.isTrash(hSceneOne11)  # type: ignore
    assert project.tree.isTrash(hSceneOne12)  # type: ignore
    assert project.tree.isTrash(hSceneOne13)  # type: ignore

    # qtbot.stop()


@pytest.mark.gui
def testGuiProjTree_SplitDocument(qtbot, monkeypatch, nwGUI, projPath, mockRnd, ipsumText):
    """Test the split document function."""
    splitData = {}
    splitText = []

    monkeypatch.setattr(GuiDocSplit, "__init__", lambda *a: None)
    monkeypatch.setattr(GuiDocSplit, "exec", lambda *a: None)
    monkeypatch.setattr(GuiDocSplit, "softDelete", lambda *a: None)
    monkeypatch.setattr(GuiDocSplit, "result", lambda *a: QtAccepted)
    monkeypatch.setattr(GuiDocSplit, "data", lambda *a: (splitData, splitText))

    # Create a project
    buildTestProject(nwGUI, projPath)

    project = SHARED.project
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

    hSplitDoc = project.newFile("Split Doc", C.hNovelRoot)
    project.writeNewFile(hSplitDoc, 1, True, docText)  # type: ignore
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
            assert tHandle in project.tree
            assert not (projPath / "content" / f"{tHandle}.nwd").is_file()

    # Writing succeeds
    assert projTree._splitDocument(hSplitDoc) is True
    for tHandle in sndSet:
        assert tHandle in project.tree
        assert (projPath / "content" / f"{tHandle}.nwd").is_file()

    # Add to a folder and move source to trash
    splitData["intoFolder"] = True
    splitData["moveToTrash"] = True
    assert projTree._splitDocument(hSplitDoc) is True
    assert "0000000000029" in project.tree  # The folder
    for tHandle in trdSet:
        assert tHandle in project.tree
        assert (projPath / "content" / f"{tHandle}.nwd").is_file()

    assert project.tree.isTrash(hSplitDoc) is True  # type: ignore

    # Cancelled by user
    with monkeypatch.context() as mp:
        mp.setattr(GuiDocSplit, "result", lambda *a: QtRejected)
        assert projTree._splitDocument(hSplitDoc) is False

    # qtbot.stop()


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
        mp.setattr(QMessageBox, "result", lambda *a: QMessageBox.StandardButton.No)
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

    # Check tree order that all items are next to each other
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


@pytest.mark.gui
def testGuiProjTree_AutoScroll(qtbot, monkeypatch, nwGUI: GuiMain, projPath, mockRnd):
    """Test the auto scroll feature."""
    buildTestProject(nwGUI, projPath)
    projTree: GuiProjectTree = nwGUI.projView.projTree

    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda parent, text: (text, True))
    monkeypatch.setattr(QTreeWidget, "dragMoveEvent", lambda *a, **k: None)
    monkeypatch.setattr(QTimer, "isActive", lambda *a: False)
    monkeypatch.setattr(QTimer, "start", lambda *a: None)

    projTree.setSelectedHandle(C.hChapterDir, True)
    projTree._getTreeItem(C.hChapterDir).setExpanded(True)  # type: ignore
    for i in range(100):
        projTree.newTreeItem(nwItemType.FILE, None, 3, False)

    projTree.setSelectedHandle("0000000000015", True)
    nwGUI.resize(500, 500)

    action = Qt.DropAction.MoveAction
    mime = QMimeData()
    mouse = QtMouseLeft
    modifier = QtModNone

    # Scroll Down
    h = projTree.height()
    projTree.dragMoveEvent(QDragMoveEvent(QPoint(1, h-1), action, mime, mouse, modifier))
    assert projTree._scrollDirection == 1
    projTree._doAutoScroll()
    assert projTree._scrollDirection == 0
    projTree.dragMoveEvent(QDragMoveEvent(QPoint(1, h-2), action, mime, mouse, modifier))
    assert projTree._scrollDirection == 1
    projTree._doAutoScroll()
    assert projTree._scrollDirection == 0
    projTree.dragMoveEvent(QDragMoveEvent(QPoint(1, h-3), action, mime, mouse, modifier))
    assert projTree._scrollDirection == 1
    projTree._doAutoScroll()
    assert projTree._scrollDirection == 0
    projTree.dragMoveEvent(QDragMoveEvent(QPoint(1, h-4), action, mime, mouse, modifier))
    assert projTree._scrollDirection == 1
    projTree._doAutoScroll()
    assert projTree._scrollDirection == 0

    # Scroll Up
    projTree.dragMoveEvent(QDragMoveEvent(QPoint(1, 1), action, mime, mouse, modifier))
    assert projTree._scrollDirection == -1
    projTree._doAutoScroll()
    assert projTree._scrollDirection == 0
    projTree.dragMoveEvent(QDragMoveEvent(QPoint(1, 2), action, mime, mouse, modifier))
    assert projTree._scrollDirection == -1
    projTree._doAutoScroll()
    assert projTree._scrollDirection == 0
    projTree.dragMoveEvent(QDragMoveEvent(QPoint(1, 3), action, mime, mouse, modifier))
    assert projTree._scrollDirection == -1
    projTree._doAutoScroll()
    assert projTree._scrollDirection == 0
    projTree.dragMoveEvent(QDragMoveEvent(QPoint(1, 4), action, mime, mouse, modifier))
    assert projTree._scrollDirection == -1
    projTree._doAutoScroll()
    assert projTree._scrollDirection == 0

    # qtbot.stop()


@pytest.mark.gui
def testGuiProjTree_DragAndDrop(qtbot, monkeypatch, caplog, nwGUI: GuiMain, projPath, mockRnd):
    """Test the auto scroll feature."""
    buildTestProject(nwGUI, projPath)
    projTree: GuiProjectTree = nwGUI.projView.projTree

    monkeypatch.setattr(QTreeWidget, "dropEvent", lambda *a, **k: None)

    projTree.setSelectedHandle(C.hSceneDoc, True)
    projTree._getTreeItem(C.hChapterDir).setExpanded(True)  # type: ignore

    nPos = projTree.visualItemRect(projTree._getTreeItem(C.hNovelRoot)).bottomLeft()
    action = Qt.DropAction.MoveAction
    mime = QMimeData()
    mouse = QtMouseLeft
    modifier = QtModNone

    projTree.saveTreeOrder()
    treeOrder = SHARED.project.tree._order

    # Move an item, but no selection
    event = QDropEvent(nPos, action, mime, mouse, modifier)
    projTree.dropEvent(event)
    projTree.saveTreeOrder()
    assert SHARED.project.tree._order == treeOrder

    # Invalid location
    caplog.clear()
    event = QDropEvent(QPoint(1000, 1000), action, mime, mouse, modifier)
    projTree.dropEvent(event)
    assert event.isAccepted() is False
    assert "Invalid drop location" in caplog.text
    projTree.saveTreeOrder()
    assert SHARED.project.tree._order == treeOrder

    # Root item selected
    caplog.clear()
    event = QDropEvent(nPos, action, mime, mouse, modifier)
    projTree.clearSelection()
    projTree._getTreeItem(C.hTitlePage).setSelected(True)  # type: ignore
    projTree._getTreeItem(C.hNovelRoot).setSelected(True)  # type: ignore
    projTree.dropEvent(event)
    assert event.isAccepted() is False
    projTree.saveTreeOrder()
    assert SHARED.project.tree._order == treeOrder

    # Make sure illegal drag events are cancelled
    with monkeypatch.context() as mp:
        mp.setattr(QTreeWidget, "dragEnterEvent", lambda *a: None)
        mime = QMimeData()
        mime.setText("foobar")
        event = QDragEnterEvent(nPos, action, mime, mouse, modifier)
        projTree.clearSelection()
        projTree._getTreeItem(C.hNovelRoot).setSelected(True)  # type: ignore
        projTree._getTreeItem(C.hTitlePage).setSelected(True)  # type: ignore
        projTree._getTreeItem(C.hChapterDoc).setSelected(True)  # type: ignore
        assert projTree.selectedItems() == [  # Novel Root selection is cancelled automatically
            projTree._getTreeItem(C.hTitlePage), projTree._getTreeItem(C.hChapterDoc)
        ]
        projTree.dragEnterEvent(event)
        assert mime.text() == ""
        assert projTree._popAlert is not None

    # Pop the alert
    with monkeypatch.context() as mp:
        mp.setattr(QTreeWidget, "startDrag", lambda *a: None)
        projTree.startDrag(None)  # type: ignore
        assert projTree._popAlert is None

    # Valid drag events are processed
    with monkeypatch.context() as mp:
        mp.setattr(QTreeWidget, "dragEnterEvent", lambda *a: None)
        mime = QMimeData()
        mime.setText("foobar")
        event = QDragEnterEvent(nPos, action, mime, mouse, modifier)
        projTree.clearSelection()
        projTree._getTreeItem(C.hChapterDoc).setSelected(True)  # type: ignore
        projTree._getTreeItem(C.hSceneDoc).setSelected(True)  # type: ignore
        assert projTree.selectedItems() == [  # Novel Root selection is cancelled automatically
            projTree._getTreeItem(C.hChapterDoc), projTree._getTreeItem(C.hSceneDoc)
        ]
        projTree.dragEnterEvent(event)
        assert mime.text() == "foobar"
        assert projTree._popAlert is None

    # qtbot.stop()


@pytest.mark.gui
def testGuiProjTree_Other(qtbot, monkeypatch, nwGUI: GuiMain, projPath, mockRnd):
    """Test various parts of the project tree class not covered by
    other tests.
    """
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

    # Mouse Button Clicks
    # ===================

    eType = QEvent.Type.MouseButtonPress
    pos = projTree.visualItemRect(projTree._getTreeItem(C.hChapterDoc)).center()
    button = QtMouseMiddle
    modifier = QtModNone

    # Trigger the viewer
    event = QMouseEvent(eType, pos, button, button, modifier)
    projTree.mousePressEvent(event)
    assert nwGUI.docViewer.docHandle == C.hChapterDoc

    # Trigger the left click clear
    pos = QPoint(5000, 5000)
    button = QtMouseLeft
    event = QMouseEvent(eType, pos, button, button, modifier)
    projTree.setSelectedHandle(C.hChapterDoc)
    projTree.mousePressEvent(event)
    assert projTree.selectedItems() == []

    # Rename Item
    # ===========

    with monkeypatch.context() as mp:
        mp.setattr(GuiEditLabel, "getLabel", lambda *a, **k: ("FooBar", True))
        projTree.clearSelection()
        assert SHARED.project.tree[C.hChapterDoc].itemName == "New Chapter"  # type: ignore
        projView.renameTreeItem(C.hChapterDoc)
        assert SHARED.project.tree[C.hChapterDoc].itemName == "FooBar"  # type: ignore

        projTree.setSelectedHandle(C.hSceneDoc)
        assert SHARED.project.tree[C.hSceneDoc].itemName == "New Scene"  # type: ignore
        projView.renameTreeItem()
        assert SHARED.project.tree[C.hSceneDoc].itemName == "FooBar"  # type: ignore

    # Check Crash Resistance
    # ======================
    projTree._postItemMove("dfghj")  # This should exit cleanly

    # qtbot.stop()


@pytest.mark.gui
def testGuiProjTree_ContextMenu(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test the building of the project tree context menu. All this does
    is test that the menu builds. It doesn't open the actual menu.
    """
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    # Create a project
    buildTestProject(nwGUI, projPath)
    nwGUI.openProject(projPath)
    nwGUI._switchFocus(nwFocus.TREE)

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
    assert SHARED.project.tree[hSubNote].itemParent == hNovelNote  # type: ignore

    def itemPos(tHandle):
        return projTree.visualItemRect(projTree._getTreeItem(tHandle)).center()

    # Pop the menu
    with monkeypatch.context() as mp:
        mp.setattr(QMenu, "exec", lambda *a: None)
        projTree.clearSelection()

        # No item under menu
        assert projTree._openContextMenu(projTree.viewport().rect().bottomRight()) is False

        # Open Trash Menu
        assert projTree._openContextMenu(itemPos(hTrashRoot)) is True

        # Open Single Select Menu
        assert projTree._openContextMenu(itemPos(C.hNovelRoot)) is True

        # Open Multi-Select Menu
        projTree._getTreeItem(hNovelNote).setSelected(True)
        projTree._getTreeItem(hSubNote).setSelected(True)
        assert projTree._openContextMenu(itemPos(hCharNote)) is True

        # Check the keyboard shortcut handler as well
        projTree.setSelectedHandle(C.hNovelRoot)
        assert projTree.openContextOnSelected() is True
        projTree.clearSelection()
        assert projTree.openContextOnSelected() is False

    # Menu Builders
    # =============

    # Context Menu on Root Item
    nwItem = SHARED.project.tree[C.hNovelRoot]
    assert isinstance(nwItem, NWItem)
    ctxMenu = _TreeContextMenu(projTree, nwItem)
    ctxMenu.buildSingleSelectMenu(True)
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Create New ...", "Rename", "Set Status to ...", "Expand All",
        "Collapse All", "Duplicate", "Delete Permanently",
    ]

    # Context Menu on Folder Item
    nwItem = SHARED.project.tree[C.hChapterDir]
    assert isinstance(nwItem, NWItem)
    ctxMenu = _TreeContextMenu(projTree, nwItem)
    ctxMenu.buildSingleSelectMenu(True)
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Create New ...", "Rename", "Set Status to ...", "Transform ...", "Expand All",
        "Collapse All", "Duplicate", "Move to Trash",
    ]

    def getTransformSubMenu(menu: QMenu) -> list[str]:
        for action in menu.actions():
            if action.text() == "Transform ...":
                return [x.text() for x in action.menu().actions() if x.text()]
        return []

    # Context Menu on Document File Item
    nwItem = SHARED.project.tree[C.hChapterDoc]
    assert isinstance(nwItem, NWItem)
    ctxMenu = _TreeContextMenu(projTree, nwItem)
    ctxMenu.buildSingleSelectMenu(True)
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Open Document", "View Document", "Create New ...", "Rename", "Rename to Heading",
        "Toggle Active", "Set Status to ...", "Transform ...", "Expand All", "Collapse All",
        "Duplicate", "Move to Trash",
    ]
    assert getTransformSubMenu(ctxMenu) == [
        "Convert to Project Note", "Merge Child Items into Self",
        "Merge Child Items into New", "Split Document by Headings"
    ]

    # Context Menu on Note File Item in Character Folder
    nwItem = SHARED.project.tree[hCharNote]
    assert isinstance(nwItem, NWItem)
    ctxMenu = _TreeContextMenu(projTree, nwItem)
    ctxMenu.buildSingleSelectMenu(False)
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Open Document", "View Document", "Create New ...", "Rename", "Rename to Heading",
        "Toggle Active", "Set Importance to ...", "Transform ...", "Duplicate", "Move to Trash",
    ]
    assert getTransformSubMenu(ctxMenu) == [
        "Split Document by Headings",
    ]

    # Context Menu on Note File Item in Novel Tree
    nwItem = SHARED.project.tree[hNovelNote]
    assert isinstance(nwItem, NWItem)
    ctxMenu = _TreeContextMenu(projTree, nwItem)
    ctxMenu.buildSingleSelectMenu(False)
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Open Document", "View Document", "Create New ...", "Rename", "Rename to Heading",
        "Toggle Active", "Set Status to ...", "Transform ...", "Duplicate", "Move to Trash",
    ]
    assert getTransformSubMenu(ctxMenu) == [
        "Convert to Novel Document", "Split Document by Headings",
    ]

    # Context Menu on Multiple Items, Clicked on Document
    nwItem = SHARED.project.tree[hNovelNote]
    assert isinstance(nwItem, NWItem)
    ctxMenu = _TreeContextMenu(projTree, nwItem)
    ctxMenu.buildMultiSelectMenu([hCharNote, hNovelNote, hSubNote])
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Set Active to ...", "Set Status to ...", "Move to Trash",
    ]

    # Context Menu on Multiple Items, Clicked on Note
    nwItem = SHARED.project.tree[hCharNote]
    assert isinstance(nwItem, NWItem)
    ctxMenu = _TreeContextMenu(projTree, nwItem)
    ctxMenu.buildMultiSelectMenu([hCharNote, hNovelNote, hSubNote])
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Set Active to ...", "Set Importance to ...", "Move to Trash",
    ]

    # Direct Edit Functions, Single
    # =============================

    nwItem = SHARED.project.tree[hNovelNote]
    assert isinstance(nwItem, NWItem)

    # # Toggle active flag
    ctxMenu = _TreeContextMenu(projTree, nwItem)
    ctxMenu.buildSingleSelectMenu(False)
    assert nwItem.isActive is True
    ctxMenu._toggleItemActive()
    assert nwItem.isActive is False

    # Change item status
    assert nwItem.itemStatus == "s000000"
    ctxMenu._changeItemStatus("s000001")
    assert nwItem.itemStatus == "s000001"

    # Change item importance
    assert nwItem.itemImport == "i000004"
    ctxMenu._changeItemImport("i000005")
    assert nwItem.itemImport == "i000005"

    # Change item layout
    assert nwItem.itemLayout == nwItemLayout.NOTE
    ctxMenu._changeItemLayout(nwItemLayout.DOCUMENT)
    assert nwItem.itemLayout == nwItemLayout.DOCUMENT
    ctxMenu._changeItemLayout(nwItemLayout.NOTE)
    assert nwItem.itemLayout == nwItemLayout.NOTE

    # Convert Folders to Documents
    # ============================

    projView.setSelectedHandle(hNovelNote)
    assert projTree.newTreeItem(nwItemType.FOLDER) is True
    projView.setSelectedHandle(hNewFolderOne)
    assert projTree.newTreeItem(nwItemType.FILE) is True

    projView.setSelectedHandle(hNovelNote)
    assert projTree.newTreeItem(nwItemType.FOLDER) is True
    projView.setSelectedHandle(hNewFolderTwo)
    assert projTree.newTreeItem(nwItemType.FILE, isNote=True) is True

    nwItem = SHARED.project.tree[hNewFolderOne]
    assert isinstance(nwItem, NWItem)
    ctxMenu = _TreeContextMenu(projTree, nwItem)
    ctxMenu.buildSingleSelectMenu(False)

    # Click no on the dialog
    with monkeypatch.context() as mp:
        mp.setattr(QMessageBox, "result", lambda *a: QMessageBox.StandardButton.No)
        ctxMenu._covertFolderToFile(nwItemLayout.DOCUMENT)
        assert SHARED.project.tree[hNewFolderOne].isFolderType()  # type: ignore

    # Convert the first folder to a document
    ctxMenu._covertFolderToFile(nwItemLayout.DOCUMENT)
    assert SHARED.project.tree[hNewFolderOne].isFileType()  # type: ignore
    assert SHARED.project.tree[hNewFolderOne].isDocumentLayout()  # type: ignore

    nwItem = SHARED.project.tree[hNewFolderTwo]
    assert isinstance(nwItem, NWItem)
    ctxMenu = _TreeContextMenu(projTree, nwItem)
    ctxMenu.buildSingleSelectMenu(False)

    # Convert the second folder to a note
    ctxMenu._covertFolderToFile(nwItemLayout.NOTE)
    assert SHARED.project.tree[hNewFolderTwo].isFileType()  # type: ignore
    assert SHARED.project.tree[hNewFolderTwo].isNoteLayout()  # type: ignore

    # Direct Edit Functions, Multi
    # ============================

    nwItem = SHARED.project.tree[hCharNote]
    assert isinstance(nwItem, NWItem)
    ctxMenu = _TreeContextMenu(projTree, nwItem)
    ctxMenu.buildMultiSelectMenu([hCharNote, hNovelNote, hSubNote])

    projTree.clearSelection()
    projTree._getTreeItem(hCharNote).setSelected(True)
    projTree._getTreeItem(hNovelNote).setSelected(True)
    projTree._getTreeItem(hSubNote).setSelected(True)

    # Item Active
    assert SHARED.project.tree[hCharNote].isActive is True  # type: ignore
    assert SHARED.project.tree[hNovelNote].isActive is False  # type: ignore
    assert SHARED.project.tree[hSubNote].isActive is True  # type: ignore
    ctxMenu._iterItemActive(False)
    assert SHARED.project.tree[hCharNote].isActive is False  # type: ignore
    assert SHARED.project.tree[hNovelNote].isActive is False  # type: ignore
    assert SHARED.project.tree[hSubNote].isActive is False  # type: ignore
    ctxMenu._iterItemActive(True)
    assert SHARED.project.tree[hCharNote].isActive is True  # type: ignore
    assert SHARED.project.tree[hNovelNote].isActive is True  # type: ignore
    assert SHARED.project.tree[hSubNote].isActive is True  # type: ignore

    # Item Status
    assert SHARED.project.tree[hCharNote].itemStatus  == "s000000"  # type: ignore
    assert SHARED.project.tree[hNovelNote].itemStatus == "s000001"  # type: ignore
    assert SHARED.project.tree[hSubNote].itemStatus   == "s000000"  # type: ignore
    ctxMenu._iterSetItemStatus("s000003")
    assert SHARED.project.tree[hCharNote].itemStatus  == "s000000"  # type: ignore
    assert SHARED.project.tree[hNovelNote].itemStatus == "s000003"  # type: ignore
    assert SHARED.project.tree[hSubNote].itemStatus   == "s000003"  # type: ignore

    # Item Importance
    assert SHARED.project.tree[hCharNote].itemImport  == "i000004"  # type: ignore
    assert SHARED.project.tree[hNovelNote].itemImport == "i000005"  # type: ignore
    assert SHARED.project.tree[hSubNote].itemImport   == "i000004"  # type: ignore
    ctxMenu._iterSetItemImport("i000007")
    assert SHARED.project.tree[hCharNote].itemImport  == "i000007"  # type: ignore
    assert SHARED.project.tree[hNovelNote].itemImport == "i000005"  # type: ignore
    assert SHARED.project.tree[hSubNote].itemImport   == "i000004"  # type: ignore

    # Move to Trash
    assert SHARED.project.tree[hCharNote].itemRoot  == C.hCharRoot   # type: ignore
    assert SHARED.project.tree[hNovelNote].itemRoot == C.hNovelRoot  # type: ignore
    assert SHARED.project.tree[hSubNote].itemRoot   == C.hNovelRoot  # type: ignore
    ctxMenu._iterMoveToTrash()
    assert SHARED.project.tree[hCharNote].itemRoot  == hTrashRoot  # type: ignore
    assert SHARED.project.tree[hNovelNote].itemRoot == hTrashRoot  # type: ignore
    assert SHARED.project.tree[hSubNote].itemRoot   == hTrashRoot  # type: ignore

    # Permanently Delete Menu
    nwItem = SHARED.project.tree[hCharNote]
    assert isinstance(nwItem, NWItem)
    ctxMenu = _TreeContextMenu(projTree, nwItem)
    ctxMenu.buildMultiSelectMenu([hCharNote, hNovelNote, hSubNote])
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Set Active to ...", "Set Importance to ...", "Delete Permanently",
    ]

    # Permanently Delete
    ctxMenu._iterPermDelete()
    assert SHARED.project.tree[hCharNote] is None
    assert SHARED.project.tree[hNovelNote] is None
    assert SHARED.project.tree[hSubNote] is None

    # qtbot.stop()


@pytest.mark.gui
def testGuiProjTree_Templates(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test the templates feature of the project tree."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    # Create a project
    buildTestProject(nwGUI, projPath)
    nwGUI.openProject(projPath)
    nwGUI._switchFocus(nwFocus.TREE)
    nwGUI.show()

    project = SHARED.project

    projView = nwGUI.projView
    projTree = projView.projTree
    projBar  = projView.projBar

    # Handles for new objects
    hTemplatesRoot = "0000000000010"
    hSceneTemplate = "0000000000011"
    hNoteTemplate  = "0000000000012"
    hNewScene      = "0000000000013"
    hNewCharacter  = "0000000000014"

    # Add template folder
    projTree.newTreeItem(nwItemType.ROOT, nwItemClass.TEMPLATE)
    nwTemplateRoot = project.tree[hTemplatesRoot]
    assert nwTemplateRoot is not None
    assert nwTemplateRoot.itemName == "Templates"

    # Add a scene template
    projTree.setSelectedHandle(hTemplatesRoot)
    projTree.newTreeItem(nwItemType.FILE, hLevel=3, isNote=False)
    nwSceneTemplate = project.tree[hSceneTemplate]
    assert nwSceneTemplate is not None
    assert nwSceneTemplate.itemName == "New Scene"
    assert projBar.mTemplates.actions()[0].text() == "New Scene"

    # Rename the scene template
    with qtbot.waitSignal(projTree.itemRefreshed, timeout=1000) as signal:
        projTree.renameTreeItem(hSceneTemplate, name="Scene")
        assert signal.args[0] == hSceneTemplate
        assert signal.args[1].itemName == "Scene"
        assert projBar.mTemplates.actions()[0].text() == "Scene"

    # Add a note template
    projTree.setSelectedHandle(hTemplatesRoot)
    projTree.newTreeItem(nwItemType.FILE, hLevel=1, isNote=True)
    nwNoteTemplate = project.tree[hNoteTemplate]
    assert nwNoteTemplate is not None
    assert nwNoteTemplate.itemName == "New Note"
    assert projBar.mTemplates.actions()[1].text() == "New Note"

    # Rename the note template
    with qtbot.waitSignal(projTree.itemRefreshed, timeout=1000) as signal:
        projTree.renameTreeItem(hNoteTemplate, name="Note")
        assert signal.args[0] == hNoteTemplate
        assert signal.args[1].itemName == "Note"
        assert projBar.mTemplates.actions()[1].text() == "Note"

    # Add new content to template files
    (projPath / "content" / f"{hSceneTemplate}.nwd").write_text("### Scene\n\n@pov: Jane\n\n")
    (projPath / "content" / f"{hNoteTemplate}.nwd").write_text("# Jane\n\n@tag: Jane\n\n")

    # Add a new scene using the template
    projTree.setSelectedHandle(C.hSceneDoc, doScroll=True)
    projBar.mTemplates.actions()[0].trigger()
    nwNewScene = project.tree[hNewScene]
    assert nwNewScene is not None
    assert nwNewScene.itemName == "Scene"
    assert project.storage.getDocument(hNewScene).readDocument() == "### Scene\n\n@pov: Jane\n\n"

    # Add a new note using the template
    projTree.setSelectedHandle(C.hCharRoot, doScroll=True)
    projBar.mTemplates.actions()[1].trigger()
    nwNewCharacter = project.tree[hNewCharacter]
    assert nwNewCharacter is not None
    assert nwNewCharacter.itemName == "Note"
    assert project.storage.getDocument(hNewCharacter).readDocument() == "# Jane\n\n@tag: Jane\n\n"

    # Remove the templates
    with qtbot.waitSignal(projTree.itemRefreshed, timeout=1000) as signal:
        assert projBar.mTemplates.menuAction().isVisible() is True
        assert len(projBar.mTemplates.actions()) == 2
        projTree.moveItemToTrash(hNoteTemplate)
        assert len(projBar.mTemplates.actions()) == 1
        projTree.moveItemToTrash(hSceneTemplate)
        assert len(projBar.mTemplates.actions()) == 0
        assert projBar.mTemplates.menuAction().isVisible() is False

    # qtbot.stop()
