# -*- coding: utf-8 -*-
"""novelWriter Project Class Tester
"""

import pytest
from os import path, mkdir, listdir
from shutil import copyfile
from zipfile import ZipFile

from nwtools import cmpFiles

from nw.core.project import NWProject
from nw.core.document import NWDoc
from nw.core.spellcheck import NWSpellEnchant, NWSpellSimple
from nw.constants import nwItemClass, nwItemType, nwItemLayout, nwFiles

@pytest.mark.project
def testProjectNewOpenSave(nwFuncTemp, nwTempProj, nwRef, nwTemp, nwDummy):
    projFile = path.join(nwFuncTemp, "nwProject.nwx")
    testFile = path.join(nwTempProj, "1_nwProject.nwx")
    refFile  = path.join(nwRef, "proj", "1_nwProject.nwx")

    theProject = NWProject(nwDummy)
    theProject.projTree.setSeed(42)

    assert theProject.newProject({"projPath": nwFuncTemp})
    assert theProject.setProjectPath(nwFuncTemp)
    assert theProject.saveProject()
    assert theProject.closeProject()

    # Check the new project
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [2, 6, 7, 8])

    # Open again
    assert theProject.openProject(projFile)

    # Save and close
    assert theProject.saveProject()
    assert theProject.closeProject()
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [2, 6, 7, 8])
    assert not theProject.projChanged

    # Open a second time
    assert theProject.openProject(projFile)
    assert not theProject.openProject(projFile)
    assert theProject.openProject(projFile, overrideLock=True)
    assert theProject.saveProject()
    assert theProject.closeProject()
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [2, 6, 7, 8])

@pytest.mark.project
def testProjectNewRoot(nwFuncTemp, nwTempProj, nwRef, nwDummy):
    projFile = path.join(nwFuncTemp, "nwProject.nwx")
    testFile = path.join(nwTempProj, "2_nwProject.nwx")
    refFile  = path.join(nwRef, "proj", "2_nwProject.nwx")

    theProject = NWProject(nwDummy)
    theProject.projTree.setSeed(42)

    assert theProject.newProject({"projPath": nwFuncTemp})
    assert theProject.setProjectPath(nwFuncTemp)
    assert theProject.saveProject()
    assert theProject.closeProject()
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

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [2, 6, 7, 8])
    assert not theProject.projChanged

@pytest.mark.project
def testProjectNewFile(nwFuncTemp, nwTempProj, nwRef, nwDummy):
    projFile = path.join(nwFuncTemp, "nwProject.nwx")
    testFile = path.join(nwTempProj, "3_nwProject.nwx")
    refFile  = path.join(nwRef, "proj", "3_nwProject.nwx")

    theProject = NWProject(nwDummy)
    theProject.projTree.setSeed(42)

    assert theProject.newProject({"projPath": nwFuncTemp})
    assert theProject.setProjectPath(nwFuncTemp)
    assert theProject.saveProject()
    assert theProject.closeProject()
    assert theProject.openProject(projFile)

    assert isinstance(theProject.newFile("Hello", nwItemClass.NOVEL,     "31489056e0916"), str)
    assert isinstance(theProject.newFile("Jane",  nwItemClass.CHARACTER, "71ee45a3c0db9"), str)
    assert theProject.projChanged
    assert theProject.saveProject()
    assert theProject.closeProject()

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [2, 6, 7, 8])
    assert not theProject.projChanged

@pytest.mark.project
def testProjectNewCustom(nwFuncTemp, nwTempProj, nwRef, nwDummy):

    projFile = path.join(nwFuncTemp, "nwProject.nwx")
    testFile = path.join(nwTempProj, "4_nwProject.nwx")
    refFile  = path.join(nwRef, "proj", "4_nwProject.nwx")

    projData = {
        "projName": "Test Custom",
        "projTitle": "Test Novel",
        "projAuthors": "Jane Doe\nJohn Doh\n",
        "projPath": nwFuncTemp,
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
    theProject = NWProject(nwDummy)
    theProject.projTree.setSeed(42)

    assert theProject.newProject(projData)
    assert theProject.saveProject()
    assert theProject.closeProject()

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [2, 6, 7, 8])

