"""
novelWriter – NWTree Class Tester
=================================

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

import pytest
import random

from pathlib import Path

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
    theProject = NWProject(mockGUI)

    itemA = NWItem(theProject, "a000000000001")
    itemA._name = "Novel"
    itemA._parent = None
    itemA._type = nwItemType.ROOT
    itemA._class = nwItemClass.NOVEL
    itemA._expanded = True

    itemB = NWItem(theProject, "b000000000001")
    itemB._name = "Act One"
    itemB._parent = "a000000000001"
    itemB._type = nwItemType.FOLDER
    itemB._class = nwItemClass.NOVEL
    itemB._expanded = True

    itemC = NWItem(theProject, "c000000000001")
    itemC._name = "Chapter One"
    itemC._parent = "b000000000001"
    itemC._type = nwItemType.FILE
    itemC._class = nwItemClass.NOVEL
    itemC._layout = nwItemLayout.DOCUMENT
    itemC._charCount = 300
    itemC._wordCount = 50
    itemC._paraCount = 2

    itemD = NWItem(theProject, "c000000000002")
    itemD._name = "Scene One"
    itemD._parent = "b000000000001"
    itemD._type = nwItemType.FILE
    itemD._class = nwItemClass.NOVEL
    itemD._layout = nwItemLayout.DOCUMENT
    itemD._charCount = 3000
    itemD._wordCount = 500
    itemD._paraCount = 20

    itemE = NWItem(theProject, "a000000000002")
    itemE._name = "Outtakes"
    itemE._parent = None
    itemE._type = nwItemType.ROOT
    itemE._class = nwItemClass.ARCHIVE
    itemE._expanded = False

    itemF = NWItem(theProject, "a000000000003")
    itemF._name = "Trash"
    itemF._parent = None
    itemF._type = nwItemType.ROOT
    itemF._class = nwItemClass.TRASH
    itemF._expanded = False

    itemG = NWItem(theProject, "a000000000004")
    itemG._name = "Characters"
    itemG._parent = None
    itemG._type = nwItemType.ROOT
    itemG._class = nwItemClass.CHARACTER
    itemG._expanded = True

    itemH = NWItem(theProject, "b000000000002")
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
    theProject = NWProject(mockGUI)
    theTree = NWTree(theProject)

    # Check that tree is empty (calls NWTree.__bool__)
    assert bool(theTree) is False

    # Check for archive and trash folders
    assert theTree.trashRoot() is None

    aHandles = []
    for nwItem in mockItems:
        aHandles.append(nwItem.itemHandle)
        assert theTree.append(nwItem) is True
        assert theTree.updateItemData(nwItem.itemHandle) is True

    assert theTree._treeChanged is True

    # Check that tree is not empty (calls __bool__)
    assert bool(theTree) is True

    # Check the number of elements (calls __len__)
    assert len(theTree) == len(mockItems)

    # Check that we have the correct handles
    assert theTree.handles() == aHandles

    # Check by iterator (calls __iter__, __next__ and __getitem__)
    for theItem, theHandle in zip(theTree, aHandles):
        assert theItem.itemHandle == theHandle

    # Trash Folder
    # ============

    # Check that we have the correct archive and trash folders
    assert theTree.trashRoot() == "a000000000003"
    assert theTree.findRoot(nwItemClass.ARCHIVE) == "a000000000002"
    assert theTree.isTrash("a000000000003") is True

    # Check that we have the root classes
    assert theTree.rootClasses() == {
        nwItemClass.NOVEL, nwItemClass.CHARACTER, nwItemClass.ARCHIVE, nwItemClass.TRASH
    }

    # Check the isTrash function
    assert theTree.isTrash("0000000000000") is True  # Doesn't exist
    assert theTree.isTrash("a000000000003") is True  # This the trash folder

    theTree["a000000000003"].setClass(nwItemClass.NO_CLASS)  # type: ignore
    assert theTree.isTrash("a000000000003") is True  # This is still trash
    theTree["a000000000003"].setClass(nwItemClass.TRASH)  # type: ignore

    assert theTree.isTrash("b000000000002") is False  # This is not trash

    value = theTree["b000000000002"].itemParent  # type: ignore
    theTree["b000000000002"].setParent("a000000000003")  # type: ignore
    assert theTree.isTrash("b000000000002") is True  # This is in trash
    theTree["b000000000002"].setParent(value)  # type: ignore

    value = theTree["b000000000002"].itemRoot  # type: ignore
    theTree["b000000000002"].setRoot("a000000000003")  # type: ignore
    assert theTree.isTrash("b000000000002") is True  # This is in trash
    theTree["b000000000002"].setRoot(value)  # type: ignore

    # Try to add another trash folder
    itemT = NWItem(theProject, "1111111111111")
    itemT._name = "Trash"
    itemT._type = nwItemType.ROOT
    itemT._class = nwItemClass.TRASH
    itemT._expanded = False

    assert theTree.append(itemT) is False
    assert len(theTree) == len(mockItems)

    # Create or Add Items
    # ===================

    # Create a new item, but with invalid parent
    assert theTree.create("New File", "blabla", nwItemType.FILE, nwItemClass.NO_CLASS) is None

    # Create a new, valid item
    nHandle = theTree.create("New File", "b000000000001", nwItemType.FILE, nwItemClass.NO_CLASS)
    assert isHandle(nHandle)
    assert nHandle == "0000000000000"

    # The new item should be the last item in the tree
    theList = theTree.handles()
    assert theList[-1] == nHandle

    # Retrieve the item
    itemT = theTree[nHandle]
    assert isinstance(itemT, NWItem)
    assert len(theTree) == len(mockItems) + 1

    # We should not be allowed to add the item again
    assert theTree.append(itemT) is False
    assert len(theTree) == len(mockItems) + 1

    # Create an invalid item to add, which will be rejected
    itemU = NWItem.duplicate(itemT, "blabla")
    assert theTree.append(itemU) is False
    assert len(theTree) == len(mockItems) + 1

    # Duplicate Items
    # ===============

    # Duplicate a non-existing item
    assert theTree.duplicate("blabla") is None

    # Duplicate the new item
    itemV = theTree.duplicate(nHandle)
    assert isinstance(itemV, NWItem)
    assert len(theTree) == len(mockItems) + 2

    dHandle = itemV.itemHandle
    assert dHandle == "0000000000001"

    # Delete Items
    # ============

    # Delete a non-existing item
    del theTree["stuff"]
    assert len(theTree) == len(mockItems) + 2

    # Delete the last items
    del theTree[nHandle]
    del theTree[dHandle]
    assert len(theTree) == len(mockItems)
    assert nHandle not in theTree

    # Delete the Novel, Archive and Trash folders
    del theTree["a000000000001"]
    assert len(theTree) == len(mockItems) - 1
    assert "a000000000001" not in theTree

    del theTree["a000000000002"]
    assert len(theTree) == len(mockItems) - 2
    assert "a000000000002" not in theTree

    del theTree["a000000000003"]
    assert len(theTree) == len(mockItems) - 3
    assert "a000000000003" not in theTree
    assert theTree.trashRoot() is None

# END Test testCoreTree_BuildTree


@pytest.mark.core
def testCoreTree_PackUnpack(mockGUI, mockItems):
    """Test packing and unpacking data."""
    theProject = NWProject(mockGUI)
    theTree = NWTree(theProject)

    aHandles = []
    for nwItem in mockItems:
        aHandles.append(nwItem.itemHandle)
        theTree.append(nwItem)
        theTree.updateItemData(nwItem.itemHandle)

    assert len(theTree) == len(mockItems)

    # Pack
    tree = theTree.pack()
    for i, nwItem in enumerate(mockItems):
        assert tree[i]["itemAttr"]["handle"] == nwItem.itemHandle

    # Unpack
    theTree.clear()
    assert len(theTree) == 0
    assert theTree.handles() == []
    theTree.unpack(tree)
    assert theTree.handles() == aHandles

# END Test testCoreTree_PackUnpack


@pytest.mark.core
def testCoreTree_Methods(mockGUI, mockItems):
    """Test various class methods."""
    theProject = NWProject(mockGUI)
    theTree = NWTree(theProject)

    for nwItem in mockItems:
        theTree.append(nwItem)
        theTree.updateItemData(nwItem.itemHandle)

    assert len(theTree) == len(mockItems)

    # Update item data, nonsense handle
    assert theTree.updateItemData("stuff") is False

    # Update item data, invalid item parent
    corrParent = theTree["b000000000001"].itemParent  # type: ignore
    theTree["b000000000001"].setParent("0000000000000")  # type: ignore
    assert theTree.updateItemData("b000000000001") is False

    # Update item data, valid item parent
    theTree["b000000000001"].setParent(corrParent)  # type: ignore
    assert theTree.updateItemData("b000000000001") is True

    # Update item data, root is unreachable
    maxDepth = theTree.MAX_DEPTH
    theTree.MAX_DEPTH = 0  # type: ignore
    with pytest.raises(RecursionError):
        theTree.updateItemData("b000000000001")
    theTree.MAX_DEPTH = maxDepth

    # Check type
    assert theTree.checkType("blabla", nwItemType.FILE) is False
    assert theTree.checkType("b000000000001", nwItemType.FILE) is False
    assert theTree.checkType("c000000000001", nwItemType.FILE) is True

    # Root item lookup
    assert theTree.findRoot(nwItemClass.WORLD) is None
    assert theTree.findRoot(nwItemClass.NOVEL) == "a000000000001"
    assert theTree.findRoot(nwItemClass.CHARACTER) == "a000000000004"

    # Iter roots
    roots = list(theTree.iterRoots(None))
    assert roots[0][0] == "a000000000001"
    assert roots[1][0] == "a000000000002"
    assert roots[2][0] == "a000000000003"
    assert roots[3][0] == "a000000000004"

    # Add a fake item to root and check that it can handle it
    theTree._treeRoots["0000000000000"] = NWItem(theProject, "0000000000000")
    assert theTree.findRoot(nwItemClass.WORLD) is None
    del theTree._treeRoots["0000000000000"]

    # Get item path
    assert theTree.getItemPath("stuff") == []
    assert theTree.getItemPath("c000000000001") == [
        "c000000000001", "b000000000001", "a000000000001"
    ]

    # Cause recursion error
    maxDepth = theTree.MAX_DEPTH
    theTree.MAX_DEPTH = 0  # type: ignore
    with pytest.raises(RecursionError):
        theTree.getItemPath("c000000000001")
    theTree.MAX_DEPTH = maxDepth

    # Break the folder parent handle
    theTree["b000000000001"]._parent = "stuff"  # type: ignore
    assert theTree.getItemPath("c000000000001") == [
        "c000000000001", "b000000000001"
    ]

    theTree["b000000000001"]._parent = "a000000000001"  # type: ignore
    assert theTree.getItemPath("c000000000001") == [
        "c000000000001", "b000000000001", "a000000000001"
    ]

# END Test testCoreTree_Methods


@pytest.mark.core
def testCoreTree_MakeHandles(mockGUI):
    """Test generating item handles."""
    random.seed(42)
    theProject = NWProject(mockGUI)
    theTree = NWTree(theProject)

    handles = ["1c803a3b1799d", "bdd6406671ad1", "3eb1346685257", "23b8c392456de"]

    random.seed(42)
    tHandle = theTree._makeHandle()
    assert tHandle == handles[0]
    theTree._projTree[handles[0]] = None  # type: ignore

    # Add the next in line to the project to force duplicate
    theTree._projTree[handles[1]] = None  # type: ignore
    tHandle = theTree._makeHandle()
    assert tHandle == handles[2]
    theTree._projTree[handles[2]] = None  # type: ignore

    # Reset the seed to force collissions, which should still end up
    # returning the next handle in the sequence
    random.seed(42)
    tHandle = theTree._makeHandle()
    assert tHandle == handles[3]

# END Test testCoreTree_MakeHandles


@pytest.mark.core
def testCoreTree_Stats(mockGUI, mockItems):
    """Test project stats methods."""
    theProject = NWProject(mockGUI)
    theTree = NWTree(theProject)

    for nwItem in mockItems:
        theTree.append(nwItem)

    assert len(theTree) == len(mockItems)
    theTree._treeOrder.append("stuff")

    # Count Words
    novelWords, noteWords = theTree.sumWords()
    assert novelWords == 550
    assert noteWords == 400

# END Test testCoreTree_Stats


@pytest.mark.core
def testCoreTree_Reorder(caplog, mockGUI, mockItems):
    """Test changing tree order."""
    theProject = NWProject(mockGUI)
    theTree = NWTree(theProject)

    aHandle = []
    for nwItem in mockItems:
        aHandle.append(nwItem.itemHandle)
        theTree.append(nwItem)

    assert len(theTree) == len(mockItems)

    bHandle = aHandle.copy()
    bHandle[2], bHandle[3] = bHandle[3], bHandle[2]
    assert aHandle != bHandle

    assert theTree.handles() == aHandle
    theTree.setOrder(bHandle)
    assert theTree.handles() == bHandle

    caplog.clear()
    theTree.setOrder(bHandle + ["stuff"])
    assert theTree.handles() == bHandle
    assert "Handle 'stuff' in new tree order is not in old order" in caplog.text

    caplog.clear()
    theTree._treeOrder.append("stuff")
    theTree.setOrder(bHandle)
    assert theTree.handles() == bHandle
    assert "Handle 'stuff' in old tree order is not in new order" in caplog.text

# END Test testCoreTree_Reorder


@pytest.mark.core
def testCoreTree_ToCFile(monkeypatch, fncPath, mockGUI, mockItems):
    """Test writing the ToC.txt file."""
    theProject = NWProject(mockGUI)
    theTree = NWTree(theProject)

    for nwItem in mockItems:
        theTree.append(nwItem)
        theTree.updateItemData(nwItem.itemHandle)

    assert len(theTree) == len(mockItems)
    theTree._treeOrder.append("stuff")

    def mockIsFile(fileName):
        """Return True for items that are files in novelWriter and
        should thus also be files in the project folder structure.
        """
        dItem = theTree[fileName.name[:13]]
        assert dItem is not None
        return dItem.itemType == nwItemType.FILE

    monkeypatch.setattr("pathlib.Path.is_file", mockIsFile)
    theProject._storage._runtimePath = fncPath
    (fncPath / "content").mkdir()

    # Block extraction of the path
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.storage.NWStorage.contentPath", lambda *a: None)
        assert theTree.writeToCFile() is False

    # Block opening the file
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert theTree.writeToCFile() is False

    # Allow writing
    assert theTree.writeToCFile() is True

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
