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

import pytest
import random

from pathlib import Path

from tools import C, buildTestProject
from mocked import causeOSError

from novelwriter.enum import nwItemClass, nwItemType, nwItemLayout
from novelwriter.common import isHandle
from novelwriter.constants import nwFiles
from novelwriter.core.item import NWItem
from novelwriter.core.tree import NWTree
from novelwriter.core.project import NWProject


@pytest.fixture(scope="function")
def mockItems(mockGUI, mockRnd):
    """Create a list of mock items."""
    project = NWProject()

    itemA = NWItem(project, "a000000000001")
    itemA._name = "Novel"
    itemA._parent = None
    itemA._type = nwItemType.ROOT
    itemA._class = nwItemClass.NOVEL
    itemA._expanded = True

    itemB = NWItem(project, "b000000000001")
    itemB._name = "Act One"
    itemB._parent = "a000000000001"
    itemB._type = nwItemType.FOLDER
    itemB._class = nwItemClass.NOVEL
    itemB._expanded = True

    itemC = NWItem(project, "c000000000001")
    itemC._name = "Chapter One"
    itemC._parent = "b000000000001"
    itemC._type = nwItemType.FILE
    itemC._class = nwItemClass.NOVEL
    itemC._layout = nwItemLayout.DOCUMENT
    itemC._charCount = 300
    itemC._wordCount = 50
    itemC._paraCount = 2

    itemD = NWItem(project, "c000000000002")
    itemD._name = "Scene One"
    itemD._parent = "b000000000001"
    itemD._type = nwItemType.FILE
    itemD._class = nwItemClass.NOVEL
    itemD._layout = nwItemLayout.DOCUMENT
    itemD._charCount = 3000
    itemD._wordCount = 500
    itemD._paraCount = 20

    itemE = NWItem(project, "a000000000002")
    itemE._name = "Outtakes"
    itemE._parent = None
    itemE._type = nwItemType.ROOT
    itemE._class = nwItemClass.ARCHIVE
    itemE._expanded = False

    itemF = NWItem(project, "a000000000003")
    itemF._name = "Trash"
    itemF._parent = None
    itemF._type = nwItemType.ROOT
    itemF._class = nwItemClass.TRASH
    itemF._expanded = False

    itemG = NWItem(project, "a000000000004")
    itemG._name = "Characters"
    itemG._parent = None
    itemG._type = nwItemType.ROOT
    itemG._class = nwItemClass.CHARACTER
    itemG._expanded = True

    itemH = NWItem(project, "b000000000002")
    itemH._name = "Jane Doe"
    itemH._parent = "a000000000004"
    itemH._type = nwItemType.FILE
    itemH._class = nwItemClass.CHARACTER
    itemH._layout = nwItemLayout.NOTE
    itemH._charCount = 2000
    itemH._wordCount = 400
    itemH._paraCount = 16

    return [itemA, itemB, itemC, itemD, itemE, itemF, itemG, itemH]


