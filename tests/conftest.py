# -*- coding: utf-8 -*-
"""novelWriter Test Config
"""

import sys
import pytest
import shutil
import os

from dummy import DummyMain

from PyQt5.QtWidgets import QMessageBox

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import nw # noqa: E402

from nw.config import Config # noqa: E402

##
#  Core Test Folders
##

@pytest.fixture(scope="session")
def tmpDir():
    """A temporary folder for the test session. This folder is
    presistent after the test so that the status of generated files can
    be checked. The folder is instead cleared before a new test session.
    """
    testDir = os.path.dirname(__file__)
    theDir = os.path.join(testDir, "temp")
    if os.path.isdir(theDir):
        shutil.rmtree(theDir)
    if not os.path.isdir(theDir):
        os.mkdir(theDir)
    return theDir

@pytest.fixture(scope="session")
def refDir():
    """The folder where all the reference files are stored for verifying
    the results of tests.
    """
    testDir = os.path.dirname(__file__)
    theDir = os.path.join(testDir, "reference")
    return theDir

@pytest.fixture(scope="session")
def outDir(tmpDir):
    """An output folder for test results
    """
    theDir = os.path.join(tmpDir, "results")
    if not os.path.isdir(theDir):
        os.mkdir(theDir)
    return theDir

@pytest.fixture(scope="function")
def fncDir(tmpDir):
    """A temporary folder for a single test function.
    """
    fncDir = os.path.join(tmpDir, "f_temp")
    if os.path.isdir(fncDir):
        shutil.rmtree(fncDir)
    if not os.path.isdir(fncDir):
        os.mkdir(fncDir)
    yield fncDir
    if os.path.isdir(fncDir):
        shutil.rmtree(fncDir)
    return

@pytest.fixture(scope="function")
def fncProj(fncDir):
    """A temporary folder for a single test function,
    with a project folder.
    """
    prjDir = os.path.join(fncDir, "project")
    if os.path.isdir(prjDir):
        shutil.rmtree(prjDir)
    if not os.path.isdir(prjDir):
        os.mkdir(prjDir)
    return prjDir

##
#  novelWriter Objects
##

@pytest.fixture(scope="function")
def tmpConf(tmpDir):
    """Create a temporary novelWriter configuration object.
    """
    confFile = os.path.join(tmpDir, "novelwriter.conf")
    if os.path.isfile(confFile):
        os.unlink(confFile)
    theConf = Config()
    theConf.initConfig(tmpDir, tmpDir)
    theConf.setLastPath("")
    return theConf

@pytest.fixture(scope="function")
def dummyGUI(tmpConf):
    """Create a dummy instance of novelWriter's main GUI class.
    """
    theDummy = DummyMain()
    theDummy.mainConf = tmpConf
    return theDummy

@pytest.fixture(scope="function")
def nwGUI(qtbot, fncDir):
    """Create an instance of the novelWriter GUI.
    """
    nwGUI = nw.main(["--testmode", "--config=%s" % fncDir, "--data=%s" % fncDir])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(20)

    nwGUI.mainConf.lastPath = fncDir

    yield nwGUI

    qtbot.wait(20)
    nwGUI.closeMain()
    qtbot.wait(20)

    return

##
#  Temp Project Folders
##

@pytest.fixture(scope="function")
def nwMinimal(tmpDir):
    """A minimal novelWriter example project.
    """
    testDir = os.path.dirname(__file__)
    minimalStore = os.path.join(testDir, "minimal")
    minimalDir = os.path.join(tmpDir, "minimal")
    if os.path.isdir(minimalDir):
        shutil.rmtree(minimalDir)
    shutil.copytree(minimalStore, minimalDir)
    cacheDir = os.path.join(minimalDir, "cache")
    if os.path.isdir(cacheDir):
        shutil.rmtree(cacheDir)
    metaDir = os.path.join(minimalDir, "meta")
    if os.path.isdir(metaDir):
        shutil.rmtree(metaDir)
    yield minimalDir
    if os.path.isdir(minimalDir):
        shutil.rmtree(minimalDir)
    return

@pytest.fixture(scope="function")
def nwLipsum(tmpDir):
    """A medium sized novelWriter example project with a lot of Lorem
    Ipsum dummy text.
    """
    testDir = os.path.dirname(__file__)
    lipsumStore = os.path.join(testDir, "lipsum")
    lipsumDir = os.path.join(tmpDir, "lipsum")
    if os.path.isdir(lipsumDir):
        shutil.rmtree(lipsumDir)
    shutil.copytree(lipsumStore, lipsumDir)
    cacheDir = os.path.join(lipsumDir, "cache")
    if os.path.isdir(cacheDir):
        shutil.rmtree(cacheDir)
    metaDir = os.path.join(lipsumDir, "meta")
    if os.path.isdir(metaDir):
        shutil.rmtree(metaDir)
    yield lipsumDir
    if os.path.isdir(lipsumDir):
        shutil.rmtree(lipsumDir)
    return

@pytest.fixture(scope="function")
def nwOldProj(tmpDir):
    """A minimal movelWriter project using the old folder structure.
    """
    testDir = os.path.dirname(__file__)
    oldProjStore = os.path.join(testDir, "oldproj")
    oldProjDir = os.path.join(tmpDir, "oldproj")
    if os.path.isdir(oldProjDir):
        shutil.rmtree(oldProjDir)
    shutil.copytree(oldProjStore, oldProjDir)
    yield oldProjDir
    if os.path.isdir(oldProjDir):
        shutil.rmtree(oldProjDir)
    return

##
#  Monkey Patch Dialogs
##

@pytest.fixture(scope="function")
def yesToAll(monkeypatch):
    """Make the message boxes/questions always say yes.
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
    yield
    monkeypatch.undo()
    return

# =============================================================================================== #

##
#  Temporary Test Folders
##

@pytest.fixture(scope="session")
def nwTempGUI(tmpDir):
    """A temporary folder for GUI tests.
    """
    guiDir = os.path.join(tmpDir, "gui")
    if not os.path.isdir(guiDir):
        os.mkdir(guiDir)
    return guiDir

@pytest.fixture(scope="session")
def nwTempBuild(tmpDir):
    """A temporary folder for build tests.
    """
    buildDir = os.path.join(tmpDir, "build")
    if not os.path.isdir(buildDir):
        os.mkdir(buildDir)
    return buildDir
