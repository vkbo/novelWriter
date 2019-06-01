# -*- coding: utf-8 -*-
"""novelWriter Main GUI Class Tester
"""

import nw, pytest
from nwtools import *

from os import path, unlink
from PyQt5.QtCore import Qt

from nw.gui.projecteditor import GuiProjectEditor
from nw.gui.timelineview  import GuiTimeLineView
from nw.gui.itemeditor    import GuiItemEditor
from nw.enum              import *

keyDelay  = 10
stepDelay = 50

@pytest.mark.gui
def testMainWindows(qtbot, nwTempGUI, nwRef):
    nwGUI = nw.main(["--testmode","--config=%s" % nwTempGUI])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    # Create new, save, close project
    nwGUI.theProject.handleSeed = 42
    assert nwGUI.newProject(nwTempGUI, True)
    assert nwGUI.saveProject()
    assert nwGUI.closeProject()

    assert len(nwGUI.theProject.projTree) == 0
    assert len(nwGUI.theProject.treeOrder) == 0
    assert len(nwGUI.theProject.treeRoots) == 0
    assert nwGUI.theProject.trashRoot is None
    assert nwGUI.theProject.projPath is None
    assert nwGUI.theProject.projMeta is None
    assert nwGUI.theProject.projCache is None
    assert nwGUI.theProject.projFile == "nwProject.nwx"
    assert nwGUI.theProject.projName == ""
    assert nwGUI.theProject.bookTitle == ""
    assert len(nwGUI.theProject.bookAuthors) == 0
    assert nwGUI.theProject.spellCheck == False

    # Check the files
    projFile = path.join(nwTempGUI,"nwProject.nwx")
    assert cmpFiles(projFile, path.join(nwRef,"gui","0_nwProject.nwx"), [2])
    qtbot.wait(stepDelay)

    # Re-open project
    assert nwGUI.openProject(nwTempGUI)
    qtbot.wait(stepDelay)

    # Check that we loaded the data
    assert len(nwGUI.theProject.projTree) == 6
    assert len(nwGUI.theProject.treeOrder) == 6
    assert len(nwGUI.theProject.treeRoots) == 4
    assert nwGUI.theProject.trashRoot is None
    assert nwGUI.theProject.projPath == nwTempGUI
    assert nwGUI.theProject.projMeta == path.join(nwTempGUI,"meta")
    assert nwGUI.theProject.projCache == path.join(nwTempGUI,"cache")
    assert nwGUI.theProject.projFile == "nwProject.nwx"
    assert nwGUI.theProject.projName == ""
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

    nwGUI.mainMenu.toolsSpellCheck.setChecked(True)
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

    # Check the files
    projFile = path.join(nwTempGUI,"nwProject.nwx")
    assert cmpFiles(projFile, path.join(nwRef,"gui","1_nwProject.nwx"), [2])
    sceneFile = path.join(nwTempGUI,"data_0","2d20bbd7e394_main.nwd")
    assert cmpFiles(sceneFile, path.join(nwRef,"gui","1_2d20bbd7e394_main.nwd"))
    sceneFile = path.join(nwTempGUI,"data_2","fca346db6561_main.nwd")
    assert cmpFiles(sceneFile, path.join(nwRef,"gui","1_fca346db6561_main.nwd"))
    sceneFile = path.join(nwTempGUI,"data_3","1489056e0916_main.nwd")
    assert cmpFiles(sceneFile, path.join(nwRef,"gui","1_1489056e0916_main.nwd"))
    sceneFile = path.join(nwTempGUI,"data_7","688b6ef52555_main.nwd")
    assert cmpFiles(sceneFile, path.join(nwRef,"gui","1_688b6ef52555_main.nwd"))

    nwGUI.closeMain()
    # qtbot.stopForInteraction()

