# -*- coding: utf-8 -*-
"""novelWriter Project Class Tester
"""

import pytest
from os import path
from shutil import copyfile

from nwtools import cmpFiles

from nw.core.project import NWProject
from nw.core.document import NWDoc
from nw.core.index import NWIndex
from nw.core.spellcheck import NWSpellEnchant, NWSpellSimple
from nw.constants import nwItemClass, nwItemLayout

@pytest.mark.project
def testProjectNewOpenSave(nwFuncTemp, nwTempProj, nwRef, nwTemp, nwDummy):
    projFile = path.join(nwFuncTemp, "nwProject.nwx")
    testFile = path.join(nwTempProj, "1_nwProject.nwx")
    refFile  = path.join(nwRef, "proj", "1_nwProject.nwx")

    theProject = NWProject(nwDummy)
    theProject.projTree.setSeed(42)

    assert theProject.newProject({"projPath": nwFuncTemp})
    assert theProject.setProjectPath(nwFuncTemp)
    assert theProject.saveProject()
    assert theProject.closeProject()

    # Check the new project
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [2, 6, 7, 8])

    # Open again
    assert theProject.openProject(projFile)

    # Save and close
    assert theProject.saveProject()
    assert theProject.closeProject()
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [2, 6, 7, 8])
    assert not theProject.projChanged

    # Open a second time
    assert theProject.openProject(projFile)
    assert not theProject.openProject(projFile)
    assert theProject.openProject(projFile, overrideLock=True)
    assert theProject.saveProject()
    assert theProject.closeProject()
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [2, 6, 7, 8])

@pytest.mark.project
def testProjectNewRoot(nwFuncTemp, nwTempProj, nwRef, nwDummy):
    projFile = path.join(nwFuncTemp, "nwProject.nwx")
    testFile = path.join(nwTempProj, "2_nwProject.nwx")
    refFile  = path.join(nwRef, "proj", "2_nwProject.nwx")

    theProject = NWProject(nwDummy)
    theProject.projTree.setSeed(42)

    assert theProject.newProject({"projPath": nwFuncTemp})
    assert theProject.setProjectPath(nwFuncTemp)
    assert theProject.saveProject()
    assert theProject.closeProject()
    assert theProject.openProject(projFile)

    assert isinstance(theProject.newRoot("Novel",     nwItemClass.NOVEL),     type(None))
    assert isinstance(theProject.newRoot("Plot",      nwItemClass.PLOT),      type(None))
    assert isinstance(theProject.newRoot("Character", nwItemClass.CHARACTER), type(None))
    assert isinstance(theProject.newRoot("World",     nwItemClass.WORLD),     type(None))
    assert isinstance(theProject.newRoot("Timeline",  nwItemClass.TIMELINE),  str)
    assert isinstance(theProject.newRoot("Object",    nwItemClass.OBJECT),    str)
    assert isinstance(theProject.newRoot("Custom1",   nwItemClass.CUSTOM),    str)
    assert isinstance(theProject.newRoot("Custom2",   nwItemClass.CUSTOM),    str)

    assert theProject.projChanged
    assert theProject.saveProject()
    assert theProject.closeProject()

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [2, 6, 7, 8])
    assert not theProject.projChanged

@pytest.mark.project
def testProjectNewFile(nwFuncTemp, nwTempProj, nwRef, nwDummy):
    projFile = path.join(nwFuncTemp, "nwProject.nwx")
    testFile = path.join(nwTempProj, "3_nwProject.nwx")
    refFile  = path.join(nwRef, "proj", "3_nwProject.nwx")

    theProject = NWProject(nwDummy)
    theProject.projTree.setSeed(42)

    assert theProject.newProject({"projPath": nwFuncTemp})
    assert theProject.setProjectPath(nwFuncTemp)
    assert theProject.saveProject()
    assert theProject.closeProject()
    assert theProject.openProject(projFile)

    assert isinstance(theProject.newFile("Hello", nwItemClass.NOVEL,     "31489056e0916"), str)
    assert isinstance(theProject.newFile("Jane",  nwItemClass.CHARACTER, "71ee45a3c0db9"), str)
    assert theProject.projChanged
    assert theProject.saveProject()
    assert theProject.closeProject()

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [2, 6, 7, 8])
    assert not theProject.projChanged

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

    # The novel file should now refer to Jane as @pov and @char
    theRefs = theIndex.getReferences(nHandle)
    assert str(theRefs["@pov"]) == "['Jane']"
    assert str(theRefs["@char"]) == "['Jane']"

    # The character file should have a record of the reference from the novel file
    theRefs = theIndex.getBackReferenceList(cHandle)
    assert str(theRefs) == "{'%s': 'T000001'}" % nHandle

    assert theProject.closeProject()