@pytest.mark.core
def testCoreTree_BuildTree(mockGUI, mockItems):
    """Test building a project tree from a list of items."""
    project = NWProject()
    tree = NWTree(project)

    # Check that tree is empty (calls NWTree.__bool__)
    assert bool(tree) is False

    # Check for archive and trash folders
    assert tree.trashRoot is None

    aHandles = []
    for nwItem in mockItems:
        aHandles.append(nwItem.itemHandle)
        assert tree.append(nwItem) is True
        assert tree.updateItemData(nwItem.itemHandle) is True

    assert tree._changed is True

    # Check that tree is not empty (calls __bool__)
    assert bool(tree) is True

    # Check the number of elements (calls __len__)
    assert len(tree) == len(mockItems)

    # Check that we have the correct handles
    assert tree.handles() == aHandles

    # Check by iterator (calls __iter__, __next__ and __getitem__)
    for item, handle in zip(tree, aHandles):
        assert item.itemHandle == handle

    # Trash Folder
    # ============

    # Check that we have the correct archive and trash folders
    assert tree.trashRoot == "a000000000003"
    assert tree.findRoot(nwItemClass.ARCHIVE) == "a000000000002"
    assert tree.isTrash("a000000000003") is True

    # Check that we have the root classes
    assert tree.rootClasses() == {
        nwItemClass.NOVEL, nwItemClass.CHARACTER, nwItemClass.ARCHIVE, nwItemClass.TRASH
    }

    # Check the isTrash function
    assert tree.isTrash("0000000000000") is True  # Doesn't exist
    assert tree.isTrash("a000000000003") is True  # This the trash folder

    tree["a000000000003"].setClass(nwItemClass.NO_CLASS)  # type: ignore
    assert tree.isTrash("a000000000003") is True  # This is still trash
    tree["a000000000003"].setClass(nwItemClass.TRASH)  # type: ignore

    assert tree.isTrash("b000000000002") is False  # This is not trash

    value = tree["b000000000002"].itemParent  # type: ignore
    tree["b000000000002"].setParent("a000000000003")  # type: ignore
    assert tree.isTrash("b000000000002") is True  # This is in trash
    tree["b000000000002"].setParent(value)  # type: ignore

    value = tree["b000000000002"].itemRoot  # type: ignore
    tree["b000000000002"].setRoot("a000000000003")  # type: ignore
    assert tree.isTrash("b000000000002") is True  # This is in trash
    tree["b000000000002"].setRoot(value)  # type: ignore

    # Try to add another trash folder
    itemT = NWItem(project, "1111111111111")
    itemT._name = "Trash"
    itemT._type = nwItemType.ROOT
    itemT._class = nwItemClass.TRASH
    itemT._expanded = False

    assert tree.append(itemT) is False
    assert len(tree) == len(mockItems)

    # Create or Add Items
    # ===================

    # Create a new item, but with invalid parent
    assert tree.create("New File", "blabla", nwItemType.FILE, nwItemClass.NO_CLASS) is None

    # Create a new, valid item
    nHandle = tree.create("New File", "b000000000001", nwItemType.FILE, nwItemClass.NO_CLASS)
    assert isHandle(nHandle)
    assert nHandle == "0000000000000"

    # The new item should be the last item in the tree
    handles = tree.handles()
    assert handles[-1] == nHandle

    # Retrieve the item
    itemT = tree[nHandle]
    assert isinstance(itemT, NWItem)
    assert len(tree) == len(mockItems) + 1

    # We should not be allowed to add the item again
    assert tree.append(itemT) is False
    assert len(tree) == len(mockItems) + 1

    # Create an invalid item to add, which will be rejected
    itemU = NWItem.duplicate(itemT, "blabla")
    assert tree.append(itemU) is False
    assert len(tree) == len(mockItems) + 1

    # Create a new root, but with a parent set anyway (the parent should be ignored)
    zHandle = tree.create("Custom", "a000000000001", nwItemType.ROOT, nwItemClass.CUSTOM)
    assert isinstance(zHandle, str)
    itemZ = tree[zHandle]
    assert isinstance(itemZ, NWItem)
    assert itemZ.itemParent is None
    del tree[zHandle]

    # Duplicate Items
    # ===============

    # Duplicate a non-existing item
    assert tree.duplicate("blabla") is None

    # Duplicate the new item
    itemV = tree.duplicate(nHandle)
    assert isinstance(itemV, NWItem)
    assert len(tree) == len(mockItems) + 2

    dHandle = itemV.itemHandle
    assert dHandle == "0000000000002"

    # Delete Items
    # ============

    # Delete a non-existing item
    del tree["stuff"]
    assert len(tree) == len(mockItems) + 2

    # Delete the last items
    del tree[nHandle]
    del tree[dHandle]
    assert len(tree) == len(mockItems)
    assert nHandle not in tree

    # Delete the Novel, Archive and Trash folders
    del tree["a000000000001"]
    assert len(tree) == len(mockItems) - 1
    assert "a000000000001" not in tree

    del tree["a000000000002"]
    assert len(tree) == len(mockItems) - 2
    assert "a000000000002" not in tree

    del tree["a000000000003"]
    assert len(tree) == len(mockItems) - 3
    assert "a000000000003" not in tree
    assert tree.trashRoot is None

# END Test testCoreTree_BuildTree


