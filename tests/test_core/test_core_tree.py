"""
novelWriter – NWTree Class Tester
=================================

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

import random

from copy import deepcopy
from pathlib import Path

import pytest

from novelwriter.constants import nwFiles
from novelwriter.core.item import NWItem
from novelwriter.core.project import NWProject
from novelwriter.core.tree import NWTree
from novelwriter.enum import nwItemClass, nwItemType

from tests.mocked import causeOSError
from tests.tools import C, buildTestProject


@pytest.fixture(scope="function")
def mockItems(mockGUI, mockRnd, fncPath):
    """Create a list of mock items."""
    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)
    return project.tree.pack()


@pytest.mark.core
def testCoreTree_Populate(monkeypatch, mockGUI, mockItems):
    """Test populating the project tree."""
    project = NWProject()
    tree = NWTree(project)

    # Check that tree is empty
    assert bool(tree) is False
    assert len(tree) == 0

    # Trash should be added on request
    assert tree.trash is not None
    assert tree.nodes[tree.trash.item.itemHandle].item.itemName == "Trash"
    assert bool(tree) is True
    assert len(tree) == 1
    tree.clear()

    # Load Items
    tree.unpack(mockItems)
    assert len(tree) == 9
    assert tree.trash is not None
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Pack the data again
    assert [n["name"] for n in tree.pack()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Inject a node in the map, but not in the tree (inconsistent tree)
    # This should be ignored
    tree._nodes["123456789abc"] = tree.model.root
    assert [n["name"] for n in tree.pack()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Clear, and populate in reverse order
    tree.clear()
    assert bool(tree) is False
    assert len(tree) == 0
    tree.unpack(list(reversed(mockItems)))
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Locations", "Characters", "Plot", "Novel", "New Folder",
        "New Scene", "New Chapter", "Title Page", "Trash",
    ]

    # Clear, and populate with one item being its own parent
    tree.clear()
    assert bool(tree) is False
    assert len(tree) == 0
    modItems = deepcopy(mockItems)
    assert modItems[1]["name"] == "Title Page"
    modItems[1]["itemAttr"]["parent"] = modItems[1]["itemAttr"]["handle"]
    tree.unpack(mockItems)
    assert len(tree) == 9
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Clear and populate reversed with max depth limit very low
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.tree.MAX_DEPTH", 1)
        tree.clear()
        assert bool(tree) is False
        assert len(tree) == 0
        tree.unpack(list(reversed(mockItems)))
        assert [n.item.itemName for n in tree.model.root.allChildren()] == [
            "Locations", "Characters", "Plot", "Novel", "Trash",
        ]


@pytest.mark.core
def testCoreTree_ManipulateTree(mockGUI, mockItems):
    """Check create, add, remove and duplicate items."""
    project = NWProject()
    tree = NWTree(project)
    tree.unpack(mockItems)
    assert len(tree) == 9
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Create Root
    oHandle = tree.create("Objects", None, nwItemType.ROOT, nwItemClass.OBJECT, pos=4)
    assert oHandle is not None
    assert oHandle in tree

    # Create Folder
    fHandle = tree.create("Foo", oHandle, nwItemType.FOLDER, pos=0)
    assert fHandle is not None
    assert fHandle in tree

    # Create File
    bHandle = tree.create("Bar", fHandle, nwItemType.FILE, pos=0)
    assert bHandle is not None
    assert bHandle in tree

    # Check Tree
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Objects", "Foo", "Bar", "Trash",
    ]

    # Cannot add a folder or file with no parent
    assert tree.create("Foo", None, nwItemType.FOLDER, pos=0) is None
    assert tree.create("Bar", None, nwItemType.FILE, pos=0) is None
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Objects", "Foo", "Bar", "Trash",
    ]

    # Duplicate Bar -> Baz
    baz = tree.duplicate(bHandle, fHandle, True)
    assert baz is not None
    baz.setName("Baz")
    zHandle = baz.itemHandle
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Objects", "Foo", "Bar", "Baz", "Trash",
    ]

    # Duplicate non-existent
    assert tree.duplicate("bob", fHandle, True) is None
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Objects", "Foo", "Bar", "Baz", "Trash",
    ]

    # Remove Baz
    assert tree.remove(zHandle) is True
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Objects", "Foo", "Bar", "Trash",
    ]
    assert len(tree._items) == len(tree.model.root.allChildren())
    assert len(tree._items) == len(tree._nodes)

    # Remove non-existing
    assert tree.remove("bob") is False

    # Add item with non-existing parent
    item = NWItem(project, tree._makeHandle())
    item.setParent(tree._makeHandle())
    assert tree.add(item) is False
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Objects", "Foo", "Bar", "Trash",
    ]

    # Add item with non parent, that isn't a root
    item = NWItem(project, tree._makeHandle())
    item.setType(nwItemType.FOLDER)
    assert tree.add(item) is False
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Objects", "Foo", "Bar", "Trash",
    ]


@pytest.mark.core
def testCoreTree_ItemMethods(monkeypatch, mockGUI, mockItems):
    """Check the item methods of the tree."""
    project = NWProject()
    tree = NWTree(project)
    tree.unpack(mockItems)
    assert len(tree) == 9
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Check Type
    assert tree.checkType(C.hNovelRoot, nwItemType.ROOT) is True
    assert tree.checkType(C.hNovelRoot, nwItemType.FOLDER) is False
    assert tree.checkType(C.hNovelRoot, nwItemType.FILE) is False

    assert tree.checkType(C.hChapterDir, nwItemType.ROOT) is False
    assert tree.checkType(C.hChapterDir, nwItemType.FOLDER) is True
    assert tree.checkType(C.hChapterDir, nwItemType.FILE) is False

    assert tree.checkType(C.hChapterDoc, nwItemType.ROOT) is False
    assert tree.checkType(C.hChapterDoc, nwItemType.FOLDER) is False
    assert tree.checkType(C.hChapterDoc, nwItemType.FILE) is True

    assert tree.checkType(C.hInvalid, nwItemType.ROOT) is False
    assert tree.checkType(C.hInvalid, nwItemType.FOLDER) is False
    assert tree.checkType(C.hInvalid, nwItemType.FILE) is False

    # Item Path
    assert tree.itemPath(C.hSceneDoc, asName=True) == ["New Scene", "New Folder", "Novel"]
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.tree.MAX_DEPTH", 1)
        assert tree.itemPath(C.hSceneDoc, asName=True) == ["New Scene"]

    # Sub Tree
    assert tree.subTree(C.hInvalid) == []
    assert tree.subTree(C.hNovelRoot) == [
        C.hTitlePage, C.hChapterDir, C.hChapterDoc, C.hSceneDoc,
    ]

    # Root Classes
    classes = tree.rootClasses()
    assert len(classes) == 5
    assert nwItemClass.NOVEL in classes
    assert nwItemClass.PLOT in classes
    assert nwItemClass.CHARACTER in classes
    assert nwItemClass.WORLD in classes
    assert nwItemClass.TIMELINE not in classes
    assert nwItemClass.OBJECT not in classes
    assert nwItemClass.ENTITY not in classes
    assert nwItemClass.CUSTOM not in classes
    assert nwItemClass.ARCHIVE not in classes
    assert nwItemClass.TEMPLATE not in classes
    assert nwItemClass.TRASH in classes

    # Iter Roots
    assert list(tree.iterRoots(nwItemClass.NOVEL)) == [(C.hNovelRoot, tree[C.hNovelRoot])]
    assert list(tree.iterRoots(nwItemClass.PLOT)) == [(C.hPlotRoot, tree[C.hPlotRoot])]
    assert list(tree.iterRoots(nwItemClass.CHARACTER)) == [(C.hCharRoot, tree[C.hCharRoot])]
    assert list(tree.iterRoots(nwItemClass.WORLD)) == [(C.hWorldRoot, tree[C.hWorldRoot])]
    assert list(tree.iterRoots(nwItemClass.OBJECT)) == []

    # Find Root
    assert tree.findRoot(nwItemClass.NOVEL) == C.hNovelRoot
    assert tree.findRoot(nwItemClass.PLOT) == C.hPlotRoot
    assert tree.findRoot(nwItemClass.CHARACTER) == C.hCharRoot
    assert tree.findRoot(nwItemClass.WORLD) == C.hWorldRoot
    assert tree.findRoot(nwItemClass.OBJECT) is None


@pytest.mark.core
def testCoreTree_OtherMethods(qtbot, monkeypatch, mockGUI, fncPath, mockRnd):
    """Check other methods in the tree."""
    project = NWProject()
    buildTestProject(project, fncPath)
    tree = project.tree
    trash = tree.trash

    assert len(tree) == 9
    assert [n.item.itemName for n in tree.model.root.allChildren()] == [
        "Novel", "Title Page", "New Folder", "New Chapter", "New Scene",
        "Plot", "Characters", "Locations", "Trash",
    ]

    # Refresh All
    assert tree.sumWords() == (9, 0)
    assert tree.model.root.count == 9

    for node in tree.nodes.values():
        if node.item.isFileType():
            node.item.setWordCount(5)

    with qtbot.waitSignal(tree._model.layoutChanged):
        tree.refreshAllItems()
    assert tree.model.root.count == 15

    project.index.rebuild()
    tree.refreshAllItems()
    assert tree.model.root.count == 9

    # Trash can't be created
    assert trash is not None
    assert tree._getTrashNode() is trash
    tree._trash = None
    assert tree._getTrashNode() is trash
    tree.remove(trash.item.itemHandle)

    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.tree.NWTree.create", lambda *a, **k: None)
        assert tree._getTrashNode() is None


@pytest.mark.core
def testCoreTree_CheckConsistency(caplog, mockGUI, fncPath, mockRnd):
    """Check the project tree's consistency."""
    project = NWProject()
    buildTestProject(project, fncPath)

    # By default, all is well
    caplog.clear()
    assert project.tree.checkConsistency("Recovered") == (0, 0)
    assert all(m.endswith("OK") for m in caplog.messages)

    # Create a new file with no meta data, and let the function handle it as orphaned
    xHandle = "0123456789abc"
    contentPath = project.storage.contentPath
    assert isinstance(contentPath, Path)
    assert contentPath == fncPath / "content"
    (contentPath / f"{xHandle}.nwd").write_text("### Stuff", encoding="utf-8")

    assert project.tree.checkConsistency("Recovered") == (1, 1)
    assert xHandle in project.tree
    itemX = project.tree[xHandle]
    assert isinstance(itemX, NWItem)

    # It should by default be added as a Novel file
    assert itemX.itemParent == C.hNovelRoot
    assert itemX.itemRoot == C.hNovelRoot
    assert itemX.itemClass == nwItemClass.NOVEL
    assert itemX.itemName == "[Recovered] 0123456789abc"

    # Set an unknown class in the orphaned item
    itemX.setClass(nwItemClass.OBJECT)
    itemX.setName("Stuff")
    itemX.setParent(C.hInvalid)
    project.storage.getDocument(xHandle).writeDocument("### Stuff")  # This adds meta data

    # Remove the item in the project, and re-run the consistency check
    project.tree.remove(xHandle)
    assert project.tree.checkConsistency("Recovered") == (1, 1)
    assert xHandle in project.tree
    itemX = project.tree[xHandle]
    assert isinstance(itemX, NWItem)

    # It should again be added as a Novel file
    assert itemX.itemParent == C.hNovelRoot
    assert itemX.itemRoot == C.hNovelRoot
    assert itemX.itemClass == nwItemClass.NOVEL
    assert itemX.itemName == "[Recovered] Stuff"

    # If the tree is empty, a new root folder is created
    project.tree.clear()
    assert project.tree.checkConsistency("Recovered") == (4, 4)
    assert len(project.tree) == 5
    nHandle = project.tree.findRoot(nwItemClass.NOVEL)
    assert project.tree[nHandle].itemName == "Recovered"  # type: ignore


