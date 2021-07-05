"""
novelWriter – Main GUI Editor Class Tester
==========================================

This file is a part of novelWriter
Copyright 2018–2021, Veronica Berglyd Olsen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import pytest
import os

from shutil import copyfile
from tools import cmpFiles

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QDialog

from nw.dialogs.itemeditor import GuiItemEditor
from nw.gui.doceditor import GuiDocEditor
from nw.gui.projtree import GuiProjectTree
from nw.enum import nwItemType, nwWidget

keyDelay = 2
typeDelay = 1
stepDelay = 20


@pytest.mark.gui
def testGuiMain_Editing(qtbot, monkeypatch, nwGUI, fncProj, refDir, outDir):
    """Test the document editor.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *args: QMessageBox.Yes)
    monkeypatch.setattr(GuiItemEditor, "exec_", lambda *args: None)
    monkeypatch.setattr(GuiItemEditor, "result", lambda *args: QDialog.Accepted)
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *args: True)
    monkeypatch.setattr(GuiDocEditor, "hasFocus", lambda *args: True)

    # Create new, save, close project
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": fncProj})
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
    projFile = os.path.join(fncProj, "nwProject.nwx")
    testFile = os.path.join(outDir, "guiEditor_Main_Initial_nwProject.nwx")
    compFile = os.path.join(refDir, "guiEditor_Main_Initial_nwProject.nwx")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, [2, 6, 7, 8])
    qtbot.wait(stepDelay)

    # qtbot.stopForInteraction()

    # Re-open project
    assert nwGUI.openProject(fncProj)
    qtbot.wait(stepDelay)

    # Check that we loaded the data
    assert len(nwGUI.theProject.projTree) == 8
    assert len(nwGUI.theProject.projTree._treeOrder) == 8
    assert len(nwGUI.theProject.projTree._treeRoots) == 4
    assert nwGUI.theProject.projTree.trashRoot() is None
    assert nwGUI.theProject.projPath == fncProj
    assert nwGUI.theProject.projMeta == os.path.join(fncProj, "meta")
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

    # Change some settings
    nwGUI.mainConf.hideHScroll = True
    nwGUI.mainConf.hideVScroll = True
    nwGUI.mainConf.scrollPastEnd = True
    nwGUI.mainConf.autoScrollPos = 80
    nwGUI.mainConf.autoScroll = True

    # Add a Character File
    nwGUI.switchFocus(nwWidget.TREE)
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem("71ee45a3c0db9").setSelected(True)
    nwGUI.treeView.newTreeItem(nwItemType.FILE, None)
    assert nwGUI.openSelectedItem()

    # Type something into the document
    nwGUI.switchFocus(nwWidget.EDITOR)
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
    nwGUI.switchFocus(nwWidget.TREE)
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem("44cb730c42048").setSelected(True)
    nwGUI.treeView.newTreeItem(nwItemType.FILE, None)
    assert nwGUI.openSelectedItem()

    # Type something into the document
    nwGUI.switchFocus(nwWidget.EDITOR)
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
    nwGUI.switchFocus(nwWidget.TREE)
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem("811786ad1ae74").setSelected(True)
    nwGUI.treeView.newTreeItem(nwItemType.FILE, None)
    assert nwGUI.openSelectedItem()

    # Add Some Text
    nwGUI.docEditor.replaceText("Hello World!")
    assert nwGUI.docEditor.getText() == "Hello World!"
    nwGUI.docEditor.replaceText("")

    # Type something into the document
    nwGUI.switchFocus(nwWidget.EDITOR)
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
    nwGUI.switchFocus(nwWidget.TREE)
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem("73475cb40a568").setExpanded(True)
    nwGUI.treeView._getTreeItem("31489056e0916").setExpanded(True)
    nwGUI.treeView._getTreeItem("0e17daca5f3e1").setSelected(True)
    assert nwGUI.openSelectedItem()

    # Type something into the document
    nwGUI.switchFocus(nwWidget.EDITOR)
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

    for c in "This is a paragraph of nonsense text.":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in (
        "This is another paragraph of much longer nonsense text. "
        "It is in fact 1 very very NONSENSICAL nonsense text! "
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
    assert nwGUI.docEditor.docChanged()
    assert nwGUI.saveDocument()
    assert not nwGUI.docEditor.docChanged()
    qtbot.wait(stepDelay)
    nwGUI.rebuildIndex()
    qtbot.wait(stepDelay)

    # Open and view the edited document
    nwGUI.switchFocus(nwWidget.VIEWER)
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
    assert nwGUI.theProject.projTree["2fca346db6561"] is not None  # Trash
    assert nwGUI.saveProject()

    # Check the files
    projFile = os.path.join(fncProj, "nwProject.nwx")
    testFile = os.path.join(outDir, "guiEditor_Main_Final_nwProject.nwx")
    compFile = os.path.join(refDir, "guiEditor_Main_Final_nwProject.nwx")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, [2, 6, 7, 8])

    projFile = os.path.join(fncProj, "content", "031b4af5197ec.nwd")
    testFile = os.path.join(outDir, "guiEditor_Main_Final_031b4af5197ec.nwd")
    compFile = os.path.join(refDir, "guiEditor_Main_Final_031b4af5197ec.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    projFile = os.path.join(fncProj, "content", "1a6562590ef19.nwd")
    testFile = os.path.join(outDir, "guiEditor_Main_Final_1a6562590ef19.nwd")
    compFile = os.path.join(refDir, "guiEditor_Main_Final_1a6562590ef19.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    projFile = os.path.join(fncProj, "content", "0e17daca5f3e1.nwd")
    testFile = os.path.join(outDir, "guiEditor_Main_Final_0e17daca5f3e1.nwd")
    compFile = os.path.join(refDir, "guiEditor_Main_Final_0e17daca5f3e1.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    projFile = os.path.join(fncProj, "content", "41cfc0d1f2d12.nwd")
    testFile = os.path.join(outDir, "guiEditor_Main_Final_41cfc0d1f2d12.nwd")
    compFile = os.path.join(refDir, "guiEditor_Main_Final_41cfc0d1f2d12.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    # qtbot.stopForInteraction()

# END Test testGuiMain_Editing
