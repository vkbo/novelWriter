# -*- coding: utf-8 -*-
"""novelWriter Main GUI Class Tester
"""

import nw
import pytest
import logging
import os
import sys

from shutil import copyfile
from nwtools import cmpFiles

from PyQt5.QtCore import Qt, QUrl, QPoint, QItemSelectionModel
from PyQt5.QtGui import QTextCursor, QColor, QPixmap, QIcon
from PyQt5.QtWidgets import (
    qApp, QAction, QTreeWidgetItem, QStyle, QFileDialog, QMessageBox
)

from nw.constants import (
    nwItemType, nwItemClass, nwUnicode, nwOutline, nwDocAction, nwDocInsert
)

keyDelay = 2
typeDelay = 1
stepDelay = 20

@pytest.mark.gui
def testLaunch(qtbot, monkeypatch, nwFuncTemp, nwTemp):

    # Defaults
    nwGUI = nw.main(
        ["--testmode", "--config=%s" % nwFuncTemp, "--data=%s" % nwTemp, "--style=Fusion"]
    )
    assert nw.logger.getEffectiveLevel() == logging.WARNING
    nwGUI.closeMain()
    nwGUI.close()

    # Log Levels
    nwGUI = nw.main(
        ["--testmode", "--info", "--config=%s" % nwFuncTemp, "--data=%s" % nwTemp]
    )
    assert nw.logger.getEffectiveLevel() == logging.INFO
    nwGUI.closeMain()
    nwGUI.close()

    nwGUI = nw.main(
        ["--testmode", "--debug", "--config=%s" % nwFuncTemp, "--data=%s" % nwTemp]
    )
    assert nw.logger.getEffectiveLevel() == logging.DEBUG
    nwGUI.closeMain()
    nwGUI.close()

    nwGUI = nw.main(
        ["--testmode", "--verbose", "--config=%s" % nwFuncTemp, "--data=%s" % nwTemp]
    )
    assert nw.logger.getEffectiveLevel() == 5
    nwGUI.closeMain()
    nwGUI.close()

    # Help and Version
    with pytest.raises(SystemExit) as ex:
        nwGUI = nw.main(
            ["--testmode", "--help", "--config=%s" % nwFuncTemp, "--data=%s" % nwTemp]
        )
    nwGUI.closeMain()
    nwGUI.close()
    assert ex.value.code == 0

    with pytest.raises(SystemExit) as ex:
        nwGUI = nw.main(
            ["--testmode", "--version", "--config=%s" % nwFuncTemp, "--data=%s" % nwTemp]
        )
    nwGUI.closeMain()
    nwGUI.close()
    assert ex.value.code == 0

    # Invalid options
    with pytest.raises(SystemExit) as ex:
        nwGUI = nw.main(
            ["--testmode", "--invalid", "--config=%s" % nwFuncTemp, "--data=%s" % nwTemp]
        )
    nwGUI.closeMain()
    nwGUI.close()
    assert ex.value.code == 2

    # Simulate import error
    monkeypatch.setitem(sys.modules, "lxml", None)
    monkeypatch.setattr("sys.hexversion", 0x0)
    monkeypatch.setattr("nw.CONFIG.verQtValue", 50000)
    monkeypatch.setattr("nw.CONFIG.verPyQtValue", 50000)
    with pytest.raises(SystemExit) as ex:
        nwGUI = nw.main(
            ["--testmode", "--config=%s" % nwFuncTemp, "--data=%s" % nwTemp]
        )
    nwGUI.closeMain()
    nwGUI.close()
    assert ex.value.code & 4 == 4   # Python version not satisfied
    assert ex.value.code & 8 == 8   # Qt version not satisfied
    assert ex.value.code & 16 == 16 # PyQt version not satisfied
    assert ex.value.code & 32 == 32 # lxml package missing
    monkeypatch.undo()