@pytest.mark.project
def testProjectNewSample(nwFuncTemp, nwRef, nwConf, nwDummy):
    projData = {
        "projName": "Test Sample",
        "projTitle": "Test Novel",
        "projAuthors": "Jane Doe\nJohn Doh\n",
        "projPath": nwFuncTemp,
        "popSample": True,
        "popMinimal": False,
        "popCustom": False,
    }
    theProject = NWProject(nwDummy)
    theProject.projTree.setSeed(42)
    theProject.mainConf = nwConf

    assert theProject.newProject(projData)
    assert theProject.openProject(nwFuncTemp)
    assert theProject.projName == "Sample Project"
    assert theProject.saveProject()
    assert theProject.closeProject()

@pytest.mark.project
def testDocMeta(nwDummy, nwLipsum):
    theProject = NWProject(nwDummy)
    theProject.projTree.setSeed(42)
    assert theProject.openProject(nwLipsum)

    aDoc = NWDoc(theProject, nwDummy)
    assert aDoc.openDocument("47666c91c7ccf")
    theMeta, thePath, theClass, theLayout = aDoc.getMeta()

    assert theMeta == "Scene Five"
    assert len(thePath) == 3
    assert thePath[0] == "47666c91c7ccf"
    assert thePath[1] == "6bd935d2490cd"
    assert thePath[2] == "b3643d0f92e32"
    assert theClass == nwItemClass.NOVEL
    assert theLayout == nwItemLayout.SCENE

    aDoc._docMeta = "too_short"
    theMeta, thePath, theClass, theLayout = aDoc.getMeta()
    assert theMeta == ""
    assert thePath == []
    assert theClass is None
    assert theLayout is None

@pytest.mark.project
def testSpellEnchant(nwTemp, nwConf):
    wList = path.join(nwTemp, "wordlist.txt")
    with open(wList, mode="w") as wFile:
        wFile.write("a_word\nb_word\nc_word\n")

    spChk = NWSpellEnchant()
    spChk.mainConf = nwConf
    spChk.setLanguage("en", wList)

    assert spChk.checkWord("a_word")
    assert spChk.checkWord("b_word")
    assert spChk.checkWord("c_word")
    assert not spChk.checkWord("d_word")

    spChk.addWord("d_word")
    assert spChk.checkWord("d_word")

    wSuggest = spChk.suggestWords("wrod")
    assert len(wSuggest) > 0
    assert "word" in wSuggest

    dList = spChk.listDictionaries()
    assert len(dList) > 0

@pytest.mark.project
def testSpellSimple(nwTemp, nwConf):
    wList = path.join(nwTemp, "wordlist.txt")
    with open(wList, mode="w") as wFile:
        wFile.write("a_word\nb_word\nc_word\n")

    spChk = NWSpellSimple()
    spChk.mainConf = nwConf
    spChk.setLanguage("en", wList)

    assert spChk.checkWord("a_word")
    assert spChk.checkWord("b_word")
    assert spChk.checkWord("c_word")
    assert not spChk.checkWord("d_word")

    spChk.addWord("d_word")
    assert spChk.checkWord("d_word")

    wSuggest = spChk.suggestWords("wrod")
    assert len(wSuggest) > 0
    assert "word" in wSuggest

    dList = spChk.listDictionaries()
    assert len(dList) > 0