@pytest.mark.core
def testCoreTree_PackUnpack(mockGUI, mockItems):
    """Test packing and unpacking data."""
    project = NWProject()
    tree = NWTree(project)

    aHandles = []
    for nwItem in mockItems:
        aHandles.append(nwItem.itemHandle)
        tree.append(nwItem)
        tree.updateItemData(nwItem.itemHandle)

    assert len(tree) == len(mockItems)

    # Pack
    packed = tree.pack()
    for i, nwItem in enumerate(mockItems):
        assert packed[i]["itemAttr"]["handle"] == nwItem.itemHandle

    # Unpack
    tree.clear()
    assert len(tree) == 0
    assert tree.handles() == []
    tree.unpack(packed)
    assert tree.handles() == aHandles

# END Test testCoreTree_PackUnpack


@pytest.mark.core
def testCoreTree_CheckConsistency(caplog: pytest.LogCaptureFixture, mockGUI, fncPath, mockRnd):
    """Check the project consistency."""
    project = NWProject()
    buildTestProject(project, fncPath)

    # By default, all is well
    caplog.clear()
    assert project.tree.checkConsistency("Recovered") == (0, 0)
    assert all(m.endswith("OK") for m in caplog.messages)

    # Give the scene file an unknown parent
    caplog.clear()
    project.tree[C.hSceneDoc].setParent(C.hInvalid)  # type: ignore
    assert project.tree.checkConsistency("Recovered") == (1, 1)
    assert f"'{C.hSceneDoc}' ... ERROR" in caplog.text

    # The scene file should have been added back to its home
    itemS = project.tree[C.hSceneDoc]
    assert isinstance(itemS, NWItem)
    assert itemS.itemParent == C.hChapterDir

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
    del project.tree[xHandle]
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

# END Test testCoreTree_CheckConsistency


@pytest.mark.core
def testCoreTree_Methods(monkeypatch, mockGUI, mockItems):
    """Test various class methods."""
    project = NWProject()
    tree = NWTree(project)

    for nwItem in mockItems:
        tree.append(nwItem)
        tree.updateItemData(nwItem.itemHandle)

    assert len(tree) == len(mockItems)

    # Update item data, nonsense handle
    assert tree.updateItemData("stuff") is False

    # Update item data, invalid item parent
    corrParent = tree["b000000000001"].itemParent  # type: ignore
    tree["b000000000001"].setParent("0000000000000")  # type: ignore
    assert tree.updateItemData("b000000000001") is False

    # Update item data, valid item parent
    tree["b000000000001"].setParent(corrParent)  # type: ignore
    assert tree.updateItemData("b000000000001") is True

    # Update item data, root is unreachable
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.tree.MAX_DEPTH", 0)
        with pytest.raises(RecursionError):
            tree.updateItemData("b000000000001")

    # Check type
    assert tree.checkType("blabla", nwItemType.FILE) is False
    assert tree.checkType("b000000000001", nwItemType.FILE) is False
    assert tree.checkType("c000000000001", nwItemType.FILE) is True

    # Root item lookup
    assert tree.findRoot(nwItemClass.WORLD) is None
    assert tree.findRoot(nwItemClass.NOVEL) == "a000000000001"
    assert tree.findRoot(nwItemClass.CHARACTER) == "a000000000004"

    # Iter roots
    roots = list(tree.iterRoots(None))
    assert roots[0][0] == "a000000000001"
    assert roots[1][0] == "a000000000002"
    assert roots[2][0] == "a000000000003"
    assert roots[3][0] == "a000000000004"

    # Add a fake item to root and check that it can handle it
    tree._roots["0000000000000"] = NWItem(project, "0000000000000")
    assert tree.findRoot(nwItemClass.WORLD) is None
    del tree._roots["0000000000000"]

    # Get item path
    assert tree.getItemPath("stuff") == []
    assert tree.getItemPath("c000000000001") == [
        "c000000000001", "b000000000001", "a000000000001"
    ]
    assert tree.getItemPath("c000000000001", asName=True) == [
        "Chapter One", "Act One", "Novel"
    ]

    # Cause recursion error
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.tree.MAX_DEPTH", 0)
        with pytest.raises(RecursionError):
            tree.getItemPath("c000000000001")

    # Break the folder parent handle
    tree["b000000000001"]._parent = "stuff"  # type: ignore
    assert tree.getItemPath("c000000000001") == [
        "c000000000001", "b000000000001"
    ]

    tree["b000000000001"]._parent = "a000000000001"  # type: ignore
    assert tree.getItemPath("c000000000001") == [
        "c000000000001", "b000000000001", "a000000000001"
    ]

