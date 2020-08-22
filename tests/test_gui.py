# -*- coding: utf-8 -*-
"""novelWriter Main GUI Class Tester
"""

import nw
import pytest
import json
from nwtools import cmpFiles

from os import path
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QAction, QDialogButtonBox, QTreeWidgetItem

from nw.gui import (
    GuiProjectSettings, GuiItemEditor, GuiAbout, GuiBuildNovel,
    GuiDocMerge, GuiDocSplit, GuiWritingStats, GuiProjectWizard,
    GuiProjectLoad
)
from nw.constants import (
    nwItemType, nwItemLayout, nwItemClass, nwDocAction, nwUnicode, nwOutline
)

keyDelay = 2
stepDelay = 20

@pytest.mark.gui
def testMainWindows(qtbot, nwTempGUI, nwRef, nwTemp):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwTempGUI, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    # Create new, save, close project
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": nwTempGUI}, True)
    assert nwGUI.saveProject()
    assert nwGUI.closeProject()

    assert len(nwGUI.theProject.projTree) == 0
    assert len(nwGUI.theProject.projTree._treeOrder) == 0
    assert len(nwGUI.theProject.projTree._treeRoots) == 0
    assert nwGUI.theProject.projTree.trashRoot() is None
    assert nwGUI.theProject.projPath is None
    assert nwGUI.theProject.projMeta is None
    assert nwGUI.theProject.projFile == "nwProject.nwx"
    assert nwGUI.theProject.projName == ""
    assert nwGUI.theProject.bookTitle == ""
    assert len(nwGUI.theProject.bookAuthors) == 0
    assert not nwGUI.theProject.spellCheck

    # Check the files
    projFile = path.join(nwTempGUI, "nwProject.nwx")
    assert cmpFiles(projFile, path.join(nwRef, "gui", "0_nwProject.nwx"), [2, 6, 7, 8])
    qtbot.wait(stepDelay)

    # qtbot.stopForInteraction()

    # Re-open project
    assert nwGUI.openProject(nwTempGUI)
    qtbot.wait(stepDelay)

    # Check that we loaded the data
    assert len(nwGUI.theProject.projTree) == 8
    assert len(nwGUI.theProject.projTree._treeOrder) == 8
    assert len(nwGUI.theProject.projTree._treeRoots) == 4
    assert nwGUI.theProject.projTree.trashRoot() is None
    assert nwGUI.theProject.projPath == nwTempGUI
    assert nwGUI.theProject.projMeta == path.join(nwTempGUI, "meta")
    assert nwGUI.theProject.projFile == "nwProject.nwx"
    assert nwGUI.theProject.projName == "New Project"
    assert nwGUI.theProject.bookTitle == ""
    assert len(nwGUI.theProject.bookAuthors) == 0
    assert not nwGUI.theProject.spellCheck

    # Check that tree items have been created
    assert nwGUI.treeView._getTreeItem("73475cb40a568") is not None
    assert nwGUI.treeView._getTreeItem("25fc0e7096fc6") is not None
    assert nwGUI.treeView._getTreeItem("31489056e0916") is not None
    assert nwGUI.treeView._getTreeItem("98010bd9270f9") is not None
    assert nwGUI.treeView._getTreeItem("0e17daca5f3e1") is not None
    assert nwGUI.treeView._getTreeItem("44cb730c42048") is not None
    assert nwGUI.treeView._getTreeItem("71ee45a3c0db9") is not None
    assert nwGUI.treeView._getTreeItem("811786ad1ae74") is not None

    nwGUI.mainMenu.aSpellCheck.setChecked(True)
    assert nwGUI.mainMenu._toggleSpellCheck()

    # Add a Character File
    nwGUI.setFocus(1)
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem("71ee45a3c0db9").setSelected(True)
    nwGUI.treeView.newTreeItem(nwItemType.FILE, None)
    assert nwGUI.openSelectedItem()

    # Type something into the document
    nwGUI.setFocus(2)
    qtbot.keyClick(nwGUI.docEditor, "a", modifier=Qt.ControlModifier, delay=keyDelay)
    for c in "# Jane Doe":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "@tag: Jane":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "This is a file about Jane.":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    # Add a Plot File
    nwGUI.setFocus(1)
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem("44cb730c42048").setSelected(True)
    nwGUI.treeView.newTreeItem(nwItemType.FILE, None)
    assert nwGUI.openSelectedItem()

    # Type something into the document
    nwGUI.setFocus(2)
    qtbot.keyClick(nwGUI.docEditor, "a", modifier=Qt.ControlModifier, delay=keyDelay)
    for c in "# Main Plot":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "@tag: MainPlot":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "This is a file detailing the main plot.":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    # Add a World File
    nwGUI.setFocus(1)
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem("811786ad1ae74").setSelected(True)
    nwGUI.treeView.newTreeItem(nwItemType.FILE, None)
    assert nwGUI.openSelectedItem()

    # Add Some Text
    nwGUI.docEditor.replaceText("Hello World!")
    assert nwGUI.docEditor.getText() == "Hello World!"
    nwGUI.docEditor.replaceText("")

    # Type something into the document
    nwGUI.setFocus(2)
    qtbot.keyClick(nwGUI.docEditor, "a", modifier=Qt.ControlModifier, delay=keyDelay)
    for c in "# Main Location":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "@tag: Home":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "This is a file describing Jane's home.":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    # Select the 'New Scene' file
    nwGUI.setFocus(1)
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem("73475cb40a568").setExpanded(True)
    nwGUI.treeView._getTreeItem("31489056e0916").setExpanded(True)
    nwGUI.treeView._getTreeItem("0e17daca5f3e1").setSelected(True)
    assert nwGUI.openSelectedItem()

    # Type something into the document
    nwGUI.setFocus(2)
    qtbot.keyClick(nwGUI.docEditor, "a", modifier=Qt.ControlModifier, delay=keyDelay)
    for c in "# Novel":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "## Chapter":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "@pov: Jane":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "@plot: MainPlot":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "### Scene":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "% How about a comment?":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "@pov: Jane":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "@plot: MainPlot":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "@location: Home":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "#### Some Section":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "@char: Jane":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "This is a paragraph of dummy text.":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in (
        "This is another paragraph of much longer dummy text. "
        "It is in fact very very dumb dummy text! "
    ):
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    for c in "We can also try replacing \"quotes\", even single's quotes are replaced. ":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    for c in "We can hyphen-ate, make dashes -- and even longer dashes --- if we want. ":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    for c in "Ellipsis? Not a problem either ... ":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    qtbot.wait(stepDelay)
    nwGUI.docEditor.wCounter.run()
    qtbot.wait(stepDelay)

    # Save the document
    assert nwGUI.docEditor.docChanged
    assert nwGUI.saveDocument()
    assert not nwGUI.docEditor.docChanged
    qtbot.wait(stepDelay)
    nwGUI.rebuildIndex()
    qtbot.wait(stepDelay)

    # Open and view the edited document
    nwGUI.setFocus(3)
    assert nwGUI.openDocument("0e17daca5f3e1")
    assert nwGUI.viewDocument("0e17daca5f3e1")
    qtbot.wait(stepDelay)
    assert nwGUI.saveProject()
    assert nwGUI.closeDocViewer()
    qtbot.wait(stepDelay)

    # Check a Quick Create and Delete
    assert nwGUI.treeView.newTreeItem(nwItemType.FILE, None)
    newHandle = nwGUI.treeView.getSelectedHandle()
    assert nwGUI.theProject.projTree["2858dcd1057d3"] is not None
    assert nwGUI.treeView.deleteItem()
    assert nwGUI.treeView.setSelectedHandle(newHandle)
    assert nwGUI.treeView.deleteItem()
    assert nwGUI.theProject.projTree["2fca346db6561"] is not None # Trash
    assert nwGUI.saveProject()

    # Check the files
    refFile = path.join(nwTempGUI, "nwProject.nwx")
    assert cmpFiles(refFile, path.join(nwRef, "gui", "1_nwProject.nwx"), [2, 6, 7, 8])
    refFile = path.join(nwTempGUI, "content", "031b4af5197ec.nwd")
    assert cmpFiles(refFile, path.join(nwRef, "gui", "1_031b4af5197ec.nwd"))
    refFile = path.join(nwTempGUI, "content", "1a6562590ef19.nwd")
    assert cmpFiles(refFile, path.join(nwRef, "gui", "1_1a6562590ef19.nwd"))
    refFile = path.join(nwTempGUI, "content", "0e17daca5f3e1.nwd")
    assert cmpFiles(refFile, path.join(nwRef, "gui", "1_0e17daca5f3e1.nwd"))
    refFile = path.join(nwTempGUI, "content", "41cfc0d1f2d12.nwd")
    assert cmpFiles(refFile, path.join(nwRef, "gui", "1_41cfc0d1f2d12.nwd"))

    nwGUI.closeMain()
    # qtbot.stopForInteraction()