@pytest.mark.gui
def testDocEditor(qtbot, yesToAll, nwFuncTemp, nwTempGUI, nwRef, nwTemp):

    nwGUI = nw.main(["--testmode", "--config=%s" % nwTemp, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    # Create new, save, close project
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": nwFuncTemp})
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
    projFile = os.path.join(nwFuncTemp, "nwProject.nwx")
    testFile = os.path.join(nwTempGUI, "0_nwProject.nwx")
    refFile  = os.path.join(nwRef, "gui", "0_nwProject.nwx")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [2, 6, 7, 8])
    qtbot.wait(stepDelay)

    # qtbot.stopForInteraction()

    # Re-open project
    assert nwGUI.openProject(nwFuncTemp)
    qtbot.wait(stepDelay)

    # Check that we loaded the data
    assert len(nwGUI.theProject.projTree) == 8
    assert len(nwGUI.theProject.projTree._treeOrder) == 8
    assert len(nwGUI.theProject.projTree._treeRoots) == 4
    assert nwGUI.theProject.projTree.trashRoot() is None
    assert nwGUI.theProject.projPath == nwFuncTemp
    assert nwGUI.theProject.projMeta == os.path.join(nwFuncTemp, "meta")
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
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "@tag: Jane":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "This is a file about Jane.":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
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
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "@tag: MainPlot":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "This is a file detailing the main plot.":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
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
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "@tag: Home":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "This is a file describing Jane's home.":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    # Trigger autosaves before making more changes
    nwGUI._autoSaveDocument()
    nwGUI._autoSaveProject()

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
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "## Chapter":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "@pov: Jane":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "@plot: MainPlot":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "### Scene":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "% How about a comment?":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "@pov: Jane":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "@plot: MainPlot":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    for c in "@location: Home":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "#### Some Section":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "@char: Jane":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "This is a paragraph of dummy text.":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in (
        "This is another paragraph of much longer dummy text. "
        "It is in fact very very dumb dummy text! "
    ):
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    for c in "We can also try replacing \"quotes\", even single 'quotes' are replaced. ":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    for c in "Isn't that nice? ":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    for c in "We can hyphen-ate, make dashes -- and even longer dashes --- if we want. ":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    for c in "Ellipsis? Not a problem either ... ":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    for c in "How about three hyphens - -":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Left, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Backspace, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Right, delay=keyDelay)
    for c in "- for long dash? It works too.":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "\"Full line double quoted text.\"":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "'Full line single quoted text.'":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
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
    projFile = os.path.join(nwFuncTemp, "nwProject.nwx")
    testFile = os.path.join(nwTempGUI, "1_nwProject.nwx")
    refFile  = os.path.join(nwRef, "gui", "1_nwProject.nwx")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [2, 6, 7, 8])

    projFile = os.path.join(nwFuncTemp, "content", "031b4af5197ec.nwd")
    testFile = os.path.join(nwTempGUI, "1_031b4af5197ec.nwd")
    refFile  = os.path.join(nwRef, "gui", "1_031b4af5197ec.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    projFile = os.path.join(nwFuncTemp, "content", "1a6562590ef19.nwd")
    testFile = os.path.join(nwTempGUI, "1_1a6562590ef19.nwd")
    refFile  = os.path.join(nwRef, "gui", "1_1a6562590ef19.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    projFile = os.path.join(nwFuncTemp, "content", "0e17daca5f3e1.nwd")
    testFile = os.path.join(nwTempGUI, "1_0e17daca5f3e1.nwd")
    refFile  = os.path.join(nwRef, "gui", "1_0e17daca5f3e1.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    projFile = os.path.join(nwFuncTemp, "content", "41cfc0d1f2d12.nwd")
    testFile = os.path.join(nwTempGUI, "1_41cfc0d1f2d12.nwd")
    refFile  = os.path.join(nwRef, "gui", "1_41cfc0d1f2d12.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    # qtbot.stopForInteraction()
    nwGUI.closeMain()
    nwGUI.close()

@pytest.mark.gui
def testDocViewer(qtbot, yesToAll, nwLipsum, nwTemp):

    nwGUI = nw.main(["--testmode", "--config=%s" % nwLipsum, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    # Open project
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.openProject(nwLipsum)

    # Rebuild the index as it isn't automatically copied
    assert nwGUI.theIndex.tagIndex == {}
    assert nwGUI.theIndex.refIndex == {}
    nwGUI.mainMenu.aRebuildIndex.activate(QAction.Trigger)
    assert nwGUI.theIndex.tagIndex != {}
    assert nwGUI.theIndex.refIndex != {}

    # Select a document in the project tree
    assert nwGUI.treeView.setSelectedHandle("88243afbe5ed8")

    # Middle-click the selected item
    theItem = nwGUI.treeView._getTreeItem("88243afbe5ed8")
    theRect = nwGUI.treeView.visualItemRect(theItem)
    qtbot.mouseClick(nwGUI.treeView.viewport(), Qt.MidButton, pos=theRect.center())
    assert nwGUI.docViewer.theHandle == "88243afbe5ed8"

    # Reload the text
    origText = nwGUI.docViewer.toPlainText()
    nwGUI.docViewer.setPlainText("Oops, all gone!")
    nwGUI.docViewer.docHeader._refreshDocument()
    assert nwGUI.docViewer.toPlainText() == origText

    # Cursor line
    assert not nwGUI.docViewer.setCursorLine("not a number")
    assert nwGUI.docViewer.setCursorLine(3)
    theCursor = nwGUI.docViewer.textCursor()
    assert theCursor.position() == 40

    # Cursor position
    assert not nwGUI.docViewer.setCursorPosition("not a number")
    assert nwGUI.docViewer.setCursorPosition(100)

    # Select word
    nwGUI.docViewer._makeSelection(QTextCursor.WordUnderCursor)

    qClip = qApp.clipboard()
    qClip.clear()

    # Cut
    assert nwGUI.docViewer.docAction(nwDocAction.CUT)
    assert qClip.text() == "laoreet"
    qClip.clear()

    # Copy
    assert nwGUI.docViewer.docAction(nwDocAction.COPY)
    assert qClip.text() == "laoreet"
    qClip.clear()

    # Select Paragraph
    assert nwGUI.docViewer.docAction(nwDocAction.SEL_PARA)
    theCursor = nwGUI.docViewer.textCursor()
    assert theCursor.selectedText() == (
        "Synopsis: Aenean ut placerat velit. Etiam laoreet ullamcorper risus, "
        "eget lobortis enim scelerisque non. Suspendisse id maximus nunc, et "
        "mollis sapien. Curabitur vel semper sapien, non pulvinar dolor. "
        "Etiam finibus nisi vel mi molestie consectetur."
    )

    # Select All
    assert nwGUI.docViewer.docAction(nwDocAction.SEL_ALL)
    theCursor = nwGUI.docViewer.textCursor()
    assert len(theCursor.selectedText()) == 3061

    # Other actions
    assert not nwGUI.docViewer.docAction(nwDocAction.NO_ACTION)

    # Close document
    nwGUI.docViewer.docHeader._closeDocument()
    assert nwGUI.docViewer.theHandle is None

    # Action on no document
    assert not nwGUI.docViewer.docAction(nwDocAction.COPY)

    # Open again via menu
    assert nwGUI.treeView.setSelectedHandle("88243afbe5ed8")
    nwGUI.mainMenu.aViewDoc.activate(QAction.Trigger)

    # Select "Bod" link
    assert nwGUI.docViewer.setCursorPosition(27)
    nwGUI.docViewer._makeSelection(QTextCursor.WordUnderCursor)
    theRect = nwGUI.docViewer.cursorRect()
    # qtbot.mouseClick(nwGUI.docViewer.viewport(), Qt.LeftButton, pos=theRect.center(), delay=100)
    nwGUI.docViewer._linkClicked(QUrl("#char=Bod"))
    assert nwGUI.docViewer.theHandle == "4c4f28287af27"

    # Click mouse nav buttons
    qtbot.mouseClick(nwGUI.docViewer.viewport(), Qt.BackButton, pos=theRect.center(), delay=100)
    assert nwGUI.docViewer.theHandle == "88243afbe5ed8"
    qtbot.mouseClick(nwGUI.docViewer.viewport(), Qt.ForwardButton, pos=theRect.center(), delay=100)
    assert nwGUI.docViewer.theHandle == "4c4f28287af27"

    # Scroll bar default on empty document
    nwGUI.docViewer.clear()
    assert nwGUI.docViewer.getScrollPosition() == 0
    nwGUI.docViewer.reloadText()

    # Change document title
    nwItem = nwGUI.theProject.projTree["4c4f28287af27"]
    nwItem.setName("Test Title")
    assert nwItem.itemName == "Test Title"
    nwGUI.docViewer.updateDocInfo("4c4f28287af27")
    assert nwGUI.docViewer.docHeader.theTitle.text() == "Characters  ›  Test Title"

    # Ttile without full path
    nwGUI.mainConf.showFullPath = False
    nwGUI.docViewer.updateDocInfo("4c4f28287af27")
    assert nwGUI.docViewer.docHeader.theTitle.text() == "Test Title"
    nwGUI.mainConf.showFullPath = True

    # Document footer show/hide references
    viewState = nwGUI.viewMeta.isVisible()
    nwGUI.docViewer.docFooter._doShowHide()
    assert nwGUI.viewMeta.isVisible() is not viewState
    nwGUI.docViewer.docFooter._doShowHide()
    assert nwGUI.viewMeta.isVisible() is viewState

    # Document footer sticky
    viewState = nwGUI.docViewer.stickyRef
    nwGUI.docViewer.docFooter._doToggleSticky(not viewState)
    assert nwGUI.docViewer.stickyRef is not viewState
    nwGUI.docViewer.docFooter._doToggleSticky(viewState)
    assert nwGUI.docViewer.stickyRef is viewState

    # Document footer show/hide synopsis
    assert nwGUI.viewDocument("f96ec11c6a3da")
    assert len(nwGUI.docViewer.toPlainText()) == 4315
    nwGUI.docViewer.docFooter._doToggleSynopsis(False)
    assert len(nwGUI.docViewer.toPlainText()) == 4099

    # Document footer show/hide comments
    assert nwGUI.viewDocument("846352075de7d")
    assert len(nwGUI.docViewer.toPlainText()) == 675
    nwGUI.docViewer.docFooter._doToggleComments(False)
    assert len(nwGUI.docViewer.toPlainText()) == 635

    # qtbot.stopForInteraction()
    nwGUI.closeMain()
    nwGUI.close()

@pytest.mark.gui
def testProjectTree(qtbot, yesToAll, nwMinimal, nwTemp):

    nwGUI = nw.main(["--testmode", "--config=%s" % nwMinimal, "--data=%s" % nwTemp, nwMinimal])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    nwGUI.theProject.projTree.setSeed(42)
    nwTree = nwGUI.treeView

    # No location selected for new item
    assert not nwTree.newTreeItem(nwItemType.FILE, None)
    assert not nwTree.newTreeItem(nwItemType.FOLDER, None)

    # Select a location
    chItem = nwTree._getTreeItem("a6d311a93600a")
    nwTree.setCurrentItem(chItem, QItemSelectionModel.Current)
    chItem.setExpanded(True)

    # Create new item with no class set
    assert nwTree.newTreeItem(nwItemType.FILE, None)
    assert nwTree.newTreeItem(nwItemType.FOLDER, None)

    # Add roots
    assert not nwTree.newTreeItem(nwItemType.ROOT, None)              # Defaults to NOVEL
    assert not nwTree.newTreeItem(nwItemType.ROOT, nwItemClass.WORLD) # Duplicate
    assert nwTree.newTreeItem(nwItemType.ROOT, nwItemClass.CUSTOM)    # Valid

    # Check that we have the correct tree order
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "f5ab3e30151e1", "8c659a11cd429", "73475cb40a568", "44cb730c42048"
    ]

    # Move second item up twice (should give same result)
    nwTree.setSelectedHandle("8c659a11cd429")
    nwGUI.mainMenu.aMoveUp.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "8c659a11cd429", "f5ab3e30151e1", "73475cb40a568", "44cb730c42048"
    ]
    nwGUI.mainMenu.aMoveUp.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "8c659a11cd429", "f5ab3e30151e1", "73475cb40a568", "44cb730c42048"
    ]

    # Move it back down four times (last to should be the same)
    nwGUI.mainMenu.aMoveDown.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "f5ab3e30151e1", "8c659a11cd429", "73475cb40a568", "44cb730c42048"
    ]
    nwGUI.mainMenu.aMoveDown.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "f5ab3e30151e1", "73475cb40a568", "8c659a11cd429", "44cb730c42048"
    ]
    nwGUI.mainMenu.aMoveDown.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "f5ab3e30151e1", "73475cb40a568", "44cb730c42048", "8c659a11cd429"
    ]
    nwGUI.mainMenu.aMoveDown.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "f5ab3e30151e1", "73475cb40a568", "44cb730c42048", "8c659a11cd429"
    ]

    # Move a root item (top level items are different) twice
    nwTree.flushTreeOrder()
    assert nwGUI.theProject.projTree._treeOrder.index("9d5247ab588e0") == 9
    nwTree.setSelectedHandle("9d5247ab588e0")

    nwGUI.mainMenu.aMoveDown.activate(QAction.Trigger)
    nwTree.flushTreeOrder()
    assert nwGUI.theProject.projTree._treeOrder.index("9d5247ab588e0") == 10

    nwGUI.mainMenu.aMoveDown.activate(QAction.Trigger)
    nwTree.flushTreeOrder()
    assert nwGUI.theProject.projTree._treeOrder.index("9d5247ab588e0") == 10

    # Add some content to the new file
    nwGUI.openDocument("73475cb40a568")
    nwGUI.docEditor.setText("# Hello World\n")
    nwGUI.saveDocument()
    assert os.path.isfile(os.path.join(nwMinimal, "content", "73475cb40a568.nwd"))

    # Delete the items we added earlier
    nwTree.clearSelection()
    assert not nwTree.emptyTrash() # No folder yet
    assert not nwTree.deleteItem(None)
    assert not nwTree.deleteItem("1111111111111")
    assert nwTree.deleteItem("73475cb40a568") # New File
    assert nwTree.deleteItem("44cb730c42048") # New Folder
    assert nwTree.deleteItem("71ee45a3c0db9") # Custom Root
    assert "73475cb40a568" in nwGUI.theProject.projTree._treeOrder
    assert "44cb730c42048" not in nwGUI.theProject.projTree._treeOrder
    assert "71ee45a3c0db9" not in nwGUI.theProject.projTree._treeOrder

    # The file is in trash, empty it
    assert os.path.isfile(os.path.join(nwMinimal, "content", "73475cb40a568.nwd"))
    assert nwTree.emptyTrash()
    assert not nwTree.emptyTrash() # Already empty
    assert not os.path.isfile(os.path.join(nwMinimal, "content", "73475cb40a568.nwd"))
    assert "73475cb40a568" not in nwGUI.theProject.projTree._treeOrder

    # Close the project
    nwGUI.closeProject()

    # Add an orphaned file
    orphFile = os.path.join(nwMinimal, "content", "1234567890abc.nwd")
    with open(orphFile, mode="w+", encoding="utf8") as outFile:
        outFile.write("# Hello World\n")

    # Open the project again
    nwGUI.openProject(nwMinimal)

    # Check that the orphaned file was found and added to the tree
    assert nwTree.orphRoot is not None
    nwTree.flushTreeOrder()
    assert "1234567890abc" not in nwGUI.theProject.projTree._treeOrder
    orItem = nwTree._getTreeItem("1234567890abc")
    assert orItem.text(nwTree.C_NAME) == "Orphaned File 1"

    # Move it to the Plot folder
    # plItem = nwTree._getTreeItem("7695ce551d265")
    # orRect = nwTree.visualItemRect(orItem)
    # plRect = nwTree.visualItemRect(plItem)

    # qtbot.mouseMove(nwTree.viewport(), pos=orRect.center(), delay=1000)
    # qtbot.mousePress(nwTree.viewport(), Qt.LeftButton, pos=orRect.center(), delay=1000)
    # qtbot.mouseMove(nwTree.viewport(), pos=plRect.center(), delay=1000)
    # qtbot.mouseRelease(nwTree.viewport(), Qt.LeftButton, pos=plRect.center(), delay=1000)

    # qtbot.stopForInteraction()
    nwGUI.closeMain()
    nwGUI.close()

