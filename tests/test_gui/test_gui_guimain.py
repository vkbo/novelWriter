"""
novelWriter – Main GUI Editor Class Tester
==========================================

This file is a part of novelWriter
Copyright (C) 2020 Veronica Berglyd Olsen and novelWriter contributors

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
"""  # noqa
from __future__ import annotations

import shutil

from pathlib import Path
from shutil import copyfile
from unittest.mock import Mock

import pytest

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QInputDialog

from novelwriter import CONFIG, SHARED, __hexversion__
from novelwriter.common import jsonEncode
from novelwriter.config import DEF_GUI_DARK, DEF_GUI_LIGHT
from novelwriter.constants import nwFiles
from novelwriter.dialogs.editlabel import GuiEditLabel
from novelwriter.enum import nwDocAction, nwDocMode, nwFocus, nwItemType, nwState, nwTheme, nwView
from novelwriter.gui.doceditor import GuiDocEditor
from novelwriter.gui.noveltree import GuiNovelView
from novelwriter.gui.outline import GuiOutlineView
from novelwriter.gui.projtree import GuiProjectTree
from novelwriter.shared import _GuiAlert
from novelwriter.tools.welcome import GuiWelcome
from novelwriter.types import QtModCtrl, QtModShift

from tests.mocked import causeOSError
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
    assert SHARED.hasProject is True
    nwGUI.closeProject()
    assert SHARED.hasProject is False

    # Open as if called from Welcome
    nwGUI._openProjectFromWelcome(projPath)
    assert SHARED.hasProject is True
    nwGUI.closeProject()
    assert SHARED.hasProject is False

    # Open as if called from Welcome, invalid path
    with monkeypatch.context() as mp:
        mp.setattr(nwGUI, "showWelcomeDialog", lambda *a: None)
        nwGUI._openProjectFromWelcome(None)
        assert SHARED.hasProject is False

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

    # Check that closes can be blocked
    with monkeypatch.context() as mp:
        mp.setattr(_GuiAlert, "finalState", False)
        assert nwGUI.openProject(projPath) is True
        assert nwGUI.closeMain() is False
    nwGUI.closeProject()

    # Check that latest release info is set
    nwGUI.showPostLaunchDialogs()
    assert CONFIG.lastNotes != "0x0"

    # Set some config error
    CONFIG._hasError = True
    CONFIG._errData.append("Foo")

    # Check that project open dialog launches
    nwGUI.postLaunchTasks(None)
    qtbot.waitUntil(lambda: SHARED.findTopLevelWidget(GuiWelcome) is not None, timeout=1000)
    welcome = SHARED.findTopLevelWidget(GuiWelcome)
    assert isinstance(welcome, GuiWelcome)
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
        nwGUI.projView.projTree.setSelectedHandle(sHandle)
        nwGUI._keyPressReturn()
        assert nwGUI.docEditor.docHandle == sHandle
        nwGUI.closeDocument()

    # Novel Tree has focus
    nwGUI._changeView(nwView.NOVEL)
    with monkeypatch.context() as mp:
        mp.setattr(GuiNovelView, "treeHasFocus", lambda *a: True)
        assert nwGUI.docEditor.docHandle is None
        model = nwGUI.novelView.novelTree._getModel()
        assert model is not None
        nwGUI.novelView.novelTree.setCurrentIndex(model.createIndex(2, 0))
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
    theme = SHARED.theme
    CONFIG.themeMode = nwTheme.DARK
    CONFIG.darkTheme = DEF_GUI_DARK
    CONFIG.lightTheme = DEF_GUI_LIGHT
    theme.loadTheme()
    assert theme.isDarkTheme is True

    nwGUI._processConfigChanges(False, True, False, False)
    nwGUI._processConfigChanges(True, True, True, True)

    # Check editor syntax
    syntax = SHARED.theme.syntaxTheme
    assert nwGUI.docEditor.palette().color(QPalette.ColorRole.Window) == syntax.back
    assert nwGUI.docEditor.docHeader.palette().color(QPalette.ColorRole.Window) == syntax.back
    assert nwGUI.docViewer.palette().color(QPalette.ColorRole.Window) == syntax.back
    assert nwGUI.docViewer.docHeader.palette().color(QPalette.ColorRole.Window) == syntax.back

    # Update by check
    CONFIG.themeMode = nwTheme.LIGHT
    nwGUI.checkThemeUpdate()
    assert theme.isDarkTheme is False

    # Through change event
    event = Mock()
    event.type.return_value = 210
    CONFIG.themeMode = nwTheme.DARK
    nwGUI.changeEvent(event)
    assert theme.isDarkTheme is True

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
    assert len(SHARED.project.tree._items) == 0
    assert len(SHARED.project.tree._nodes) == 0
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
    assert len(SHARED.project.tree) == 9
    assert SHARED.project.tree.model.root.childCount() == 5
    assert SHARED.project.tree.trash is not None  # Created automatically
    assert SHARED.project.data.name == "New Project"
    assert SHARED.project.data.author == "Jane Doe"
    assert SHARED.project.data.spellCheck is False

    # Check that tree items have been created
    assert SHARED.project.tree[C.hNovelRoot] is not None
    assert SHARED.project.tree[C.hPlotRoot] is not None
    assert SHARED.project.tree[C.hCharRoot] is not None
    assert SHARED.project.tree[C.hWorldRoot] is not None
    assert SHARED.project.tree[C.hTitlePage] is not None
    assert SHARED.project.tree[C.hChapterDir] is not None
    assert SHARED.project.tree[C.hChapterDoc] is not None
    assert SHARED.project.tree[C.hSceneDoc] is not None

    nwGUI.mainMenu.aSpellCheck.setChecked(True)
    nwGUI.mainMenu._toggleSpellCheck()

    # Change some settings
    CONFIG.hideHScroll = True
    CONFIG.hideVScroll = True
    CONFIG.autoScroll = False

    # Add a Character File
    nwGUI._changeView(nwView.PROJECT)
    nwGUI.projView.projTree.expandAll()
    nwGUI.projView.projTree.clearSelection()
    nwGUI.projView.projTree.setSelectedHandle(C.hCharRoot)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE, None, isNote=True)
    nwGUI.projView.projTree.expandAll()
    nwGUI.openSelectedItem()

    # Text Editor
    # ===========

    # Syntax Highlighting
    CONFIG.dialogStyle = 3
    CONFIG.dialogLine = "–"
    CONFIG.altDialogOpen = "<|"
    CONFIG.altDialogClose = "|>"

    docEditor = nwGUI.docEditor
    docEditor._qDocument.syntaxHighlighter.initHighlighter()

    # Type something into the document
    nwGUI.docEditor.setFocus()
    qtbot.keyClick(docEditor, "a", modifier=QtModCtrl, delay=KEY_DELAY)
    for c in "# Jane Doe":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    for c in "@tag: Jane":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    for c in "This is a file about Jane.":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    # Add a Plot File
    nwGUI.projView.projTree.expandAll()
    nwGUI.projView.projTree.clearSelection()
    nwGUI.projView.projTree.setSelectedHandle(C.hPlotRoot)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE, None, isNote=True)
    nwGUI.projView.projTree.expandAll()
    nwGUI.openSelectedItem()

    # Type something into the document
    nwGUI.docEditor.setFocus()
    qtbot.keyClick(docEditor, "a", modifier=QtModCtrl, delay=KEY_DELAY)
    for c in "# Main Plot":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    for c in "@tag: MainPlot":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    for c in "This is a file [i]detailing[/i] the main plot.":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    # Add a World File
    nwGUI.projView.projTree.expandAll()
    nwGUI.projView.projTree.clearSelection()
    nwGUI.projView.projTree.setSelectedHandle(C.hWorldRoot)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE, None, isNote=True)
    nwGUI.projView.projTree.expandAll()
    nwGUI.openSelectedItem()

    # Add Some Text
    docEditor.replaceText("Hello World!")
    assert docEditor.getText() == "Hello World!"
    docEditor.replaceText("")

    # Type something into the document
    nwGUI.docEditor.setFocus()
    qtbot.keyClick(docEditor, "a", modifier=QtModCtrl, delay=KEY_DELAY)
    for c in "# Main Location":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    for c in "@tag: Home":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    for c in "This is a file describing Jane's home.":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    # Trigger autosaves before making more changes
    nwGUI._autoSaveDocument()
    nwGUI._autoSaveProject()

    # Select the 'New Scene' file
    nwGUI.projView.projTree.expandAll()
    nwGUI.projView.projTree.clearSelection()
    nwGUI.projView.projTree.setSelectedHandle(C.hSceneDoc)
    nwGUI.openSelectedItem()

    # Type something into the document
    nwGUI.docEditor.setFocus()
    qtbot.keyClick(docEditor, "a", modifier=QtModCtrl, delay=KEY_DELAY)
    for c in "# Novel":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    for c in "## Chapter":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    for c in "@pov: Jane":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    for c in "@plot: MainPlot":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    for c in "### Scene":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    for c in "% How about a comment?":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    for c in "@pov: Jane":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    for c in "@plot: MainPlot":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    for c in "@location: Home":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    for c in "#### Some Section":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    for c in "@char: Jane":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    for c in "This is a paragraph of nonsense text.":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    # Don't allow Shift+Enter to insert a line separator (issue #1150)
    for c in "This is another paragraph":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Enter, modifier=QtModShift, delay=KEY_DELAY)
    for c in "with a line separator in it.":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

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
    for c in "We can even go on to a ---- hotizontal bar. ":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    for c in "Ellipsis? Not a problem either ... ":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    for c in "How about three hyphens - -":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Left, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Backspace, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Right, delay=KEY_DELAY)
    for c in "- for long dash? It works too. ":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    for c in "Even four hyphens - - -":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Left, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Backspace, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Left, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Backspace, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Right, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Right, delay=KEY_DELAY)
    for c in "- for a horizontal works!":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    # Dialogue
    # ========

    for c in '"Full line double quoted text."':
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    for c in "'Full line single quoted text.'":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    # Insert spaces before and after quotes
    CONFIG.fmtPadBefore = "\u201d"
    CONFIG.fmtPadAfter = "\u201c"
    docEditor.initEditor()

    for c in 'Some "double quoted text with spaces padded".':
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    CONFIG.fmtPadBefore = ""
    CONFIG.fmtPadAfter = ""
    docEditor.initEditor()

    # Dialogue Line
    for c in "-- Hi, I am a character speaking.":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    # Narrator Break
    CONFIG.narratorBreak = "–"
    docEditor = nwGUI.docEditor
    docEditor._qDocument.syntaxHighlighter.initHighlighter()

    for c in "-- Hi, I am also a character speaking, -- said another character. -- How are you?":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    # Special Formatting
    # ==================

    # Insert spaces before colon, but ignore tags
    CONFIG.fmtPadBefore = ":"
    docEditor.initEditor()

    for c in "@object: NoSpaceAdded":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    for c in "% synopsis: Space before this is OK.":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    for c in "%Footnote.abc: A simple footnote.":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    for c in "Add space before this colon: See?":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    for c in "But don't add a double space : See?":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    CONFIG.fmtPadBefore = ""
    docEditor.initEditor()

    # Indent and Align
    # ================

    nwGUI._switchFocus(nwView.EDITOR)
    for c in '\t"Tab-indented text"':
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    for c in '>"Paragraph-indented text"':
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    for c in '>>"Right-aligned text"':
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    for c in "\t'Tab-indented text'":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    for c in ">'Paragraph-indented text'":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    for c in ">>'Right-aligned text'":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

    docEditor._wCounterDoc.run()

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

    projFile = projPath / "content" / "0000000000013.nwd"
    testFile = tstPaths.outDir / "guiEditor_Main_Final_0000000000013.nwd"
    compFile = tstPaths.refDir / "guiEditor_Main_Final_0000000000013.nwd"
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

    # Open with keypress
    nwGUI.closeDocViewer()
    assert nwGUI.docViewer.docHandle is None
    nwGUI.projView.setSelectedHandle(C.hSceneDoc)
    with monkeypatch.context() as mp:
        mp.setattr(nwGUI.projView.projTree, "hasFocus", lambda *a: True)
        qtbot.keyClick(
            nwGUI.projView.projTree, Qt.Key.Key_Return, modifier=QtModShift, delay=KEY_DELAY
        )
    assert nwGUI.docViewer.docHandle == C.hSceneDoc

    # qtbot.stop()


