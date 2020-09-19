# -*- coding: utf-8 -*-
"""novelWriter Dialog Class Tester
"""

import nw
import pytest
import json
from shutil import copyfile
from nwtools import cmpFiles

from os import path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialogButtonBox, QTreeWidgetItem

from nw.gui import (
    GuiProjectSettings, GuiItemEditor, GuiAbout, GuiBuildNovel,
    GuiDocMerge, GuiDocSplit, GuiWritingStats, GuiProjectWizard,
    GuiProjectLoad
)
from nw.constants import (
    nwItemType, nwItemLayout, nwItemClass
)

keyDelay = 2
stepDelay = 20

@pytest.mark.gui
def testProjectEditor(qtbot, nwFuncTemp, nwTempGUI, nwRef, nwTemp):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwFuncTemp, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    # Create new, save, open project
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": nwFuncTemp}, True)
    nwGUI.mainConf.backupPath = nwFuncTemp

    projEdit = GuiProjectSettings(nwGUI, nwGUI.theProject)
    projEdit.show()
    qtbot.addWidget(projEdit)

    qtbot.wait(stepDelay)
    projEdit.tabMain.editName.setText("")
    for c in "Project Name":
        qtbot.keyClick(projEdit.tabMain.editName, c, delay=keyDelay)
    for c in "Project Title":
        qtbot.keyClick(projEdit.tabMain.editTitle, c, delay=keyDelay)
    for c in "Jane Doe":
        qtbot.keyClick(projEdit.tabMain.editAuthors, c, delay=keyDelay)
    qtbot.keyClick(projEdit.tabMain.editAuthors, Qt.Key_Return, delay=keyDelay)
    for c in "John Doh":
        qtbot.keyClick(projEdit.tabMain.editAuthors, c, delay=keyDelay)

    # Test Status Tab
    qtbot.wait(stepDelay)
    projEdit._tabBox.setCurrentWidget(projEdit.tabStatus)
    projEdit.tabStatus.listBox.item(2).setSelected(True)
    qtbot.mouseClick(projEdit.tabStatus.delButton, Qt.LeftButton)
    qtbot.mouseClick(projEdit.tabStatus.newButton, Qt.LeftButton)
    projEdit.tabStatus.listBox.item(3).setSelected(True)
    for n in range(8):
        qtbot.keyClick(projEdit.tabStatus.editName, Qt.Key_Backspace, delay=keyDelay)
    for c in "Final":
        qtbot.keyClick(projEdit.tabStatus.editName, c, delay=keyDelay)
    qtbot.mouseClick(projEdit.tabStatus.saveButton, Qt.LeftButton)

    # Auto-Replace Tab
    qtbot.wait(stepDelay)
    projEdit._tabBox.setCurrentWidget(projEdit.tabReplace)

    qtbot.mouseClick(projEdit.tabReplace.addButton, Qt.LeftButton)
    projEdit.tabReplace.listBox.topLevelItem(0).setSelected(True)
    for c in "Th is ":
        qtbot.keyClick(projEdit.tabReplace.editKey, c, delay=keyDelay)
    for c in "With This Stuff ":
        qtbot.keyClick(projEdit.tabReplace.editValue, c, delay=keyDelay)
    qtbot.mouseClick(projEdit.tabReplace.saveButton, Qt.LeftButton)

    qtbot.wait(stepDelay)
    projEdit.tabReplace.listBox.clearSelection()
    qtbot.mouseClick(projEdit.tabReplace.addButton, Qt.LeftButton)

    newIdx = -1
    for i in range(projEdit.tabReplace.listBox.topLevelItemCount()):
        if projEdit.tabReplace.listBox.topLevelItem(i).text(0) == "<keyword2>":
            newIdx = i
            break

    assert newIdx >= 0
    newItem = projEdit.tabReplace.listBox.topLevelItem(newIdx)
    projEdit.tabReplace.listBox.setCurrentItem(newItem)
    qtbot.mouseClick(projEdit.tabReplace.delButton, Qt.LeftButton)

    qtbot.wait(stepDelay)
    projEdit._doSave()

    # Open again, and check project settings
    projEdit = GuiProjectSettings(nwGUI, nwGUI.theProject)
    qtbot.addWidget(projEdit)
    assert projEdit.tabMain.editName.text()  == "Project Name"
    assert projEdit.tabMain.editTitle.text() == "Project Title"
    theAuth = projEdit.tabMain.editAuthors.toPlainText().strip().splitlines()
    assert len(theAuth) == 2
    assert theAuth[0] == "Jane Doe"
    assert theAuth[1] == "John Doh"

    projEdit._doClose()

    qtbot.wait(stepDelay)
    assert nwGUI.saveProject()
    qtbot.wait(stepDelay)

    # Check the files
    projFile = path.join(nwFuncTemp, "nwProject.nwx")
    testFile = path.join(nwTempGUI, "2_nwProject.nwx")
    refFile  = path.join(nwRef, "gui", "2_nwProject.nwx")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [2, 8, 9, 10])

    # qtbot.stopForInteraction()
    nwGUI.closeMain()

