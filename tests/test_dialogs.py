# -*- coding: utf-8 -*-
"""novelWriter Dialog Class Tester
"""

import nw
import pytest
import json
import os
import sys

from shutil import copyfile
from nwtools import cmpFiles, getGuiItem

from PyQt5.QtCore import Qt, QItemSelectionModel
from PyQt5.QtWidgets import (
    QDialogButtonBox, QTreeWidgetItem, QListWidgetItem, QDialog, QAction,
    QMessageBox, QFileDialog, QFontDialog
)

from nw.gui import (
    GuiProjectSettings, GuiItemEditor, GuiAbout, GuiBuildNovel,
    GuiDocMerge, GuiDocSplit, GuiWritingStats, GuiProjectWizard,
    GuiProjectLoad, GuiPreferences
)
from nw.gui.custom import QuotesDialog
from nw.constants import nwItemLayout, nwItemClass, nwFiles

keyDelay = 2
typeDelay = 1
stepDelay = 20

@pytest.mark.gui
def testProjectSettings(qtbot, monkeypatch, yesToAll, nwFuncTemp, nwTempGUI, nwRef, nwTemp):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwTemp, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    # Check that we cannot open when there is no project
    nwGUI.mainMenu.aProjectSettings.activate(QAction.Trigger)
    assert getGuiItem("GuiProjectSettings") is None

    # Create new project
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": nwFuncTemp})
    nwGUI.mainConf.backupPath = nwFuncTemp

    # Get the dialog object
    monkeypatch.setattr(GuiProjectSettings, "exec_", lambda *args: None)
    monkeypatch.setattr(GuiProjectSettings, "result", lambda *args: QDialog.Accepted)
    nwGUI.mainMenu.aProjectSettings.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiProjectSettings") is not None, timeout=1000)

    projEdit = getGuiItem("GuiProjectSettings")
    assert isinstance(projEdit, GuiProjectSettings)
    projEdit.show()
    qtbot.addWidget(projEdit)

    # Main settings
    qtbot.wait(stepDelay)
    projEdit.tabMain.editName.setText("")
    for c in "Project Name":
        qtbot.keyClick(projEdit.tabMain.editName, c, delay=typeDelay)
    for c in "Project Title":
        qtbot.keyClick(projEdit.tabMain.editTitle, c, delay=typeDelay)
    for c in "Jane Doe":
        qtbot.keyClick(projEdit.tabMain.editAuthors, c, delay=typeDelay)
    qtbot.keyClick(projEdit.tabMain.editAuthors, Qt.Key_Return, delay=keyDelay)
    for c in "John Doh":
        qtbot.keyClick(projEdit.tabMain.editAuthors, c, delay=typeDelay)

    # Test Status Tab
    qtbot.wait(stepDelay)
    projEdit._tabBox.setCurrentWidget(projEdit.tabStatus)
    projEdit.tabStatus.listBox.item(2).setSelected(True)
    qtbot.mouseClick(projEdit.tabStatus.delButton, Qt.LeftButton)
    qtbot.mouseClick(projEdit.tabStatus.newButton, Qt.LeftButton)
    projEdit.tabStatus.listBox.item(3).setSelected(True)
    for n in range(8):
        qtbot.keyClick(projEdit.tabStatus.editName, Qt.Key_Backspace, delay=typeDelay)
    for c in "Final":
        qtbot.keyClick(projEdit.tabStatus.editName, c, delay=typeDelay)
    qtbot.mouseClick(projEdit.tabStatus.saveButton, Qt.LeftButton)

    # Auto-Replace Tab
    qtbot.wait(stepDelay)
    projEdit._tabBox.setCurrentWidget(projEdit.tabReplace)

    qtbot.mouseClick(projEdit.tabReplace.addButton, Qt.LeftButton)
    projEdit.tabReplace.listBox.topLevelItem(0).setSelected(True)
    for c in "Th is ":
        qtbot.keyClick(projEdit.tabReplace.editKey, c, delay=typeDelay)
    for c in "With This Stuff ":
        qtbot.keyClick(projEdit.tabReplace.editValue, c, delay=typeDelay)
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
    nwGUI.mainMenu.aProjectSettings.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiProjectSettings") is not None, timeout=1000)

    projEdit = getGuiItem("GuiProjectSettings")
    assert isinstance(projEdit, GuiProjectSettings)

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
    projFile = os.path.join(nwFuncTemp, "nwProject.nwx")
    testFile = os.path.join(nwTempGUI, "2_nwProject.nwx")
    refFile  = os.path.join(nwRef, "gui", "2_nwProject.nwx")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [2, 8, 9, 10])

    # qtbot.stopForInteraction()
    nwGUI.closeMain()