@pytest.mark.project
def testProjectOptions(nwDummy, nwLipsum):
    theProject = NWProject(nwDummy)
    assert theProject.projMeta is None

    theOpts = theProject.optState
    assert not theOpts.loadSettings()
    assert not theOpts.saveSettings()

    # No Settings
    assert theProject.openProject(nwLipsum)
    assert theOpts.loadSettings()
    assert theOpts.saveSettings()
    assert str(theOpts.theState) == r"{}"

    # Read Invalid Settings and Filter
    stateFile = path.join(theProject.projMeta, nwFiles.OPTS_FILE)
    with open(stateFile, mode="w", encoding="utf8") as outFile:
        outFile.write(
            r'{"GuiProjectSettings": {"winWidth": 100, "winHeight": 50}, "NoGroup": {"NoName": 0}}'
        )
    assert theOpts.loadSettings()
    assert str(theOpts.theState) == r"{'GuiProjectSettings': {'winWidth': 100, 'winHeight': 50}}"

    # Set New Settings
    assert not theOpts.setValue("NoGroup", "NoName", None)
    assert not theOpts.setValue("GuiProjectSettings", "NoName", None)
    assert theOpts.setValue("GuiProjectSettings", "winWidth", 200)
    assert theOpts.setValue("GuiProjectSettings", "winHeight", 80)
    assert str(theOpts.theState) == r"{'GuiProjectSettings': {'winWidth': 200, 'winHeight': 80}}"

    # Check Read/Write Types

    ## String
    assert theOpts.setValue("GuiWritingStats", "winWidth", "123")
    assert isinstance(theOpts.getString("GuiWritingStats", "winWidth", "456"), str)
    assert theOpts.getString("GuiWritingStats", "NoName", "456") == "456"

    ## Int
    assert theOpts.setValue("GuiWritingStats", "winWidth", "123")
    assert isinstance(theOpts.getInt("GuiWritingStats", "winWidth", 456), int)
    assert theOpts.getInt("GuiWritingStats", "NoName", 456) == 456
    assert theOpts.setValue("GuiWritingStats", "winWidth", "True")
    assert theOpts.getInt("GuiWritingStats", "NoName", 456) == 456

    ## Float
    assert theOpts.setValue("GuiWritingStats", "winWidth", "123")
    assert isinstance(theOpts.getFloat("GuiWritingStats", "winWidth", 456.0), float)
    assert theOpts.getFloat("GuiWritingStats", "NoName", 456.0) == 456.0
    assert theOpts.setValue("GuiWritingStats", "winWidth", "True")
    assert theOpts.getFloat("GuiWritingStats", "winWidth", 456.0) == 456.0

    ## Bool
    assert theOpts.setValue("GuiWritingStats", "winWidth", True)
    assert isinstance(theOpts.getBool("GuiWritingStats", "winWidth", False), bool)
    assert theOpts.getFloat("GuiWritingStats", "NoName", False) is False
    assert theOpts.setValue("GuiWritingStats", "winWidth", "True")
    assert theOpts.getFloat("GuiWritingStats", "winWidth", False) is False