@pytest.mark.gui
def testEditFormatMenu(qtbot, yesToAll, nwLipsum, nwTemp):

    nwGUI = nw.main(["--testmode", "--config=%s" % nwLipsum, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    # Test Document Action with No Project
    assert not nwGUI.docEditor.docAction(nwDocAction.COPY)

    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.openProject(nwLipsum)
    qtbot.wait(stepDelay)

    # Split By Chapter
    assert nwGUI.openDocument("4c4f28287af27")
    assert nwGUI.docEditor.setCursorPosition(30)

    cleanText = nwGUI.docEditor.getText()[27:74]

    # Bold
    nwGUI.mainMenu.aFmtStrong.activate(QAction.Trigger)
    fmtStr = "**Pellentesque** nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:78] == fmtStr
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aFmtStrong.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Italic
    nwGUI.mainMenu.aFmtEmph.activate(QAction.Trigger)
    fmtStr = "_Pellentesque_ nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:76] == fmtStr
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aFmtEmph.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Strikethrough
    nwGUI.mainMenu.aFmtStrike.activate(QAction.Trigger)
    fmtStr = "~~Pellentesque~~ nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:78] == fmtStr
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aFmtStrike.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Should get us back to plain
    nwGUI.mainMenu.aFmtStrong.activate(QAction.Trigger)
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aFmtEmph.activate(QAction.Trigger)
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aFmtEmph.activate(QAction.Trigger)
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aFmtStrong.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Double Quotes
    nwGUI.mainMenu.aFmtDQuote.activate(QAction.Trigger)
    fmtStr = "“Pellentesque” nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:76] == fmtStr
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aEditUndo.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Single Quotes
    nwGUI.mainMenu.aFmtSQuote.activate(QAction.Trigger)
    fmtStr = "‘Pellentesque’ nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:76] == fmtStr
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aEditUndo.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Block Formats
    assert nwGUI.docEditor.setCursorPosition(30)
    nwGUI.mainMenu.aFmtHead1.activate(QAction.Trigger)
    fmtStr = "# Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:76] == fmtStr
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aFmtHead2.activate(QAction.Trigger)
    fmtStr = "## Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:77] == fmtStr
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aFmtHead3.activate(QAction.Trigger)
    fmtStr = "### Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:78] == fmtStr
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aFmtHead4.activate(QAction.Trigger)
    fmtStr = "#### Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:79] == fmtStr
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aFmtNoFormat.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aFmtComment.activate(QAction.Trigger)
    fmtStr = "% Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:76] == fmtStr
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aFmtNoFormat.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Check comment with no space before text
    assert nwGUI.docEditor.setCursorPosition(27)
    assert nwGUI.docEditor.insertText("%")
    fmtStr = "%Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:75] == fmtStr
    qtbot.wait(stepDelay)

    nwGUI.mainMenu.aFmtNoFormat.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Undo/Redo
    nwGUI.mainMenu.aEditUndo.activate(QAction.Trigger)
    fmtStr = "%Pellentesque nec erat ut nulla posuere commodo."
    assert nwGUI.docEditor.getText()[27:75] == fmtStr
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aEditRedo.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:74] == cleanText
    qtbot.wait(stepDelay)

    # Cut, Copy and Paste
    assert nwGUI.docEditor.setCursorPosition(27)
    nwGUI.docEditor._makeSelection(QTextCursor.WordUnderCursor)

    nwGUI.mainMenu.aEditCut.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:77] == (
        " nec erat ut nulla posuere commodo. Curabitur nisi"
    )

    nwGUI.mainMenu.aEditPaste.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:77] == (
        "Pellentesque nec erat ut nulla posuere commodo. Cu"
    )

    assert nwGUI.docEditor.setCursorPosition(27)
    nwGUI.docEditor._makeSelection(QTextCursor.WordUnderCursor)

    nwGUI.mainMenu.aEditCopy.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:77] == (
        "Pellentesque nec erat ut nulla posuere commodo. Cu"
    )

    assert nwGUI.docEditor.setCursorPosition(27)
    nwGUI.mainMenu.aEditPaste.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[27:77] == (
        "PellentesquePellentesque nec erat ut nulla posuere"
    )
    nwGUI.mainMenu.aEditUndo.activate(QAction.Trigger)

    # Select Paragraph/All
    assert nwGUI.docEditor.setCursorPosition(30)
    nwGUI.mainMenu.aSelectPar.activate(QAction.Trigger)
    theCursor = nwGUI.docEditor.textCursor()
    assert theCursor.selectedText() == (
        "Pellentesque nec erat ut nulla posuere commodo. Curabitur nisi augue, imperdiet et porta "
        "imperdiet, efficitur id leo. Cras finibus arcu at nibh commodo congue. Proin suscipit "
        "placerat condimentum. Aenean ante enim, cursus id lorem a, blandit venenatis nibh. "
        "Maecenas suscipit porta elit, sit amet porta felis porttitor eu. Sed a dui nibh. "
        "Phasellus sed faucibus dui. Pellentesque felis nulla, ultrices non efficitur quis, "
        "rutrum id mi. Mauris tempus auctor nisl, in bibendum enim pellentesque sit amet. Proin "
        "nunc lacus, imperdiet nec posuere ac, interdum non lectus."
    )

    assert nwGUI.docEditor.setCursorPosition(30)
    nwGUI.mainMenu.aSelectAll.activate(QAction.Trigger)
    theCursor = nwGUI.docEditor.textCursor()
    assert len(theCursor.selectedText()) == 1883

    # Clear the Text
    nwGUI.docEditor.clear()
    assert nwGUI.docEditor.isEmpty()

    # Replace Quotes
    nwGUI.docEditor.setText((
        "### New Text\n\n"
        "Text with 'single' quotes and 'tricky stuff's'.\n\n"
        "Also text with \"double\" quotes which are \"less tricky\".\n\n"
    ))

    nwGUI.mainMenu.aSelectAll.activate(QAction.Trigger)
    nwGUI.mainMenu.aFmtReplSng.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == (
        "### New Text\n\n"
        "Text with ‘single’ quotes and ‘tricky stuff’s’.\n\n"
        "Also text with \"double\" quotes which are \"less tricky\".\n\n"
    )

    nwGUI.mainMenu.aSelectAll.activate(QAction.Trigger)
    nwGUI.mainMenu.aFmtReplDbl.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == (
        "### New Text\n\n"
        "Text with ‘single’ quotes and ‘tricky stuff’s’.\n\n"
        "Also text with “double” quotes which are “less tricky”.\n\n"
    )

    # Test Invalid Document Action
    assert not nwGUI.docEditor.docAction(nwDocAction.NO_ACTION)

    # Test Invalid Formats
    nwGUI.docEditor.setText((
        "### New Text\n\n"
        "@tag: Bod\n\n"
        "Text with 'single' quotes and 'tricky stuff's'.\n\n"
        "Also text with \"double\" quotes which are \"less tricky\".\n\n"
    ))

    # Cannot Format Tag
    assert nwGUI.docEditor.setCursorPosition(17)
    assert not nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT)

    # Cannot Format Empty Line
    assert nwGUI.docEditor.setCursorPosition(13)
    assert not nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT)

    # Invalid Action
    assert nwGUI.docEditor.setCursorPosition(30)
    assert not nwGUI.docEditor._formatBlock(nwDocAction.NO_ACTION)

    # Ensure No Changes
    assert nwGUI.docEditor.getText() == (
        "### New Text\n\n"
        "@tag: Bod\n\n"
        "Text with 'single' quotes and 'tricky stuff's'.\n\n"
        "Also text with \"double\" quotes which are \"less tricky\".\n\n"
    )

    # qtbot.stopForInteraction()
    nwGUI.closeMain()
    nwGUI.close()

