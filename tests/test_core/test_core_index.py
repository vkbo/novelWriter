"""
novelWriter – NWIndex Class Tester
==================================

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

import json
import pytest

from shutil import copyfile

from mocked import causeException
from tools import C, buildTestProject, cmpFiles, writeFile

from novelwriter.enum import nwItemClass, nwItemLayout
from novelwriter.constants import nwFiles
from novelwriter.core.index import IndexItem, NWIndex, countWords, TagsIndex
from novelwriter.core.project import NWProject


@pytest.mark.core
def testCoreIndex_LoadSave(monkeypatch, prjLipsum, mockGUI, tstPaths):
    """Test core functionality of scanning, saving, loading and checking
    the index cache file.
    """
    projFile = prjLipsum / "meta" / nwFiles.INDEX_FILE
    testFile = tstPaths.outDir / "coreIndex_LoadSave_tagsIndex.json"
    compFile = tstPaths.refDir / "coreIndex_LoadSave_tagsIndex.json"

    theProject = NWProject()
    assert theProject.openProject(prjLipsum)

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

    # No folder for saving
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.storage.NWStorage.getMetaFile", lambda *a: None)
        assert theIndex.saveIndex() is False

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

    # No folder for loading
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.storage.NWStorage.getMetaFile", lambda *a: None)
        assert theIndex.loadIndex() is False

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

    # Rebuild index
    theIndex.clearIndex()
    theIndex.rebuildIndex()

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
    writeFile(projFile, '{"novelWriter.tagsIndex": {}, "novelWriter.itemIndex": {}}')
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
    theProject.closeProject()

# END Test testCoreIndex_LoadSave


@pytest.mark.core
def testCoreIndex_ScanThis(mockGUI):
    """Test the tag scanner function scanThis."""
    theProject = NWProject()
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

    theProject.closeProject()

# END Test testCoreIndex_ScanThis


@pytest.mark.core
def testCoreIndex_CheckThese(mockGUI, fncPath, mockRnd):
    """Test the tag checker function checkThese.
    """
    theProject = NWProject()
    mockRnd.reset()
    buildTestProject(theProject, fncPath)
    theIndex = theProject.index
    theIndex.clearIndex()

    nHandle = theProject.newFile("Hello", C.hNovelRoot)
    cHandle = theProject.newFile("Jane",  C.hCharRoot)
    nItem = theProject.tree[nHandle]
    cItem = theProject.tree[cHandle]

    assert theIndex.rootChangedSince(C.hNovelRoot, 0) is False
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
    assert theIndex._tagsIndex.tagHeading("Jane") == "T0001"
    assert theIndex._tagsIndex.tagClass("Jane") == "CHARACTER"
    assert theIndex.getItemHeader(nHandle, "T0001").title == "Hello World!"
    assert theIndex.getReferences(nHandle, "T0001") == {
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

    assert theIndex.rootChangedSince(C.hNovelRoot, 0) is True
    assert theIndex.indexChangedSince(0) is True

    assert cItem.mainHeading == "H1"
    assert nItem.mainHeading == "H1"

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

    theProject.closeProject()

# END Test testCoreIndex_CheckThese


@pytest.mark.core
def testCoreIndex_ScanText(mockGUI, fncPath, mockRnd):
    """Check the index text scanner."""
    theProject = NWProject()
    mockRnd.reset()
    buildTestProject(theProject, fncPath)
    theIndex = theProject.index

    # Some items for fail to scan tests
    dHandle = theProject.newFolder("Folder", C.hNovelRoot)
    xHandle = theProject.newFile("No Layout", C.hNovelRoot)
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
    assert theIndex.scanText(xHandle, "## Hello World!") is True
    assert xItem.mainHeading == "H2"

    # Create the archive root
    aHandle = theProject.newRoot(nwItemClass.ARCHIVE)
    assert theProject.tree[aHandle] is not None
    xItem.setParent(aHandle)
    theProject.tree.updateItemData(xItem.itemHandle)
    assert theIndex.scanText(xHandle, "### Hello World!") is True
    assert xItem.mainHeading == "H3"

    # Make some usable items
    tHandle = theProject.newFile("Title", C.hNovelRoot)
    pHandle = theProject.newFile("Page",  C.hNovelRoot)
    nHandle = theProject.newFile("Hello", C.hNovelRoot)
    cHandle = theProject.newFile("Jane",  C.hCharRoot)
    sHandle = theProject.newFile("Scene", C.hNovelRoot)

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
    assert theIndex._tagsIndex.tagHeading("Jane") == "T0001"
    assert theIndex._tagsIndex.tagClass("Jane") == "CHARACTER"
    assert theIndex.getItemHeader(nHandle, "T0001").title == "Hello World!"

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
    assert theIndex._itemIndex[nHandle]["T0001"].references == {}
    assert theIndex._itemIndex[nHandle]["T0002"].references == {}
    assert theIndex._itemIndex[nHandle]["T0003"].references == {}
    assert theIndex._itemIndex[nHandle]["T0004"].references == {}

    assert theIndex._itemIndex[nHandle]["T0001"].level == "H1"
    assert theIndex._itemIndex[nHandle]["T0002"].level == "H2"
    assert theIndex._itemIndex[nHandle]["T0003"].level == "H3"
    assert theIndex._itemIndex[nHandle]["T0004"].level == "H4"

    assert theIndex._itemIndex[nHandle]["T0001"].line == 1
    assert theIndex._itemIndex[nHandle]["T0002"].line == 7
    assert theIndex._itemIndex[nHandle]["T0003"].line == 13
    assert theIndex._itemIndex[nHandle]["T0004"].line == 19

    assert theIndex._itemIndex[nHandle]["T0001"].title == "Title One"
    assert theIndex._itemIndex[nHandle]["T0002"].title == "Title Two"
    assert theIndex._itemIndex[nHandle]["T0003"].title == "Title Three"
    assert theIndex._itemIndex[nHandle]["T0004"].title == "Title Four"

    assert theIndex._itemIndex[nHandle]["T0001"].charCount == 23
    assert theIndex._itemIndex[nHandle]["T0002"].charCount == 23
    assert theIndex._itemIndex[nHandle]["T0003"].charCount == 27
    assert theIndex._itemIndex[nHandle]["T0004"].charCount == 56

    assert theIndex._itemIndex[nHandle]["T0001"].wordCount == 4
    assert theIndex._itemIndex[nHandle]["T0002"].wordCount == 4
    assert theIndex._itemIndex[nHandle]["T0003"].wordCount == 4
    assert theIndex._itemIndex[nHandle]["T0004"].wordCount == 9

    assert theIndex._itemIndex[nHandle]["T0001"].paraCount == 1
    assert theIndex._itemIndex[nHandle]["T0002"].paraCount == 1
    assert theIndex._itemIndex[nHandle]["T0003"].paraCount == 1
    assert theIndex._itemIndex[nHandle]["T0004"].paraCount == 3

    assert theIndex._itemIndex[nHandle]["T0001"].synopsis == "Synopsis One."
    assert theIndex._itemIndex[nHandle]["T0002"].synopsis == "Synopsis Two."
    assert theIndex._itemIndex[nHandle]["T0003"].synopsis == "Synopsis Three."
    assert theIndex._itemIndex[nHandle]["T0004"].synopsis == "Synopsis Four."

    # Note File
    assert theIndex.scanText(cHandle, (
        "# Title One\n\n"
        "@tag: One\n\n"
        "% synopsis: Synopsis One.\n\n"
        "Paragraph One.\n\n"
    ))
    assert theIndex._itemIndex[cHandle]["T0001"].references == {}
    assert theIndex._itemIndex[cHandle]["T0001"].level == "H1"
    assert theIndex._itemIndex[cHandle]["T0001"].line == 1
    assert theIndex._itemIndex[cHandle]["T0001"].title == "Title One"
    assert theIndex._itemIndex[cHandle]["T0001"].charCount == 23
    assert theIndex._itemIndex[cHandle]["T0001"].wordCount == 4
    assert theIndex._itemIndex[cHandle]["T0001"].paraCount == 1
    assert theIndex._itemIndex[cHandle]["T0001"].synopsis == "Synopsis One."

    # Valid and Invalid References
    assert theIndex.scanText(sHandle, (
        "# Title One\n\n"
        "@pov: One\n\n"  # Valid
        "@char: Two\n\n"  # Invalid tag
        "@:\n\n"  # Invalid line
        "% synopsis: Synopsis One.\n\n"
        "Paragraph One.\n\n"
    ))
    assert theIndex._itemIndex[sHandle]["T0001"].references == {
        "One": {"@pov"}, "Two": {"@char"}
    }

    # Special Titles
    # ==============

    assert theIndex.scanText(tHandle, (
        "#! My Project\n\n"
        ">> By Jane Doe <<\n\n"
    ))
    assert theIndex._itemIndex[cHandle]["T0001"].references == {}
    assert theIndex._itemIndex[tHandle]["T0001"].level == "H1"
    assert theIndex._itemIndex[tHandle]["T0001"].line == 1
    assert theIndex._itemIndex[tHandle]["T0001"].title == "My Project"
    assert theIndex._itemIndex[tHandle]["T0001"].charCount == 21
    assert theIndex._itemIndex[tHandle]["T0001"].wordCount == 5
    assert theIndex._itemIndex[tHandle]["T0001"].paraCount == 1
    assert theIndex._itemIndex[tHandle]["T0001"].synopsis == ""

    assert theIndex.scanText(tHandle, (
        "##! Prologue\n\n"
        "In the beginning there was time ...\n\n"
    ))
    assert theIndex._itemIndex[cHandle]["T0001"].references == {}
    assert theIndex._itemIndex[tHandle]["T0001"].level == "H2"
    assert theIndex._itemIndex[tHandle]["T0001"].line == 1
    assert theIndex._itemIndex[tHandle]["T0001"].title == "Prologue"
    assert theIndex._itemIndex[tHandle]["T0001"].charCount == 43
    assert theIndex._itemIndex[tHandle]["T0001"].wordCount == 8
    assert theIndex._itemIndex[tHandle]["T0001"].paraCount == 1
    assert theIndex._itemIndex[tHandle]["T0001"].synopsis == ""

    # Page wo/Title
    # =============

    theProject.tree[pHandle]._layout = nwItemLayout.DOCUMENT
    assert theIndex.scanText(pHandle, (
        "This is a page with some text on it.\n\n"
    ))
    assert theIndex._itemIndex[pHandle]["T0000"].references == {}
    assert theIndex._itemIndex[pHandle]["T0000"].level == "H0"
    assert theIndex._itemIndex[pHandle]["T0000"].line == 0
    assert theIndex._itemIndex[pHandle]["T0000"].title == ""
    assert theIndex._itemIndex[pHandle]["T0000"].charCount == 36
    assert theIndex._itemIndex[pHandle]["T0000"].wordCount == 9
    assert theIndex._itemIndex[pHandle]["T0000"].paraCount == 1
    assert theIndex._itemIndex[pHandle]["T0000"].synopsis == ""

    theProject.tree[pHandle]._layout = nwItemLayout.NOTE
    assert theIndex.scanText(pHandle, (
        "This is a page with some text on it.\n\n"
    ))
    assert theIndex._itemIndex[pHandle]["T0000"].references == {}
    assert theIndex._itemIndex[pHandle]["T0000"].level == "H0"
    assert theIndex._itemIndex[pHandle]["T0000"].line == 0
    assert theIndex._itemIndex[pHandle]["T0000"].title == ""
    assert theIndex._itemIndex[pHandle]["T0000"].charCount == 36
    assert theIndex._itemIndex[pHandle]["T0000"].wordCount == 9
    assert theIndex._itemIndex[pHandle]["T0000"].paraCount == 1
    assert theIndex._itemIndex[pHandle]["T0000"].synopsis == ""

    theProject.closeProject()

# END Test testCoreIndex_ScanText


@pytest.mark.core
def testCoreIndex_ExtractData(mockGUI, fncPath, mockRnd):
    """Check the index data extraction functions."""
    theProject = NWProject()
    mockRnd.reset()
    buildTestProject(theProject, fncPath)

    theIndex = theProject.index
    theIndex.reIndexHandle(C.hNovelRoot)
    theIndex.reIndexHandle(C.hPlotRoot)
    theIndex.reIndexHandle(C.hCharRoot)
    theIndex.reIndexHandle(C.hWorldRoot)
    theIndex.reIndexHandle(C.hTitlePage)
    theIndex.reIndexHandle(C.hChapterDir)
    theIndex.reIndexHandle(C.hChapterDoc)
    theIndex.reIndexHandle(C.hSceneDoc)

    nHandle = theProject.newFile("Hello", C.hNovelRoot)
    cHandle = theProject.newFile("Jane",  C.hCharRoot)

    assert theIndex.getItemHeader("", "") is None
    assert theIndex.getItemHeader(C.hNovelRoot, "") is None

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
        f"{C.hTitlePage}:T0001",
        f"{C.hChapterDoc}:T0001",
        f"{C.hSceneDoc}:T0001",
        f"{nHandle}:T0001",
    ]

    # Check that excluded files can be skipped
    theProject.tree[nHandle].setActive(False)

    theKeys = []
    for aKey, _, _, _ in theIndex.novelStructure(skipExcl=False):
        theKeys.append(aKey)

    assert theKeys == [
        f"{C.hTitlePage}:T0001",
        f"{C.hChapterDoc}:T0001",
        f"{C.hSceneDoc}:T0001",
        f"{nHandle}:T0001",
    ]

    theKeys = []
    for aKey, _, _, _ in theIndex.novelStructure(skipExcl=True):
        theKeys.append(aKey)

    assert theKeys == [
        f"{C.hTitlePage}:T0001",
        f"{C.hChapterDoc}:T0001",
        f"{C.hSceneDoc}:T0001",
    ]

    # The novel file should have the correct counts
    cC, wC, pC = theIndex.getCounts(nHandle)
    assert cC == 62  # Characters in text and title only
    assert wC == 12  # Words in text and title only
    assert pC == 2   # Paragraphs in text only

    # getItemData + getHandleHeaderCount
    # ==================================

    theItem = theIndex.getItemData(nHandle)
    assert isinstance(theItem, IndexItem)
    assert theItem.headings() == ["T0001"]
    assert theIndex.getHandleHeaderCount(nHandle) == 1

    # getReferences
    # =============

    # Look up an invalid handle
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
    assert theIndex.getBackReferenceList(C.hTitlePage) == {}

    # The character file should have a record of the reference from the novel file
    theRefs = theIndex.getBackReferenceList(cHandle)
    assert theRefs == {nHandle: "T0001"}

    # getTagSource
    # ============

    assert theIndex.getTagSource("Jane") == (cHandle, "T0001")
    assert theIndex.getTagSource("John") == (None, "T0000")

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
    cC, wC, pC = theIndex.getCounts(nHandle, "T0001")
    assert cC == 62
    assert wC == 12
    assert pC == 2

    # Second part
    cC, wC, pC = theIndex.getCounts(nHandle, "T0002")
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
    cC, wC, pC = theIndex.getCounts(cHandle, "T0001")
    assert cC == 62
    assert wC == 12
    assert pC == 2

    # Second part
    cC, wC, pC = theIndex.getCounts(cHandle, "T0002")
    assert cC == 90
    assert wC == 16
    assert pC == 2

    # Novel Stats
    # ===========

    hHandle = theProject.newFile("Chapter", C.hNovelRoot)
    sHandle = theProject.newFile("Scene One", C.hNovelRoot)
    tHandle = theProject.newFile("Scene Two", C.hNovelRoot)

    theProject.tree[hHandle].itemLayout == nwItemLayout.DOCUMENT
    theProject.tree[sHandle].itemLayout == nwItemLayout.DOCUMENT
    theProject.tree[tHandle].itemLayout == nwItemLayout.DOCUMENT

    assert theIndex.scanText(hHandle, "## Chapter One\n\n")
    assert theIndex.scanText(sHandle, "### Scene One\n\n")
    assert theIndex.scanText(tHandle, "### Scene Two\n\n")

    assert [(h, t) for h, t, _ in theIndex._itemIndex.iterNovelStructure(skipExcl=False)] == [
        (C.hTitlePage, "T0001"),
        (C.hChapterDoc, "T0001"),
        (C.hSceneDoc, "T0001"),
        (nHandle, "T0001"),
        (nHandle, "T0002"),
        (hHandle, "T0001"),
        (sHandle, "T0001"),
        (tHandle, "T0001"),
    ]

    assert [(h, t) for h, t, _ in theIndex._itemIndex.iterNovelStructure(skipExcl=True)] == [
        (C.hTitlePage, "T0001"),
        (C.hChapterDoc, "T0001"),
        (C.hSceneDoc, "T0001"),
        (hHandle, "T0001"),
        (sHandle, "T0001"),
        (tHandle, "T0001"),
    ]

    # Add a fake handle to the tree and check that it's ignored
    theProject.tree._order.append("0000000000000")
    assert [(h, t) for h, t, _ in theIndex._itemIndex.iterNovelStructure(skipExcl=False)] == [
        (C.hTitlePage, "T0001"),
        (C.hChapterDoc, "T0001"),
        (C.hSceneDoc, "T0001"),
        (nHandle, "T0001"),
        (nHandle, "T0002"),
        (hHandle, "T0001"),
        (sHandle, "T0001"),
        (tHandle, "T0001"),
    ]
    theProject.tree._order.remove("0000000000000")

    # Extract stats
    assert theIndex.getNovelWordCount(skipExcl=False) == 43
    assert theIndex.getNovelWordCount(skipExcl=True) == 15
    assert theIndex.getNovelTitleCounts(skipExcl=False) == [0, 3, 2, 3, 0]
    assert theIndex.getNovelTitleCounts(skipExcl=True) == [0, 1, 2, 3, 0]

    # Table of Contents
    assert theIndex.getTableOfContents(C.hNovelRoot, 0, skipExcl=True) == []
    assert theIndex.getTableOfContents(C.hNovelRoot, 1, skipExcl=True) == [
        (f"{C.hTitlePage}:T0001", 1, "New Novel", 15),
    ]
    assert theIndex.getTableOfContents(C.hNovelRoot, 2, skipExcl=True) == [
        (f"{C.hTitlePage}:T0001", 1, "New Novel", 5),
        (f"{C.hChapterDoc}:T0001", 2, "New Chapter", 4),
        (f"{hHandle}:T0001", 2, "Chapter One", 6),
    ]
    assert theIndex.getTableOfContents(C.hNovelRoot, 3, skipExcl=True) == [
        (f"{C.hTitlePage}:T0001", 1, "New Novel", 5),
        (f"{C.hChapterDoc}:T0001", 2, "New Chapter", 2),
        (f"{C.hSceneDoc}:T0001", 3, "New Scene", 2),
        (f"{hHandle}:T0001", 2, "Chapter One", 2),
        (f"{sHandle}:T0001", 3, "Scene One", 2),
        (f"{tHandle}:T0001", 3, "Scene Two", 2),
    ]

    assert theIndex.getTableOfContents(C.hNovelRoot, 0, skipExcl=False) == []
    assert theIndex.getTableOfContents(C.hNovelRoot, 1, skipExcl=False) == [
        (f"{C.hTitlePage}:T0001", 1, "New Novel", 9),
        (f"{nHandle}:T0001", 1, "Hello World!", 12),
        (f"{nHandle}:T0002", 1, "Hello World!", 22),
    ]

    assert theIndex.saveIndex() is True
    assert theProject.saveProject() is True
    theProject.closeProject()

# END Test testCoreIndex_ExtractData


@pytest.mark.core
def testCoreIndex_TagsIndex():
    """Check the TagsIndex class."""
    tagsIndex = TagsIndex()
    assert tagsIndex._tags == {}

    # Expected data
    content = {
        "Tag1": {
            "handle": "0000000000001",
            "heading": "T0001",
            "class": nwItemClass.NOVEL.name,
        },
        "Tag2": {
            "handle": "0000000000002",
            "heading": "T0002",
            "class": nwItemClass.CHARACTER.name,
        },
        "Tag3": {
            "handle": "0000000000003",
            "heading": "T0003",
            "class": nwItemClass.PLOT.name,
        },
    }

    # Add data
    tagsIndex.add("Tag1", "0000000000001", "T0001", nwItemClass.NOVEL)
    tagsIndex.add("Tag2", "0000000000002", "T0002", nwItemClass.CHARACTER)
    tagsIndex.add("Tag3", "0000000000003", "T0003", nwItemClass.PLOT)
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
    assert tagsIndex.tagHeading("Tag1") == "T0001"
    assert tagsIndex.tagHeading("Tag2") == "T0002"
    assert tagsIndex.tagHeading("Tag3") == "T0003"
    assert tagsIndex.tagHeading("Tag4") == "T0000"

    # Read back classes
    assert tagsIndex.tagClass("Tag1") == nwItemClass.NOVEL.name
    assert tagsIndex.tagClass("Tag2") == nwItemClass.CHARACTER.name
    assert tagsIndex.tagClass("Tag3") == nwItemClass.PLOT.name
    assert tagsIndex.tagClass("Tag4") is None

    # Pack Data
    assert tagsIndex.packData() == content

    # Delete the second key and a non-existant key
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
                "heading": "T0001",
                "class": "NOVEL",
            }
        })

    # Missing handle
    with pytest.raises(KeyError):
        tagsIndex.unpackData({
            "Tag1": {
                "heading": "T0001",
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
                "heading": "T0001",
            }
        })

    # Invalid handle
    with pytest.raises(ValueError):
        tagsIndex.unpackData({
            "Tag1": {
                "handle": "blablabla",
                "heading": "T0001",
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
                "heading": "T0001",
                "class": "blabla",
            }
        })

# END Test testCoreIndex_TagsIndex


@pytest.mark.core
def testCoreIndex_ItemIndex(mockGUI, fncPath, mockRnd):
    """Check the ItemIndex class."""
    theProject = NWProject()
    mockRnd.reset()
    buildTestProject(theProject, fncPath)
    theProject.index.clearIndex()

    nHandle = C.hTitlePage
    cHandle = C.hChapterDoc
    sHandle = C.hSceneDoc

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
    assert itemIndex.allItemTags(cHandle) == []
    assert list(itemIndex.iterItemHeaders(cHandle))[0][0] == "T0000"

    # Add a heading to the item, which should replace the T000000 heading
    assert itemIndex.addItemHeading(cHandle, 1, "H2", "Chapter One") == "T0001"
    assert list(itemIndex.iterItemHeaders(cHandle))[0][0] == "T0001"

    # Add a heading to an invalid item
    assert itemIndex.addItemHeading(C.hInvalid, 1, "H1", "Stuff") == "T0000"

    # Set the remaining data values
    itemIndex.setHeadingCounts(cHandle, "T0001", 60, 10, 2)
    itemIndex.setHeadingSynopsis(cHandle, "T0001", "In the beginning ...")
    itemIndex.setHeadingTag(cHandle, "T0001", "One")
    itemIndex.addHeadingReferences(cHandle, "T0001", ["Jane"], "@pov")
    itemIndex.addHeadingReferences(cHandle, "T0001", ["Jane"], "@focus")
    itemIndex.addHeadingReferences(cHandle, "T0001", ["Jane", "John"], "@char")
    idxData = itemIndex.packData()

    assert idxData[cHandle]["headings"]["T0001"] == {
        "level": "H2", "line": 1, "title": "Chapter One", "tag": "One",
        "cCount": 60, "wCount": 10, "pCount": 2, "synopsis": "In the beginning ...",
    }
    assert "@pov" in idxData[cHandle]["references"]["T0001"]["Jane"]
    assert "@focus" in idxData[cHandle]["references"]["T0001"]["Jane"]
    assert "@char" in idxData[cHandle]["references"]["T0001"]["Jane"]
    assert "@char" in idxData[cHandle]["references"]["T0001"]["John"]

    # Add the other two files
    itemIndex.add(nHandle, theProject.tree[nHandle])
    itemIndex.add(sHandle, theProject.tree[sHandle])
    itemIndex.addItemHeading(nHandle, 1, "H1", "Novel")
    itemIndex.addItemHeading(sHandle, 1, "H3", "Scene One")

    # Check Item and Heading Direct Access
    # ====================================

    # Check repr strings
    assert repr(itemIndex[nHandle]) == f"<IndexItem handle='{nHandle}'>"
    assert repr(itemIndex[nHandle]["T0001"]) == "<IndexHeading key='T0001'>"

    # Check content of a single item
    assert "T0001" in itemIndex[nHandle]
    assert itemIndex[cHandle].allTags() == ["One"]

    # Check the content of a single heading
    assert itemIndex[cHandle]["T0001"].key == "T0001"
    assert itemIndex[cHandle]["T0001"].level == "H2"
    assert itemIndex[cHandle]["T0001"].line == 1
    assert itemIndex[cHandle]["T0001"].title == "Chapter One"
    assert itemIndex[cHandle]["T0001"].tag == "One"
    assert itemIndex[cHandle]["T0001"].charCount == 60
    assert itemIndex[cHandle]["T0001"].wordCount == 10
    assert itemIndex[cHandle]["T0001"].paraCount == 2
    assert itemIndex[cHandle]["T0001"].synopsis == "In the beginning ..."
    assert "Jane" in itemIndex[cHandle]["T0001"].references
    assert "John" in itemIndex[cHandle]["T0001"].references

    # Check heading level setter
    itemIndex[cHandle]["T0001"].setLevel("H3")  # Change it
    assert itemIndex[cHandle]["T0001"].level == "H3"
    itemIndex[cHandle]["T0001"].setLevel("H2")  # Set it back
    assert itemIndex[cHandle]["T0001"].level == "H2"
    itemIndex[cHandle]["T0001"].setLevel("H5")  # Invalid level
    assert itemIndex[cHandle]["T0001"].level == "H2"

    # Data Extraction
    # ===============

    # Get headers
    allHeads = list(itemIndex.iterAllHeaders())
    assert allHeads[0][0] == cHandle
    assert allHeads[1][0] == nHandle
    assert allHeads[2][0] == sHandle
    assert allHeads[0][1] == "T0001"
    assert allHeads[1][1] == "T0001"
    assert allHeads[2][1] == "T0001"

    # Ask for stuff that doesn't exist
    assert itemIndex.allItemTags("blablabla") == []

    # Novel Structure
    # ===============

    # Add a second novel
    mHandle = theProject.newRoot(nwItemClass.NOVEL)
    uHandle = theProject.newFile("Title Page", mHandle)
    itemIndex.add(uHandle, theProject.tree[uHandle])
    itemIndex.addItemHeading(uHandle, "T0001", "H1", "Novel 2")
    assert uHandle in itemIndex

    # Structure of all novels
    nStruct = list(itemIndex.iterNovelStructure())
    assert len(nStruct) == 4
    assert nStruct[0][0] == nHandle
    assert nStruct[1][0] == cHandle
    assert nStruct[2][0] == sHandle
    assert nStruct[3][0] == uHandle

    # Novel structure with root handle set
    nStruct = list(itemIndex.iterNovelStructure(rHandle=C.hNovelRoot))
    assert len(nStruct) == 3
    assert nStruct[0][0] == nHandle
    assert nStruct[1][0] == cHandle
    assert nStruct[2][0] == sHandle

    nStruct = list(itemIndex.iterNovelStructure(rHandle=mHandle))
    assert len(nStruct) == 1
    assert nStruct[0][0] == uHandle

    # Inject garbage into tree
    theProject.tree._order.append("stuff")
    nStruct = list(itemIndex.iterNovelStructure())
    assert len(nStruct) == 4
    assert nStruct[0][0] == nHandle
    assert nStruct[1][0] == cHandle
    assert nStruct[2][0] == sHandle
    assert nStruct[3][0] == uHandle

    # Skip excluded
    theProject.tree[sHandle].setActive(False)
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
    itemIndex.unpackData({C.hInvalid: {}})
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
            "headings": {"T0001": {}},
            "references": {"T0001": {}, "T0002": {}},
        }
    })
    assert "T0001" in itemIndex[cHandle]
    assert "T0002" not in itemIndex[cHandle]
    itemIndex.clear()

    # Tag keys must be strings
    with pytest.raises(ValueError):
        itemIndex.unpackData({
            cHandle: {
                "headings": {"T0001": {}},
                "references": {"T0001": {1234: "@pov"}},
            }
        })

    # Type must be strings
    with pytest.raises(ValueError):
        itemIndex.unpackData({
            cHandle: {
                "headings": {"T0001": {}},
                "references": {"T0001": {"John": []}},
            }
        })

    # Types must be valid
    with pytest.raises(ValueError):
        itemIndex.unpackData({
            cHandle: {
                "headings": {"T0001": {}},
                "references": {"T0001": {"John": "@pov,@char,@stuff"}},
            }
        })

    # This should pass
    itemIndex.unpackData({
        cHandle: {
            "headings": {"T0001": {}},
            "references": {"T0001": {"John": "@pov,@char"}},
        }
    })

# END Test testCoreIndex_ItemIndex


@pytest.mark.core
def testCoreIndex_CountWords():
    """Test the word counter and the exclusion filers."""
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
