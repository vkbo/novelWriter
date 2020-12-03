# -*- coding: utf-8 -*-
"""novelWriter Project Class Tester
"""

import pytest
import os

from shutil import copyfile
from zipfile import ZipFile

from tools import cmpFiles

from nw.core.project import NWProject
from nw.core.spellcheck import NWSpellEnchant, NWSpellSimple
from nw.constants import nwConst, nwItemClass, nwItemType, nwItemLayout, nwFiles

@pytest.mark.project
def testProjectNewOpenSave(nwFuncTemp, nwTempProj, refDir, tmpDir, dummyGUI):
    """Test that a basic project can be created, and opened and saved.
    """
    projFile = os.path.join(nwFuncTemp, "nwProject.nwx")
    testFile = os.path.join(nwTempProj, "1_nwProject.nwx")
    refFile  = os.path.join(refDir, "proj", "1_nwProject.nwx")

    theProject = NWProject(dummyGUI)
    theProject.projTree.setSeed(42)

    # Setting no data should fail
    assert not theProject.newProject({})

    # Try again with a proper path
    assert theProject.newProject({"projPath": nwFuncTemp})
    assert theProject.setProjectPath(nwFuncTemp)
    assert theProject.saveProject()
    assert theProject.closeProject()

    # Creating the project once more should fail
    assert not theProject.newProject({"projPath": nwFuncTemp})

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
def testProjectNewRoot(nwFuncTemp, nwTempProj, refDir, dummyGUI):
    """Check that new root folders can be added to the project.
    """
    projFile = os.path.join(nwFuncTemp, "nwProject.nwx")
    testFile = os.path.join(nwTempProj, "2_nwProject.nwx")
    refFile  = os.path.join(refDir, "proj", "2_nwProject.nwx")

    theProject = NWProject(dummyGUI)
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
def testProjectNewFile(nwFuncTemp, nwTempProj, refDir, dummyGUI):
    """Check that new files can be added to the project.
    """
    projFile = os.path.join(nwFuncTemp, "nwProject.nwx")
    testFile = os.path.join(nwTempProj, "3_nwProject.nwx")
    refFile  = os.path.join(refDir, "proj", "3_nwProject.nwx")

    theProject = NWProject(dummyGUI)
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
def testProjectNewCustomA(nwFuncTemp, nwTempProj, refDir, dummyGUI):
    """Create a new project from a project wizard dictionary.
    Custom type with chapters and scenes.
    """
    projFile = os.path.join(nwFuncTemp, "nwProject.nwx")
    testFile = os.path.join(nwTempProj, "4_nwProject.nwx")
    refFile  = os.path.join(refDir, "proj", "4_nwProject.nwx")

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
    theProject = NWProject(dummyGUI)
    theProject.projTree.setSeed(42)

    assert theProject.newProject(projData)
    assert theProject.saveProject()
    assert theProject.closeProject()

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [2, 6, 7, 8])

@pytest.mark.project
def testProjectNewCustomB(nwFuncTemp, nwTempProj, refDir, dummyGUI):
    """Create a new project from a project wizard dictionary.
    Custom type without chapters, but with scenes.
    """
    projFile = os.path.join(nwFuncTemp, "nwProject.nwx")
    testFile = os.path.join(nwTempProj, "5_nwProject.nwx")
    refFile  = os.path.join(refDir, "proj", "5_nwProject.nwx")

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
        "numChapters": 0,
        "numScenes": 6,
        "chFolders": True,
    }
    theProject = NWProject(dummyGUI)
    theProject.projTree.setSeed(42)

    assert theProject.newProject(projData)
    assert theProject.saveProject()
    assert theProject.closeProject()

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [2, 6, 7, 8])