@pytest.mark.gui
def testProjectEditor(qtbot, nwTempGUI, nwRef, nwTemp):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwTempGUI, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    # Create new, save, open project
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": nwTempGUI}, True)
    nwGUI.mainConf.backupPath = nwTempGUI

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
    projFile = path.join(nwTempGUI, "nwProject.nwx")
    assert cmpFiles(projFile, path.join(nwRef, "gui", "2_nwProject.nwx"), [2, 8, 9, 10])

    # qtbot.stopForInteraction()
    nwGUI.closeMain()

@pytest.mark.gui
def testItemEditor(qtbot, nwTempGUI, nwRef, nwTemp):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwTempGUI, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    # Create new, save, open project
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": nwTempGUI}, True)
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
    projFile = path.join(nwTempGUI, "nwProject.nwx")
    assert cmpFiles(projFile, path.join(nwRef, "gui", "3_nwProject.nwx"), [2, 6, 7, 8])

    nwGUI.closeMain()
    # qtbot.stopForInteraction()

@pytest.mark.gui
def testWritingStatsExport(qtbot, nwTempGUI, nwRef, nwTemp):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwTempGUI, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    assert nwGUI.openProject(nwTempGUI)
    qtbot.wait(stepDelay)

    nwGUI.mainConf.lastPath = nwTempGUI
    sessLog = GuiWritingStats(nwGUI, nwGUI.theProject)
    sessLog.show()
    qtbot.wait(stepDelay)

    assert sessLog._saveData(sessLog.FMT_CSV)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = path.join(nwTempGUI, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.loads(inFile.read())

    assert len(jsonData) == 3
    assert jsonData[1]["length"] > 0
    assert jsonData[1]["newWords"] == 84
    assert jsonData[1]["novelWords"] == 63
    assert jsonData[1]["noteWords"] == 27

    # No Novel Files
    qtbot.mouseClick(sessLog.incNovel, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = path.join(nwTempGUI, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.loads(inFile.read())

    assert len(jsonData) == 2
    assert jsonData[0]["length"] > 0
    assert jsonData[0]["newWords"] == 27
    assert jsonData[0]["novelWords"] == 63
    assert jsonData[0]["noteWords"] == 27

    # No Note Files
    qtbot.mouseClick(sessLog.incNovel, Qt.LeftButton)
    qtbot.mouseClick(sessLog.incNotes, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = path.join(nwTempGUI, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.loads(inFile.read())

    assert len(jsonData) == 3
    assert jsonData[1]["length"] > 0
    assert jsonData[1]["newWords"] == 57
    assert jsonData[1]["novelWords"] == 63
    assert jsonData[1]["noteWords"] == 27

    # No Negative Entries
    qtbot.mouseClick(sessLog.incNotes, Qt.LeftButton)
    qtbot.mouseClick(sessLog.hideNegative, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = path.join(nwTempGUI, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.loads(inFile.read())

    assert len(jsonData) == 2

    # Un-hide Zero Entries
    qtbot.mouseClick(sessLog.hideNegative, Qt.LeftButton)
    qtbot.mouseClick(sessLog.hideZeros, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = path.join(nwTempGUI, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.loads(inFile.read())

    assert len(jsonData) == 4

    # Group by Day
    qtbot.mouseClick(sessLog.groupByDay, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = path.join(nwTempGUI, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.loads(inFile.read())

    # Check against both 1 and 2 as this can be 2 if test was started just before midnight.
    # A failed test should in any case produce a 4
    assert len(jsonData) in (1, 2)

    # qtbot.stopForInteraction()

    sessLog._doClose()
    nwGUI.closeMain()

@pytest.mark.gui
def testAboutBox(qtbot, nwTempGUI, nwRef, nwTemp):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwTempGUI, "--data=%s" % nwTemp])
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

    nwGUI = nw.main(["--testmode", "--config=%s" % nwTempBuild, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    assert nwGUI.openProject(nwLipsum)

    nwGUI.mainConf.lastPath = nwTempBuild

    nwBuild = GuiBuildNovel(nwGUI, nwGUI.theProject)

    # Default Settings
    qtbot.mouseClick(nwBuild.buildNovel, Qt.LeftButton)

    assert nwBuild._saveDocument(nwBuild.FMT_NWD)
    assert nwBuild._saveDocument(nwBuild.FMT_HTM)

    refFile = path.join(nwTempBuild, "Lorem Ipsum.nwd")
    assert cmpFiles(refFile, path.join(nwRef, "build", "1_LoremIpsum.nwd"), [])
    refFile = path.join(nwTempBuild, "Lorem Ipsum.htm")
    assert cmpFiles(refFile, path.join(nwRef, "build", "1_LoremIpsum.htm"), [])

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

    refFile = path.join(nwTempBuild, "Lorem Ipsum.nwd")
    assert cmpFiles(refFile, path.join(nwRef, "build", "2_LoremIpsum.nwd"), [])
    refFile = path.join(nwTempBuild, "Lorem Ipsum.htm")
    assert cmpFiles(refFile, path.join(nwRef, "build", "2_LoremIpsum.htm"), [])

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

    refFile = path.join(nwTempBuild, "Lorem Ipsum.nwd")
    assert cmpFiles(refFile, path.join(nwRef, "build", "3_LoremIpsum.nwd"), [])
    refFile = path.join(nwTempBuild, "Lorem Ipsum.htm")
    assert cmpFiles(refFile, path.join(nwRef, "build", "3_LoremIpsum.htm"), [])

    # qtbot.stopForInteraction()
    nwBuild._doClose()
    nwGUI.closeMain()

@pytest.mark.gui
def testMergeTool(qtbot, nwTempGUI, nwLipsum, nwRef, nwTemp):

    nwGUI = nw.main(["--testmode", "--config=%s" % nwTempGUI, "--data=%s" % nwTemp])
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

    refFile = path.join(nwLipsum, "content", "73475cb40a568.nwd")
    assert cmpFiles(refFile, path.join(nwRef, "gui", "4_73475cb40a568.nwd"))

    # qtbot.stopForInteraction()
    nwGUI.closeMain()

@pytest.mark.gui
def testSplitTool(qtbot, nwTempGUI, nwLipsum, nwRef, nwTemp):

    nwGUI = nw.main(["--testmode", "--config=%s" % nwTempGUI, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.openProject(nwLipsum)
    qtbot.wait(stepDelay)

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
    refFile = path.join(nwLipsum, "content", "71ee45a3c0db9.nwd")
    assert cmpFiles(refFile, path.join(nwRef, "gui", "4_73475cb40a568.nwd"), [1])

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

    refFile = path.join(nwLipsum, "content", "25fc0e7096fc6.nwd")
    assert cmpFiles(refFile, path.join(nwRef, "gui", "5_25fc0e7096fc6.nwd"))
    refFile = path.join(nwLipsum, "content", "31489056e0916.nwd")
    assert cmpFiles(refFile, path.join(nwRef, "gui", "5_31489056e0916.nwd"))
    refFile = path.join(nwLipsum, "content", "98010bd9270f9.nwd")
    assert cmpFiles(refFile, path.join(nwRef, "gui", "5_98010bd9270f9.nwd"))

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

    refFile = path.join(nwLipsum, "content", "1a6562590ef19.nwd")
    assert cmpFiles(refFile, path.join(nwRef, "gui", "5_25fc0e7096fc6.nwd"), [1])
    refFile = path.join(nwLipsum, "content", "031b4af5197ec.nwd")
    assert cmpFiles(refFile, path.join(nwRef, "gui", "5_031b4af5197ec.nwd"))
    refFile = path.join(nwLipsum, "content", "41cfc0d1f2d12.nwd")
    assert cmpFiles(refFile, path.join(nwRef, "gui", "5_41cfc0d1f2d12.nwd"))
    refFile = path.join(nwLipsum, "content", "2858dcd1057d3.nwd")
    assert cmpFiles(refFile, path.join(nwRef, "gui", "5_2858dcd1057d3.nwd"))
    refFile = path.join(nwLipsum, "content", "2fca346db6561.nwd")
    assert cmpFiles(refFile, path.join(nwRef, "gui", "5_2fca346db6561.nwd"))

    # qtbot.stopForInteraction()
    nwGUI.closeMain()

@pytest.mark.gui
def testNewProjectWizard(qtbot, nwTempGUI, nwLipsum, nwRef, nwTemp):

    from PyQt5.QtWidgets import QWizard
    from nw.gui.projwizard import (
        ProjWizardIntroPage, ProjWizardFolderPage, ProjWizardPopulatePage,
        ProjWizardCustomPage, ProjWizardFinalPage
    )

    nwGUI = nw.main(["--testmode", "--config=%s" % nwTempGUI, "--data=%s" % nwTemp])
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
def testDocAction(qtbot, nwTempGUI, nwLipsum, nwRef, nwTemp):

    nwGUI = nw.main(["--testmode", "--config=%s" % nwTempGUI, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.openProject(nwLipsum)
    qtbot.wait(stepDelay)

    # Split By Chapter
    assert nwGUI.openDocument("4c4f28287af27")
    assert nwGUI.docEditor.setCursorPosition(30)

    cleanText = nwGUI.docEditor.getText()[27:74]

    # Bold
    assert nwGUI.passDocumentAction(nwDocAction.STRONG)
    fmtStr = "**Pellentesque** nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:78] == fmtStr
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.STRONG)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Italic
    assert nwGUI.passDocumentAction(nwDocAction.EMPH)
    fmtStr = "_Pellentesque_ nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:76] == fmtStr
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.EMPH)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Strikethrough
    assert nwGUI.passDocumentAction(nwDocAction.STRIKE)
    fmtStr = "~~Pellentesque~~ nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:78] == fmtStr
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.STRIKE)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Should get us back to plain
    assert nwGUI.passDocumentAction(nwDocAction.STRONG)
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.EMPH)
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.EMPH)
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.STRONG)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Double Quotes
    assert nwGUI.passDocumentAction(nwDocAction.D_QUOTE)
    fmtStr = "“Pellentesque” nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:76] == fmtStr
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.UNDO)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Single Quotes
    assert nwGUI.passDocumentAction(nwDocAction.S_QUOTE)
    fmtStr = "‘Pellentesque’ nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:76] == fmtStr
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.UNDO)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Block Formats
    assert nwGUI.docEditor.setCursorPosition(30)
    assert nwGUI.passDocumentAction(nwDocAction.BLOCK_H1)
    fmtStr = "# Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:76] == fmtStr
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.BLOCK_H2)
    fmtStr = "## Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:77] == fmtStr
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.BLOCK_H3)
    fmtStr = "### Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:78] == fmtStr
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.BLOCK_H4)
    fmtStr = "#### Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:79] == fmtStr
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.BLOCK_TXT)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.BLOCK_COM)
    fmtStr = "% Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:76] == fmtStr
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.BLOCK_TXT)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Undo/Redo
    assert nwGUI.passDocumentAction(nwDocAction.UNDO)
    fmtStr = "% Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:76] == fmtStr
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.REDO)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # qtbot.stopForInteraction()
    nwGUI.closeMain()

