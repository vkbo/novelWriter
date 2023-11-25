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
from __future__ import annotations

import json
import pytest

from shutil import copyfile

from mocked import causeException
from novelwriter.core.item import NWItem
from tools import C, buildTestProject, cmpFiles, writeFile

from novelwriter.enum import nwComment, nwItemClass, nwItemLayout
from novelwriter.constants import nwFiles
from novelwriter.core.index import IndexItem, NWIndex, countWords, TagsIndex, processComment
from novelwriter.core.project import NWProject


@pytest.mark.core
def testCoreIndex_LoadSave(monkeypatch, prjLipsum, mockGUI, tstPaths):
    """Test core functionality of scanning, saving, loading and checking
    the index cache file.
    """
    projFile = prjLipsum / "meta" / nwFiles.INDEX_FILE
    testFile = tstPaths.outDir / "coreIndex_LoadSave_tagsIndex.json"
    compFile = tstPaths.refDir / "coreIndex_LoadSave_tagsIndex.json"

    project = NWProject()
    assert project.openProject(prjLipsum)

    index = NWIndex(project)
    assert repr(index) == "<NWIndex project='Lorem Ipsum'>"

    notIndexable = {
        "b3643d0f92e32": False,  # Novel ROOT
        "45e6b01ca35c1": False,  # Chapter One FOLDER
        "6bd935d2490cd": False,  # Chapter Two FOLDER
        "67a8707f2f249": False,  # Character ROOT
        "6c6afb1247750": False,  # Plot ROOT
        "60bdf227455cc": False,  # World ROOT
    }
    for tItem in project.tree:
        assert index.reIndexHandle(tItem.itemHandle) is notIndexable.get(tItem.itemHandle, True)

    assert index.reIndexHandle(None) is False

    # No folder for saving
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.storage.NWStorage.getMetaFile", lambda *a: None)
        assert index.saveIndex() is False

    # Make the save fail
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeException)
        assert index.saveIndex() is False

    # Make the save pass
    assert index.saveIndex() is True

    # Take a copy of the index
    tagIndex = str(index._tagsIndex.packData())
    itemsIndex = str(index._itemIndex.packData())

    # Delete a handle
    assert index._tagsIndex["Bod"] is not None
    assert index._itemIndex["4c4f28287af27"] is not None
    index.deleteHandle("4c4f28287af27")
    assert index._tagsIndex["Bod"] is None
    assert index._itemIndex["4c4f28287af27"] is None

    # Clear the index
    index.clearIndex()
    assert index._tagsIndex._tags == {}
    assert index._itemIndex._items == {}

    # No folder for loading
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.storage.NWStorage.getMetaFile", lambda *a: None)
        assert index.loadIndex() is False

    # Make the load fail
    with monkeypatch.context() as mp:
        mp.setattr(json, "load", causeException)
        assert index.loadIndex() is False
        assert index.indexBroken is True

    # Make the load pass
    assert index.loadIndex() is True
    assert index.indexBroken is False

    assert str(index._tagsIndex.packData()) == tagIndex
    assert str(index._itemIndex.packData()) == itemsIndex

    # Rebuild index
    index.clearIndex()
    index.rebuildIndex()

    assert str(index._tagsIndex.packData()) == tagIndex
    assert str(index._itemIndex.packData()) == itemsIndex

    # Check File
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    # Write an empty index file and load it
    writeFile(projFile, "{}")
    assert index.loadIndex() is False
    assert index.indexBroken is True

    # Write an index file that passes loading, but is still empty
    writeFile(projFile, '{"novelWriter.tagsIndex": {}, "novelWriter.itemIndex": {}}')
    assert index.loadIndex() is True
    assert index.indexBroken is False

    # Check that the index is re-populated
    assert "04468803b92e1" in index._itemIndex
    assert "2426c6f0ca922" in index._itemIndex
    assert "441420a886d82" in index._itemIndex
    assert "47666c91c7ccf" in index._itemIndex
    assert "4c4f28287af27" in index._itemIndex
    assert "846352075de7d" in index._itemIndex
    assert "88243afbe5ed8" in index._itemIndex
    assert "88d59a277361b" in index._itemIndex
    assert "8c58a65414c23" in index._itemIndex
    assert "db7e733775d4d" in index._itemIndex
    assert "eb103bc70c90c" in index._itemIndex
    assert "f8c0562e50f1b" in index._itemIndex
    assert "f96ec11c6a3da" in index._itemIndex
    assert "fb609cd8319dc" in index._itemIndex
    assert "7a992350f3eb6" in index._itemIndex

    # Finalise
    project.closeProject()

# END Test testCoreIndex_LoadSave