@pytest.mark.gui
def testContextMenu(qtbot, yesToAll, nwLipsum, nwTemp):

    nwGUI = nw.main(["--testmode", "--config=%s" % nwLipsum, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.openProject(nwLipsum)
    assert nwGUI.openDocument("4c4f28287af27")
    qtbot.wait(stepDelay)

    # Editor Context Menu
    theCursor = nwGUI.docEditor.textCursor()
    theCursor.setPosition(100)
    nwGUI.docEditor.setTextCursor(theCursor)
    theRect = nwGUI.docEditor.cursorRect()

    nwGUI.docEditor._openContextMenu(theRect.bottomRight())
    qtbot.mouseClick(nwGUI.docEditor, Qt.LeftButton, pos=theRect.topLeft())

    nwGUI.docEditor._makePosSelection(QTextCursor.WordUnderCursor, theRect.center())
    theCursor = nwGUI.docEditor.textCursor()
    assert theCursor.selectedText() == "imperdiet"

    nwGUI.docEditor._makePosSelection(QTextCursor.BlockUnderCursor, theRect.center())
    theCursor = nwGUI.docEditor.textCursor()
    assert theCursor.selectedText() == (
        "Pellentesque nec erat ut nulla posuere commodo. Curabitur nisi augue, imperdiet et porta "
        "imperdiet, efficitur id leo. Cras finibus arcu at nibh commodo congue. Proin suscipit "
        "placerat condimentum. Aenean ante enim, cursus id lorem a, blandit venenatis nibh. "
        "Maecenas suscipit porta elit, sit amet porta felis porttitor eu. Sed a dui nibh. "
        "Phasellus sed faucibus dui. Pellentesque felis nulla, ultrices non efficitur quis, "
        "rutrum id mi. Mauris tempus auctor nisl, in bibendum enim pellentesque sit amet. Proin "
        "nunc lacus, imperdiet nec posuere ac, interdum non lectus."
    )

    # Viewer Context Menu
    assert nwGUI.viewDocument("4c4f28287af27")

    theCursor = nwGUI.docViewer.textCursor()
    theCursor.setPosition(100)
    nwGUI.docViewer.setTextCursor(theCursor)
    theRect = nwGUI.docViewer.cursorRect()

    nwGUI.docViewer._openContextMenu(theRect.bottomRight())
    qtbot.mouseClick(nwGUI.docViewer, Qt.LeftButton, pos=theRect.topLeft())

    nwGUI.docViewer._makePosSelection(QTextCursor.WordUnderCursor, theRect.center())
    theCursor = nwGUI.docViewer.textCursor()
    assert theCursor.selectedText() == "imperdiet"

    nwGUI.docEditor._makePosSelection(QTextCursor.BlockUnderCursor, theRect.center())
    theCursor = nwGUI.docEditor.textCursor()
    assert theCursor.selectedText() == (
        "Pellentesque nec erat ut nulla posuere commodo. Curabitur nisi augue, imperdiet et porta "
        "imperdiet, efficitur id leo. Cras finibus arcu at nibh commodo congue. Proin suscipit "
        "placerat condimentum. Aenean ante enim, cursus id lorem a, blandit venenatis nibh. "
        "Maecenas suscipit porta elit, sit amet porta felis porttitor eu. Sed a dui nibh. "
        "Phasellus sed faucibus dui. Pellentesque felis nulla, ultrices non efficitur quis, "
        "rutrum id mi. Mauris tempus auctor nisl, in bibendum enim pellentesque sit amet. Proin "
        "nunc lacus, imperdiet nec posuere ac, interdum non lectus."
    )

    # Navigation History
    assert nwGUI.viewDocument("04468803b92e1")
    assert nwGUI.docViewer.theHandle == "04468803b92e1"
    assert nwGUI.docViewer.docHeader.backButton.isEnabled()
    assert not nwGUI.docViewer.docHeader.forwardButton.isEnabled()

    qtbot.mouseClick(nwGUI.docViewer.docHeader.backButton, Qt.LeftButton)
    assert nwGUI.docViewer.theHandle == "4c4f28287af27"
    assert not nwGUI.docViewer.docHeader.backButton.isEnabled()
    assert nwGUI.docViewer.docHeader.forwardButton.isEnabled()

    qtbot.mouseClick(nwGUI.docViewer.docHeader.forwardButton, Qt.LeftButton)
    assert nwGUI.docViewer.theHandle == "04468803b92e1"
    assert nwGUI.docViewer.docHeader.backButton.isEnabled()
    assert not nwGUI.docViewer.docHeader.forwardButton.isEnabled()

    # qtbot.stopForInteraction()
    nwGUI.closeMain()
    nwGUI.close()

@pytest.mark.gui
def testInsertMenu(qtbot, monkeypatch, nwFuncTemp, nwTemp):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwTemp, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": nwFuncTemp})

    assert nwGUI.treeView._getTreeItem("0e17daca5f3e1") is not None

    nwGUI.setFocus(1)
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem("0e17daca5f3e1").setSelected(True)
    assert nwGUI.openSelectedItem()
    nwGUI.docEditor.clear()

    # Test Faulty Inserts
    assert nwGUI.docEditor.insertText("hello world")
    assert nwGUI.docEditor.getText() == "hello world"
    nwGUI.docEditor.clear()

    assert not nwGUI.docEditor.insertText(nwDocInsert.NO_INSERT)
    assert nwGUI.docEditor.isEmpty()

    assert not nwGUI.docEditor.insertText(None)
    assert nwGUI.docEditor.isEmpty()

    # qtbot.stopForInteraction()

    # Check Menu Entries
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

    ##
    #  Insert text from file
    ##
    nwGUI.closeDocument()

    # First, with no path
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args, **kwards: ("", ""))
    assert not nwGUI.importDocument()

    # Then with a path, but an invalid one
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args, **kwards: (" ", ""))
    assert not nwGUI.importDocument()

    # Then a valid path, but bot a file that exists
    theFile = os.path.join(nwTemp, "import.txt")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args, **kwards: (theFile, ""))
    assert not nwGUI.importDocument()

    # Create the file and try again, but with no target document open
    with open(theFile, mode="w+", encoding="utf8") as outFile:
        outFile.write("Foo")
    assert not nwGUI.importDocument()

    # Open the document from before, and add some text to it
    nwGUI.openDocument("0e17daca5f3e1")
    nwGUI.docEditor.setText("Bar")
    assert nwGUI.docEditor.getText() == "Bar"

    # The document isn't empty, so the message box should pop
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.No)
    assert not nwGUI.importDocument()
    assert nwGUI.docEditor.getText() == "Bar"

    # Finally, accept the replaced text, this time we use the menu entry to trigger it
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.Yes)
    nwGUI.mainMenu.aImportFile.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText() == "Foo"

    ##
    #  Reveal file location
    ##

    theMessage = ""

    def recordMsg(*args):
        nonlocal theMessage
        theMessage = args[3]
        return None

    assert not theMessage
    monkeypatch.setattr(QMessageBox, "information", recordMsg)
    nwGUI.mainMenu.aFileDetails.activate(QAction.Trigger)

    theBits = theMessage.split("<br>")
    assert len(theBits) == 3
    assert theBits[0] == "File details for the currently open file"
    assert theBits[1] == "Handle: 0e17daca5f3e1"
    assert theBits[2] == "Location: %s" % os.path.join(nwFuncTemp, "content", "0e17daca5f3e1.nwd")

    # qtbot.stopForInteraction()
    nwGUI.closeMain()
    nwGUI.close()

