# -*- coding: utf-8 -*-
"""novelWriter Main GUI Class Tester
"""

import nw, pytest, sys
from nwtools import *

from os import path, unlink
from PyQt5.QtCore import Qt

from nw.gui import (
    GuiProjectSettings, GuiItemEditor, GuiAbout, GuiBuildNovel,
    GuiDocMerge, GuiDocSplit
)
from nw.constants import *

keyDelay  =  5
stepDelay = 50

@pytest.mark.gui
def testMainWindows(qtbot, nwTempGUI, nwRef, nwTemp):
    nwGUI = nw.main(["--testmode","--config=%s" % nwTempGUI, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    # Create new, save, close project
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject(nwTempGUI, True)
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
    assert nwGUI.theProject.spellCheck == False

    # Check the files
    projFile = path.join(nwTempGUI,"nwProject.nwx")
    assert cmpFiles(projFile, path.join(nwRef,"gui","0_nwProject.nwx"), [2, 6, 7, 8])
    qtbot.wait(stepDelay)

    # qtbot.stopForInteraction()

    # Re-open project
    assert nwGUI.openProject(nwTempGUI)
    qtbot.wait(stepDelay)

    # Check that we loaded the data
    assert len(nwGUI.theProject.projTree) == 6
    assert len(nwGUI.theProject.projTree._treeOrder) == 6
    assert len(nwGUI.theProject.projTree._treeRoots) == 4
    assert nwGUI.theProject.projTree.trashRoot() is None
    assert nwGUI.theProject.projPath == nwTempGUI
    assert nwGUI.theProject.projMeta == path.join(nwTempGUI,"meta")
    assert nwGUI.theProject.projFile == "nwProject.nwx"
    assert nwGUI.theProject.projName == "New Project"
    assert nwGUI.theProject.bookTitle == ""
    assert len(nwGUI.theProject.bookAuthors) == 0
    assert nwGUI.theProject.spellCheck == False

    # Check that tree items have been created
    assert nwGUI.treeView._getTreeItem("73475cb40a568") is not None
    assert nwGUI.treeView._getTreeItem("25fc0e7096fc6") is not None
    assert nwGUI.treeView._getTreeItem("31489056e0916") is not None
    assert nwGUI.treeView._getTreeItem("44cb730c42048") is not None
    assert nwGUI.treeView._getTreeItem("71ee45a3c0db9") is not None
    assert nwGUI.treeView._getTreeItem("811786ad1ae74") is not None

    nwGUI.mainMenu.aSpellCheck.setChecked(True)
    assert nwGUI.mainMenu._toggleSpellCheck()

    # Add a Character File
    nwGUI.setFocus(1)
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem("44cb730c42048").setSelected(True)
    nwGUI.treeView.newTreeItem(nwItemType.FILE, None)
    assert nwGUI.openSelectedItem()

    # Type something into the document
    nwGUI.setFocus(2)
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
    nwGUI.treeView._getTreeItem("71ee45a3c0db9").setSelected(True)
    nwGUI.treeView.newTreeItem(nwItemType.FILE, None)
    assert nwGUI.openSelectedItem()

    # Type something into the document
    nwGUI.setFocus(2)
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
    nwGUI.treeView._getTreeItem("25fc0e7096fc6").setExpanded(True)
    nwGUI.treeView._getTreeItem("31489056e0916").setSelected(True)
    assert nwGUI.openSelectedItem()

    # Type something into the document
    nwGUI.setFocus(2)
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

    for c in "This is another paragraph of much longer dummy text. It is in fact very very dumb dummy text! ":
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
    assert nwGUI.openDocument("31489056e0916")
    assert nwGUI.viewDocument("31489056e0916")
    qtbot.wait(stepDelay)
    assert nwGUI.saveProject()
    assert nwGUI.closeDocViewer()
    qtbot.wait(stepDelay)

    # Check a Quick Create and Delete
    assert nwGUI.treeView.newTreeItem(nwItemType.FILE, None)
    newHandle = nwGUI.treeView.getSelectedHandle()
    assert nwGUI.theProject.projTree["031b4af5197ec"] is not None
    assert nwGUI.treeView.deleteItem()
    assert nwGUI.treeView.setSelectedHandle(newHandle)
    assert nwGUI.treeView.deleteItem()
    assert nwGUI.saveProject()

    # Check the files
    refFile = path.join(nwTempGUI, "nwProject.nwx")
    assert cmpFiles(refFile, path.join(nwRef, "gui", "1_nwProject.nwx"), [2, 6, 7, 8])
    refFile = path.join(nwTempGUI, "content", "0e17daca5f3e1.nwd")
    assert cmpFiles(refFile, path.join(nwRef, "gui", "1_0e17daca5f3e1.nwd"))
    refFile = path.join(nwTempGUI, "content", "98010bd9270f9.nwd")
    assert cmpFiles(refFile, path.join(nwRef, "gui", "1_98010bd9270f9.nwd"))
    refFile = path.join(nwTempGUI, "content", "31489056e0916.nwd")
    assert cmpFiles(refFile, path.join(nwRef, "gui", "1_31489056e0916.nwd"))
    refFile = path.join(nwTempGUI, "content", "1a6562590ef19.nwd")
    assert cmpFiles(refFile, path.join(nwRef, "gui", "1_1a6562590ef19.nwd"))

    nwGUI.closeMain()
    # qtbot.stopForInteraction()

@pytest.mark.gui
def testProjectEditor(qtbot, nwTempGUI, nwRef, nwTemp):
    nwGUI = nw.main(["--testmode","--config=%s" % nwTempGUI, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    # Create new, save, open project
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject(nwTempGUI, True)
    nwGUI.mainConf.backupPath = nwTempGUI

    projEdit = GuiProjectSettings(nwGUI, nwGUI.theProject)
    projEdit.show()
    qtbot.addWidget(projEdit)

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
    projEdit._tabBox.setCurrentWidget(projEdit.tabReplace)

    qtbot.mouseClick(projEdit.tabReplace.addButton, Qt.LeftButton)
    projEdit.tabReplace.listBox.topLevelItem(0).setSelected(True)
    for c in "Th is ":
        qtbot.keyClick(projEdit.tabReplace.editKey, c, delay=keyDelay)
    for c in "With This Stuff ":
        qtbot.keyClick(projEdit.tabReplace.editValue, c, delay=keyDelay)
    qtbot.mouseClick(projEdit.tabReplace.saveButton, Qt.LeftButton)

    projEdit.tabReplace.listBox.clearSelection()
    qtbot.mouseClick(projEdit.tabReplace.addButton, Qt.LeftButton)
    projEdit.tabReplace.listBox.topLevelItem(0).setSelected(True)
    for c in "Delete":
        qtbot.keyClick(projEdit.tabReplace.editKey, c, delay=keyDelay)
    for c in "This Stuff":
        qtbot.keyClick(projEdit.tabReplace.editValue, c, delay=keyDelay)
    qtbot.mouseClick(projEdit.tabReplace.saveButton, Qt.LeftButton)

    projEdit.tabReplace.listBox.clearSelection()
    projEdit.tabReplace.listBox.topLevelItem(0).setSelected(True)
    qtbot.mouseClick(projEdit.tabReplace.delButton, Qt.LeftButton)

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
    projFile = path.join(nwTempGUI,"nwProject.nwx")
    assert cmpFiles(projFile, path.join(nwRef, "gui", "2_nwProject.nwx"), [2, 8, 9, 10])

    nwGUI.closeMain()
    # qtbot.stopForInteraction()

@pytest.mark.gui
def testItemEditor(qtbot, nwTempGUI, nwRef, nwTemp):
    nwGUI = nw.main(["--testmode","--config=%s" % nwTempGUI, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    # Create new, save, open project
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject(nwTempGUI, True)
    assert nwGUI.openDocument("31489056e0916")

    itemEdit = GuiItemEditor(nwGUI, nwGUI.theProject, "31489056e0916")
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

    itemEdit = GuiItemEditor(nwGUI, nwGUI.theProject, "31489056e0916")
    qtbot.addWidget(itemEdit)
    assert itemEdit.editName.text()          == "Just a Page"
    assert itemEdit.editStatus.currentData() == "Note"
    assert itemEdit.editLayout.currentData() == nwItemLayout.PAGE
    itemEdit._doClose()

    # Check that the header is updated
    nwGUI.docEditor.updateDocTitle("31489056e0916")
    assert nwGUI.docEditor.docHeader.theTitle.text() == "Novel  ›  New Chapter  ›  Just a Page"
    assert not nwGUI.docEditor.setCursorLine("where?")
    assert nwGUI.docEditor.setCursorLine(2)
    qtbot.wait(stepDelay)
    assert nwGUI.docEditor.getCursorPosition() == 9

    qtbot.wait(stepDelay)
    assert nwGUI.saveProject()
    qtbot.wait(stepDelay)

    # Check the files
    projFile = path.join(nwTempGUI,"nwProject.nwx")
    assert cmpFiles(projFile, path.join(nwRef, "gui", "3_nwProject.nwx"), [2, 6, 7, 8])

    nwGUI.closeMain()
    # qtbot.stopForInteraction()

@pytest.mark.gui
def testAboutBox(qtbot, nwTempGUI, nwRef, nwTemp):
    nwGUI = nw.main(["--testmode","--config=%s" % nwTempGUI, "--data=%s" % nwTemp])
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

    nwGUI = nw.main(["--testmode","--config=%s" % nwTempBuild, "--data=%s" % nwTemp])
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

    nwGUI = nw.main(["--testmode","--config=%s" % nwTempGUI, "--data=%s" % nwTemp])
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

    nwGUI = nw.main(["--testmode","--config=%s" % nwTempGUI, "--data=%s" % nwTemp])
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
def testDocAction(qtbot, nwTempGUI, nwLipsum, nwRef, nwTemp):

    nwGUI = nw.main(["--testmode","--config=%s" % nwTempGUI, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.openProject(nwLipsum)
    qtbot.wait(stepDelay)

    # CUT        = 3
    # COPY       = 4
    # PASTE      = 5
    # SEL_ALL    = 12
    # SEL_PARA   = 13
    # FIND       = 14
    # REPLACE    = 15
    # GO_NEXT    = 16
    # GO_PREV    = 17
    # REPL_NEXT  = 18

    # Split By Chapter
    assert nwGUI.openDocument("4c4f28287af27")
    assert nwGUI.docEditor.setCursorPosition(30)

    cleanText = nwGUI.docEditor.getText()[27:74]

    # Bold
    assert nwGUI.passDocumentAction(nwDocAction.BOLD)
    assert nwGUI.docEditor.getText()[27:78] == "**Pellentesque** nec erat ut nulla posuere commodo."
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.BOLD)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Italic
    assert nwGUI.passDocumentAction(nwDocAction.ITALIC)
    assert nwGUI.docEditor.getText()[27:76] == "*Pellentesque* nec erat ut nulla posuere commodo."
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.ITALIC)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Bold-Italic
    assert nwGUI.passDocumentAction(nwDocAction.BOLDITALIC)
    assert nwGUI.docEditor.getText()[27:80] == "***Pellentesque*** nec erat ut nulla posuere commodo."
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.BOLDITALIC)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Strikethrough
    assert nwGUI.passDocumentAction(nwDocAction.STRIKE)
    assert nwGUI.docEditor.getText()[27:78] == "~~Pellentesque~~ nec erat ut nulla posuere commodo."
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.STRIKE)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Should get us back to plain
    assert nwGUI.passDocumentAction(nwDocAction.BOLD)
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.ITALIC)
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.ITALIC)
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.BOLD)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Equivalent of the above
    assert nwGUI.passDocumentAction(nwDocAction.BOLDITALIC)
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.ITALIC)
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.BOLD)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Double Quotes
    assert nwGUI.passDocumentAction(nwDocAction.D_QUOTE)
    assert nwGUI.docEditor.getText()[27:76] == "“Pellentesque” nec erat ut nulla posuere commodo."
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.UNDO)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Single Quotes
    assert nwGUI.passDocumentAction(nwDocAction.S_QUOTE)
    assert nwGUI.docEditor.getText()[27:76] == "‘Pellentesque’ nec erat ut nulla posuere commodo."
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.UNDO)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Block Formats
    assert nwGUI.docEditor.setCursorPosition(30)
    assert nwGUI.passDocumentAction(nwDocAction.BLOCK_H1)
    assert nwGUI.docEditor.getText()[27:76] == "# Pellentesque nec erat ut nulla posuere commodo."
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.BLOCK_H2)
    assert nwGUI.docEditor.getText()[27:77] == "## Pellentesque nec erat ut nulla posuere commodo."
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.BLOCK_H3)
    assert nwGUI.docEditor.getText()[27:78] == "### Pellentesque nec erat ut nulla posuere commodo."
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.BLOCK_H4)
    assert nwGUI.docEditor.getText()[27:79] == "#### Pellentesque nec erat ut nulla posuere commodo."
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.BLOCK_TXT)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.BLOCK_COM)
    assert nwGUI.docEditor.getText()[27:76] == "% Pellentesque nec erat ut nulla posuere commodo."
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.BLOCK_TXT)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Undo/Redo
    assert nwGUI.passDocumentAction(nwDocAction.UNDO)
    assert nwGUI.docEditor.getText()[27:76] == "% Pellentesque nec erat ut nulla posuere commodo."
    qtbot.wait(stepDelay)
    assert nwGUI.passDocumentAction(nwDocAction.REDO)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # qtbot.stopForInteraction()
    nwGUI.closeMain()
