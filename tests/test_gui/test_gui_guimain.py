"""
novelWriter – Main GUI Editor Class Tester
==========================================

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

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
from __future__ import annotations

import sys

from shutil import copyfile

import pytest

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QInputDialog, QMenu

from novelwriter import CONFIG, SHARED
from novelwriter.dialogs.editlabel import GuiEditLabel
from novelwriter.enum import nwFocus, nwItemType, nwView
from novelwriter.gui.doceditor import GuiDocEditor
from novelwriter.gui.noveltree import GuiNovelView
from novelwriter.gui.outline import GuiOutlineView
from novelwriter.gui.projtree import GuiProjectTree
from novelwriter.tools.welcome import GuiWelcome

from tests.tools import NWD_IGNORE, XML_IGNORE, C, buildTestProject, cmpFiles

KEY_DELAY = 1


@pytest.mark.gui
def testGuiMain_ProjectBlocker(nwGUI):
    """Test the blocking of features when there's no project open."""
    # Test no-project blocking
    assert nwGUI.closeProject() is True
    assert nwGUI.saveProject() is False
    assert nwGUI.openDocument(None) is False
    assert nwGUI.viewDocument(None) is False
    assert nwGUI.importDocument() is False


@pytest.mark.gui
def testGuiMain_Launch(qtbot, monkeypatch, nwGUI, projPath):
    """Test the handling of launch tasks."""
    monkeypatch.setattr(GuiWelcome, "exec", lambda *a: None)
    CONFIG.lastNotes = "0x0"
    buildTestProject(nwGUI, projPath)

    # Open Lipsum project
    nwGUI.postLaunchTasks(projPath)
    nwGUI.closeProject()

    # Project open fails
    with monkeypatch.context() as mp:
        mp.setattr(SHARED, "openProject", lambda *a: False)
        assert nwGUI.openProject(projPath) is False

    # Handle locked project
    with monkeypatch.context() as mp:
        mp.setattr(SHARED, "openProject", lambda *a, **k: False)
        SHARED._lockedBy = ["a", "b", "c", "d"]
        assert nwGUI.openProject(projPath) is False
        SHARED._lockedBy = None

    assert nwGUI.openProject(projPath) is True
    nwGUI.closeProject()

    # Check that latest release info updated
    assert CONFIG.lastNotes != "0x0"

    # Set some config error
    CONFIG._hasError = True
    CONFIG._errData.append("Foo")

    # Check that project open dialog launches
    nwGUI.postLaunchTasks(None)
    qtbot.waitUntil(lambda: SHARED.findTopLevelWidget(GuiWelcome) is not None, timeout=1000)
    assert isinstance(welcome := SHARED.findTopLevelWidget(GuiWelcome), GuiWelcome)
    welcome.show()
    welcome.close()

    # Config errors should be cleared
    assert SHARED.lastAlert == "Foo"
    assert CONFIG._hasError is False

    # qtbot.stop()


