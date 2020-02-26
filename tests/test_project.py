# -*- coding: utf-8 -*-
"""novelWriter Project Class Tester
"""

import nw, pytest, types
from os import path

from nwtools import *
from nwdummy import DummyMain

from nw.config          import Config
from nw.project.project import NWProject
from nw.project.item    import NWItem
from nw.project.index   import NWIndex
from nw.constants       import nwItemClass

theConf = Config()
theMain = DummyMain()
theMain.mainConf = theConf

theProject = NWProject(theMain)
theProject.handleSeed = 42

@pytest.mark.project
def testProjectNew(nwTempProj,nwRef,nwTemp):
    projFile = path.join(nwTempProj,"nwProject.nwx")
    refFile  = path.join(nwRef,"proj","1_nwProject.nwx")
    assert theConf.initConfig(nwRef, nwTemp)
    assert theProject.newProject()
    assert theProject.setProjectPath(nwTempProj)
    assert theProject.saveProject()
    assert theProject.closeProject()
    assert cmpFiles(projFile, refFile, [2])

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
    assert cmpFiles(projFile, refFile, [2])
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
    assert cmpFiles(projFile, refFile, [2])

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
    assert cmpFiles(projFile, refFile, [2])
    assert not theProject.projChanged

@pytest.mark.project
def testIndexScanThis(nwTempProj):
    projFile = path.join(nwTempProj,"nwProject.nwx")
    assert theProject.openProject(projFile)

    theIndex = NWIndex(theProject,theMain)
    tHandle  = "31489056e0916"

    isValid, theBits, thePos = theIndex.scanThis("tag: this, and this")
    assert not isValid

    isValid, theBits, thePos = theIndex.scanThis("@:")
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

    isValid, theBits, thePos = theIndex.scanThis("@tag: this, and this")
    assert isValid
    assert str(theBits) == "['@tag', 'this', 'and this']"
    assert str(thePos)  == "[0, 6, 12]"

    assert theProject.closeProject()

@pytest.mark.project
def testBuildIndex(nwTempProj):
    projFile = path.join(nwTempProj,"nwProject.nwx")
    assert theProject.openProject(projFile)

    theIndex = NWIndex(theProject,theMain)
    tHandle  = "31489056e0916"

    theIndex.scanText(tHandle, (
        "# Novel\n\n"
        "## Chapter\n\n"
        "### Scene\n\n"
        "#### Section\n\n"
        "@pov: John\n"
        "@char: Jane\n"
        "@location: Somewhere\n"
    ))

    assert theIndex.buildNovelList()
    assert str(theIndex.novelList)  == "[[1, 1, 'Novel', 'SCENE'], [3, 2, 'Chapter', 'SCENE'], [5, 3, 'Scene', 'SCENE'], [7, 4, 'Section', 'SCENE']]"
    assert str(theIndex.novelOrder) == "['31489056e0916:1', '31489056e0916:3', '31489056e0916:5', '31489056e0916:7']"
    assert theProject.closeProject()
