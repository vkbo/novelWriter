# -*- coding: utf-8 -*-
"""novelWriter Main GUI Class Tester
"""

import nw, pytest
from nwtools import *
from os import path, unlink
from PyQt5.QtCore import Qt

keyDelay  = 10
stepDelay = 50
testDir   = path.dirname(__file__)
testRef   = path.join(testDir,"reference")

@pytest.mark.gui
def testMainWindows(qtbot, tmpdir):
    confDir = str(tmpdir.mkdir("conf"))
    projDir = str(tmpdir.mkdir("project"))
    nwGUI = nw.main(["--testmode","--config=%s" % confDir])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    # Create new, save, open project
    nwGUI.theProject.handleSeed = 42
    assert nwGUI.theProject.setProjectPath(projDir)
    assert nwGUI.newProject()
    assert nwGUI.theProject.setProjectPath(projDir)
    assert nwGUI.saveProject()
    qtbot.wait(stepDelay)
    assert nwGUI.openProject(projDir)
    qtbot.wait(stepDelay)

    # Check that tree items have been created
    assert nwGUI.treeView._getTreeItem("73475cb40a568") is not None
    assert nwGUI.treeView._getTreeItem("25fc0e7096fc6") is not None
    assert nwGUI.treeView._getTreeItem("31489056e0916") is not None
    assert nwGUI.treeView._getTreeItem("44cb730c42048") is not None
    assert nwGUI.treeView._getTreeItem("71ee45a3c0db9") is not None
    assert nwGUI.treeView._getTreeItem("811786ad1ae74") is not None

    # Select the 'New Scene' file
    nwGUI.treeView.setFocus()
    nwGUI.treeView._getTreeItem("73475cb40a568").setExpanded(True)
    nwGUI.treeView._getTreeItem("25fc0e7096fc6").setExpanded(True)
    nwGUI.treeView._getTreeItem("31489056e0916").setSelected(True)
    assert nwGUI.openSelectedItem()

    # Type something into the document
    nwGUI.docEditor.setFocus()
    for c in "# Hello World!":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "## With a Subtitle":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "### An Even Subier Title":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "#### Basically Not a Title at All":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "% How about a comment?":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "@keyword: value":
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
    nwGUI.docEditor._runCounter()
    qtbot.wait(1000)

    # Save the document
    assert nwGUI.docEditor.docChanged
    assert nwGUI.saveDocument()
    qtbot.wait(stepDelay)

    # Check the files
    projFile = path.join(projDir,"nwProject.nwx")
    assert cmpFiles(projFile, path.join(testRef,"gui_nwProject.nwx"), [2])
    sceneFile = path.join(projDir,"data_3","1489056e0916_main.nwd")
    assert cmpFiles(sceneFile, path.join(testRef,"gui_1489056e0916_main.nwd"))

    # qtbot.stopForInteraction()