@pytest.mark.gui
def testTextSearch(qtbot, monkeypatch, yesToAll, nwLipsum, nwTemp):

    nwGUI = nw.main(["--testmode", "--config=%s" % nwLipsum, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.openProject(nwLipsum)
    assert nwGUI.openDocument("4c4f28287af27")
    origText = nwGUI.docEditor.getText()
    qtbot.wait(stepDelay)

    # Select the Word "est"
    assert nwGUI.docEditor.setCursorPosition(618)
    nwGUI.docEditor._makeSelection(QTextCursor.WordUnderCursor)
    theCursor = nwGUI.docEditor.textCursor()
    assert theCursor.selectedText() == "est"

    # Activate Search
    nwGUI.mainMenu.aFind.activate(QAction.Trigger)
    assert nwGUI.docEditor.docSearch.isVisible()
    assert nwGUI.docEditor.docSearch.getSearchText() == "est"

    # Find Next by Enter
    monkeypatch.setattr(nwGUI.docEditor.docSearch.searchBox, "hasFocus", lambda: True)
    qtbot.keyClick(nwGUI.docEditor.docSearch.searchBox, Qt.Key_Return, delay=keyDelay)
    assert abs(nwGUI.docEditor.getCursorPosition() - 1272) < 3

    # Find Next by Button
    qtbot.mouseClick(nwGUI.docEditor.docSearch.searchButton, Qt.LeftButton, delay=keyDelay)
    assert abs(nwGUI.docEditor.getCursorPosition() - 1486) < 3

    # Activate Loop Search
    nwGUI.docEditor.docSearch.toggleLoop.activate(QAction.Trigger)
    assert nwGUI.docEditor.docSearch.toggleLoop.isChecked()
    assert nwGUI.docEditor.docSearch.doLoop

    # Find Next by Menu Search > Find Next
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 620) < 3

    # Close Search
    nwGUI.docEditor.docSearch.cancelSearch.activate(QAction.Trigger)
    assert not nwGUI.docEditor.docSearch.isVisible()
    assert nwGUI.docEditor.setCursorPosition(15)

    # Toggle Search Again with Header Button
    qtbot.mouseClick(nwGUI.docEditor.docHeader.searchButton, Qt.LeftButton, delay=keyDelay)
    assert nwGUI.docEditor.docSearch.setSearchText("")
    assert nwGUI.docEditor.docSearch.isVisible()

    # Enable RegEx Search
    nwGUI.docEditor.docSearch.toggleRegEx.activate(QAction.Trigger)
    assert nwGUI.docEditor.docSearch.toggleRegEx.isChecked()
    assert nwGUI.docEditor.docSearch.isRegEx

    # Set Invalid RegEx
    assert nwGUI.docEditor.docSearch.setSearchText(r"\bSus[")
    qtbot.mouseClick(nwGUI.docEditor.docSearch.searchButton, Qt.LeftButton, delay=keyDelay)
    assert nwGUI.docEditor.getCursorPosition() < 3 # No result

    # Set Valid RegEx
    assert nwGUI.docEditor.docSearch.setSearchText(r"\bSus")
    qtbot.mouseClick(nwGUI.docEditor.docSearch.searchButton, Qt.LeftButton, delay=keyDelay)
    assert abs(nwGUI.docEditor.getCursorPosition() - 196) < 3

    # Find Next and then Prev
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 297) < 3
    nwGUI.mainMenu.aFindPrev.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 196) < 3

    # Make RegEx Case Sensitive
    nwGUI.docEditor.docSearch.toggleCase.activate(QAction.Trigger)
    assert nwGUI.docEditor.docSearch.toggleCase.isChecked()
    assert nwGUI.docEditor.docSearch.isCaseSense

    # Find Next (One Result)
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 599) < 3
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 599) < 3

    # Trigger Replace
    nwGUI.mainMenu.aReplace.activate(QAction.Trigger)
    assert nwGUI.docEditor.docSearch.setReplaceText("foo")

    # Disable RegEx Case Sensitive
    nwGUI.docEditor.docSearch.toggleCase.activate(QAction.Trigger)
    assert not nwGUI.docEditor.docSearch.toggleCase.isChecked()
    assert not nwGUI.docEditor.docSearch.isCaseSense

    # Toggle Replace Preserve Case
    nwGUI.docEditor.docSearch.toggleMatchCap.activate(QAction.Trigger)
    assert nwGUI.docEditor.docSearch.toggleMatchCap.isChecked()
    assert nwGUI.docEditor.docSearch.doMatchCap

    # Replace "Sus" with "Foo" via Menu
    nwGUI.mainMenu.aReplaceNext.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[596:607] == "Foopendisse"

    # Find Next to Loop File
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)

    # Replace "sus" with "foo" via Replace Button
    qtbot.mouseClick(nwGUI.docEditor.docSearch.replaceButton, Qt.LeftButton, delay=keyDelay)
    assert nwGUI.docEditor.getText()[193:201] == "foocipit"

    # Revert Last Two Replaces
    assert nwGUI.docEditor.docAction(nwDocAction.UNDO)
    assert nwGUI.docEditor.docAction(nwDocAction.UNDO)
    assert nwGUI.docEditor.getText() == origText

    # Disable RegEx Search
    nwGUI.docEditor.docSearch.toggleRegEx.activate(QAction.Trigger)
    assert not nwGUI.docEditor.docSearch.toggleRegEx.isChecked()
    assert not nwGUI.docEditor.docSearch.isRegEx

    # Close Search and Select "est" Again
    nwGUI.docEditor.docSearch.cancelSearch.activate(QAction.Trigger)
    assert nwGUI.docEditor.setCursorPosition(618)
    nwGUI.docEditor._makeSelection(QTextCursor.WordUnderCursor)
    theCursor = nwGUI.docEditor.textCursor()
    assert theCursor.selectedText() == "est"

    # Activate Search Again
    nwGUI.mainMenu.aFind.activate(QAction.Trigger)
    assert nwGUI.docEditor.docSearch.isVisible()
    assert nwGUI.docEditor.docSearch.getSearchText() == "est"

    # Enable Full Word Search
    nwGUI.docEditor.docSearch.toggleWord.activate(QAction.Trigger)
    assert nwGUI.docEditor.docSearch.toggleWord.isChecked()
    assert nwGUI.docEditor.docSearch.isWholeWord

    # Only One Match
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 620) < 3
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 620) < 3

    # Enable Next Doc Search
    nwGUI.docEditor.docSearch.toggleProject.activate(QAction.Trigger)
    assert nwGUI.docEditor.docSearch.toggleProject.isChecked()
    assert nwGUI.docEditor.docSearch.doNextFile

    # Next Match
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert nwGUI.docEditor.theHandle == "2426c6f0ca922" # Next document
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 620) < 3
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 1127) < 3

    # Toggle Replace
    nwGUI.docEditor._beginReplace()

    # MonkeyPatch the focus cycle. We can't really test this very well, other than
    # check that the tabs aren't captured when the main editor has focus
    monkeypatch.setattr(nwGUI.docEditor, "hasFocus", lambda: True)
    monkeypatch.setattr(nwGUI.docEditor.docSearch.searchBox, "hasFocus", lambda: False)
    monkeypatch.setattr(nwGUI.docEditor.docSearch.replaceBox, "hasFocus", lambda: False)
    assert not nwGUI.docEditor.focusNextPrevChild(True)

    monkeypatch.setattr(nwGUI.docEditor, "hasFocus", lambda: False)
    monkeypatch.setattr(nwGUI.docEditor.docSearch.searchBox, "hasFocus", lambda: True)
    monkeypatch.setattr(nwGUI.docEditor.docSearch.replaceBox, "hasFocus", lambda: False)
    assert nwGUI.docEditor.focusNextPrevChild(True)

    monkeypatch.setattr(nwGUI.docEditor.docSearch.searchBox, "hasFocus", lambda: False)
    monkeypatch.setattr(nwGUI.docEditor.docSearch.replaceBox, "hasFocus", lambda: True)
    assert nwGUI.docEditor.focusNextPrevChild(True)

    # qtbot.stopForInteraction()
    nwGUI.closeMain()
    nwGUI.close()