@pytest.mark.gui
def testItemEditor(qtbot, nwFuncTemp, nwTempGUI, nwRef, nwTemp):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwFuncTemp, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    # Create new, save, open project
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": nwFuncTemp}, True)
    assert nwGUI.openDocument("0e17daca5f3e1")

    itemEdit = GuiItemEditor(nwGUI, nwGUI.theProject, "0e17daca5f3e1")
    qtbot.addWidget(itemEdit)

    assert itemEdit.editName.text()          == "New Scene"
    assert itemEdit.editStatus.currentData() == "New"
    assert itemEdit.editLayout.currentData() == nwItemLayout.SCENE

    for c in "Just a Page":
        qtbot.keyClick(itemEdit.editName, c, delay=keyDelay)
    itemEdit.editStatus.setCurrentIndex(1)
    layoutIdx = itemEdit.editLayout.findData(nwItemLayout.PAGE)
    itemEdit.editLayout.setCurrentIndex(layoutIdx)

    itemEdit.editExport.setChecked(False)
    assert not itemEdit.editExport.isChecked()
    itemEdit._doSave()

    itemEdit = GuiItemEditor(nwGUI, nwGUI.theProject, "0e17daca5f3e1")
    qtbot.addWidget(itemEdit)
    assert itemEdit.editName.text()          == "Just a Page"
    assert itemEdit.editStatus.currentData() == "Note"
    assert itemEdit.editLayout.currentData() == nwItemLayout.PAGE
    itemEdit._doClose()

    # Check that the header is updated
    nwGUI.docEditor.updateDocInfo("0e17daca5f3e1")
    assert nwGUI.docEditor.docHeader.theTitle.text() == "Novel  ›  New Chapter  ›  Just a Page"
    assert not nwGUI.docEditor.setCursorLine("where?")
    assert nwGUI.docEditor.setCursorLine(2)
    qtbot.wait(stepDelay)
    assert nwGUI.docEditor.getCursorPosition() == 15

    qtbot.wait(stepDelay)
    assert nwGUI.saveProject()
    qtbot.wait(stepDelay)

    # Check the files
    projFile = path.join(nwFuncTemp, "nwProject.nwx")
    testFile = path.join(nwTempGUI, "3_nwProject.nwx")
    refFile  = path.join(nwRef, "gui", "3_nwProject.nwx")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [2, 6, 7, 8])

    nwGUI.closeMain()
    # qtbot.stopForInteraction()

