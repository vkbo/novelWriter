"""
novelWriter – Main GUI Editor Class Tester
==========================================

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

from tools import C, buildTestProject
from mocked import causeOSError

from PyQt5.QtGui import QTextBlock, QTextCursor, QTextOption
from PyQt5.QtCore import QThreadPool, Qt
from PyQt5.QtWidgets import QAction, qApp

from novelwriter import CONFIG, SHARED
from novelwriter.enum import nwDocAction, nwDocInsert, nwItemLayout, nwTrinary, nwWidget
from novelwriter.constants import nwKeyWords, nwUnicode
from novelwriter.core.index import countWords
from novelwriter.gui.doceditor import GuiDocEditor, GuiDocToolBar

KEY_DELAY = 1


@pytest.mark.gui
def testGuiEditor_Init(qtbot, nwGUI, projPath, ipsumText, mockRnd):
    """Test initialising the editor."""
    # Open project
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc)

    nwGUI.docEditor.setPlainText("### Lorem Ipsum\n\n%s" % ipsumText[0])
    assert nwGUI.saveDocument()

    # Check Defaults
    qDoc = nwGUI.docEditor.document()
    assert qDoc.defaultTextOption().alignment() == Qt.AlignLeft
    assert nwGUI.docEditor.verticalScrollBarPolicy() == Qt.ScrollBarAsNeeded
    assert nwGUI.docEditor.horizontalScrollBarPolicy() == Qt.ScrollBarAsNeeded
    assert nwGUI.docEditor._typPadChar == nwUnicode.U_NBSP

    # Check that editor handles settings
    CONFIG.textFont = ""
    CONFIG.doJustify = True
    CONFIG.showTabsNSpaces = True
    CONFIG.showLineEndings = True
    CONFIG.hideVScroll = True
    CONFIG.hideHScroll = True
    CONFIG.fmtPadThin = True

    nwGUI.docEditor.initEditor()

    qDoc = nwGUI.docEditor.document()
    assert CONFIG.textFont == qDoc.defaultFont().family()
    assert qDoc.defaultTextOption().alignment() == Qt.AlignJustify
    assert qDoc.defaultTextOption().flags() & QTextOption.ShowTabsAndSpaces
    assert qDoc.defaultTextOption().flags() & QTextOption.ShowLineAndParagraphSeparators
    assert nwGUI.docEditor.verticalScrollBarPolicy() == Qt.ScrollBarAlwaysOff
    assert nwGUI.docEditor.horizontalScrollBarPolicy() == Qt.ScrollBarAlwaysOff
    assert nwGUI.docEditor._typPadChar == nwUnicode.U_THNBSP

    # qtbot.stop()

# END Test testGuiEditor_Init


@pytest.mark.gui
def testGuiEditor_LoadText(qtbot, monkeypatch, caplog, nwGUI, projPath, ipsumText, mockRnd):
    """Test loading text into the editor."""
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True

    longText = "### Lorem Ipsum\n\n%s" % "\n\n".join(ipsumText*20)
    nwGUI.docEditor.replaceText(longText)
    assert nwGUI.saveDocument() is True
    assert nwGUI.closeDocument() is True

    # Load Text
    # =========

    # Invalid handle
    assert nwGUI.docEditor.loadText("abcdefghijklm") is False

    # Regular open
    assert nwGUI.docEditor.loadText(C.hSceneDoc) is True

    # Regular open, with line number (1 indexed)
    assert nwGUI.docEditor.loadText(C.hSceneDoc, tLine=4) is True
    cursPos = nwGUI.docEditor.getCursorPosition()
    assert nwGUI.docEditor.document().findBlock(cursPos).blockNumber() == 3

    # Load empty document
    nwGUI.docEditor.replaceText("")
    assert nwGUI.saveDocument() is True
    assert nwGUI.docEditor.loadText(C.hSceneDoc) is True
    assert nwGUI.docEditor.toPlainText() == ""

    # qtbot.stop()

# END Test testGuiEditor_LoadText


@pytest.mark.gui
def testGuiEditor_SaveText(qtbot, monkeypatch, caplog, nwGUI, projPath, ipsumText, mockRnd):
    """Test saving text from the editor."""
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True

    # Save Text
    # =========

    longText = "### Lorem Ipsum\n\n%s" % "\n\n".join(ipsumText)
    nwGUI.docEditor.replaceText(longText)

    # Missing item
    nwItem = nwGUI.docEditor._nwItem
    nwGUI.docEditor._nwItem = None
    assert nwGUI.docEditor.saveText() is False
    nwGUI.docEditor._nwItem = nwItem

    # Unknown handle
    nwGUI.docEditor._docHandle = "0123456789abcdef"
    assert nwGUI.docEditor.saveText() is False
    nwGUI.docEditor._docHandle = C.hSceneDoc

    # Cause error when saving
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert nwGUI.docEditor.saveText() is False
        assert "Could not save document." in caplog.text

    # Change header level
    assert SHARED.project.tree[C.hSceneDoc].itemLayout == nwItemLayout.DOCUMENT  # type: ignore
    nwGUI.docEditor.replaceText(longText[1:])
    assert nwGUI.docEditor.saveText() is True
    assert SHARED.project.tree[C.hSceneDoc].itemLayout == nwItemLayout.DOCUMENT  # type: ignore

    # Regular save
    assert nwGUI.docEditor.saveText() is True

    # qtbot.stop()

# END Test testGuiEditor_SaveText


@pytest.mark.gui
def testGuiEditor_MetaData(qtbot, nwGUI, projPath, mockRnd):
    """Test extracting various meta data and other values."""
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True

    # Get Text
    # This should replace line and paragraph separators, but preserve
    # non-breaking spaces.
    newText = (
        "### New Scene\u2029\u2029"
        "Some\u2028text.\u2029"
        "More\u00a0text.\u2029"
    )
    nwGUI.docEditor.replaceText(newText)
    assert nwGUI.docEditor.getText() == "### New Scene\n\nSome\ntext.\nMore\u00a0text.\n"

    # Check Propertoes
    assert nwGUI.docEditor.docChanged is True
    assert nwGUI.docEditor.docHandle == C.hSceneDoc
    assert nwGUI.docEditor.lastActive > 0.0
    assert nwGUI.docEditor.isEmpty is False

    # Cursor Position
    nwGUI.docEditor.setCursorPosition(10)
    assert nwGUI.docEditor.getCursorPosition() == 10
    assert SHARED.project.tree[C.hSceneDoc].cursorPos != 10  # type: ignore
    nwGUI.docEditor.saveCursorPosition()
    assert SHARED.project.tree[C.hSceneDoc].cursorPos == 10  # type: ignore

    nwGUI.docEditor.setCursorLine(None)
    assert nwGUI.docEditor.getCursorPosition() == 10
    nwGUI.docEditor.setCursorLine(3)
    assert nwGUI.docEditor.getCursorPosition() == 15

    # Document Changed Signal
    nwGUI.docEditor._docChanged = False
    with qtbot.waitSignal(nwGUI.docEditor.editedStatusChanged, raising=True, timeout=100):
        nwGUI.docEditor.setDocumentChanged(True)
    assert nwGUI.docEditor._docChanged is True

    # qtbot.stop()

# END Test testGuiEditor_MetaData


@pytest.mark.gui
def testGuiEditor_Actions(qtbot, nwGUI, projPath, ipsumText, mockRnd):
    """Test the document actions. This is not an extensive test of the
    action features, just that the actions are actually called. The
    various action features are tested when their respective functions
    are tested.
    """
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True

    text = "### A Scene\n\n%s" % "\n\n".join(ipsumText)
    nwGUI.docEditor.replaceText(text)
    theDoc = nwGUI.docEditor.document()

    # Select/Cut/Copy/Paste/Undo/Redo
    # ===============================

    qApp.clipboard().clear()

    # Select All
    assert nwGUI.docEditor.docAction(nwDocAction.SEL_ALL) is True
    theCursor = nwGUI.docEditor.textCursor()
    assert theCursor.hasSelection() is True
    assert theCursor.selectedText() == text.replace("\n", "\u2029")
    theCursor.clearSelection()

    # Select Paragraph
    nwGUI.docEditor.setCursorPosition(1000)
    assert nwGUI.docEditor.getCursorPosition() == 1000
    assert nwGUI.docEditor.docAction(nwDocAction.SEL_PARA) is True
    theCursor = nwGUI.docEditor.textCursor()
    assert theCursor.selectedText() == ipsumText[1]

    # Cut Selected Text
    nwGUI.docEditor.replaceText(text)
    nwGUI.docEditor.setCursorPosition(1000)
    assert nwGUI.docEditor.docAction(nwDocAction.SEL_PARA) is True
    assert nwGUI.docEditor.docAction(nwDocAction.CUT) is True

    newText = nwGUI.docEditor.getText()
    newPara = list(filter(str.strip, newText.split("\n")))
    assert newPara[0] == "### A Scene"
    assert newPara[1] == ipsumText[0]
    assert newPara[2] == ipsumText[2]
    assert newPara[3] == ipsumText[3]
    assert newPara[4] == ipsumText[4]

    # Paste Back In
    assert nwGUI.docEditor.docAction(nwDocAction.PASTE) is True
    assert nwGUI.docEditor.getText() == text

    # Copy Next Paragraph
    nwGUI.docEditor.replaceText(text)
    nwGUI.docEditor.setCursorPosition(1500)
    assert nwGUI.docEditor.docAction(nwDocAction.SEL_PARA) is True
    assert nwGUI.docEditor.docAction(nwDocAction.COPY) is True

    # Paste at End
    nwGUI.docEditor.setCursorPosition(theDoc.characterCount())
    theCursor = nwGUI.docEditor.textCursor()
    theCursor.insertBlock()
    theCursor.insertBlock()

    assert nwGUI.docEditor.docAction(nwDocAction.PASTE) is True
    newText = nwGUI.docEditor.getText()
    newPara = list(filter(str.strip, newText.split("\n")))
    assert newPara[5] == ipsumText[4]
    assert newPara[6] == ipsumText[2]

    qApp.clipboard().clear()

    # Emphasis/Undo/Redo
    # ==================

    text = "### A Scene\n\n%s" % ipsumText[0]
    nwGUI.docEditor.replaceText(text)

    # Emphasis
    nwGUI.docEditor.setCursorPosition(50)
    assert nwGUI.docEditor.docAction(nwDocAction.EMPH) is True
    assert nwGUI.docEditor.getText() == text.replace("consectetur", "_consectetur_")
    assert nwGUI.docEditor.docAction(nwDocAction.UNDO) is True
    assert nwGUI.docEditor.getText() == text

    # Strong
    nwGUI.docEditor.setCursorPosition(50)
    assert nwGUI.docEditor.docAction(nwDocAction.STRONG) is True
    assert nwGUI.docEditor.getText() == text.replace("consectetur", "**consectetur**")
    assert nwGUI.docEditor.docAction(nwDocAction.UNDO) is True
    assert nwGUI.docEditor.getText() == text

    # Strikeout
    nwGUI.docEditor.setCursorPosition(50)
    assert nwGUI.docEditor.docAction(nwDocAction.STRIKE) is True
    assert nwGUI.docEditor.getText() == text.replace("consectetur", "~~consectetur~~")
    assert nwGUI.docEditor.docAction(nwDocAction.UNDO) is True
    assert nwGUI.docEditor.getText() == text

    # Redo
    assert nwGUI.docEditor.docAction(nwDocAction.REDO) is True
    assert nwGUI.docEditor.getText() == text.replace("consectetur", "~~consectetur~~")
    assert nwGUI.docEditor.docAction(nwDocAction.UNDO) is True
    assert nwGUI.docEditor.getText() == text

    # Shortcodes
    # ==========

    text = "### A Scene\n\n%s" % ipsumText[0]
    nwGUI.docEditor.replaceText(text)

    # Italic
    nwGUI.docEditor.setCursorPosition(46)
    assert nwGUI.docEditor.docAction(nwDocAction.SC_ITALIC) is True
    assert nwGUI.docEditor.getText() == text.replace("consectetur", "[i]consectetur[/i]")
    assert nwGUI.docEditor.docAction(nwDocAction.UNDO) is True
    assert nwGUI.docEditor.getText() == text

    # Bold
    nwGUI.docEditor.setCursorPosition(46)
    assert nwGUI.docEditor.docAction(nwDocAction.SC_BOLD) is True
    assert nwGUI.docEditor.getText() == text.replace("consectetur", "[b]consectetur[/b]")
    assert nwGUI.docEditor.docAction(nwDocAction.UNDO) is True
    assert nwGUI.docEditor.getText() == text

    # Strikethrough
    nwGUI.docEditor.setCursorPosition(46)
    assert nwGUI.docEditor.docAction(nwDocAction.SC_STRIKE) is True
    assert nwGUI.docEditor.getText() == text.replace("consectetur", "[s]consectetur[/s]")
    assert nwGUI.docEditor.docAction(nwDocAction.UNDO) is True
    assert nwGUI.docEditor.getText() == text

    # Underline
    nwGUI.docEditor.setCursorPosition(46)
    assert nwGUI.docEditor.docAction(nwDocAction.SC_ULINE) is True
    assert nwGUI.docEditor.getText() == text.replace("consectetur", "[u]consectetur[/u]")
    assert nwGUI.docEditor.docAction(nwDocAction.UNDO) is True
    assert nwGUI.docEditor.getText() == text

    # Superscript
    nwGUI.docEditor.setCursorPosition(46)
    assert nwGUI.docEditor.docAction(nwDocAction.SC_SUP) is True
    assert nwGUI.docEditor.getText() == text.replace("consectetur", "[sup]consectetur[/sup]")
    assert nwGUI.docEditor.docAction(nwDocAction.UNDO) is True
    assert nwGUI.docEditor.getText() == text

    # Subscript
    nwGUI.docEditor.setCursorPosition(46)
    assert nwGUI.docEditor.docAction(nwDocAction.SC_SUB) is True
    assert nwGUI.docEditor.getText() == text.replace("consectetur", "[sub]consectetur[/sub]")
    assert nwGUI.docEditor.docAction(nwDocAction.UNDO) is True
    assert nwGUI.docEditor.getText() == text

    # Quotes
    # ======

    text = "### A Scene\n\n%s" % ipsumText[0]
    nwGUI.docEditor.replaceText(text)

    # Add Single Quotes
    nwGUI.docEditor.setCursorPosition(50)
    assert nwGUI.docEditor.docAction(nwDocAction.S_QUOTE) is True
    assert nwGUI.docEditor.getText() == text.replace("consectetur", "\u2018consectetur\u2019")
    assert nwGUI.docEditor.docAction(nwDocAction.UNDO) is True
    assert nwGUI.docEditor.getText() == text

    # Add Double Quotes
    nwGUI.docEditor.setCursorPosition(50)
    assert nwGUI.docEditor.docAction(nwDocAction.D_QUOTE) is True
    assert nwGUI.docEditor.getText() == text.replace("consectetur", "\u201cconsectetur\u201d")
    assert nwGUI.docEditor.docAction(nwDocAction.UNDO) is True
    assert nwGUI.docEditor.getText() == text

    # Replace Single Quotes
    repText = text.replace("consectetur", "'consectetur'")
    nwGUI.docEditor.replaceText(repText)
    assert nwGUI.docEditor.docAction(nwDocAction.SEL_ALL) is True
    assert nwGUI.docEditor.docAction(nwDocAction.REPL_SNG) is True
    assert nwGUI.docEditor.getText() == text.replace("consectetur", "\u2018consectetur\u2019")

    # Replace Double Quotes
    repText = text.replace("consectetur", "\"consectetur\"")
    nwGUI.docEditor.replaceText(repText)
    assert nwGUI.docEditor.docAction(nwDocAction.SEL_ALL) is True
    assert nwGUI.docEditor.docAction(nwDocAction.REPL_DBL) is True
    assert nwGUI.docEditor.getText() == text.replace("consectetur", "\u201cconsectetur\u201d")

    # Remove Line Breaks
    # ==================

    text = "### A Scene\n\n%s" % ipsumText[0]
    repText = text[:100] + text[100:].replace(" ", "\n", 3)
    nwGUI.docEditor.replaceText(repText)
    assert nwGUI.docEditor.docAction(nwDocAction.RM_BREAKS) is True
    assert nwGUI.docEditor.getText().strip() == text.strip()

    # Format Block
    # ============

    text = "## Scene Title\n\nScene text.\n\n"
    nwGUI.docEditor.replaceText(text)

    # Header 1
    nwGUI.docEditor.setCursorPosition(0)
    assert nwGUI.docEditor.docAction(nwDocAction.BLOCK_H1) is True
    assert nwGUI.docEditor.getText() == "# Scene Title\n\nScene text.\n\n"

    # Header 2
    nwGUI.docEditor.setCursorPosition(0)
    assert nwGUI.docEditor.docAction(nwDocAction.BLOCK_H2) is True
    assert nwGUI.docEditor.getText() == "## Scene Title\n\nScene text.\n\n"

    # Header 3
    nwGUI.docEditor.setCursorPosition(0)
    assert nwGUI.docEditor.docAction(nwDocAction.BLOCK_H3) is True
    assert nwGUI.docEditor.getText() == "### Scene Title\n\nScene text.\n\n"

    # Header 4
    nwGUI.docEditor.setCursorPosition(0)
    assert nwGUI.docEditor.docAction(nwDocAction.BLOCK_H4) is True
    assert nwGUI.docEditor.getText() == "#### Scene Title\n\nScene text.\n\n"

    # Comment
    nwGUI.docEditor.setCursorPosition(20)
    assert nwGUI.docEditor.docAction(nwDocAction.BLOCK_COM) is True
    assert nwGUI.docEditor.getText() == "#### Scene Title\n\n% Scene text.\n\n"

    # Text
    nwGUI.docEditor.setCursorPosition(20)
    assert nwGUI.docEditor.docAction(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "#### Scene Title\n\nScene text.\n\n"

    # Align Left
    nwGUI.docEditor.setCursorPosition(20)
    assert nwGUI.docEditor.docAction(nwDocAction.ALIGN_L) is True
    assert nwGUI.docEditor.getText() == "#### Scene Title\n\nScene text. <<\n\n"

    # Align Right
    nwGUI.docEditor.setCursorPosition(20)
    assert nwGUI.docEditor.docAction(nwDocAction.ALIGN_R) is True
    assert nwGUI.docEditor.getText() == "#### Scene Title\n\n>> Scene text.\n\n"

    # Align Centre
    nwGUI.docEditor.setCursorPosition(20)
    assert nwGUI.docEditor.docAction(nwDocAction.ALIGN_C) is True
    assert nwGUI.docEditor.getText() == "#### Scene Title\n\n>> Scene text. <<\n\n"

    # Indent Left
    nwGUI.docEditor.setCursorPosition(20)
    assert nwGUI.docEditor.docAction(nwDocAction.INDENT_L) is True
    assert nwGUI.docEditor.getText() == "#### Scene Title\n\n> Scene text.\n\n"

    # Indent Right
    nwGUI.docEditor.setCursorPosition(20)
    assert nwGUI.docEditor.docAction(nwDocAction.INDENT_R) is True
    assert nwGUI.docEditor.getText() == "#### Scene Title\n\n> Scene text. <\n\n"

    # Text (Reset)
    nwGUI.docEditor.setCursorPosition(20)
    assert nwGUI.docEditor.docAction(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "#### Scene Title\n\nScene text.\n\n"

    # Invalid Actions
    # ===============

    # No Document Handle
    nwGUI.docEditor._docHandle = None
    assert nwGUI.docEditor.docAction(nwDocAction.BLOCK_TXT) is False
    nwGUI.docEditor._docHandle = C.hSceneDoc

    # Wrong Action Type
    assert nwGUI.docEditor.docAction(None) is False

    # Unknown Action
    assert nwGUI.docEditor.docAction(nwDocAction.NO_ACTION) is False

    # qtbot.stop()

# END Test testGuiEditor_Actions


@pytest.mark.gui
def testGuiEditor_ToolBar(qtbot, nwGUI, projPath, mockRnd):
    """Test the document actions. This is not an extensive test of the
    action features, just that the actions are actually called. The
    various action features are tested when their respective functions
    are tested.
    """
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True

    docEditor: GuiDocEditor = nwGUI.docEditor
    docToolBar: GuiDocToolBar = docEditor.docToolBar

    text = (
        "### A Scene\n\n"
        "Text bold one\n\n"
        "Text bold two\n\n"
        "Text italic one\n\n"
        "Text italic two\n\n"
        "Text strikethrough one\n\n"
        "Text strikethrough two\n\n"
        "Text underline one\n\n"
        "Text superscript one\n\n"
        "Text subscript one\n\n"
    )
    length = len(text)
    docEditor.replaceText(text)
    assert len(docEditor.getText()) == length

    # Show the ToolBar
    assert docToolBar.isVisible() is False
    docEditor._toggleToolBarVisibility()
    assert docToolBar.isVisible() is True

    # Markdown Mode
    assert docToolBar.tbMode.isChecked() is False

    # Click Bold
    docEditor.setCursorPosition(20)
    docToolBar.tbBold.click()
    assert len(docEditor.getText()) == length + 4

    # Click Italic
    docEditor.setCursorPosition(54)
    docToolBar.tbItalic.click()
    assert len(docEditor.getText()) == length + 6

    # Click Strikethrough
    docEditor.setCursorPosition(90)
    docToolBar.tbStrike.click()
    assert len(docEditor.getText()) == length + 10

    # Shortcode Mode
    docToolBar.tbMode.click()
    assert docToolBar.tbMode.isChecked() is True

    # Click Bold
    docEditor.setCursorPosition(39)
    docToolBar.tbBold.click()
    assert len(docEditor.getText()) == length + 17

    # Click Italic
    docEditor.setCursorPosition(80)
    docToolBar.tbItalic.click()
    assert len(docEditor.getText()) == length + 24

    # Click Strikethrough
    docEditor.setCursorPosition(132)
    docToolBar.tbStrike.click()
    assert len(docEditor.getText()) == length + 31

    # Click Underline
    docEditor.setCursorPosition(163)
    docToolBar.tbUnderline.click()
    assert len(docEditor.getText()) == length + 38

    # Click Superscript
    docEditor.setCursorPosition(190)
    docToolBar.tbSuperscript.click()
    assert len(docEditor.getText()) == length + 49

    # Click Subscript
    docEditor.setCursorPosition(223)
    docToolBar.tbSubscript.click()
    assert len(docEditor.getText()) == length + 60

    # Check Result
    assert docEditor.getText() == (
        "### A Scene\n\n"
        "Text **bold** one\n\n"
        "Text [b]bold[/b] two\n\n"
        "Text _italic_ one\n\n"
        "Text [i]italic[/i] two\n\n"
        "Text ~~strikethrough~~ one\n\n"
        "Text [s]strikethrough[/s] two\n\n"
        "Text [u]underline[/u] one\n\n"
        "Text [sup]superscript[/sup] one\n\n"
        "Text [sub]subscript[/sub] one\n\n"
    )

    # qtbot.stop()

# END Test testGuiEditor_ToolBar


@pytest.mark.gui
def testGuiEditor_Insert(qtbot, monkeypatch, nwGUI, projPath, ipsumText, mockRnd):
    """Test the document insert functions."""
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True

    text = "### A Scene\n\n%s" % "\n\n".join(ipsumText)
    nwGUI.docEditor.replaceText(text)

    # Insert Text
    # ===========

    text = "### A Scene\n\n%s" % ipsumText[0]
    nwGUI.docEditor.replaceText(text)

    # No Document Handle
    nwGUI.docEditor._docHandle = None
    nwGUI.docEditor.setCursorPosition(24)
    assert nwGUI.docEditor.insertText("Stuff") is False
    nwGUI.docEditor._docHandle = C.hSceneDoc

    # Insert String
    nwGUI.docEditor.setCursorPosition(24)
    assert nwGUI.docEditor.insertText(", ipsumer,") is True
    assert nwGUI.docEditor.getText() == text[:24] + ", ipsumer," + text[24:]

    # Single Quotes
    nwGUI.docEditor.replaceText(text)
    nwGUI.docEditor.setCursorPosition(41)
    assert nwGUI.docEditor.insertText(nwDocInsert.QUOTE_LS) is True
    nwGUI.docEditor.setCursorPosition(53)
    assert nwGUI.docEditor.insertText(nwDocInsert.QUOTE_RS) is True
    assert nwGUI.docEditor.getText() == text.replace("consectetur", "\u2018consectetur\u2019")

    # Double Quotes
    nwGUI.docEditor.replaceText(text)
    nwGUI.docEditor.setCursorPosition(41)
    assert nwGUI.docEditor.insertText(nwDocInsert.QUOTE_LD) is True
    nwGUI.docEditor.setCursorPosition(53)
    assert nwGUI.docEditor.insertText(nwDocInsert.QUOTE_RD) is True
    assert nwGUI.docEditor.getText() == text.replace("consectetur", "\u201cconsectetur\u201d")

    # Invalid Inserts
    assert nwGUI.docEditor.insertText(nwDocInsert.NO_INSERT) is False
    assert nwGUI.docEditor.insertText(123) is False

    # Insert KeyWords
    # ===============

    text = "### A Scene\n\n\n%s" % ipsumText[0]
    nwGUI.docEditor.replaceText(text)
    nwGUI.docEditor.setCursorLine(3)

    # Invalid Keyword
    assert nwGUI.docEditor.insertKeyWord("stuff") is False
    assert nwGUI.docEditor.getText() == text

    # Valid Keyword
    assert nwGUI.docEditor.insertKeyWord(nwKeyWords.POV_KEY) is True
    assert nwGUI.docEditor.insertText("Jane\n")
    assert nwGUI.docEditor.getText() == text.replace(
        "\n\n\n", "\n\n@pov: Jane\n\n", 1
    )

    # Invalid Block
    with monkeypatch.context() as mp:
        mp.setattr(QTextBlock, "isValid", lambda *a, **k: False)
        assert nwGUI.docEditor.insertKeyWord(nwKeyWords.POV_KEY) is False

    # Insert In-Block
    nwGUI.docEditor.setCursorPosition(20)
    assert nwGUI.docEditor.insertKeyWord(nwKeyWords.CHAR_KEY) is True
    assert nwGUI.docEditor.insertText("John")
    assert nwGUI.docEditor.getText() == text.replace(
        "\n\n\n", "\n\n@pov: Jane\n@char: John\n\n", 1
    )

    # qtbot.stop()

# END Test testGuiEditor_Insert


@pytest.mark.gui
def testGuiEditor_TextManipulation(qtbot, monkeypatch, nwGUI, projPath, ipsumText, mockRnd):
    """Test the text manipulation functions."""
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True

    text = "### A Scene\n\n%s" % "\n\n".join(ipsumText)
    nwGUI.docEditor.replaceText(text)

    # Clear Surrounding
    # =================

    # No Selection
    text = "### A Scene\n\n%s" % ipsumText[0]
    nwGUI.docEditor.replaceText(text)
    nwGUI.docEditor.setCursorPosition(45)

    cursor = nwGUI.docEditor.textCursor()
    assert nwGUI.docEditor._clearSurrounding(cursor, 1) is False

    # Clear Characters, 1 Layer
    repText = text.replace("consectetur", "=consectetur=")
    nwGUI.docEditor.replaceText(repText)
    nwGUI.docEditor.setCursorPosition(45)

    cursor = nwGUI.docEditor.textCursor()
    cursor.select(QTextCursor.WordUnderCursor)
    assert nwGUI.docEditor._clearSurrounding(cursor, 1) is True
    assert nwGUI.docEditor.getText() == text

    # Clear Characters, 2 Layers
    repText = text.replace("consectetur", "==consectetur==")
    nwGUI.docEditor.replaceText(repText)
    nwGUI.docEditor.setCursorPosition(45)

    cursor = nwGUI.docEditor.textCursor()
    cursor.select(QTextCursor.WordUnderCursor)
    assert nwGUI.docEditor._clearSurrounding(cursor, 2) is True
    assert nwGUI.docEditor.getText() == text

    # Wrap Selection
    # ==============

    text = "### A Scene\n\n%s" % "\n\n".join(ipsumText[0:2])
    nwGUI.docEditor.replaceText(text)
    nwGUI.docEditor.setCursorPosition(45)

    # No Selection
    with monkeypatch.context() as mp:
        mp.setattr(nwGUI.docEditor, "_autoSelect", lambda: QTextCursor())
        assert nwGUI.docEditor._wrapSelection("=", "=") is False

    # Wrap Equal
    nwGUI.docEditor.replaceText(text)
    nwGUI.docEditor.setCursorPosition(45)
    assert nwGUI.docEditor._wrapSelection("=") is True
    assert nwGUI.docEditor.getText() == text.replace("consectetur", "=consectetur=")

    # Wrap Unequal
    nwGUI.docEditor.replaceText(text)
    nwGUI.docEditor.setCursorPosition(45)
    assert nwGUI.docEditor._wrapSelection("=", "*") is True
    assert nwGUI.docEditor.getText() == text.replace("consectetur", "=consectetur*")

    # Past Paragraph
    nwGUI.docEditor.replaceText(text)
    cursor = nwGUI.docEditor.textCursor()
    cursor.setPosition(13, QTextCursor.MoveAnchor)
    cursor.setPosition(1000, QTextCursor.KeepAnchor)
    nwGUI.docEditor.setTextCursor(cursor)
    assert nwGUI.docEditor._wrapSelection("=") is True

    newText = nwGUI.docEditor.getText()
    newPara = list(filter(str.strip, newText.split("\n")))
    assert newPara[1] == "="+ipsumText[0]+"="
    assert newPara[2] == ipsumText[1]

    # Toggle Format
    # =============

    text = "### A Scene\n\n%s" % "\n\n".join(ipsumText[0:2])
    nwGUI.docEditor.replaceText(text)
    nwGUI.docEditor.setCursorPosition(45)

    # No Selection
    with monkeypatch.context() as mp:
        mp.setattr(nwGUI.docEditor, "_autoSelect", lambda: QTextCursor())
        assert nwGUI.docEditor._toggleFormat(2, "=") is False

    # Wrap Single Equal
    nwGUI.docEditor.replaceText(text)
    nwGUI.docEditor.setCursorPosition(45)
    assert nwGUI.docEditor._toggleFormat(1, "=") is True
    assert nwGUI.docEditor.getText() == text.replace("consectetur", "=consectetur=")

    # Past Paragraph
    nwGUI.docEditor.replaceText(text)
    cursor = nwGUI.docEditor.textCursor()
    cursor.setPosition(13, QTextCursor.MoveAnchor)
    cursor.setPosition(1000, QTextCursor.KeepAnchor)
    nwGUI.docEditor.setTextCursor(cursor)
    assert nwGUI.docEditor._toggleFormat(1, "=") is True

    newText = nwGUI.docEditor.getText()
    newPara = list(filter(str.strip, newText.split("\n")))
    assert newPara[1] == "="+ipsumText[0]+"="
    assert newPara[2] == ipsumText[1]

    # Wrap Double Equal
    nwGUI.docEditor.replaceText(text)
    nwGUI.docEditor.setCursorPosition(45)
    assert nwGUI.docEditor._toggleFormat(2, "=") is True
    assert nwGUI.docEditor.getText() == text.replace("consectetur", "==consectetur==")

    # Toggle Double Equal
    nwGUI.docEditor.replaceText(text)
    nwGUI.docEditor.setCursorPosition(45)
    assert nwGUI.docEditor._toggleFormat(2, "=") is True
    assert nwGUI.docEditor._toggleFormat(2, "=") is True
    assert nwGUI.docEditor.getText() == text

    # Toggle Triple+Double Equal
    nwGUI.docEditor.replaceText(text)
    nwGUI.docEditor.setCursorPosition(45)
    assert nwGUI.docEditor._toggleFormat(3, "=") is True
    assert nwGUI.docEditor._toggleFormat(2, "=") is True
    assert nwGUI.docEditor.getText() == text.replace("consectetur", "=consectetur=")

    # Toggle Unequal
    repText = text.replace("consectetur", "=consectetur==")
    nwGUI.docEditor.replaceText(repText)
    nwGUI.docEditor.setCursorPosition(45)
    assert nwGUI.docEditor._toggleFormat(1, "=") is True
    assert nwGUI.docEditor.getText() == text.replace("consectetur", "consectetur=")
    assert nwGUI.docEditor._toggleFormat(1, "=") is True
    assert nwGUI.docEditor.getText() == repText

    # Replace Quotes
    # ==============

    # No Selection
    text = "### A Scene\n\n%s" % ipsumText[0].replace("consectetur", "=consectetur=")
    nwGUI.docEditor.replaceText(text)
    nwGUI.docEditor.setCursorPosition(45)
    assert nwGUI.docEditor._replaceQuotes("=", "<", ">") is False

    # First Paragraph Selected
    # This should not replace anything in second paragraph
    text = "### A Scene\n\n%s" % "\n\n".join(ipsumText[0:2]).replace("ipsum", "=ipsum=")
    nwGUI.docEditor.replaceText(text)
    nwGUI.docEditor.setCursorPosition(45)
    assert nwGUI.docEditor.docAction(nwDocAction.SEL_PARA)
    assert nwGUI.docEditor._replaceQuotes("=", "<", ">") is True

    newText = nwGUI.docEditor.getText()
    newPara = list(filter(str.strip, newText.split("\n")))
    assert newPara[1] == ipsumText[0].replace("ipsum", "<ipsum>")
    assert newPara[2] == ipsumText[1].replace("ipsum", "=ipsum=")

    # Edge of Document
    text = ipsumText[0].replace("Lorem", "=Lorem=")
    nwGUI.docEditor.replaceText(text)
    nwGUI.docEditor.setCursorPosition(45)
    assert nwGUI.docEditor.docAction(nwDocAction.SEL_ALL)
    assert nwGUI.docEditor._replaceQuotes("=", "<", ">") is True
    assert nwGUI.docEditor.getText() == text.replace("=Lorem=", "<Lorem>")

    # Remove Line Breaks
    # ==================

    parOne = ipsumText[0].replace(" ", "\n", 5)
    parTwo = ipsumText[1].replace(" ", "\n", 5)

    # Remove All
    text = "### A Scene\n\n%s\n\n%s" % (parOne, parTwo)
    nwGUI.docEditor.replaceText(text)
    nwGUI.docEditor.setCursorPosition(45)
    nwGUI.docEditor._removeInParLineBreaks()
    assert nwGUI.docEditor.getText() == "### A Scene\n\n%s\n" % "\n\n".join(ipsumText[0:2])

    # Remove First Paragraph
    # Second paragraphs should remain unchanged
    text = "### A Scene\n\n%s\n\n%s" % (parOne, parTwo)
    nwGUI.docEditor.replaceText(text)
    cursor = nwGUI.docEditor.textCursor()
    cursor.setPosition(16, QTextCursor.MoveAnchor)
    cursor.setPosition(680, QTextCursor.KeepAnchor)
    nwGUI.docEditor.setTextCursor(cursor)
    nwGUI.docEditor._removeInParLineBreaks()

    newText = nwGUI.docEditor.getText()
    newPara = list(filter(str.strip, newText.split("\n")))
    twoBits = parTwo.split()
    assert newPara[1] == ipsumText[0]
    assert newPara[2] == twoBits[0]
    assert newPara[3] == twoBits[1]
    assert newPara[4] == twoBits[2]
    assert newPara[5] == twoBits[3]
    assert newPara[6] == twoBits[4]
    assert newPara[7] == " ".join(twoBits[5:])

    # Key Press Events
    # ================
    text = "### A Scene\n\n%s\n\n%s" % (parOne, parTwo)
    nwGUI.docEditor.replaceText(text)
    assert nwGUI.docEditor.getText() == text

    # Select All
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_A, modifier=Qt.ControlModifier, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Delete, delay=KEY_DELAY)
    assert nwGUI.docEditor.getText() == ""

    # Undo
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Z, modifier=Qt.ControlModifier, delay=KEY_DELAY)
    assert nwGUI.docEditor.getText() == text

    # Redo
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Y, modifier=Qt.ControlModifier, delay=KEY_DELAY)
    assert nwGUI.docEditor.getText() == ""

    # qtbot.stop()

# END Test testGuiEditor_TextManipulation


@pytest.mark.gui
def testGuiEditor_BlockFormatting(qtbot, monkeypatch, nwGUI, projPath, ipsumText, mockRnd):
    """Test the block formatting function."""
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True

    # Invalid and Generic
    # ===================

    theText = "### A Scene\n\n%s" % ipsumText[0]
    nwGUI.docEditor.replaceText(theText)

    # Invalid Block
    nwGUI.docEditor.setCursorPosition(0)
    with monkeypatch.context() as mp:
        mp.setattr(QTextBlock, "isValid", lambda *a, **k: False)
        assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is False

    # Keyword
    nwGUI.docEditor.replaceText("@pov: Jane\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is False
    assert nwGUI.docEditor.getText() == "@pov: Jane\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 5

    # Unsupported Format
    nwGUI.docEditor.replaceText("% Comment\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.NO_ACTION) is False

    # Block Stripping : Left Side
    # ===========================

    # Strip Comment w/Space
    nwGUI.docEditor.replaceText("% Comment\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Comment\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 3

    # Strip Comment wo/Space
    nwGUI.docEditor.replaceText("%Comment\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Comment\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 4

    # Strip Header 1
    nwGUI.docEditor.replaceText("# Title\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Title\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 3

    # Strip Header 2
    nwGUI.docEditor.replaceText("## Title\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Title\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 2

    # Strip Header 3
    nwGUI.docEditor.replaceText("### Title\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Title\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 1

    # Strip Header 4
    nwGUI.docEditor.replaceText("#### Title\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Title\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 0

    # Strip Novel Title
    nwGUI.docEditor.replaceText("#! Title\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Title\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 2

    # Strip Unnumbered CHapter
    nwGUI.docEditor.replaceText("##! Title\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Title\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 1

    # Strip Text
    nwGUI.docEditor.replaceText("Generic text\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Generic text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 5

    # Strip Left Angle Brackets : Double w/Space
    nwGUI.docEditor.replaceText(">> Some text\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 2

    # Strip Left Angle Brackets : Single w/Space
    nwGUI.docEditor.replaceText("> Some text\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 3

    # Strip Left Angle Brackets : Double wo/Space
    nwGUI.docEditor.replaceText(">>Some text\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 3

    # Strip Left Angle Brackets : Single wo/Space
    nwGUI.docEditor.replaceText(">Some text\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 4

    # Block Stripping : Right Side
    # ============================

    # Strip Right Angle Brackets : Double w/Space
    nwGUI.docEditor.replaceText("Some text <<\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 5

    # Strip Right Angle Brackets : Single w/Space
    nwGUI.docEditor.replaceText("Some text <\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 5

    # Strip Right Angle Brackets : Double wo/Space
    nwGUI.docEditor.replaceText("Some text<<\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 5

    # Strip Right Angle Brackets : Single wo/Space
    nwGUI.docEditor.replaceText("Some text<\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 5

    # Block Stripping : Both Sides
    # ============================

    nwGUI.docEditor.replaceText(">> Some text <<\n\n")
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"

    nwGUI.docEditor.replaceText(">Some text <<\n\n")
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"

    nwGUI.docEditor.replaceText(">Some text<\n\n")
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"

    # New Formats
    # ===========

    # Comment
    nwGUI.docEditor.replaceText("Some text\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_COM) is True
    assert nwGUI.docEditor.getText() == "% Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 7

    # Toggle Comment w/Space
    nwGUI.docEditor.replaceText("% Some text\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_COM) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 3

    # Toggle Comment wo/Space
    nwGUI.docEditor.replaceText("%Some text\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_COM) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 4

    # Header 1
    nwGUI.docEditor.replaceText("Some text\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_H1) is True
    assert nwGUI.docEditor.getText() == "# Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 7

    # Header 2
    nwGUI.docEditor.replaceText("Some text\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_H2) is True
    assert nwGUI.docEditor.getText() == "## Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 8

    # Header 3
    nwGUI.docEditor.replaceText("Some text\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_H3) is True
    assert nwGUI.docEditor.getText() == "### Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 9

    # Header 4
    nwGUI.docEditor.replaceText("Some text\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_H4) is True
    assert nwGUI.docEditor.getText() == "#### Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 10

    # Novel Title
    nwGUI.docEditor.replaceText("Some text\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TTL) is True
    assert nwGUI.docEditor.getText() == "#! Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 8

    # Unnumbered Chapter
    nwGUI.docEditor.replaceText("Some text\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_UNN) is True
    assert nwGUI.docEditor.getText() == "##! Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 9

    # Left Indent
    nwGUI.docEditor.replaceText("Some text\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.INDENT_L) is True
    assert nwGUI.docEditor.getText() == "> Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 7

    # Right Indent
    nwGUI.docEditor.replaceText("Some text\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.INDENT_R) is True
    assert nwGUI.docEditor.getText() == "Some text <\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 5

    # Right/Left Indent
    nwGUI.docEditor.replaceText("Some text\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.INDENT_L) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.INDENT_R) is True
    assert nwGUI.docEditor.getText() == "> Some text <\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 7

    # Left Align
    nwGUI.docEditor.replaceText("Some text\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.ALIGN_L) is True
    assert nwGUI.docEditor.getText() == "Some text <<\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 5

    # Right Align
    nwGUI.docEditor.replaceText("Some text\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.ALIGN_R) is True
    assert nwGUI.docEditor.getText() == ">> Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 8

    # Centre Align
    nwGUI.docEditor.replaceText("Some text\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.ALIGN_C) is True
    assert nwGUI.docEditor.getText() == ">> Some text <<\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 8

    # Left/Right Align (Overrides)
    nwGUI.docEditor.replaceText("Some text\n\n")
    nwGUI.docEditor.setCursorPosition(5)
    assert nwGUI.docEditor._formatBlock(nwDocAction.ALIGN_L) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.ALIGN_R) is True
    assert nwGUI.docEditor.getText() == ">> Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 8

    # Other Checks
    # ============

    # Final Cursor Position Out of Range
    nwGUI.docEditor.replaceText("#### Title\n\n")
    nwGUI.docEditor.setCursorPosition(3)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Title\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 5

    # Third Line
    # This also needs to add a new block
    nwGUI.docEditor.replaceText("#### Title\n\nThe Text\n\n")
    nwGUI.docEditor.setCursorLine(3)
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_COM) is True
    assert nwGUI.docEditor.getText() == "#### Title\n\n% The Text\n\n"

    # qtbot.stop()

# END Test testGuiEditor_BlockFormatting


@pytest.mark.gui
def testGuiEditor_Tags(qtbot, nwGUI, projPath, ipsumText, mockRnd):
    """Test the document editor tags functionality."""
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True

    # Create Scene
    text = "### A Scene\n\n@char: Jane, John\n\n@object: Gun\n\n@:\n\n" + ipsumText[0] + "\n\n"
    nwGUI.docEditor.replaceText(text)

    # Create Character
    text = "### Jane Doe\n\n@tag: Jane\n\n" + ipsumText[1] + "\n\n"
    cHandle = SHARED.project.newFile("Jane Doe", C.hCharRoot)
    assert nwGUI.openDocument(cHandle) is True
    nwGUI.docEditor.replaceText(text)
    assert nwGUI.saveDocument() is True
    assert nwGUI.projView.projTree.revealNewTreeItem(cHandle)
    nwGUI.docEditor.updateTagHighLighting()

    # Follow Tag
    # ==========
    assert nwGUI.openDocument(C.hSceneDoc) is True

    # Empty Block
    nwGUI.docEditor.setCursorLine(2)
    assert nwGUI.docEditor._processTag() is nwTrinary.UNKNOWN

    # Not On Tag
    nwGUI.docEditor.setCursorLine(1)
    assert nwGUI.docEditor._processTag() is nwTrinary.UNKNOWN

    # On Tag Keyword
    nwGUI.docEditor.setCursorPosition(15)
    assert nwGUI.docEditor._processTag() is nwTrinary.UNKNOWN

    # On Known Tag, No Follow
    nwGUI.docEditor.setCursorPosition(22)
    assert nwGUI.docEditor._processTag(follow=False) is nwTrinary.POSITIVE
    assert nwGUI.docViewer._docHandle is None

    # On Known Tag, Follow
    nwGUI.docEditor.setCursorPosition(22)
    assert nwGUI.docViewer._docHandle is None
    assert nwGUI.docEditor._processTag(follow=True) is nwTrinary.POSITIVE
    assert nwGUI.docViewer._docHandle == cHandle
    assert nwGUI.closeDocViewer() is True
    assert nwGUI.docViewer._docHandle is None

    # On Unknown Tag, Create It
    assert "0000000000011" not in SHARED.project.tree
    nwGUI.docEditor.setCursorPosition(28)
    assert nwGUI.docEditor._processTag(create=True) is nwTrinary.NEGATIVE
    assert "0000000000011" in SHARED.project.tree

    # On Unknown Tag, Missing Root
    assert "0000000000012" not in SHARED.project.tree
    nwGUI.docEditor.setCursorPosition(42)
    assert nwGUI.docEditor._processTag(create=True) is nwTrinary.NEGATIVE
    assert "0000000000012" not in SHARED.project.tree

    nwGUI.docEditor.setCursorPosition(47)
    assert nwGUI.docEditor._processTag() is nwTrinary.UNKNOWN

    # qtbot.stop()

# END Test testGuiEditor_Tags


@pytest.mark.gui
def testGuiEditor_Completer(qtbot, nwGUI, projPath, mockRnd):
    """Test the document editor meta completer functionality."""
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True

    # Create Character
    text = (
        "# Jane Doe\n\n"
        "@tag: Jane\n\n"
        "# John Doe\n\n"
        "@tag: John\n\n"
    )
    cHandle = SHARED.project.newFile("People", C.hCharRoot)
    assert nwGUI.openDocument(cHandle) is True
    nwGUI.docEditor.replaceText(text)
    assert nwGUI.saveDocument() is True
    assert nwGUI.projView.projTree.revealNewTreeItem(cHandle)

    docEditor = nwGUI.docEditor
    docEditor.replaceText("")
    completer = docEditor._completer

    # Create Scene
    nwGUI.switchFocus(nwWidget.EDITOR)
    for c in "### Scene One":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)

    # Type Keyword @
    qtbot.keyClick(docEditor, "@", delay=KEY_DELAY)
    assert len(completer.actions()) == len(nwKeyWords.VALID_KEYS)

    # Type "c" to filer list to 2
    qtbot.keyClick(docEditor, "c", delay=KEY_DELAY)
    assert len(completer.actions()) == 2

    # Type "q" to filer list to 0
    qtbot.keyClick(docEditor, "q", delay=KEY_DELAY)
    assert len(completer.actions()) == 0

    # Delete character and go select @char
    qtbot.keyClick(docEditor, Qt.Key_Backspace, delay=KEY_DELAY)
    assert len(completer.actions()) == 2
    completer.actions()[0].trigger()
    assert docEditor.getText() == (
        "### Scene One\n\n"
        "@char:"
    )

    # The list of Characters should show up automatically
    qtbot.keyClick(docEditor, " ", delay=KEY_DELAY)
    assert [a.text() for a in completer.actions()] == ["Jane", "John"]

    # Typing "q" should clear the list
    qtbot.keyClick(docEditor, "q", delay=KEY_DELAY)
    assert [a.text() for a in completer.actions()] == []

    # Deleting it and typing "a", should leave "Jane"
    qtbot.keyClick(docEditor, Qt.Key_Backspace, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, "a", delay=KEY_DELAY)
    assert [a.text() for a in completer.actions()] == ["Jane"]

    # Selecting "Jane" should insert it
    completer.actions()[0].trigger()
    qtbot.keyClick(docEditor, Qt.Key_Return, delay=KEY_DELAY)
    assert docEditor.getText() == (
        "### Scene One\n\n"
        "@char: Jane\n"
    )

    # Start a new line with a nonsense keyword, which should be handled
    for c in "@: ":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Backspace, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Backspace, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key_Backspace, delay=KEY_DELAY)

    # Send keypresses to the completer object
    qtbot.keyClick(docEditor, "@", delay=KEY_DELAY)
    assert len(completer.actions()) == len(nwKeyWords.VALID_KEYS)
    qtbot.keyClick(completer, "f", delay=KEY_DELAY)
    qtbot.keyClick(completer, Qt.Key_Down, delay=KEY_DELAY)
    qtbot.keyClick(completer, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(completer, " ", delay=KEY_DELAY)
    qtbot.keyClick(completer, "h", delay=KEY_DELAY)
    qtbot.keyClick(completer, Qt.Key_Down, delay=KEY_DELAY)
    qtbot.keyClick(completer, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(completer, Qt.Key_Escape, delay=KEY_DELAY)
    assert docEditor.getText() == (
        "### Scene One\n\n"
        "@char: Jane\n"
        "@focus: John"
    )

    # qtbot.stop()

# END Test testGuiEditor_Completer


@pytest.mark.gui
def testGuiEditor_WordCounters(qtbot, monkeypatch, nwGUI, projPath, ipsumText, mockRnd):
    """Test saving text from the editor."""
    class MockThreadPool:

        def __init__(self):
            self._objID = None

        def start(self, runObj, priority=0):
            self._objID = id(runObj)

        def objectID(self):
            return self._objID

    threadPool = MockThreadPool()
    monkeypatch.setattr(QThreadPool, "globalInstance", lambda *a: threadPool)
    nwGUI.docEditor.wcTimerDoc.blockSignals(True)
    nwGUI.docEditor.wcTimerSel.blockSignals(True)

    buildTestProject(nwGUI, projPath)

    # Run on an empty document
    nwGUI.docEditor._runDocCounter()
    assert nwGUI.docEditor.docFooter.wordsText.text() == "Words: 0 (+0)"
    nwGUI.docEditor._updateDocCounts(0, 0, 0)
    assert nwGUI.docEditor.docFooter.wordsText.text() == "Words: 0 (+0)"

    nwGUI.docEditor._runSelCounter()
    assert nwGUI.docEditor.docFooter.wordsText.text() == "Words: 0 (+0)"
    nwGUI.docEditor._updateSelCounts(0, 0, 0)
    assert nwGUI.docEditor.docFooter.wordsText.text() == "Words: 0 (+0)"

    # Open a document and populate it
    SHARED.project.tree[C.hSceneDoc]._initCount = 0  # type: ignore
    SHARED.project.tree[C.hSceneDoc]._wordCount = 0  # type: ignore
    assert nwGUI.openDocument(C.hSceneDoc) is True

    theText = "\n\n".join(ipsumText)
    cC, wC, pC = countWords(theText)
    nwGUI.docEditor.replaceText(theText)

    # Check that a busy counter is blocked
    with monkeypatch.context() as mp:
        mp.setattr(nwGUI.docEditor.wCounterDoc, "isRunning", lambda *a: True)
        nwGUI.docEditor._runDocCounter()
        assert nwGUI.docEditor.docFooter.wordsText.text() == "Words: 0 (+0)"

    with monkeypatch.context() as mp:
        mp.setattr(nwGUI.docEditor.wCounterSel, "isRunning", lambda *a: True)
        nwGUI.docEditor._runSelCounter()
        assert nwGUI.docEditor.docFooter.wordsText.text() == "Words: 0 (+0)"

    # Run the full word counter
    nwGUI.docEditor._runDocCounter()
    assert threadPool.objectID() == id(nwGUI.docEditor.wCounterDoc)

    nwGUI.docEditor.wCounterDoc.run()
    # nwGUI.docEditor._updateDocCounts(cC, wC, pC)
    assert SHARED.project.tree[C.hSceneDoc]._charCount == cC  # type: ignore
    assert SHARED.project.tree[C.hSceneDoc]._wordCount == wC  # type: ignore
    assert SHARED.project.tree[C.hSceneDoc]._paraCount == pC  # type: ignore
    assert nwGUI.docEditor.docFooter.wordsText.text() == f"Words: {wC} (+{wC})"

    # Select all text
    assert nwGUI.docEditor.docFooter._docSelection is False
    nwGUI.docEditor.docAction(nwDocAction.SEL_ALL)
    assert nwGUI.docEditor.docFooter._docSelection is True

    # Run the selection word counter
    nwGUI.docEditor._runSelCounter()
    assert threadPool.objectID() == id(nwGUI.docEditor.wCounterSel)

    nwGUI.docEditor.wCounterSel.run()
    # nwGUI.docEditor._updateSelCounts(cC, wC, pC)
    assert nwGUI.docEditor.docFooter.wordsText.text() == f"Words: {wC} selected"

    # qtbot.stop()

# END Test testGuiEditor_WordCounters


@pytest.mark.gui
def testGuiEditor_Search(qtbot, monkeypatch, nwGUI, prjLipsum):
    """Test the document editor search functionality."""
    monkeypatch.setattr(GuiDocEditor, "hasFocus", lambda *a: True)

    assert nwGUI.openProject(prjLipsum) is True
    assert nwGUI.openDocument("4c4f28287af27") is True
    origText = nwGUI.docEditor.getText()

    # Select the Word "est"
    nwGUI.docEditor.setCursorPosition(630)
    nwGUI.docEditor._makeSelection(QTextCursor.WordUnderCursor)
    theCursor = nwGUI.docEditor.textCursor()
    assert theCursor.selectedText() == "est"

    # Activate search
    nwGUI.mainMenu.aFind.activate(QAction.Trigger)
    assert nwGUI.docEditor.docSearch.isVisible()
    assert nwGUI.docEditor.docSearch.searchText == "est"

    # Find next by enter key
    monkeypatch.setattr(nwGUI.docEditor.docSearch.searchBox, "hasFocus", lambda: True)
    qtbot.keyClick(nwGUI.docEditor.docSearch.searchBox, Qt.Key_Return, delay=KEY_DELAY)
    assert abs(nwGUI.docEditor.getCursorPosition() - 1284) < 3

    # Find next by button
    qtbot.mouseClick(nwGUI.docEditor.docSearch.searchButton, Qt.LeftButton, delay=KEY_DELAY)
    assert abs(nwGUI.docEditor.getCursorPosition() - 1498) < 3

    # Activate loop search
    nwGUI.docEditor.docSearch.toggleLoop.activate(QAction.Trigger)
    assert nwGUI.docEditor.docSearch.toggleLoop.isChecked()
    assert nwGUI.docEditor.docSearch.doLoop is True

    # Find next by menu Search > Find Next
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 632) < 3

    # Close search
    nwGUI.docEditor.docSearch.cancelSearch.activate(QAction.Trigger)
    assert nwGUI.docEditor.docSearch.isVisible() is False
    nwGUI.docEditor.setCursorPosition(15)

    # Toggle search again with header button
    qtbot.mouseClick(nwGUI.docEditor.docHeader.searchButton, Qt.LeftButton, delay=KEY_DELAY)
    nwGUI.docEditor.docSearch.setSearchText("")
    assert nwGUI.docEditor.docSearch.isVisible() is True

    # Search for non-existing
    nwGUI.docEditor.setCursorPosition(0)
    nwGUI.docEditor.docSearch.setSearchText("abcdef")
    qtbot.mouseClick(nwGUI.docEditor.docSearch.searchButton, Qt.LeftButton, delay=KEY_DELAY)
    assert nwGUI.docEditor.getCursorPosition() < 3  # No result

    # Enable RegEx search
    nwGUI.docEditor.docSearch.toggleRegEx.activate(QAction.Trigger)
    assert nwGUI.docEditor.docSearch.toggleRegEx.isChecked()
    assert nwGUI.docEditor.docSearch.isRegEx is True

    # Set invalid RegEx
    nwGUI.docEditor.setCursorPosition(0)
    nwGUI.docEditor.docSearch.setSearchText(r"\bSus[")
    qtbot.mouseClick(nwGUI.docEditor.docSearch.searchButton, Qt.LeftButton, delay=KEY_DELAY)
    assert nwGUI.docEditor.getCursorPosition() < 3  # No result

    # Set dangerous RegEx (issue #1015)
    # If this doesn't get caught, the app will hang
    nwGUI.docEditor.setCursorPosition(0)
    nwGUI.docEditor.docSearch.setSearchText(r".*")
    qtbot.mouseClick(nwGUI.docEditor.docSearch.searchButton, Qt.LeftButton, delay=KEY_DELAY)
    assert abs(nwGUI.docEditor.getCursorPosition() - 14) < 3

    # Set valid RegEx
    nwGUI.docEditor.docSearch.setSearchText(r"\bSus")
    qtbot.mouseClick(nwGUI.docEditor.docSearch.searchButton, Qt.LeftButton, delay=KEY_DELAY)
    assert abs(nwGUI.docEditor.getCursorPosition() - 208) < 3

    # Find next and then prev
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 309) < 3
    nwGUI.mainMenu.aFindPrev.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 208) < 3

    # Make RegEx case sensitive
    nwGUI.docEditor.docSearch.toggleCase.activate(QAction.Trigger)
    assert nwGUI.docEditor.docSearch.toggleCase.isChecked()
    assert nwGUI.docEditor.docSearch.isCaseSense is True

    # Find next/prev (one result)
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 611) < 3
    nwGUI.mainMenu.aFindPrev.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 611) < 3
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 611) < 3

    # Trigger replace
    nwGUI.mainMenu.aReplace.activate(QAction.Trigger)
    nwGUI.docEditor.docSearch.setReplaceText("foo")

    # Disable RegEx case sensitive
    nwGUI.docEditor.docSearch.toggleCase.activate(QAction.Trigger)
    assert nwGUI.docEditor.docSearch.toggleCase.isChecked() is False
    assert nwGUI.docEditor.docSearch.isCaseSense is False

    # Toggle replace preserve case
    nwGUI.docEditor.docSearch.toggleMatchCap.activate(QAction.Trigger)
    assert nwGUI.docEditor.docSearch.toggleMatchCap.isChecked()
    assert nwGUI.docEditor.docSearch.doMatchCap is True

    # Replace "Sus" with "Foo" via menu
    nwGUI.docEditor.setCursorPosition(590)
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    nwGUI.mainMenu.aReplaceNext.activate(QAction.Trigger)
    assert nwGUI.docEditor.getText()[608:619] == "Foopendisse"

    # Find next/prev to loop file
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 208) < 3
    nwGUI.mainMenu.aFindPrev.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 1790) < 3
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 208) < 3

    # Replace "sus" with "foo" via replace button
    qtbot.mouseClick(nwGUI.docEditor.docSearch.replaceButton, Qt.LeftButton, delay=KEY_DELAY)
    assert nwGUI.docEditor.getText()[205:213] == "foocipit"

    # Revert last two replaces
    assert nwGUI.docEditor.docAction(nwDocAction.UNDO)
    assert nwGUI.docEditor.docAction(nwDocAction.UNDO)
    assert nwGUI.docEditor.getText() == origText

    # Disable RegEx search
    nwGUI.docEditor.docSearch.toggleRegEx.activate(QAction.Trigger)
    assert not nwGUI.docEditor.docSearch.toggleRegEx.isChecked()
    assert nwGUI.docEditor.docSearch.isRegEx is False

    # Close search and select "est" again
    nwGUI.docEditor.docSearch.cancelSearch.activate(QAction.Trigger)
    nwGUI.docEditor.setCursorPosition(630)
    nwGUI.docEditor._makeSelection(QTextCursor.WordUnderCursor)
    theCursor = nwGUI.docEditor.textCursor()
    assert theCursor.selectedText() == "est"

    # Activate search again
    nwGUI.mainMenu.aFind.activate(QAction.Trigger)
    assert nwGUI.docEditor.docSearch.isVisible()
    assert nwGUI.docEditor.docSearch.searchText == "est"

    # Enable full word search
    nwGUI.docEditor.docSearch.toggleWord.activate(QAction.Trigger)
    assert nwGUI.docEditor.docSearch.toggleWord.isChecked()
    assert nwGUI.docEditor.docSearch.isWholeWord is True

    # Only one match
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 632) < 3
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 632) < 3

    # Enable next doc search
    nwGUI.docEditor.docSearch.toggleProject.activate(QAction.Trigger)
    assert nwGUI.docEditor.docSearch.toggleProject.isChecked()
    assert nwGUI.docEditor.docSearch.doNextFile is True

    # Next match
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert nwGUI.docEditor.docHandle == "2426c6f0ca922"  # Next document
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 620) < 3
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 1127) < 3

    # Next doc, no match
    assert nwGUI.docEditor.docSearch.doNextFile is True
    nwGUI.docEditor.docSearch.setSearchText("abcdef")
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert nwGUI.docEditor.docHandle != "2426c6f0ca922"
    assert nwGUI.docEditor.docHandle == "04468803b92e1"
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert nwGUI.docEditor.docHandle != "04468803b92e1"
    assert nwGUI.docEditor.docHandle == "7a992350f3eb6"

    # Toggle Replace
    nwGUI.docEditor.beginReplace()

    # MonkeyPatch the focus cycle. We can't really test this very well, other than
    # check that the tabs aren't captured when the main editor has focus
    monkeypatch.setattr(nwGUI.docEditor, "hasFocus", lambda: True)
    monkeypatch.setattr(nwGUI.docEditor.docSearch.searchBox, "hasFocus", lambda: False)
    monkeypatch.setattr(nwGUI.docEditor.docSearch.replaceBox, "hasFocus", lambda: False)
    assert nwGUI.docEditor.focusNextPrevChild(True) is False

    monkeypatch.setattr(nwGUI.docEditor, "hasFocus", lambda: False)
    monkeypatch.setattr(nwGUI.docEditor.docSearch.searchBox, "hasFocus", lambda: True)
    monkeypatch.setattr(nwGUI.docEditor.docSearch.replaceBox, "hasFocus", lambda: False)
    assert nwGUI.docEditor.focusNextPrevChild(True) is True

    monkeypatch.setattr(nwGUI.docEditor.docSearch.searchBox, "hasFocus", lambda: False)
    monkeypatch.setattr(nwGUI.docEditor.docSearch.replaceBox, "hasFocus", lambda: True)
    assert nwGUI.docEditor.focusNextPrevChild(True) is True

    # qtbot.stop()

# END Test testGuiEditor_Search


@pytest.mark.gui
def testGuiEditor_StaticMethods():
    """Test the document editor's static methods."""
    # Check the method that decides if it is allowed to insert a space
    # before a colon using the French, Spanish, etc language feature
    assert GuiDocEditor._allowSpaceBeforeColon("", "") is True
    assert GuiDocEditor._allowSpaceBeforeColon("", ":") is True
    assert GuiDocEditor._allowSpaceBeforeColon("some text", ":") is True

    assert GuiDocEditor._allowSpaceBeforeColon("@:", ":") is False
    assert GuiDocEditor._allowSpaceBeforeColon("@>", ">") is True

    assert GuiDocEditor._allowSpaceBeforeColon("%", ":") is True
    assert GuiDocEditor._allowSpaceBeforeColon("%:", ":") is True
    assert GuiDocEditor._allowSpaceBeforeColon("%synopsis:", ":") is False
    assert GuiDocEditor._allowSpaceBeforeColon("%Synopsis:", ":") is False
    assert GuiDocEditor._allowSpaceBeforeColon("% synopsis:", ":") is False
    assert GuiDocEditor._allowSpaceBeforeColon("% Synopsis:", ":") is False
    assert GuiDocEditor._allowSpaceBeforeColon("%  synopsis:", ":") is False
    assert GuiDocEditor._allowSpaceBeforeColon("%  Synopsis:", ":") is False
    assert GuiDocEditor._allowSpaceBeforeColon("%synopsis :", ":") is True
    assert GuiDocEditor._allowSpaceBeforeColon("%Synopsis :", ":") is True

# END Test testGuiEditor_StaticMethods