@pytest.mark.gui
def testItemEditor(qtbot, yesToAll, monkeypatch, nwFuncTemp, nwTempGUI, nwRef, nwTemp):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwTemp, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    # Create new, save, open project
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": nwFuncTemp})
    assert nwGUI.openDocument("0e17daca5f3e1")
    assert nwGUI.treeView.setSelectedHandle("0e17daca5f3e1", doScroll=True)

    monkeypatch.setattr(GuiItemEditor, "exec_", lambda *args: None)
    nwGUI.mainMenu.aEditItem.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiItemEditor") is not None, timeout=1000)

    itemEdit = getGuiItem("GuiItemEditor")
    assert isinstance(itemEdit, GuiItemEditor)
    itemEdit.show()

    qtbot.addWidget(itemEdit)

    assert itemEdit.editName.text()          == "New Scene"
    assert itemEdit.editStatus.currentData() == "New"
    assert itemEdit.editLayout.currentData() == nwItemLayout.SCENE

    for c in "Just a Page":
        qtbot.keyClick(itemEdit.editName, c, delay=typeDelay)
    itemEdit.editStatus.setCurrentIndex(1)
    layoutIdx = itemEdit.editLayout.findData(nwItemLayout.PAGE)
    itemEdit.editLayout.setCurrentIndex(layoutIdx)

    itemEdit.editExport.setChecked(False)
    assert not itemEdit.editExport.isChecked()
    itemEdit._doSave()

    nwGUI.mainMenu.aEditItem.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiItemEditor") is not None, timeout=1000)

    itemEdit = getGuiItem("GuiItemEditor")
    assert isinstance(itemEdit, GuiItemEditor)
    itemEdit.show()

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
    projFile = os.path.join(nwFuncTemp, "nwProject.nwx")
    testFile = os.path.join(nwTempGUI, "3_nwProject.nwx")
    refFile  = os.path.join(nwRef, "gui", "3_nwProject.nwx")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [2, 6, 7, 8])

    # qtbot.stopForInteraction()
    nwGUI.closeMain()

