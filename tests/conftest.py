# -*- coding: utf-8 -*-
"""novelWriter Test Config
"""

import sys
import pytest
import shutil
import os

from nwdummy import DummyMain

# from PyQt5.QtWidgets import QMessageBox

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

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
    tempDir = os.path.join(testDir, "temp")
    if os.path.isdir(tempDir):
        shutil.rmtree(tempDir)
    if not os.path.isdir(tempDir):
        os.mkdir(tempDir)
    return tempDir

# @pytest.fixture(scope="session")
# def nwRef():
#     """The folder where all the reference files are stored for verifying
#     the results of tests.
#     """
#     testDir = os.path.dirname(__file__)
#     refDir = os.path.join(testDir, "reference")
#     return refDir

##
#  novelWriter Objects
##

# @pytest.fixture(scope="session")
# def tmpConf(nwTemp):
#     """Create a temporary novelWriter configuration object.
#     """
#     theConf = Config()
#     theConf.initConfig(nwTemp, nwTemp)
#     theConf.setLastPath("")
#     return theConf

@pytest.fixture(scope="session")
def tmpConf(tmpDir):
    """Create a temporary novelWriter configuration object.
    """
    theConf = Config()
    theConf.initConfig(tmpDir, tmpDir)
    theConf.setLastPath("")
    return theConf

# @pytest.fixture(scope="session")
# def nwConf(nwRef, nwTemp):
#     """Temporary novelWriter configuration used for the dummy instance
#     of novelWriter's main GUI.
#     """
#     theConf = Config()
#     theConf.initConfig(nwRef, nwTemp)
#     return theConf

@pytest.fixture(scope="session")
def dummyGUI(tmpConf):
    """Create a dummy instance of novelWriter's main GUI class.
    """
    theDummy = DummyMain()
    theDummy.mainConf = tmpConf
    return theDummy

##
#  Temporary Test Folders
##

# @pytest.fixture(scope="session")
# def nwTempProj(nwTemp):
#     """A temporary folder for project tests.
#     """
#     projDir = os.path.join(nwTemp, "proj")
#     if not os.path.isdir(projDir):
#         os.mkdir(projDir)
#     return projDir

# @pytest.fixture(scope="session")
# def nwTempGUI(nwTemp):
#     """A temporary folder for GUI tests.
#     """
#     guiDir = os.path.join(nwTemp, "gui")
#     if not os.path.isdir(guiDir):
#         os.mkdir(guiDir)
#     return guiDir

# @pytest.fixture(scope="session")
# def nwTempBuild(nwTemp):
#     """A temporary folder for build tests.
#     """
#     buildDir = os.path.join(nwTemp, "build")
#     if not os.path.isdir(buildDir):
#         os.mkdir(buildDir)
#     return buildDir

# @pytest.fixture(scope="function")
# def nwFuncTemp(nwTemp):
#     """A temporary folder for a single test function.
#     """
#     funcDir = os.path.join(nwTemp, "ftemp")
#     if os.path.isdir(funcDir):
#         shutil.rmtree(funcDir)
#     if not os.path.isdir(funcDir):
#         os.mkdir(funcDir)
#     yield funcDir
#     if os.path.isdir(funcDir):
#         shutil.rmtree(funcDir)
#     return

##
#  Temp Folders for Projects
##

# @pytest.fixture(scope="function")
# def nwMinimal(nwTemp):
#     """A minimal novelWriter example project.
#     """
#     testDir = os.path.dirname(__file__)
#     minimalStore = os.path.join(testDir, "minimal")
#     minimalDir = os.path.join(nwTemp, "minimal")
#     if os.path.isdir(minimalDir):
#         shutil.rmtree(minimalDir)
#     shutil.copytree(minimalStore, minimalDir)
#     cacheDir = os.path.join(minimalDir, "cache")
#     if os.path.isdir(cacheDir):
#         shutil.rmtree(cacheDir)
#     metaDir = os.path.join(minimalDir, "meta")
#     if os.path.isdir(metaDir):
#         shutil.rmtree(metaDir)
#     yield minimalDir
#     if os.path.isdir(minimalDir):
#         shutil.rmtree(minimalDir)
#     return

# @pytest.fixture(scope="function")
# def nwLipsum(nwTemp):
#     """A medium sized novelWriter example project with a lot of Lorem
#     Ipsum dummy text.
#     """
#     testDir = os.path.dirname(__file__)
#     lipsumStore = os.path.join(testDir, "lipsum")
#     lipsumDir = os.path.join(nwTemp, "lipsum")
#     if os.path.isdir(lipsumDir):
#         shutil.rmtree(lipsumDir)
#     shutil.copytree(lipsumStore, lipsumDir)
#     cacheDir = os.path.join(lipsumDir, "cache")
#     if os.path.isdir(cacheDir):
#         shutil.rmtree(cacheDir)
#     metaDir = os.path.join(lipsumDir, "meta")
#     if os.path.isdir(metaDir):
#         shutil.rmtree(metaDir)
#     yield lipsumDir
#     if os.path.isdir(lipsumDir):
#         shutil.rmtree(lipsumDir)
#     return

# @pytest.fixture(scope="function")
# def nwOldProj(nwTemp):
#     """A minimal movelWriter project using the old folder structure.
#     """
#     testDir = os.path.dirname(__file__)
#     oldProjStore = os.path.join(testDir, "oldproj")
#     oldProjDir = os.path.join(nwTemp, "oldproj")
#     if os.path.isdir(oldProjDir):
#         shutil.rmtree(oldProjDir)
#     shutil.copytree(oldProjStore, oldProjDir)
#     yield oldProjDir
#     if os.path.isdir(oldProjDir):
#         shutil.rmtree(oldProjDir)
#     return

##
#  Monkey Patch Dialogs
##

# @pytest.fixture(scope="function")
# def yesToAll(monkeypatch):
#     """Make the message boxes/questions always say yes.
#     """
#     monkeypatch.setattr(
#         QMessageBox, "question", lambda *args, **kwargs: QMessageBox.Yes
#     )
#     monkeypatch.setattr(
#         QMessageBox, "information", lambda *args, **kwargs: QMessageBox.Yes
#     )
#     monkeypatch.setattr(
#         QMessageBox, "warning", lambda *args, **kwargs: QMessageBox.Yes
#     )
#     monkeypatch.setattr(
#         QMessageBox, "critical", lambda *args, **kwargs: QMessageBox.Yes
#     )
#     return