@pytest.mark.project
def testProjectNewSampleA(nwFuncTemp, nwConf, dummyGUI, tmpDir):
    """Check that we can create a new project can be created from the
    provided sample project via a zip file.
    """
    projData = {
        "projName": "Test Sample",
        "projTitle": "Test Novel",
        "projAuthors": "Jane Doe\nJohn Doh\n",
        "projPath": nwFuncTemp,
        "popSample": True,
        "popMinimal": False,
        "popCustom": False,
    }
    theProject = NWProject(dummyGUI)
    theProject.projTree.setSeed(42)
    theProject.mainConf = nwConf

    # Sample set, but no path
    assert not theProject.newProject({"popSample": True})

    # Force the lookup path for assets to our temp folder
    srcSample = os.path.abspath(os.path.join(nwConf.appRoot, "sample"))
    dstSample = os.path.join(tmpDir, "sample.zip")
    nwConf.assetPath = tmpDir

    # Create and open a defective zip file
    with open(dstSample, mode="w+") as outFile:
        outFile.write("foo")

    assert not theProject.newProject(projData)
    os.unlink(dstSample)

    # Create a real zip file, and unpack it
    with ZipFile(dstSample, "w") as zipObj:
        zipObj.write(os.path.join(srcSample, "nwProject.nwx"), "nwProject.nwx")
        for docFile in os.listdir(os.path.join(srcSample, "content")):
            srcDoc = os.path.join(srcSample, "content", docFile)
            zipObj.write(srcDoc, "content/"+docFile)

    assert theProject.newProject(projData)
    assert theProject.openProject(nwFuncTemp)
    assert theProject.projName == "Sample Project"
    assert theProject.saveProject()
    assert theProject.closeProject()
    os.unlink(dstSample)

@pytest.mark.project
def testProjectNewSampleB(monkeypatch, nwFuncTemp, nwConf, dummyGUI, tmpDir):
    """Check that we can create a new project can be created from the
    provided sample project folder.
    """
    projData = {
        "projName": "Test Sample",
        "projTitle": "Test Novel",
        "projAuthors": "Jane Doe\nJohn Doh\n",
        "projPath": nwFuncTemp,
        "popSample": True,
        "popMinimal": False,
        "popCustom": False,
    }
    theProject = NWProject(dummyGUI)
    theProject.projTree.setSeed(42)
    theProject.mainConf = nwConf

    # Make sure we do not pick up the nw/assets/sample.zip file
    nwConf.assetPath = tmpDir

    # Set a fake project file name
    monkeypatch.setattr(nwFiles, "PROJ_FILE", "nothing.nwx")
    assert not theProject.newProject(projData)

    monkeypatch.setattr(nwFiles, "PROJ_FILE", "nwProject.nwx")
    assert theProject.newProject(projData)
    assert theProject.openProject(nwFuncTemp)
    assert theProject.projName == "Sample Project"
    assert theProject.saveProject()
    assert theProject.closeProject()

    # Misdirect the appRoot path so neither is possible
    nwConf.appRoot = tmpDir
    assert not theProject.newProject(projData)

@pytest.mark.project
def testProjectMethods(monkeypatch, nwMinimal, dummyGUI):
    """Test other project class methods and functions.
    """
    theProject = NWProject(dummyGUI)
    theProject.projTree.setSeed(42)
    assert theProject.openProject(nwMinimal)
    assert theProject.projPath == nwMinimal

    # Setting project path
    assert theProject.setProjectPath(None)
    assert theProject.projPath is None
    assert theProject.setProjectPath("")
    assert theProject.projPath is None
    assert theProject.setProjectPath("~")
    assert theProject.projPath == os.path.expanduser("~")

    # Create a new folder and populate it
    projPath = os.path.join(nwMinimal, "dummy1")
    assert theProject.setProjectPath(projPath, newProject=True)

    # Make os.mkdir fail
    def altMkdir(*args):
        raise Exception("Oops!")

    monkeypatch.setattr("os.mkdir", altMkdir)
    projPath = os.path.join(nwMinimal, "dummy2")
    assert not theProject.setProjectPath(projPath, newProject=True)

    # Project Name
    assert theProject.setProjectName("  A Name ")
    assert theProject.projName == "A Name"

    # Project Title
    assert theProject.setBookTitle("  A Title ")
    assert theProject.bookTitle == "A Title"

    # Project Authors
    assert not theProject.setBookAuthors([])
    assert theProject.setBookAuthors(" Jane Doe \n John Doh \n ")
    assert theProject.bookAuthors == ["Jane Doe", "John Doh"]

