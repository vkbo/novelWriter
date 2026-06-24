"""
novelWriter – Main GUI Project Tree Class Tester
================================================

This file is a part of novelWriter
Copyright (C) 2020 Veronica Berglyd Olsen and novelWriter contributors

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
"""  # noqa
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from PyQt6.QtCore import QEvent, QItemSelectionModel, QModelIndex, QPointF
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QMenu

from novelwriter import CONFIG, SHARED
from novelwriter.dialogs.docmerge import GuiDocMerge
from novelwriter.dialogs.docsplit import GuiDocSplit
from novelwriter.dialogs.editlabel import GuiEditLabel
from novelwriter.enum import nwDocMode, nwItemClass, nwItemLayout, nwItemType
from novelwriter.gui.projtree import _TreeContextMenu
from novelwriter.shared import _GuiAlert
from novelwriter.types import (
    QtAccepted, QtModNone, QtMouseLeft, QtMouseMiddle, QtRejected,
    QtScrollAlwaysOff, QtScrollAsNeeded
)

from tests.mocked import causeOSError
from tests.tools import C, buildTestProject


@pytest.mark.gui
def testGuiProjTree_NewTreeItem(qtbot, caplog, monkeypatch, nwGUI, projPath, mockRnd):
    """Test adding items to the project tree."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    projView = nwGUI.projView
    projTree = projView.projTree
    project = SHARED.project
    tree = project.tree

    # Try to add item with no project
    projTree.newTreeItem(nwItemType.FILE)
    assert len(tree) == 0

    # Create a project
    buildTestProject(nwGUI, projPath)
    trash = tree.trash
    assert trash is not None
    assert len(tree) == 9
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Root Items
    # ==========

    # No class set
    projTree.newTreeItem(nwItemType.ROOT)
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Create Objects root item after Locations
    hObjectRoot = "0000000000011"
    projView.setSelectedHandle(C.hWorldRoot)
    projTree.newTreeItem(nwItemType.ROOT, nwItemClass.OBJECT)
    assert hObjectRoot in tree
    item = tree[hObjectRoot]
    assert item is not None
    assert item.itemName == "Objects"
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Objects", "Trash",
    ]

    # File/Folder Items
    # =================

    # No location selected for new item
    projTree._clearSelection()

    caplog.clear()
    projTree.newTreeItem(nwItemType.FILE)
    assert "Did not find anywhere" in caplog.text

    caplog.clear()
    projTree.newTreeItem(nwItemType.FOLDER)
    assert "Did not find anywhere" in caplog.text

    # Try to add them to Trash
    projView.setSelectedHandle(trash.item.itemHandle)

    caplog.clear()
    projTree.newTreeItem(nwItemType.FILE)
    assert "Cannot add new files or folders" in caplog.text

    caplog.clear()
    projTree.newTreeItem(nwItemType.FOLDER)
    assert "Cannot add new files or folders" in caplog.text

    # Create new folder as child of Novel folder
    hNewFolder = "0000000000012"
    projView.setSelectedHandle(C.hNovelRoot, doScroll=True)
    projTree.newTreeItem(nwItemType.FOLDER)
    assert hNewFolder in tree
    item = tree[hNewFolder]
    assert item is not None
    assert item.itemName == "New Folder"
    assert item.itemParent == C.hNovelRoot
    assert item.itemRoot == C.hNovelRoot
    assert item.itemClass == nwItemClass.NOVEL
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "New Folder", "Plot", "Characters", "Locations", "Objects", "Trash",
    ]

    # Add a new file in the new folder
    hNewFile = "0000000000013"
    projView.setSelectedHandle(hNewFolder, doScroll=True)
    projTree.newTreeItem(nwItemType.FILE, hLevel=0)
    assert hNewFile in tree
    item = tree[hNewFile]
    assert item is not None
    assert item.itemName == "New Document"
    assert item.itemParent == hNewFolder
    assert item.itemRoot == C.hNovelRoot
    assert item.itemClass == nwItemClass.NOVEL
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "New Folder", "New Document", "Plot", "Characters", "Locations",
        "Objects", "Trash",
    ]

    # Add a new partition next to the other new file
    hNewPart = "0000000000014"
    projView.setSelectedHandle(hNewFile, doScroll=True)
    projTree.newTreeItem(nwItemType.FILE, hLevel=1)
    assert hNewPart in tree
    item = tree[hNewPart]
    assert item is not None
    assert item.itemName == "New Part"
    assert item.itemParent == hNewFolder
    assert item.itemRoot == C.hNovelRoot
    assert item.itemClass == nwItemClass.NOVEL
    assert nwGUI.openDocument(hNewPart)
    assert nwGUI.docEditor.getText() == "# New Part\n\n"
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "New Folder", "New Document", "New Part", "Plot", "Characters",
        "Locations", "Objects", "Trash",
    ]

    # Add a new chapter next to the other new file
    hNewChapter = "0000000000015"
    projView.setSelectedHandle(hNewPart, doScroll=True)
    projTree.newTreeItem(nwItemType.FILE, hLevel=2)
    assert hNewChapter in tree
    item = tree[hNewChapter]
    assert item is not None
    assert item.itemName == "New Chapter"
    assert item.itemParent == hNewFolder
    assert item.itemRoot == C.hNovelRoot
    assert item.itemClass == nwItemClass.NOVEL
    assert nwGUI.openDocument(hNewChapter)
    assert nwGUI.docEditor.getText() == "## New Chapter\n\n"
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "New Folder", "New Document", "New Part", "New Chapter", "Plot",
        "Characters", "Locations", "Objects", "Trash",
    ]

    # Add a new scene next to the other new file
    hNewScene = "0000000000016"
    projView.setSelectedHandle(hNewChapter, doScroll=True)
    projTree.newTreeItem(nwItemType.FILE, hLevel=3)
    assert hNewScene in tree
    item = tree[hNewScene]
    assert item is not None
    assert item.itemName == "New Scene"
    assert item.itemParent == hNewFolder
    assert item.itemRoot == C.hNovelRoot
    assert item.itemClass == nwItemClass.NOVEL
    assert nwGUI.openDocument(hNewScene)
    assert nwGUI.docEditor.getText() == "### New Scene\n\n"
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "New Folder", "New Document", "New Part", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Objects", "Trash",
    ]

    # Add a new scene with the content copied from the previous
    nwGUI.openDocument(hNewScene)
    nwGUI.docEditor.setPlainText("### New Scene\n\nWith Stuff\n\n")
    nwGUI.saveDocument()

    hNewSceneCopy = "0000000000017"
    projView.setSelectedHandle(hNewScene, doScroll=True)
    projTree.newTreeItem(nwItemType.FILE, copyDoc=hNewScene)
    assert hNewSceneCopy in tree
    item = tree[hNewSceneCopy]
    assert item is not None
    assert item.itemName == "New Scene"
    assert item.itemParent == hNewFolder
    assert item.itemRoot == C.hNovelRoot
    assert item.itemClass == nwItemClass.NOVEL
    assert nwGUI.openDocument(hNewSceneCopy)
    assert nwGUI.docEditor.getText() == "### New Scene\n\nWith Stuff\n\n"
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "New Folder", "New Document", "New Part", "New Chapter", "New Scene",
        "New Scene", "Plot", "Characters", "Locations", "Objects", "Trash",
    ]

    # Add a new file to the characters folder
    hNewCharacter = "0000000000018"
    projView.setSelectedHandle(C.hCharRoot, doScroll=True)
    projTree.newTreeItem(nwItemType.FILE, hLevel=1, isNote=True)
    assert hNewCharacter in tree
    item = tree[hNewCharacter]
    assert item is not None
    assert item.itemName == "New Note"
    assert item.itemParent == C.hCharRoot
    assert item.itemRoot == C.hCharRoot
    assert item.itemClass == nwItemClass.CHARACTER
    assert nwGUI.openDocument(hNewCharacter)
    assert nwGUI.docEditor.getText() == "# New Note\n\n"
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "New Folder", "New Document", "New Part", "New Chapter", "New Scene",
        "New Scene", "Plot", "Characters", "New Note", "Locations",
        "Objects", "Trash",
    ]

    # Cancel during creation
    with monkeypatch.context() as mp:
        mp.setattr(GuiEditLabel, "getLabel", lambda *a, **k: ("", False))
        projView.setSelectedHandle(hNewFile, doScroll=True)
        projTree.newTreeItem(nwItemType.FILE)
        assert [n.item.itemName for n in tree.model.root.allChildren()] == [
            "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
            "New Folder", "New Document", "New Part", "New Chapter", "New Scene",
            "New Scene", "Plot", "Characters", "New Note", "Locations",
            "Objects", "Trash",
        ]

    # From Template
    # =============

    # Create template folder
    hTemplateRoot = "0000000000019"
    projView.setSelectedHandle(hObjectRoot)
    projTree.newTreeItem(nwItemType.ROOT, nwItemClass.TEMPLATE)
    assert hTemplateRoot in tree
    item = tree[hTemplateRoot]
    assert item is not None
    assert item.itemName == "Templates"
    assert item.itemParent is None
    assert item.itemRoot == hTemplateRoot
    assert item.itemClass == nwItemClass.TEMPLATE
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "New Folder", "New Document", "New Part", "New Chapter", "New Scene",
        "New Scene", "Plot", "Characters", "New Note", "Locations",
        "Objects", "Templates", "Trash",
    ]

    # Create scene template
    hSceneTemplate = "000000000001a"
    projView.setSelectedHandle(hTemplateRoot, doScroll=True)
    projTree.newTreeItem(nwItemType.FILE, hLevel=3)
    assert hSceneTemplate in tree
    item = tree[hSceneTemplate]
    assert item is not None
    assert item.itemName == "New Scene"
    assert item.itemParent == hTemplateRoot
    assert item.itemRoot == hTemplateRoot
    assert item.itemClass == nwItemClass.TEMPLATE

    item.setName("New Scene Template")
    nwGUI.openDocument(hSceneTemplate)
    nwGUI.docEditor.setPlainText("### New Scene Template\n\nWith Stuff\n\n")
    nwGUI.saveDocument()
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "New Folder", "New Document", "New Part", "New Chapter", "New Scene",
        "New Scene", "Plot", "Characters", "New Note", "Locations",
        "Objects", "Templates", "New Scene Template", "Trash",
    ]

    # Create from template
    hNewFromTemplate = "000000000001b"
    projView.setSelectedHandle(hNewSceneCopy, doScroll=True)
    projView.createFileFromTemplate(hSceneTemplate)
    assert hNewFromTemplate in tree
    item = tree[hNewFromTemplate]
    assert item is not None
    assert item.itemName == "New Scene Template"
    assert item.itemParent == hNewFolder
    assert item.itemRoot == C.hNovelRoot
    assert item.itemClass == nwItemClass.NOVEL
    assert nwGUI.openDocument(hNewFromTemplate)
    assert nwGUI.docEditor.getText() == "### New Scene Template\n\nWith Stuff\n\n"
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "New Folder", "New Document", "New Part", "New Chapter", "New Scene",
        "New Scene", "New Scene Template", "Plot", "Characters", "New Note",
        "Locations", "Objects", "Templates", "New Scene Template", "Trash",
    ]

    # Rename Item
    # ===========

    # Rename plot folder
    with monkeypatch.context() as mp:
        mp.setattr(GuiEditLabel, "getLabel", lambda *a, **k: ("Stuff", True))
        projView.setSelectedHandle(C.hPlotRoot, doScroll=True)
        projView.renameTreeItem()
        item = tree[C.hPlotRoot]
        assert item is not None
        assert item.itemName == "Stuff"

    # Clean up
    # qtbot.stop()
    nwGUI.closeProject()


@pytest.mark.gui
def testGuiProjTree_SimpleOperations(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test simple operations in the project tree like internal move,
    change selection and expand/collapse nodes.
    """
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    projView = nwGUI.projView
    projTree = projView.projTree
    project = SHARED.project
    tree = project.tree
    model = tree.model

    # The default model is empty
    assert projView.getSelectedHandle() is None
    assert projTree._getModel() is None
    assert projTree._selectedRows() == []
    assert projTree._getNode(QModelIndex()) is None

    # Create a project
    buildTestProject(nwGUI, projPath)
    trash = tree.trash
    assert trash is not None
    assert len(tree) == 9
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Add some scenes
    hFolder = "0000000000011"
    hScenes = ["0000000000012", "0000000000013", "0000000000014", "0000000000015"]
    projView.setSelectedHandle(C.hNovelRoot, doScroll=True)
    projTree.newTreeItem(nwItemType.FOLDER)
    assert hFolder in tree
    item = tree[hFolder]
    assert item is not None
    item.setName("Chapter Folder")

    projView.setSelectedHandle(hFolder, doScroll=True)
    for n, hScene in enumerate(hScenes):
        projTree.newTreeItem(nwItemType.FILE, hLevel=3)
        assert hScene in tree
        item = tree[hScene]
        assert item is not None
        item.setName(f"Scene {n+1}")

    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Chapter Folder", "Scene 1", "Scene 2", "Scene 3", "Scene 4",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Expansion
    # =========

    # Default State
    assert [n.item.itemHandle for n in [model.node(i) for i in model.allExpanded()] if n] == [
        C.hNovelRoot, hFolder
    ]

    # Expand Novel
    projTree.expandFromIndex(model.indexFromHandle(C.hNovelRoot))
    assert [n.item.itemHandle for n in [model.node(i) for i in model.allExpanded()] if n] == [
        C.hNovelRoot, C.hChapterDir, hFolder
    ]

    # Collapse Novel
    projTree.collapseFromIndex(model.indexFromHandle(C.hNovelRoot))
    assert [n.item.itemHandle for n in [model.node(i) for i in model.allExpanded()] if n] == [
        C.hNovelRoot
    ]

    # Move Up
    # =======

    # Already first
    projView.setSelectedHandle(hScenes[0], doScroll=True)
    projTree.moveItemUp()
    assert [n.item.itemName for n in tree.model.root.allChildren()][5:10] == [
        "Chapter Folder", "Scene 1", "Scene 2", "Scene 3", "Scene 4",
    ]

    # Proper move
    projView.setSelectedHandle(hScenes[1], doScroll=True)
    projTree.moveItemUp()
    assert [n.item.itemName for n in tree.model.root.allChildren()][5:10] == [
        "Chapter Folder", "Scene 2", "Scene 1", "Scene 3", "Scene 4",
    ]

    # Move Down
    # =========

    # Already last
    projView.setSelectedHandle(hScenes[3], doScroll=True)
    projTree.moveItemDown()
    assert [n.item.itemName for n in tree.model.root.allChildren()][5:10] == [
        "Chapter Folder", "Scene 2", "Scene 1", "Scene 3", "Scene 4",
    ]

    # Proper move
    projView.setSelectedHandle(hScenes[1], doScroll=True)
    projTree.moveItemDown()
    assert [n.item.itemName for n in tree.model.root.allChildren()][5:10] == [
        "Chapter Folder", "Scene 1", "Scene 2", "Scene 3", "Scene 4",
    ]

    # Select Up
    # =========

    # Sibling
    projView.setSelectedHandle(hFolder, doScroll=True)
    assert projView.getSelectedHandle() == hFolder
    projTree.goToSiblingUp()
    assert projView.getSelectedHandle() == C.hChapterDir
    projTree.goToSiblingUp()
    assert projView.getSelectedHandle() == C.hTitlePage
    projTree.goToSiblingUp()
    assert projView.getSelectedHandle() == C.hTitlePage

    # Parent
    projTree.goToParent()
    assert projView.getSelectedHandle() == C.hNovelRoot
    projTree.goToParent()
    assert projView.getSelectedHandle() == C.hNovelRoot

    # Select Down
    # =========

    # Child
    projView.setSelectedHandle(C.hNovelRoot, doScroll=True)
    assert projView.getSelectedHandle() == C.hNovelRoot
    projTree.goToFirstChild()
    assert projView.getSelectedHandle() == C.hTitlePage

    # Sibling
    projTree.goToSiblingDown()
    assert projView.getSelectedHandle() == C.hChapterDir
    projTree.goToSiblingDown()
    assert projView.getSelectedHandle() == hFolder
    projTree.goToSiblingDown()
    assert projView.getSelectedHandle() == hFolder


