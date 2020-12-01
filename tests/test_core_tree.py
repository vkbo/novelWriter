# -*- coding: utf-8 -*-
"""novelWriter NWTree Class Tester
"""

import os
import pytest

from lxml import etree

from nw.core.project import NWProject, NWItem, NWTree
from nw.constants import nwItemClass, nwItemType, nwItemLayout, nwFiles

@pytest.fixture(scope="session")
def dummyItems(dummyGUI):
    """Create a list of dummy items.
    """
    theProject = NWProject(dummyGUI)

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
def testCoreTree_BuildTree(dummyGUI, dummyItems):
    """Test building a project tree from a list of items.
    """
    theProject = NWProject(dummyGUI)
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
    for tHandle, pHande, nwItem in dummyItems:
        aHandles.append(tHandle)
        theTree.append(tHandle, pHande, nwItem)

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

    theTree.append("1234567890abc", None, itemT)
    assert len(theTree) == len(dummyItems)

    # Generate handle automatically
    itemT = NWItem(theProject)
    itemT.itemName = "New File"
    itemT.itemType = nwItemType.FILE
    itemT.itemClass = nwItemClass.NOVEL
    itemT.itemLayout = nwItemLayout.SCENE

    theTree.append(None, None, itemT)
    assert len(theTree) == len(dummyItems) + 1

    theList = theTree.handles()
    assert theList[-1] == "73475cb40a568"

    # Duplicate handle
    itemT = NWItem(theProject)
    itemT.itemName = "New File"
    itemT.itemType = nwItemType.FILE
    itemT.itemClass = nwItemClass.NOVEL
    itemT.itemLayout = nwItemLayout.SCENE

    theTree.append("73475cb40a568", None, itemT)
    assert len(theTree) == len(dummyItems) + 2

    theList = theTree.handles()
    assert theList[-1] == "44cb730c42048"

    # Delete the last two items
    del theTree["dummy"]
    assert len(theTree) == len(dummyItems) + 2

    del theTree["44cb730c42048"]
    assert len(theTree) == len(dummyItems) + 1
    assert "44cb730c42048" not in theTree

    del theTree["73475cb40a568"]
    assert len(theTree) == len(dummyItems)
    assert "73475cb40a568" not in theTree

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
def testCoreTree_Methods(dummyGUI, dummyItems):
    """Test building a project tree from a list of items.
    """
    theProject = NWProject(dummyGUI)
    theTree = NWTree(theProject)

    for tHandle, pHande, nwItem in dummyItems:
        theTree.append(tHandle, pHande, nwItem)

    assert len(theTree) == len(dummyItems)

    # Root item lookup
    theTree._treeRoots.append("dummy")
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
    assert theTree.getRootItem("dummy") is None

    # Get item path
    assert theTree.getItemPath("dummy") == []
    assert theTree.getItemPath("c000000000001") == [
        "c000000000001", "b000000000001", "a000000000001"
    ]

    # Break the folder parent handle
    theTree["b000000000001"].itemParent = "dummy"
    assert theTree.getItemPath("c000000000001") == [
        "c000000000001", "b000000000001"
    ]

    theTree["b000000000001"].itemParent = "a000000000001"
    assert theTree.getItemPath("c000000000001") == [
        "c000000000001", "b000000000001", "a000000000001"
    ]

    # Change file layout
    assert not theTree.setFileItemLayout("dummy", nwItemLayout.UNNUMBERED)
    assert not theTree.setFileItemLayout("b000000000001", nwItemLayout.UNNUMBERED)
    assert not theTree.setFileItemLayout("c000000000001", "stuff")
    assert theTree.setFileItemLayout("c000000000001", nwItemLayout.UNNUMBERED)
    assert theTree["c000000000001"].itemLayout == nwItemLayout.UNNUMBERED

# END Test testCoreTree_Methods

@pytest.mark.core
def testCoreTree_MakeHandles(dummyGUI, monkeypatch):
    """Test generating item handles.
    """
    theProject = NWProject(dummyGUI)
    theTree = NWTree(theProject)

    theTree.setSeed(42)

    tHandle = theTree._makeHandle()
    assert tHandle == "73475cb40a568"

    # Add the next in line to the project to foprce duplicate
    theTree._projTree["44cb730c42048"] = None
    tHandle = theTree._makeHandle()
    assert tHandle == "71ee45a3c0db9"

    # Fix the time() function and force a handle collission
    theTree.setSeed(None)
    monkeypatch.setattr("nw.core.tree.time", lambda: 123.4)

    tHandle = theTree._makeHandle()
    theTree._projTree[tHandle] = None
    assert tHandle == "5f466d7afa48b"

    tHandle = theTree._makeHandle()
    theTree._projTree[tHandle] = None
    assert tHandle == "a79acf4c634a7"

    monkeypatch.undo()

# END Test testCoreTree_MakeHandles