@pytest.mark.project
def testProjectOrphanedFiles(dummyGUI, nwLipsum):
    """Check that files in the content folder that are not tracked in
    the project XML file are handled correctly by the orphaned files
    function. It should also restore as much meta data as possible from
    the meta line at the top of the document file.
    """
    theProject = NWProject(dummyGUI)
    assert theProject.openProject(nwLipsum)
    assert theProject.projTree["636b6aa9b697b"] is None
    assert theProject.closeProject()

    # First Item with Meta Data
    orphPath = os.path.join(nwLipsum, "content", "636b6aa9b697b.nwd")
    with open(orphPath, mode="w", encoding="utf8") as outFile:
        outFile.write("%%~name:Mars\n")
        outFile.write("%%~path:5eaea4e8cdee8/636b6aa9b697b\n")
        outFile.write("%%~kind:WORLD/NOTE\n")
        outFile.write("%%~invalid\n")
        outFile.write("\n")

    # Second Item without Meta Data
    orphPath = os.path.join(nwLipsum, "content", "736b6aa9b697b.nwd")
    with open(orphPath, mode="w", encoding="utf8") as outFile:
        outFile.write("\n")

    # Invalid File Name
    dummyPath = os.path.join(nwLipsum, "content", "636b6aa9b697b.txt")
    with open(dummyPath, mode="w", encoding="utf8") as outFile:
        outFile.write("\n")

    # Invalid File Name
    dummyPath = os.path.join(nwLipsum, "content", "636b6aa9b697bb.nwd")
    with open(dummyPath, mode="w", encoding="utf8") as outFile:
        outFile.write("\n")

    # Invalid File Name
    dummyPath = os.path.join(nwLipsum, "content", "abcdefghijklm.nwd")
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
    assert oItem.itemParent is None
    assert oItem.itemClass == nwItemClass.WORLD
    assert oItem.itemType == nwItemType.FILE
    assert oItem.itemLayout == nwItemLayout.NOTE

    # Second Item without Meta Data
    oItem = theProject.projTree["736b6aa9b697b"]
    assert oItem is not None
    assert oItem.itemName == "Orphaned File 1"
    assert oItem.itemHandle == "736b6aa9b697b"
    assert oItem.itemParent is None
    assert oItem.itemClass == nwItemClass.NO_CLASS
    assert oItem.itemType == nwItemType.FILE
    assert oItem.itemLayout == nwItemLayout.NO_LAYOUT

    assert theProject.saveProject(nwLipsum)
    assert theProject.closeProject()