@pytest.mark.gui
def testGuiMain_ProjectTreeItems(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test handling of project tree items based on GUI focus states."""
    buildTestProject(nwGUI, projPath)

    sHandle = "000000000000f"
    nwGUI.openSelectedItem()
    assert nwGUI.docEditor.docHandle is None

    # Project Tree has focus
    nwGUI._changeView(nwView.PROJECT)
    nwGUI._switchFocus(nwFocus.TREE)
    nwGUI.projStack.setCurrentIndex(0)
    with monkeypatch.context() as mp:
        mp.setattr(GuiProjectTree, "hasFocus", lambda *a: True)
        assert nwGUI.docEditor.docHandle is None
        nwGUI.projView.projTree._getTreeItem(sHandle).setSelected(True)
        nwGUI._keyPressReturn()
        assert nwGUI.docEditor.docHandle == sHandle
        nwGUI.closeDocument()

    # Novel Tree has focus
    nwGUI._changeView(nwView.NOVEL)
    nwGUI.novelView.novelTree.refreshTree(rootHandle=None, overRide=True)
    with monkeypatch.context() as mp:
        mp.setattr(GuiNovelView, "treeHasFocus", lambda *a: True)
        assert nwGUI.docEditor.docHandle is None
        selItem = nwGUI.novelView.novelTree.topLevelItem(2)
        nwGUI.novelView.novelTree.setCurrentItem(selItem)
        nwGUI._keyPressReturn()
        assert nwGUI.docEditor.docHandle == sHandle
        nwGUI.closeDocument()

    # Project Outline has focus
    nwGUI._changeView(nwView.OUTLINE)
    nwGUI._switchFocus(nwFocus.OUTLINE)
    with monkeypatch.context() as mp:
        mp.setattr(GuiOutlineView, "treeHasFocus", lambda *a: True)
        assert nwGUI.docEditor.docHandle is None
        selItem = nwGUI.outlineView.outlineTree.topLevelItem(2)
        nwGUI.outlineView.outlineTree.setCurrentItem(selItem)
        nwGUI._keyPressReturn()
        assert nwGUI.docEditor.docHandle == sHandle
        nwGUI.closeDocument()

    # qtbot.stop()


@pytest.mark.gui
def testGuiMain_UpdateTheme(qtbot, nwGUI):
    """Test updating the theme in the GUI."""
    mainTheme = SHARED.theme
    CONFIG.guiTheme = "default_dark"
    CONFIG.guiSyntax = "default_dark"
    mainTheme.loadTheme()
    mainTheme.loadSyntax()
    nwGUI._processConfigChanges(True, True, True, True)

    syntaxBack = SHARED.theme.colBack

    assert nwGUI.docEditor.palette().color(QPalette.ColorRole.Window) == syntaxBack
    assert nwGUI.docEditor.docHeader.palette().color(QPalette.ColorRole.Window) == syntaxBack
    assert nwGUI.docViewer.palette().color(QPalette.ColorRole.Window) == syntaxBack
    assert nwGUI.docViewer.docHeader.palette().color(QPalette.ColorRole.Window) == syntaxBack

    # qtbot.stop()


@pytest.mark.gui
def testGuiMain_Editing(qtbot, monkeypatch, nwGUI, projPath, tstPaths, mockRnd):
    """Test the document editor."""
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: True)
    monkeypatch.setattr(GuiDocEditor, "hasFocus", lambda *a: True)
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, text: (text, True))
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    # Create new, save, close project
    buildTestProject(nwGUI, projPath)
    assert nwGUI.saveProject()
    assert nwGUI.closeProject()

    assert len(SHARED.project.tree) == 0
    assert len(SHARED.project.tree._order) == 0
    assert len(SHARED.project.tree._roots) == 0
    assert SHARED.project.tree.trashRoot is None
    assert SHARED.project.data.name == ""
    assert SHARED.project.data.author == ""
    assert SHARED.project.data.spellCheck is False

    # Check the files
    projFile = projPath / "nwProject.nwx"
    testFile = tstPaths.outDir / "guiEditor_Main_Initial_nwProject.nwx"
    compFile = tstPaths.refDir / "guiEditor_Main_Initial_nwProject.nwx"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=XML_IGNORE)

    # Re-open project
    assert nwGUI.openProject(projPath)

    # Check that we loaded the data
    assert len(SHARED.project.tree) == 8
    assert len(SHARED.project.tree._order) == 8
    assert len(SHARED.project.tree._roots) == 4
    assert SHARED.project.tree.trashRoot is None
    assert SHARED.project.data.name == "New Project"
    assert SHARED.project.data.author == "Jane Doe"
    assert SHARED.project.data.spellCheck is False

    # Check that tree items have been created
    assert nwGUI.projView.projTree._getTreeItem(C.hNovelRoot) is not None
    assert nwGUI.projView.projTree._getTreeItem(C.hPlotRoot) is not None
    assert nwGUI.projView.projTree._getTreeItem(C.hCharRoot) is not None
    assert nwGUI.projView.projTree._getTreeItem(C.hWorldRoot) is not None
    assert nwGUI.projView.projTree._getTreeItem(C.hTitlePage) is not None
    assert nwGUI.projView.projTree._getTreeItem(C.hChapterDir) is not None
    assert nwGUI.projView.projTree._getTreeItem(C.hChapterDoc) is not None
    assert nwGUI.projView.projTree._getTreeItem(C.hSceneDoc) is not None

    nwGUI.mainMenu.aSpellCheck.setChecked(True)
    nwGUI.mainMenu._toggleSpellCheck()

    # Change some settings
    CONFIG.hideHScroll = True
    CONFIG.hideVScroll = True
    CONFIG.autoScrollPos = 80
    CONFIG.autoScroll = True

    # Add a Character File
    nwGUI._switchFocus(nwFocus.TREE)
    nwGUI.projView.projTree.clearSelection()
    nwGUI.projView.projTree._getTreeItem(C.hCharRoot).setSelected(True)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE, None, isNote=True)
    nwGUI.openSelectedItem()

    # Text Editor
    # ===========

    # Syntax Highlighting
    CONFIG.dialogStyle = 3
    CONFIG.dialogLine = "–"
    CONFIG.narratorBreak = "–"
    CONFIG.altDialogOpen = "<|"
    CONFIG.altDialogClose = "|>"

    docEditor = nwGUI.docEditor
    docEditor._qDocument.syntaxHighlighter.initHighlighter()

    # Type something into the document
    nwGUI.docEditor.setFocus()
    qtbot.keyClick(docEditor, "a", modifier=Qt.ControlModifier, delay=KEY_DELAY)
    for c in "# Jane Doe":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    for c in "@tag: Jane":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    for c in "This is a file about Jane.":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    # Add a Plot File
    nwGUI._switchFocus(nwFocus.TREE)
    nwGUI.projView.projTree.clearSelection()
    nwGUI.projView.projTree._getTreeItem(C.hPlotRoot).setSelected(True)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE, None, isNote=True)
    nwGUI.openSelectedItem()

    # Type something into the document
    nwGUI.docEditor.setFocus()
    qtbot.keyClick(docEditor, "a", modifier=Qt.ControlModifier, delay=KEY_DELAY)
    for c in "# Main Plot":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    for c in "@tag: MainPlot":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    for c in "This is a file [i]detailing[/i] the main plot.":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    # Add a World File
    nwGUI._switchFocus(nwFocus.TREE)
    nwGUI.projView.projTree.clearSelection()
    nwGUI.projView.projTree._getTreeItem(C.hWorldRoot).setSelected(True)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE, None, isNote=True)
    nwGUI.openSelectedItem()

    # Add Some Text
    docEditor.replaceText("Hello World!")
    assert docEditor.getText() == "Hello World!"
    docEditor.replaceText("")

    # Type something into the document
    nwGUI.docEditor.setFocus()
    qtbot.keyClick(docEditor, "a", modifier=Qt.ControlModifier, delay=KEY_DELAY)
    for c in "# Main Location":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    for c in "@tag: Home":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    for c in "This is a file describing Jane's home.":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    # Trigger autosaves before making more changes
    nwGUI._autoSaveDocument()
    nwGUI._autoSaveProject()

    # Select the 'New Scene' file
    nwGUI._switchFocus(nwFocus.TREE)
    nwGUI.projView.projTree.clearSelection()
    nwGUI.projView.projTree._getTreeItem(C.hNovelRoot).setExpanded(True)
    nwGUI.projView.projTree._getTreeItem(C.hChapterDir).setExpanded(True)
    nwGUI.projView.projTree._getTreeItem(C.hSceneDoc).setSelected(True)
    nwGUI.openSelectedItem()

    # Type something into the document
    nwGUI.docEditor.setFocus()
    qtbot.keyClick(docEditor, "a", modifier=Qt.ControlModifier, delay=KEY_DELAY)
    for c in "# Novel":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "## Chapter":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "@pov: Jane":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    for c in "@plot: MainPlot":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "### Scene":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "% How about a comment?":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    for c in "@pov: Jane":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    for c in "@plot: MainPlot":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    for c in "@location: Home":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "#### Some Section":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "@char: Jane":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "This is a paragraph of nonsense text.":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    # Don't allow Shift+Enter to insert a line separator (issue #1150)
    for c in "This is another paragraph":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Enter, modifier=Qt.ShiftModifier, delay=KEY_DELAY)
    for c in "with a line separator in it.":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    # Auto-Replace
    # ============

    for c in (
        "This is another paragraph of much longer nonsense text. "
        "It is in fact 1 very very NONSENSICAL nonsense text! "
    ):
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    for c in "We can also try replacing \"quotes\", even single 'quotes' are replaced. ":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    for c in "Isn't that nice? ":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    for c in "We can hyphen-ate, make dashes -- and even longer dashes --- if we want. ":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    for c in "Ellipsis? Not a problem either ... ":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    for c in "How about three hyphens - -":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Left, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Backspace, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Right, delay=KEY_DELAY)
    for c in "- for long dash? It works too.":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "\"Full line double quoted text.\"":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "'Full line single quoted text.'":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    # Insert spaces before and after quotes
    docEditor._typPadBefore = "\u201d"
    docEditor._typPadAfter = "\u201c"

    for c in "Some \"double quoted text with spaces padded\".":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    docEditor._typPadBefore = ""
    docEditor._typPadAfter = ""

    # Insert spaces before colon, but ignore tags and synopsis
    docEditor._typPadBefore = ":"

    for c in "@object: NoSpaceAdded":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "% synopsis: No space before this colon.":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "Add space before this colon: See?":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "But don't add a double space : See?":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    docEditor._typPadBefore = ""

    # Indent and Align
    # ================

    for c in "\t\"Tab-indented text\"":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in ">\"Paragraph-indented text\"":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in ">>\"Right-aligned text\"":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "\t'Tab-indented text'":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in ">'Paragraph-indented text'":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in ">>'Right-aligned text'":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    docEditor.wCounterDoc.run()

    # Spell Checking
    # ==============

    for c in "Some text with tesst in it.":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    currPos = docEditor.getCursorPosition()
    assert docEditor._qDocument.spellErrorAtPos(currPos) == ("", -1, -1, [])

    errPos = currPos - 13
    if not sys.platform.startswith("win32"):
        # Skip on Windows as spell checking is off there
        # This check will fail without an 'en' dictionary, like aspell-en
        word, cPos, cLen, suggest = docEditor._qDocument.spellErrorAtPos(errPos)
        assert word == "tesst"
        assert cPos == 15
        assert cLen == 5
        assert "test" in suggest

    with monkeypatch.context() as mp:
        mp.setattr(QMenu, "exec", lambda *a: None)
        docEditor.setCursorPosition(errPos)
        docEditor._openContextFromCursor()

    # Check Files
    # ===========

    # Save the document
    assert docEditor.docChanged
    nwGUI.saveDocument()
    assert docEditor.docChanged is False
    nwGUI.forceSaveDocument()
    assert docEditor.docChanged is False
    nwGUI.rebuildIndex()

    # Open and view the edited document
    nwGUI.docViewer.setFocus()
    assert nwGUI.openDocument(C.hSceneDoc)
    assert nwGUI.viewDocument(C.hSceneDoc)
    assert nwGUI.saveProject()
    assert nwGUI.closeViewerPanel()

    # Check the files
    projFile = projPath / "nwProject.nwx"
    testFile = tstPaths.outDir / "guiEditor_Main_Final_nwProject.nwx"
    compFile = tstPaths.refDir / "guiEditor_Main_Final_nwProject.nwx"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=(*XML_IGNORE, "<spellCheck"))

    projFile = projPath / "content" / "000000000000f.nwd"
    testFile = tstPaths.outDir / "guiEditor_Main_Final_000000000000f.nwd"
    compFile = tstPaths.refDir / "guiEditor_Main_Final_000000000000f.nwd"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=NWD_IGNORE)

    projFile = projPath / "content" / "0000000000010.nwd"
    testFile = tstPaths.outDir / "guiEditor_Main_Final_0000000000010.nwd"
    compFile = tstPaths.refDir / "guiEditor_Main_Final_0000000000010.nwd"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=NWD_IGNORE)

    projFile = projPath / "content" / "0000000000011.nwd"
    testFile = tstPaths.outDir / "guiEditor_Main_Final_0000000000011.nwd"
    compFile = tstPaths.refDir / "guiEditor_Main_Final_0000000000011.nwd"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=NWD_IGNORE)

    projFile = projPath / "content" / "0000000000012.nwd"
    testFile = tstPaths.outDir / "guiEditor_Main_Final_0000000000012.nwd"
    compFile = tstPaths.refDir / "guiEditor_Main_Final_0000000000012.nwd"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=NWD_IGNORE)

    # qtbot.stop()


@pytest.mark.gui
def testGuiMain_Viewing(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test the document viewer."""
    buildTestProject(nwGUI, projPath)
    nwGUI.closeProject()

    # View before a project is open does nothing
    assert nwGUI.splitView.isVisible() is False
    assert nwGUI.viewDocument(None) is False
    assert nwGUI.splitView.isVisible() is False

    # Open project requires a path
    assert nwGUI.openProject(None) is False
    assert SHARED.hasProject is False

    # Open the test project, properly
    nwGUI.openProject(projPath)
    assert nwGUI.docEditor.docHandle == C.hTitlePage

    # If editor has focus, open that document
    with monkeypatch.context() as mp:
        mp.setattr(nwGUI.docEditor, "hasFocus", lambda *a: True)
        nwGUI.viewDocument(None)
        assert nwGUI.docViewer.docHandle == C.hTitlePage
    nwGUI.closeDocViewer()

    # If editor does not have focus, open selected handle
    with monkeypatch.context() as mp:
        mp.setattr(nwGUI.docEditor, "hasFocus", lambda *a: False)
        nwGUI.projView.projTree.setSelectedHandle(C.hSceneDoc)
        nwGUI.viewDocument(None)
        assert nwGUI.docViewer.docHandle == C.hSceneDoc

    # If there is no selection, get last selected
    SHARED.project.data.setLastHandle(C.hChapterDoc, "viewer")
    assert SHARED.project.data.getLastHandle("viewer") == C.hChapterDoc
    with monkeypatch.context() as mp:
        mp.setattr(nwGUI.docEditor, "hasFocus", lambda *a: False)
        nwGUI.projView.projTree.clearSelection()
        nwGUI.viewDocument(None)
        assert nwGUI.docViewer.docHandle == C.hChapterDoc

    # If all fails, don't open anything
    SHARED.project.data.setLastHandle(None, "viewer")
    assert SHARED.project.data.getLastHandle("viewer") is None
    with monkeypatch.context() as mp:
        mp.setattr(nwGUI.docEditor, "hasFocus", lambda *a: False)
        nwGUI.projView.projTree.clearSelection()
        assert nwGUI.viewDocument(None) is False

    # If editor doc was edited and requested for the viewer, save it first
    nwGUI.openDocument(C.hSceneDoc)
    nwGUI.docEditor.setPlainText("### New Scene\n\nWith some stuff in it!\n\n")
    assert nwGUI.docEditor.docChanged is True

    nwGUI.viewDocument(C.hSceneDoc)
    assert nwGUI.docViewer.toPlainText() == "New Scene\nWith some stuff in it!"

    # qtbot.stop()


@pytest.mark.gui
def testGuiMain_Features(qtbot, nwGUI, projPath, mockRnd):
    """Test various features of the main window."""
    buildTestProject(nwGUI, projPath)
    assert SHARED.focusMode is False

    # Focus Mode
    # ==========

    # No document open, so not allowing focus mode
    nwGUI.toggleFocusMode()
    assert nwGUI.treePane.isVisible() is True
    assert nwGUI.mainStatus.isVisible() is True
    assert nwGUI.mainMenu.isVisible() is True
    assert nwGUI.sideBar.isVisible() is True

    # Open a file in editor and viewer
    assert nwGUI.openDocument(C.hSceneDoc)
    assert nwGUI.viewDocument(C.hSceneDoc)

    # Enable focus mode
    nwGUI.toggleFocusMode()
    assert nwGUI.treePane.isVisible() is False
    assert nwGUI.mainStatus.isVisible() is False
    assert nwGUI.mainMenu.isVisible() is False
    assert nwGUI.sideBar.isVisible() is False
    assert nwGUI.splitView.isVisible() is False

    # Disable focus mode
    nwGUI.toggleFocusMode()
    assert nwGUI.treePane.isVisible() is True
    assert nwGUI.mainStatus.isVisible() is True
    assert nwGUI.mainMenu.isVisible() is True
    assert nwGUI.sideBar.isVisible() is True
    assert nwGUI.splitView.isVisible() is True

    # Full Screen Mode
    # ================

    assert nwGUI.windowState() & Qt.WindowFullScreen != Qt.WindowFullScreen
    nwGUI.toggleFullScreenMode()
    assert nwGUI.windowState() & Qt.WindowFullScreen == Qt.WindowFullScreen
    nwGUI.toggleFullScreenMode()
    assert nwGUI.windowState() & Qt.WindowFullScreen != Qt.WindowFullScreen

    # SideBar Menu
    # ============

    # Just make sure the custom event handler executes and doesn't fail
    nwGUI.sideBar.mSettings.show()
    nwGUI.sideBar.mSettings.hide()

    # qtbot.stop()