@pytest.mark.gui
def testWritingStatsExport(qtbot, nwFuncTemp, nwTemp):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwFuncTemp, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    # Create new, save, close project
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": nwFuncTemp}, True)
    assert nwGUI.saveProject()
    assert nwGUI.closeProject()
    qtbot.wait(stepDelay)

    assert nwGUI.openProject(nwFuncTemp)
    qtbot.wait(stepDelay)

    # Add some text to the scene file
    assert nwGUI.openDocument("0e17daca5f3e1")
    assert nwGUI.docEditor.insertText(
        "# Scene One\n\n"
        "It was the best of times, it was the worst of times, it was the age of wisdom, it was "
        "the age of foolishness, it was the epoch of belief, it was the epoch of incredulity, it "
        "was the season of Light, it was the season of Darkness, it was the spring of hope, it "
        "was the winter of despair, we had everything before us, we had nothing before us, we "
        "were all going direct to Heaven, we were all going direct the other way – in short, the "
        "period was so far like the present period, that some of its noisiest authorities "
        "insisted on its being received, for good or for evil, in the superlative degree of "
        "comparison only.\n\n"
    )
    assert nwGUI.saveDocument()

    # Add a note file with some text
    nwGUI.setFocus(1)
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem("71ee45a3c0db9").setSelected(True)
    nwGUI.treeView.newTreeItem(nwItemType.FILE, None)
    assert nwGUI.openSelectedItem()
    assert nwGUI.docEditor.insertText(
        "# Jane Doe\n\n"
        "All about Jane.\n\n"
    )
    assert nwGUI.saveDocument()
    qtbot.wait(500) # Ensures that the session length is > 0

    assert nwGUI.saveProject()
    assert nwGUI.closeProject()
    qtbot.wait(stepDelay)

    # Open again, and check the stats
    assert nwGUI.openProject(nwFuncTemp)
    qtbot.wait(stepDelay)

    nwGUI.mainConf.lastPath = nwFuncTemp
    sessLog = GuiWritingStats(nwGUI, nwGUI.theProject)
    sessLog.show()
    qtbot.wait(stepDelay)

    assert sessLog._saveData(sessLog.FMT_CSV)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = path.join(nwFuncTemp, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.loads(inFile.read())

    assert len(jsonData) == 2
    assert jsonData[1]["length"] >= 0
    assert jsonData[1]["newWords"] == 126
    assert jsonData[1]["novelWords"] == 127
    assert jsonData[1]["noteWords"] == 5

    # No Novel Files
    qtbot.mouseClick(sessLog.incNovel, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = path.join(nwFuncTemp, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.loads(inFile.read())

    assert len(jsonData) == 1
    assert jsonData[0]["length"] >= 0
    assert jsonData[0]["newWords"] == 5
    assert jsonData[0]["novelWords"] == 127
    assert jsonData[0]["noteWords"] == 5

    # No Note Files
    qtbot.mouseClick(sessLog.incNovel, Qt.LeftButton)
    qtbot.mouseClick(sessLog.incNotes, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = path.join(nwFuncTemp, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.loads(inFile.read())

    assert len(jsonData) == 2
    assert jsonData[1]["length"] >= 0
    assert jsonData[1]["newWords"] == 121
    assert jsonData[1]["novelWords"] == 127
    assert jsonData[1]["noteWords"] == 5

    # No Negative Entries
    qtbot.mouseClick(sessLog.incNotes, Qt.LeftButton)
    qtbot.mouseClick(sessLog.hideNegative, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = path.join(nwFuncTemp, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.loads(inFile.read())

    assert len(jsonData) == 2

    # Un-hide Zero Entries
    qtbot.mouseClick(sessLog.hideNegative, Qt.LeftButton)
    qtbot.mouseClick(sessLog.hideZeros, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = path.join(nwFuncTemp, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.loads(inFile.read())

    assert len(jsonData) == 2

    # Group by Day
    qtbot.mouseClick(sessLog.groupByDay, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = path.join(nwFuncTemp, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.loads(inFile.read())

    # Check against both 1 and 2 as this can be 2 if test was started just before midnight.
    # A failed test should in any case produce a 4
    assert len(jsonData) in (1, 2)

    # qtbot.stopForInteraction()

    sessLog._doClose()
    nwGUI.closeMain()

@pytest.mark.gui
def testAboutBox(qtbot, nwFuncTemp, nwTemp):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwFuncTemp, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    msgAbout = GuiAbout(nwGUI)
    assert msgAbout.pageAbout.document().characterCount() > 100
    assert msgAbout.pageLicense.document().characterCount() > 100

    # qtbot.stopForInteraction()
    msgAbout._doClose()
    nwGUI.closeMain()

@pytest.mark.gui
def testBuildTool(qtbot, nwTempBuild, nwLipsum, nwRef, nwTemp):

    nwGUI = nw.main(["--testmode", "--config=%s" % nwLipsum, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    assert nwGUI.openProject(nwLipsum)

    nwGUI.mainConf.lastPath = nwLipsum

    nwBuild = GuiBuildNovel(nwGUI, nwGUI.theProject)

    # Default Settings
    qtbot.mouseClick(nwBuild.buildNovel, Qt.LeftButton)

    assert nwBuild._saveDocument(nwBuild.FMT_NWD)
    assert nwBuild._saveDocument(nwBuild.FMT_HTM)

    projFile = path.join(nwLipsum, "Lorem Ipsum.nwd")
    testFile = path.join(nwTempBuild, "1_LoremIpsum.nwd")
    refFile  = path.join(nwRef, "build", "1_LoremIpsum.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    projFile = path.join(nwLipsum, "Lorem Ipsum.htm")
    testFile = path.join(nwTempBuild, "1_LoremIpsum.htm")
    refFile  = path.join(nwRef, "build", "1_LoremIpsum.htm")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    # Change Title Formats and Flip Switches
    nwBuild.fmtChapter.setText(r"Chapter %chw%: %title%")
    qtbot.wait(stepDelay)
    nwBuild.fmtScene.setText(r"Scene %ch%.%sc%: %title%")
    qtbot.wait(stepDelay)
    nwBuild.fmtSection.setText(r"%ch%.%sc%.1: %title%")
    qtbot.wait(stepDelay)

    qtbot.mouseClick(nwBuild.justifyText, Qt.LeftButton)
    qtbot.wait(stepDelay)
    qtbot.mouseClick(nwBuild.includeSynopsis, Qt.LeftButton)
    qtbot.wait(stepDelay)
    qtbot.mouseClick(nwBuild.includeComments, Qt.LeftButton)
    qtbot.wait(stepDelay)
    qtbot.mouseClick(nwBuild.includeKeywords, Qt.LeftButton)
    qtbot.wait(stepDelay)

    qtbot.mouseClick(nwBuild.noteFiles, Qt.LeftButton)
    qtbot.wait(stepDelay)
    qtbot.mouseClick(nwBuild.ignoreFlag, Qt.LeftButton)
    qtbot.wait(stepDelay)

    qtbot.mouseClick(nwBuild.buildNovel, Qt.LeftButton)

    assert nwBuild._saveDocument(nwBuild.FMT_NWD)
    assert nwBuild._saveDocument(nwBuild.FMT_HTM)

    projFile = path.join(nwLipsum, "Lorem Ipsum.nwd")
    testFile = path.join(nwTempBuild, "2_LoremIpsum.nwd")
    refFile  = path.join(nwRef, "build", "2_LoremIpsum.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    projFile = path.join(nwLipsum, "Lorem Ipsum.htm")
    testFile = path.join(nwTempBuild, "2_LoremIpsum.htm")
    refFile  = path.join(nwRef, "build", "2_LoremIpsum.htm")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    # Putline Mode
    nwBuild.fmtChapter.setText(r"Chapter %chw%: %title%")
    qtbot.wait(stepDelay)
    nwBuild.fmtScene.setText(r"Scene %sca%: %title%")
    qtbot.wait(stepDelay)
    nwBuild.fmtSection.setText(r"Section: %title%")
    qtbot.wait(stepDelay)

    qtbot.mouseClick(nwBuild.includeComments, Qt.LeftButton)
    qtbot.wait(stepDelay)
    qtbot.mouseClick(nwBuild.noteFiles, Qt.LeftButton)
    qtbot.wait(stepDelay)
    qtbot.mouseClick(nwBuild.ignoreFlag, Qt.LeftButton)
    qtbot.wait(stepDelay)
    qtbot.mouseClick(nwBuild.includeBody, Qt.LeftButton)
    qtbot.wait(stepDelay)

    qtbot.mouseClick(nwBuild.buildNovel, Qt.LeftButton)

    assert nwBuild._saveDocument(nwBuild.FMT_NWD)
    assert nwBuild._saveDocument(nwBuild.FMT_HTM)

    projFile = path.join(nwLipsum, "Lorem Ipsum.nwd")
    testFile = path.join(nwTempBuild, "3_LoremIpsum.nwd")
    refFile  = path.join(nwRef, "build", "3_LoremIpsum.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    projFile = path.join(nwLipsum, "Lorem Ipsum.htm")
    testFile = path.join(nwTempBuild, "3_LoremIpsum.htm")
    refFile  = path.join(nwRef, "build", "3_LoremIpsum.htm")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    # qtbot.stopForInteraction()
    nwBuild._doClose()
    nwGUI.closeMain()

@pytest.mark.gui
def testMergeSplitTools(qtbot, nwTempGUI, nwLipsum, nwRef, nwTemp):

    nwGUI = nw.main(["--testmode", "--config=%s" % nwLipsum, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.openProject(nwLipsum)
    qtbot.wait(stepDelay)

    assert nwGUI.treeView.setSelectedHandle("45e6b01ca35c1")
    qtbot.wait(stepDelay)

    nwMerge = GuiDocMerge(nwGUI, nwGUI.theProject)
    qtbot.wait(stepDelay)

    nwMerge._doMerge()
    qtbot.wait(stepDelay)

    assert nwGUI.theProject.projTree["73475cb40a568"] is not None

    projFile = path.join(nwLipsum, "content", "73475cb40a568.nwd")
    testFile = path.join(nwTempGUI, "4_73475cb40a568.nwd")
    refFile  = path.join(nwRef, "gui", "4_73475cb40a568.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    # Split By Chapter
    assert nwGUI.treeView.setSelectedHandle("73475cb40a568")
    qtbot.wait(stepDelay)
    nwSplit = GuiDocSplit(nwGUI, nwGUI.theProject)
    qtbot.wait(stepDelay)
    nwSplit.splitLevel.setCurrentIndex(1)
    qtbot.wait(stepDelay)

    nwSplit._doSplit()
    assert nwGUI.theProject.projTree["71ee45a3c0db9"] is not None

    # This should give us back the file as it was before
    projFile = path.join(nwLipsum, "content", "71ee45a3c0db9.nwd")
    testFile = path.join(nwTempGUI, "4_71ee45a3c0db9.nwd")
    refFile  = path.join(nwRef, "gui", "4_73475cb40a568.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [1])

    # Split By Scene
    assert nwGUI.treeView.setSelectedHandle("73475cb40a568")
    qtbot.wait(stepDelay)
    nwSplit = GuiDocSplit(nwGUI, nwGUI.theProject)
    qtbot.wait(stepDelay)
    nwSplit.splitLevel.setCurrentIndex(2)
    qtbot.wait(stepDelay)

    nwSplit._doSplit()

    assert nwGUI.theProject.projTree["25fc0e7096fc6"] is not None
    assert nwGUI.theProject.projTree["31489056e0916"] is not None
    assert nwGUI.theProject.projTree["98010bd9270f9"] is not None

    projFile = path.join(nwLipsum, "content", "25fc0e7096fc6.nwd")
    testFile = path.join(nwTempGUI, "5_25fc0e7096fc6.nwd")
    refFile  = path.join(nwRef, "gui", "5_25fc0e7096fc6.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    projFile = path.join(nwLipsum, "content", "31489056e0916.nwd")
    testFile = path.join(nwTempGUI, "5_31489056e0916.nwd")
    refFile  = path.join(nwRef, "gui", "5_31489056e0916.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    projFile = path.join(nwLipsum, "content", "98010bd9270f9.nwd")
    testFile = path.join(nwTempGUI, "5_98010bd9270f9.nwd")
    refFile  = path.join(nwRef, "gui", "5_98010bd9270f9.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    # Split By Section
    assert nwGUI.treeView.setSelectedHandle("73475cb40a568")
    qtbot.wait(stepDelay)
    nwSplit = GuiDocSplit(nwGUI, nwGUI.theProject)
    qtbot.wait(stepDelay)
    nwSplit.splitLevel.setCurrentIndex(3)
    qtbot.wait(stepDelay)

    nwSplit._doSplit()

    assert nwGUI.theProject.projTree["1a6562590ef19"] is not None
    assert nwGUI.theProject.projTree["031b4af5197ec"] is not None
    assert nwGUI.theProject.projTree["41cfc0d1f2d12"] is not None
    assert nwGUI.theProject.projTree["2858dcd1057d3"] is not None
    assert nwGUI.theProject.projTree["2fca346db6561"] is not None

    projFile = path.join(nwLipsum, "content", "1a6562590ef19.nwd")
    testFile = path.join(nwTempGUI, "5_25fc0e7096fc6.nwd")
    refFile  = path.join(nwRef, "gui", "5_25fc0e7096fc6.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [1])

    projFile = path.join(nwLipsum, "content", "031b4af5197ec.nwd")
    testFile = path.join(nwTempGUI, "5_031b4af5197ec.nwd")
    refFile  = path.join(nwRef, "gui", "5_031b4af5197ec.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    projFile = path.join(nwLipsum, "content", "41cfc0d1f2d12.nwd")
    testFile = path.join(nwTempGUI, "5_41cfc0d1f2d12.nwd")
    refFile  = path.join(nwRef, "gui", "5_41cfc0d1f2d12.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    projFile = path.join(nwLipsum, "content", "2858dcd1057d3.nwd")
    testFile = path.join(nwTempGUI, "5_2858dcd1057d3.nwd")
    refFile  = path.join(nwRef, "gui", "5_2858dcd1057d3.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    projFile = path.join(nwLipsum, "content", "2fca346db6561.nwd")
    testFile = path.join(nwTempGUI, "5_2fca346db6561.nwd")
    refFile  = path.join(nwRef, "gui", "5_2fca346db6561.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    # qtbot.stopForInteraction()
    nwGUI.closeMain()

@pytest.mark.gui
def testNewProjectWizard(qtbot, nwLipsum, nwTemp):

    from PyQt5.QtWidgets import QWizard
    from nw.gui.projwizard import (
        ProjWizardIntroPage, ProjWizardFolderPage, ProjWizardPopulatePage,
        ProjWizardCustomPage, ProjWizardFinalPage
    )

    nwGUI = nw.main(["--testmode", "--config=%s" % nwLipsum, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    for wStep in range(3):

        # The Wizard
        nwWiz = GuiProjectWizard(nwGUI)
        nwWiz.show()
        qtbot.waitForWindowShown(nwWiz)

        # Intro Page
        introPage = nwWiz.currentPage()
        assert isinstance(introPage, ProjWizardIntroPage)
        assert not nwWiz.button(QWizard.NextButton).isEnabled()

        qtbot.wait(stepDelay)
        for c in "Test Minimal":
            qtbot.keyClick(introPage.projName, c, delay=keyDelay)

        qtbot.wait(stepDelay)
        for c in "Minimal Novel":
            qtbot.keyClick(introPage.projTitle, c, delay=keyDelay)

        qtbot.wait(stepDelay)
        for c in "Jane Doe":
            qtbot.keyClick(introPage.projAuthors, c, delay=keyDelay)

        # Setting projName should activate the button
        assert nwWiz.button(QWizard.NextButton).isEnabled()

        qtbot.wait(stepDelay)
        qtbot.mouseClick(nwWiz.button(QWizard.NextButton), Qt.LeftButton)

        # Folder Page
        storagePage = nwWiz.currentPage()
        assert isinstance(storagePage, ProjWizardFolderPage)
        assert not nwWiz.button(QWizard.NextButton).isEnabled()

        qtbot.wait(stepDelay)
        projPath = path.join(nwTemp, "dummy")
        for c in projPath:
            qtbot.keyClick(storagePage.projPath, c, delay=keyDelay)

        # Setting projPath should activate the button
        assert nwWiz.button(QWizard.NextButton).isEnabled()

        qtbot.wait(stepDelay)
        qtbot.mouseClick(nwWiz.button(QWizard.NextButton), Qt.LeftButton)

        # Populate Page
        popPage = nwWiz.currentPage()
        assert isinstance(popPage, ProjWizardPopulatePage)
        assert nwWiz.button(QWizard.NextButton).isEnabled()

        qtbot.wait(stepDelay)
        if wStep == 0:
            popPage.popMinimal.setChecked(True)
        elif wStep == 1:
            popPage.popCustom.setChecked(True)
        elif wStep == 2:
            popPage.popSample.setChecked(True)

        qtbot.wait(stepDelay)
        qtbot.mouseClick(nwWiz.button(QWizard.NextButton), Qt.LeftButton)

        # Custom Page
        if wStep == 1:
            customPage = nwWiz.currentPage()
            assert isinstance(customPage, ProjWizardCustomPage)
            assert nwWiz.button(QWizard.NextButton).isEnabled()

            customPage.addPlot.setChecked(True)
            customPage.addChar.setChecked(True)
            customPage.addWorld.setChecked(True)
            customPage.addTime.setChecked(True)
            customPage.addObject.setChecked(True)
            customPage.addEntity.setChecked(True)

            qtbot.wait(stepDelay)
            qtbot.mouseClick(nwWiz.button(QWizard.NextButton), Qt.LeftButton)

        # Final Page
        finalPage = nwWiz.currentPage()
        assert isinstance(finalPage, ProjWizardFinalPage)
        assert nwWiz.button(QWizard.FinishButton).isEnabled()
        qtbot.mouseClick(nwWiz.button(QWizard.FinishButton), Qt.LeftButton)

        # Check Data
        projData = nwGUI._assembleProjectWizardData(nwWiz)
        assert projData["projName"]    == "Test Minimal"
        assert projData["projTitle"]   == "Minimal Novel"
        assert projData["projAuthors"] == "Jane Doe"
        assert projData["projPath"]    == projPath
        assert projData["popMinimal"]  == (wStep == 0)
        assert projData["popCustom"]   == (wStep == 1)
        assert projData["popSample"]   == (wStep == 2)
        if wStep == 1:
            assert projData["addRoots"] == [
                nwItemClass.PLOT,
                nwItemClass.CHARACTER,
                nwItemClass.WORLD,
                nwItemClass.TIMELINE,
                nwItemClass.OBJECT,
                nwItemClass.ENTITY,
            ]
            assert projData["numChapters"] == 5
            assert projData["numScenes"] == 5
            assert projData["chFolders"]
        else:
            assert projData["addRoots"] == []
            assert projData["numChapters"] == 0
            assert projData["numScenes"] == 0
            assert not projData["chFolders"]

    # qtbot.stopForInteraction()
    nwGUI.closeMain()

@pytest.mark.gui
def testLoadProject(qtbot, nwMinimal, nwTemp):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwMinimal, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    assert nwGUI.openProject(nwMinimal)
    assert nwGUI.closeProject()

    nwLoad = GuiProjectLoad(nwGUI)
    nwLoad.show()

    recentCount = nwLoad.listBox.topLevelItemCount()
    assert recentCount > 0

    selItem = nwLoad.listBox.topLevelItem(0)
    selPath = selItem.data(nwLoad.C_NAME, Qt.UserRole)
    assert isinstance(selItem, QTreeWidgetItem)

    nwLoad.selPath.setText("")
    nwLoad.listBox.setCurrentItem(selItem)
    nwLoad._doSelectRecent()
    assert nwLoad.selPath.text() == selPath

    qtbot.mouseClick(nwLoad.buttonBox.button(QDialogButtonBox.Open), Qt.LeftButton)
    assert nwLoad.openPath == selPath
    assert nwLoad.openState == nwLoad.OPEN_STATE

    del nwLoad
    nwLoad = GuiProjectLoad(nwGUI)
    nwLoad.show()

    qtbot.mouseClick(nwLoad.buttonBox.button(QDialogButtonBox.Cancel), Qt.LeftButton)
    assert nwLoad.openPath is None
    assert nwLoad.openState == nwLoad.NONE_STATE

    nwLoad.show()
    qtbot.mouseClick(nwLoad.newButton, Qt.LeftButton)
    assert nwLoad.openPath is None
    assert nwLoad.openState == nwLoad.NEW_STATE

    nwLoad.show()
    nwLoad._keyPressDelete()
    assert nwLoad.listBox.topLevelItemCount() == recentCount - 1

    nwLoad.close()
    # qtbot.stopForInteraction()
    nwGUI.closeMain()
