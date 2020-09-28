# -*- coding: utf-8 -*-
"""novelWriter Test Config
"""

import sys
import pytest
import shutil

from os import path, mkdir
from nwdummy import DummyMain

from PyQt5.QtWidgets import QMessageBox

sys.path.insert(1, path.abspath(path.join(path.dirname(__file__), path.pardir)))

from nw.config import Config # noqa: E402

##
#  Core Test Folders
##

@pytest.fixture(scope="session")
def nwTemp():
    """A temporary folder for the test session. This folder is
    presistent after the test so that the status of generated files can
    be checked. The folder is instead cleared before a new test session.
    """
    testDir = path.dirname(__file__)
    tempDir = path.join(testDir, "temp")
    if path.isdir(tempDir):
        shutil.rmtree(tempDir)
    if not path.isdir(tempDir):
        mkdir(tempDir)
    return tempDir

@pytest.fixture(scope="session")
def nwRef():
    """The folder where all the reference files are stored for verifying
    the results of tests.
    """
    testDir = path.dirname(__file__)
    refDir = path.join(testDir, "reference")
    return refDir

##
#  novelWriter Objects
##

@pytest.fixture(scope="session")
def tmpConf(nwTemp):
    """Create a temporary novelWriter configuration object.
    """
    theConf = Config()
    theConf.initConfig(nwTemp, nwTemp)
    theConf.setLastPath("")
    return theConf

@pytest.fixture(scope="session")
def nwConf(nwRef, nwTemp):
    """Temporary novelWriter configuration used for the dummy instance
    of novelWriter's main GUI.
    """
    theConf = Config()
    theConf.initConfig(nwRef, nwTemp)
    return theConf

@pytest.fixture(scope="session")
def nwDummy(nwRef, nwTemp, nwConf):
    """Create a dummy instance of novelWriter's main GUI class.
    """
    theDummy = DummyMain()
    theDummy.mainConf = nwConf
    return theDummy

##
#  Temporary Test Folders
##

@pytest.fixture(scope="session")
def nwTempProj(nwTemp):
    """A temporary folder for project tests.
    """
    projDir = path.join(nwTemp, "proj")
    if not path.isdir(projDir):
        mkdir(projDir)
    return projDir

@pytest.fixture(scope="session")
def nwTempGUI(nwTemp):
    """A temporary folder for GUI tests.
    """
    guiDir = path.join(nwTemp, "gui")
    if not path.isdir(guiDir):
        mkdir(guiDir)
    return guiDir

@pytest.fixture(scope="session")
def nwTempBuild(nwTemp):
    """A temporary folder for build tests.
    """
    buildDir = path.join(nwTemp, "build")
    if not path.isdir(buildDir):
        mkdir(buildDir)
    return buildDir

@pytest.fixture(scope="function")
def nwFuncTemp(nwTemp):
    """A temporary folder for a single test function.
    """
    funcDir = path.join(nwTemp, "ftemp")
    if path.isdir(funcDir):
        shutil.rmtree(funcDir)
    if not path.isdir(funcDir):
        mkdir(funcDir)
    yield funcDir
    if path.isdir(funcDir):
        shutil.rmtree(funcDir)
    return

##
#  Temp Folders for Projects
##

@pytest.fixture(scope="function")
def nwMinimal(nwTemp):
    """A minimal novelWriter example project.
    """
    testDir = path.dirname(__file__)
    minimalStore = path.join(testDir, "minimal")
    minimalDir = path.join(nwTemp, "minimal")
    if path.isdir(minimalDir):
        shutil.rmtree(minimalDir)
    shutil.copytree(minimalStore, minimalDir)
    cacheDir = path.join(minimalDir, "cache")
    if path.isdir(cacheDir):
        shutil.rmtree(cacheDir)
    metaDir = path.join(minimalDir, "meta")
    if path.isdir(metaDir):
        shutil.rmtree(metaDir)
    yield minimalDir
    if path.isdir(minimalDir):
        shutil.rmtree(minimalDir)
    return

@pytest.fixture(scope="function")
def nwLipsum(nwTemp):
    """A medium sized novelWriter example project with a lot of Lorem
    Ipsum dummy text.
    """
    testDir = path.dirname(__file__)
    lipsumStore = path.join(testDir, "lipsum")
    lipsumDir = path.join(nwTemp, "lipsum")
    if path.isdir(lipsumDir):
        shutil.rmtree(lipsumDir)
    shutil.copytree(lipsumStore, lipsumDir)
    cacheDir = path.join(lipsumDir, "cache")
    if path.isdir(cacheDir):
        shutil.rmtree(cacheDir)
    metaDir = path.join(lipsumDir, "meta")
    if path.isdir(metaDir):
        shutil.rmtree(metaDir)
    yield lipsumDir
    if path.isdir(lipsumDir):
        shutil.rmtree(lipsumDir)
    return

@pytest.fixture(scope="function")
def nwOldProj(nwTemp):
    """A minimal movelWriter project using the old folder structure.
    """
    testDir = path.dirname(__file__)
    oldProjStore = path.join(testDir, "oldproj")
    oldProjDir = path.join(nwTemp, "oldproj")
    if path.isdir(oldProjDir):
        shutil.rmtree(oldProjDir)
    shutil.copytree(oldProjStore, oldProjDir)
    yield oldProjDir
    if path.isdir(oldProjDir):
        shutil.rmtree(oldProjDir)
    return

##
#  Monkey Patch Dialogs
##

@pytest.fixture(scope="function")
def yesToAll(monkeypatch):
    """Make the message boxes/questions always say yes to the dress!
    """
    monkeypatch.setattr(
        QMessageBox, "question", lambda *args, **kwargs: QMessageBox.Yes
    )
    monkeypatch.setattr(
        QMessageBox, "information", lambda *args, **kwargs: QMessageBox.Yes
    )
    monkeypatch.setattr(
        QMessageBox, "warning", lambda *args, **kwargs: QMessageBox.Yes
    )
    monkeypatch.setattr(
        QMessageBox, "critical", lambda *args, **kwargs: QMessageBox.Yes
    )
    return