@pytest.mark.project
def testProjectOldFormat(dummyGUI, nwOldProj):
    """Test that a project folder structure of version 1.0 can be
    converted to the latest folder structure. Version 1.0 split the
    documents into 'data_0' ... 'data_f' folders, which are now all
    contained in a single 'content' folder.
    """
    theProject = NWProject(dummyGUI)
    theProject.mainConf.showGUI = False

    # Create dummy files for known legacy files
    deleteFiles = [
        os.path.join(nwOldProj, "cache", "nwProject.nwx.0"),
        os.path.join(nwOldProj, "cache", "nwProject.nwx.1"),
        os.path.join(nwOldProj, "cache", "nwProject.nwx.2"),
        os.path.join(nwOldProj, "cache", "nwProject.nwx.3"),
        os.path.join(nwOldProj, "cache", "nwProject.nwx.4"),
        os.path.join(nwOldProj, "cache", "nwProject.nwx.5"),
        os.path.join(nwOldProj, "cache", "nwProject.nwx.6"),
        os.path.join(nwOldProj, "cache", "nwProject.nwx.7"),
        os.path.join(nwOldProj, "cache", "nwProject.nwx.8"),
        os.path.join(nwOldProj, "cache", "nwProject.nwx.9"),
        os.path.join(nwOldProj, "meta",  "mainOptions.json"),
        os.path.join(nwOldProj, "meta",  "exportOptions.json"),
        os.path.join(nwOldProj, "meta",  "outlineOptions.json"),
        os.path.join(nwOldProj, "meta",  "timelineOptions.json"),
        os.path.join(nwOldProj, "meta",  "docMergeOptions.json"),
        os.path.join(nwOldProj, "meta",  "sessionLogOptions.json"),
    ]

    # Add some files that shouldn't be there
    deleteFiles.append(os.path.join(nwOldProj, "data_f", "whatnow.nwd"))
    deleteFiles.append(os.path.join(nwOldProj, "data_f", "whatnow.txt"))

    # Add some folders that shouldn't be there
    os.mkdir(os.path.join(nwOldProj, "stuff"))
    os.mkdir(os.path.join(nwOldProj, "data_1", "stuff"))

    # Create dummy files
    os.mkdir(os.path.join(nwOldProj, "cache"))
    for aFile in deleteFiles:
        with open(aFile, mode="w+", encoding="utf8") as outFile:
            outFile.write("Hi")
    for aFile in deleteFiles:
        assert os.path.isfile(aFile)

    # Open project and check that files that are not supposed to be
    # there have been removed
    assert theProject.openProject(nwOldProj)
    for aFile in deleteFiles:
        assert not os.path.isfile(aFile)

    assert not os.path.isdir(os.path.join(nwOldProj, "data_1", "stuff"))
    assert not os.path.isdir(os.path.join(nwOldProj, "data_1"))
    assert not os.path.isdir(os.path.join(nwOldProj, "data_7"))
    assert not os.path.isdir(os.path.join(nwOldProj, "data_8"))
    assert not os.path.isdir(os.path.join(nwOldProj, "data_9"))
    assert not os.path.isdir(os.path.join(nwOldProj, "data_a"))
    assert not os.path.isdir(os.path.join(nwOldProj, "data_f"))

    # Check stuff that has been moved
    assert os.path.isdir(os.path.join(nwOldProj, "junk"))
    assert os.path.isdir(os.path.join(nwOldProj, "junk", "stuff"))
    assert os.path.isfile(os.path.join(nwOldProj, "junk", "whatnow.nwd"))
    assert os.path.isfile(os.path.join(nwOldProj, "junk", "whatnow.txt"))

    # Check that files we want to keep are in the right place
    assert os.path.isdir(os.path.join(nwOldProj, "cache"))
    assert os.path.isdir(os.path.join(nwOldProj, "content"))
    assert os.path.isdir(os.path.join(nwOldProj, "meta"))

    assert os.path.isfile(os.path.join(nwOldProj, "content", "f528d831f5b24.nwd"))
    assert os.path.isfile(os.path.join(nwOldProj, "content", "88124a4292d8b.nwd"))
    assert os.path.isfile(os.path.join(nwOldProj, "content", "91239bf2f8b69.nwd"))
    assert os.path.isfile(os.path.join(nwOldProj, "content", "19752e7f9d8af.nwd"))
    assert os.path.isfile(os.path.join(nwOldProj, "content", "a764d5acf5a21.nwd"))
    assert os.path.isfile(os.path.join(nwOldProj, "content", "9058ae29f0dfd.nwd"))
    assert os.path.isfile(os.path.join(nwOldProj, "content", "7ff63b8afc4cd.nwd"))

    assert os.path.isfile(os.path.join(nwOldProj, "meta", "tagsIndex.json"))
    assert os.path.isfile(os.path.join(nwOldProj, "meta", "sessionInfo.log"))

    # Close the project
    theProject.closeProject()

    # Check that new files have been created
    assert os.path.isfile(os.path.join(nwOldProj, "meta", "guiOptions.json"))
    assert os.path.isfile(os.path.join(nwOldProj, "meta", "sessionStats.log"))
    assert os.path.isfile(os.path.join(nwOldProj, "ToC.txt"))

@pytest.mark.project
def testProjectBackup(dummyGUI, nwMinimal, tmpDir):
    """Test the automated backup feature of the project class. The test
    creates a backup of the Minimal test project, and then unzips the
    backupd file and checks that the project XML file is identical to
    the original file.
    """
    theProject = NWProject(dummyGUI)
    assert theProject.openProject(nwMinimal)

    # Test faulty settings
    # Invalid path
    theProject.mainConf.backupPath = None
    assert not theProject.zipIt(doNotify=False)

    # Missing project name
    theProject.mainConf.backupPath = tmpDir
    theProject.projName = ""
    assert not theProject.zipIt(doNotify=False)

    # Non-existent folder
    theProject.mainConf.backupPath = os.path.join(tmpDir, "nonexistent")
    theProject.projName = "Test Minimal"
    assert not theProject.zipIt(doNotify=False)

    # Same folder as project (causes infinite loop in zipping)
    theProject.mainConf.backupPath = nwMinimal
    assert not theProject.zipIt(doNotify=False)

    # Test correct settings
    theProject.mainConf.backupPath = tmpDir
    assert theProject.zipIt(doNotify=False)

    theFiles = os.listdir(os.path.join(tmpDir, "Test Minimal"))
    assert len(theFiles) == 1

    theZip = theFiles[0]
    assert theZip[:12] == "Backup from "
    assert theZip[-4:] == ".zip"

    # Extract the archive
    with ZipFile(os.path.join(tmpDir, "Test Minimal", theZip), "r") as inZip:
        inZip.extractall(os.path.join(tmpDir, "extract"))

    # Check that the main project file was restored
    assert cmpFiles(
        os.path.join(nwMinimal, "nwProject.nwx"), os.path.join(tmpDir, "extract", "nwProject.nwx")
    )