@pytest.mark.gui
def testGuiProjTree_MouseClicks(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test mouse clicks in the project tree."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    projView = nwGUI.projView
    projTree = projView.projTree
    project = SHARED.project
    tree = project.tree
    model = tree.model

    # The default model is empty
    assert projView.getSelectedHandle() is None
    assert projTree._getModel() is None
    assert projTree._selectedRows() == []
    assert projTree._getNode(QModelIndex()) is None

    # Create a project
    buildTestProject(nwGUI, projPath)
    trash = tree.trash
    assert trash is not None
    assert len(tree) == 9

    # Single click emits a signal
    with qtbot.waitSignal(projView.selectedItemChanged) as signal:
        projTree._onSelectionChange(model.indexFromHandle(C.hNovelRoot), QModelIndex())
    assert signal.args[0] == C.hNovelRoot

    # Double click on folder expands/collapses it
    assert [n.item.itemHandle for n in [model.node(i) for i in model.allExpanded()] if n] == []
    projTree._onDoubleClick(model.indexFromHandle(C.hNovelRoot))
    assert [n.item.itemHandle for n in [model.node(i) for i in model.allExpanded()] if n] == [
        C.hNovelRoot
    ]
    projTree._onDoubleClick(model.indexFromHandle(C.hNovelRoot))
    assert [n.item.itemHandle for n in [model.node(i) for i in model.allExpanded()] if n] == []

    # Double click on file opens it
    with qtbot.waitSignal(projView.openDocumentRequest) as signal:
        projTree._onDoubleClick(model.indexFromHandle(C.hChapterDoc))
    assert signal.args[0] == C.hChapterDoc
    assert signal.args[1] == nwDocMode.EDIT
    assert signal.args[2] == ""
    assert signal.args[3] is True

    # Mouse Button Clicks
    # ===================

    eType = QEvent.Type.MouseButtonPress
    modifier = QtModNone

    # Trigger the viewer
    pos = QPointF(projTree.visualRect(model.indexFromHandle(C.hChapterDoc)).center())
    button = QtMouseMiddle
    event = QMouseEvent(eType, pos, button, button, modifier)
    projTree.mousePressEvent(event)
    assert nwGUI.docViewer.docHandle == C.hChapterDoc

    # Trigger the left click clear
    pos = QPointF(5000.0, 5000.0)
    button = QtMouseLeft
    event = QMouseEvent(eType, pos, button, button, modifier)

    projTree.setSelectedHandle(C.hChapterDoc)
    assert projView.getSelectedHandle() == C.hChapterDoc

    projTree.mousePressEvent(event)
    assert projView.getSelectedHandle() is None


@pytest.mark.gui
def testGuiProjTree_DeleteRequest(qtbot, caplog, monkeypatch, nwGUI, projPath, mockRnd):
    """Test delete requests in the project tree."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    projView = nwGUI.projView
    projTree = projView.projTree
    project = SHARED.project
    tree = project.tree

    # Create a project
    buildTestProject(nwGUI, projPath)
    trash = tree.trash
    assert trash is not None
    assert len(tree) == 9
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Add some scenes
    hFolder = "0000000000011"
    hScenes = ["0000000000012", "0000000000013", "0000000000014", "0000000000015"]
    projView.setSelectedHandle(C.hNovelRoot, doScroll=True)
    projTree.newTreeItem(nwItemType.FOLDER)
    assert hFolder in tree
    item = tree[hFolder]
    assert item is not None
    item.setName("Chapter Folder")

    projView.setSelectedHandle(hFolder, doScroll=True)
    for n, hScene in enumerate(hScenes):
        projTree.newTreeItem(nwItemType.FILE, hLevel=3)
        assert hScene in tree
        item = tree[hScene]
        assert item is not None
        item.setName(f"Scene {n+1}")

    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Chapter Folder", "Scene 1", "Scene 2", "Scene 3", "Scene 4",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Calling it with no selection, does nothing
    projTree._clearSelection()
    projTree.processDeleteRequest()
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Chapter Folder", "Scene 1", "Scene 2", "Scene 3", "Scene 4",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Deleting a used root raises an error
    projTree.processDeleteRequest([C.hNovelRoot])
    assert SHARED.lastAlert[0] == "Root folders can only be deleted when they are empty."
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Chapter Folder", "Scene 1", "Scene 2", "Scene 3", "Scene 4",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Deleting a unused root is fine
    projTree.processDeleteRequest([C.hWorldRoot])
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Chapter Folder", "Scene 1", "Scene 2", "Scene 3", "Scene 4",
        "Plot", "Characters", "Trash",
    ]

    # User can cancel move to trash
    with monkeypatch.context() as mp:
        mp.setattr(_GuiAlert, "finalState", False)
        projTree.processDeleteRequest(hScenes, askFirst=True)
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Chapter Folder", "Scene 1", "Scene 2", "Scene 3", "Scene 4",
        "Plot", "Characters", "Trash",
    ]

    # Items not already in trash can be moved there
    projTree.processDeleteRequest(hScenes, askFirst=True)
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Chapter Folder", "Plot", "Characters", "Trash",
        "Scene 1", "Scene 2", "Scene 3", "Scene 4",
    ]

    # User can block permanent deletion
    with monkeypatch.context() as mp:
        mp.setattr(_GuiAlert, "finalState", False)
        projTree.processDeleteRequest(hScenes[0:2], askFirst=True)
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Chapter Folder", "Plot", "Characters", "Trash",
        "Scene 1", "Scene 2", "Scene 3", "Scene 4",
    ]

    # Items in trash can be permanently deleted
    projTree.processDeleteRequest(hScenes[0:2], askFirst=True)
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Chapter Folder", "Plot", "Characters", "Trash",
        "Scene 3", "Scene 4",
    ]

    # Moving a parent item to trash, includes children
    projTree.processDeleteRequest([C.hChapterDir], askFirst=True)
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "Chapter Folder", "Plot", "Characters", "Trash",
        "Scene 3", "Scene 4", "New Folder", "New Chapter", "New Scene",
    ]

    # Permanently delete in trash is recursive
    projTree.processDeleteRequest([C.hChapterDir], askFirst=True)
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "Chapter Folder", "Plot", "Characters", "Trash",
        "Scene 3", "Scene 4",
    ]

    # Trash can be completely emptied, but user can block it
    with monkeypatch.context() as mp:
        mp.setattr(_GuiAlert, "finalState", False)
        projTree.emptyTrash()
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "Chapter Folder", "Plot", "Characters", "Trash",
        "Scene 3", "Scene 4",
    ]

    # Opening documents before delete, will close them
    nwGUI.openDocument(hScenes[2])
    nwGUI.viewDocument(hScenes[3])

    assert nwGUI.docEditor.docHandle == hScenes[2]
    assert nwGUI.docViewer.docHandle == hScenes[3]

    # Trash can be completely emptied
    projTree.emptyTrash()
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "Chapter Folder", "Plot", "Characters", "Trash",
    ]

    assert nwGUI.docEditor.docHandle is None
    assert nwGUI.docViewer.docHandle is None

    # Emptying empty trash pops an alert
    projTree.emptyTrash()
    assert SHARED.lastAlert[0] == "The Trash folder is already empty."

    # Trash can be deleted if empty
    projTree.processDeleteRequest([trash.item.itemHandle])
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "Chapter Folder", "Plot", "Characters"
    ]

    # Emptying trash when it doesn't exist, recreates it
    projTree.emptyTrash()
    assert SHARED.lastAlert[0] == "The Trash folder is already empty."
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "Chapter Folder", "Plot", "Characters", "Trash",
    ]


@pytest.mark.gui
def testGuiProjTree_MergeDocuments(qtbot, monkeypatch, nwGUI, projPath, mockRnd, ipsumText):
    """Test the merge document function."""
    mergeData = {}

    monkeypatch.setattr(GuiDocMerge, "__init__", lambda *a: None)
    monkeypatch.setattr(GuiDocMerge, "exec", lambda *a: None)
    monkeypatch.setattr(GuiDocMerge, "softDelete", lambda *a: None)
    monkeypatch.setattr(GuiDocMerge, "result", lambda *a: QtAccepted)
    monkeypatch.setattr(GuiDocMerge, "data", lambda *a: mergeData)

    projView = nwGUI.projView
    projTree = projView.projTree
    project = SHARED.project
    tree = project.tree

    # Create a project
    buildTestProject(nwGUI, projPath)
    trash = tree.trash
    assert trash is not None
    assert len(tree) == 9
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Create File to Merge
    hChapter1 = project.newFile("Chapter 1", C.hNovelRoot)
    assert hChapter1 == "0000000000011"

    hSceneOne11 = project.newFile("Scene 1.1", hChapter1)
    hSceneOne12 = project.newFile("Scene 1.2", hChapter1)
    hSceneOne13 = project.newFile("Scene 1.3", hChapter1)
    assert hSceneOne11 == "0000000000012"
    assert hSceneOne12 == "0000000000013"
    assert hSceneOne13 == "0000000000014"

    mergedDoc1 = "0000000000015"

    docText1 = "\n\n".join(ipsumText[0:2]) + "\n\n"
    docText2 = "\n\n".join(ipsumText[1:3]) + "\n\n"
    docText3 = "\n\n".join(ipsumText[2:4]) + "\n\n"
    docText4 = "\n\n".join(ipsumText[3:5]) + "\n\n"

    lenText1 = len(docText1)
    lenText2 = len(docText2)
    lenText3 = len(docText3)
    lenText4 = len(docText4)
    lenAll = lenText1 + lenText2 + lenText3 + lenText4

    project.writeNewFile(hChapter1, 2, True, docText1)
    project.writeNewFile(hSceneOne11, 3, True, docText2)
    project.writeNewFile(hSceneOne12, 3, True, docText3)
    project.writeNewFile(hSceneOne13, 3, True, docText4)

    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Chapter 1", "Scene 1.1", "Scene 1.2", "Scene 1.3",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Invalid file handle
    assert projTree.mergeDocuments(C.hInvalid, False) is False

    # Cannot merge root item
    assert projTree.mergeDocuments(C.hNovelRoot, False) is False

    # Merge to new file, but there is now merge data
    mergeData.clear()
    assert projTree.mergeDocuments(hChapter1, True) is False

    # Merge to New Doc
    # ================

    # Set merge job for new documents
    mergeData["finalItems"] = [hChapter1, hSceneOne11, hSceneOne12, hSceneOne13]
    mergeData["moveToTrash"] = False

    # User cancels merge
    with monkeypatch.context() as mp:
        mp.setattr(GuiDocMerge, "result", lambda *a: QtRejected)
        assert projTree.mergeDocuments(hChapter1, True) is False

    # The merge goes through
    assert projTree.mergeDocuments(hChapter1, True) is True
    mergedText = project.storage.getDocument(mergedDoc1).readDocument()
    assert mergedText is not None
    assert len(mergedText) > lenAll
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Chapter 1", "Scene 1.1", "Scene 1.2", "Scene 1.3", "[Merged] Chapter 1",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Merge to Existing Doc
    # =====================

    # Set merge job for parent document
    mergeData["finalItems"] = [hSceneOne11, hSceneOne12, hSceneOne13]
    mergeData["moveToTrash"] = False

    # Merging to a folder is not allowed
    assert projTree.mergeDocuments(C.hChapterDir, False) is False

    # Block writing and check error handling
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert projTree.mergeDocuments(hChapter1, False) is False

    # Successful merge, and move to trash
    mergeData["moveToTrash"] = True
    mergedText = project.storage.getDocument(hChapter1).readDocument()
    assert mergedText is not None
    assert len(mergedText) < lenAll
    assert projTree.mergeDocuments(hChapter1, False) is True
    mergedText = project.storage.getDocument(hChapter1).readDocument()
    assert mergedText is not None
    assert len(mergedText) > lenAll

    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Chapter 1", "[Merged] Chapter 1",
        "Plot", "Characters", "Locations", "Trash",
        "Scene 1.1", "Scene 1.2", "Scene 1.3",
    ]

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

    projView = nwGUI.projView
    projTree = projView.projTree
    project = SHARED.project
    tree = project.tree

    # Create a project
    buildTestProject(nwGUI, projPath)
    trash = tree.trash
    assert trash is not None
    assert len(tree) == 9
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Trash",
    ]

    docText = (
        "Text\n\n"
        "##! Prologue\n\nText\n\n"
        "## Chapter One\n\nText\n\n"
        "### Scene One\n\nText\n\n"
        "###! Scene Two\n\nText\n\n"
        "## Chapter Two\n\nText\n\n"
        "### Scene Three\n\nText\n\n"
        "###! Scene Four\n\nText\n\n"
        "#! New Title\n\nText\n\n"
        "## New Chapter\n\nText\n\n"
        "### New Scene\n\nText\n\n"
        "#### New Section\n\nText\n\n"
    )

    hSplitDoc = project.newFile("Split Doc", C.hNovelRoot)
    assert hSplitDoc is not None
    project.writeNewFile(hSplitDoc, 1, True, docText)

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
        "0000000000012", "0000000000013", "0000000000014", "0000000000015",
        "0000000000016", "0000000000017", "0000000000018", "0000000000019",
        "000000000001a", "000000000001b", "000000000001c", "000000000001d",
    ]
    sndSet = [
        "000000000001e", "000000000001f", "0000000000020", "0000000000021",
        "0000000000022", "0000000000023", "0000000000024", "0000000000025",
        "0000000000026", "0000000000027", "0000000000028", "0000000000029",
    ]
    trdSet = [
        "000000000002b", "000000000002c", "000000000002d", "000000000002e",
        "000000000002f", "0000000000030", "0000000000031", "0000000000032",
        "0000000000033", "0000000000034", "0000000000035", "0000000000036",
    ]

    # Try to split an invalid document and a non-document
    assert projTree.splitDocument(C.hInvalid) is False
    assert projTree.splitDocument(C.hNovelRoot) is False

    # Split into same root folder
    splitData["intoFolder"] = False

    # Writing fails
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert projTree.splitDocument(hSplitDoc) is True
        for tHandle in fstSet:
            assert tHandle in project.tree
            assert not (projPath / "content" / f"{tHandle}.nwd").is_file()

    # Writing succeeds
    assert projTree.splitDocument(hSplitDoc) is True
    for tHandle in sndSet:
        assert tHandle in project.tree
        assert (projPath / "content" / f"{tHandle}.nwd").is_file()

    # Add to a folder and move source to trash
    splitData["intoFolder"] = True
    splitData["moveToTrash"] = True
    assert projTree.splitDocument(hSplitDoc) is True
    assert "0000000000029" in project.tree  # The folder
    for tHandle in trdSet:
        assert tHandle in project.tree
        assert (projPath / "content" / f"{tHandle}.nwd").is_file()

    assert trash.allChildren() == [tree.nodes[hSplitDoc]]

    # Cancelled by user
    with monkeypatch.context() as mp:
        mp.setattr(GuiDocSplit, "result", lambda *a: QtRejected)
        assert projTree.splitDocument(hSplitDoc) is False

    # qtbot.stop()


@pytest.mark.gui
def testGuiProjTree_Duplicate(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test the duplicate items function."""
    # Create a project
    projView = nwGUI.projView
    projTree = projView.projTree
    project = SHARED.project
    tree = project.tree

    # Create a project
    buildTestProject(nwGUI, projPath)
    trash = tree.trash
    assert trash is not None
    assert len(tree) == 9
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Trash",
    ]

    projTree.expandAll()

    # Nothing to do
    projTree.duplicateFromHandle(C.hInvalid)
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Duplicate title page, but select no
    with monkeypatch.context() as mp:
        mp.setattr(_GuiAlert, "finalState", False)
        projTree.duplicateFromHandle(C.hTitlePage)
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Duplicate title page
    projTree.duplicateFromHandle(C.hTitlePage)
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "Title Page", "New Folder", "New Chapter",
        "New Scene", "Plot", "Characters", "Locations", "Trash",
    ]

    # Duplicate folder
    projTree.duplicateFromHandle(C.hChapterDir)
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "Title Page", "New Folder", "New Chapter",
        "New Scene", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Duplicate novel root
    projTree.duplicateFromHandle(C.hNovelRoot)
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "Title Page", "New Folder", "New Chapter",
        "New Scene", "New Folder", "New Chapter", "New Scene",
        "Novel", "Title Page", "Title Page", "New Folder", "New Chapter",
        "New Scene", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # qtbot.stop()


