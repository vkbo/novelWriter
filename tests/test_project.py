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
from nw.enum            import nwItemClass

theConf = Config()
theMain = DummyMain()
theMain.mainConf = theConf

theProject = NWProject(theMain)
theProject.handleSeed = 42

@pytest.mark.project
def testProjectNew(nwTempProj,nwRef):
    projFile = path.join(nwTempProj,"nwProject.nwx")
    refFile  = path.join(nwRef,"proj","1_nwProject.nwx")
    assert theConf.initConfig(nwRef)
    assert theProject.newProject()
    assert theProject.setProjectPath(nwTempProj)
    assert theProject.saveProject()
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
    assert cmpFiles(projFile, refFile, [2])
    assert not theProject.projChanged

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
    assert cmpFiles(projFile, refFile, [2])
    assert not theProject.projChanged