@pytest.mark.gui
def testInsertMenu(qtbot, nwTempGUI, nwFuncTemp, nwTemp):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwTempGUI, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": nwFuncTemp}, True)

    assert nwGUI.treeView._getTreeItem("31489056e0916") is not None

    nwGUI.setFocus(1)
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem("31489056e0916").setSelected(True)
    nwGUI.treeView.newTreeItem(nwItemType.FILE, None)
    assert nwGUI.openSelectedItem()

    # qtbot.stopForInteraction()

    nwGUI.mainMenu.aInsENDash.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_ENDASH
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsEMDash.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_EMDASH
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsEllipsis.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_HELLIP
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsQuoteLS.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwGUI.mainConf.fmtSingleQuotes[0]
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsQuoteRS.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwGUI.mainConf.fmtSingleQuotes[1]
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsQuoteLD.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwGUI.mainConf.fmtDoubleQuotes[0]
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsQuoteRD.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwGUI.mainConf.fmtDoubleQuotes[1]
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsMSApos.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_MAPOSS
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsMDApos.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_MAPOSD
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsHardBreak.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "  \n"
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsNBSpace.activate(QAction.Trigger)
    if nwGUI.mainConf.verQtValue >= 50900:
        assert nwGUI.docEditor.getText() == nwUnicode.U_NBSP
    else:
        assert nwGUI.docEditor.getText() == " "
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsThinSpace.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == nwUnicode.U_THNSP
    nwGUI.docEditor.clear()

    nwGUI.mainMenu.aInsThinNBSpace.activate(QAction.Trigger)
    if nwGUI.mainConf.verQtValue >= 50900:
        assert nwGUI.docEditor.getText() == nwUnicode.U_THNBSP
    else:
        assert nwGUI.docEditor.getText() == " "
    nwGUI.docEditor.clear()

    # qtbot.stopForInteraction()
    nwGUI.closeMain()

