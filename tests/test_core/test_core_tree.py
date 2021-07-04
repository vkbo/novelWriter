"""
novelWriter – NWTree Class Tester
=================================

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

import os
import pytest

from lxml import etree
from hashlib import sha256

from tools import readFile

from nw.core.project import NWProject, NWItem, NWTree
from nw.enum import nwItemClass, nwItemType, nwItemLayout
from nw.constants import nwFiles


@pytest.fixture(scope="function")
def dummyItems(mockGUI):
    """Create a list of mock items.
    """
    theProject = NWProject(mockGUI)

    itemA = NWItem(theProject)
    itemA.itemName = "Novel"
    itemA.itemType = nwItemType.ROOT
    itemA.itemClass = nwItemClass.NOVEL
    itemA.isExpanded = True

    itemB = NWItem(theProject)
    itemB.itemName = "Act One"
    itemB.itemType = nwItemType.FOLDER
    itemB.itemClass = nwItemClass.NOVEL
    itemB.isExpanded = True

    itemC = NWItem(theProject)
    itemC.itemName = "Chapter One"
    itemC.itemType = nwItemType.FILE
    itemC.itemClass = nwItemClass.NOVEL
    itemC.itemLayout = nwItemLayout.CHAPTER
    itemC.charCount = 300
    itemC.wordCount = 50
    itemC.paraCount = 2

    itemD = NWItem(theProject)
    itemD.itemName = "Scene One"
    itemD.itemType = nwItemType.FILE
    itemD.itemClass = nwItemClass.NOVEL
    itemD.itemLayout = nwItemLayout.SCENE
    itemD.charCount = 3000
    itemD.wordCount = 500
    itemD.paraCount = 20

    itemE = NWItem(theProject)
    itemE.itemName = "Outtakes"
    itemE.itemType = nwItemType.ROOT
    itemE.itemClass = nwItemClass.ARCHIVE
    itemE.isExpanded = False

    itemF = NWItem(theProject)
    itemF.itemName = "Trash"
    itemF.itemType = nwItemType.TRASH
    itemF.itemClass = nwItemClass.TRASH
    itemF.isExpanded = False

    itemG = NWItem(theProject)
    itemG.itemName = "Characters"
    itemG.itemType = nwItemType.ROOT
    itemG.itemClass = nwItemClass.CHARACTER
    itemG.isExpanded = True

    itemH = NWItem(theProject)
    itemH.itemName = "Jane Doe"
    itemH.itemType = nwItemType.FILE
    itemH.itemClass = nwItemClass.CHARACTER
    itemH.itemLayout = nwItemLayout.NOTE
    itemH.charCount = 2000
    itemH.wordCount = 400
    itemH.paraCount = 16

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
def testCoreTree_BuildTree(mockGUI, dummyItems):
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
    for tHandle, pHandle, nwItem in dummyItems:
        aHandles.append(tHandle)
        assert theTree.append(tHandle, pHandle, nwItem)

    assert theTree._treeChanged

    # Check that tree is not empty (calls __bool__)
    assert theTree

    # Check the number of elements (calls __len__)
    assert len(theTree) == len(dummyItems)

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
    itemT.itemName = "Trash"
    itemT.itemType = nwItemType.TRASH
    itemT.itemClass = nwItemClass.TRASH
    itemT.isExpanded = False

    assert not theTree.append("1234567890abc", None, itemT)
    assert len(theTree) == len(dummyItems)

    # Generate handle automatically
    itemT = NWItem(theProject)
    itemT.itemName = "New File"
    itemT.itemType = nwItemType.FILE
    itemT.itemClass = nwItemClass.NOVEL
    itemT.itemLayout = nwItemLayout.SCENE

    assert theTree.append(None, None, itemT)
    assert len(theTree) == len(dummyItems) + 1

    theList = theTree.handles()
    assert theList[-1] == "73475cb40a568"

    # Try to add existing handle
    assert not theTree.append("73475cb40a568", None, itemT)
    assert len(theTree) == len(dummyItems) + 1

    # Delete a non-existing item
    del theTree["stuff"]
    assert len(theTree) == len(dummyItems) + 1

    # Delete the last item
    del theTree["73475cb40a568"]
    assert len(theTree) == len(dummyItems)
    assert "73475cb40a568" not in theTree

    # Delete the Novel, Archive and Trash folders
    del theTree["a000000000001"]
    assert len(theTree) == len(dummyItems) - 1
    assert "a000000000001" not in theTree

    del theTree["a000000000002"]
    assert len(theTree) == len(dummyItems) - 2
    assert "a000000000002" not in theTree
    assert theTree.archiveRoot() is None

    del theTree["a000000000003"]
    assert len(theTree) == len(dummyItems) - 3
    assert "a000000000003" not in theTree
    assert theTree.trashRoot() is None

# END Test testCoreTree_BuildTree


@pytest.mark.core
def testCoreTree_Methods(mockGUI, dummyItems):
    """Test bvarious class methods.
    """
    theProject = NWProject(mockGUI)
    theTree = NWTree(theProject)

    for tHandle, pHandle, nwItem in dummyItems:
        theTree.append(tHandle, pHandle, nwItem)

    assert len(theTree) == len(dummyItems)

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
    theTree["b000000000001"].itemParent = "stuff"
    assert theTree.getItemPath("c000000000001") == [
        "c000000000001", "b000000000001"
    ]

    theTree["b000000000001"].itemParent = "a000000000001"
    assert theTree.getItemPath("c000000000001") == [
        "c000000000001", "b000000000001", "a000000000001"
    ]

    # Change file layout
    assert not theTree.setFileItemLayout("stuff", nwItemLayout.UNNUMBERED)
    assert not theTree.setFileItemLayout("b000000000001", nwItemLayout.UNNUMBERED)
    assert not theTree.setFileItemLayout("c000000000001", "stuff")
    assert theTree.setFileItemLayout("c000000000001", nwItemLayout.UNNUMBERED)
    assert theTree["c000000000001"].itemLayout == nwItemLayout.UNNUMBERED

# END Test testCoreTree_Methods


@pytest.mark.core
def testCoreTree_UpdateItemLayout(mockGUI, dummyItems):
    """Test building a project tree from a list of items.
    """
    theProject = NWProject(mockGUI)
    theTree = NWTree(theProject)

    for tHandle, pHandle, nwItem in dummyItems:
        theTree.append(tHandle, pHandle, nwItem)

    assert len(theTree) == len(dummyItems)

    # Check rejected items
    assert not theTree.updateItemLayout("0000000000000", "H1")  # Non-existent handle
    assert not theTree.updateItemLayout("a000000000004", "H2")  # Character file
    assert not theTree.updateItemLayout("c000000000002", "H0")  # Wrong header level

    cHandle = "c000000000002"

    # Check layouts we won't change
    theTree[cHandle].setLayout(nwItemLayout.NO_LAYOUT)
    assert not theTree.updateItemLayout("c000000000002", "H1")

    theTree[cHandle].setLayout(nwItemLayout.TITLE)
    assert not theTree.updateItemLayout("c000000000002", "H1")

    theTree[cHandle].setLayout(nwItemLayout.PAGE)
    assert not theTree.updateItemLayout("c000000000002", "H1")

    theTree[cHandle].setLayout(nwItemLayout.NOTE)
    assert not theTree.updateItemLayout("c000000000002", "H1")

    # BOOK is also a layout we change to, but never from
    theTree[cHandle].setLayout(nwItemLayout.BOOK)
    assert not theTree.updateItemLayout("c000000000002", "H1")

    # Test SCENE Changes
    # ==================

    # H1 -> BOOK
    theTree[cHandle].setLayout(nwItemLayout.SCENE)
    assert theTree.updateItemLayout("c000000000002", "H1")
    assert theTree[cHandle].itemLayout == nwItemLayout.BOOK

    # H2 -> CHAPTER
    theTree[cHandle].setLayout(nwItemLayout.SCENE)
    assert theTree.updateItemLayout("c000000000002", "H2")
    assert theTree[cHandle].itemLayout == nwItemLayout.CHAPTER

    # H3 -> No CHange
    theTree[cHandle].setLayout(nwItemLayout.SCENE)
    assert not theTree.updateItemLayout("c000000000002", "H3")

    # H4 -> No CHange
    theTree[cHandle].setLayout(nwItemLayout.SCENE)
    assert not theTree.updateItemLayout("c000000000002", "H4")

    # Test CHAPTER Changes
    # ====================

    # H1 -> BOOK
    theTree[cHandle].setLayout(nwItemLayout.CHAPTER)
    assert theTree.updateItemLayout("c000000000002", "H1")
    assert theTree[cHandle].itemLayout == nwItemLayout.BOOK

    # H2 -> No Change
    theTree[cHandle].setLayout(nwItemLayout.CHAPTER)
    assert not theTree.updateItemLayout("c000000000002", "H2")

    # H3 -> SCENE
    theTree[cHandle].setLayout(nwItemLayout.CHAPTER)
    assert theTree.updateItemLayout("c000000000002", "H3")
    assert theTree[cHandle].itemLayout == nwItemLayout.SCENE

    # H4 -> SCENE
    theTree[cHandle].setLayout(nwItemLayout.CHAPTER)
    assert theTree.updateItemLayout("c000000000002", "H4")
    assert theTree[cHandle].itemLayout == nwItemLayout.SCENE

    # Test UNNUMBERED Changes
    # =======================

    # H1 -> BOOK
    theTree[cHandle].setLayout(nwItemLayout.UNNUMBERED)
    assert theTree.updateItemLayout("c000000000002", "H1")
    assert theTree[cHandle].itemLayout == nwItemLayout.BOOK

    # H2 -> No Change
    theTree[cHandle].setLayout(nwItemLayout.UNNUMBERED)
    assert not theTree.updateItemLayout("c000000000002", "H2")

    # H3 -> SCENE
    theTree[cHandle].setLayout(nwItemLayout.UNNUMBERED)
    assert theTree.updateItemLayout("c000000000002", "H3")
    assert theTree[cHandle].itemLayout == nwItemLayout.SCENE

    # H4 -> SCENE
    theTree[cHandle].setLayout(nwItemLayout.UNNUMBERED)
    assert theTree.updateItemLayout("c000000000002", "H4")
    assert theTree[cHandle].itemLayout == nwItemLayout.SCENE

    # Test PARTITION Changes
    # ======================

    # H1 -> BOOK
    theTree[cHandle].setLayout(nwItemLayout.PARTITION)
    assert not theTree.updateItemLayout("c000000000002", "H1")

    # H2 -> No Change
    theTree[cHandle].setLayout(nwItemLayout.PARTITION)
    assert theTree.updateItemLayout("c000000000002", "H2")
    assert theTree[cHandle].itemLayout == nwItemLayout.CHAPTER

    # H3 -> SCENE
    theTree[cHandle].setLayout(nwItemLayout.PARTITION)
    assert theTree.updateItemLayout("c000000000002", "H3")
    assert theTree[cHandle].itemLayout == nwItemLayout.SCENE

    # H4 -> SCENE
    theTree[cHandle].setLayout(nwItemLayout.PARTITION)
    assert theTree.updateItemLayout("c000000000002", "H4")
    assert theTree[cHandle].itemLayout == nwItemLayout.SCENE

# END Test testCoreTree_UpdateItemLayout


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
    monkeypatch.setattr("nw.core.tree.time", lambda: 123.4)

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
def testCoreTree_Stats(mockGUI, dummyItems):
    """Test project stats methods.
    """
    theProject = NWProject(mockGUI)
    theTree = NWTree(theProject)

    for tHandle, pHandle, nwItem in dummyItems:
        theTree.append(tHandle, pHandle, nwItem)

    assert len(theTree) == len(dummyItems)
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
def testCoreTree_Reorder(mockGUI, dummyItems):
    """Test changing tree order.
    """
    theProject = NWProject(mockGUI)
    theTree = NWTree(theProject)

    aHandle = []
    for tHandle, pHandle, nwItem in dummyItems:
        aHandle.append(tHandle)
        theTree.append(tHandle, pHandle, nwItem)

    assert len(theTree) == len(dummyItems)

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
def testCoreTree_XMLPackUnpack(mockGUI, dummyItems):
    """Test packing and unpacking the tree to and from XML.
    """
    theProject = NWProject(mockGUI)
    theTree = NWTree(theProject)

    for tHandle, pHandle, nwItem in dummyItems:
        theTree.append(tHandle, pHandle, nwItem)

    assert len(theTree) == len(dummyItems)

    nwXML = etree.Element("novelWriterXML")
    theTree.packXML(nwXML)
    assert etree.tostring(nwXML, pretty_print=False, encoding="utf-8") == (
        b"<novelWriterXML>"
        b"<content count=\"8\">"
        b"<item handle=\"a000000000001\" order=\"0\" parent=\"None\">"
        b"<name>Novel</name><type>ROOT</type><class>NOVEL</class><status>None</status>"
        b"<expanded>True</expanded></item>"
        b"<item handle=\"b000000000001\" order=\"0\" parent=\"a000000000001\">"
        b"<name>Act One</name><type>FOLDER</type><class>NOVEL</class><status>None</status>"
        b"<expanded>True</expanded></item>"
        b"<item handle=\"c000000000001\" order=\"0\" parent=\"b000000000001\">"
        b"<name>Chapter One</name><type>FILE</type><class>NOVEL</class><status>None</status>"
        b"<exported>True</exported><layout>CHAPTER</layout><charCount>300</charCount>"
        b"<wordCount>50</wordCount><paraCount>2</paraCount><cursorPos>0</cursorPos></item>"
        b"<item handle=\"c000000000002\" order=\"0\" parent=\"b000000000001\">"
        b"<name>Scene One</name><type>FILE</type><class>NOVEL</class><status>None</status>"
        b"<exported>True</exported><layout>SCENE</layout><charCount>3000</charCount>"
        b"<wordCount>500</wordCount><paraCount>20</paraCount><cursorPos>0</cursorPos></item>"
        b"<item handle=\"a000000000002\" order=\"0\" parent=\"None\">"
        b"<name>Outtakes</name><type>ROOT</type><class>ARCHIVE</class><status>None</status>"
        b"<expanded>False</expanded></item>"
        b"<item handle=\"a000000000003\" order=\"0\" parent=\"None\">"
        b"<name>Trash</name><type>TRASH</type><class>TRASH</class><status>None</status>"
        b"<expanded>False</expanded></item>"
        b"<item handle=\"a000000000004\" order=\"0\" parent=\"None\">"
        b"<name>Characters</name><type>ROOT</type><class>CHARACTER</class><status>None</status>"
        b"<expanded>True</expanded></item>"
        b"<item handle=\"b000000000002\" order=\"0\" parent=\"a000000000002\">"
        b"<name>Jane Doe</name><type>FILE</type><class>CHARACTER</class><status>None</status>"
        b"<exported>True</exported><layout>NOTE</layout><charCount>2000</charCount>"
        b"<wordCount>400</wordCount><paraCount>16</paraCount><cursorPos>0</cursorPos></item>"
        b"</content></novelWriterXML>"
    )

    theTree.clear()
    assert len(theTree) == 0
    assert not theTree.unpackXML(nwXML)
    assert theTree.unpackXML(nwXML[0])
    assert len(theTree) == len(dummyItems)

# END Test testCoreTree_XMLPackUnpack


@pytest.mark.core
def testCoreTree_ToCFile(monkeypatch, mockGUI, dummyItems, tmpDir):
    """Test writing the ToC.txt file.
    """
    theProject = NWProject(mockGUI)
    theTree = NWTree(theProject)

    for tHandle, pHandle, nwItem in dummyItems:
        theTree.append(tHandle, pHandle, nwItem)

    assert len(theTree) == len(dummyItems)
    theTree._treeOrder.append("stuff")

    def dummyIsFile(fileName):
        """Return True for items that are files in novelWriter and
        should thus also be files in the project folder structure.
        """
        dItem = theTree[fileName[8:21]]
        assert dItem is not None
        return dItem.itemType == nwItemType.FILE

    monkeypatch.setattr("os.path.isfile", dummyIsFile)

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
        "File Name                  Class      Layout      Document Label\n"
        "-------------------------------------------------------------\n"
        f"{pathA}  NOVEL      CHAPTER     Chapter One\n"
        f"{pathB}  NOVEL      SCENE       Scene One\n"
        f"{pathC}  CHARACTER  NOTE        Jane Doe\n"
    )

# END Test testCoreTree_ToCFile