@pytest.mark.gui
def testTimeLineView(qtbot, nwTempGUI, nwRef):
    nwGUI = nw.main(["--testmode","--config=%s" % nwTempGUI])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    # Create new, save, open project
    nwGUI.theProject.handleSeed = 42
    assert nwGUI.openProject(nwTempGUI)
    qtbot.wait(stepDelay)

    timeLine = GuiTimeLineView(nwGUI, nwGUI.theProject, nwGUI.theIndex)
    qtbot.addWidget(timeLine)

    assert timeLine.numRows == 4
    assert timeLine.numCols == 3

    # qtbot.stopForInteraction()
    nwGUI.closeMain()

@pytest.mark.gui
def testProjectEditor(qtbot, nwTempGUI, nwRef):
    nwGUI = nw.main(["--testmode","--config=%s" % nwTempGUI])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    # Create new, save, open project
    nwGUI.theProject.handleSeed = 42
    assert nwGUI.newProject(nwTempGUI, True)

    projEdit = GuiProjectEditor(nwGUI, nwGUI.theProject)
    qtbot.addWidget(projEdit)

    for c in "Project Name":
        qtbot.keyClick(projEdit.tabMain.editName, c, delay=keyDelay)
    for c in "Project Title":
        qtbot.keyClick(projEdit.tabMain.editTitle, c, delay=keyDelay)
    for c in "Jane Doe":
        qtbot.keyClick(projEdit.tabMain.editAuthors, c, delay=keyDelay)
    qtbot.keyClick(projEdit.tabMain.editAuthors, Qt.Key_Return, delay=keyDelay)
    for c in "John Doh":
        qtbot.keyClick(projEdit.tabMain.editAuthors, c, delay=keyDelay)

    #Test Status Tab
    projEdit.tabWidget.setCurrentWidget(projEdit.tabStatus)
    projEdit.tabStatus.listBox.item(2).setSelected(True)
    qtbot.mouseClick(projEdit.tabStatus.delButton, Qt.LeftButton)
    qtbot.mouseClick(projEdit.tabStatus.newButton, Qt.LeftButton)
    projEdit.tabStatus.listBox.item(3).setSelected(True)
    for n in range(8):
        qtbot.keyClick(projEdit.tabStatus.editName, Qt.Key_Backspace, delay=keyDelay)
    for c in "Final":
        qtbot.keyClick(projEdit.tabStatus.editName, c, delay=keyDelay)
    qtbot.mouseClick(projEdit.tabStatus.saveButton, Qt.LeftButton)

    projEdit._doSave()

    # Open again, and check project settings
    projEdit = GuiProjectEditor(nwGUI, nwGUI.theProject)
    qtbot.addWidget(projEdit)
    assert projEdit.tabMain.editName.text()    == "Project Name"
    assert projEdit.tabMain.editTitle.text()   == "Project Title"
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
    assert cmpFiles(projFile, path.join(nwRef,"gui","2_nwProject.nwx"), [2])

    nwGUI.closeMain()
    # qtbot.stopForInteraction()

@pytest.mark.gui
def testItemEditor(qtbot, nwTempGUI, nwRef):
    nwGUI = nw.main(["--testmode","--config=%s" % nwTempGUI])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    # Create new, save, open project
    nwGUI.theProject.handleSeed = 42
    assert nwGUI.newProject(nwTempGUI, True)

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

    qtbot.mouseClick(itemEdit.saveButton, Qt.LeftButton)

    itemEdit = GuiItemEditor(nwGUI, nwGUI.theProject, "31489056e0916")
    qtbot.addWidget(itemEdit)
    assert itemEdit.editName.text()          == "Just a Page"
    assert itemEdit.editStatus.currentData() == "Note"
    assert itemEdit.editLayout.currentData() == nwItemLayout.PAGE

    qtbot.mouseClick(itemEdit.closeButton, Qt.LeftButton)

    qtbot.wait(stepDelay)
    assert nwGUI.saveProject()
    qtbot.wait(stepDelay)

    # Check the files
    projFile = path.join(nwTempGUI,"nwProject.nwx")
    assert cmpFiles(projFile, path.join(nwRef,"gui","3_nwProject.nwx"), [2])

    nwGUI.closeMain()
    # qtbot.stopForInteraction()
