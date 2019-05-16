# -*- coding: utf-8 -*-
"""novelWriter Project Class Tester
"""

import nw, pytest, types
from os import path, unlink

from nwtools import *
from nwdummy import DummyMain

from nw.config          import Config
from nw.project.project import NWProject
from nw.project.item    import NWItem
from nw.enum            import nwItemClass

theConf  = Config()
theMain  = DummyMain()
theMain.mainConf = theConf
testDir  = path.dirname(__file__)
testTemp = path.join(testDir,"temp")
testRef  = path.join(testDir,"reference")
testProj = path.join(testTemp,"proj")

ensureDir(testTemp)
ensureDir(testProj)

theConf.initConfig(testRef)
theProject = NWProject(theMain)
theProject.handleSeed = 42

projFile = path.join(testProj,"nwProject.nwx")

@pytest.mark.project
def testProjectNew():
    assert theProject.newProject()
    assert theProject.setProjectPath(testProj)
    assert theProject.saveProject()
    assert cmpFiles(projFile, path.join(testRef,"new_nwProject.nwx"), [2])

@pytest.mark.project
def testProjectOpen():
    assert theProject.openProject(projFile)

@pytest.mark.project
def testProjectSave():
    assert theProject.saveProject()
    assert cmpFiles(projFile, path.join(testRef,"new_nwProject.nwx"), [2])
    assert not theProject.projChanged

@pytest.mark.project
def testProjectNewRoot():
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
    assert cmpFiles(projFile, path.join(testRef,"roots_nwProject.nwx"), [2])
    assert not theProject.projChanged
