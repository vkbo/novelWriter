# -*- coding: utf-8 -*-
"""novelWriter Project Class Tester
"""

import pytest

from nw.core.project import NWProject
from nw.core.index import NWIndex
from nw.constants import nwItemClass

@pytest.mark.project
def testIndexScanThis(nwMinimal, nwDummy):

    theProject = NWProject(nwDummy)
    theProject.projTree.setSeed(42)
    assert theProject.openProject(nwMinimal)

    theIndex = NWIndex(theProject, nwDummy)

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
    assert str(theBits) == "['@a']"
    assert str(thePos)  == "[0]"

    isValid, theBits, thePos = theIndex.scanThis("@a:b")
    assert isValid
    assert str(theBits) == "['@a', 'b']"
    assert str(thePos)  == "[0, 3]"

    isValid, theBits, thePos = theIndex.scanThis("@a:b,c,d")
    assert isValid
    assert str(theBits) == "['@a', 'b', 'c', 'd']"
    assert str(thePos)  == "[0, 3, 5, 7]"

    isValid, theBits, thePos = theIndex.scanThis("@a : b , c , d")
    assert isValid
    assert str(theBits) == "['@a', 'b', 'c', 'd']"
    assert str(thePos)  == "[0, 5, 9, 13]"

    isValid, theBits, thePos = theIndex.scanThis("@tag: this, and this")
    assert isValid
    assert str(theBits) == "['@tag', 'this', 'and this']"
    assert str(thePos)  == "[0, 6, 12]"

    assert theProject.closeProject()

@pytest.mark.project
def testIndexCheckThese(nwMinimal, nwDummy):

    theProject = NWProject(nwDummy)
    theProject.projTree.setSeed(42)
    assert theProject.openProject(nwMinimal)

    theIndex = NWIndex(theProject, nwDummy)
    nHandle = theProject.newFile("Hello", nwItemClass.NOVEL,     "a508bb932959c")
    cHandle = theProject.newFile("Jane",  nwItemClass.CHARACTER, "afb3043c7b2b3")
    nItem = theProject.projTree[nHandle]
    cItem = theProject.projTree[cHandle]

    assert theIndex.scanText(cHandle, (
        "# Jane Smith\n"
        "@tag: Jane"
    ))
    assert theIndex.scanText(nHandle, (
        "# Hello World!\n"
        "@pov: Jane"
    ))
    assert str(theIndex.tagIndex) == "{'Jane': [2, '%s', 'CHARACTER', 'T000001']}" % cHandle
    assert theIndex.novelIndex[nHandle]["T000001"]["title"] == "Hello World!"

    assert str(theIndex.checkThese(["@tag",  "Jane"], cItem)) == "[True, True]"
    assert str(theIndex.checkThese(["@tag",  "John"], cItem)) == "[True, True]"
    assert str(theIndex.checkThese(["@tag",  "Jane"], nItem)) == "[True, False]"
    assert str(theIndex.checkThese(["@tag",  "John"], nItem)) == "[True, True]"
    assert str(theIndex.checkThese(["@pov",  "John"], nItem)) == "[True, False]"
    assert str(theIndex.checkThese(["@pov",  "Jane"], nItem)) == "[True, True]"
    assert str(theIndex.checkThese(["@ pov", "Jane"], nItem)) == "[False, False]"
    assert str(theIndex.checkThese(["@what", "Jane"], nItem)) == "[False, False]"

    assert theProject.closeProject()

@pytest.mark.project
def testIndexMeta(nwMinimal, nwDummy):

    theProject = NWProject(nwDummy)
    theProject.projTree.setSeed(42)
    assert theProject.openProject(nwMinimal)

    theIndex = NWIndex(theProject, nwDummy)
    nHandle = theProject.newFile("Hello", nwItemClass.NOVEL,     "a508bb932959c")
    cHandle = theProject.newFile("Jane",  nwItemClass.CHARACTER, "afb3043c7b2b3")

    assert theIndex.scanText(cHandle, (
        "# Jane Smith\n"
        "@tag: Jane\n"
    ))
    assert theIndex.scanText(nHandle, (
        "# Hello World!\n"
        "@pov: Jane\n"
        "@char: Jane\n"
        "\n"
        "% this is a comment\n"
        "\n"
        "This is a story about Jane Smith.\n"
        "\n"
        "Well, not really.\n"
    ))
    assert str(theIndex.tagIndex) == "{'Jane': [2, '%s', 'CHARACTER', 'T000001']}" % cHandle
    assert theIndex.novelIndex[nHandle]["T000001"]["title"] == "Hello World!"

    # The novel structure should contain the pointer to the novel file header
    assert str(theIndex.getNovelStructure()) == "['%s:T000001']" % nHandle

    # The novel file should have the correct counts
    cC, wC, pC = theIndex.getCounts(nHandle)
    assert cC == 62 # Characters in text and title only
    assert wC == 12 # Words in text and title only
    assert pC == 2  # Paragraphs in text only

    # Look up an ivalid handle
    theRefs = theIndex.getReferences("Not a handle")
    assert theRefs["@pov"] == []
    assert theRefs["@char"] == []

    # The novel file should now refer to Jane as @pov and @char
    theRefs = theIndex.getReferences(nHandle)
    assert str(theRefs["@pov"]) == "['Jane']"
    assert str(theRefs["@char"]) == "['Jane']"

    # The character file should have a record of the reference from the novel file
    theRefs = theIndex.getBackReferenceList(cHandle)
    assert str(theRefs) == "{'%s': 'T000001'}" % nHandle

    # Get section counts for a novel file
    assert theIndex.scanText(nHandle, (
        "# Hello World!\n"
        "@pov: Jane\n"
        "@char: Jane\n"
        "\n"
        "% this is a comment\n"
        "\n"
        "This is a story about Jane Smith.\n"
        "\n"
        "Well, not really.\n"
        "\n"
        "# Hello World!\n"
        "@pov: Jane\n"
        "@char: Jane\n"
        "\n"
        "% this is a comment\n"
        "\n"
        "This is a story about Jane Smith.\n"
        "\n"
        "Well, not really.\n"
    ))
    # Whole document
    cC, wC, pC = theIndex.getCounts(nHandle)
    assert cC == 124
    assert wC == 24
    assert pC == 4

    # First part
    cC, wC, pC = theIndex.getCounts(nHandle, "T000001")
    assert cC == 62
    assert wC == 12
    assert pC == 2

    # First part
    cC, wC, pC = theIndex.getCounts(nHandle, "T000011")
    assert cC == 62
    assert wC == 12
    assert pC == 2

    # Get section counts for a note file
    assert theIndex.scanText(cHandle, (
        "# Hello World!\n"
        "@pov: Jane\n"
        "@char: Jane\n"
        "\n"
        "% this is a comment\n"
        "\n"
        "This is a story about Jane Smith.\n"
        "\n"
        "Well, not really.\n"
        "\n"
        "# Hello World!\n"
        "@pov: Jane\n"
        "@char: Jane\n"
        "\n"
        "% this is a comment\n"
        "\n"
        "This is a story about Jane Smith.\n"
        "\n"
        "Well, not really.\n"
    ))
    # Whole document
    cC, wC, pC = theIndex.getCounts(cHandle)
    assert cC == 124
    assert wC == 24
    assert pC == 4

    # First part
    cC, wC, pC = theIndex.getCounts(cHandle, "T000001")
    assert cC == 62
    assert wC == 12
    assert pC == 2

    # First part
    cC, wC, pC = theIndex.getCounts(cHandle, "T000011")
    assert cC == 62
    assert wC == 12
    assert pC == 2

    assert theProject.closeProject()
