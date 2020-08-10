# -*- coding: utf-8 -*-
"""novelWriter Project Class Tester
"""

import nw
import pytest
from os import path

from nwtools import *
from nwdummy import DummyMain

from nw.config import Config
from nw.core.project import NWProject
from nw.core.index import NWIndex
from nw.constants import nwItemClass

theConf = Config()
theMain = DummyMain()
theMain.mainConf = theConf

theProject = NWProject(theMain)
theProject.projTree.setSeed(42)

@pytest.mark.project
def testProjectNewMinimal(nwTempProj, nwRef, nwTemp):
    projFile = path.join(nwTempProj,"nwProject.nwx")
    refFile  = path.join(nwRef,"proj", "1_nwProject.nwx")
    assert theConf.initConfig(nwRef, nwTemp)
    assert theProject.newProject({"projPath": nwTempProj})
    assert theProject.setProjectPath(nwTempProj)
    assert theProject.saveProject()
    assert theProject.closeProject()
    assert cmpFiles(projFile, refFile, [2, 6, 7, 8])

@pytest.mark.project
def testProjectOpen(nwTempProj):
    projFile = path.join(nwTempProj,"nwProject.nwx")
    assert theProject.openProject(projFile)

@pytest.mark.project
def testProjectSave(nwTempProj,nwRef):
    projFile = path.join(nwTempProj,"nwProject.nwx")
    refFile  = path.join(nwRef,"proj","1_nwProject.nwx")
    assert theProject.saveProject()
    assert theProject.closeProject()
    assert cmpFiles(projFile, refFile, [2, 6, 7, 8])
    assert not theProject.projChanged

@pytest.mark.project
def testProjectOpenTwice(nwTempProj,nwRef):
    projFile = path.join(nwTempProj,"nwProject.nwx")
    refFile  = path.join(nwRef,"proj","1_nwProject.nwx")
    assert theProject.openProject(projFile)
    assert not theProject.openProject(projFile)
    assert theProject.openProject(projFile, overrideLock=True)
    assert theProject.saveProject()
    assert theProject.closeProject()
    assert cmpFiles(projFile, refFile, [2, 6, 7, 8])

@pytest.mark.project
def testProjectNewRoot(nwTempProj,nwRef):
    projFile = path.join(nwTempProj,"nwProject.nwx")
    refFile  = path.join(nwRef,"proj","2_nwProject.nwx")
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
    assert cmpFiles(projFile, refFile, [2, 6, 7, 8])
    assert not theProject.projChanged

@pytest.mark.project
def testProjectNewFile(nwTempProj,nwRef):
    projFile = path.join(nwTempProj,"nwProject.nwx")
    refFile  = path.join(nwRef,"proj","3_nwProject.nwx")
    assert theProject.openProject(projFile)
    assert isinstance(theProject.newFile("Hello", nwItemClass.NOVEL,     "73475cb40a568"), str)
    assert isinstance(theProject.newFile("Jane",  nwItemClass.CHARACTER, "71ee45a3c0db9"), str)
    assert theProject.projChanged
    assert theProject.saveProject()
    assert theProject.closeProject()
    assert cmpFiles(projFile, refFile, [2, 6, 7, 8])
    assert not theProject.projChanged

@pytest.mark.project
def testIndexScanThis(nwTempProj):
    projFile = path.join(nwTempProj,"nwProject.nwx")
    assert theProject.openProject(projFile)

    theIndex = NWIndex(theProject, theMain)
    tHandle  = "31489056e0916"

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
def testIndexCheckThese(nwTempProj):
    projFile = path.join(nwTempProj,"nwProject.nwx")
    assert theProject.openProject(projFile)

    theIndex = NWIndex(theProject, theMain)
    nHandle  = "0e17daca5f3e1"
    nItem    = theProject.projTree[nHandle]
    cHandle  = "02d20bbd7e394"
    cItem    = theProject.projTree[cHandle]

    assert theIndex.scanText(cHandle, (
        "# Jane Smith\n"
        "@tag: Jane"
    ))
    assert theIndex.scanText(nHandle, (
        "# Hello World!\n"
        "@pov: Jane"
    ))
    assert str(theIndex.tagIndex) == "{'Jane': [2, '02d20bbd7e394', 'CHARACTER', 'T000001']}"
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
def testIndexMeta(nwTempProj):
    projFile = path.join(nwTempProj,"nwProject.nwx")
    assert theProject.openProject(projFile)

    theIndex = NWIndex(theProject, theMain)
    nHandle  = "0e17daca5f3e1"
    nItem    = theProject.projTree[nHandle]
    cHandle  = "02d20bbd7e394"
    cItem    = theProject.projTree[cHandle]

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
    assert str(theIndex.tagIndex) == "{'Jane': [2, '02d20bbd7e394', 'CHARACTER', 'T000001']}"
    assert theIndex.novelIndex[nHandle]["T000001"]["title"] == "Hello World!"

    # The novel structure should contain the pointer to the novel file header
    assert str(theIndex.getNovelStructure()) == "['0e17daca5f3e1:T000001']"

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
    assert str(theRefs) == "{'0e17daca5f3e1': 'T000001'}"

    assert theProject.closeProject()

# The two following tests must be at the end as they mess up the config object
# and the handle seed. They go into their own folders, but use the same project
# object as the test above.

@pytest.mark.project
def testProjectNewCustom(nwTempCustom, nwRef, nwTemp):
    projData = {
        "projName": "Test Custom",
        "projTitle": "Test Novel",
        "projAuthors": "Jane Doe\nJohn Doh\n",
        "projPath": nwTempCustom,
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
    theProject.mainConf = theConf
    theProject.projTree.setSeed(42)
    assert theProject.newProject(projData)
    assert theProject.saveProject()
    assert theProject.closeProject()
    projFile = path.join(nwTempCustom, "nwProject.nwx")
    refFile  = path.join(nwRef, "proj", "4_nwProject.nwx")
    assert cmpFiles(projFile, refFile, [2, 6, 7, 8])

@pytest.mark.project
def testProjectNewSample(nwTempSample, nwLipsum, nwRef, nwTemp):
    projData = {
        "projName": "Test Sample",
        "projTitle": "Test Novel",
        "projAuthors": "Jane Doe\nJohn Doh\n",
        "projPath": nwTempSample,
        "popSample": True,
        "popMinimal": False,
        "popCustom": False,
    }
    theProject.mainConf = theConf
    assert theProject.newProject(projData)
    assert theProject.openProject(nwTempSample)
    assert theProject.projName == "Sample Project"
    assert theProject.saveProject()
    assert theProject.closeProject()