@pytest.mark.project
def testOrphanedFiles(nwDummy, nwLipsum):
    theProject = NWProject(nwDummy)
    assert theProject.openProject(nwLipsum)
    assert theProject.projTree["636b6aa9b697b"] is None
    assert theProject.closeProject()

    # First Item with Meta Data
    orphPath = path.join(nwLipsum, "content", "636b6aa9b697b.nwd")
    with open(orphPath, mode="w", encoding="utf8") as outFile:
        outFile.write(r"%%~ 5eaea4e8cdee8:15c4492bd5107:WORLD:NOTE:Mars")
        outFile.write("\n")

    # Second Item without Meta Data
    orphPath = path.join(nwLipsum, "content", "736b6aa9b697b.nwd")
    with open(orphPath, mode="w", encoding="utf8") as outFile:
        outFile.write("\n")

    # Invalid File Name
    dummyPath = path.join(nwLipsum, "content", "636b6aa9b697b.txt")
    with open(dummyPath, mode="w", encoding="utf8") as outFile:
        outFile.write("\n")

    # Invalid File Name
    dummyPath = path.join(nwLipsum, "content", "636b6aa9b697bb.nwd")
    with open(dummyPath, mode="w", encoding="utf8") as outFile:
        outFile.write("\n")

    # Invalid File Name
    dummyPath = path.join(nwLipsum, "content", "abcdefghijklm.nwd")
    with open(dummyPath, mode="w", encoding="utf8") as outFile:
        outFile.write("\n")

    assert theProject.openProject(nwLipsum)
    assert theProject.projPath is not None
    assert theProject.projTree["636b6aa9b697bb"] is None
    assert theProject.projTree["abcdefghijklm"] is None

    # First Item with Meta Data
    oItem = theProject.projTree["636b6aa9b697b"]
    assert oItem is not None
    assert oItem.itemName == "Mars"
    assert oItem.itemHandle == "636b6aa9b697b"
    assert oItem.parHandle is None
    assert oItem.itemClass == nwItemClass.WORLD
    assert oItem.itemType == nwItemType.FILE
    assert oItem.itemLayout == nwItemLayout.NOTE

    # Second Item without Meta Data
    oItem = theProject.projTree["736b6aa9b697b"]
    assert oItem is not None
    assert oItem.itemName == "Orphaned File 1"
    assert oItem.itemHandle == "736b6aa9b697b"
    assert oItem.parHandle is None
    assert oItem.itemClass == nwItemClass.NO_CLASS
    assert oItem.itemType == nwItemType.FILE
    assert oItem.itemLayout == nwItemLayout.NO_LAYOUT

    assert theProject.saveProject(nwLipsum)
    assert theProject.closeProject()

@pytest.mark.project
def testOldProject(nwDummy, nwOldProj):
    theProject = NWProject(nwDummy)
    theProject.mainConf.showGUI = False

    # Create dummy files for known legacy files
    deleteFiles = [
        path.join(nwOldProj, "cache", "nwProject.nwx.0"),
        path.join(nwOldProj, "cache", "nwProject.nwx.1"),
        path.join(nwOldProj, "cache", "nwProject.nwx.2"),
        path.join(nwOldProj, "cache", "nwProject.nwx.3"),
        path.join(nwOldProj, "cache", "nwProject.nwx.4"),
        path.join(nwOldProj, "cache", "nwProject.nwx.5"),
        path.join(nwOldProj, "cache", "nwProject.nwx.6"),
        path.join(nwOldProj, "cache", "nwProject.nwx.7"),
        path.join(nwOldProj, "cache", "nwProject.nwx.8"),
        path.join(nwOldProj, "cache", "nwProject.nwx.9"),
        path.join(nwOldProj, "meta",  "mainOptions.json"),
        path.join(nwOldProj, "meta",  "exportOptions.json"),
        path.join(nwOldProj, "meta",  "outlineOptions.json"),
        path.join(nwOldProj, "meta",  "timelineOptions.json"),
        path.join(nwOldProj, "meta",  "docMergeOptions.json"),
        path.join(nwOldProj, "meta",  "sessionLogOptions.json"),
    ]

    # Add some files that shouldn't be there
    deleteFiles.append(path.join(nwOldProj, "data_f", "whatnow.nwd"))
    deleteFiles.append(path.join(nwOldProj, "data_f", "whatnow.txt"))

    # Add some folders that shouldn't be there
    mkdir(path.join(nwOldProj, "stuff"))
    mkdir(path.join(nwOldProj, "data_1", "stuff"))

    # Create dummy files
    mkdir(path.join(nwOldProj, "cache"))
    for aFile in deleteFiles:
        with open(aFile, mode="w+", encoding="utf8") as outFile:
            outFile.write("Hi")
    for aFile in deleteFiles:
        assert path.isfile(aFile)

    # Open project and check that files that are not supposed to be
    # there have been removed
    assert theProject.openProject(nwOldProj)
    for aFile in deleteFiles:
        assert not path.isfile(aFile)

    assert not path.isdir(path.join(nwOldProj, "data_1", "stuff"))
    assert not path.isdir(path.join(nwOldProj, "data_1"))
    assert not path.isdir(path.join(nwOldProj, "data_7"))
    assert not path.isdir(path.join(nwOldProj, "data_8"))
    assert not path.isdir(path.join(nwOldProj, "data_9"))
    assert not path.isdir(path.join(nwOldProj, "data_a"))
    assert not path.isdir(path.join(nwOldProj, "data_f"))

    # Check stuff that has been moved
    assert path.isdir(path.join(nwOldProj, "junk"))
    assert path.isdir(path.join(nwOldProj, "junk", "stuff"))
    assert path.isfile(path.join(nwOldProj, "junk", "whatnow.nwd"))
    assert path.isfile(path.join(nwOldProj, "junk", "whatnow.txt"))

    # Check that files we want to keep are in the right place
    assert path.isdir(path.join(nwOldProj, "cache"))
    assert path.isdir(path.join(nwOldProj, "content"))
    assert path.isdir(path.join(nwOldProj, "meta"))

    assert path.isfile(path.join(nwOldProj, "content", "f528d831f5b24.nwd"))
    assert path.isfile(path.join(nwOldProj, "content", "88124a4292d8b.nwd"))
    assert path.isfile(path.join(nwOldProj, "content", "91239bf2f8b69.nwd"))
    assert path.isfile(path.join(nwOldProj, "content", "19752e7f9d8af.nwd"))
    assert path.isfile(path.join(nwOldProj, "content", "a764d5acf5a21.nwd"))
    assert path.isfile(path.join(nwOldProj, "content", "9058ae29f0dfd.nwd"))
    assert path.isfile(path.join(nwOldProj, "content", "7ff63b8afc4cd.nwd"))

    assert path.isfile(path.join(nwOldProj, "meta", "tagsIndex.json"))
    assert path.isfile(path.join(nwOldProj, "meta", "sessionInfo.log"))

    # Close the project
    theProject.closeProject()

    # Check that new files have been created
    assert path.isfile(path.join(nwOldProj, "meta", "guiOptions.json"))
    assert path.isfile(path.join(nwOldProj, "meta", "sessionStats.log"))
    assert path.isfile(path.join(nwOldProj, "ToC.json"))
    assert path.isfile(path.join(nwOldProj, "ToC.txt"))

