# -*- coding: utf-8 -*-
"""novelWriter Test Config
"""

import sys
import pytest
import shutil

from os import path, mkdir
from nwdummy import DummyMain

sys.path.insert(1, path.abspath(path.join(path.dirname(__file__), path.pardir)))

from nw.config import Config # noqa: E402

@pytest.fixture(scope="session")
def nwTemp():
    testDir = path.dirname(__file__)
    tempDir = path.join(testDir, "temp")
    if path.isdir(tempDir):
        shutil.rmtree(tempDir)
    if not path.isdir(tempDir):
        mkdir(tempDir)
    return tempDir

@pytest.fixture(scope="session")
def nwRef():
    testDir = path.dirname(__file__)
    refDir = path.join(testDir, "reference")
    return refDir

@pytest.fixture(scope="session")
def nwConf(nwRef, nwTemp):
    theConf = Config()
    theConf.initConfig(nwRef, nwTemp)
    return theConf

@pytest.fixture(scope="session")
def nwDummy(nwRef, nwTemp, nwConf):
    theDummy = DummyMain()
    theDummy.mainConf = nwConf
    return theDummy

@pytest.fixture(scope="session")
def nwTempProj(nwTemp):
    projDir = path.join(nwTemp, "proj")
    if not path.isdir(projDir):
        mkdir(projDir)
    return projDir

@pytest.fixture(scope="session")
def nwTempGUI(nwTemp):
    guiDir = path.join(nwTemp, "gui")
    if not path.isdir(guiDir):
        mkdir(guiDir)
    return guiDir

@pytest.fixture(scope="session")
def nwTempBuild(nwTemp):
    buildDir = path.join(nwTemp, "build")
    if not path.isdir(buildDir):
        mkdir(buildDir)
    return buildDir

@pytest.fixture(scope="function")
def nwFuncTemp(nwTemp):
    funcDir = path.join(nwTemp, "ftemp")
    if path.isdir(funcDir):
        shutil.rmtree(funcDir)
    if not path.isdir(funcDir):
        mkdir(funcDir)
    yield funcDir
    if path.isdir(funcDir):
        shutil.rmtree(funcDir)
    return

@pytest.fixture(scope="function")
def nwMinimal(nwTemp):
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

@pytest.fixture(scope="session")
def nwLipsum():
    testDir = path.dirname(__file__)
    tempDir = path.join(testDir, "temp")
    lipsumStore = path.join(testDir, "lipsum")
    lipsumDir = path.join(tempDir, "lipsum")
    if path.isdir(lipsumDir):
        shutil.rmtree(lipsumDir)
    shutil.copytree(lipsumStore, lipsumDir)
    cacheDir = path.join(lipsumDir, "cache")
    if path.isdir(cacheDir):
        shutil.rmtree(cacheDir)
    metaDir = path.join(lipsumDir, "meta")
    if path.isdir(metaDir):
        shutil.rmtree(metaDir)
    return lipsumDir
