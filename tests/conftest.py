# -*- coding: utf-8 -*-
"""
novelWriter – Test Suite Configuration
======================================

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

import sys
import pytest
import shutil
import os

from dummy import DummyMain
from tools import cleanProject

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
    tstDir = os.path.dirname(__file__)
    srcDir = os.path.join(tstDir, "minimal")
    dstDir = os.path.join(tmpDir, "minimal")
    if os.path.isdir(dstDir):
        shutil.rmtree(dstDir)

    shutil.copytree(srcDir, dstDir)
    cleanProject(dstDir)

    yield dstDir

    if os.path.isdir(dstDir):
        shutil.rmtree(dstDir)

    return

@pytest.fixture(scope="function")
def nwLipsum(tmpDir):
    """A medium sized novelWriter example project with a lot of Lorem
    Ipsum dummy text.
    """
    tstDir = os.path.dirname(__file__)
    srcDir = os.path.join(tstDir, "lipsum")
    dstDir = os.path.join(tmpDir, "lipsum")
    if os.path.isdir(dstDir):
        shutil.rmtree(dstDir)

    shutil.copytree(srcDir, dstDir)
    cleanProject(dstDir)

    yield dstDir

    if os.path.isdir(dstDir):
        shutil.rmtree(dstDir)

    return

@pytest.fixture(scope="function")
def nwOldProj(tmpDir):
    """A minimal movelWriter project using the old folder structure used
    for storage versions < 1.2.
    """
    tstDir = os.path.dirname(__file__)
    srcDir = os.path.join(tstDir, "oldproj")
    dstDir = os.path.join(tmpDir, "oldproj")
    if os.path.isdir(dstDir):
        shutil.rmtree(dstDir)

    shutil.copytree(srcDir, dstDir)

    yield dstDir

    if os.path.isdir(dstDir):
        shutil.rmtree(dstDir)

    return