# END Test testCoreTree_Methods


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
    tree._tree[handles[0]] = None  # type: ignore

    # Add the next in line to the project to force duplicate
    tree._tree[handles[1]] = None  # type: ignore
    tHandle = tree._makeHandle()
    assert tHandle == handles[2]
    tree._tree[handles[2]] = None  # type: ignore

    # Reset the seed to force collissions, which should still end up
    # returning the next handle in the sequence
    random.seed(42)
    tHandle = tree._makeHandle()
    assert tHandle == handles[3]

# END Test testCoreTree_MakeHandles


@pytest.mark.core
def testCoreTree_Stats(mockGUI, mockItems):
    """Test project stats methods."""
    project = NWProject()
    tree = NWTree(project)

    for nwItem in mockItems:
        tree.append(nwItem)

    assert len(tree) == len(mockItems)
    tree._order.append("stuff")

    # Count Words
    novelWords, noteWords = tree.sumWords()
    assert novelWords == 550
    assert noteWords == 400

# END Test testCoreTree_Stats


@pytest.mark.core
def testCoreTree_Reorder(caplog, mockGUI, mockItems):
    """Test changing tree order."""
    project = NWProject()
    tree = NWTree(project)

    aHandle = []
    for nwItem in mockItems:
        aHandle.append(nwItem.itemHandle)
        tree.append(nwItem)

    assert len(tree) == len(mockItems)

    bHandle = aHandle.copy()
    bHandle[2], bHandle[3] = bHandle[3], bHandle[2]
    assert aHandle != bHandle

    assert tree.handles() == aHandle
    tree.setOrder(bHandle)
    assert tree.handles() == bHandle

    caplog.clear()
    tree.setOrder(bHandle + ["stuff"])
    assert tree.handles() == bHandle
    assert "Handle 'stuff' in new tree order is not in old order" in caplog.text

    caplog.clear()
    tree._order.append("stuff")
    tree.setOrder(bHandle)
    assert tree.handles() == bHandle
    assert "Handle 'stuff' in old tree order is not in new order" in caplog.text

# END Test testCoreTree_Reorder


@pytest.mark.core
def testCoreTree_ToCFile(monkeypatch, fncPath, mockGUI, mockItems):
    """Test writing the ToC.txt file."""
    project = NWProject()
    tree = NWTree(project)

    for nwItem in mockItems:
        tree.append(nwItem)
        tree.updateItemData(nwItem.itemHandle)

    assert len(tree) == len(mockItems)
    tree._order.append("stuff")

    def mockIsFile(fileName):
        """Return True for items that are files in novelWriter and
        should thus also be files in the project folder structure.
        """
        dItem = tree[fileName.name[:13]]
        assert dItem is not None
        return dItem.itemType == nwItemType.FILE

    monkeypatch.setattr("pathlib.Path.is_file", mockIsFile)
    project._storage._runtimePath = fncPath
    (fncPath / "content").mkdir()

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

    pathA = str(Path("content") / "c000000000001.nwd")
    pathB = str(Path("content") / "c000000000002.nwd")
    pathC = str(Path("content") / "b000000000002.nwd")

    assert (fncPath / nwFiles.TOC_TXT).read_text() == (
        "\n"
        "Table of Contents\n"
        "=================\n"
        "\n"
        "File Name                  Class      Layout    Document Label\n"
        "--------------------------------------------------------------\n"
        f"{pathA}  NOVEL      DOCUMENT  Chapter One\n"
        f"{pathB}  NOVEL      DOCUMENT  Scene One\n"
        f"{pathC}  CHARACTER  NOTE      Jane Doe\n"
    )

# END Test testCoreTree_ToCFile
