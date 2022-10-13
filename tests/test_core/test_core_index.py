"""
novelWriter – NWIndex Class Tester
==================================

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
import json
import pytest

from shutil import copyfile

from mock import causeException
from tools import buildTestProject, cmpFiles, writeFile

from novelwriter.core.project import NWProject
from novelwriter.core.index import NWIndex, countWords, TagsIndex
from novelwriter.enum import nwItemClass, nwItemLayout


@pytest.mark.core
def testCoreIndex_LoadSave(monkeypatch, nwLipsum, mockGUI, outDir, refDir):
    """Test core functionality of scaning, saving, loading and checking
    the index cache file.
    """
    projFile = os.path.join(nwLipsum, "meta", "tagsIndex.json")
    testFile = os.path.join(outDir, "coreIndex_LoadSave_tagsIndex.json")
    compFile = os.path.join(refDir, "coreIndex_LoadSave_tagsIndex.json")

    theProject = NWProject(mockGUI)
    assert theProject.openProject(nwLipsum)

    theIndex = NWIndex(theProject)
    assert repr(theIndex) == "<NWIndex project='Lorem Ipsum'>"

    notIndexable = {
        "b3643d0f92e32": False,  # Novel ROOT
        "45e6b01ca35c1": False,  # Chapter One FOLDER
        "6bd935d2490cd": False,  # Chapter Two FOLDER
        "67a8707f2f249": False,  # Character ROOT
        "6c6afb1247750": False,  # Plot ROOT
        "60bdf227455cc": False,  # World ROOT
    }
    for tItem in theProject.tree:
        assert theIndex.reIndexHandle(tItem.itemHandle) is notIndexable.get(tItem.itemHandle, True)

    assert theIndex.reIndexHandle(None) is False

    # Make the save fail
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeException)
        assert theIndex.saveIndex() is False

    # Make the save pass
    assert theIndex.saveIndex() is True

    # Take a copy of the index
    tagIndex = str(theIndex._tagsIndex.packData())
    itemsIndex = str(theIndex._itemIndex.packData())

    # Delete a handle
    assert theIndex._tagsIndex["Bod"] is not None
    assert theIndex._itemIndex["4c4f28287af27"] is not None
    theIndex.deleteHandle("4c4f28287af27")
    assert theIndex._tagsIndex["Bod"] is None
    assert theIndex._itemIndex["4c4f28287af27"] is None

    # Clear the index
    theIndex.clearIndex()
    assert theIndex._tagsIndex._tags == {}
    assert theIndex._itemIndex._items == {}

    # Make the load fail
    with monkeypatch.context() as mp:
        mp.setattr(json, "load", causeException)
        assert theIndex.loadIndex() is False
        assert theIndex.indexBroken is True

    # Make the load pass
    assert theIndex.loadIndex() is True
    assert theIndex.indexBroken is False

    assert str(theIndex._tagsIndex.packData()) == tagIndex
    assert str(theIndex._itemIndex.packData()) == itemsIndex

    # Check File
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    # Write an emtpy index file and load it
    writeFile(projFile, "{}")
    assert theIndex.loadIndex() is False
    assert theIndex.indexBroken is True

    # Write an index file that passes loading, but is still empty
    writeFile(projFile, '{"tagsIndex": {}, "itemIndex": {}}')
    assert theIndex.loadIndex() is True
    assert theIndex.indexBroken is False

    # Check that the index is re-populated
    assert "04468803b92e1" in theIndex._itemIndex
    assert "2426c6f0ca922" in theIndex._itemIndex
    assert "441420a886d82" in theIndex._itemIndex
    assert "47666c91c7ccf" in theIndex._itemIndex
    assert "4c4f28287af27" in theIndex._itemIndex
    assert "846352075de7d" in theIndex._itemIndex
    assert "88243afbe5ed8" in theIndex._itemIndex
    assert "88d59a277361b" in theIndex._itemIndex
    assert "8c58a65414c23" in theIndex._itemIndex
    assert "db7e733775d4d" in theIndex._itemIndex
    assert "eb103bc70c90c" in theIndex._itemIndex
    assert "f8c0562e50f1b" in theIndex._itemIndex
    assert "f96ec11c6a3da" in theIndex._itemIndex
    assert "fb609cd8319dc" in theIndex._itemIndex
    assert "7a992350f3eb6" in theIndex._itemIndex

    # Finalise
    assert theProject.closeProject() is True

# END Test testCoreIndex_LoadSave


@pytest.mark.core
def testCoreIndex_ScanThis(mockGUI):
    """Test the tag scanner function scanThis.
    """
    theProject = NWProject(mockGUI)
    theIndex = theProject.index

    isValid, theBits, thePos = theIndex.scanThis("tag: this, and this")
    assert isValid is False

    isValid, theBits, thePos = theIndex.scanThis("@")
    assert isValid is False

    isValid, theBits, thePos = theIndex.scanThis("@:")
    assert isValid is False

    isValid, theBits, thePos = theIndex.scanThis(" @a: b")
    assert isValid is False

    isValid, theBits, thePos = theIndex.scanThis("@a:")
    assert isValid is True
    assert theBits == ["@a"]
    assert thePos  == [0]

    isValid, theBits, thePos = theIndex.scanThis("@a:b")
    assert isValid is True
    assert theBits == ["@a", "b"]
    assert thePos  == [0, 3]

    isValid, theBits, thePos = theIndex.scanThis("@a:b,c,d")
    assert isValid is True
    assert theBits == ["@a", "b", "c", "d"]
    assert thePos  == [0, 3, 5, 7]

    isValid, theBits, thePos = theIndex.scanThis("@a : b , c , d")
    assert isValid is True
    assert theBits == ["@a", "b", "c", "d"]
    assert thePos  == [0, 5, 9, 13]

    isValid, theBits, thePos = theIndex.scanThis("@tag: this, and this")
    assert isValid is True
    assert theBits == ["@tag", "this", "and this"]
    assert thePos  == [0, 6, 12]

    assert theProject.closeProject() is True

# END Test testCoreIndex_ScanThis


@pytest.mark.core
def testCoreIndex_CheckThese(mockGUI, fncDir, mockRnd):
    """Test the tag checker function checkThese.
    """
    theProject = NWProject(mockGUI)
    buildTestProject(theProject, fncDir)
    theIndex = theProject.index

    nHandle = theProject.newFile("Hello", "0000000000010")
    cHandle = theProject.newFile("Jane",  "0000000000012")
    nItem = theProject.tree[nHandle]
    cItem = theProject.tree[cHandle]

    assert theIndex.rootChangedSince("0000000000010", 0) is False
    assert theIndex.indexChangedSince(0) is False

    assert theIndex.scanText(cHandle, (
        "# Jane Smith\n"
        "@tag: Jane\n"
        "@tag:\n"
        "@:\n"
    ))
    assert theIndex.scanText(nHandle, (
        "# Hello World!\n"
        "@pov: Jane\n"
        "@invalid: John\n"  # Checks for issue #688
    ))
    assert theIndex._tagsIndex.tagHandle("Jane") == cHandle
    assert theIndex._tagsIndex.tagHeading("Jane") == "T000001"
    assert theIndex._tagsIndex.tagClass("Jane") == "CHARACTER"
    assert theIndex.getNovelData(nHandle, "T000001").title == "Hello World!"
    assert theIndex.getReferences(nHandle, "T000001") == {
        "@char": [],
        "@custom": [],
        "@entity": [],
        "@focus": [],
        "@location": [],
        "@object": [],
        "@plot": [],
        "@pov": ["Jane"],
        "@time": []
    }

    assert theIndex.rootChangedSince("0000000000010", 0) is True
    assert theIndex.indexChangedSince(0) is True

    assert theIndex.getHandleHeaderLevel(cHandle) == "H1"
    assert theIndex.getHandleHeaderLevel(nHandle) == "H1"

    # Zero Items
    assert theIndex.checkThese([], cItem) == []

    # One Item
    assert theIndex.checkThese(["@tag"], cItem) == [True]
    assert theIndex.checkThese(["@who"], cItem) == [False]

    # Two Items
    assert theIndex.checkThese(["@tag", "Jane"], cItem) == [True, True]
    assert theIndex.checkThese(["@tag", "John"], cItem) == [True, True]
    assert theIndex.checkThese(["@tag", "Jane"], nItem) == [True, False]
    assert theIndex.checkThese(["@tag", "John"], nItem) == [True, True]
    assert theIndex.checkThese(["@pov", "John"], nItem) == [True, False]
    assert theIndex.checkThese(["@pov", "Jane"], nItem) == [True, True]
    assert theIndex.checkThese(["@ pov", "Jane"], nItem) == [False, False]
    assert theIndex.checkThese(["@what", "Jane"], nItem) == [False, False]

    # Three Items
    assert theIndex.checkThese(["@tag", "Jane", "John"], cItem) == [True, True, False]
    assert theIndex.checkThese(["@who", "Jane", "John"], cItem) == [False, False, False]
    assert theIndex.checkThese(["@pov", "Jane", "John"], nItem) == [True, True, False]

    assert theProject.closeProject() is True

# END Test testCoreIndex_CheckThese


@pytest.mark.core
def testCoreIndex_ScanText(mockGUI, fncDir, mockRnd):
    """Check the index text scanner.
    """
    theProject = NWProject(mockGUI)
    buildTestProject(theProject, fncDir)
    theIndex = theProject.index

    # Some items for fail to scan tests
    dHandle = theProject.newFolder("Folder", "0000000000010")
    xHandle = theProject.newFile("No Layout", "0000000000010")
    xItem = theProject.tree[xHandle]
    xItem.setLayout(nwItemLayout.NO_LAYOUT)

    # Check invalid data
    assert theIndex.scanText(None, "Hello World!") is False
    assert theIndex.scanText(dHandle, "Hello World!") is False
    assert theIndex.scanText(xHandle, "Hello World!") is False

    xItem.setLayout(nwItemLayout.DOCUMENT)
    xItem.setParent(None)
    assert theIndex.scanText(xHandle, "Hello World!") is False

    # Create the trash folder
    tHandle = theProject.trashFolder()
    assert theProject.tree[tHandle] is not None
    xItem.setParent(tHandle)
    theProject.tree.updateItemData(xItem.itemHandle)
    assert xItem.itemRoot == tHandle
    assert xItem.itemClass == nwItemClass.TRASH
    assert theIndex.scanText(xHandle, "Hello World!") is False

    # Create the archive root
    aHandle = theProject.newRoot(nwItemClass.ARCHIVE)
    assert theProject.tree[aHandle] is not None
    xItem.setParent(aHandle)
    theProject.tree.updateItemData(xItem.itemHandle)
    assert theIndex.scanText(xHandle, "Hello World!") is False

    # Make some usable items
    tHandle = theProject.newFile("Title", "0000000000010")
    pHandle = theProject.newFile("Page",  "0000000000010")
    nHandle = theProject.newFile("Hello", "0000000000010")
    cHandle = theProject.newFile("Jane",  "0000000000012")
    sHandle = theProject.newFile("Scene", "0000000000010")

    # Text Indexing
    # =============

    # Index correct text
    assert theIndex.scanText(cHandle, (
        "# Jane Smith\n"
        "@tag: Jane\n"
    ))
    assert theIndex.scanText(nHandle, (
        "# Hello World!\n"
        "@pov: Jane\n"
        "@char: Jane\n\n"
        "% this is a comment\n\n"
        "This is a story about Jane Smith.\n\n"
        "Well, not really.\n"
    ))
    assert theIndex._tagsIndex.tagHandle("Jane") == cHandle
    assert theIndex._tagsIndex.tagHeading("Jane") == "T000001"
    assert theIndex._tagsIndex.tagClass("Jane") == "CHARACTER"
    assert theIndex.getNovelData(nHandle, "T000001").title == "Hello World!"

    # Title Indexing
    # ==============

    # Document File
    assert theIndex.scanText(nHandle, (
        "# Title One\n\n"
        "% synopsis: Synopsis One.\n\n"
        "Paragraph One.\n\n"
        "## Title Two\n\n"
        "% synopsis: Synopsis Two.\n\n"
        "Paragraph Two.\n\n"
        "### Title Three\n\n"
        "% synopsis: Synopsis Three.\n\n"
        "Paragraph Three.\n\n"
        "#### Title Four\n\n"
        "% synopsis: Synopsis Four.\n\n"
        "Paragraph Four.\n\n"
        "##### Title Five\n\n"  # Not interpreted as a title, the hashes are counted as a word
        "Paragraph Five.\n\n"
    ))
    assert theIndex._itemIndex[nHandle]["T000001"].references == {}
    assert theIndex._itemIndex[nHandle]["T000007"].references == {}
    assert theIndex._itemIndex[nHandle]["T000013"].references == {}
    assert theIndex._itemIndex[nHandle]["T000019"].references == {}

    assert theIndex._itemIndex[nHandle]["T000001"].level == "H1"
    assert theIndex._itemIndex[nHandle]["T000007"].level == "H2"
    assert theIndex._itemIndex[nHandle]["T000013"].level == "H3"
    assert theIndex._itemIndex[nHandle]["T000019"].level == "H4"

    assert theIndex._itemIndex[nHandle]["T000001"].title == "Title One"
    assert theIndex._itemIndex[nHandle]["T000007"].title == "Title Two"
    assert theIndex._itemIndex[nHandle]["T000013"].title == "Title Three"
    assert theIndex._itemIndex[nHandle]["T000019"].title == "Title Four"

    assert theIndex._itemIndex[nHandle]["T000001"].charCount == 23
    assert theIndex._itemIndex[nHandle]["T000007"].charCount == 23
    assert theIndex._itemIndex[nHandle]["T000013"].charCount == 27
    assert theIndex._itemIndex[nHandle]["T000019"].charCount == 56

    assert theIndex._itemIndex[nHandle]["T000001"].wordCount == 4
    assert theIndex._itemIndex[nHandle]["T000007"].wordCount == 4
    assert theIndex._itemIndex[nHandle]["T000013"].wordCount == 4
    assert theIndex._itemIndex[nHandle]["T000019"].wordCount == 9

    assert theIndex._itemIndex[nHandle]["T000001"].paraCount == 1
    assert theIndex._itemIndex[nHandle]["T000007"].paraCount == 1
    assert theIndex._itemIndex[nHandle]["T000013"].paraCount == 1
    assert theIndex._itemIndex[nHandle]["T000019"].paraCount == 3

    assert theIndex._itemIndex[nHandle]["T000001"].synopsis == "Synopsis One."
    assert theIndex._itemIndex[nHandle]["T000007"].synopsis == "Synopsis Two."
    assert theIndex._itemIndex[nHandle]["T000013"].synopsis == "Synopsis Three."
    assert theIndex._itemIndex[nHandle]["T000019"].synopsis == "Synopsis Four."

    # Note File
    assert theIndex.scanText(cHandle, (
        "# Title One\n\n"
        "@tag: One\n\n"
        "% synopsis: Synopsis One.\n\n"
        "Paragraph One.\n\n"
    ))
    assert theIndex._itemIndex[cHandle]["T000001"].references == {}
    assert theIndex._itemIndex[cHandle]["T000001"].level == "H1"
    assert theIndex._itemIndex[cHandle]["T000001"].title == "Title One"
    assert theIndex._itemIndex[cHandle]["T000001"].charCount == 23
    assert theIndex._itemIndex[cHandle]["T000001"].wordCount == 4
    assert theIndex._itemIndex[cHandle]["T000001"].paraCount == 1
    assert theIndex._itemIndex[cHandle]["T000001"].synopsis == "Synopsis One."

    # Valid and Invalid References
    assert theIndex.scanText(sHandle, (
        "# Title One\n\n"
        "@pov: One\n\n"  # Valid
        "@char: Two\n\n"  # Invalid tag
        "@:\n\n"  # Invalid line
        "% synopsis: Synopsis One.\n\n"
        "Paragraph One.\n\n"
    ))
    assert theIndex._itemIndex[sHandle]["T000001"].references == {
        "One": {"@pov"}, "Two": {"@char"}
    }

    # Special Titles
    # ==============

    assert theIndex.scanText(tHandle, (
        "#! My Project\n\n"
        ">> By Jane Doe <<\n\n"
    ))
    assert theIndex._itemIndex[cHandle]["T000001"].references == {}
    assert theIndex._itemIndex[tHandle]["T000001"].level == "H1"
    assert theIndex._itemIndex[tHandle]["T000001"].title == "My Project"
    assert theIndex._itemIndex[tHandle]["T000001"].charCount == 21
    assert theIndex._itemIndex[tHandle]["T000001"].wordCount == 5
    assert theIndex._itemIndex[tHandle]["T000001"].paraCount == 1
    assert theIndex._itemIndex[tHandle]["T000001"].synopsis == ""

    assert theIndex.scanText(tHandle, (
        "##! Prologue\n\n"
        "In the beginning there was time ...\n\n"
    ))
    assert theIndex._itemIndex[cHandle]["T000001"].references == {}
    assert theIndex._itemIndex[tHandle]["T000001"].level == "H2"
    assert theIndex._itemIndex[tHandle]["T000001"].title == "Prologue"
    assert theIndex._itemIndex[tHandle]["T000001"].charCount == 43
    assert theIndex._itemIndex[tHandle]["T000001"].wordCount == 8
    assert theIndex._itemIndex[tHandle]["T000001"].paraCount == 1
    assert theIndex._itemIndex[tHandle]["T000001"].synopsis == ""

    # Page wo/Title
    # =============

    theProject.tree[pHandle]._layout = nwItemLayout.DOCUMENT
    assert theIndex.scanText(pHandle, (
        "This is a page with some text on it.\n\n"
    ))
    assert theIndex._itemIndex[pHandle]["T000000"].references == {}
    assert theIndex._itemIndex[pHandle]["T000000"].level == "H0"
    assert theIndex._itemIndex[pHandle]["T000000"].title == ""
    assert theIndex._itemIndex[pHandle]["T000000"].charCount == 36
    assert theIndex._itemIndex[pHandle]["T000000"].wordCount == 9
    assert theIndex._itemIndex[pHandle]["T000000"].paraCount == 1
    assert theIndex._itemIndex[pHandle]["T000000"].synopsis == ""

    theProject.tree[pHandle]._layout = nwItemLayout.NOTE
    assert theIndex.scanText(pHandle, (
        "This is a page with some text on it.\n\n"
    ))
    assert theIndex._itemIndex[pHandle]["T000000"].references == {}
    assert theIndex._itemIndex[pHandle]["T000000"].level == "H0"
    assert theIndex._itemIndex[pHandle]["T000000"].title == ""
    assert theIndex._itemIndex[pHandle]["T000000"].charCount == 36
    assert theIndex._itemIndex[pHandle]["T000000"].wordCount == 9
    assert theIndex._itemIndex[pHandle]["T000000"].paraCount == 1
    assert theIndex._itemIndex[pHandle]["T000000"].synopsis == ""

    assert theProject.closeProject() is True

# END Test testCoreIndex_ScanText


@pytest.mark.core
def testCoreIndex_ExtractData(mockGUI, fncDir, mockRnd):
    """Check the index data extraction functions.
    """
    theProject = NWProject(mockGUI)
    buildTestProject(theProject, fncDir)

    theIndex = theProject.index
    theIndex.reIndexHandle("0000000000010")
    theIndex.reIndexHandle("0000000000011")
    theIndex.reIndexHandle("0000000000012")
    theIndex.reIndexHandle("0000000000013")
    theIndex.reIndexHandle("0000000000014")
    theIndex.reIndexHandle("0000000000015")
    theIndex.reIndexHandle("0000000000016")
    theIndex.reIndexHandle("0000000000017")

    nHandle = theProject.newFile("Hello", "0000000000010")
    cHandle = theProject.newFile("Jane",  "0000000000012")

    assert theIndex.getNovelData("", "") is None
    assert theIndex.getNovelData("0000000000010", "") is None

    assert theIndex.scanText(cHandle, (
        "# Jane Smith\n"
        "@tag: Jane\n"
    ))
    assert theIndex.scanText(nHandle, (
        "# Hello World!\n"
        "@pov: Jane\n"
        "@char: Jane\n\n"
        "% this is a comment\n\n"
        "This is a story about Jane Smith.\n\n"
        "Well, not really.\n"
    ))

    # The novel structure should contain the pointer to the novel file header
    theKeys = []
    for aKey, _, _, _ in theIndex.novelStructure():
        theKeys.append(aKey)

    assert theKeys == [
        "0000000000014:T000001",
        "0000000000016:T000001",
        "0000000000017:T000001",
        "%s:T000001" % nHandle,
    ]

    # Check that excluded files can be skipped
    theProject.tree[nHandle].setExported(False)

    theKeys = []
    for aKey, _, _, _ in theIndex.novelStructure(skipExcl=False):
        theKeys.append(aKey)

    assert theKeys == [
        "0000000000014:T000001",
        "0000000000016:T000001",
        "0000000000017:T000001",
        "%s:T000001" % nHandle,
    ]

    theKeys = []
    for aKey, _, _, _ in theIndex.novelStructure(skipExcl=True):
        theKeys.append(aKey)

    assert theKeys == [
        "0000000000014:T000001",
        "0000000000016:T000001",
        "0000000000017:T000001",
    ]

    # The novel file should have the correct counts
    cC, wC, pC = theIndex.getCounts(nHandle)
    assert cC == 62  # Characters in text and title only
    assert wC == 12  # Words in text and title only
    assert pC == 2   # Paragraphs in text only

    # getReferences
    # =============

    # Look up an ivalid handle
    theRefs = theIndex.getReferences("Not a handle")
    assert theRefs["@pov"] == []
    assert theRefs["@char"] == []

    # The novel file should now refer to Jane as @pov and @char
    theRefs = theIndex.getReferences(nHandle)
    assert theRefs["@pov"] == ["Jane"]
    assert theRefs["@char"] == ["Jane"]

    # getBackReferenceList
    # ====================

    # None handle should return an empty dict
    assert theIndex.getBackReferenceList(None) == {}

    # The Title Page file should have no references as it has no tag
    assert theIndex.getBackReferenceList("0000000000014") == {}

    # The character file should have a record of the reference from the novel file
    theRefs = theIndex.getBackReferenceList(cHandle)
    assert theRefs == {nHandle: "T000001"}

    # getTagSource
    # ============

    assert theIndex.getTagSource("Jane") == (cHandle, "T000001")
    assert theIndex.getTagSource("John") == (None, "T000000")

    # getCounts
    # =========
    # For whole text and sections

    # Invalid handle or title should return 0s
    assert theIndex.getCounts("stuff") == (0, 0, 0)
    assert theIndex.getCounts(nHandle, "stuff") == (0, 0, 0)

    # Get section counts for a novel file
    assert theIndex.scanText(nHandle, (
        "# Hello World!\n"
        "@pov: Jane\n"
        "@char: Jane\n\n"
        "% this is a comment\n\n"
        "This is a story about Jane Smith.\n\n"
        "Well, not really.\n\n"
        "# Hello World!\n"
        "@pov: Jane\n"
        "@char: Jane\n\n"
        "% this is a comment\n\n"
        "This is a story about Jane Smith.\n\n"
        "Well, not really. She's still awesome though.\n"
    ))
    # Whole document
    cC, wC, pC = theIndex.getCounts(nHandle)
    assert cC == 152
    assert wC == 28
    assert pC == 4

    # First part
    cC, wC, pC = theIndex.getCounts(nHandle, "T000001")
    assert cC == 62
    assert wC == 12
    assert pC == 2

    # Second part
    cC, wC, pC = theIndex.getCounts(nHandle, "T000011")
    assert cC == 90
    assert wC == 16
    assert pC == 2

    # Get section counts for a note file
    assert theIndex.scanText(cHandle, (
        "# Hello World!\n"
        "@pov: Jane\n"
        "@char: Jane\n\n"
        "% this is a comment\n\n"
        "This is a story about Jane Smith.\n\n"
        "Well, not really.\n\n"
        "# Hello World!\n"
        "@pov: Jane\n"
        "@char: Jane\n\n"
        "% this is a comment\n\n"
        "This is a story about Jane Smith.\n\n"
        "Well, not really. She's still awesome though.\n"
    ))
    # Whole document
    cC, wC, pC = theIndex.getCounts(cHandle)
    assert cC == 152
    assert wC == 28
    assert pC == 4

    # First part
    cC, wC, pC = theIndex.getCounts(cHandle, "T000001")
    assert cC == 62
    assert wC == 12
    assert pC == 2

    # Second part
    cC, wC, pC = theIndex.getCounts(cHandle, "T000011")
    assert cC == 90
    assert wC == 16
    assert pC == 2

    # Novel Stats
    # ===========

    hHandle = theProject.newFile("Chapter", "0000000000010")
    sHandle = theProject.newFile("Scene One", "0000000000010")
    tHandle = theProject.newFile("Scene Two", "0000000000010")

    theProject.tree[hHandle].itemLayout == nwItemLayout.DOCUMENT
    theProject.tree[sHandle].itemLayout == nwItemLayout.DOCUMENT
    theProject.tree[tHandle].itemLayout == nwItemLayout.DOCUMENT

    assert theIndex.scanText(hHandle, "## Chapter One\n\n")
    assert theIndex.scanText(sHandle, "### Scene One\n\n")
    assert theIndex.scanText(tHandle, "### Scene Two\n\n")

    assert [(h, t) for h, t, _ in theIndex._itemIndex.iterNovelStructure(skipExcl=False)] == [
        ("0000000000014", "T000001"),
        ("0000000000016", "T000001"),
        ("0000000000017", "T000001"),
        (nHandle, "T000001"),
        (nHandle, "T000011"),
        (hHandle, "T000001"),
        (sHandle, "T000001"),
        (tHandle, "T000001"),
    ]

    assert [(h, t) for h, t, _ in theIndex._itemIndex.iterNovelStructure(skipExcl=True)] == [
        ("0000000000014", "T000001"),
        ("0000000000016", "T000001"),
        ("0000000000017", "T000001"),
        (hHandle, "T000001"),
        (sHandle, "T000001"),
        (tHandle, "T000001"),
    ]

    # Add a fake handle to the tree and check that it's ignored
    theProject.tree._treeOrder.append("0000000000000")
    assert [(h, t) for h, t, _ in theIndex._itemIndex.iterNovelStructure(skipExcl=False)] == [
        ("0000000000014", "T000001"),
        ("0000000000016", "T000001"),
        ("0000000000017", "T000001"),
        (nHandle, "T000001"),
        (nHandle, "T000011"),
        (hHandle, "T000001"),
        (sHandle, "T000001"),
        (tHandle, "T000001"),
    ]
    theProject.tree._treeOrder.remove("0000000000000")

    # Extract stats
    assert theIndex.getNovelWordCount(skipExcl=False) == 43
    assert theIndex.getNovelWordCount(skipExcl=True) == 15
    assert theIndex.getNovelTitleCounts(skipExcl=False) == [0, 3, 2, 3, 0]
    assert theIndex.getNovelTitleCounts(skipExcl=True) == [0, 1, 2, 3, 0]

    # Table of Contents
    assert theIndex.getTableOfContents("0000000000010", 0, skipExcl=True) == []
    assert theIndex.getTableOfContents("0000000000010", 1, skipExcl=True) == [
        ("0000000000014:T000001", 1, "New Novel", 15),
    ]
    assert theIndex.getTableOfContents("0000000000010", 2, skipExcl=True) == [
        ("0000000000014:T000001", 1, "New Novel", 5),
        ("0000000000016:T000001", 2, "New Chapter", 4),
        ("%s:T000001" % hHandle, 2, "Chapter One", 6),
    ]
    assert theIndex.getTableOfContents("0000000000010", 3, skipExcl=True) == [
        ("0000000000014:T000001", 1, "New Novel", 5),
        ("0000000000016:T000001", 2, "New Chapter", 2),
        ("0000000000017:T000001", 3, "New Scene", 2),
        ("%s:T000001" % hHandle, 2, "Chapter One", 2),
        ("%s:T000001" % sHandle, 3, "Scene One", 2),
        ("%s:T000001" % tHandle, 3, "Scene Two", 2),
    ]

    assert theIndex.getTableOfContents("0000000000010", 0, skipExcl=False) == []
    assert theIndex.getTableOfContents("0000000000010", 1, skipExcl=False) == [
        ("0000000000014:T000001", 1, "New Novel", 9),
        ("%s:T000001" % nHandle, 1, "Hello World!", 12),
        ("%s:T000011" % nHandle, 1, "Hello World!", 22),
    ]

    # Header Word Counts
    bHandle = "0000000000000"
    assert theIndex.getHandleWordCounts(bHandle) == []
    assert theIndex.getHandleWordCounts(hHandle) == [("%s:T000001" % hHandle, 2)]
    assert theIndex.getHandleWordCounts(sHandle) == [("%s:T000001" % sHandle, 2)]
    assert theIndex.getHandleWordCounts(tHandle) == [("%s:T000001" % tHandle, 2)]
    assert theIndex.getHandleWordCounts(nHandle) == [
        ("%s:T000001" % nHandle, 12), ("%s:T000011" % nHandle, 16)
    ]

    assert theIndex.saveIndex() is True
    assert theProject.saveProject() is True
    assert theProject.closeProject() is True

    # Header Record
    bHandle = "0000000000000"
    assert theIndex.getHandleHeaders(bHandle) == []
    assert theIndex.getHandleHeaders(hHandle) == [("T000001", "H2", "Chapter One")]
    assert theIndex.getHandleHeaders(sHandle) == [("T000001", "H3", "Scene One")]
    assert theIndex.getHandleHeaders(tHandle) == [("T000001", "H3", "Scene Two")]
    assert theIndex.getHandleHeaders(nHandle) == [
        ("T000001", "H1", "Hello World!"), ("T000011", "H1", "Hello World!")
    ]

# END Test testCoreIndex_ExtractData


@pytest.mark.core
def testCoreIndex_TagsIndex():
    """Check the TagsIndex class.
    """
    tagsIndex = TagsIndex()
    assert tagsIndex._tags == {}

    # Expected data
    content = {
        "Tag1": {
            "handle": "0000000000001",
            "heading": "T000001",
            "class": nwItemClass.NOVEL.name,
        },
        "Tag2": {
            "handle": "0000000000002",
            "heading": "T000002",
            "class": nwItemClass.CHARACTER.name,
        },
        "Tag3": {
            "handle": "0000000000003",
            "heading": "T000003",
            "class": nwItemClass.PLOT.name,
        },
    }

    # Add data
    tagsIndex.add("Tag1", "0000000000001", "T000001", nwItemClass.NOVEL)
    tagsIndex.add("Tag2", "0000000000002", "T000002", nwItemClass.CHARACTER)
    tagsIndex.add("Tag3", "0000000000003", "T000003", nwItemClass.PLOT)
    assert tagsIndex._tags == content

    # Get items
    assert tagsIndex["Tag1"] == content["Tag1"]
    assert tagsIndex["Tag2"] == content["Tag2"]
    assert tagsIndex["Tag3"] == content["Tag3"]
    assert tagsIndex["Tag4"] is None

    # Contains
    assert "Tag1" in tagsIndex
    assert "Tag2" in tagsIndex
    assert "Tag3" in tagsIndex
    assert "Tag4" not in tagsIndex

    # Read back handles
    assert tagsIndex.tagHandle("Tag1") == "0000000000001"
    assert tagsIndex.tagHandle("Tag2") == "0000000000002"
    assert tagsIndex.tagHandle("Tag3") == "0000000000003"
    assert tagsIndex.tagHandle("Tag4") is None

    # Read back headings
    assert tagsIndex.tagHeading("Tag1") == "T000001"
    assert tagsIndex.tagHeading("Tag2") == "T000002"
    assert tagsIndex.tagHeading("Tag3") == "T000003"
    assert tagsIndex.tagHeading("Tag4") == "T000000"

    # Read back classes
    assert tagsIndex.tagClass("Tag1") == nwItemClass.NOVEL.name
    assert tagsIndex.tagClass("Tag2") == nwItemClass.CHARACTER.name
    assert tagsIndex.tagClass("Tag3") == nwItemClass.PLOT.name
    assert tagsIndex.tagClass("Tag4") is None

    # Pack Data
    assert tagsIndex.packData() == content

    # Delete the second key and a nomn-existant key
    del tagsIndex["Tag2"]
    del tagsIndex["Tag4"]
    assert "Tag1" in tagsIndex
    assert "Tag2" not in tagsIndex
    assert "Tag3" in tagsIndex
    assert "Tag4" not in tagsIndex

    # Clear and reload
    tagsIndex.clear()
    assert tagsIndex._tags == {}
    assert tagsIndex.packData() == {}

    tagsIndex.unpackData(content)
    assert tagsIndex._tags == content
    assert tagsIndex.packData() == content

    # Unpack Errors
    # =============
    tagsIndex.clear()

    # Invalid data type
    with pytest.raises(ValueError):
        tagsIndex.unpackData([])

    # Invalid key
    with pytest.raises(ValueError):
        tagsIndex.unpackData({
            1234: {
                "handle": "0000000000001",
                "heading": "T000001",
                "class": "NOVEL",
            }
        })

    # Missing handle
    with pytest.raises(KeyError):
        tagsIndex.unpackData({
            "Tag1": {
                "heading": "T000001",
                "class": "NOVEL",
            }
        })

    # Missing heading
    with pytest.raises(KeyError):
        tagsIndex.unpackData({
            "Tag1": {
                "handle": "0000000000001",
                "class": "NOVEL",
            }
        })

    # Missing class
    with pytest.raises(KeyError):
        tagsIndex.unpackData({
            "Tag1": {
                "handle": "0000000000001",
                "heading": "T000001",
            }
        })

    # Invalid handle
    with pytest.raises(ValueError):
        tagsIndex.unpackData({
            "Tag1": {
                "handle": "blablabla",
                "heading": "T000001",
                "class": "NOVEL",
            }
        })

    # Invalid heading
    with pytest.raises(ValueError):
        tagsIndex.unpackData({
            "Tag1": {
                "handle": "0000000000001",
                "heading": "blabla",
                "class": "NOVEL",
            }
        })

    # Invalid class
    with pytest.raises(ValueError):
        tagsIndex.unpackData({
            "Tag1": {
                "handle": "0000000000001",
                "heading": "T000001",
                "class": "blabla",
            }
        })

# END Test testCoreIndex_TagsIndex


@pytest.mark.core
def testCoreIndex_ItemIndex(mockGUI, fncDir, mockRnd):
    """Check the ItemIndex class.
    """
    theProject = NWProject(mockGUI)
    buildTestProject(theProject, fncDir)

    nHandle = "0000000000014"
    cHandle = "0000000000016"
    sHandle = "0000000000017"

    assert theProject.index.saveIndex() is True
    itemIndex = theProject.index._itemIndex

    # The index should be empty
    assert nHandle not in itemIndex
    assert cHandle not in itemIndex
    assert sHandle not in itemIndex

    # Add Items
    # =========
    assert cHandle not in itemIndex

    # Add the novel chapter file
    itemIndex.add(cHandle, theProject.tree[cHandle])
    assert cHandle in itemIndex
    assert itemIndex[cHandle].item == theProject.tree[cHandle]
    assert itemIndex.mainItemHeader(cHandle) == "H0"
    assert itemIndex.allItemTags(cHandle) == []
    assert list(itemIndex.iterItemHeaders(cHandle))[0][0] == "T000000"

    # Add a heading to the item, which should replace the T000000 heading
    itemIndex.addItemHeading(cHandle, "T000001", "H2", "Chapter One")
    assert itemIndex.mainItemHeader(cHandle) == "H2"
    assert list(itemIndex.iterItemHeaders(cHandle))[0][0] == "T000001"

    # Set the remainig data values
    itemIndex.setHeadingCounts(cHandle, "T000001", 60, 10, 2)
    itemIndex.setHeadingSynopsis(cHandle, "T000001", "In the beginning ...")
    itemIndex.setHeadingTag(cHandle, "T000001", "One")
    itemIndex.addHeadingReferences(cHandle, "T000001", ["Jane"], "@pov")
    itemIndex.addHeadingReferences(cHandle, "T000001", ["Jane"], "@focus")
    itemIndex.addHeadingReferences(cHandle, "T000001", ["Jane", "John"], "@char")
    idxData = itemIndex.packData()

    assert idxData[cHandle]["level"] == "H2"
    assert idxData[cHandle]["headings"]["T000001"] == {
        "level": "H2", "title": "Chapter One", "tag": "One",
        "cCount": 60, "wCount": 10, "pCount": 2, "synopsis": "In the beginning ...",
    }
    assert "@pov" in idxData[cHandle]["references"]["T000001"]["Jane"]
    assert "@focus" in idxData[cHandle]["references"]["T000001"]["Jane"]
    assert "@char" in idxData[cHandle]["references"]["T000001"]["Jane"]
    assert "@char" in idxData[cHandle]["references"]["T000001"]["John"]

    # Add the other two files
    itemIndex.add(nHandle, theProject.tree[nHandle])
    itemIndex.add(sHandle, theProject.tree[sHandle])
    itemIndex.addItemHeading(nHandle, "T000001", "H1", "Novel")
    itemIndex.addItemHeading(sHandle, "T000001", "H3", "Scene One")

    # Check Item and Heading Direct Access
    # ====================================

    # Check repr strings
    assert repr(itemIndex[nHandle]) == f"<IndexItem handle='{nHandle}'>"
    assert repr(itemIndex[nHandle]["T000001"]) == "<IndexHeading key='T000001'>"

    # Check content of a single item
    assert "T000001" in itemIndex[nHandle]
    assert itemIndex[cHandle].allTags() == ["One"]

    # Check the content of a single heading
    assert itemIndex[cHandle]["T000001"].key == "T000001"
    assert itemIndex[cHandle]["T000001"].level == "H2"
    assert itemIndex[cHandle]["T000001"].title == "Chapter One"
    assert itemIndex[cHandle]["T000001"].tag == "One"
    assert itemIndex[cHandle]["T000001"].charCount == 60
    assert itemIndex[cHandle]["T000001"].wordCount == 10
    assert itemIndex[cHandle]["T000001"].paraCount == 2
    assert itemIndex[cHandle]["T000001"].synopsis == "In the beginning ..."
    assert "Jane" in itemIndex[cHandle]["T000001"].references
    assert "John" in itemIndex[cHandle]["T000001"].references

    # Check heading level setter
    itemIndex[cHandle]["T000001"].setLevel("H3")  # Change it
    assert itemIndex[cHandle]["T000001"].level == "H3"
    itemIndex[cHandle]["T000001"].setLevel("H2")  # Set it back
    assert itemIndex[cHandle]["T000001"].level == "H2"
    itemIndex[cHandle]["T000001"].setLevel("H5")  # Invalid level
    assert itemIndex[cHandle]["T000001"].level == "H2"

    # Data Extraction
    # ===============

    # Get headers
    allHeads = list(itemIndex.iterAllHeaders())
    assert allHeads[0][0] == cHandle
    assert allHeads[1][0] == nHandle
    assert allHeads[2][0] == sHandle
    assert allHeads[0][1] == "T000001"
    assert allHeads[1][1] == "T000001"
    assert allHeads[2][1] == "T000001"

    # Ask for stuff that doesn't exist
    assert itemIndex.mainItemHeader("blablabla") == "H0"
    assert itemIndex.allItemTags("blablabla") == []

    # Novel Structure
    # ===============

    # Add a second novel
    mHandle = theProject.newRoot(nwItemClass.NOVEL)
    uHandle = theProject.newFile("Title Page", mHandle)
    itemIndex.add(uHandle, theProject.tree[uHandle])
    itemIndex.addItemHeading(uHandle, "T000001", "H1", "Novel 2")
    assert uHandle in itemIndex

    # Structure of all novels
    nStruct = list(itemIndex.iterNovelStructure())
    assert len(nStruct) == 4
    assert nStruct[0][0] == nHandle
    assert nStruct[1][0] == cHandle
    assert nStruct[2][0] == sHandle
    assert nStruct[3][0] == uHandle

    # Novel structure with root handle set
    nStruct = list(itemIndex.iterNovelStructure(rootHandle="0000000000010"))
    assert len(nStruct) == 3
    assert nStruct[0][0] == nHandle
    assert nStruct[1][0] == cHandle
    assert nStruct[2][0] == sHandle

    nStruct = list(itemIndex.iterNovelStructure(rootHandle=mHandle))
    assert len(nStruct) == 1
    assert nStruct[0][0] == uHandle

    # Inject garbage into tree
    theProject.tree._treeOrder.append("stuff")
    nStruct = list(itemIndex.iterNovelStructure())
    assert len(nStruct) == 4
    assert nStruct[0][0] == nHandle
    assert nStruct[1][0] == cHandle
    assert nStruct[2][0] == sHandle
    assert nStruct[3][0] == uHandle

    # Skip excluded
    theProject.tree[sHandle].setExported(False)
    nStruct = list(itemIndex.iterNovelStructure(skipExcl=True))
    assert len(nStruct) == 3
    assert nStruct[0][0] == nHandle
    assert nStruct[1][0] == cHandle
    assert nStruct[2][0] == uHandle

    # Delete new item
    del itemIndex[uHandle]
    assert uHandle not in itemIndex

    # Unpack Error Handling
    # =====================

    # Pack/unpack should restore state
    content = itemIndex.packData()
    itemIndex.clear()
    itemIndex.unpackData(content)
    assert itemIndex.packData() == content
    itemIndex.clear()

    # Data must be dictionary
    with pytest.raises(ValueError):
        itemIndex.unpackData("stuff")

    # Keys must be valid handles
    with pytest.raises(ValueError):
        itemIndex.unpackData({"stuff": "more stuff"})

    # Unknown keys should be skipped
    itemIndex.unpackData({"0000000000000": {}})
    assert itemIndex._items == {}

    # Known keys can be added, even witout data
    itemIndex.unpackData({nHandle: {}})
    assert nHandle in itemIndex

    # Title tags must be valid
    with pytest.raises(ValueError):
        itemIndex.unpackData({cHandle: {"headings": {"TTTTTTT": {}}}})

    # Reference without a heading should be rejected
    itemIndex.unpackData({
        cHandle: {
            "headings": {"T000001": {}},
            "references": {"T000001": {}, "T000002": {}},
        }
    })
    assert "T000001" in itemIndex[cHandle]
    assert "T000002" not in itemIndex[cHandle]
    itemIndex.clear()

    # Tag keys must be strings
    with pytest.raises(ValueError):
        itemIndex.unpackData({
            cHandle: {
                "headings": {"T000001": {}},
                "references": {"T000001": {1234: "@pov"}},
            }
        })

    # Type must be strings
    with pytest.raises(ValueError):
        itemIndex.unpackData({
            cHandle: {
                "headings": {"T000001": {}},
                "references": {"T000001": {"John": []}},
            }
        })

    # Types must be valid
    with pytest.raises(ValueError):
        itemIndex.unpackData({
            cHandle: {
                "headings": {"T000001": {}},
                "references": {"T000001": {"John": "@pov,@char,@stuff"}},
            }
        })

    # This should pass
    itemIndex.unpackData({
        cHandle: {
            "headings": {"T000001": {}},
            "references": {"T000001": {"John": "@pov,@char"}},
        }
    })

# END Test testCoreIndex_ItemIndex


@pytest.mark.core
def testCoreIndex_CountWords():
    """Test the word counter and the exclusion filers.
    """
    # Non-Text
    assert countWords(None) == (0, 0, 0)
    assert countWords(1234) == (0, 0, 0)

    # General Text
    cC, wC, pC = countWords((
        "# Heading One\n"
        "## Heading Two\n"
        "### Heading Three\n"
        "#### Heading Four\n\n"
        "@tag: value\n\n"
        "% A comment that should not be counted.\n\n"
        "The first paragraph.\n\n"
        "The second paragraph.\n\n\n"
        "The third paragraph.\n\n"
        "Dashes\u2013and even longer\u2014dashes."
    ))
    assert cC == 138
    assert wC == 22
    assert pC == 4

    # Text Alignment
    cC, wC, pC = countWords((
        "# Title\n\n"
        "Left aligned<<\n\n"
        "Left aligned <<\n\n"
        "Right indent<\n\n"
        "Right indent <\n\n"
    ))
    assert cC == 53
    assert wC == 9
    assert pC == 4

    cC, wC, pC = countWords((
        "# Title\n\n"
        ">>Right aligned\n\n"
        ">> Right aligned\n\n"
        ">Left indent\n\n"
        "> Left indent\n\n"
    ))
    assert cC == 53
    assert wC == 9
    assert pC == 4

    cC, wC, pC = countWords((
        "# Title\n\n"
        ">>Centre aligned<<\n\n"
        ">> Centre aligned <<\n\n"
        ">Double indent<\n\n"
        "> Double indent <\n\n"
    ))
    assert cC == 59
    assert wC == 9
    assert pC == 4

    # Formatting Codes
    cC, wC, pC = countWords((
        "Some text\n\n"
        "[NEWPAGE]\n\n"
        "more text\n\n"
        "[NEW PAGE]]\n\n"
        "even more text\n\n"
        "[VSPACE]\n\n"
        "and some final text\n\n"
        "[VSPACE:4]\n\n"
        "THE END\n\n"
    ))
    assert cC == 58
    assert wC == 13
    assert pC == 5

# END Test testCoreIndex_CountWords
