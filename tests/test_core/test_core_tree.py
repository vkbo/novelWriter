"""
novelWriter – NWTree Class Tester
=================================

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

from lxml import etree
from hashlib import sha256

from tools import readFile

from novelwriter.core.project import NWProject, NWItem, NWTree
from novelwriter.enum import nwItemClass, nwItemType, nwItemLayout
from novelwriter.constants import nwFiles


@pytest.fixture(scope="function")
def mockItems(mockGUI):
    """Create a list of mock items.
    """
    theProject = NWProject(mockGUI)

    itemA = NWItem(theProject)
    itemA._name = "Novel"
    itemA._type = nwItemType.ROOT
    itemA._class = nwItemClass.NOVEL
    itemA._expanded = True

    itemB = NWItem(theProject)
    itemB._name = "Act One"
    itemB._type = nwItemType.FOLDER
    itemB._class = nwItemClass.NOVEL
    itemB._expanded = True

    itemC = NWItem(theProject)
    itemC._name = "Chapter One"
    itemC._type = nwItemType.FILE
    itemC._class = nwItemClass.NOVEL
    itemC._layout = nwItemLayout.DOCUMENT
    itemC._charCount = 300
    itemC._wordCount = 50
    itemC._paraCount = 2

    itemD = NWItem(theProject)
    itemD._name = "Scene One"
    itemD._type = nwItemType.FILE
    itemD._class = nwItemClass.NOVEL
    itemD._layout = nwItemLayout.DOCUMENT
    itemD._charCount = 3000
    itemD._wordCount = 500
    itemD._paraCount = 20

    itemE = NWItem(theProject)
    itemE._name = "Outtakes"
    itemE._type = nwItemType.ROOT
    itemE._class = nwItemClass.ARCHIVE
    itemE._expanded = False

    itemF = NWItem(theProject)
    itemF._name = "Trash"
    itemF._type = nwItemType.TRASH
    itemF._class = nwItemClass.TRASH
    itemF._expanded = False

    itemG = NWItem(theProject)
    itemG._name = "Characters"
    itemG._type = nwItemType.ROOT
    itemG._class = nwItemClass.CHARACTER
    itemG._expanded = True

    itemH = NWItem(theProject)
    itemH._name = "Jane Doe"
    itemH._type = nwItemType.FILE
    itemH._class = nwItemClass.CHARACTER
    itemH._layout = nwItemLayout.NOTE
    itemH._charCount = 2000
    itemH._wordCount = 400
    itemH._paraCount = 16

    theItems = [
        ("a000000000001", None,            itemA),
        ("b000000000001", "a000000000001", itemB),
        ("c000000000001", "b000000000001", itemC),
        ("c000000000002", "b000000000001", itemD),
        ("a000000000002", None,            itemE),
        ("a000000000003", None,            itemF),
        ("a000000000004", None,            itemG),
        ("b000000000002", "a000000000002", itemH),
    ]

    return theItems


@pytest.mark.core
def testCoreTree_BuildTree(mockGUI, mockItems):
    """Test building a project tree from a list of items.
    """
    theProject = NWProject(mockGUI)
    theTree = NWTree(theProject)

    theTree.setSeed(42)
    assert theTree._handleSeed == 42

    # Check that tree is empty (calls NWTree.__bool__)
    assert not theTree

    # Check for archive and trash folders
    assert theTree.trashRoot() is None
    assert theTree.archiveRoot() is None
    assert not theTree.isTrashRoot("a000000000003")

    aHandles = []
    for tHandle, pHandle, nwItem in mockItems:
        aHandles.append(tHandle)
        assert theTree.append(tHandle, pHandle, nwItem)

    assert theTree._treeChanged

    # Check that tree is not empty (calls __bool__)
    assert theTree

    # Check the number of elements (calls __len__)
    assert len(theTree) == len(mockItems)

    # Check that we have the correct handles
    assert theTree.handles() == aHandles

    # Check by iterator (calls __iter__, __next__ and __getitem__)
    for theItem, theHandle in zip(theTree, aHandles):
        assert theItem.itemHandle == theHandle

    # Check that we have the correct archive and trash folders
    assert theTree.trashRoot() == "a000000000003"
    assert theTree.archiveRoot() == "a000000000002"
    assert theTree.isTrashRoot("a000000000003")

    # Try to add another trash folder
    itemT = NWItem(theProject)
    itemT._name = "Trash"
    itemT._type = nwItemType.TRASH
    itemT._class = nwItemClass.TRASH
    itemT._expanded = False

    assert not theTree.append("1234567890abc", None, itemT)
    assert len(theTree) == len(mockItems)

    # Generate handle automatically
    itemT = NWItem(theProject)
    itemT._name = "New File"
    itemT._type = nwItemType.FILE
    itemT._class = nwItemClass.NOVEL
    itemT._layout = nwItemLayout.DOCUMENT

    assert theTree.append(None, None, itemT)
    assert len(theTree) == len(mockItems) + 1

    theList = theTree.handles()
    assert theList[-1] == "73475cb40a568"

    # Try to add existing handle
    assert not theTree.append("73475cb40a568", None, itemT)
    assert len(theTree) == len(mockItems) + 1

    # Delete a non-existing item
    del theTree["stuff"]
    assert len(theTree) == len(mockItems) + 1

    # Delete the last item
    del theTree["73475cb40a568"]
    assert len(theTree) == len(mockItems)
    assert "73475cb40a568" not in theTree

    # Delete the Novel, Archive and Trash folders
    del theTree["a000000000001"]
    assert len(theTree) == len(mockItems) - 1
    assert "a000000000001" not in theTree

    del theTree["a000000000002"]
    assert len(theTree) == len(mockItems) - 2
    assert "a000000000002" not in theTree
    assert theTree.archiveRoot() is None

    del theTree["a000000000003"]
    assert len(theTree) == len(mockItems) - 3
    assert "a000000000003" not in theTree
    assert theTree.trashRoot() is None

# END Test testCoreTree_BuildTree


@pytest.mark.core
def testCoreTree_Methods(mockGUI, mockItems):
    """Test various class methods.
    """
    theProject = NWProject(mockGUI)
    theTree = NWTree(theProject)

    for tHandle, pHandle, nwItem in mockItems:
        theTree.append(tHandle, pHandle, nwItem)

    assert len(theTree) == len(mockItems)

    # Chech type
    assert theTree.checkType("blabla", nwItemType.FILE) is False
    assert theTree.checkType("b000000000001", nwItemType.FILE) is False
    assert theTree.checkType("c000000000001", nwItemType.FILE) is True

    # Root item lookup
    theTree._treeRoots.append("stuff")
    assert theTree.findRoot(nwItemClass.WORLD) is None
    assert theTree.findRoot(nwItemClass.NOVEL) == "a000000000001"
    assert theTree.findRoot(nwItemClass.CHARACTER) == "a000000000004"

    # Check for root uniqueness
    assert theTree.checkRootUnique(nwItemClass.CUSTOM)
    assert theTree.checkRootUnique(nwItemClass.WORLD)
    assert not theTree.checkRootUnique(nwItemClass.NOVEL)
    assert not theTree.checkRootUnique(nwItemClass.CHARACTER)

    # Find root item of child item
    assert theTree.getRootItem("b000000000001").itemHandle == "a000000000001"
    assert theTree.getRootItem("c000000000001").itemHandle == "a000000000001"
    assert theTree.getRootItem("c000000000002").itemHandle == "a000000000001"
    assert theTree.getRootItem("stuff") is None

    # Get item path
    assert theTree.getItemPath("stuff") == []
    assert theTree.getItemPath("c000000000001") == [
        "c000000000001", "b000000000001", "a000000000001"
    ]

    # Break the folder parent handle
    theTree["b000000000001"]._parent = "stuff"
    assert theTree.getItemPath("c000000000001") == [
        "c000000000001", "b000000000001"
    ]

    theTree["b000000000001"]._parent = "a000000000001"
    assert theTree.getItemPath("c000000000001") == [
        "c000000000001", "b000000000001", "a000000000001"
    ]

    # Change file layout
    assert theTree.setFileItemLayout("stuff", nwItemLayout.DOCUMENT) is False
    assert theTree.setFileItemLayout("b000000000001", nwItemLayout.DOCUMENT) is False
    assert theTree.setFileItemLayout("c000000000001", "stuff") is False
    assert theTree.setFileItemLayout("c000000000001", nwItemLayout.NOTE) is True
    assert theTree["c000000000001"].itemLayout == nwItemLayout.NOTE

# END Test testCoreTree_Methods


@pytest.mark.core
def testCoreTree_MakeHandles(monkeypatch, mockGUI):
    """Test generating item handles.
    """
    theProject = NWProject(mockGUI)
    theTree = NWTree(theProject)

    theTree.setSeed(42)

    tHandle = theTree._makeHandle()
    assert tHandle == "73475cb40a568"

    # Add the next in line to the project to force duplicate
    theTree._projTree["44cb730c42048"] = None
    tHandle = theTree._makeHandle()
    assert tHandle == "71ee45a3c0db9"

    # Fix the time() function and force a handle collission
    theTree.setSeed(None)
    theTree._handleCount = 0
    monkeypatch.setattr("novelwriter.core.tree.time", lambda: 123.4)

    tHandle = theTree._makeHandle()
    theTree._projTree[tHandle] = None
    newSeed = "123.4_0_"
    assert tHandle == sha256(newSeed.encode()).hexdigest()[0:13]

    tHandle = theTree._makeHandle()
    theTree._projTree[tHandle] = None
    newSeed = "123.4_1_"
    assert tHandle == sha256(newSeed.encode()).hexdigest()[0:13]

    # Reset the count and the handle for 0 and 1 should be duplicates
    # which forces the function to add the '!'
    theTree._handleCount = 0
    tHandle = theTree._makeHandle()
    theTree._projTree[tHandle] = None
    newSeed = "123.4_1_!"
    assert tHandle == sha256(newSeed.encode()).hexdigest()[0:13]

# END Test testCoreTree_MakeHandles


@pytest.mark.core
def testCoreTree_Stats(mockGUI, mockItems):
    """Test project stats methods.
    """
    theProject = NWProject(mockGUI)
    theTree = NWTree(theProject)

    for tHandle, pHandle, nwItem in mockItems:
        theTree.append(tHandle, pHandle, nwItem)

    assert len(theTree) == len(mockItems)
    theTree._treeOrder.append("stuff")

    # Count Words
    novelWords, noteWords = theTree.sumWords()
    assert novelWords == 550
    assert noteWords == 400

    # Count types
    nRoot, nFolder, nFile = theTree.countTypes()
    assert nRoot == 3
    assert nFolder == 1
    assert nFile == 3

# END Test testCoreTree_Stats


@pytest.mark.core
def testCoreTree_Reorder(mockGUI, mockItems):
    """Test changing tree order.
    """
    theProject = NWProject(mockGUI)
    theTree = NWTree(theProject)

    aHandle = []
    for tHandle, pHandle, nwItem in mockItems:
        aHandle.append(tHandle)
        theTree.append(tHandle, pHandle, nwItem)

    assert len(theTree) == len(mockItems)

    bHandle = aHandle.copy()
    bHandle[2], bHandle[3] = bHandle[3], bHandle[2]
    assert aHandle != bHandle

    assert theTree.handles() == aHandle
    theTree.setOrder(bHandle)
    assert theTree.handles() == bHandle

    theTree.setOrder(bHandle + ["stuff"])
    assert theTree.handles() == bHandle

    theTree._treeOrder.append("stuff")
    theTree.setOrder(bHandle)
    assert theTree.handles() == bHandle

# END Test testCoreTree_Reorder


@pytest.mark.core
def testCoreTree_XMLPackUnpack(mockGUI, mockItems):
    """Test packing and unpacking the tree to and from XML.
    """
    theProject = NWProject(mockGUI)
    theTree = NWTree(theProject)

    for tHandle, pHandle, nwItem in mockItems:
        theTree.append(tHandle, pHandle, nwItem)

    assert len(theTree) == len(mockItems)

    nwXML = etree.Element("novelWriterXML")
    theTree.packXML(nwXML)
    assert etree.tostring(nwXML, pretty_print=False, encoding="utf-8") == (
        b'<novelWriterXML>'
        b'<content count="8">'
        b'<item handle="a000000000001" parent="None" order="0" type="ROOT" class="NOVEL"><meta '
        b'expanded="True"/><name status="None" import="None">Novel</name></item>'
        b'<item handle="b000000000001" parent="a000000000001" order="0" type="FOLDER" '
        b'class="NOVEL"><meta expanded="True"/><name status="None" import="None">Act One</name>'
        b'</item>'
        b'<item handle="c000000000001" parent="b000000000001" order="0" type="FILE" class="NOVEL" '
        b'layout="DOCUMENT"><meta charCount="300" wordCount="50" paraCount="2" cursorPos="0"/>'
        b'<name status="None" import="None" exported="True">Chapter One</name></item>'
        b'<item handle="c000000000002" parent="b000000000001" order="0" type="FILE" class="NOVEL" '
        b'layout="DOCUMENT"><meta charCount="3000" wordCount="500" paraCount="20" cursorPos="0"/>'
        b'<name status="None" import="None" exported="True">Scene One</name></item>'
        b'<item handle="a000000000002" parent="None" order="0" type="ROOT" class="ARCHIVE"><meta '
        b'expanded="False"/><name status="None" import="None">Outtakes</name></item>'
        b'<item handle="a000000000003" parent="None" order="0" type="TRASH" class="TRASH"><meta '
        b'expanded="False"/><name status="None" import="None">Trash</name></item>'
        b'<item handle="a000000000004" parent="None" order="0" type="ROOT" class="CHARACTER">'
        b'<meta expanded="True"/><name status="None" import="None">Characters</name></item>'
        b'<item handle="b000000000002" parent="a000000000002" order="0" type="FILE" '
        b'class="CHARACTER" layout="NOTE"><meta charCount="2000" wordCount="400" paraCount="16" '
        b'cursorPos="0"/><name status="None" import="None" exported="True">Jane Doe</name></item>'
        b'</content>'
        b'</novelWriterXML>'
    )

    theTree.clear()
    assert len(theTree) == 0
    assert not theTree.unpackXML(nwXML)
    assert theTree.unpackXML(nwXML[0])
    assert len(theTree) == len(mockItems)

# END Test testCoreTree_XMLPackUnpack


@pytest.mark.core
def testCoreTree_ToCFile(monkeypatch, mockGUI, mockItems, tmpDir):
    """Test writing the ToC.txt file.
    """
    theProject = NWProject(mockGUI)
    theTree = NWTree(theProject)

    for tHandle, pHandle, nwItem in mockItems:
        theTree.append(tHandle, pHandle, nwItem)

    assert len(theTree) == len(mockItems)
    theTree._treeOrder.append("stuff")

    def mockIsFile(fileName):
        """Return True for items that are files in novelWriter and
        should thus also be files in the project folder structure.
        """
        dItem = theTree[fileName[8:21]]
        assert dItem is not None
        return dItem.itemType == nwItemType.FILE

    monkeypatch.setattr("os.path.isfile", mockIsFile)

    theProject.projContent = "content"
    theProject.projPath = None
    assert not theTree.writeToCFile()

    theProject.projPath = tmpDir
    assert theTree.writeToCFile()

    pathA = os.path.join("content", "c000000000001.nwd")
    pathB = os.path.join("content", "c000000000002.nwd")
    pathC = os.path.join("content", "b000000000002.nwd")

    assert readFile(os.path.join(tmpDir, nwFiles.TOC_TXT)) == (
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