@pytest.mark.project
def testBackupProject(nwDummy, nwMinimal, nwTemp):
    theProject = NWProject(nwDummy)
    assert theProject.openProject(nwMinimal)

    # Test faulty settings
    # Invalid path
    theProject.mainConf.backupPath = None
    assert not theProject.zipIt(doNotify=False)

    # Missing project name
    theProject.mainConf.backupPath = nwTemp
    theProject.projName = ""
    assert not theProject.zipIt(doNotify=False)

    # Non-existent folder
    theProject.mainConf.backupPath = path.join(nwTemp, "nonexistent")
    theProject.projName = "Test Minimal"
    assert not theProject.zipIt(doNotify=False)

    # Same folder as project (causes infinite loop in zipping)
    theProject.mainConf.backupPath = nwMinimal
    assert not theProject.zipIt(doNotify=False)

    # Test correct settings
    theProject.mainConf.backupPath = nwTemp
    assert theProject.zipIt(doNotify=False)

    theFiles = listdir(path.join(nwTemp, "Test Minimal"))
    assert len(theFiles) == 1

    theZip = theFiles[0]
    assert theZip[:12] == "Backup from "
    assert theZip[-4:] == ".zip"

    # Extract the archive
    with ZipFile(path.join(nwTemp, "Test Minimal", theZip), "r") as inZip:
        inZip.extractall(path.join(nwTemp, "extract"))

    # Check that the main project file was restored
    assert cmpFiles(
        path.join(nwMinimal, "nwProject.nwx"), path.join(nwTemp, "extract", "nwProject.nwx")
    )
