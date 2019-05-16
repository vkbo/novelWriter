# -*- coding: utf-8 -*-
"""novelWriter Main GUI Class Tester
"""

import nw, pytest
from nwtools import *
from os import path, unlink
from PyQt5.QtCore import Qt

keyDelay = 10
testDir  = path.dirname(__file__)
testRef  = path.join(testDir,"reference")

@pytest.mark.gui
def testMainWindows(qtbot, tmpdir):
    confDir = tmpdir.mkdir("conf")
    projDir = tmpdir.mkdir("project")
    nwGUI = nw.main(["--testmode","--config=%s" % confDir])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(500)
    nwGUI.theProject.handleSeed = 42
    assert nwGUI.theProject.setProjectPath(projDir)
    assert nwGUI.newProject()
    assert nwGUI.theProject.setProjectPath(projDir)
    assert nwGUI.saveProject()
    qtbot.wait(500)
    assert nwGUI.openProject(projDir)
    qtbot.keyClick(nwGUI.treeView, Qt.Key_1, modifier=Qt.ControlModifier, delay=keyDelay)
    qtbot.keyClick(nwGUI.treeView, Qt.Key_Down, delay=keyDelay)
    qtbot.keyClick(nwGUI.treeView, Qt.Key_Right, delay=keyDelay)
    qtbot.keyClick(nwGUI.treeView, Qt.Key_Down, delay=keyDelay)
    qtbot.keyClick(nwGUI.treeView, Qt.Key_Right, delay=keyDelay)
    qtbot.keyClick(nwGUI.treeView, Qt.Key_Down, delay=keyDelay)
    qtbot.keyClick(nwGUI.treeView, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.treeView, Qt.Key_2, modifier=Qt.ControlModifier, delay=keyDelay)
    for c in "# Hello World!":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "This is a paragraph of dummy text.":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "This is another paragraph of much longer dummy text. It is in fact very very dum dummy text! ":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    for c in "We can also try replacing \"quotes\", even single's quotes are replaced. ":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    for c in "We can hyphen-ate, make dashes -- and even longer dashes --- if we want. ":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    for c in "Ellipsis? Not a problem either ... ":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.wait(500)
    qtbot.keyClick(nwGUI, "s", modifier=Qt.ControlModifier, delay=keyDelay)
    qtbot.wait(500)

    projFile = projDir.join("nwProject.nwx")
    assert cmpFiles(projFile, path.join(testRef,"gui_nwProject.nwx"), [2])
    sceneFile = projDir.join("data_3","1489056e0916_main.nwd")
    assert cmpFiles(sceneFile, path.join(testRef,"gui_1489056e0916_main.nwd"))

    # qtbot.stopForInteraction()
