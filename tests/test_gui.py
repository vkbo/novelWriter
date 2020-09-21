# -*- coding: utf-8 -*-
"""novelWriter Main GUI Class Tester
"""

import nw
import pytest
from shutil import copyfile
from nwtools import cmpFiles

from os import path
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QAction, QTreeWidgetItem

from nw.constants import nwItemType, nwUnicode, nwOutline, nwDocAction, nwDocInsert

keyDelay = 2
stepDelay = 20

@pytest.mark.gui
def testMainWindow(qtbot, nwFuncTemp, nwTempGUI, nwRef, nwTemp):

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
    projFile = path.join(nwFuncTemp, "nwProject.nwx")
    testFile = path.join(nwTempGUI, "0_nwProject.nwx")
    refFile  = path.join(nwRef, "gui", "0_nwProject.nwx")
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
    assert nwGUI.theProject.projMeta == path.join(nwFuncTemp, "meta")
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
    for c in "We can also try replacing \"quotes\", even single 'quotes' are replaced. ":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    for c in "Isn't that nice? ":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    for c in "We can hyphen-ate, make dashes -- and even longer dashes --- if we want. ":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    for c in "Ellipsis? Not a problem either ... ":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    for c in "How about three hyphens - -":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Left, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Backspace, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Right, delay=keyDelay)
    for c in "- for long dash? It works too.":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "\"Full line double quoted text.\"":
        qtbot.keyClick(nwGUI.docEditor, c, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "'Full line single quoted text.'":
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
    projFile = path.join(nwFuncTemp, "nwProject.nwx")
    testFile = path.join(nwTempGUI, "1_nwProject.nwx")
    refFile  = path.join(nwRef, "gui", "1_nwProject.nwx")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile, [2, 6, 7, 8])

    projFile = path.join(nwFuncTemp, "content", "031b4af5197ec.nwd")
    testFile = path.join(nwTempGUI, "1_031b4af5197ec.nwd")
    refFile  = path.join(nwRef, "gui", "1_031b4af5197ec.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    projFile = path.join(nwFuncTemp, "content", "1a6562590ef19.nwd")
    testFile = path.join(nwTempGUI, "1_1a6562590ef19.nwd")
    refFile  = path.join(nwRef, "gui", "1_1a6562590ef19.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    projFile = path.join(nwFuncTemp, "content", "0e17daca5f3e1.nwd")
    testFile = path.join(nwTempGUI, "1_0e17daca5f3e1.nwd")
    refFile  = path.join(nwRef, "gui", "1_0e17daca5f3e1.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    projFile = path.join(nwFuncTemp, "content", "41cfc0d1f2d12.nwd")
    testFile = path.join(nwTempGUI, "1_41cfc0d1f2d12.nwd")
    refFile  = path.join(nwRef, "gui", "1_41cfc0d1f2d12.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, refFile)

    nwGUI.closeMain()
    # qtbot.stopForInteraction()

@pytest.mark.gui
def testEditFormatMenu(qtbot, nwLipsum, nwTemp):

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

def testContextMenu(qtbot, nwLipsum, nwTemp):

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

@pytest.mark.gui
def testInsertMenu(qtbot, nwFuncTemp, nwTemp):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwFuncTemp, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": nwFuncTemp}, True)

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

    # qtbot.stopForInteraction()
    nwGUI.closeMain()

@pytest.mark.gui
def testOutline(qtbot, nwLipsum, nwTemp):

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