@pytest.mark.core
def testCoreIndex_ScanThis(mockGUI):
    """Test the tag scanner function scanThis."""
    project = NWProject()
    index = project.index

    isValid, theBits, thePos = index.scanThis("tag: this, and this")
    assert isValid is False

    isValid, theBits, thePos = index.scanThis("@")
    assert isValid is False

    isValid, theBits, thePos = index.scanThis("@:")
    assert isValid is False

    isValid, theBits, thePos = index.scanThis(" @a: b")
    assert isValid is False

    isValid, theBits, thePos = index.scanThis("@a:")
    assert isValid is True
    assert theBits == ["@a"]
    assert thePos  == [0]

    isValid, theBits, thePos = index.scanThis("@a:b")
    assert isValid is True
    assert theBits == ["@a", "b"]
    assert thePos  == [0, 3]

    isValid, theBits, thePos = index.scanThis("@a:b,c,d")
    assert isValid is True
    assert theBits == ["@a", "b", "c", "d"]
    assert thePos  == [0, 3, 5, 7]

    isValid, theBits, thePos = index.scanThis("@a : b , c , d")
    assert isValid is True
    assert theBits == ["@a", "b", "c", "d"]
    assert thePos  == [0, 5, 9, 13]

    isValid, theBits, thePos = index.scanThis("@tag: this, and this")
    assert isValid is True
    assert theBits == ["@tag", "this", "and this"]
    assert thePos  == [0, 6, 12]

    isValid, theBits, thePos = index.scanThis("@tag: this,, and this")
    assert isValid is True
    assert theBits == ["@tag", "this", "", "and this"]
    assert thePos  == [0, 6, 11, 13]

    isValid, theBits, thePos = index.scanThis("@tag: this, , and this")
    assert isValid is True
    assert theBits == ["@tag", "this", "", "and this"]
    assert thePos  == [0, 6, 12, 14]

    project.closeProject()

# END Test testCoreIndex_ScanThis