@pytest.mark.gui
def testGuiProjTree_Other(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test various parts of the project tree class not covered by
    other tests.
    """
    buildTestProject(nwGUI, projPath)
    projView = nwGUI.projView
    projTree = projView.projTree

    # Method: initSettings
    # ====================

    # Test that the scrollbar setting works
    CONFIG.hideVScroll = True
    CONFIG.hideHScroll = True
    projView.initSettings()
    assert projTree.verticalScrollBarPolicy() == QtScrollAlwaysOff
    assert projTree.horizontalScrollBarPolicy() == QtScrollAlwaysOff

    CONFIG.hideVScroll = False
    CONFIG.hideHScroll = False
    projView.initSettings()
    assert projTree.verticalScrollBarPolicy() == QtScrollAsNeeded
    assert projTree.horizontalScrollBarPolicy() == QtScrollAsNeeded

    # qtbot.stop()


@pytest.mark.gui
def testGuiProjTree_ContextMenu(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test the building of the project tree context menu. All this does
    is test that the menu builds. It doesn't open the actual menu.
    """
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))
    QtSelect = QItemSelectionModel.SelectionFlag.Select

    # Create a project
    projView = nwGUI.projView
    projTree = projView.projTree
    project = SHARED.project
    tree = project.tree
    model = tree.model

    # Create a project
    buildTestProject(nwGUI, projPath)
    trash = tree.trash
    assert trash is not None
    assert len(tree) == 9
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Handles for new objects
    hCharNote     = "0000000000011"
    hNovelNote    = "0000000000012"
    hTrashDoc     = "0000000000013"
    hSubNote      = "0000000000014"
    hNewFolderOne = "0000000000015"
    hNewFolderTwo = "0000000000017"
    hTrashRoot    = trash.item.itemHandle

    projTree.expandAll()
    projTree.setSelectedHandle(C.hCharRoot)
    projTree.newTreeItem(nwItemType.FILE, isNote=True)
    projTree.setSelectedHandle(C.hNovelRoot)
    projTree.newTreeItem(nwItemType.FILE, isNote=True)
    projTree.setSelectedHandle(C.hNovelRoot)
    projTree.newTreeItem(nwItemType.FILE)
    projTree.setSelectedHandle(hTrashDoc)
    projTree.processDeleteRequest()

    project.newFile("SubNote", hNovelNote)
    item = tree[hSubNote]
    assert item is not None
    assert item.itemName == "SubNote"
    assert item.itemParent == hNovelNote

    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "New Note", "SubNote", "Plot", "Characters", "New Note", "Locations",
        "Trash", "New Part",
    ]

    # Pop the menu in various positions and check for success
    with monkeypatch.context() as mp:
        mockMenu = MagicMock()
        mp.setattr(QMenu, "exec", mockMenu)
        projTree._clearSelection()

        # No item under menu
        projTree.openContextMenu(projTree.viewport().rect().bottomRight())
        assert mockMenu.call_count == 0

        # Open Trash Menu
        projView.setSelectedHandle(hTrashRoot)
        projTree.openContextMenu()
        assert mockMenu.call_count == 1

        # Open Single Select Menu
        projView.setSelectedHandle(C.hNovelRoot)
        projTree.openContextMenu()
        assert mockMenu.call_count == 2

        # Open Multi-Select Menu
        projTree.selectionModel().select(model.indexFromHandle(hNovelNote), QtSelect)
        projTree.selectionModel().select(model.indexFromHandle(hSubNote), QtSelect)
        projTree.openContextMenu()
        assert mockMenu.call_count == 3
        projTree.clearSelection()

    # Menu Builders
    # =============

    # Context Menu on Root Item
    node = tree.nodes[C.hNovelRoot]
    indices = [model.indexFromHandle(C.hNovelRoot)]
    ctxMenu = _TreeContextMenu(projTree, model, node, indices)
    ctxMenu.buildSingleSelectMenu()
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Create New ...", "Rename", "Set Status to ...", "Expand All",
        "Collapse All", "Duplicate", "Delete Permanently",
    ]

    # Context Menu on Folder Item
    node = tree.nodes[C.hChapterDir]
    indices = [model.indexFromHandle(C.hChapterDir)]
    ctxMenu = _TreeContextMenu(projTree, model, node, indices)
    ctxMenu.buildSingleSelectMenu()
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Create New ...", "Rename", "Set Status to ...", "Transform ...", "Expand All",
        "Collapse All", "Duplicate", "Move to Trash",
    ]

    def getTransformSubMenu(menu: QMenu) -> list[str]:
        for action in menu.actions():
            if action.text() == "Transform ...":
                submenu = action.menu()
                assert submenu is not None
                return [x.text() for x in submenu.actions() if x.text()]
        return []

    # Context Menu on Document File Item
    node = tree.nodes[C.hChapterDoc]
    indices = [model.indexFromHandle(C.hChapterDoc)]
    ctxMenu = _TreeContextMenu(projTree, model, node, indices)
    ctxMenu.buildSingleSelectMenu()
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Open Document", "View Document", "Create New ...", "Rename", "Rename to Heading",
        "Toggle Active", "Set Status to ...", "Transform ...", "Duplicate", "Move to Trash",
    ]
    assert getTransformSubMenu(ctxMenu) == [
        "Convert to Project Note", "Split Document by Headings"
    ]

    # Context Menu on Note File Item in Character Folder
    node = tree.nodes[hCharNote]
    indices = [model.indexFromHandle(hCharNote)]
    ctxMenu = _TreeContextMenu(projTree, model, node, indices)
    ctxMenu.buildSingleSelectMenu()
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Open Document", "View Document", "Create New ...", "Rename", "Rename to Heading",
        "Toggle Active", "Set Importance to ...", "Transform ...", "Duplicate", "Move to Trash",
    ]
    assert getTransformSubMenu(ctxMenu) == [
        "Split Document by Headings",
    ]

    # Context Menu on Note File Item in Novel Tree
    node = tree.nodes[hNovelNote]
    indices = [model.indexFromHandle(hNovelNote)]
    ctxMenu = _TreeContextMenu(projTree, model, node, indices)
    ctxMenu.buildSingleSelectMenu()
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Open Document", "View Document", "Create New ...", "Rename", "Rename to Heading",
        "Toggle Active", "Set Status to ...", "Transform ...", "Expand All", "Collapse All",
        "Duplicate", "Move to Trash",
    ]
    assert getTransformSubMenu(ctxMenu) == [
        "Convert to Novel Document", "Merge Child Items into Self",
        "Merge Child Items into New", "Split Document by Headings",
    ]

    # Context Menu on Multiple Items, Clicked on Document
    node = tree.nodes[hNovelNote]
    indices = [
        model.indexFromHandle(hCharNote),
        model.indexFromHandle(hNovelNote),
        model.indexFromHandle(hSubNote),
    ]
    ctxMenu = _TreeContextMenu(projTree, model, node, indices)
    ctxMenu.buildMultiSelectMenu()
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Set Active to ...", "Set Status to ...", "Move to Trash",
    ]

    # Context Menu on Multiple Items, Clicked on Note
    node = tree.nodes[hCharNote]
    indices = [
        model.indexFromHandle(hCharNote),
        model.indexFromHandle(hNovelNote),
        model.indexFromHandle(hSubNote),
    ]
    ctxMenu = _TreeContextMenu(projTree, model, node, indices)
    ctxMenu.buildMultiSelectMenu()
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Set Active to ...", "Set Importance to ...", "Move to Trash",
    ]

    # Direct Edit Functions, Single
    # =============================

    node = tree.nodes[hNovelNote]
    indices = [model.indexFromHandle(hNovelNote)]

    # Toggle active flag
    ctxMenu = _TreeContextMenu(projTree, model, node, indices)
    ctxMenu.buildSingleSelectMenu()
    assert node.item.isActive is True
    ctxMenu._toggleItemActive()
    assert node.item.isActive is False

    # Change item status
    assert node.item.itemStatus == "s000000"
    ctxMenu._changeItemStatus("s000001")
    assert node.item.itemStatus == "s000001"

    # Change item importance
    assert node.item.itemImport == "i000004"
    ctxMenu._changeItemImport("i000005")
    assert node.item.itemImport == "i000005"

    # Change item layout
    assert node.item.itemLayout == nwItemLayout.NOTE
    ctxMenu._changeItemLayout(nwItemLayout.DOCUMENT)
    assert node.item.itemLayout == nwItemLayout.DOCUMENT
    ctxMenu._changeItemLayout(nwItemLayout.NOTE)
    assert node.item.itemLayout == nwItemLayout.NOTE

    # Convert Folders to Documents
    # ============================

    projView.setSelectedHandle(hNovelNote)
    projTree.newTreeItem(nwItemType.FOLDER)
    projView.setSelectedHandle(hNewFolderOne)
    projTree.newTreeItem(nwItemType.FILE)

    projView.setSelectedHandle(hNovelNote)
    projTree.newTreeItem(nwItemType.FOLDER)
    projView.setSelectedHandle(hNewFolderTwo)
    projTree.newTreeItem(nwItemType.FILE, isNote=True)

    assert hNewFolderOne in tree
    assert hNewFolderTwo in tree

    nodeOne = tree.nodes[hNewFolderOne]
    nodeTwo = tree.nodes[hNewFolderTwo]

    # Select Folder One
    indices = [model.indexFromHandle(hNewFolderOne)]
    ctxMenu = _TreeContextMenu(projTree, model, nodeOne, indices)
    ctxMenu.buildSingleSelectMenu()

    # Click no on the dialog
    with monkeypatch.context() as mp:
        mp.setattr(_GuiAlert, "finalState", False)
        ctxMenu._convertFolderToFile(nwItemLayout.DOCUMENT)
        assert nodeOne.item.isFolderType()

    # Convert the first folder to a document
    assert nodeOne.item.isFolderType()
    ctxMenu._convertFolderToFile(nwItemLayout.DOCUMENT)
    assert nodeOne.item.isFileType()
    assert nodeOne.item.isDocumentLayout()

    # Select Folder Two
    indices = [model.indexFromHandle(hNewFolderTwo)]
    ctxMenu = _TreeContextMenu(projTree, model, nodeTwo, indices)
    ctxMenu.buildSingleSelectMenu()

    # Convert the second folder to a note
    ctxMenu._convertFolderToFile(nwItemLayout.NOTE)
    assert nodeTwo.item.isFileType()
    assert nodeTwo.item.isNoteLayout()

    # Direct Edit Functions, Multi
    # ============================

    node = tree.nodes[hCharNote]
    indices = [
        model.indexFromHandle(hCharNote),
        model.indexFromHandle(hNovelNote),
        model.indexFromHandle(hSubNote),
    ]
    ctxMenu = _TreeContextMenu(projTree, model, node, indices)
    ctxMenu.buildMultiSelectMenu()

    # projTree.clearSelection()
    # projTree._getTreeItem(hCharNote).setSelected(True)
    # projTree._getTreeItem(hNovelNote).setSelected(True)
    # projTree._getTreeItem(hSubNote).setSelected(True)

    nodeCNote = tree.nodes[hCharNote]
    nodeNNote = tree.nodes[hNovelNote]
    nodeSNote = tree.nodes[hSubNote]

    # Item Active
    assert nodeCNote.item.isActive is True
    assert nodeNNote.item.isActive is False
    assert nodeSNote.item.isActive is True
    ctxMenu._iterItemActive(False)
    assert nodeCNote.item.isActive is False
    assert nodeNNote.item.isActive is False
    assert nodeSNote.item.isActive is False
    ctxMenu._iterItemActive(True)
    assert nodeCNote.item.isActive is True
    assert nodeNNote.item.isActive is True
    assert nodeSNote.item.isActive is True

    # Item Status
    assert nodeCNote.item.itemStatus == "s000000"
    assert nodeNNote.item.itemStatus == "s000001"
    assert nodeSNote.item.itemStatus == "s000000"
    ctxMenu._iterSetItemStatus("s000003")
    assert nodeCNote.item.itemStatus == "s000000"
    assert nodeNNote.item.itemStatus == "s000003"
    assert nodeSNote.item.itemStatus == "s000003"

    # Item Importance
    assert nodeCNote.item.itemImport == "i000004"
    assert nodeNNote.item.itemImport == "i000005"
    assert nodeSNote.item.itemImport == "i000004"
    ctxMenu._iterSetItemImport("i000007")
    assert nodeCNote.item.itemImport == "i000007"
    assert nodeNNote.item.itemImport == "i000005"
    assert nodeSNote.item.itemImport == "i000004"

    # qtbot.stop()