@pytest.mark.core
def testCoreTree_Stats(dummyGUI, dummyItems):
    """Test project stats methods.
    """
    theProject = NWProject(dummyGUI)
    theTree = NWTree(theProject)

    for tHandle, pHande, nwItem in dummyItems:
        theTree.append(tHandle, pHande, nwItem)

    assert len(theTree) == len(dummyItems)
    theTree._treeOrder.append("dummy")

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
def testCoreTree_Reorder(dummyGUI, dummyItems):
    """Test changing tree order.
    """
    theProject = NWProject(dummyGUI)
    theTree = NWTree(theProject)

    aHandle = []
    for tHandle, pHande, nwItem in dummyItems:
        aHandle.append(tHandle)
        theTree.append(tHandle, pHande, nwItem)

    assert len(theTree) == len(dummyItems)

    bHandle = aHandle.copy()
    bHandle[2], bHandle[3] = bHandle[3], bHandle[2]
    assert aHandle != bHandle

    assert theTree.handles() == aHandle
    theTree.setOrder(bHandle)
    assert theTree.handles() == bHandle

    theTree.setOrder(bHandle + ["dummy"])
    assert theTree.handles() == bHandle

    theTree._treeOrder.append("dummy")
    theTree.setOrder(bHandle)
    assert theTree.handles() == bHandle

# END Test testCoreTree_Reorder

@pytest.mark.core
def testCoreTree_XMLPackUnpack(dummyGUI, dummyItems):
    """Test changing tree order.
    """
    theProject = NWProject(dummyGUI)
    theTree = NWTree(theProject)

    for tHandle, pHande, nwItem in dummyItems:
        theTree.append(tHandle, pHande, nwItem)

    assert len(theTree) == len(dummyItems)

    nwXML = etree.Element("novelWriterXML")
    theTree.packXML(nwXML)
    assert etree.tostring(nwXML, pretty_print=False, encoding="utf-8") == (
        b"<novelWriterXML>"
        b"<content count=\"8\">"
        b"<item handle=\"a000000000001\" order=\"None\" parent=\"None\">"
        b"<name>Novel</name><type>ROOT</type><class>NOVEL</class><status>None</status>"
        b"<expanded>True</expanded></item>"
        b"<item handle=\"b000000000001\" order=\"None\" parent=\"a000000000001\">"
        b"<name>Act One</name><type>FOLDER</type><class>NOVEL</class><status>None</status>"
        b"<expanded>True</expanded></item>"
        b"<item handle=\"c000000000001\" order=\"None\" parent=\"b000000000001\">"
        b"<name>Chapter One</name><type>FILE</type><class>NOVEL</class><status>None</status>"
        b"<exported>True</exported><layout>UNNUMBERED</layout><charCount>300</charCount>"
        b"<wordCount>50</wordCount><paraCount>2</paraCount><cursorPos>0</cursorPos></item>"
        b"<item handle=\"c000000000002\" order=\"None\" parent=\"b000000000001\">"
        b"<name>Scene One</name><type>FILE</type><class>NOVEL</class><status>None</status>"
        b"<exported>True</exported><layout>SCENE</layout><charCount>3000</charCount>"
        b"<wordCount>500</wordCount><paraCount>20</paraCount><cursorPos>0</cursorPos></item>"
        b"<item handle=\"a000000000002\" order=\"None\" parent=\"None\">"
        b"<name>Outtakes</name><type>ROOT</type><class>ARCHIVE</class><status>None</status>"
        b"<expanded>False</expanded></item>"
        b"<item handle=\"a000000000003\" order=\"None\" parent=\"None\">"
        b"<name>Trash</name><type>TRASH</type><class>TRASH</class><status>None</status>"
        b"<expanded>False</expanded></item>"
        b"<item handle=\"a000000000004\" order=\"None\" parent=\"None\">"
        b"<name>Characters</name><type>ROOT</type><class>CHARACTER</class><status>None</status>"
        b"<expanded>True</expanded></item>"
        b"<item handle=\"b000000000002\" order=\"None\" parent=\"a000000000002\">"
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
def testCoreTree_ToCFile(dummyGUI, dummyItems, tmpDir, monkeypatch):
    """Test writing the ToC.txt file.
    """
    theProject = NWProject(dummyGUI)
    theTree = NWTree(theProject)

    for tHandle, pHande, nwItem in dummyItems:
        theTree.append(tHandle, pHande, nwItem)

    assert len(theTree) == len(dummyItems)
    theTree._treeOrder.append("dummy")

    monkeypatch.setattr("os.path.isfile", lambda *args: True)

    theProject.projContent = "content"
    theProject.projPath = None
    assert not theTree.writeToCFile()

    theProject.projPath = tmpDir
    assert theTree.writeToCFile()

    with open(os.path.join(tmpDir, nwFiles.TOC_TXT), mode="r", encoding="utf8") as inFile:
        assert inFile.read() == (
            "\n"
            "Table of Contents\n"
            "=================\n"
            "\n"
            "File Name                  Class      Layout      Document Label\n"
            "-------------------------------------------------------------\n"
            "content/a000000000001.nwd  NOVEL      NO_LAYOUT   Novel\n"
            "content/b000000000001.nwd  NOVEL      NO_LAYOUT   Act One\n"
            "content/c000000000001.nwd  NOVEL      UNNUMBERED  Chapter One\n"
            "content/c000000000002.nwd  NOVEL      SCENE       Scene One\n"
            "content/a000000000002.nwd  ARCHIVE    NO_LAYOUT   Outtakes\n"
            "content/a000000000003.nwd  TRASH      NO_LAYOUT   Trash\n"
            "content/a000000000004.nwd  CHARACTER  NO_LAYOUT   Characters\n"
            "content/b000000000002.nwd  CHARACTER  NOTE        Jane Doe\n"
        )

# END Test testCoreTree_ToCFile
