# -*- coding: utf-8 -*-
"""
novelWriter – NWIndex Class Tester
==================================

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

import pytest
import os
import json

from shutil import copyfile

from tools import cmpFiles

from nw.core.project import NWProject
from nw.core.index import NWIndex
from nw.constants import nwItemClass, nwItemLayout

@pytest.mark.core
def testCoreIndex_LoadSave(monkeypatch, nwLipsum, dummyGUI, outDir, refDir):
    """Test core functionality of scaning, saving, loading and checking
    the index cache file.
    """
    projFile = os.path.join(nwLipsum, "meta", "tagsIndex.json")
    testFile = os.path.join(outDir, "coreIndex_LoadSave_tagsIndex.json")
    compFile = os.path.join(refDir, "coreIndex_LoadSave_tagsIndex.json")

    theProject = NWProject(dummyGUI)
    theProject.projTree.setSeed(42)
    assert theProject.openProject(nwLipsum)

    monkeypatch.setattr("nw.core.index.time", lambda: 123.4)

    theIndex = NWIndex(theProject, dummyGUI)
    notIndexable = {
        "b3643d0f92e32": False, # Novel ROOT
        "45e6b01ca35c1": False, # Chapter One FOLDER
        "6bd935d2490cd": False, # Chapter Two FOLDER
        "67a8707f2f249": False, # Character ROOT
        "6c6afb1247750": False, # Plot ROOT
        "60bdf227455cc": False, # World ROOT
    }
    for tItem in theProject.projTree:
        assert theIndex.reIndexHandle(tItem.itemHandle) is notIndexable.get(tItem.itemHandle, True)

    assert not theIndex.reIndexHandle(None)

    # Dummy exception function
    def doPanic(*arg, **kwargs):
        raise Exception

    # Make the save fail
    monkeypatch.setattr(json, "dump", doPanic)
    assert not theIndex.saveIndex()

    # Make the save pass
    monkeypatch.undo()
    assert theIndex.saveIndex()

    # Take a copy of the index
    tagIndex = str(theIndex._tagIndex)
    refIndex = str(theIndex._refIndex)
    novelIndex = str(theIndex._novelIndex)
    noteIndex = str(theIndex._noteIndex)
    textCounts = str(theIndex._textCounts)

    # Delete a handle
    assert theIndex._tagIndex.get("Bod", None) is not None
    assert theIndex._refIndex.get("4c4f28287af27", None) is not None
    assert theIndex._noteIndex.get("4c4f28287af27", None) is not None
    assert theIndex._textCounts.get("4c4f28287af27", None) is not None
    theIndex.deleteHandle("4c4f28287af27")
    assert theIndex._tagIndex.get("Bod", None) is None
    assert theIndex._refIndex.get("4c4f28287af27", None) is None
    assert theIndex._noteIndex.get("4c4f28287af27", None) is None
    assert theIndex._textCounts.get("4c4f28287af27", None) is None

    # Clear the index
    theIndex.clearIndex()
    assert not theIndex._tagIndex
    assert not theIndex._refIndex
    assert not theIndex._novelIndex
    assert not theIndex._noteIndex
    assert not theIndex._textCounts

    # Make the load fail
    monkeypatch.setattr(json, "load", doPanic)
    assert not theIndex.loadIndex()

    # Make the load pass
    monkeypatch.undo()
    assert theIndex.loadIndex()

    assert str(theIndex._tagIndex) == tagIndex
    assert str(theIndex._refIndex) == refIndex
    assert str(theIndex._novelIndex) == novelIndex
    assert str(theIndex._noteIndex) == noteIndex
    assert str(theIndex._textCounts) == textCounts

    # Break the index and check that we notice
    assert not theIndex.indexBroken
    theIndex._tagIndex["Bod"].append("Stuff") # No longer len() == 4
    theIndex.checkIndex()
    assert theIndex.indexBroken

    assert theIndex.loadIndex()
    assert not theIndex.indexBroken
    theIndex._refIndex["fb609cd8319dc"]["T000001"]["tags"].append("Stuff") # No longer len() == 3
    theIndex.checkIndex()
    assert theIndex.indexBroken

    assert theIndex.loadIndex()
    assert not theIndex.indexBroken
    theIndex._novelIndex["7a992350f3eb6"]["T000001"]["Stuff"] = "" # No longer len(keys()) == 8
    theIndex.checkIndex()
    assert theIndex.indexBroken

    assert theIndex.loadIndex()
    assert not theIndex.indexBroken
    theIndex._noteIndex["4c4f28287af27"]["T000001"]["Stuff"] = "" # No longer len(keys()) == 8
    theIndex.checkIndex()
    assert theIndex.indexBroken

    assert theIndex.loadIndex()
    assert not theIndex.indexBroken
    theIndex._textCounts["7a992350f3eb6"].append("Stuff") # No longer len() == 3
    theIndex.checkIndex()
    assert theIndex.indexBroken

    # Make the try/except trigger as well
    assert theIndex.loadIndex()
    assert not theIndex.indexBroken
    theIndex._refIndex["fb609cd8319dc"]["T000001"] = {"tagssss": []} # Wrong key name
    theIndex.checkIndex()
    assert theIndex.indexBroken

    # Finalise
    assert theProject.closeProject()

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

# END Test testCoreIndex_LoadSave

@pytest.mark.core
def testCoreIndex_ScanThis(nwMinimal, dummyGUI):
    """Test the tag scanner function scanThis.
    """
    theProject = NWProject(dummyGUI)
    theProject.projTree.setSeed(42)
    assert theProject.openProject(nwMinimal)

    theIndex = NWIndex(theProject, dummyGUI)

    isValid, theBits, thePos = theIndex.scanThis("tag: this, and this")
    assert not isValid

    isValid, theBits, thePos = theIndex.scanThis("@")
    assert not isValid

    isValid, theBits, thePos = theIndex.scanThis("@:")
    assert not isValid

    isValid, theBits, thePos = theIndex.scanThis(" @a: b")
    assert not isValid

    isValid, theBits, thePos = theIndex.scanThis("@a:")
    assert isValid
    assert theBits == ["@a"]
    assert thePos  == [0]

    isValid, theBits, thePos = theIndex.scanThis("@a:b")
    assert isValid
    assert theBits == ["@a", "b"]
    assert thePos  == [0, 3]

    isValid, theBits, thePos = theIndex.scanThis("@a:b,c,d")
    assert isValid
    assert theBits == ["@a", "b", "c", "d"]
    assert thePos  == [0, 3, 5, 7]

    isValid, theBits, thePos = theIndex.scanThis("@a : b , c , d")
    assert isValid
    assert theBits == ["@a", "b", "c", "d"]
    assert thePos  == [0, 5, 9, 13]

    isValid, theBits, thePos = theIndex.scanThis("@tag: this, and this")
    assert isValid
    assert theBits == ["@tag", "this", "and this"]
    assert thePos  == [0, 6, 12]

    assert theProject.closeProject()

# END Test testCoreIndex_ScanThis

@pytest.mark.core
def testCoreIndex_CheckThese(nwMinimal, dummyGUI):
    """Test the tag checker function checkThese.
    """
    theProject = NWProject(dummyGUI)
    theProject.projTree.setSeed(42)
    assert theProject.openProject(nwMinimal)

    theIndex = NWIndex(theProject, dummyGUI)
    nHandle = theProject.newFile("Hello", nwItemClass.NOVEL,     "a508bb932959c")
    cHandle = theProject.newFile("Jane",  nwItemClass.CHARACTER, "afb3043c7b2b3")
    nItem = theProject.projTree[nHandle]
    cItem = theProject.projTree[cHandle]

    assert not theIndex.novelChangedSince(0)
    assert not theIndex.notesChangedSince(0)
    assert not theIndex.indexChangedSince(0)

    assert theIndex.scanText(cHandle, (
        "# Jane Smith\n"
        "@tag: Jane"
    ))
    assert theIndex.scanText(nHandle, (
        "# Hello World!\n"
        "@pov: Jane"
    ))
    assert theIndex._tagIndex == {"Jane": [2, cHandle, "CHARACTER", "T000001"]}
    assert theIndex.getNovelData(nHandle, "T000001")["title"] == "Hello World!"

    assert theIndex.novelChangedSince(0)
    assert theIndex.notesChangedSince(0)
    assert theIndex.indexChangedSince(0)

    assert theIndex.checkThese([], cItem) == []
    assert theIndex.checkThese(["@tag",  "Jane"], cItem) == [True, True]
    assert theIndex.checkThese(["@tag",  "John"], cItem) == [True, True]
    assert theIndex.checkThese(["@tag",  "Jane"], nItem) == [True, False]
    assert theIndex.checkThese(["@tag",  "John"], nItem) == [True, True]
    assert theIndex.checkThese(["@pov",  "John"], nItem) == [True, False]
    assert theIndex.checkThese(["@pov",  "Jane"], nItem) == [True, True]
    assert theIndex.checkThese(["@ pov", "Jane"], nItem) == [False, False]
    assert theIndex.checkThese(["@what", "Jane"], nItem) == [False, False]

    assert theProject.closeProject()

# END Test testCoreIndex_CheckThese

@pytest.mark.core
def testCoreIndex_ScanText(nwMinimal, dummyGUI):
    """Check the index text scanner.
    """
    theProject = NWProject(dummyGUI)
    theProject.projTree.setSeed(42)
    assert theProject.openProject(nwMinimal)

    theIndex = NWIndex(theProject, dummyGUI)

    # Some items for fail to scan tests
    dHandle = theProject.newFolder("Folder", nwItemClass.NOVEL, "a508bb932959c")
    xHandle = theProject.newFile("No Layout", nwItemClass.NOVEL, "a508bb932959c")
    xItem = theProject.projTree[xHandle]
    xItem.setLayout(nwItemLayout.NO_LAYOUT)

    # Check invalid data
    assert not theIndex.scanText(None, "Hello World!")
    assert not theIndex.scanText(dHandle, "Hello World!")
    assert not theIndex.scanText(xHandle, "Hello World!")

    xItem.setLayout(nwItemLayout.SCENE)
    xItem.setParent(None)
    assert not theIndex.scanText(xHandle, "Hello World!")

    # Create the trash folder
    tHandle = theProject.trashFolder()
    assert theProject.projTree[tHandle] is not None
    xItem.setParent(tHandle)
    assert not theIndex.scanText(xHandle, "Hello World!")

    # Create the archive root
    aHandle = theProject.newRoot("Outtakes", nwItemClass.ARCHIVE)
    assert theProject.projTree[aHandle] is not None
    xItem.setParent(aHandle)
    assert not theIndex.scanText(xHandle, "Hello World!")

    # Make some usable items
    pHandle = theProject.newFile("Page",  nwItemClass.NOVEL, "a508bb932959c")
    nHandle = theProject.newFile("Hello", nwItemClass.NOVEL, "a508bb932959c")
    cHandle = theProject.newFile("Jane",  nwItemClass.CHARACTER, "afb3043c7b2b3")
    sHandle = theProject.newFile("Scene", nwItemClass.NOVEL, "a508bb932959c")

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
    assert str(theIndex._tagIndex) == "{'Jane': [2, '%s', 'CHARACTER', 'T000001']}" % cHandle
    assert theIndex.getNovelData(nHandle, "T000001")["title"] == "Hello World!"

    # Check that title sections are indexed properly
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
        "##### Title Five\n\n" # Not interpreted as a title, the hashes are counted as a word
        "Paragraph Five.\n\n"
    ))
    assert theIndex._refIndex[nHandle].get("T000000", None) is not None # Always there
    assert theIndex._refIndex[nHandle].get("T000001", None) is not None # Heading 1
    assert theIndex._refIndex[nHandle].get("T000002", None) is None
    assert theIndex._refIndex[nHandle].get("T000003", None) is None
    assert theIndex._refIndex[nHandle].get("T000004", None) is None
    assert theIndex._refIndex[nHandle].get("T000005", None) is None
    assert theIndex._refIndex[nHandle].get("T000006", None) is None
    assert theIndex._refIndex[nHandle].get("T000007", None) is not None # Heading 2
    assert theIndex._refIndex[nHandle].get("T000008", None) is None
    assert theIndex._refIndex[nHandle].get("T000009", None) is None
    assert theIndex._refIndex[nHandle].get("T000010", None) is None
    assert theIndex._refIndex[nHandle].get("T000011", None) is None
    assert theIndex._refIndex[nHandle].get("T000012", None) is None
    assert theIndex._refIndex[nHandle].get("T000013", None) is not None # Heading 3
    assert theIndex._refIndex[nHandle].get("T000014", None) is None
    assert theIndex._refIndex[nHandle].get("T000015", None) is None
    assert theIndex._refIndex[nHandle].get("T000016", None) is None
    assert theIndex._refIndex[nHandle].get("T000017", None) is None
    assert theIndex._refIndex[nHandle].get("T000018", None) is None
    assert theIndex._refIndex[nHandle].get("T000019", None) is not None # Heading 4
    assert theIndex._refIndex[nHandle].get("T000020", None) is None
    assert theIndex._refIndex[nHandle].get("T000021", None) is None
    assert theIndex._refIndex[nHandle].get("T000022", None) is None
    assert theIndex._refIndex[nHandle].get("T000023", None) is None
    assert theIndex._refIndex[nHandle].get("T000024", None) is None
    assert theIndex._refIndex[nHandle].get("T000025", None) is None
    assert theIndex._refIndex[nHandle].get("T000026", None) is None

    assert theIndex._novelIndex[nHandle]["T000001"]["level"] == "H1"
    assert theIndex._novelIndex[nHandle]["T000007"]["level"] == "H2"
    assert theIndex._novelIndex[nHandle]["T000013"]["level"] == "H3"
    assert theIndex._novelIndex[nHandle]["T000019"]["level"] == "H4"

    assert theIndex._novelIndex[nHandle]["T000001"]["title"] == "Title One"
    assert theIndex._novelIndex[nHandle]["T000007"]["title"] == "Title Two"
    assert theIndex._novelIndex[nHandle]["T000013"]["title"] == "Title Three"
    assert theIndex._novelIndex[nHandle]["T000019"]["title"] == "Title Four"

    assert theIndex._novelIndex[nHandle]["T000001"]["layout"] == "SCENE"
    assert theIndex._novelIndex[nHandle]["T000007"]["layout"] == "SCENE"
    assert theIndex._novelIndex[nHandle]["T000013"]["layout"] == "SCENE"
    assert theIndex._novelIndex[nHandle]["T000019"]["layout"] == "SCENE"

    assert theIndex._novelIndex[nHandle]["T000001"]["synopsis"] == "Synopsis One."
    assert theIndex._novelIndex[nHandle]["T000007"]["synopsis"] == "Synopsis Two."
    assert theIndex._novelIndex[nHandle]["T000013"]["synopsis"] == "Synopsis Three."
    assert theIndex._novelIndex[nHandle]["T000019"]["synopsis"] == "Synopsis Four."

    assert theIndex._novelIndex[nHandle]["T000001"]["cCount"] == 23
    assert theIndex._novelIndex[nHandle]["T000007"]["cCount"] == 23
    assert theIndex._novelIndex[nHandle]["T000013"]["cCount"] == 27
    assert theIndex._novelIndex[nHandle]["T000019"]["cCount"] == 56

    assert theIndex._novelIndex[nHandle]["T000001"]["wCount"] == 4
    assert theIndex._novelIndex[nHandle]["T000007"]["wCount"] == 4
    assert theIndex._novelIndex[nHandle]["T000013"]["wCount"] == 4
    assert theIndex._novelIndex[nHandle]["T000019"]["wCount"] == 9

    assert theIndex._novelIndex[nHandle]["T000001"]["pCount"] == 1
    assert theIndex._novelIndex[nHandle]["T000007"]["pCount"] == 1
    assert theIndex._novelIndex[nHandle]["T000013"]["pCount"] == 1
    assert theIndex._novelIndex[nHandle]["T000019"]["pCount"] == 3

    assert theIndex.scanText(cHandle, (
        "# Title One\n\n"
        "@tag: One\n\n"
        "% synopsis: Synopsis One.\n\n"
        "Paragraph One.\n\n"
    ))
    assert theIndex._refIndex[cHandle].get("T000000", None) is not None
    assert theIndex._refIndex[cHandle].get("T000001", None) is not None
    assert theIndex._refIndex[cHandle].get("T000002", None) is None
    assert theIndex._refIndex[cHandle].get("T000003", None) is None
    assert theIndex._refIndex[cHandle].get("T000004", None) is None
    assert theIndex._refIndex[cHandle].get("T000005", None) is None
    assert theIndex._refIndex[cHandle].get("T000006", None) is None
    assert theIndex._refIndex[cHandle].get("T000007", None) is None

    assert theIndex._noteIndex[cHandle]["T000001"]["level"] == "H1"
    assert theIndex._noteIndex[cHandle]["T000001"]["title"] == "Title One"
    assert theIndex._noteIndex[cHandle]["T000001"]["layout"] == "NOTE"
    assert theIndex._noteIndex[cHandle]["T000001"]["synopsis"] == "Synopsis One."
    assert theIndex._noteIndex[cHandle]["T000001"]["cCount"] == 23
    assert theIndex._noteIndex[cHandle]["T000001"]["wCount"] == 4
    assert theIndex._noteIndex[cHandle]["T000001"]["pCount"] == 1

    assert theIndex.scanText(sHandle, (
        "# Title One\n\n"
        "@pov: One\n\n" # Valid
        "@char: Two\n\n" # Invalid tag
        "@:\n\n" # Invalid line
        "% synopsis: Synopsis One.\n\n"
        "Paragraph One.\n\n"
    ))
    assert theIndex._refIndex[sHandle]["T000001"]["tags"] == (
        [[3, "@pov", "One"], [5, "@char", "Two"]]
    )

    # Page wo/Title
    theProject.projTree[pHandle].itemLayout = nwItemLayout.PAGE
    assert theIndex.scanText(pHandle, (
        "This is a page with some text on it.\n\n"
    ))
    assert theIndex._novelIndex[pHandle]["T000000"]["level"] == "H0"
    assert theIndex._novelIndex[pHandle]["T000000"]["title"] == "Untitled Page"
    assert theIndex._novelIndex[pHandle]["T000000"]["layout"] == "PAGE"
    assert theIndex._novelIndex[pHandle]["T000000"]["synopsis"] == ""
    assert theIndex._novelIndex[pHandle]["T000000"]["cCount"] == 36
    assert theIndex._novelIndex[pHandle]["T000000"]["wCount"] == 9
    assert theIndex._novelIndex[pHandle]["T000000"]["pCount"] == 1
    assert pHandle not in theIndex._noteIndex

    theProject.projTree[pHandle].itemLayout = nwItemLayout.NOTE
    assert theIndex.scanText(pHandle, (
        "This is a page with some text on it.\n\n"
    ))
    assert theIndex._noteIndex[pHandle]["T000000"]["level"] == "H0"
    assert theIndex._noteIndex[pHandle]["T000000"]["title"] == "Untitled Page"
    assert theIndex._noteIndex[pHandle]["T000000"]["layout"] == "NOTE"
    assert theIndex._noteIndex[pHandle]["T000000"]["synopsis"] == ""
    assert theIndex._noteIndex[pHandle]["T000000"]["cCount"] == 36
    assert theIndex._noteIndex[pHandle]["T000000"]["wCount"] == 9
    assert theIndex._noteIndex[pHandle]["T000000"]["pCount"] == 1
    assert pHandle not in theIndex._novelIndex

    assert theProject.closeProject()

# END Test testCoreIndex_ScanText

@pytest.mark.core
def testCoreIndex_ExtractData(nwMinimal, dummyGUI):
    """Check the index data extraction functions.
    """
    theProject = NWProject(dummyGUI)
    theProject.projTree.setSeed(42)
    assert theProject.openProject(nwMinimal)

    theIndex = NWIndex(theProject, dummyGUI)
    nHandle = theProject.newFile("Hello", nwItemClass.NOVEL,     "a508bb932959c")
    cHandle = theProject.newFile("Jane",  nwItemClass.CHARACTER, "afb3043c7b2b3")

    assert theIndex.getNovelData("", "") is None
    assert theIndex.getNovelData("a508bb932959c", "") is None

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

    assert theKeys == ["%s:T000001" % nHandle]

    # Check that excluded files can be skipped
    theProject.projTree[nHandle].setExported(False)

    theKeys = []
    for aKey, _, _, _ in theIndex.novelStructure(skipExcluded=False):
        theKeys.append(aKey)

    assert theKeys == ["%s:T000001" % nHandle]

    theKeys = []
    for aKey, _, _, _ in theIndex.novelStructure(skipExcluded=True):
        theKeys.append(aKey)

    assert theKeys == []

    theKeys = []
    for aKey, _, _, _ in theIndex.novelStructure():
        theKeys.append(aKey)

    assert theKeys == []

    # The novel file should have the correct counts
    cC, wC, pC = theIndex.getCounts(nHandle)
    assert cC == 62 # Characters in text and title only
    assert wC == 12 # Words in text and title only
    assert pC == 2  # Paragraphs in text only

    ##
    #  getReferences
    ##

    # Look up an ivalid handle
    theRefs = theIndex.getReferences("Not a handle")
    assert theRefs["@pov"] == []
    assert theRefs["@char"] == []

    # The novel file should now refer to Jane as @pov and @char
    theRefs = theIndex.getReferences(nHandle)
    assert theRefs["@pov"] == ["Jane"]
    assert theRefs["@char"] == ["Jane"]

    ##
    #  getBackReferenceList
    ##

    # None handle should return an empty dict
    assert theIndex.getBackReferenceList(None) == {}

    # The character file should have a record of the reference from the novel file
    theRefs = theIndex.getBackReferenceList(cHandle)
    assert theRefs == {nHandle: "T000001"}

    ##
    #  getTagSource
    ##

    assert theIndex.getTagSource("Jane") == (cHandle, 2, "T000001")
    assert theIndex.getTagSource("John") == (None, 0, "T000000")

    ##
    #  getCounts for whole text and sections
    ##

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

    # First part
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

    # First part
    cC, wC, pC = theIndex.getCounts(cHandle, "T000011")
    assert cC == 90
    assert wC == 16
    assert pC == 2

    ##
    #  Novel Stats
    ##

    hHandle = theProject.newFile("Chapter", nwItemClass.NOVEL, "a508bb932959c")
    sHandle = theProject.newFile("Scene One", nwItemClass.NOVEL, "a508bb932959c")
    tHandle = theProject.newFile("Scene Two", nwItemClass.NOVEL, "a508bb932959c")

    theProject.projTree[hHandle].itemLayout == nwItemLayout.CHAPTER
    theProject.projTree[sHandle].itemLayout == nwItemLayout.SCENE
    theProject.projTree[tHandle].itemLayout == nwItemLayout.SCENE

    assert theIndex.scanText(hHandle, "## Chapter One\n\n")
    assert theIndex.scanText(sHandle, "### Scene One\n\n")
    assert theIndex.scanText(tHandle, "### Scene Two\n\n")

    assert theIndex._listNovelHandles(False) == [nHandle, hHandle, sHandle, tHandle]
    assert theIndex._listNovelHandles(True) == [hHandle, sHandle, tHandle]

    # Add a fake handle to the tree and check that it's ignored
    theProject.projTree._treeOrder.append("0000000000000")
    assert theIndex._listNovelHandles(False) == [nHandle, hHandle, sHandle, tHandle]
    theProject.projTree._treeOrder.remove("0000000000000")

    # Extract stats
    assert theIndex.getNovelWordCount(False) == 34
    assert theIndex.getNovelWordCount(True) == 6
    assert theIndex.getNovelTitleCounts(False) == [0, 2, 1, 2, 0]
    assert theIndex.getNovelTitleCounts(True) == [0, 0, 1, 2, 0]

    # Table of Contents
    assert theIndex.getTableOfContents(0, True) == []
    assert theIndex.getTableOfContents(1, True) == []
    assert theIndex.getTableOfContents(2, True) == [
        ("%s:T000001" % hHandle, 2, "Chapter One", 6),
    ]
    assert theIndex.getTableOfContents(3, True) == [
        ("%s:T000001" % hHandle, 2, "Chapter One", 2),
        ("%s:T000001" % sHandle, 3, "Scene One", 2),
        ("%s:T000001" % tHandle, 3, "Scene Two", 2),
    ]

    assert theIndex.getTableOfContents(0, False) == []
    assert theIndex.getTableOfContents(1, False) == [
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

    assert theProject.closeProject()

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
