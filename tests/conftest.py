# -*- coding: utf-8 -*-
"""novelWriter Test Config
"""

import sys, pytest, shutil
from os import path, mkdir

sys.path.insert(1, path.abspath(path.join(path.dirname(__file__), path.pardir)))

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

@pytest.fixture(scope="session")
def nwRef():
    testDir = path.dirname(__file__)
    refDir = path.join(testDir, "reference")
    return refDir

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