@pytest.mark.gui
def testGuiMain_Features(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test various features of the main window."""
    buildTestProject(nwGUI, projPath)
    cHandle = SHARED.project.newFile("Jane", C.hCharRoot)
    newDoc = SHARED.project.storage.getDocument(cHandle)
    newDoc.writeDocument("# Jane\n\n@tag: Jane\n\n")
    nwGUI.rebuildIndex()

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
    assert SHARED.focusMode is True
    assert nwGUI.treePane.isVisible() is False
    assert nwGUI.mainStatus.isVisible() is False
    assert nwGUI.mainMenu.isVisible() is False
    assert nwGUI.sideBar.isVisible() is False
    assert nwGUI.splitView.isVisible() is False

    # Disable focus mode
    nwGUI.toggleFocusMode()
    assert SHARED.focusMode is False
    assert nwGUI.treePane.isVisible() is True
    assert nwGUI.mainStatus.isVisible() is True
    assert nwGUI.mainMenu.isVisible() is True
    assert nwGUI.sideBar.isVisible() is True
    assert nwGUI.splitView.isVisible() is True

    # Closing editor disables focus mode
    nwGUI.toggleFocusMode()
    assert SHARED.focusMode is True
    nwGUI.closeDocument()
    assert SHARED.focusMode is False
    nwGUI.openDocument(C.hSceneDoc)

    # Pressing Escape turns off focus mode
    nwGUI.toggleFocusMode()
    assert SHARED.focusMode is True
    qtbot.keyClick(nwGUI, Qt.Key.Key_Escape)
    assert SHARED.focusMode is False

    # If search is active, Escape is redirected to editor
    nwGUI.toggleFocusMode()
    assert SHARED.focusMode is True
    nwGUI.docEditor.beginSearch()
    qtbot.keyClick(nwGUI, Qt.Key.Key_Escape)
    assert SHARED.focusMode is True

    # Full Screen Mode
    # ================

    fullScreen = Qt.WindowState.WindowFullScreen
    assert nwGUI.windowState() & fullScreen != fullScreen
    nwGUI.toggleFullScreenMode()
    assert nwGUI.windowState() & fullScreen == fullScreen
    nwGUI.toggleFullScreenMode()
    assert nwGUI.windowState() & fullScreen != fullScreen

    # SideBar Menu
    # ============

    # Just make sure the custom event handler executes and doesn't fail
    nwGUI.sideBar.mSettings.show()
    nwGUI.sideBar.mSettings.hide()

    # Redirect Tag Open
    # =================

    nwGUI.closeDocument()
    nwGUI.closeDocViewer()
    assert nwGUI.docEditor.docHandle is None
    assert nwGUI.docViewer.docHandle is None
    nwGUI._followTag("John", nwDocMode.EDIT)  # Doesn't exist
    assert nwGUI.docEditor.docHandle is None
    assert nwGUI.docViewer.docHandle is None
    nwGUI._followTag("Jane", nwDocMode.EDIT)
    assert nwGUI.docEditor.docHandle == cHandle
    assert nwGUI.docViewer.docHandle is None
    nwGUI._followTag("Jane", nwDocMode.VIEW)
    assert nwGUI.docEditor.docHandle == cHandle
    assert nwGUI.docViewer.docHandle == cHandle

    # Errors Handling
    # ===============

    # Cannot edit a folder
    assert nwGUI.openDocument(C.hChapterDir) is False

    # Handle I/O error
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert nwGUI.openDocument(C.hChapterDoc) is False

    # qtbot.stop()


@pytest.mark.gui
def testGuiMain_OpenClose(qtbot, monkeypatch, nwGUI, projPath, fncPath, mockRnd):
    """Test various features of the main window."""
    buildTestProject(nwGUI, projPath)
    nwGUI.openDocument(C.hSceneDoc)
    nwGUI.viewDocument(C.hTitlePage)

    # Handle broken index on project open
    idxData = jsonEncode({"novelWriter.meta": {"version": __hexversion__}})
    nwGUI.closeProject()
    idxPath: Path = projPath / "meta" / nwFiles.INDEX_FILE
    assert idxPath.read_text(encoding="utf-8") != "{}"
    idxPath.write_text(idxData, encoding="utf-8")

    nwGUI.openProject(projPath)
    nwGUI.saveProject()
    assert idxPath.read_text(encoding="utf-8") != "{}"
    assert nwGUI.docEditor.docHandle == C.hSceneDoc
    assert nwGUI.docViewer.docHandle == C.hTitlePage

    # Block closing
    assert SHARED.hasProject is True
    with monkeypatch.context() as mp:
        mp.setattr(_GuiAlert, "finalState", False)
        assert nwGUI.openProject(projPath) is False
        assert SHARED.hasProject is True

    # Don't open on lockfile question: No
    lockPath: Path = projPath / nwFiles.PROJ_LOCK
    lockBack: Path = projPath / f"{nwFiles.PROJ_LOCK}.bak"

    shutil.copyfile(lockPath, lockBack)
    nwGUI.closeProject()
    shutil.copyfile(lockBack, lockPath)

    with monkeypatch.context() as mp:
        mp.setattr(_GuiAlert, "finalState", False)
        assert nwGUI.openProject(projPath) is False

    assert nwGUI.openProject(projPath) is True

    # Backup on close
    backDir = CONFIG.backupPath() / SHARED.project.data.name
    assert not backDir.exists()

    CONFIG.backupOnClose = True
    assert nwGUI.openProject(projPath) is True
    nwGUI.closeProject()
    assert backDir.exists()
    assert len(list(backDir.iterdir())) > 0


@pytest.mark.gui
def testGuiMain_FocusView(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test switching focus and view of the main window."""
    buildTestProject(nwGUI, projPath)

    nwGUI.openDocument(C.hSceneDoc)
    nwGUI.viewDocument(C.hSceneDoc)

    # Toggle Focus
    # ============
    nwGUI.docEditor.setFocus()
    assert nwGUI.docEditor.anyFocus()

    # Simulate focus change to viewer
    nwGUI._appFocusChanged(None, nwGUI.docViewer)
    assert nwGUI.docEditor.docHeader.itemTitle._state == nwState.INACTIVE
    assert nwGUI.docViewer.docHeader.itemTitle._state == nwState.NORMAL

    # Simulate focus change to editor
    nwGUI._appFocusChanged(None, nwGUI.docEditor)
    assert nwGUI.docEditor.docHeader.itemTitle._state == nwState.NORMAL
    assert nwGUI.docViewer.docHeader.itemTitle._state == nwState.INACTIVE

    # Focus Tree
    # ==========
    assert nwGUI.projStack.currentWidget() == nwGUI.projView

    # Switch from editor to project tree
    nwGUI.docEditor.setFocus()
    nwGUI._switchFocus(nwFocus.TREE)
    assert nwGUI.projStack.currentWidget() == nwGUI.projView

    # Triggering again should switch to novel view
    nwGUI._switchFocus(nwFocus.TREE)
    assert nwGUI.projStack.currentWidget() == nwGUI.novelView

    # Switch from editor to novel view
    nwGUI.docEditor.setFocus()
    nwGUI._switchFocus(nwFocus.TREE)
    assert nwGUI.projStack.currentWidget() == nwGUI.novelView

    # Triggering again should switch back to project tree
    nwGUI._switchFocus(nwFocus.TREE)
    assert nwGUI.projStack.currentWidget() == nwGUI.projView

    # If in search mode, should default to project tree
    nwGUI._changeView(nwView.SEARCH)
    nwGUI._switchFocus(nwFocus.TREE)
    assert nwGUI.projStack.currentWidget() == nwGUI.projView

    # Focus Document
    # ==============
    nwGUI._switchFocus(nwFocus.TREE)

    def mockEmitEditorFocus(*a):
        nwGUI._appFocusChanged(None, nwGUI.docEditor)

    def mockEmitViewerFocus(*a):
        nwGUI._appFocusChanged(None, nwGUI.docViewer)

    # Switch to viewer
    with monkeypatch.context() as mp:
        mp.setattr(nwGUI.docEditor, "hasFocus", lambda *a: True)
        mp.setattr(nwGUI.docViewer, "hasFocus", lambda *a: False)
        mp.setattr(nwGUI.docEditor, "setFocus", mockEmitEditorFocus)
        mp.setattr(nwGUI.docViewer, "setFocus", mockEmitViewerFocus)
        nwGUI._switchFocus(nwFocus.DOCUMENT)
        assert nwGUI.docEditor.docHeader.itemTitle._state == nwState.INACTIVE
        assert nwGUI.docViewer.docHeader.itemTitle._state == nwState.NORMAL

    # Call again to switch to editor
    with monkeypatch.context() as mp:
        mp.setattr(nwGUI.docEditor, "hasFocus", lambda *a: False)
        mp.setattr(nwGUI.docViewer, "hasFocus", lambda *a: True)
        mp.setattr(nwGUI.docEditor, "setFocus", mockEmitEditorFocus)
        mp.setattr(nwGUI.docViewer, "setFocus", mockEmitViewerFocus)
        nwGUI._switchFocus(nwFocus.DOCUMENT)
        assert nwGUI.docEditor.docHeader.itemTitle._state == nwState.NORMAL
        assert nwGUI.docViewer.docHeader.itemTitle._state == nwState.INACTIVE

    # Default to editor
    with monkeypatch.context() as mp:
        mp.setattr(nwGUI.docEditor, "hasFocus", lambda *a: False)
        mp.setattr(nwGUI.docViewer, "hasFocus", lambda *a: False)
        mp.setattr(nwGUI.docEditor, "setFocus", mockEmitEditorFocus)
        mp.setattr(nwGUI.docViewer, "setFocus", mockEmitViewerFocus)
        nwGUI._switchFocus(nwFocus.DOCUMENT)
        assert nwGUI.docEditor.docHeader.itemTitle._state == nwState.NORMAL
        assert nwGUI.docViewer.docHeader.itemTitle._state == nwState.INACTIVE

    # Focus Outline
    # =============
    nwGUI._switchFocus(nwFocus.OUTLINE)
    assert nwGUI.mainStack.currentWidget() == nwGUI.outlineView

    # Pass Actions
    # ============

    # Pass to editor
    with monkeypatch.context() as mp:
        mp.setattr(nwGUI.docEditor, "hasFocus", lambda *a: True)
        mp.setattr(nwGUI.docViewer, "hasFocus", lambda *a: False)
        nwGUI._passDocumentAction(nwDocAction.SEL_ALL)
        assert nwGUI.docEditor.textCursor().hasSelection() is True

    # Pass to viewer
    with monkeypatch.context() as mp:
        mp.setattr(nwGUI.docEditor, "hasFocus", lambda *a: False)
        mp.setattr(nwGUI.docViewer, "hasFocus", lambda *a: True)
        nwGUI._passDocumentAction(nwDocAction.SEL_ALL)
        assert nwGUI.docViewer.textCursor().hasSelection() is True

    # qtbot.stop()
