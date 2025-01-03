"""
novelWriter – Item Model Tester
===============================

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

import pytest

from PyQt5.QtCore import QMimeData, QModelIndex, Qt

from novelwriter.common import decodeMimeHandles
from novelwriter.constants import nwConst
from novelwriter.core.item import NWItem
from novelwriter.core.itemmodel import INV_ROOT, NODE_FLAGS, ProjectNode
from novelwriter.core.project import NWProject
from novelwriter.enum import nwItemLayout, nwItemType

from tests.tools import buildTestProject


@pytest.mark.core
def testCoreItemModel_ProjectNode_Root(mockGUI):
    """Test the project node class for the root."""
    project = NWProject()
    root = ProjectNode(NWItem(project, INV_ROOT))

    # Defaults
    assert bool(root) is True
    assert root.item.itemHandle == INV_ROOT
    assert repr(root) == "<ProjectNode handle=invisibleRoot parent=None row=0 children=0>"
    assert root.children == []
    assert root.count == 0

    # Data
    assert root.row() == 0
    assert root.childCount() == 0
    assert root.parent() is None
    assert root.child(0) is None
    assert root.allChildren() == []


@pytest.mark.core
def testCoreItemModel_ProjectNode_Children(mockGUI, mockRnd, fncPath):
    """Test the project node class for children."""
    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)
    root = project.tree.model.root

    # Check Root
    assert root.childCount() == 4
    assert root.count == 9

    # Check Children
    child0 = root.child(0)
    child1 = root.child(1)
    child2 = root.child(2)
    child3 = root.child(3)

    assert child0 is not None
    assert child1 is not None
    assert child2 is not None
    assert child3 is not None

    assert child0.item.itemName == "Novel"
    assert child1.item.itemName == "Plot"
    assert child2.item.itemName == "Characters"
    assert child3.item.itemName == "Locations"

    assert child0.childCount() == 2
    assert child1.childCount() == 0
    assert child2.childCount() == 0
    assert child3.childCount() == 0

    # Check Novel Content
    child00 = child0.child(0)
    child01 = child0.child(1)

    assert child00 is not None
    assert child01 is not None

    assert child00.item.itemName == "Title Page"
    assert child01.item.itemName == "New Folder"

    child010 = child01.child(0)
    child011 = child01.child(1)

    assert child010 is not None
    assert child011 is not None

    assert child010.item.itemName == "New Chapter"
    assert child011.item.itemName == "New Scene"

    # Check Relationships
    assert child0.parent() is root
    assert child1.parent() is root
    assert child2.parent() is root
    assert child3.parent() is root
    assert child01.parent() is child0
    assert child010.parent() is child01
    assert child011.parent() is child01

    # Expand
    child0.setExpanded(True)
    child1.setExpanded(True)
    child2.setExpanded(True)
    child3.setExpanded(True)
    assert child0.item.isExpanded is True  # Only one with children
    assert child1.item.isExpanded is False
    assert child2.item.isExpanded is False
    assert child3.item.isExpanded is False


@pytest.mark.core
def testCoreItemModel_ProjectNode_Modify(mockGUI, mockRnd, fncPath):
    """Test modifying project nodes."""
    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)
    root = project.tree.model.root

    # Novel folder
    novel = root.child(0)
    assert novel is not None
    assert novel.item.itemName == "Novel"

    # Chapter folder
    folder = novel.child(1)
    assert folder is not None
    assert folder.item.itemName == "New Folder"

    # Append scene
    project.tree.create("Scene 1", folder.item.itemHandle, nwItemType.FILE)
    scene1 = folder.child(2)
    assert scene1 is not None
    assert scene1.item.itemName == "Scene 1"

    # Insert scene
    project.tree.create("Scene 2", folder.item.itemHandle, nwItemType.FILE, pos=1)
    scene2 = folder.child(1)
    assert scene2 is not None
    assert scene2.item.itemName == "Scene 2"

    # Scene 1 should now have moved
    assert scene1.row() == 3
    assert [n.item.itemName for n in folder.children] == [
        "New Chapter", "Scene 2", "New Scene", "Scene 1",
    ]

    # Check that defaults have been set
    assert scene1.item.itemParent == folder.item.itemHandle
    assert scene2.item.itemParent == folder.item.itemHandle

    assert scene1.item.itemClass == folder.item.itemClass
    assert scene2.item.itemClass == folder.item.itemClass

    assert scene1.item.itemLayout == nwItemLayout.DOCUMENT
    assert scene2.item.itemLayout == nwItemLayout.DOCUMENT

    # Move Scene 2, invalid position is ignored
    folder.moveChild(1, -1)
    scene2 = folder.child(1)
    assert scene2 is not None
    assert scene2.item.itemName == "Scene 2"

    # Move Scene 2, past end is ignored
    folder.moveChild(1, 20)
    scene2 = folder.child(1)
    assert scene2 is not None
    assert scene2.item.itemName == "Scene 2"

    # Move Scene 2, last position is ok
    folder.moveChild(1, 3)
    scene2 = folder.child(3)
    assert scene2 is not None
    assert scene2.item.itemName == "Scene 2"
    assert [n.item.itemName for n in folder.children] == [
        "New Chapter", "New Scene", "Scene 1", "Scene 2",
    ]

    # Remove original scene, invalid position
    removed = folder.takeChild(-1)
    assert removed is None
    assert folder.childCount() == 4

    # Remove original scene, past end
    removed = folder.takeChild(20)
    assert removed is None
    assert folder.childCount() == 4

    # Remove original scene, ok
    removed = folder.takeChild(1)
    assert removed is not None
    assert removed.item.itemName == "New Scene"
    assert folder.childCount() == 3
    assert [n.item.itemName for n in folder.children] == [
        "New Chapter", "Scene 1", "Scene 2",
    ]


@pytest.mark.core
def testCoreItemModel_ProjectNode_Data(mockGUI, mockRnd, fncPath):
    """Test data access from project nodes."""
    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)
    root = project.tree.model.root

    # Novel folder
    novel = root.child(0)
    assert novel is not None
    assert novel.item.itemName == "Novel"

    # Chapter folder
    folder = novel.child(1)
    assert folder is not None
    assert folder.item.itemName == "New Folder"

    # Scene document
    scene = folder.child(1)
    assert scene is not None
    assert scene.item.itemName == "New Scene"

    # Check Data
    assert novel.data(0, Qt.ItemDataRole.DisplayRole) == "Novel"
    assert novel.data(1, Qt.ItemDataRole.DisplayRole) == "9"
    assert scene.data(0, Qt.ItemDataRole.DisplayRole) == "New Scene"
    assert scene.data(1, Qt.ItemDataRole.DisplayRole) == "2"

    assert novel.data(2, Qt.ItemDataRole.ToolTipRole) == ""
    assert novel.data(3, Qt.ItemDataRole.ToolTipRole) == "New"
    assert scene.data(2, Qt.ItemDataRole.ToolTipRole) == "Active"
    assert scene.data(3, Qt.ItemDataRole.ToolTipRole) == "New"

    # Check Flags
    assert novel.flags() == NODE_FLAGS
    assert scene.flags() == NODE_FLAGS | Qt.ItemFlag.ItemIsDragEnabled


@pytest.mark.core
def testCoreItemModel_ProjectModel_Interface(mockGUI, mockRnd, fncPath):
    """Test the model interface for the project model."""
    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)
    model = project.tree.model

    # Init
    assert isinstance(model.root, ProjectNode)
    assert model.root.item.itemHandle == INV_ROOT

    # Indices
    rootIdx = QModelIndex()
    novelIdx = model.index(0, 0, rootIdx)
    folderIdx = model.index(1, 0, novelIdx)
    sceneIdx = model.index(1, 0, folderIdx)
    invalidIdx = model.index(-1, -1)

    assert rootIdx.isValid() is False
    assert novelIdx.isValid() is True
    assert folderIdx.isValid() is True
    assert sceneIdx.isValid() is True
    assert invalidIdx.isValid() is False

    # Columns and Rows
    assert model.rowCount(rootIdx) == 4
    assert model.columnCount(rootIdx) == 4
    assert model.rowCount(novelIdx) == 2
    assert model.columnCount(novelIdx) == 4

    # Parent of Novel
    parent = model.parent(novelIdx)
    assert parent.row() == 0
    assert parent.column() == 0
    assert parent.internalPointer() is model.root

    # Parent of Root
    parent = model.parent(rootIdx)
    assert parent.isValid() is False

    # Data and Flags
    assert model.data(novelIdx, Qt.ItemDataRole.DisplayRole) == "Novel"
    assert model.data(sceneIdx, Qt.ItemDataRole.DisplayRole) == "New Scene"
    assert model.data(invalidIdx, Qt.ItemDataRole.DisplayRole) is None
    assert model.flags(novelIdx) == NODE_FLAGS
    assert model.flags(sceneIdx) == NODE_FLAGS | Qt.ItemFlag.ItemIsDragEnabled
    assert model.flags(invalidIdx) == Qt.ItemFlag.NoItemFlags


@pytest.mark.core
def testCoreItemModel_ProjectModel_DragNDrop(mockGUI, mockRnd, fncPath):
    """Test drag and drop for the project model."""
    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)
    model = project.tree.model

    # Nodes
    novel = model.root.child(0)
    assert novel is not None
    folder = novel.child(1)
    assert folder is not None
    chapter = folder.child(0)
    assert chapter is not None
    scene = folder.child(1)
    assert scene is not None

    assert novel.item.itemName == "Novel"
    assert folder.item.itemName == "New Folder"
    assert chapter.item.itemName == "New Chapter"
    assert scene.item.itemName == "New Scene"

    # Indices
    rootIdx = QModelIndex()
    novelIdx = model.index(0, 0, rootIdx)
    folderIdx = model.index(1, 0, novelIdx)
    chapterIdx = model.index(0, 0, folderIdx)
    sceneIdx = model.index(1, 0, folderIdx)
    invalidIdx = model.index(-1, -1)

    # Only move is allowed
    assert model.supportedDragActions() == Qt.DropAction.MoveAction
    assert model.supportedDropActions() == Qt.DropAction.MoveAction

    # Only handles are dragged and dropped
    assert model.mimeTypes() == [nwConst.MIME_HANDLE]

    # Get mime data
    novelMime = model.mimeData([novelIdx])
    assert decodeMimeHandles(novelMime) == [novel.item.itemHandle]

    sceneMime = model.mimeData([sceneIdx])
    assert decodeMimeHandles(sceneMime) == [scene.item.itemHandle]

    sceneChapterMime = model.mimeData([chapterIdx, sceneIdx])
    assert decodeMimeHandles(sceneChapterMime) == [
        chapter.item.itemHandle, scene.item.itemHandle,
    ]

    multiMime = model.mimeData([novelIdx, folderIdx, sceneIdx, invalidIdx])
    assert decodeMimeHandles(multiMime) == [
        novel.item.itemHandle, folder.item.itemHandle, scene.item.itemHandle,
    ]

    # Check that drop is possible
    invalidMime = QMimeData()
    invalidMime.setData("plain/text", b"foobar")

    assert model.canDropMimeData(invalidMime, Qt.DropAction.MoveAction, 0, 0, novelIdx) is False
    assert model.canDropMimeData(sceneMime, Qt.DropAction.MoveAction, 0, 0, novelIdx) is True

    # Drop the scene on the novel folder
    assert [n.item.itemName for n in model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations",
    ]
    assert model.dropMimeData(invalidMime, Qt.DropAction.MoveAction, 0, 0, novelIdx) is False
    assert model.dropMimeData(sceneChapterMime, Qt.DropAction.MoveAction, 0, 0, novelIdx) is True
    assert [n.item.itemName for n in model.root.allChildren()] == [
        "Novel", "New Chapter", "New Scene", "Title Page", "New Folder",
        "Plot", "Characters", "Locations",
    ]


@pytest.mark.core
def testCoreItemModel_ProjectModel_Data(mockGUI, mockRnd, fncPath):
    """Test data access for the project model."""
    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)
    model = project.tree.model

    # Nodes
    root = model.root
    novel = root.child(0)
    assert novel is not None
    folder = novel.child(1)
    assert folder is not None
    chapter = folder.child(0)
    assert chapter is not None
    scene = folder.child(1)
    assert scene is not None

    assert novel.item.itemName == "Novel"
    assert folder.item.itemName == "New Folder"
    assert chapter.item.itemName == "New Chapter"
    assert scene.item.itemName == "New Scene"

    # Indices
    rootIdx = QModelIndex()
    novelIdx = model.index(0, 0, rootIdx)
    folderIdx = model.index(1, 0, novelIdx)
    chapterIdx = model.index(0, 0, folderIdx)
    sceneIdx = model.index(1, 0, folderIdx)
    invalidIdx = model.index(-1, -1)

    # Check Rows
    assert model.row(rootIdx) == -1
    assert model.row(novelIdx) == 0
    assert model.row(folderIdx) == 1
    assert model.row(chapterIdx) == 0
    assert model.row(sceneIdx) == 1
    assert model.row(invalidIdx) == -1

    # Check Nodes
    assert model.node(rootIdx) is None
    assert model.node(novelIdx) is novel
    assert model.node(folderIdx) is folder
    assert model.node(chapterIdx) is chapter
    assert model.node(sceneIdx) is scene
    assert model.node(invalidIdx) is None

    nodes = model.nodes([novelIdx, folderIdx, chapterIdx, sceneIdx])
    assert nodes[0] is novel
    assert nodes[1] is folder
    assert nodes[2] is chapter
    assert nodes[3] is scene

    # Index from Handle
    assert model.indexFromHandle(None).isValid() is False
    assert model.node(model.indexFromHandle(novel.item.itemHandle)) is novel
    assert model.node(model.indexFromHandle(folder.item.itemHandle)) is folder
    assert model.node(model.indexFromHandle(chapter.item.itemHandle)) is chapter
    assert model.node(model.indexFromHandle(scene.item.itemHandle)) is scene

    # Index from Node
    assert model.indexFromHandle(None).isValid() is False
    assert model.node(model.indexFromNode(novel)) is novel
    assert model.node(model.indexFromNode(folder)) is folder
    assert model.node(model.indexFromNode(chapter)) is chapter
    assert model.node(model.indexFromNode(scene)) is scene


@pytest.mark.core
def testCoreItemModel_ProjectModel_Edit(qtbot, mockGUI, mockRnd, fncPath):
    """Test editing the project model."""
    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)
    model = project.tree.model

    # Nodes
    root = model.root
    novel = root.child(0)
    assert novel is not None
    title = novel.child(0)
    assert title is not None
    folder = novel.child(1)
    assert folder is not None
    chapter = folder.child(0)
    assert chapter is not None
    scene = folder.child(1)
    assert scene is not None

    assert novel.item.itemName == "Novel"
    assert title.item.itemName == "Title Page"
    assert folder.item.itemName == "New Folder"
    assert chapter.item.itemName == "New Chapter"
    assert scene.item.itemName == "New Scene"

    # Indices
    novelIdx = model.indexFromNode(novel)
    titleIdx = model.indexFromNode(title)
    folderIdx = model.indexFromNode(folder)
    chapterIdx = model.indexFromNode(chapter)
    sceneIdx = model.indexFromNode(scene)
    invalidIdx = model.index(-1, -1)

    # Initial Order
    assert [n.item.itemName for n in model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations",
    ]

    # Remove Child, invalid index
    assert model.removeChild(novelIdx, -1) is None
    assert model.removeChild(novelIdx, 99) is None

    # Remove Child
    with qtbot.waitSignal(model.rowsAboutToBeRemoved) as signal:
        child = model.removeChild(novelIdx, titleIdx.row())
    assert signal.args[0].internalPointer().item.itemName == "Novel"
    assert signal.args[1] == 0
    assert signal.args[2] == 0
    assert child is not None
    assert child.item.itemName == "Title Page"
    assert [n.item.itemName for n in model.root.allChildren()] == [
        "Novel", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations",
    ]
    titleIdx = model.indexFromNode(title)
    folderIdx = model.indexFromNode(folder)
    chapterIdx = model.indexFromNode(chapter)
    sceneIdx = model.indexFromNode(scene)

    # Insert Child
    with qtbot.waitSignal(model.rowsAboutToBeInserted) as signal:
        model.insertChild(child, novelIdx, 1)
    assert signal.args[0].internalPointer().item.itemName == "Novel"
    assert signal.args[1] == 1
    assert signal.args[2] == 1
    assert [n.item.itemName for n in model.root.allChildren()] == [
        "Novel", "New Folder", "New Chapter", "New Scene", "Title Page",
        "Plot", "Characters", "Locations",
    ]
    titleIdx = model.indexFromNode(title)
    folderIdx = model.indexFromNode(folder)
    chapterIdx = model.indexFromNode(chapter)
    sceneIdx = model.indexFromNode(scene)

    # Move it back with internal move
    with qtbot.waitSignal(model.rowsAboutToBeMoved) as signal:
        model.internalMove(titleIdx, -1)
    assert signal.args[0].internalPointer().item.itemName == "Novel"
    assert signal.args[1] == 1
    assert signal.args[2] == 1
    assert signal.args[3].internalPointer().item.itemName == "Novel"
    assert signal.args[4] == 0
    assert [n.item.itemName for n in model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations",
    ]
    titleIdx = model.indexFromNode(title)
    folderIdx = model.indexFromNode(folder)
    chapterIdx = model.indexFromNode(chapter)
    sceneIdx = model.indexFromNode(scene)

    # Move Multiple, with parent
    # Chapter and scene selection is flipped, but they should be deselected
    # because folder is also selected, so their order should not change
    model.multiMove([folderIdx, sceneIdx, chapterIdx, invalidIdx], novelIdx, 0)
    assert [n.item.itemName for n in model.root.allChildren()] == [
        "Novel", "New Folder", "New Chapter", "New Scene", "Title Page",
        "Plot", "Characters", "Locations",
    ]
    assert folder.parent() is novel
    assert chapter.parent() is folder
    assert scene.parent() is folder

    titleIdx = model.indexFromNode(title)
    folderIdx = model.indexFromNode(folder)
    chapterIdx = model.indexFromNode(chapter)
    sceneIdx = model.indexFromNode(scene)

    # Move Multiple, siblings, altered order
    # Chapter and scene selection is flipped, and they should now be reordered,
    # and no longer in the folder
    model.multiMove([sceneIdx, chapterIdx, invalidIdx], novelIdx, 0)
    assert [n.item.itemName for n in model.root.allChildren()] == [
        "Novel", "New Scene", "New Chapter", "New Folder", "Title Page",
        "Plot", "Characters", "Locations",
    ]
    assert folder.parent() is novel
    assert chapter.parent() is novel
    assert scene.parent() is novel


@pytest.mark.core
def testCoreItemModel_ProjectModel_Other(qtbot, mockGUI, mockRnd, fncPath):
    """Test other methods of the project model."""
    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)
    model = project.tree.model

    # Nodes
    root = model.root
    novel = root.child(0)
    assert novel is not None
    title = novel.child(0)
    assert title is not None
    folder = novel.child(1)
    assert folder is not None
    chapter = folder.child(0)
    assert chapter is not None
    scene = folder.child(1)
    assert scene is not None
    trash = project.tree.trash
    assert trash is not None

    assert novel.item.itemName == "Novel"
    assert title.item.itemName == "Title Page"
    assert folder.item.itemName == "New Folder"
    assert chapter.item.itemName == "New Chapter"
    assert scene.item.itemName == "New Scene"

    assert [n.item.itemName for n in model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Indices
    chapterIdx = model.indexFromNode(chapter)
    sceneIdx = model.indexFromNode(scene)
    trashIdx = model.indexFromNode(trash)

    # Expanded
    assert model.allExpanded() == []
    novel.item.setExpanded(True)
    folder.item.setExpanded(True)
    assert [model.node(i) for i in model.allExpanded()] == [novel, folder]

    # Check Trash
    assert model.trashSelection([chapterIdx, sceneIdx]) is False
    model.multiMove([chapterIdx, sceneIdx], trashIdx)
    assert [n.item.itemName for n in model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder",
        "Plot", "Characters", "Locations", "Trash", "New Chapter", "New Scene",
    ]

    chapterIdx = model.indexFromNode(chapter)
    sceneIdx = model.indexFromNode(scene)
    assert model.trashSelection([chapterIdx, sceneIdx]) is True

    # Clear
    model.clear()
    assert [n.item.itemName for n in model.root.allChildren()] == []