@pytest.mark.gui
def testOutline(qtbot, yesToAll, nwLipsum, nwTemp):

    nwGUI = nw.main(["--testmode", "--config=%s" % nwLipsum, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    assert nwGUI.openProject(nwLipsum)
    nwGUI.mainConf.lastPath = nwLipsum

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

    assert nwGUI.projMeta.cCValue.text() == "230"
    assert nwGUI.projMeta.wCValue.text() == "40"
    assert nwGUI.projMeta.pCValue.text() == "3"

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
    nwGUI.close()

@pytest.mark.gui
def testThemes(qtbot, yesToAll, nwMinimal, nwTemp):

    nwGUI = nw.main(["--testmode", "--config=%s" % nwMinimal, "--data=%s" % nwTemp, nwMinimal])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(500)

    # Change Settings
    assert nw.CONFIG.confPath == nwMinimal
    nw.CONFIG.guiTheme = "default_dark"
    nw.CONFIG.guiSyntax = "tomorrow_night_eighties"
    nw.CONFIG.guiIcons = "typicons_colour_dark"
    nw.CONFIG.guiDark = True
    nw.CONFIG.guiFont = "Cantarell"
    nw.CONFIG.guiFontSize = 11
    nw.CONFIG.confChanged = True
    assert nw.CONFIG.saveConfig()

    nwGUI.closeMain()
    nwGUI.close()
    del nwGUI

    # Re-open
    assert nw.CONFIG.confPath == nwMinimal
    nwGUI = nw.main(["--testmode", "--config=%s" % nwMinimal, "--data=%s" % nwTemp, nwMinimal])
    assert nwGUI.mainConf.confPath == nwMinimal
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(500)

    assert nw.CONFIG.guiTheme == "default_dark"
    assert nw.CONFIG.guiSyntax == "tomorrow_night_eighties"
    assert nw.CONFIG.guiIcons == "typicons_colour_dark"
    assert nw.CONFIG.guiDark is True
    assert nw.CONFIG.guiFont == "Cantarell"
    assert nw.CONFIG.guiFontSize == 11

    # Check GUI Colours
    thePalette = nwGUI.palette()
    assert thePalette.window().color()          == QColor(54, 54, 54)
    assert thePalette.windowText().color()      == QColor(174, 174, 174)
    assert thePalette.base().color()            == QColor(62, 62, 62)
    assert thePalette.alternateBase().color()   == QColor(67, 67, 67)
    assert thePalette.text().color()            == QColor(174, 174, 174)
    assert thePalette.toolTipBase().color()     == QColor(255, 255, 192)
    assert thePalette.toolTipText().color()     == QColor(21, 21, 13)
    assert thePalette.button().color()          == QColor(62, 62, 62)
    assert thePalette.buttonText().color()      == QColor(174, 174, 174)
    assert thePalette.brightText().color()      == QColor(174, 174, 174)
    assert thePalette.highlight().color()       == QColor(44, 152, 247)
    assert thePalette.highlightedText().color() == QColor(255, 255, 255)
    assert thePalette.link().color()            == QColor(44, 152, 247)
    assert thePalette.linkVisited().color()     == QColor(44, 152, 247)

    assert nwGUI.theTheme.treeWCount  == [197, 200, 198]
    assert nwGUI.theTheme.statNone    == [150, 152, 150]
    assert nwGUI.theTheme.statSaved   == [39, 135, 78]
    assert nwGUI.theTheme.statUnsaved == [138, 32, 32]

    # Check Syntax Colours
    assert nwGUI.theTheme.colBack   == [45, 45, 45]
    assert nwGUI.theTheme.colText   == [204, 204, 204]
    assert nwGUI.theTheme.colLink   == [102, 153, 204]
    assert nwGUI.theTheme.colHead   == [102, 153, 204]
    assert nwGUI.theTheme.colHeadH  == [102, 153, 204]
    assert nwGUI.theTheme.colEmph   == [249, 145, 57]
    assert nwGUI.theTheme.colDialN  == [242, 119, 122]
    assert nwGUI.theTheme.colDialD  == [153, 204, 153]
    assert nwGUI.theTheme.colDialS  == [255, 204, 102]
    assert nwGUI.theTheme.colComm   == [153, 153, 153]
    assert nwGUI.theTheme.colKey    == [242, 119, 122]
    assert nwGUI.theTheme.colVal    == [204, 153, 204]
    assert nwGUI.theTheme.colSpell  == [242, 119, 122]
    assert nwGUI.theTheme.colTagErr == [153, 204, 153]
    assert nwGUI.theTheme.colRepTag == [102, 204, 204]
    assert nwGUI.theTheme.colMod    == [249, 145, 57]

    # Test Icon class
    theIcons = nwGUI.theTheme.theIcons
    nw.CONFIG.guiIcons = "invalid"
    assert not theIcons.updateTheme()
    nw.CONFIG.guiIcons = "typicons_colour_dark"
    assert theIcons.updateTheme()

    # Ask for a non-existent key
    anImg = theIcons.loadDecoration("nonsense", 20, 20)
    assert isinstance(anImg, QPixmap)
    assert anImg.isNull()

    # Add a non-existent file and request it
    theIcons.DECO_MAP["nonsense"] = "nofile.jpg"
    anImg = theIcons.loadDecoration("nonsense", 20, 20)
    assert isinstance(anImg, QPixmap)
    assert anImg.isNull()

    # Get a real image, with different size parameters
    anImg = theIcons.loadDecoration("wiz-back", 20, None)
    assert isinstance(anImg, QPixmap)
    assert not anImg.isNull()
    assert anImg.width() == 20
    assert anImg.height() >= 56

    anImg = theIcons.loadDecoration("wiz-back", None, 70)
    assert isinstance(anImg, QPixmap)
    assert not anImg.isNull()
    assert anImg.height() == 70
    assert anImg.width() >= 24

    anImg = theIcons.loadDecoration("wiz-back", 30, 70)
    assert isinstance(anImg, QPixmap)
    assert not anImg.isNull()
    assert anImg.height() == 70
    assert anImg.width() == 30

    anImg = theIcons.loadDecoration("wiz-back", None, None)
    assert isinstance(anImg, QPixmap)
    assert not anImg.isNull()
    assert anImg.height() >= 1500
    assert anImg.width() >= 500

    # Load icons
    anIcon = theIcons.getIcon("nonsense")
    assert isinstance(anIcon, QIcon)
    assert anIcon.isNull()

    anIcon = theIcons.getIcon("novelwriter")
    assert isinstance(anIcon, QIcon)
    assert not anIcon.isNull()

    # Add dummy icons and test alternative load paths
    theIcons.ICON_MAP["testicon1"] = (QStyle.SP_DriveHDIcon, None)
    anIcon = theIcons.getIcon("testicon1")
    assert isinstance(anIcon, QIcon)
    assert not anIcon.isNull()

    theIcons.ICON_MAP["testicon2"] = (None, "folder")
    anIcon = theIcons.getIcon("testicon2")
    assert isinstance(anIcon, QIcon)

    theIcons.ICON_MAP["testicon3"] = (None, None)
    anIcon = theIcons.getIcon("testicon3")
    assert isinstance(anIcon, QIcon)
    assert anIcon.isNull()

    # qtbot.stopForInteraction()
    nwGUI.closeMain()
    nwGUI.close()