@pytest.mark.gui
def testGuiProjTree_Templates(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test the templates feature of the project tree."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    # Create a project
    projView = nwGUI.projView
    projTree = projView.projTree
    projBar  = projView.projBar
    project = SHARED.project
    tree = project.tree

    # Create a project
    buildTestProject(nwGUI, projPath)
    trash = tree.trash
    assert trash is not None
    assert len(tree) == 9
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Handles for new objects
    hTemplatesRoot = "0000000000011"
    hSceneTemplate = "0000000000012"
    hNoteTemplate  = "0000000000013"
    hNewScene      = "0000000000014"
    hNewCharacter  = "0000000000015"

    # Add template folder
    projTree.newTreeItem(nwItemType.ROOT, nwItemClass.TEMPLATE)
    nwTemplateRoot = tree[hTemplatesRoot]
    assert nwTemplateRoot is not None
    assert nwTemplateRoot.itemName == "Templates"

    # Add a scene template
    projTree.setSelectedHandle(hTemplatesRoot)
    projTree.newTreeItem(nwItemType.FILE, hLevel=3, isNote=False)
    nwSceneTemplate = tree[hSceneTemplate]
    assert nwSceneTemplate is not None
    assert nwSceneTemplate.itemName == "New Scene"
    assert projBar.mTemplates.actions()[0].text() == "New Scene"

    # Rename the scene template
    projView.renameTreeItem(hSceneTemplate, name="Scene")
    assert projBar.mTemplates.actions()[0].text() == "Scene"

    # Add a note template
    projTree.setSelectedHandle(hTemplatesRoot)
    projTree.newTreeItem(nwItemType.FILE, hLevel=1, isNote=True)
    nwNoteTemplate = project.tree[hNoteTemplate]
    assert nwNoteTemplate is not None
    assert nwNoteTemplate.itemName == "New Note"
    assert projBar.mTemplates.actions()[1].text() == "New Note"

    # Rename the note template
    projView.renameTreeItem(hNoteTemplate, name="Note")
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
    assert project.storage.getDocument(hNewCharacter).readDocument() == "# Note\n\n@tag: Jane\n\n"

    # Clearing the menu and rebuilding it should work
    projBar.mTemplates.clearMenu()
    assert len(projBar.mTemplates.actions()) == 0
    projBar.buildTemplatesMenu()
    assert len(projBar.mTemplates.actions()) == 2

    # Remove the note template
    assert projBar.mTemplates.menuAction().isVisible() is True
    assert len(projBar.mTemplates.actions()) == 2
    assert trash.childCount() == 0
    projTree.processDeleteRequest([hNoteTemplate])
    assert trash.childCount() == 1
    assert len(projBar.mTemplates.actions()) == 1
    projTree.processDeleteRequest([hSceneTemplate])
    assert len(projBar.mTemplates.actions()) == 0
    assert projBar.mTemplates.menuAction().isVisible() is False

    # qtbot.stop()