@pytest.mark.core
def testCoreIndex_CheckThese(mockGUI, fncPath, mockRnd):
    """Test the tag checker function checkThese."""
    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)
    index = project.index
    index.clearIndex()

    nHandle = project.newFile("Hello", C.hNovelRoot)
    cHandle = project.newFile("Jane",  C.hCharRoot)
    assert isinstance(nHandle, str)
    assert isinstance(cHandle, str)

    nItem = project.tree[nHandle]
    cItem = project.tree[cHandle]
    assert isinstance(nItem, NWItem)
    assert isinstance(cItem, NWItem)

    assert index.rootChangedSince(C.hNovelRoot, 0) is False
    assert index.rootChangedSince(None, 0) is False
    assert index.indexChangedSince(0) is False

    assert index.scanText(cHandle, (
        "# Jane Smith\n"
        "@tag: Jane\n"
        "@tag:\n"
        "@:\n"
    ))
    assert index.scanText(nHandle, (
        "# Hello World!\n"
        "@pov: Jane\n"
        "@invalid: John\n"  # Checks for issue #688
    ))
    assert index._tagsIndex.tagHandle("Jane") == cHandle
    assert index._tagsIndex.tagHeading("Jane") == "T0001"
    assert index._tagsIndex.tagClass("Jane") == "CHARACTER"
    assert index.getItemHeader(nHandle, "T0001").title == "Hello World!"  # type: ignore
    assert index.getReferences(nHandle, "T0001") == {
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

    assert index.rootChangedSince(C.hNovelRoot, 0) is True
    assert index.indexChangedSince(0) is True

    assert cItem.mainHeading == "H1"
    assert nItem.mainHeading == "H1"

    # Zero Items
    assert index.checkThese([], cItem) == []

    # One Item
    assert index.checkThese(["@tag"], cItem) == [True]
    assert index.checkThese(["@who"], cItem) == [False]

    # Two Items
    assert index.checkThese(["@tag", "Jane"], cItem) == [True, True]
    assert index.checkThese(["@tag", "John"], cItem) == [True, True]
    assert index.checkThese(["@tag", "Jane"], nItem) == [True, False]
    assert index.checkThese(["@tag", "John"], nItem) == [True, True]
    assert index.checkThese(["@pov", "John"], nItem) == [True, False]
    assert index.checkThese(["@pov", "Jane"], nItem) == [True, True]
    assert index.checkThese(["@ pov", "Jane"], nItem) == [False, False]
    assert index.checkThese(["@what", "Jane"], nItem) == [False, False]

    # Three Items
    assert index.checkThese(["@tag", "Jane", "John"], cItem) == [True, True, False]
    assert index.checkThese(["@who", "Jane", "John"], cItem) == [False, False, False]
    assert index.checkThese(["@pov", "Jane", "John"], nItem) == [True, True, False]

    project.closeProject()

# END Test testCoreIndex_CheckThese


@pytest.mark.core
def testCoreIndex_ScanText(mockGUI, fncPath, mockRnd):
    """Check the index text scanner."""
    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)
    index = project.index

    # Some items for fail to scan tests
    dHandle = project.newFolder("Folder", C.hNovelRoot)
    xHandle = project.newFile("No Layout", C.hNovelRoot)
    assert isinstance(dHandle, str)
    assert isinstance(xHandle, str)

    xItem = project.tree[xHandle]
    assert isinstance(xItem, NWItem)
    xItem.setLayout(nwItemLayout.NO_LAYOUT)

    # Check invalid data
    assert index.scanText(None, "Hello World!") is False  # type: ignore
    assert index.scanText(dHandle, "Hello World!") is False
    assert index.scanText(xHandle, "Hello World!") is False

    xItem.setLayout(nwItemLayout.DOCUMENT)
    xItem.setParent(None)
    assert index.scanText(xHandle, "Hello World!") is False

    # Create the trash folder
    tHandle = project.trashFolder()
    assert project.tree[tHandle] is not None
    xItem.setParent(tHandle)
    project.tree.updateItemData(xItem.itemHandle)
    assert xItem.itemRoot == tHandle
    assert xItem.itemClass == nwItemClass.TRASH
    assert index.scanText(xHandle, "## Hello World!") is True
    assert xItem.mainHeading == "H2"

    # Create the archive root
    aHandle = project.newRoot(nwItemClass.ARCHIVE)
    assert project.tree[aHandle] is not None
    xItem.setParent(aHandle)
    project.tree.updateItemData(xItem.itemHandle)
    assert index.scanText(xHandle, "### Hello World!") is True
    assert xItem.mainHeading == "H3"

    # Make some usable items
    tHandle = project.newFile("Title", C.hNovelRoot)
    pHandle = project.newFile("Page",  C.hNovelRoot)
    nHandle = project.newFile("Hello", C.hNovelRoot)
    cHandle = project.newFile("Jane",  C.hCharRoot)
    sHandle = project.newFile("Scene", C.hNovelRoot)
    assert isinstance(tHandle, str)
    assert isinstance(pHandle, str)
    assert isinstance(nHandle, str)
    assert isinstance(cHandle, str)
    assert isinstance(sHandle, str)

    # Text Indexing
    # =============

    # Index correct text
    assert index.scanText(cHandle, (
        "# Jane Smith\n"
        "@tag: Jane\n"
    ))
    assert index.scanText(nHandle, (
        "# Hello World!\n"
        "@pov: Jane\n"
        "@char: Jane\n\n"
        "% this is a comment\n\n"
        "This is a story about Jane Smith.\n\n"
        "Well, not really.\n"
    ))
    assert index._tagsIndex.tagHandle("Jane") == cHandle
    assert index._tagsIndex.tagHeading("Jane") == "T0001"
    assert index._tagsIndex.tagClass("Jane") == "CHARACTER"
    assert index.getItemHeader(nHandle, "T0001").title == "Hello World!"  # type: ignore

    # Title Indexing
    # ==============

    # Document File
    assert index.scanText(nHandle, (
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
    assert index._itemIndex[nHandle]["T0001"].references == {}  # type: ignore
    assert index._itemIndex[nHandle]["T0002"].references == {}  # type: ignore
    assert index._itemIndex[nHandle]["T0003"].references == {}  # type: ignore
    assert index._itemIndex[nHandle]["T0004"].references == {}  # type: ignore

    assert index._itemIndex[nHandle]["T0001"].level == "H1"  # type: ignore
    assert index._itemIndex[nHandle]["T0002"].level == "H2"  # type: ignore
    assert index._itemIndex[nHandle]["T0003"].level == "H3"  # type: ignore
    assert index._itemIndex[nHandle]["T0004"].level == "H4"  # type: ignore

    assert index._itemIndex[nHandle]["T0001"].line == 1  # type: ignore
    assert index._itemIndex[nHandle]["T0002"].line == 7  # type: ignore
    assert index._itemIndex[nHandle]["T0003"].line == 13  # type: ignore
    assert index._itemIndex[nHandle]["T0004"].line == 19  # type: ignore

    assert index._itemIndex[nHandle]["T0001"].title == "Title One"  # type: ignore
    assert index._itemIndex[nHandle]["T0002"].title == "Title Two"  # type: ignore
    assert index._itemIndex[nHandle]["T0003"].title == "Title Three"  # type: ignore
    assert index._itemIndex[nHandle]["T0004"].title == "Title Four"  # type: ignore

    assert index._itemIndex[nHandle]["T0001"].charCount == 23  # type: ignore
    assert index._itemIndex[nHandle]["T0002"].charCount == 23  # type: ignore
    assert index._itemIndex[nHandle]["T0003"].charCount == 27  # type: ignore
    assert index._itemIndex[nHandle]["T0004"].charCount == 56  # type: ignore

    assert index._itemIndex[nHandle]["T0001"].wordCount == 4  # type: ignore
    assert index._itemIndex[nHandle]["T0002"].wordCount == 4  # type: ignore
    assert index._itemIndex[nHandle]["T0003"].wordCount == 4  # type: ignore
    assert index._itemIndex[nHandle]["T0004"].wordCount == 9  # type: ignore

    assert index._itemIndex[nHandle]["T0001"].paraCount == 1  # type: ignore
    assert index._itemIndex[nHandle]["T0002"].paraCount == 1  # type: ignore
    assert index._itemIndex[nHandle]["T0003"].paraCount == 1  # type: ignore
    assert index._itemIndex[nHandle]["T0004"].paraCount == 3  # type: ignore

    assert index._itemIndex[nHandle]["T0001"].synopsis == "Synopsis One."  # type: ignore
    assert index._itemIndex[nHandle]["T0002"].synopsis == "Synopsis Two."  # type: ignore
    assert index._itemIndex[nHandle]["T0003"].synopsis == "Synopsis Three."  # type: ignore
    assert index._itemIndex[nHandle]["T0004"].synopsis == "Synopsis Four."  # type: ignore

    # Note File
    assert index.scanText(cHandle, (
        "# Title One\n\n"
        "@tag: One\n\n"
        "% synopsis: Synopsis One.\n\n"
        "Paragraph One.\n\n"
    ))
    assert index._itemIndex[cHandle]["T0001"].references == {}  # type: ignore
    assert index._itemIndex[cHandle]["T0001"].level == "H1"  # type: ignore
    assert index._itemIndex[cHandle]["T0001"].line == 1  # type: ignore
    assert index._itemIndex[cHandle]["T0001"].title == "Title One"  # type: ignore
    assert index._itemIndex[cHandle]["T0001"].charCount == 23  # type: ignore
    assert index._itemIndex[cHandle]["T0001"].wordCount == 4  # type: ignore
    assert index._itemIndex[cHandle]["T0001"].paraCount == 1  # type: ignore
    assert index._itemIndex[cHandle]["T0001"].synopsis == "Synopsis One."  # type: ignore

    # Valid and Invalid References
    assert index.scanText(sHandle, (
        "# Title One\n\n"
        "@pov: One\n\n"  # Valid
        "@char: Two\n\n"  # Invalid tag
        "@:\n\n"  # Invalid line
        "% synopsis: Synopsis One.\n\n"
        "Paragraph One.\n\n"
    ))
    assert index._itemIndex[sHandle]["T0001"].references == {  # type: ignore
        "one": {"@pov"}, "two": {"@char"}
    }

    # Special Titles
    # ==============

    assert index.scanText(tHandle, (
        "#! My Project\n\n"
        ">> By Jane Doe <<\n\n"
    ))
    assert index._itemIndex[cHandle]["T0001"].references == {}  # type: ignore
    assert index._itemIndex[tHandle]["T0001"].level == "H1"  # type: ignore
    assert index._itemIndex[tHandle]["T0001"].line == 1  # type: ignore
    assert index._itemIndex[tHandle]["T0001"].title == "My Project"  # type: ignore
    assert index._itemIndex[tHandle]["T0001"].charCount == 21  # type: ignore
    assert index._itemIndex[tHandle]["T0001"].wordCount == 5  # type: ignore
    assert index._itemIndex[tHandle]["T0001"].paraCount == 1  # type: ignore
    assert index._itemIndex[tHandle]["T0001"].synopsis == ""  # type: ignore

    assert index.scanText(tHandle, (
        "##! Prologue\n\n"
        "In the beginning there was time ...\n\n"
    ))
    assert index._itemIndex[cHandle]["T0001"].references == {}  # type: ignore
    assert index._itemIndex[tHandle]["T0001"].level == "H2"  # type: ignore
    assert index._itemIndex[tHandle]["T0001"].line == 1  # type: ignore
    assert index._itemIndex[tHandle]["T0001"].title == "Prologue"  # type: ignore
    assert index._itemIndex[tHandle]["T0001"].charCount == 43  # type: ignore
    assert index._itemIndex[tHandle]["T0001"].wordCount == 8  # type: ignore
    assert index._itemIndex[tHandle]["T0001"].paraCount == 1  # type: ignore
    assert index._itemIndex[tHandle]["T0001"].synopsis == ""  # type: ignore

    # Page wo/Title
    # =============

    project.tree[pHandle]._layout = nwItemLayout.DOCUMENT  # type: ignore
    assert index.scanText(pHandle, (
        "This is a page with some text on it.\n\n"
    ))
    assert index._itemIndex[pHandle]["T0000"].references == {}  # type: ignore
    assert index._itemIndex[pHandle]["T0000"].level == "H0"  # type: ignore
    assert index._itemIndex[pHandle]["T0000"].line == 0  # type: ignore
    assert index._itemIndex[pHandle]["T0000"].title == ""  # type: ignore
    assert index._itemIndex[pHandle]["T0000"].charCount == 36  # type: ignore
    assert index._itemIndex[pHandle]["T0000"].wordCount == 9  # type: ignore
    assert index._itemIndex[pHandle]["T0000"].paraCount == 1  # type: ignore
    assert index._itemIndex[pHandle]["T0000"].synopsis == ""  # type: ignore

    project.tree[pHandle]._layout = nwItemLayout.NOTE  # type: ignore
    assert index.scanText(pHandle, (
        "This is a page with some text on it.\n\n"
    ))
    assert index._itemIndex[pHandle]["T0000"].references == {}  # type: ignore
    assert index._itemIndex[pHandle]["T0000"].level == "H0"  # type: ignore
    assert index._itemIndex[pHandle]["T0000"].line == 0  # type: ignore
    assert index._itemIndex[pHandle]["T0000"].title == ""  # type: ignore
    assert index._itemIndex[pHandle]["T0000"].charCount == 36  # type: ignore
    assert index._itemIndex[pHandle]["T0000"].wordCount == 9  # type: ignore
    assert index._itemIndex[pHandle]["T0000"].paraCount == 1  # type: ignore
    assert index._itemIndex[pHandle]["T0000"].synopsis == ""  # type: ignore

    project.closeProject()

# END Test testCoreIndex_ScanText


@pytest.mark.core
def testCoreIndex_ExtractData(mockGUI, fncPath, mockRnd):
    """Check the index data extraction functions."""
    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)

    index = project.index
    index.reIndexHandle(C.hNovelRoot)
    index.reIndexHandle(C.hPlotRoot)
    index.reIndexHandle(C.hCharRoot)
    index.reIndexHandle(C.hWorldRoot)
    index.reIndexHandle(C.hTitlePage)
    index.reIndexHandle(C.hChapterDir)
    index.reIndexHandle(C.hChapterDoc)
    index.reIndexHandle(C.hSceneDoc)

    nHandle = project.newFile("Hello", C.hNovelRoot)
    cHandle = project.newFile("Jane",  C.hCharRoot)
    assert isinstance(nHandle, str)
    assert isinstance(cHandle, str)

    assert index.getItemHeader("", "") is None
    assert index.getItemHeader(C.hNovelRoot, "") is None

    assert index.scanText(cHandle, (
        "# Jane Smith\n"
        "@tag: Jane\n"
    ))
    assert index.scanText(nHandle, (
        "# Hello World!\n"
        "@pov: Jane\n"
        "@char: Jane\n\n"
        "% this is a comment\n\n"
        "This is a story about Jane Smith.\n\n"
        "Well, not really.\n"
    ))

    # The novel structure should contain the pointer to the novel file header
    keys = []
    for aKey, _, _, _ in index.novelStructure():
        keys.append(aKey)

    assert keys == [
        f"{C.hTitlePage}:T0001",
        f"{C.hChapterDoc}:T0001",
        f"{C.hSceneDoc}:T0001",
        f"{nHandle}:T0001",
    ]

    # Check that excluded files can be skipped
    project.tree[nHandle].setActive(False)  # type: ignore

    keys = []
    for aKey, _, _, _ in index.novelStructure(skipExcl=False):
        keys.append(aKey)

    assert keys == [
        f"{C.hTitlePage}:T0001",
        f"{C.hChapterDoc}:T0001",
        f"{C.hSceneDoc}:T0001",
        f"{nHandle}:T0001",
    ]

    keys = []
    for aKey, _, _, _ in index.novelStructure(skipExcl=True):
        keys.append(aKey)

    assert keys == [
        f"{C.hTitlePage}:T0001",
        f"{C.hChapterDoc}:T0001",
        f"{C.hSceneDoc}:T0001",
    ]

    # The novel file should have the correct counts
    cC, wC, pC = index.getCounts(nHandle)
    assert cC == 62  # Characters in text and title only
    assert wC == 12  # Words in text and title only
    assert pC == 2   # Paragraphs in text only

    # getItemData + getHandleHeaderCount
    # ==================================

    item = index.getItemData(nHandle)
    assert isinstance(item, IndexItem)
    assert item.headings() == ["T0001"]
    assert index.getHandleHeaderCount(nHandle) == 1
    assert index.getHandleHeaderCount("foo") == 0

    # getReferences
    # =============

    # Look up an invalid handle
    refs = index.getReferences("Not a handle")
    assert refs["@pov"] == []
    assert refs["@char"] == []

    # The novel file should now refer to Jane as @pov and @char
    refs = index.getReferences(nHandle)
    assert refs["@pov"] == ["Jane"]
    assert refs["@char"] == ["Jane"]

    # getBackReferenceList
    # ====================

    # None handle should return an empty dict
    assert index.getBackReferenceList(None) == {}  # type: ignore

    # The Title Page file should have no references as it has no tag
    assert index.getBackReferenceList(C.hTitlePage) == {}

    # The character file should have a record of the reference from the novel file
    refs = index.getBackReferenceList(cHandle)
    assert refs[nHandle][0] == "T0001"

    # getTagSource
    # ============

    assert index.getTagSource("Jane") == (cHandle, "T0001")
    assert index.getTagSource("John") == (None, "T0000")

    # getDocumentTags
    # ===============
    assert index.getDocumentTags(cHandle) == ["jane"]
    assert index.getDocumentTags(None) == []

    # getClassTags
    # ============
    assert index.getClassTags(nwItemClass.CHARACTER) == ["Jane"]

    # getTagsData
    # ===========
    assert list(index.getTagsData()) == [(
        "jane", "Jane", "CHARACTER",
        index.getItemData(cHandle),
        index.getItemHeader(cHandle, "T0001")
    )]

    # getSingleTag
    # ============
    assert index.getSingleTag("jane") == (
        "Jane", "CHARACTER",
        index.getItemData(cHandle),
        index.getItemHeader(cHandle, "T0001")
    )
    assert index.getSingleTag("foobar") == ("", "", None, None)

    # getCounts
    # =========
    # For whole text and sections

    # Invalid handle or title should return 0s
    assert index.getCounts("stuff") == (0, 0, 0)
    assert index.getCounts(nHandle, "stuff") == (0, 0, 0)

    # Get section counts for a novel file
    assert index.scanText(nHandle, (
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
    cC, wC, pC = index.getCounts(nHandle)
    assert cC == 152
    assert wC == 28
    assert pC == 4

    # First part
    cC, wC, pC = index.getCounts(nHandle, "T0001")
    assert cC == 62
    assert wC == 12
    assert pC == 2

    # Second part
    cC, wC, pC = index.getCounts(nHandle, "T0002")
    assert cC == 90
    assert wC == 16
    assert pC == 2

    # Get section counts for a note file
    assert index.scanText(cHandle, (
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
    cC, wC, pC = index.getCounts(cHandle)
    assert cC == 152
    assert wC == 28
    assert pC == 4

    # First part
    cC, wC, pC = index.getCounts(cHandle, "T0001")
    assert cC == 62
    assert wC == 12
    assert pC == 2

    # Second part
    cC, wC, pC = index.getCounts(cHandle, "T0002")
    assert cC == 90
    assert wC == 16
    assert pC == 2

    # Novel Stats
    # ===========

    hHandle = project.newFile("Chapter", C.hNovelRoot)
    sHandle = project.newFile("Scene One", C.hNovelRoot)
    tHandle = project.newFile("Scene Two", C.hNovelRoot)

    project.tree[hHandle].itemLayout == nwItemLayout.DOCUMENT  # type: ignore
    project.tree[sHandle].itemLayout == nwItemLayout.DOCUMENT  # type: ignore
    project.tree[tHandle].itemLayout == nwItemLayout.DOCUMENT  # type: ignore

    assert index.scanText(hHandle, "## Chapter One\n\n")  # type: ignore
    assert index.scanText(sHandle, "### Scene One\n\n")  # type: ignore
    assert index.scanText(tHandle, "### Scene Two\n\n")  # type: ignore

    assert [(h, t) for h, t, _ in index._itemIndex.iterNovelStructure(skipExcl=False)] == [
        (C.hTitlePage, "T0001"),
        (C.hChapterDoc, "T0001"),
        (C.hSceneDoc, "T0001"),
        (nHandle, "T0001"),
        (nHandle, "T0002"),
        (hHandle, "T0001"),
        (sHandle, "T0001"),
        (tHandle, "T0001"),
    ]

    assert [(h, t) for h, t, _ in index._itemIndex.iterNovelStructure(skipExcl=True)] == [
        (C.hTitlePage, "T0001"),
        (C.hChapterDoc, "T0001"),
        (C.hSceneDoc, "T0001"),
        (hHandle, "T0001"),
        (sHandle, "T0001"),
        (tHandle, "T0001"),
    ]

    # Add a fake handle to the tree and check that it's ignored
    project.tree._order.append("0000000000000")
    assert [(h, t) for h, t, _ in index._itemIndex.iterNovelStructure(skipExcl=False)] == [
        (C.hTitlePage, "T0001"),
        (C.hChapterDoc, "T0001"),
        (C.hSceneDoc, "T0001"),
        (nHandle, "T0001"),
        (nHandle, "T0002"),
        (hHandle, "T0001"),
        (sHandle, "T0001"),
        (tHandle, "T0001"),
    ]
    project.tree._order.remove("0000000000000")

    # Extract stats
    assert index.getNovelWordCount(skipExcl=False) == 43
    assert index.getNovelWordCount(skipExcl=True) == 15
    assert index.getNovelTitleCounts(skipExcl=False) == [0, 3, 2, 3, 0]
    assert index.getNovelTitleCounts(skipExcl=True) == [0, 1, 2, 3, 0]

    # Table of Contents
    assert index.getTableOfContents(C.hNovelRoot, 0, skipExcl=True) == []
    assert index.getTableOfContents(C.hNovelRoot, 1, skipExcl=True) == [
        (f"{C.hTitlePage}:T0001", 1, "New Novel", 15),
    ]
    assert index.getTableOfContents(C.hNovelRoot, 2, skipExcl=True) == [
        (f"{C.hTitlePage}:T0001", 1, "New Novel", 5),
        (f"{C.hChapterDoc}:T0001", 2, "New Chapter", 4),
        (f"{hHandle}:T0001", 2, "Chapter One", 6),
    ]
    assert index.getTableOfContents(C.hNovelRoot, 3, skipExcl=True) == [
        (f"{C.hTitlePage}:T0001", 1, "New Novel", 5),
        (f"{C.hChapterDoc}:T0001", 2, "New Chapter", 2),
        (f"{C.hSceneDoc}:T0001", 3, "New Scene", 2),
        (f"{hHandle}:T0001", 2, "Chapter One", 2),
        (f"{sHandle}:T0001", 3, "Scene One", 2),
        (f"{tHandle}:T0001", 3, "Scene Two", 2),
    ]

    assert index.getTableOfContents(C.hNovelRoot, 0, skipExcl=False) == []
    assert index.getTableOfContents(C.hNovelRoot, 1, skipExcl=False) == [
        (f"{C.hTitlePage}:T0001", 1, "New Novel", 9),
        (f"{nHandle}:T0001", 1, "Hello World!", 12),
        (f"{nHandle}:T0002", 1, "Hello World!", 22),
    ]

    assert index.saveIndex() is True
    assert project.saveProject() is True
    project.closeProject()

# END Test testCoreIndex_ExtractData


@pytest.mark.core
def testCoreIndex_TagsIndex():
    """Check the TagsIndex class."""
    tagsIndex = TagsIndex()
    assert tagsIndex._tags == {}

    # Expected data
    content = {
        "tag1": {
            "name": "Tag1",
            "handle": "0000000000001",
            "heading": "T0001",
            "class": nwItemClass.NOVEL.name,
        },
        "tag2": {
            "name": "Tag2",
            "handle": "0000000000002",
            "heading": "T0002",
            "class": nwItemClass.CHARACTER.name,
        },
        "tag3": {
            "name": "Tag3",
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
    assert tagsIndex["Tag1"] == content["tag1"]
    assert tagsIndex["Tag2"] == content["tag2"]
    assert tagsIndex["Tag3"] == content["tag3"]
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
        tagsIndex.unpackData([])  # type: ignore

    # Invalid key
    with pytest.raises(ValueError):
        tagsIndex.unpackData({
            1234: {
                "name": "1234",
                "handle": "0000000000001",
                "heading": "T0001",
                "class": "NOVEL",
            }
        })

    # Missing name
    with pytest.raises(KeyError):
        tagsIndex.unpackData({
            "tag1": {
                "handle": "0000000000001",
                "heading": "T0001",
                "class": "NOVEL",
            }
        })

    # Missing handle
    with pytest.raises(KeyError):
        tagsIndex.unpackData({
            "tag1": {
                "name": "Tag1",
                "heading": "T0001",
                "class": "NOVEL",
            }
        })

    # Missing heading
    with pytest.raises(KeyError):
        tagsIndex.unpackData({
            "tag1": {
                "name": "Tag1",
                "handle": "0000000000001",
                "class": "NOVEL",
            }
        })

    # Missing class
    with pytest.raises(KeyError):
        tagsIndex.unpackData({
            "tag1": {
                "name": "Tag1",
                "handle": "0000000000001",
                "heading": "T0001",
            }
        })

    # Invalid key case
    with pytest.raises(ValueError):
        tagsIndex.unpackData({
            "Tag1": {
                "name": "Tag1",
                "handle": "blablabla",
                "heading": "T0001",
                "class": "NOVEL",
            }
        })

    # Invalid handle
    with pytest.raises(ValueError):
        tagsIndex.unpackData({
            "tag1": {
                "name": "Tag1",
                "handle": "blablabla",
                "heading": "T0001",
                "class": "NOVEL",
            }
        })

    # Invalid heading
    with pytest.raises(ValueError):
        tagsIndex.unpackData({
            "tag1": {
                "name": "Tag1",
                "handle": "0000000000001",
                "heading": "blabla",
                "class": "NOVEL",
            }
        })

    # Invalid class
    with pytest.raises(ValueError):
        tagsIndex.unpackData({
            "tag1": {
                "name": "Tag1",
                "handle": "0000000000001",
                "heading": "T0001",
                "class": "blabla",
            }
        })

# END Test testCoreIndex_TagsIndex


@pytest.mark.core
def testCoreIndex_ItemIndex(mockGUI, fncPath, mockRnd):
    """Check the ItemIndex class."""
    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)
    project.index.clearIndex()

    nHandle = C.hTitlePage
    cHandle = C.hChapterDoc
    sHandle = C.hSceneDoc

    assert project.index.saveIndex() is True
    itemIndex = project.index._itemIndex

    # The index should be empty
    assert nHandle not in itemIndex
    assert cHandle not in itemIndex
    assert sHandle not in itemIndex

    # Add Items
    # =========
    assert cHandle not in itemIndex

    # Add the novel chapter file
    itemIndex.add(cHandle, project.tree[cHandle])  # type: ignore
    assert cHandle in itemIndex
    assert itemIndex[cHandle].item == project.tree[cHandle]  # type: ignore
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
    itemIndex.addHeadingRef(cHandle, "T0001", ["Jane"], "@pov")
    itemIndex.addHeadingRef(cHandle, "T0001", ["Jane"], "@focus")
    itemIndex.addHeadingRef(cHandle, "T0001", ["Jane", "John"], "@char")
    idxData = itemIndex.packData()

    assert idxData[cHandle]["headings"]["T0001"] == {
        "level": "H2", "line": 1, "title": "Chapter One", "tag": "one",
        "cCount": 60, "wCount": 10, "pCount": 2, "synopsis": "In the beginning ...",
    }
    assert "@pov" in idxData[cHandle]["references"]["T0001"]["jane"]
    assert "@focus" in idxData[cHandle]["references"]["T0001"]["jane"]
    assert "@char" in idxData[cHandle]["references"]["T0001"]["jane"]
    assert "@char" in idxData[cHandle]["references"]["T0001"]["john"]

    # Add the other two files
    itemIndex.add(nHandle, project.tree[nHandle])  # type: ignore
    itemIndex.add(sHandle, project.tree[sHandle])  # type: ignore
    itemIndex.addItemHeading(nHandle, 1, "H1", "Novel")
    itemIndex.addItemHeading(sHandle, 1, "H3", "Scene One")

    # Check Item and Heading Direct Access
    # ====================================

    # Check repr strings
    assert repr(itemIndex[nHandle]) == f"<IndexItem handle='{nHandle}'>"
    assert repr(itemIndex[nHandle]["T0001"]) == "<IndexHeading key='T0001'>"  # type: ignore

    # Check content of a single item
    assert "T0001" in itemIndex[nHandle]  # type: ignore
    assert itemIndex[cHandle].allTags() == ["one"]  # type: ignore

    # Check the content of a single heading
    assert itemIndex[cHandle]["T0001"].key == "T0001"  # type: ignore
    assert itemIndex[cHandle]["T0001"].level == "H2"  # type: ignore
    assert itemIndex[cHandle]["T0001"].line == 1  # type: ignore
    assert itemIndex[cHandle]["T0001"].title == "Chapter One"  # type: ignore
    assert itemIndex[cHandle]["T0001"].tag == "one"  # type: ignore
    assert itemIndex[cHandle]["T0001"].charCount == 60  # type: ignore
    assert itemIndex[cHandle]["T0001"].wordCount == 10  # type: ignore
    assert itemIndex[cHandle]["T0001"].paraCount == 2  # type: ignore
    assert itemIndex[cHandle]["T0001"].synopsis == "In the beginning ..."  # type: ignore
    assert "jane" in itemIndex[cHandle]["T0001"].references  # type: ignore
    assert "john" in itemIndex[cHandle]["T0001"].references  # type: ignore

    # Check heading level setter
    itemIndex[cHandle]["T0001"].setLevel("H3")  # Change it  # type: ignore
    assert itemIndex[cHandle]["T0001"].level == "H3"  # type: ignore
    itemIndex[cHandle]["T0001"].setLevel("H2")  # Set it back  # type: ignore
    assert itemIndex[cHandle]["T0001"].level == "H2"  # type: ignore
    itemIndex[cHandle]["T0001"].setLevel("H5")  # Invalid level  # type: ignore
    assert itemIndex[cHandle]["T0001"].level == "H2"  # type: ignore

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
    mHandle = project.newRoot(nwItemClass.NOVEL)
    uHandle = project.newFile("Title Page", mHandle)
    itemIndex.add(uHandle, project.tree[uHandle])  # type: ignore
    itemIndex.addItemHeading(uHandle, "T0001", "H1", "Novel 2")  # type: ignore
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
    project.tree._order.append("stuff")
    nStruct = list(itemIndex.iterNovelStructure())
    assert len(nStruct) == 4
    assert nStruct[0][0] == nHandle
    assert nStruct[1][0] == cHandle
    assert nStruct[2][0] == sHandle
    assert nStruct[3][0] == uHandle

    # Skip excluded
    project.tree[sHandle].setActive(False)  # type: ignore
    nStruct = list(itemIndex.iterNovelStructure(skipExcl=True))
    assert len(nStruct) == 3
    assert nStruct[0][0] == nHandle
    assert nStruct[1][0] == cHandle
    assert nStruct[2][0] == uHandle

    # Delete new item
    del itemIndex[uHandle]  # type: ignore
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
        itemIndex.unpackData("stuff")  # type: ignore

    # Keys must be valid handles
    with pytest.raises(ValueError):
        itemIndex.unpackData({"stuff": "more stuff"})

    # Unknown keys should be skipped
    itemIndex.unpackData({C.hInvalid: {}})
    assert itemIndex._items == {}

    # Known keys can be added, even without data
    itemIndex.unpackData({nHandle: {}})
    assert nHandle in itemIndex
    assert itemIndex[nHandle].handle == nHandle  # type: ignore

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
    assert "T0001" in itemIndex[cHandle]  # type: ignore
    assert "T0002" not in itemIndex[cHandle]  # type: ignore
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
def testCoreIndex_processComment():
    """Test the comment processing function."""
    # Regular comment
    assert processComment("%Hi") == (nwComment.PLAIN, "Hi", 0)
    assert processComment("% Hi") == (nwComment.PLAIN, "Hi", 0)
    assert processComment("% Hi:You") == (nwComment.PLAIN, "Hi:You", 0)

    # Synopsis
    assert processComment("%synopsis:") == (nwComment.PLAIN, "synopsis:", 0)
    assert processComment("%synopsis: Hi") == (nwComment.SYNOPSIS, "Hi", 10)
    assert processComment("% synopsis: Hi") == (nwComment.SYNOPSIS, "Hi", 11)
    assert processComment("%  synopsis : Hi") == (nwComment.SYNOPSIS, "Hi", 13)
    assert processComment("%   Synopsis  : Hi") == (nwComment.SYNOPSIS, "Hi", 15)
    assert processComment("% \t  SYNOPSIS  : Hi") == (nwComment.SYNOPSIS, "Hi", 16)
    assert processComment("% \t  SYNOPSIS  : Hi:You") == (nwComment.SYNOPSIS, "Hi:You", 16)

    # Summary
    assert processComment("%summary:") == (nwComment.PLAIN, "summary:", 0)
    assert processComment("%summary: Hi") == (nwComment.SUMMARY, "Hi", 9)
    assert processComment("% summary: Hi") == (nwComment.SUMMARY, "Hi", 10)
    assert processComment("%  summary : Hi") == (nwComment.SUMMARY, "Hi", 12)
    assert processComment("%   Summary  : Hi") == (nwComment.SUMMARY, "Hi", 14)
    assert processComment("% \t  SUMMARY  : Hi") == (nwComment.SUMMARY, "Hi", 15)
    assert processComment("% \t  SUMMARY  : Hi:You") == (nwComment.SUMMARY, "Hi:You", 15)

# END Test testCoreIndex_processComment


@pytest.mark.core
def testCoreIndex_countWords():
    """Test the word counter and the exclusion filers."""
    # Non-Text
    assert countWords(None) == (0, 0, 0)  # type: ignore
    assert countWords(1234) == (0, 0, 0)  # type: ignore

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

    # Formatting Codes, Upper Case (Old Implementation)
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

    # Formatting Codes, Lower Case (Current Implementation)
    cC, wC, pC = countWords((
        "Some text\n\n"
        "[newpage]\n\n"
        "more text\n\n"
        "[new page]]\n\n"
        "even more text\n\n"
        "[vspace]\n\n"
        "and some final text\n\n"
        "[vspace:4]\n\n"
        "THE END\n\n"
    ))
    assert cC == 58
    assert wC == 13
    assert pC == 5

    # Check ShortCodes
    cC, wC, pC = countWords((
        "Text with [b]bold[/b] text and padded [b] bold [/b] text.\n\n"
        "Text with [b][i] nested [/i] emphasis [/b] in it.\n\n"
    ))
    assert cC == 78
    assert wC == 14
    assert pC == 2

# END Test testCoreIndex_countWords