@pytest.mark.gui
def testLoadProject(qtbot, nwTempGUI, nwTemp):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwTempGUI, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    nwLoad = GuiProjectLoad(nwGUI)
    nwLoad.show()

    recentCount = nwLoad.listBox.topLevelItemCount()
    assert recentCount > 1

    selItem = nwLoad.listBox.topLevelItem(1)
    selPath = selItem.data(nwLoad.C_NAME, Qt.UserRole)

    nwLoad.selPath.setText("")
    nwLoad.listBox.setCurrentItem(selItem)
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

@pytest.mark.gui
def testOutline(qtbot, nwTempBuild, nwLipsum, nwTemp):

    nwGUI = nw.main(["--testmode", "--config=%s" % nwTempBuild, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    assert nwGUI.openProject(nwLipsum)
    nwGUI.mainConf.lastPath = nwTempBuild

    nwGUI.rebuildIndex()
    nwGUI.tabWidget.setCurrentIndex(nwGUI.idxTabProj)

    assert nwGUI.projView.topLevelItemCount() > 0

    # Context Menu
    nwGUI.projView._headerRightClick(QPoint(1, 1))
    nwGUI.projView.headerMenu.actionMap[nwOutline.CCOUNT].activate(QAction.Trigger)
    nwGUI.projView.headerMenu.close()
    qtbot.mouseClick(nwGUI.projView, Qt.LeftButton)

    nwGUI.projView._loadHeaderState()
    assert not nwGUI.projView.colHidden[nwOutline.CCOUNT]

    # First Item
    nwGUI.rebuildOutline()
    selItem = nwGUI.projView.topLevelItem(0)
    assert isinstance(selItem, QTreeWidgetItem)

    nwGUI.projView.setCurrentItem(selItem)
    assert nwGUI.projMeta.titleLabel.text() == "<b>Title</b>"
    assert nwGUI.projMeta.titleValue.text() == "Lorem Ipsum"
    assert nwGUI.projMeta.fileValue.text() == "Lorem Ipsum"
    assert nwGUI.projMeta.itemValue.text() == "Finished"

    assert nwGUI.projMeta.cCValue.text() == "122"
    assert nwGUI.projMeta.wCValue.text() == "18"
    assert nwGUI.projMeta.pCValue.text() == "2"

    # Scene One
    actItem = nwGUI.projView.topLevelItem(1)
    chpItem = actItem.child(0)
    selItem = chpItem.child(0)

    nwGUI.projView.setCurrentItem(selItem)
    assert nwGUI.projMeta.titleLabel.text() == "<b>Scene</b>"
    assert nwGUI.projMeta.titleValue.text() == "Scene One"
    assert nwGUI.projMeta.fileValue.text() == "Scene One"
    assert nwGUI.projMeta.itemValue.text() == "Finished"

    # Click POV Link
    assert nwGUI.projMeta.povKeyValue.text() == "<a href='#pov=Bod'>Bod</a>"
    nwGUI.projMeta._tagClicked("#pov=Bod")
    assert nwGUI.docViewer.theHandle == "4c4f28287af27"

    # qtbot.stopForInteraction()
    nwGUI.closeMain()