@pytest.mark.core
def testCoreTree_MakeHandles(mockGUI):
    """Test generating item handles."""
    random.seed(42)
    project = NWProject()
    tree = NWTree(project)

    handles = ["1c803a3b1799d", "bdd6406671ad1", "3eb1346685257", "23b8c392456de"]

    random.seed(42)
    tHandle = tree._makeHandle()
    assert tHandle == handles[0]
    tree._items[handles[0]] = None  # type: ignore

    # Add the next in line to the project to force duplicate
    tree._items[handles[1]] = None  # type: ignore
    tHandle = tree._makeHandle()
    assert tHandle == handles[2]
    tree._items[handles[2]] = None  # type: ignore

    # Reset the seed to force collisions, which should still end up
    # returning the next handle in the sequence
    random.seed(42)
    tHandle = tree._makeHandle()
    assert tHandle == handles[3]


@pytest.mark.core
def testCoreTree_ToCFile(monkeypatch, fncPath, mockGUI, mockItems):
    """Test writing the ToC.txt file."""
    project = NWProject()
    tree = NWTree(project)
    tree.unpack(mockItems)

    def mockIsFile(fileName):
        """Return True for items that are files in novelWriter and
        should thus also be files in the project folder structure.
        """
        dItem = tree[fileName.name[:13]]
        assert dItem is not None
        return dItem.itemType == nwItemType.FILE

    monkeypatch.setattr("pathlib.Path.is_file", mockIsFile)
    project._storage._runtimePath = fncPath
    # (fncPath / "content").mkdir()

    # Block extraction of the path
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.storage.NWStorage.contentPath", lambda *a: None)
        assert tree.writeToCFile() is False

    # Block opening the file
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert tree.writeToCFile() is False

    # Allow writing
    assert tree.writeToCFile() is True
    assert (fncPath / nwFiles.TOC_TXT).read_text() == (
        "\n"
        "Table of Contents\n"
        "=================\n"
        "\n"
        "File Name                  Class      Layout    Document Label\n"
        "--------------------------------------------------------------\n"
        "content/000000000000c.nwd  NOVEL      DOCUMENT  Title Page\n"
        "content/000000000000e.nwd  NOVEL      DOCUMENT  New Chapter\n"
        "content/000000000000f.nwd  NOVEL      DOCUMENT  New Scene\n"
    )