@pytest.mark.gui
def testWritingStatsExport(qtbot, monkeypatch, yesToAll, nwFuncTemp, nwTemp):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwTemp, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    # Create new, save, close project
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": nwFuncTemp})
    qtbot.wait(200)
    assert nwGUI.saveProject()
    assert nwGUI.closeProject()
    qtbot.wait(stepDelay)

    sessFile = os.path.join(nwFuncTemp, "meta", nwFiles.SESS_STATS)
    with open(sessFile, mode="w+", encoding="utf-8") as outFile:
        outFile.write(
            "# Start Time         End Time                Novel     Notes\n"
            "2020-01-01 21:00:00  2020-01-01 21:00:05         6         0\n"
            "2020-01-03 21:00:00  2020-01-03 21:00:15       125         0\n"
            "2020-01-03 21:30:00  2020-01-03 21:30:15       125         5\n"
            "2020-01-06 21:00:00  2020-01-06 21:00:10       125         5\n"
        )

    # Open again, and check the stats
    assert nwGUI.openProject(nwFuncTemp)
    qtbot.wait(stepDelay)

    nwGUI.mainConf.lastPath = nwFuncTemp
    nwGUI.mainMenu.aWritingStats.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiWritingStats") is not None, timeout=1000)

    sessLog = getGuiItem("GuiWritingStats")
    assert isinstance(sessLog, GuiWritingStats)
    qtbot.wait(stepDelay)

    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args, **kwargs: ("", ""))
    assert not sessLog._saveData(sessLog.FMT_CSV)

    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda ss, tt, pp, options: (pp, ""))
    assert sessLog._saveData(sessLog.FMT_CSV)
    qtbot.wait(100)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(100)

    jsonStats = os.path.join(nwFuncTemp, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.load(inFile)

    qtbot.wait(stepDelay)

    assert len(jsonData) == 3
    assert jsonData[1]["length"] >= 14.0
    assert jsonData[1]["newWords"] == 119
    assert jsonData[1]["novelWords"] == 125
    assert jsonData[1]["noteWords"] == 0

    # No Novel Files
    qtbot.mouseClick(sessLog.incNovel, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = os.path.join(nwFuncTemp, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.loads(inFile.read())

    assert len(jsonData) == 1
    assert jsonData[0]["length"] >= 14.0
    assert jsonData[0]["newWords"] == 5
    assert jsonData[0]["novelWords"] == 125
    assert jsonData[0]["noteWords"] == 5

    # No Note Files
    qtbot.mouseClick(sessLog.incNovel, Qt.LeftButton)
    qtbot.mouseClick(sessLog.incNotes, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = os.path.join(nwFuncTemp, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.load(inFile)

    assert len(jsonData) == 2
    assert jsonData[1]["length"] >= 14.0
    assert jsonData[1]["newWords"] == 119
    assert jsonData[1]["novelWords"] == 125
    assert jsonData[1]["noteWords"] == 0

    # No Negative Entries
    qtbot.mouseClick(sessLog.incNotes, Qt.LeftButton)
    qtbot.mouseClick(sessLog.hideNegative, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = os.path.join(nwFuncTemp, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.load(inFile)

    assert len(jsonData) == 3

    # Un-hide Zero Entries
    qtbot.mouseClick(sessLog.hideNegative, Qt.LeftButton)
    qtbot.mouseClick(sessLog.hideZeros, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = os.path.join(nwFuncTemp, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.load(inFile)

    assert len(jsonData) == 4

    # Group by Day
    qtbot.mouseClick(sessLog.groupByDay, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = os.path.join(nwFuncTemp, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.load(inFile)

    # Check against both 1 and 2 as this can be 2 if test was started just before midnight.
    # A failed test should in any case produce a 4
    assert len(jsonData) == 3

    # qtbot.stopForInteraction()

    sessLog._doClose()
    assert nwGUI.closeProject()
    qtbot.wait(stepDelay)
    nwGUI.closeMain()

@pytest.mark.gui
def testAboutBox(qtbot, monkeypatch, nwFuncTemp, nwTemp):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwFuncTemp, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    # NW About
    monkeypatch.setattr(GuiAbout, "exec_", lambda *args: None)
    nwGUI.mainMenu.aAboutNW.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiAbout") is not None, timeout=1000)

    msgAbout = getGuiItem("GuiAbout")
    assert isinstance(msgAbout, GuiAbout)
    msgAbout.show()

    assert msgAbout.pageAbout.document().characterCount() > 100
    assert msgAbout.pageNotes.document().characterCount() > 100
    assert msgAbout.pageLicense.document().characterCount() > 100

    msgAbout.mainConf.assetPath = "whatever"

    msgAbout._fillNotesPage()
    assert msgAbout.pageNotes.toPlainText() == "Error loading release notes text ..."

    msgAbout._fillLicensePage()
    assert msgAbout.pageLicense.toPlainText() == "Error loading license text ..."

    msgAbout.showReleaseNotes()
    assert msgAbout.tabBox.currentWidget() == msgAbout.pageNotes

    # Qt About
    monkeypatch.setattr(QMessageBox, "aboutQt", lambda *args, **kwargs: None)
    nwGUI.mainMenu.aAboutQt.activate(QAction.Trigger)

    # qtbot.stopForInteraction()
    msgAbout._doClose()
    nwGUI.closeMain()

@pytest.mark.gui
def testBuildTool(qtbot, yesToAll, nwTempBuild, nwLipsum, nwRef, nwTemp):

    nwGUI = nw.main(["--testmode", "--config=%s" % nwLipsum, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    # Check that we cannot open when there is no project
    nwGUI.mainMenu.aBuildProject.activate(QAction.Trigger)
    assert getGuiItem("GuiBuildNovel") is None

    # Open a project
    assert nwGUI.openProject(nwLipsum)
    nwGUI.mainConf.lastPath = nwLipsum

    # Open the tool
    nwGUI.mainMenu.aBuildProject.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiBuildNovel") is not None, timeout=1000)

    nwBuild = getGuiItem("GuiBuildNovel")
    assert isinstance(nwBuild, GuiBuildNovel)

    # Default Settings
    qtbot.mouseClick(nwBuild.buildNovel, Qt.LeftButton)

    assert nwBuild._saveDocument(nwBuild.FMT_NWD)
    assert nwBuild._saveDocument(nwBuild.FMT_HTM)

    projFile = os.path.join(nwLipsum, "Lorem Ipsum.nwd")
    testFile = os.path.join(nwTempBuild, "1_LoremIpsum.nwd")
    refFile  = os.path.join(nwRef, "build", "1_LoremIpsum.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    projFile = os.path.join(nwLipsum, "Lorem Ipsum.htm")
    testFile = os.path.join(nwTempBuild, "1_LoremIpsum.htm")
    refFile  = os.path.join(nwRef, "build", "1_LoremIpsum.htm")
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

    projFile = os.path.join(nwLipsum, "Lorem Ipsum.nwd")
    testFile = os.path.join(nwTempBuild, "2_LoremIpsum.nwd")
    refFile  = os.path.join(nwRef, "build", "2_LoremIpsum.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    projFile = os.path.join(nwLipsum, "Lorem Ipsum.htm")
    testFile = os.path.join(nwTempBuild, "2_LoremIpsum.htm")
    refFile  = os.path.join(nwRef, "build", "2_LoremIpsum.htm")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    # Replace Tabs with Spaces
    qtbot.mouseClick(nwBuild.replaceTabs, Qt.LeftButton)
    qtbot.wait(stepDelay)

    qtbot.mouseClick(nwBuild.buildNovel, Qt.LeftButton)

    # Save files that can be compared
    assert nwBuild._saveDocument(nwBuild.FMT_NWD)
    projFile = os.path.join(nwLipsum, "Lorem Ipsum.nwd")
    testFile = os.path.join(nwTempBuild, "3_LoremIpsum.nwd")
    refFile  = os.path.join(nwRef, "build", "3_LoremIpsum.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    assert nwBuild._saveDocument(nwBuild.FMT_HTM)
    projFile = os.path.join(nwLipsum, "Lorem Ipsum.htm")
    testFile = os.path.join(nwTempBuild, "3_LoremIpsum.htm")
    refFile  = os.path.join(nwRef, "build", "3_LoremIpsum.htm")
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

    # Save files that can be compared
    assert nwBuild._saveDocument(nwBuild.FMT_NWD)
    projFile = os.path.join(nwLipsum, "Lorem Ipsum.nwd")
    testFile = os.path.join(nwTempBuild, "4_LoremIpsum.nwd")
    refFile  = os.path.join(nwRef, "build", "4_LoremIpsum.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    assert nwBuild._saveDocument(nwBuild.FMT_HTM)
    projFile = os.path.join(nwLipsum, "Lorem Ipsum.htm")
    testFile = os.path.join(nwTempBuild, "4_LoremIpsum.htm")
    refFile  = os.path.join(nwRef, "build", "4_LoremIpsum.htm")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    # Check the JSON files too at this stage
    assert nwBuild._saveDocument(nwBuild.FMT_JSON_H)
    projFile = os.path.join(nwLipsum, "Lorem Ipsum.json")
    testFile = os.path.join(nwTempBuild, "4H_LoremIpsum.json")
    refFile  = os.path.join(nwRef, "build", "4H_LoremIpsum.json")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [8])

    assert nwBuild._saveDocument(nwBuild.FMT_JSON_M)
    projFile = os.path.join(nwLipsum, "Lorem Ipsum.json")
    testFile = os.path.join(nwTempBuild, "4M_LoremIpsum.json")
    refFile  = os.path.join(nwRef, "build", "4M_LoremIpsum.json")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [8])

    # Save other file types handled by Qt
    # We assume the export itself by the Qt library works, so we just
    # check that novelWriter successfully writes the files.
    assert nwBuild._saveDocument(nwBuild.FMT_ODT)
    assert os.path.isfile(os.path.join(nwLipsum, "Lorem Ipsum.odt"))

    if not nwGUI.mainConf.osDarwin:
        assert nwBuild._saveDocument(nwBuild.FMT_PDF)
        assert os.path.isfile(os.path.join(nwLipsum, "Lorem Ipsum.pdf"))

    assert nwBuild._saveDocument(nwBuild.FMT_MD)
    assert os.path.isfile(os.path.join(nwLipsum, "Lorem Ipsum.md"))

    assert nwBuild._saveDocument(nwBuild.FMT_TXT)
    assert os.path.isfile(os.path.join(nwLipsum, "Lorem Ipsum.txt"))

    # Close the build tool
    htmlText  = nwBuild.htmlText
    htmlStyle = nwBuild.htmlStyle
    nwdText   = nwBuild.nwdText
    buildTime = nwBuild.buildTime
    nwBuild._doClose()

    # Re-open build dialog from cahce
    nwGUI.mainMenu.aBuildProject.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiBuildNovel") is not None, timeout=1000)

    nwBuild = getGuiItem("GuiBuildNovel")
    assert isinstance(nwBuild, GuiBuildNovel)

    assert nwBuild.viewCachedDoc()
    assert nwBuild.htmlText  == htmlText
    assert nwBuild.htmlStyle == htmlStyle
    assert nwBuild.nwdText   == nwdText
    assert nwBuild.buildTime == buildTime

    nwBuild._doClose()

    # qtbot.stopForInteraction()
    nwGUI.closeMain()

@pytest.mark.gui
def testMergeSplitTools(qtbot, monkeypatch, yesToAll, nwTempGUI, nwLipsum, nwRef, nwTemp):

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

    monkeypatch.setattr(GuiDocMerge, "exec_", lambda *args: None)
    nwGUI.mainMenu.aMergeDocs.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiDocMerge") is not None, timeout=1000)

    nwMerge = getGuiItem("GuiDocMerge")
    assert isinstance(nwMerge, GuiDocMerge)
    nwMerge.show()
    qtbot.wait(stepDelay)

    nwMerge._doMerge()
    qtbot.wait(stepDelay)

    assert nwGUI.theProject.projTree["73475cb40a568"] is not None

    projFile = os.path.join(nwLipsum, "content", "73475cb40a568.nwd")
    testFile = os.path.join(nwTempGUI, "4_73475cb40a568.nwd")
    refFile  = os.path.join(nwRef, "gui", "4_73475cb40a568.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    # Split By Chapter
    assert nwGUI.treeView.setSelectedHandle("73475cb40a568")
    qtbot.wait(stepDelay)

    monkeypatch.setattr(GuiDocSplit, "exec_", lambda *args: None)
    nwGUI.mainMenu.aSplitDoc.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiDocSplit") is not None, timeout=1000)

    nwSplit = getGuiItem("GuiDocSplit")
    assert isinstance(nwSplit, GuiDocSplit)
    nwSplit.show()
    qtbot.wait(stepDelay)

    nwSplit.splitLevel.setCurrentIndex(1)
    qtbot.wait(stepDelay)

    nwSplit._doSplit()
    assert nwGUI.theProject.projTree["71ee45a3c0db9"] is not None

    # This should give us back the file as it was before
    projFile = os.path.join(nwLipsum, "content", "71ee45a3c0db9.nwd")
    testFile = os.path.join(nwTempGUI, "4_71ee45a3c0db9.nwd")
    refFile  = os.path.join(nwRef, "gui", "4_73475cb40a568.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [1, 2, 3])

    # Split By Scene
    assert nwGUI.treeView.setSelectedHandle("73475cb40a568")
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aSplitDoc.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiDocSplit") is not None, timeout=1000)

    nwSplit = getGuiItem("GuiDocSplit")
    assert isinstance(nwSplit, GuiDocSplit)
    qtbot.wait(stepDelay)
    nwSplit.splitLevel.setCurrentIndex(2)
    qtbot.wait(stepDelay)

    nwSplit._doSplit()

    assert nwGUI.theProject.projTree["25fc0e7096fc6"] is not None
    assert nwGUI.theProject.projTree["31489056e0916"] is not None
    assert nwGUI.theProject.projTree["98010bd9270f9"] is not None

    projFile = os.path.join(nwLipsum, "content", "25fc0e7096fc6.nwd")
    testFile = os.path.join(nwTempGUI, "5_25fc0e7096fc6.nwd")
    refFile  = os.path.join(nwRef, "gui", "5_25fc0e7096fc6.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    projFile = os.path.join(nwLipsum, "content", "31489056e0916.nwd")
    testFile = os.path.join(nwTempGUI, "5_31489056e0916.nwd")
    refFile  = os.path.join(nwRef, "gui", "5_31489056e0916.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    projFile = os.path.join(nwLipsum, "content", "98010bd9270f9.nwd")
    testFile = os.path.join(nwTempGUI, "5_98010bd9270f9.nwd")
    refFile  = os.path.join(nwRef, "gui", "5_98010bd9270f9.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    # Split By Section
    assert nwGUI.treeView.setSelectedHandle("73475cb40a568")
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aSplitDoc.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiDocSplit") is not None, timeout=1000)

    nwSplit = getGuiItem("GuiDocSplit")
    assert isinstance(nwSplit, GuiDocSplit)
    qtbot.wait(stepDelay)
    nwSplit.splitLevel.setCurrentIndex(3)
    qtbot.wait(stepDelay)

    nwSplit._doSplit()

    assert nwGUI.theProject.projTree["1a6562590ef19"] is not None
    assert nwGUI.theProject.projTree["031b4af5197ec"] is not None
    assert nwGUI.theProject.projTree["41cfc0d1f2d12"] is not None
    assert nwGUI.theProject.projTree["2858dcd1057d3"] is not None
    assert nwGUI.theProject.projTree["2fca346db6561"] is not None

    projFile = os.path.join(nwLipsum, "content", "1a6562590ef19.nwd")
    testFile = os.path.join(nwTempGUI, "5_25fc0e7096fc6.nwd")
    refFile  = os.path.join(nwRef, "gui", "5_25fc0e7096fc6.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [1, 2, 3])

    projFile = os.path.join(nwLipsum, "content", "031b4af5197ec.nwd")
    testFile = os.path.join(nwTempGUI, "5_031b4af5197ec.nwd")
    refFile  = os.path.join(nwRef, "gui", "5_031b4af5197ec.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    projFile = os.path.join(nwLipsum, "content", "41cfc0d1f2d12.nwd")
    testFile = os.path.join(nwTempGUI, "5_41cfc0d1f2d12.nwd")
    refFile  = os.path.join(nwRef, "gui", "5_41cfc0d1f2d12.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    projFile = os.path.join(nwLipsum, "content", "2858dcd1057d3.nwd")
    testFile = os.path.join(nwTempGUI, "5_2858dcd1057d3.nwd")
    refFile  = os.path.join(nwRef, "gui", "5_2858dcd1057d3.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    projFile = os.path.join(nwLipsum, "content", "2fca346db6561.nwd")
    testFile = os.path.join(nwTempGUI, "5_2fca346db6561.nwd")
    refFile  = os.path.join(nwRef, "gui", "5_2fca346db6561.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    # qtbot.stopForInteraction()
    nwGUI.closeMain()

@pytest.mark.gui
def testNewProjectWizard(qtbot, monkeypatch, yesToAll, nwMinimal, nwTemp):

    if sys.platform.startswith("darwin"):
        # Disable for macOS because the test segfaults on QWizard.show()
        return

    from PyQt5.QtWidgets import QWizard
    from nw.gui.projwizard import (
        ProjWizardIntroPage, ProjWizardFolderPage, ProjWizardPopulatePage,
        ProjWizardCustomPage, ProjWizardFinalPage
    )

    nwGUI = nw.main(["--testmode", "--config=%s" % nwTemp, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    ##
    #  Test New Project Function
    ##

    # New with a project open should cause an error
    assert nwGUI.openProject(nwMinimal)
    assert not nwGUI.newProject()

    # Close project, but call with invalid path
    assert nwGUI.closeProject()
    monkeypatch.setattr(nwGUI, "showNewProjectDialog", lambda *args: None)
    assert not nwGUI.newProject()

    # Now, with an empty dictionary
    monkeypatch.setattr(nwGUI, "showNewProjectDialog", lambda *args: {})
    assert not nwGUI.newProject()

    # Now, with a non-empty folder
    monkeypatch.setattr(nwGUI, "showNewProjectDialog", lambda *args: {"projPath": nwMinimal})
    assert not nwGUI.newProject()

    monkeypatch.undo()

    ##
    #  Test the Wizard
    ##

    monkeypatch.setattr(GuiProjectWizard, "exec_", lambda *args: None)
    nwGUI.mainConf.lastPath = " "

    nwGUI.closeProject()
    nwGUI.showNewProjectDialog()
    qtbot.waitUntil(lambda: getGuiItem("GuiProjectWizard") is not None, timeout=1000)

    nwWiz = getGuiItem("GuiProjectWizard")
    assert isinstance(nwWiz, GuiProjectWizard)
    nwWiz.show()
    qtbot.wait(stepDelay)

    for wStep in range(4):
        # This does not actually create the project, it just generates the
        # dictionary that defines it.

        # Intro Page
        introPage = nwWiz.currentPage()
        assert isinstance(introPage, ProjWizardIntroPage)
        assert not nwWiz.button(QWizard.NextButton).isEnabled()

        qtbot.wait(stepDelay)
        for c in ("Test Minimal %d" % wStep):
            qtbot.keyClick(introPage.projName, c, delay=typeDelay)

        qtbot.wait(stepDelay)
        for c in "Minimal Novel":
            qtbot.keyClick(introPage.projTitle, c, delay=typeDelay)

        qtbot.wait(stepDelay)
        for c in "Jane Doe":
            qtbot.keyClick(introPage.projAuthors, c, delay=typeDelay)

        # Setting projName should activate the button
        assert nwWiz.button(QWizard.NextButton).isEnabled()

        qtbot.wait(stepDelay)
        qtbot.mouseClick(nwWiz.button(QWizard.NextButton), Qt.LeftButton)

        # Folder Page
        storagePage = nwWiz.currentPage()
        assert isinstance(storagePage, ProjWizardFolderPage)
        assert not nwWiz.button(QWizard.NextButton).isEnabled()

        if wStep == 0:
            # Check invalid path first, the first time we reach here
            monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **kw: "")
            qtbot.wait(stepDelay)
            qtbot.mouseClick(storagePage.browseButton, Qt.LeftButton, delay=100)
            assert storagePage.projPath.text() == ""

            # Then, we always return nwMinimal as path
            monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **kw: nwMinimal)

        qtbot.wait(stepDelay)
        qtbot.mouseClick(storagePage.browseButton, Qt.LeftButton, delay=100)
        projPath = os.path.join(nwMinimal, "Test Minimal %d" % wStep)
        assert storagePage.projPath.text() == projPath

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
            popPage.popCustom.setChecked(True)
        elif wStep == 3:
            popPage.popSample.setChecked(True)

        qtbot.wait(stepDelay)
        qtbot.mouseClick(nwWiz.button(QWizard.NextButton), Qt.LeftButton)

        # Custom Page
        if wStep == 1 or wStep == 2:
            customPage = nwWiz.currentPage()
            assert isinstance(customPage, ProjWizardCustomPage)
            assert nwWiz.button(QWizard.NextButton).isEnabled()

            customPage.addPlot.setChecked(True)
            customPage.addChar.setChecked(True)
            customPage.addWorld.setChecked(True)
            customPage.addTime.setChecked(True)
            customPage.addObject.setChecked(True)
            customPage.addEntity.setChecked(True)

            if wStep == 2:
                customPage.numChapters.setValue(0)
                customPage.numScenes.setValue(10)
                customPage.chFolders.setChecked(False)

            qtbot.wait(stepDelay)
            qtbot.mouseClick(nwWiz.button(QWizard.NextButton), Qt.LeftButton)

        # Final Page
        finalPage = nwWiz.currentPage()
        assert isinstance(finalPage, ProjWizardFinalPage)
        assert nwWiz.button(QWizard.FinishButton).isEnabled() # But we don't click it

        # Check Data
        projData = nwGUI._assembleProjectWizardData(nwWiz)
        assert projData["projName"]    == "Test Minimal %d" % wStep
        assert projData["projTitle"]   == "Minimal Novel"
        assert projData["projAuthors"] == "Jane Doe"
        assert projData["projPath"]    == projPath
        assert projData["popMinimal"]  == (wStep == 0)
        assert projData["popCustom"]   == (wStep == 1 or wStep == 2)
        assert projData["popSample"]   == (wStep == 3)
        if wStep == 1 or wStep == 2:
            assert projData["addRoots"] == [
                nwItemClass.PLOT,
                nwItemClass.CHARACTER,
                nwItemClass.WORLD,
                nwItemClass.TIMELINE,
                nwItemClass.OBJECT,
                nwItemClass.ENTITY,
            ]
            if wStep == 1:
                assert projData["numChapters"] == 5
                assert projData["numScenes"] == 5
                assert projData["chFolders"]
            else:
                assert projData["numChapters"] == 0
                assert projData["numScenes"] == 10
                assert not projData["chFolders"]
        else:
            assert projData["addRoots"] == []
            assert projData["numChapters"] == 0
            assert projData["numScenes"] == 0
            assert not projData["chFolders"]

        # Restart the wizard for next iteration
        nwWiz.restart()

    nwWiz.reject()
    nwWiz.close()

    # qtbot.stopForInteraction()
    nwGUI.closeMain()
    nwGUI.close()

@pytest.mark.gui
def testLoadProject(qtbot, monkeypatch, yesToAll, nwMinimal, nwTemp):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwMinimal, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    assert nwGUI.openProject(nwMinimal)
    assert nwGUI.closeProject()

    qtbot.wait(stepDelay)
    monkeypatch.setattr(GuiProjectLoad, "exec_", lambda *args: None)
    monkeypatch.setattr(GuiProjectLoad, "result", lambda *args: QDialog.Accepted)
    nwGUI.mainMenu.aOpenProject.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiProjectLoad") is not None, timeout=1000)

    nwLoad = getGuiItem("GuiProjectLoad")
    assert isinstance(nwLoad, GuiProjectLoad)
    nwLoad.show()

    qtbot.wait(stepDelay)
    recentCount = nwLoad.listBox.topLevelItemCount()
    assert recentCount > 0

    qtbot.wait(stepDelay)
    selItem = nwLoad.listBox.topLevelItem(0)
    selPath = selItem.data(nwLoad.C_NAME, Qt.UserRole)
    assert isinstance(selItem, QTreeWidgetItem)

    qtbot.wait(stepDelay)
    nwLoad.selPath.setText("")
    nwLoad.listBox.setCurrentItem(selItem)
    nwLoad._doSelectRecent()
    assert nwLoad.selPath.text() == selPath

    qtbot.wait(stepDelay)
    qtbot.mouseClick(nwLoad.buttonBox.button(QDialogButtonBox.Open), Qt.LeftButton)
    assert nwLoad.openPath == selPath
    assert nwLoad.openState == nwLoad.OPEN_STATE

    # Just create a new project load from scratch for the rest of the test
    del nwLoad

    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aOpenProject.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiProjectLoad") is not None, timeout=1000)

    qtbot.wait(stepDelay)
    nwLoad = getGuiItem("GuiProjectLoad")
    assert isinstance(nwLoad, GuiProjectLoad)
    nwLoad.show()

    qtbot.wait(stepDelay)
    qtbot.mouseClick(nwLoad.buttonBox.button(QDialogButtonBox.Cancel), Qt.LeftButton)
    assert nwLoad.openPath is None
    assert nwLoad.openState == nwLoad.NONE_STATE

    qtbot.wait(stepDelay)
    nwLoad.show()
    qtbot.mouseClick(nwLoad.newButton, Qt.LeftButton)
    assert nwLoad.openPath is None
    assert nwLoad.openState == nwLoad.NEW_STATE

    qtbot.wait(stepDelay)
    nwLoad.show()
    nwLoad._keyPressDelete()
    assert nwLoad.listBox.topLevelItemCount() == recentCount - 1

    getFile = os.path.join(nwMinimal, "nwProject.nwx")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args, **kwargs: (getFile, None))
    qtbot.mouseClick(nwLoad.browseButton, Qt.LeftButton)
    assert nwLoad.openPath == nwMinimal
    assert nwLoad.openState == nwLoad.OPEN_STATE
    # qtbot.stopForInteraction()

    nwLoad.close()
    nwGUI.closeMain()
    nwGUI.close()

@pytest.mark.gui
def testPreferences(qtbot, monkeypatch, yesToAll, nwMinimal, nwTemp, nwRef, tmpConf):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwMinimal, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    assert nwGUI.openProject(nwMinimal)

    monkeypatch.setattr(GuiPreferences, "exec_", lambda *args: None)
    monkeypatch.setattr(GuiPreferences, "result", lambda *args: QDialog.Accepted)
    nwGUI.mainMenu.aPreferences.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiPreferences") is not None, timeout=1000)

    nwPrefs = getGuiItem("GuiPreferences")
    assert isinstance(nwPrefs, GuiPreferences)
    nwPrefs.show()

    # Override Config
    tmpConf.confPath = nwMinimal
    tmpConf.showGUI = False
    nwGUI.mainConf = tmpConf
    nwPrefs.mainConf = tmpConf
    nwPrefs.tabGeneral.mainConf = tmpConf
    nwPrefs.tabProjects.mainConf = tmpConf
    nwPrefs.tabLayout.mainConf = tmpConf
    nwPrefs.tabEditing.mainConf = tmpConf
    nwPrefs.tabAutoRep.mainConf = tmpConf

    # General Settings
    qtbot.wait(keyDelay)
    tabGeneral = nwPrefs.tabGeneral
    nwPrefs._tabBox.setCurrentWidget(tabGeneral)

    qtbot.wait(keyDelay)
    assert not tabGeneral.preferDarkIcons.isChecked()
    qtbot.mouseClick(tabGeneral.preferDarkIcons, Qt.LeftButton)
    assert tabGeneral.preferDarkIcons.isChecked()

    qtbot.wait(keyDelay)
    assert tabGeneral.showFullPath.isChecked()
    qtbot.mouseClick(tabGeneral.showFullPath, Qt.LeftButton)
    assert not tabGeneral.showFullPath.isChecked()

    qtbot.wait(keyDelay)
    assert not tabGeneral.hideVScroll.isChecked()
    qtbot.mouseClick(tabGeneral.hideVScroll, Qt.LeftButton)
    assert tabGeneral.hideVScroll.isChecked()

    qtbot.wait(keyDelay)
    assert not tabGeneral.hideHScroll.isChecked()
    qtbot.mouseClick(tabGeneral.hideHScroll, Qt.LeftButton)
    assert tabGeneral.hideHScroll.isChecked()

    # Check font button
    monkeypatch.setattr(QFontDialog, "getFont", lambda font, obj: (font, True))
    qtbot.mouseClick(tabGeneral.fontButton, Qt.LeftButton)

    qtbot.wait(keyDelay)
    tabGeneral.guiFontSize.setValue(12)

    # Projects Settings
    qtbot.wait(keyDelay)
    tabProjects = nwPrefs.tabProjects
    nwPrefs._tabBox.setCurrentWidget(tabProjects)
    tabProjects.backupPath = "no/where"

    qtbot.wait(keyDelay)
    assert not tabProjects.backupOnClose.isChecked()
    qtbot.mouseClick(tabProjects.backupOnClose, Qt.LeftButton)
    assert tabProjects.backupOnClose.isChecked()

    # Check Browse button
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *args, **kwargs: "")
    assert not tabProjects._backupFolder()
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *args, **kwargs: "some/dir")
    qtbot.mouseClick(tabProjects.backupGetPath, Qt.LeftButton)

    qtbot.wait(keyDelay)
    tabProjects.autoSaveDoc.setValue(20)
    tabProjects.autoSaveProj.setValue(40)

    # Text Layout Settings
    qtbot.wait(keyDelay)
    tabLayout = nwPrefs.tabLayout
    nwPrefs._tabBox.setCurrentWidget(tabLayout)

    qtbot.wait(keyDelay)
    qtbot.mouseClick(tabLayout.fontButton, Qt.LeftButton)

    qtbot.wait(keyDelay)
    tabLayout.textStyleSize.setValue(13)
    tabLayout.textFlowMax.setValue(700)
    tabLayout.focusDocWidth.setValue(900)
    tabLayout.textMargin.setValue(45)
    tabLayout.tabWidth.setValue(45)

    qtbot.wait(keyDelay)
    assert not tabLayout.textFlowFixed.isChecked()
    qtbot.mouseClick(tabLayout.textFlowFixed, Qt.LeftButton)
    assert tabLayout.textFlowFixed.isChecked()

    qtbot.wait(keyDelay)
    assert not tabLayout.hideFocusFooter.isChecked()
    qtbot.mouseClick(tabLayout.hideFocusFooter, Qt.LeftButton)
    assert tabLayout.hideFocusFooter.isChecked()

    qtbot.wait(keyDelay)
    assert tabLayout.textJustify.isChecked()
    qtbot.mouseClick(tabLayout.textJustify, Qt.LeftButton)
    assert not tabLayout.textJustify.isChecked()

    qtbot.wait(keyDelay)
    assert tabLayout.scrollPastEnd.isChecked()
    qtbot.mouseClick(tabLayout.scrollPastEnd, Qt.LeftButton)
    assert not tabLayout.scrollPastEnd.isChecked()

    qtbot.wait(keyDelay)
    assert not tabLayout.autoScroll.isChecked()
    qtbot.mouseClick(tabLayout.autoScroll, Qt.LeftButton)
    assert tabLayout.autoScroll.isChecked()

    # Editor Settings
    qtbot.wait(keyDelay)
    tabEditing = nwPrefs.tabEditing
    nwPrefs._tabBox.setCurrentWidget(tabEditing)

    qtbot.wait(keyDelay)
    assert tabEditing.highlightQuotes.isChecked()
    qtbot.mouseClick(tabEditing.highlightQuotes, Qt.LeftButton)
    assert not tabEditing.highlightQuotes.isChecked()

    qtbot.wait(keyDelay)
    assert tabEditing.highlightEmph.isChecked()
    qtbot.mouseClick(tabEditing.highlightEmph, Qt.LeftButton)
    assert not tabEditing.highlightEmph.isChecked()

    qtbot.wait(keyDelay)
    assert not tabEditing.showTabsNSpaces.isChecked()
    qtbot.mouseClick(tabEditing.showTabsNSpaces, Qt.LeftButton)
    assert tabEditing.showTabsNSpaces.isChecked()

    qtbot.wait(keyDelay)
    assert not tabEditing.showLineEndings.isChecked()
    qtbot.mouseClick(tabEditing.showLineEndings, Qt.LeftButton)
    assert tabEditing.showLineEndings.isChecked()

    qtbot.wait(keyDelay)
    tabEditing.bigDocLimit.setValue(500)

    # Auto-Replace Settings
    qtbot.wait(keyDelay)
    tabAutoRep = nwPrefs.tabAutoRep
    nwPrefs._tabBox.setCurrentWidget(tabAutoRep)

    qtbot.wait(keyDelay)
    assert tabAutoRep.autoSelect.isChecked()
    qtbot.mouseClick(tabAutoRep.autoSelect, Qt.LeftButton)
    assert not tabAutoRep.autoSelect.isChecked()

    qtbot.wait(keyDelay)
    assert tabAutoRep.autoReplaceMain.isChecked()
    qtbot.mouseClick(tabAutoRep.autoReplaceMain, Qt.LeftButton)
    assert not tabAutoRep.autoReplaceMain.isChecked()

    qtbot.wait(keyDelay)
    assert not tabAutoRep.autoReplaceSQ.isEnabled()
    assert not tabAutoRep.autoReplaceDQ.isEnabled()
    assert not tabAutoRep.autoReplaceDash.isEnabled()
    assert not tabAutoRep.autoReplaceDots.isEnabled()

    monkeypatch.setattr(QuotesDialog, "selectedQuote", "'")
    monkeypatch.setattr(QuotesDialog, "exec_", lambda *args: QDialog.Accepted)
    qtbot.mouseClick(tabAutoRep.btnDoubleStyleC, Qt.LeftButton)

    # Save and Check Config
    qtbot.mouseClick(nwPrefs.buttonBox.button(QDialogButtonBox.Ok), Qt.LeftButton)

    assert tmpConf.confChanged
    tmpConf.lastPath = ""

    assert nwGUI.mainConf.saveConfig()

    # qtbot.stopForInteraction()
    nwGUI.closeMain()

    refConf = os.path.join(nwRef, "novelwriter_prefs.conf")
    projConf = os.path.join(nwGUI.mainConf.confPath, "novelwriter.conf")
    testConf = os.path.join(nwTemp, "novelwriter_prefs.conf")
    copyfile(projConf, testConf)
    ignoreLines = [
        2,                          # Timestamp
        9,                          # Release Notes
        12, 13, 14, 15, 16, 17, 18, # Window sizes
        7, 28,                      # Fonts (depends on system default)
    ]
    assert cmpFiles(testConf, refConf, ignoreLines)

@pytest.mark.gui
def testQuotesDialog(qtbot, yesToAll, nwMinimal, nwTemp):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwMinimal, "--data=%s" % nwTemp, nwMinimal])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    nwQuot = QuotesDialog(nwGUI)
    nwQuot.show()

    lastItem = ""
    for i in range(nwQuot.listBox.count()):
        anItem = nwQuot.listBox.item(i)
        assert isinstance(anItem, QListWidgetItem)
        nwQuot.listBox.clearSelection()
        nwQuot.listBox.setCurrentItem(anItem, QItemSelectionModel.Select)
        lastItem = anItem.text()[2]
        assert nwQuot.previewLabel.text() == lastItem

    nwQuot._doAccept()
    assert nwQuot.result() == QDialog.Accepted
    assert nwQuot.selectedQuote == lastItem

    # qtbot.stopForInteraction()
    nwQuot._doReject()
    nwQuot.close()
    nwGUI.closeMain()
    nwGUI.close()

@pytest.mark.gui
def testDialogsOpenClose(qtbot, monkeypatch, yesToAll, nwMinimal, nwTemp):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwMinimal, "--data=%s" % nwTemp, nwMinimal])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *args, **kwargs: nwTemp)
    assert nwGUI.selectProjectPath() == nwTemp

    # qtbot.stopForInteraction()
    nwGUI.closeMain()
    nwGUI.close()