@pytest.mark.project
def testProjectNewCustom(nwFuncTemp, nwTempProj, nwRef, nwDummy):

    projFile = path.join(nwFuncTemp, "nwProject.nwx")
    testFile = path.join(nwTempProj, "4_nwProject.nwx")
    refFile  = path.join(nwRef, "proj", "4_nwProject.nwx")

    projData = {
        "projName": "Test Custom",
        "projTitle": "Test Novel",
        "projAuthors": "Jane Doe\nJohn Doh\n",
        "projPath": nwFuncTemp,
        "popSample": False,
        "popMinimal": False,
        "popCustom": True,
        "addRoots": [
            nwItemClass.PLOT,
            nwItemClass.CHARACTER,
            nwItemClass.WORLD,
            nwItemClass.TIMELINE,
            nwItemClass.OBJECT,
            nwItemClass.ENTITY,
        ],
        "numChapters": 3,
        "numScenes": 3,
        "chFolders": True,
    }
    theProject = NWProject(nwDummy)
    theProject.projTree.setSeed(42)

    assert theProject.newProject(projData)
    assert theProject.saveProject()
    assert theProject.closeProject()

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [2, 6, 7, 8])

@pytest.mark.project
def testProjectNewSample(nwFuncTemp, nwRef, nwConf, nwDummy):
    projData = {
        "projName": "Test Sample",
        "projTitle": "Test Novel",
        "projAuthors": "Jane Doe\nJohn Doh\n",
        "projPath": nwFuncTemp,
        "popSample": True,
        "popMinimal": False,
        "popCustom": False,
    }
    theProject = NWProject(nwDummy)
    theProject.projTree.setSeed(42)
    theProject.mainConf = nwConf

    assert theProject.newProject(projData)
    assert theProject.openProject(nwFuncTemp)
    assert theProject.projName == "Sample Project"
    assert theProject.saveProject()
    assert theProject.closeProject()

@pytest.mark.project
def testDocMeta(nwDummy, nwLipsum):
    theProject = NWProject(nwDummy)
    theProject.projTree.setSeed(42)
    assert theProject.openProject(nwLipsum)

    aDoc = NWDoc(theProject, nwDummy)
    assert aDoc.openDocument("47666c91c7ccf")
    theMeta, thePath, theClass, theLayout = aDoc.getMeta()

    assert theMeta == "Scene Five"
    assert len(thePath) == 3
    assert thePath[0] == "47666c91c7ccf"
    assert thePath[1] == "6bd935d2490cd"
    assert thePath[2] == "b3643d0f92e32"
    assert theClass == nwItemClass.NOVEL
    assert theLayout == nwItemLayout.SCENE

    aDoc._docMeta = "too_short"
    theMeta, thePath, theClass, theLayout = aDoc.getMeta()
    assert theMeta == ""
    assert thePath == []
    assert theClass is None
    assert theLayout is None

@pytest.mark.project
def testSpellEnchant(nwTemp, nwConf):
    wList = path.join(nwTemp, "wordlist.txt")
    with open(wList, mode="w") as wFile:
        wFile.write("a_word\nb_word\nc_word\n")

    spChk = NWSpellEnchant()
    spChk.mainConf = nwConf
    spChk.setLanguage("en", wList)

    assert spChk.checkWord("a_word")
    assert spChk.checkWord("b_word")
    assert spChk.checkWord("c_word")
    assert not spChk.checkWord("d_word")

    spChk.addWord("d_word")
    assert spChk.checkWord("d_word")

    wSuggest = spChk.suggestWords("wrod")
    assert len(wSuggest) > 0
    assert "word" in wSuggest

    dList = spChk.listDictionaries()
    assert len(dList) > 0

@pytest.mark.project
def testSpellSimple(nwTemp, nwConf):
    wList = path.join(nwTemp, "wordlist.txt")
    with open(wList, mode="w") as wFile:
        wFile.write("a_word\nb_word\nc_word\n")

    spChk = NWSpellSimple()
    spChk.mainConf = nwConf
    spChk.setLanguage("en", wList)

    assert spChk.checkWord("a_word")
    assert spChk.checkWord("b_word")
    assert spChk.checkWord("c_word")
    assert not spChk.checkWord("d_word")

    spChk.addWord("d_word")
    assert spChk.checkWord("d_word")

    wSuggest = spChk.suggestWords("wrod")
    assert len(wSuggest) > 0
    assert "word" in wSuggest

    dList = spChk.listDictionaries()
    assert len(dList) > 0
