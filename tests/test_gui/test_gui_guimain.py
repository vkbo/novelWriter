"""
novelWriter – Main GUI Editor Class Tester
==========================================

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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

import os
import pytest

from shutil import copyfile
from tools import cmpFiles, buildTestProject, XML_IGNORE, writeFile

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QDialog

from novelwriter.gui import (
    GuiDocEditor, GuiProjectTree, GuiNovelTree, GuiOutline
)
from novelwriter.enum import nwItemType, nwWidget
from novelwriter.tools import GuiProjectWizard
from novelwriter.dialogs.itemeditor import GuiItemEditor

keyDelay = 2
typeDelay = 1
stepDelay = 20


@pytest.mark.gui
def testGuiMain_ProjectBlocker(monkeypatch, nwGUI):
    """Test the blocking of features when there's no project open.
    """
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)

    # Test no-project blocking
    assert nwGUI.closeProject() is True
    assert nwGUI.saveProject() is False
    assert nwGUI.closeDocument() is False
    assert nwGUI.openDocument(None) is False
    assert nwGUI.openNextDocument(None) is False
    assert nwGUI.saveDocument() is False
    assert nwGUI.viewDocument(None) is False
    assert nwGUI.importDocument() is False
    assert nwGUI.mergeDocuments() is False
    assert nwGUI.splitDocument() is False
    assert nwGUI.openSelectedItem() is False
    assert nwGUI.editItem() is False
    assert nwGUI.requestNovelTreeRefresh() is False
    assert nwGUI.rebuildIndex() is False
    assert nwGUI.showProjectSettingsDialog() is False
    assert nwGUI.showProjectDetailsDialog() is False
    assert nwGUI.showBuildProjectDialog() is False
    assert nwGUI.showProjectWordListDialog() is False
    assert nwGUI.showWritingStatsDialog() is False

# END Test testGuiMain_NoProject


@pytest.mark.gui
def testGuiMain_NewProject(monkeypatch, nwGUI, fncProj):
    """Test creating a new project.
    """
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)

    # No data
    with monkeypatch.context() as mp:
        mp.setattr(GuiProjectWizard, "exec_", lambda *a: None)
        assert nwGUI.newProject(projData=None) is False

    # Close project
    with monkeypatch.context() as mp:
        nwGUI.hasProject = True
        mp.setattr(QMessageBox, "question", lambda *a: QMessageBox.No)
        assert nwGUI.newProject(projData={"projPath": fncProj}) is False

    # No project path
    assert nwGUI.newProject(projData={}) is False

    # Project file already exists
    projFile = os.path.join(fncProj, nwGUI.theProject.projFile)
    writeFile(projFile, "Stuff")
    assert nwGUI.newProject(projData={"projPath": fncProj}) is False
    os.unlink(projFile)

    # An unreachable path should also fail
    projPath = os.path.join(fncProj, "stuff", "stuff", "stuff")
    assert nwGUI.newProject(projData={"projPath": projPath}) is False

    # This one should work just fine
    assert nwGUI.newProject(projData={"projPath": fncProj}) is True
    assert os.path.isfile(os.path.join(fncProj, nwGUI.theProject.projFile))
    assert os.path.isdir(os.path.join(fncProj, "content"))

# END Test testGuiMain_NewProject


@pytest.mark.gui
def testGuiMain_ProjectTreeItems(qtbot, monkeypatch, nwGUI, fncProj, mockRnd):
    """Test handling of project tree items based on GUI focus states.
    """
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)

    buildTestProject(nwGUI, fncProj)

    sHandle = "000000000000f"
    assert nwGUI.openSelectedItem() is False

    # Project Tree has focus
    nwGUI.switchFocus(nwWidget.TREE)
    nwGUI.projStack.setCurrentIndex(0)
    with monkeypatch.context() as mp:
        mp.setattr(GuiProjectTree, "hasFocus", lambda *a: True)
        assert nwGUI.docEditor.docHandle() is None
        nwGUI.treeView._getTreeItem(sHandle).setSelected(True)
        nwGUI._keyPressReturn()
        assert nwGUI.docEditor.docHandle() == sHandle
        assert nwGUI.closeDocument() is True

    # Novel Tree has focus
    nwGUI.projStack.setCurrentIndex(1)
    nwGUI.novelView.refreshTree(True)
    with monkeypatch.context() as mp:
        mp.setattr(GuiNovelTree, "hasFocus", lambda *a: True)
        assert nwGUI.docEditor.docHandle() is None
        actItem = nwGUI.novelView.topLevelItem(0)
        chpItem = actItem.child(0)
        selItem = chpItem.child(0)
        nwGUI.novelView.setCurrentItem(selItem)
        nwGUI._keyPressReturn()
        assert nwGUI.docEditor.docHandle() == sHandle
        assert nwGUI.closeDocument() is True

    # Project Outline has focus
    nwGUI.switchFocus(nwWidget.OUTLINE)
    with monkeypatch.context() as mp:
        mp.setattr(GuiOutline, "treeFocus", lambda *a: True)
        assert nwGUI.docEditor.docHandle() is None
        actItem = nwGUI.projView.outlineView.topLevelItem(0)
        chpItem = actItem.child(0)
        selItem = chpItem.child(0)
        nwGUI.projView.outlineView.setCurrentItem(selItem)
        nwGUI._keyPressReturn()
        assert nwGUI.docEditor.docHandle() == sHandle
        assert nwGUI.closeDocument() is True

    # qtbot.stopForInteraction()

# END Test testGuiMain_ProjectTreeItems


@pytest.mark.gui
def testGuiMain_Editing(qtbot, monkeypatch, nwGUI, fncProj, refDir, outDir, mockRnd):
    """Test the document editor.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(GuiItemEditor, "exec_", lambda *a: None)
    monkeypatch.setattr(GuiItemEditor, "result", lambda *a: QDialog.Accepted)
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: True)
    monkeypatch.setattr(GuiDocEditor, "hasFocus", lambda *a: True)

    # Create new, save, close project
    buildTestProject(nwGUI, fncProj)
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
    assert cmpFiles(testFile, compFile, ignoreStart=XML_IGNORE)
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
    assert nwGUI.theProject.bookTitle == "New Novel"
    assert len(nwGUI.theProject.bookAuthors) == 1
    assert nwGUI.theProject.spellCheck is False

    # Check that tree items have been created
    assert nwGUI.treeView._getTreeItem("0000000000008") is not None
    assert nwGUI.treeView._getTreeItem("0000000000009") is not None
    assert nwGUI.treeView._getTreeItem("000000000000a") is not None
    assert nwGUI.treeView._getTreeItem("000000000000b") is not None
    assert nwGUI.treeView._getTreeItem("000000000000c") is not None
    assert nwGUI.treeView._getTreeItem("000000000000d") is not None
    assert nwGUI.treeView._getTreeItem("000000000000e") is not None
    assert nwGUI.treeView._getTreeItem("000000000000f") is not None

    nwGUI.mainMenu.aSpellCheck.setChecked(True)
    assert nwGUI.mainMenu._toggleSpellCheck()

    # Change some settings
    nwGUI.mainConf.hideHScroll = True
    nwGUI.mainConf.hideVScroll = True
    nwGUI.mainConf.autoScrollPos = 80
    nwGUI.mainConf.autoScroll = True

    # Add a Character File
    nwGUI.switchFocus(nwWidget.TREE)
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem("000000000000a").setSelected(True)
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
    nwGUI.treeView._getTreeItem("0000000000009").setSelected(True)
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
    nwGUI.treeView._getTreeItem("000000000000b").setSelected(True)
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
    nwGUI.treeView._getTreeItem("0000000000008").setExpanded(True)
    nwGUI.treeView._getTreeItem("000000000000d").setExpanded(True)
    nwGUI.treeView._getTreeItem("000000000000f").setSelected(True)
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

    for c in "\t\"Tab-indented text\"":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in ">\"Paragraph-indented text\"":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in ">>\"Right-aligned text\"":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in "\t'Tab-indented text'":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in ">'Paragraph-indented text'":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    for c in ">>'Right-aligned text'":
        qtbot.keyClick(nwGUI.docEditor, c, delay=typeDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=keyDelay)

    qtbot.wait(stepDelay)
    nwGUI.docEditor.wCounterDoc.run()
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
    assert nwGUI.openDocument("000000000000f")
    assert nwGUI.viewDocument("000000000000f")
    qtbot.wait(stepDelay)
    assert nwGUI.saveProject()
    assert nwGUI.closeDocViewer()
    qtbot.wait(stepDelay)

    # Check a Quick Create and Delete
    assert nwGUI.treeView.newTreeItem(nwItemType.FILE, None)
    newHandle = nwGUI.treeView.getSelectedHandle()
    assert nwGUI.theProject.projTree["0000000000020"] is not None
    assert nwGUI.treeView.deleteItem()
    assert nwGUI.treeView.setSelectedHandle(newHandle)
    assert nwGUI.treeView.deleteItem()
    assert nwGUI.theProject.projTree["0000000000024"] is not None  # Trash
    assert nwGUI.saveProject()

    # Check the files
    projFile = os.path.join(fncProj, "nwProject.nwx")
    testFile = os.path.join(outDir, "guiEditor_Main_Final_nwProject.nwx")
    compFile = os.path.join(refDir, "guiEditor_Main_Final_nwProject.nwx")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=XML_IGNORE)

    projFile = os.path.join(fncProj, "content", "000000000000f.nwd")
    testFile = os.path.join(outDir, "guiEditor_Main_Final_000000000000f.nwd")
    compFile = os.path.join(refDir, "guiEditor_Main_Final_000000000000f.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    projFile = os.path.join(fncProj, "content", "0000000000020.nwd")
    testFile = os.path.join(outDir, "guiEditor_Main_Final_0000000000020.nwd")
    compFile = os.path.join(refDir, "guiEditor_Main_Final_0000000000020.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    projFile = os.path.join(fncProj, "content", "0000000000021.nwd")
    testFile = os.path.join(outDir, "guiEditor_Main_Final_0000000000021.nwd")
    compFile = os.path.join(refDir, "guiEditor_Main_Final_0000000000021.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    projFile = os.path.join(fncProj, "content", "0000000000022.nwd")
    testFile = os.path.join(outDir, "guiEditor_Main_Final_0000000000022.nwd")
    compFile = os.path.join(refDir, "guiEditor_Main_Final_0000000000022.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    # qtbot.stopForInteraction()

# END Test testGuiMain_Editing


@pytest.mark.gui
def testGuiMain_FocusFullMode(qtbot, monkeypatch, nwGUI, fncProj, mockRnd):
    """Test toggling focus mode in main window.
    """
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)

    buildTestProject(nwGUI, fncProj)
    assert nwGUI.isFocusMode is False

    # Focus Mode
    # ==========

    # No document open, so not allowing focus mode
    assert nwGUI.toggleFocusMode() is False

    # Open a file in editor and viewer
    assert nwGUI.openDocument("000000000000f")
    assert nwGUI.viewDocument("000000000000f")

    # Enable focus mode
    assert nwGUI.toggleFocusMode() is True
    assert nwGUI.treePane.isVisible() is False
    assert nwGUI.statusBar.isVisible() is False
    assert nwGUI.mainMenu.isVisible() is False
    assert nwGUI.viewsBar.isVisible() is False
    assert nwGUI.splitView.isVisible() is False

    # Disable focus mode
    assert nwGUI.toggleFocusMode() is True
    assert nwGUI.treePane.isVisible() is True
    assert nwGUI.statusBar.isVisible() is True
    assert nwGUI.mainMenu.isVisible() is True
    assert nwGUI.viewsBar.isVisible() is True
    assert nwGUI.splitView.isVisible() is True

    # Full Screen Mode
    # ================

    assert nwGUI.mainConf.isFullScreen is False
    nwGUI.toggleFullScreenMode()
    assert nwGUI.mainConf.isFullScreen is True
    nwGUI.toggleFullScreenMode()
    assert nwGUI.mainConf.isFullScreen is False

    # qtbot.stopForInteraction()

# END Test testGuiMain_FocusFullMode
