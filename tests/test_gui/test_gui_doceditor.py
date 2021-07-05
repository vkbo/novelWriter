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

from mock import causeOSError

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextBlock, QTextCursor, QTextOption
from PyQt5.QtWidgets import QAction, QMessageBox, qApp

from nw.gui.doceditor import GuiDocEditor
from nw.enum import nwDocAction, nwDocInsert, nwItemClass, nwItemLayout
from nw.constants import nwKeyWords, nwUnicode

keyDelay = 2
typeDelay = 1
stepDelay = 20


@pytest.mark.gui
def testGuiEditor_Init(qtbot, monkeypatch, nwGUI, nwMinimal, ipsumText):
    """Test initialising the editor.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)

    # Open project
    assert nwGUI.openProject(nwMinimal)
    assert nwGUI.openDocument("8c659a11cd429")

    nwGUI.docEditor.setText("### Lorem Ipsum\n\n%s" % ipsumText[0])
    assert nwGUI.saveDocument()
    qtbot.wait(stepDelay)

    # Check Defaults
    qDoc = nwGUI.docEditor.document()
    assert qDoc.defaultTextOption().alignment() == Qt.AlignLeft
    assert nwGUI.docEditor.verticalScrollBarPolicy() == Qt.ScrollBarAsNeeded
    assert nwGUI.docEditor.horizontalScrollBarPolicy() == Qt.ScrollBarAsNeeded
    assert nwGUI.docEditor._typPadChar == nwUnicode.U_NBSP

    # Check that editor handles settings
    nwGUI.mainConf.textFont = None
    nwGUI.mainConf.doJustify = True
    nwGUI.mainConf.showTabsNSpaces = True
    nwGUI.mainConf.showLineEndings = True
    nwGUI.mainConf.hideVScroll = True
    nwGUI.mainConf.hideHScroll = True
    nwGUI.mainConf.fmtPadThin = True

    assert nwGUI.docEditor.initEditor()

    qDoc = nwGUI.docEditor.document()
    assert nwGUI.mainConf.textFont == qDoc.defaultFont().family()
    assert qDoc.defaultTextOption().alignment() == Qt.AlignJustify
    assert qDoc.defaultTextOption().flags() & QTextOption.ShowTabsAndSpaces
    assert qDoc.defaultTextOption().flags() & QTextOption.ShowLineAndParagraphSeparators
    assert nwGUI.docEditor.verticalScrollBarPolicy() == Qt.ScrollBarAlwaysOff
    assert nwGUI.docEditor.horizontalScrollBarPolicy() == Qt.ScrollBarAlwaysOff
    assert nwGUI.docEditor._typPadChar == nwUnicode.U_THNBSP

    # qtbot.stopForInteraction()

# END Test testGuiEditor_Init


@pytest.mark.gui
def testGuiEditor_LoadText(qtbot, monkeypatch, caplog, nwGUI, nwMinimal, ipsumText):
    """Test loading text into the editor.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)

    # Open project
    sHandle = "8c659a11cd429"
    assert nwGUI.openProject(nwMinimal) is True
    assert nwGUI.openDocument(sHandle) is True

    longText = "### Lorem Ipsum\n\n%s" % "\n\n".join(ipsumText*20)
    nwGUI.docEditor.replaceText(longText)
    assert nwGUI.saveDocument() is True
    assert nwGUI.closeDocument() is True
    qtbot.wait(stepDelay)

    # Load Text
    # =========

    # Invalid handle
    assert nwGUI.docEditor.loadText("abcdefghijklm") is False

    # Document too big
    with monkeypatch.context() as mp:
        mp.setattr("nw.constants.nwConst.MAX_DOCSIZE", 100)
        assert nwGUI.docEditor.loadText(sHandle) is False
        assert "The document you are trying to open is too big." in caplog.text

    # Regular open
    assert nwGUI.docEditor.loadText(sHandle) is True
    assert nwGUI.docEditor._bigDoc is False

    # Reload too big text
    with monkeypatch.context() as mp:
        mp.setattr("nw.constants.nwConst.MAX_DOCSIZE", 100)
        assert nwGUI.docEditor.replaceText(longText) is False
        assert "The document you are trying to open is too big." in caplog.text

    # Big doc handling
    nwGUI.mainConf.bigDocLimit = 50
    assert nwGUI.docEditor.loadText(sHandle) is True
    assert nwGUI.docEditor._bigDoc is True

    # Regular open, with line number
    assert nwGUI.docEditor.loadText(sHandle, tLine=4) is True
    cursPos = nwGUI.docEditor.getCursorPosition()
    assert nwGUI.docEditor.document().findBlock(cursPos).blockNumber() == 4

    # Load empty document
    nwGUI.docEditor.replaceText("")
    assert nwGUI.saveDocument() is True
    assert nwGUI.docEditor.loadText(sHandle) is True
    assert nwGUI.docEditor.toPlainText() == ""

    # qtbot.stopForInteraction()

# END Test testGuiEditor_LoadText


@pytest.mark.gui
def testGuiEditor_SaveText(qtbot, monkeypatch, caplog, nwGUI, nwMinimal, ipsumText):
    """Test saving text from the editor.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)

    # Open project
    sHandle = "8c659a11cd429"
    assert nwGUI.openProject(nwMinimal) is True
    assert nwGUI.openDocument(sHandle) is True
    qtbot.wait(stepDelay)

    # Save Text
    # =========

    longText = "### Lorem Ipsum\n\n%s" % "\n\n".join(ipsumText)
    nwGUI.docEditor.replaceText(longText)

    # Missing item
    nwItem = nwGUI.docEditor._nwItem
    nwGUI.docEditor._nwItem = None
    assert nwGUI.docEditor.saveText() is False
    nwGUI.docEditor._nwItem = nwItem

    # Unkown handle
    nwGUI.docEditor._docHandle = "0123456789abcdef"
    assert nwGUI.docEditor.saveText() is False
    nwGUI.docEditor._docHandle = sHandle

    # Cause error when saving
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert nwGUI.docEditor.saveText() is False
        assert "Could not save document." in caplog.text

    # Change header level
    assert nwGUI.theProject.projTree[sHandle].itemLayout == nwItemLayout.SCENE
    nwGUI.docEditor.replaceText(longText[1:])
    assert nwGUI.docEditor.saveText() is True
    assert nwGUI.theProject.projTree[sHandle].itemLayout == nwItemLayout.CHAPTER

    # Regular save
    assert nwGUI.docEditor.saveText() is True

    # qtbot.stopForInteraction()

# END Test testGuiEditor_SaveText


@pytest.mark.gui
def testGuiEditor_MetaData(qtbot, monkeypatch, nwGUI, nwMinimal):
    """Test extracting various meta data and other values.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)

    # Open project
    sHandle = "8c659a11cd429"
    assert nwGUI.openProject(nwMinimal) is True
    assert nwGUI.openDocument(sHandle) is True
    qtbot.wait(stepDelay)

    # Get Text
    # Both methods should return the same result for line breaks, but not for spaces
    newText = (
        "### New Scene\u2029\u2029"
        "Some\u2028text.\u2029"
        "More\u00a0text.\u2029"
    )
    assert nwGUI.docEditor.replaceText(newText)
    assert nwGUI.docEditor.getText() == "### New Scene\n\nSome\ntext.\nMore\u00a0text.\n"
    verQtValue = nwGUI.mainConf.verQtValue
    nwGUI.mainConf.verQtValue = 50800
    assert nwGUI.docEditor.getText() == "### New Scene\n\nSome\ntext.\nMore text.\n"
    nwGUI.mainConf.verQtValue = verQtValue

    # Check Propertoes
    assert nwGUI.docEditor.docChanged() is True
    assert nwGUI.docEditor.docHandle() == sHandle
    assert nwGUI.docEditor.lastActive() > 0.0
    assert nwGUI.docEditor.isEmpty() is False
    assert nwGUI.docEditor.currentDictionary() is not None

    # Cursor Position
    assert nwGUI.docEditor.setCursorPosition(None) is False
    assert nwGUI.docEditor.setCursorPosition(10) is True
    assert nwGUI.docEditor.getCursorPosition() == 10
    assert nwGUI.theProject.projTree[sHandle].cursorPos != 10
    nwGUI.docEditor.saveCursorPosition()
    assert nwGUI.theProject.projTree[sHandle].cursorPos == 10

    assert nwGUI.docEditor.setCursorLine(None) is False
    assert nwGUI.docEditor.setCursorLine(2) is True
    assert nwGUI.docEditor.getCursorPosition() == 15

    # Document Changed Signal
    nwGUI.docEditor._docChanged = False
    with qtbot.waitSignal(nwGUI.docEditor.docEditedStatusChanged, raising=True, timeout=100):
        nwGUI.docEditor.setDocumentChanged(True)
    assert nwGUI.docEditor._docChanged is True

    # qtbot.stopForInteraction()

# END Test testGuiEditor_MetaData


@pytest.mark.gui
def testGuiEditor_Actions(qtbot, monkeypatch, nwGUI, nwMinimal, ipsumText):
    """Test the document actions. This is not an extensive test of the
    action features, just that the actions are actually called. The
    various action features are tested when their respective functions
    are tested.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)

    # Open project
    sHandle = "8c659a11cd429"
    assert nwGUI.openProject(nwMinimal) is True
    assert nwGUI.openDocument(sHandle) is True
    qtbot.wait(stepDelay)

    theText = "### A Scene\n\n%s" % "\n\n".join(ipsumText)
    assert nwGUI.docEditor.replaceText(theText) is True

    theDoc = nwGUI.docEditor.document()

    # Select/Cut/Copy/Paste/Undo/Redo
    # ===============================

    qApp.clipboard().clear()

    # Select All
    assert nwGUI.docEditor.docAction(nwDocAction.SEL_ALL) is True
    theCursor = nwGUI.docEditor.textCursor()
    assert theCursor.hasSelection() is True
    assert theCursor.selectedText() == theText.replace("\n", "\u2029")
    theCursor.clearSelection()

    # Select Paragraph
    assert nwGUI.docEditor.setCursorPosition(1000) is True
    assert nwGUI.docEditor.getCursorPosition() == 1000
    assert nwGUI.docEditor.docAction(nwDocAction.SEL_PARA) is True
    theCursor = nwGUI.docEditor.textCursor()
    assert theCursor.selectedText() == ipsumText[1]

    # Cut Selected Text
    assert nwGUI.docEditor.replaceText(theText) is True
    assert nwGUI.docEditor.setCursorPosition(1000) is True
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
    assert nwGUI.docEditor.getText() == theText

    # Copy Next Paragraph
    assert nwGUI.docEditor.replaceText(theText) is True
    assert nwGUI.docEditor.setCursorPosition(1500) is True
    assert nwGUI.docEditor.docAction(nwDocAction.SEL_PARA) is True
    assert nwGUI.docEditor.docAction(nwDocAction.COPY) is True

    # Paste at End
    assert nwGUI.docEditor.setCursorPosition(theDoc.characterCount()) is True
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

    theText = "### A Scene\n\n%s" % ipsumText[0]
    assert nwGUI.docEditor.replaceText(theText) is True

    # Emphasis
    assert nwGUI.docEditor.setCursorPosition(50) is True
    assert nwGUI.docEditor.docAction(nwDocAction.EMPH) is True
    assert nwGUI.docEditor.getText() == theText.replace("consectetur", "_consectetur_")
    assert nwGUI.docEditor.docAction(nwDocAction.UNDO) is True
    assert nwGUI.docEditor.getText() == theText

    # Strong
    assert nwGUI.docEditor.setCursorPosition(50) is True
    assert nwGUI.docEditor.docAction(nwDocAction.STRONG) is True
    assert nwGUI.docEditor.getText() == theText.replace("consectetur", "**consectetur**")
    assert nwGUI.docEditor.docAction(nwDocAction.UNDO) is True
    assert nwGUI.docEditor.getText() == theText

    # Strikeout
    assert nwGUI.docEditor.setCursorPosition(50) is True
    assert nwGUI.docEditor.docAction(nwDocAction.STRIKE) is True
    assert nwGUI.docEditor.getText() == theText.replace("consectetur", "~~consectetur~~")
    assert nwGUI.docEditor.docAction(nwDocAction.UNDO) is True
    assert nwGUI.docEditor.getText() == theText

    # Redo
    assert nwGUI.docEditor.docAction(nwDocAction.REDO) is True
    assert nwGUI.docEditor.getText() == theText.replace("consectetur", "~~consectetur~~")
    assert nwGUI.docEditor.docAction(nwDocAction.UNDO) is True
    assert nwGUI.docEditor.getText() == theText

    # Quotes
    # ======

    theText = "### A Scene\n\n%s" % ipsumText[0]
    assert nwGUI.docEditor.replaceText(theText) is True

    # Add Single Quotes
    assert nwGUI.docEditor.setCursorPosition(50) is True
    assert nwGUI.docEditor.docAction(nwDocAction.S_QUOTE) is True
    assert nwGUI.docEditor.getText() == theText.replace("consectetur", "\u2018consectetur\u2019")
    assert nwGUI.docEditor.docAction(nwDocAction.UNDO) is True
    assert nwGUI.docEditor.getText() == theText

    # Add Double Quotes
    assert nwGUI.docEditor.setCursorPosition(50) is True
    assert nwGUI.docEditor.docAction(nwDocAction.D_QUOTE) is True
    assert nwGUI.docEditor.getText() == theText.replace("consectetur", "\u201cconsectetur\u201d")
    assert nwGUI.docEditor.docAction(nwDocAction.UNDO) is True
    assert nwGUI.docEditor.getText() == theText

    # Replace Single Quotes
    repText = theText.replace("consectetur", "'consectetur'")
    assert nwGUI.docEditor.replaceText(repText) is True
    assert nwGUI.docEditor.docAction(nwDocAction.SEL_ALL) is True
    assert nwGUI.docEditor.docAction(nwDocAction.REPL_SNG) is True
    assert nwGUI.docEditor.getText() == theText.replace("consectetur", "\u2018consectetur\u2019")

    # Replace Double Quotes
    repText = theText.replace("consectetur", "\"consectetur\"")
    assert nwGUI.docEditor.replaceText(repText) is True
    assert nwGUI.docEditor.docAction(nwDocAction.SEL_ALL) is True
    assert nwGUI.docEditor.docAction(nwDocAction.REPL_DBL) is True
    assert nwGUI.docEditor.getText() == theText.replace("consectetur", "\u201cconsectetur\u201d")

    # Remove Line Breaks
    # ==================

    theText = "### A Scene\n\n%s" % ipsumText[0]
    repText = theText[:100] + theText[100:].replace(" ", "\n", 3)
    assert nwGUI.docEditor.replaceText(repText) is True
    assert nwGUI.docEditor.docAction(nwDocAction.RM_BREAKS) is True
    assert nwGUI.docEditor.getText().strip() == theText.strip()

    # Format Block
    # ============

    theText = "## Scene Title\n\nScene text.\n\n"
    assert nwGUI.docEditor.replaceText(theText) is True

    # Header 1
    assert nwGUI.docEditor.setCursorPosition(0) is True
    assert nwGUI.docEditor.docAction(nwDocAction.BLOCK_H1) is True
    assert nwGUI.docEditor.getText() == "# Scene Title\n\nScene text.\n\n"

    # Header 2
    assert nwGUI.docEditor.setCursorPosition(0) is True
    assert nwGUI.docEditor.docAction(nwDocAction.BLOCK_H2) is True
    assert nwGUI.docEditor.getText() == "## Scene Title\n\nScene text.\n\n"

    # Header 3
    assert nwGUI.docEditor.setCursorPosition(0) is True
    assert nwGUI.docEditor.docAction(nwDocAction.BLOCK_H3) is True
    assert nwGUI.docEditor.getText() == "### Scene Title\n\nScene text.\n\n"

    # Header 4
    assert nwGUI.docEditor.setCursorPosition(0) is True
    assert nwGUI.docEditor.docAction(nwDocAction.BLOCK_H4) is True
    assert nwGUI.docEditor.getText() == "#### Scene Title\n\nScene text.\n\n"

    # Comment
    assert nwGUI.docEditor.setCursorPosition(20) is True
    assert nwGUI.docEditor.docAction(nwDocAction.BLOCK_COM) is True
    assert nwGUI.docEditor.getText() == "#### Scene Title\n\n% Scene text.\n\n"

    # Text
    assert nwGUI.docEditor.setCursorPosition(20) is True
    assert nwGUI.docEditor.docAction(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "#### Scene Title\n\nScene text.\n\n"

    # Align Left
    assert nwGUI.docEditor.setCursorPosition(20) is True
    assert nwGUI.docEditor.docAction(nwDocAction.ALIGN_L) is True
    assert nwGUI.docEditor.getText() == "#### Scene Title\n\nScene text. <<\n\n"

    # Align Right
    assert nwGUI.docEditor.setCursorPosition(20) is True
    assert nwGUI.docEditor.docAction(nwDocAction.ALIGN_R) is True
    assert nwGUI.docEditor.getText() == "#### Scene Title\n\n>> Scene text.\n\n"

    # Align Centre
    assert nwGUI.docEditor.setCursorPosition(20) is True
    assert nwGUI.docEditor.docAction(nwDocAction.ALIGN_C) is True
    assert nwGUI.docEditor.getText() == "#### Scene Title\n\n>> Scene text. <<\n\n"

    # Indent Left
    assert nwGUI.docEditor.setCursorPosition(20) is True
    assert nwGUI.docEditor.docAction(nwDocAction.INDENT_L) is True
    assert nwGUI.docEditor.getText() == "#### Scene Title\n\n> Scene text.\n\n"

    # Indent Right
    assert nwGUI.docEditor.setCursorPosition(20) is True
    assert nwGUI.docEditor.docAction(nwDocAction.INDENT_R) is True
    assert nwGUI.docEditor.getText() == "#### Scene Title\n\n> Scene text. <\n\n"

    # Text (Reset)
    assert nwGUI.docEditor.setCursorPosition(20) is True
    assert nwGUI.docEditor.docAction(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "#### Scene Title\n\nScene text.\n\n"

    # Invalid Actions
    # ===============

    # No Document Handle
    nwGUI.docEditor._docHandle = None
    assert nwGUI.docEditor.docAction(nwDocAction.BLOCK_TXT) is False
    nwGUI.docEditor._docHandle = sHandle

    # Wrong Action Type
    assert nwGUI.docEditor.docAction(None) is False

    # Unknown Action
    assert nwGUI.docEditor.docAction(nwDocAction.NO_ACTION) is False

    # qtbot.stopForInteraction()

# END Test testGuiEditor_Actions


@pytest.mark.gui
def testGuiEditor_Insert(qtbot, monkeypatch, nwGUI, nwMinimal, ipsumText):
    """Test the document insert functions.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)

    # Open project
    sHandle = "8c659a11cd429"
    assert nwGUI.openProject(nwMinimal) is True
    assert nwGUI.openDocument(sHandle) is True
    qtbot.wait(stepDelay)

    theText = "### A Scene\n\n%s" % "\n\n".join(ipsumText)
    assert nwGUI.docEditor.replaceText(theText) is True

    # Insert Text
    # ===========

    theText = "### A Scene\n\n%s" % ipsumText[0]
    assert nwGUI.docEditor.replaceText(theText) is True

    # No Document Handle
    nwGUI.docEditor._docHandle = None
    assert nwGUI.docEditor.setCursorPosition(24) is True
    assert nwGUI.docEditor.insertText("Stuff") is False
    nwGUI.docEditor._docHandle = sHandle

    # Insert String
    assert nwGUI.docEditor.setCursorPosition(24) is True
    assert nwGUI.docEditor.insertText(", ipsumer,") is True
    assert nwGUI.docEditor.getText() == theText[:24] + ", ipsumer," + theText[24:]

    # Single Quotes
    assert nwGUI.docEditor.replaceText(theText) is True
    assert nwGUI.docEditor.setCursorPosition(41) is True
    assert nwGUI.docEditor.insertText(nwDocInsert.QUOTE_LS) is True
    assert nwGUI.docEditor.setCursorPosition(53) is True
    assert nwGUI.docEditor.insertText(nwDocInsert.QUOTE_RS) is True
    assert nwGUI.docEditor.getText() == theText.replace("consectetur", "\u2018consectetur\u2019")

    # Double Quotes
    assert nwGUI.docEditor.replaceText(theText) is True
    assert nwGUI.docEditor.setCursorPosition(41) is True
    assert nwGUI.docEditor.insertText(nwDocInsert.QUOTE_LD) is True
    assert nwGUI.docEditor.setCursorPosition(53) is True
    assert nwGUI.docEditor.insertText(nwDocInsert.QUOTE_RD) is True
    assert nwGUI.docEditor.getText() == theText.replace("consectetur", "\u201cconsectetur\u201d")

    # Invalid Inserts
    assert nwGUI.docEditor.insertText(nwDocInsert.NO_INSERT) is False
    assert nwGUI.docEditor.insertText(123) is False

    # Insert KeyWords
    # ===============

    theText = "### A Scene\n\n\n%s" % ipsumText[0]
    assert nwGUI.docEditor.replaceText(theText) is True
    assert nwGUI.docEditor.setCursorLine(2)

    # Invalid Keyword
    assert nwGUI.docEditor.insertKeyWord("stuff") is False
    assert nwGUI.docEditor.getText() == theText

    # Valid Keyword
    assert nwGUI.docEditor.insertKeyWord(nwKeyWords.POV_KEY) is True
    assert nwGUI.docEditor.insertText("Jane\n")
    assert nwGUI.docEditor.getText() == theText.replace(
        "\n\n\n", "\n\n@pov: Jane\n\n", 1
    )

    # Invalid Block
    with monkeypatch.context() as mp:
        mp.setattr(QTextBlock, "isValid", lambda *a, **k: False)
        assert nwGUI.docEditor.insertKeyWord(nwKeyWords.POV_KEY) is False

    # Insert In-Block
    assert nwGUI.docEditor.setCursorPosition(20) is True
    assert nwGUI.docEditor.insertKeyWord(nwKeyWords.CHAR_KEY) is True
    assert nwGUI.docEditor.insertText("John")
    assert nwGUI.docEditor.getText() == theText.replace(
        "\n\n\n", "\n\n@pov: Jane\n@char: John\n\n", 1
    )

    # qtbot.stopForInteraction()

# END Test testGuiEditor_Insert


@pytest.mark.gui
def testGuiEditor_TextManipulation(qtbot, monkeypatch, nwGUI, nwMinimal, ipsumText):
    """Test the text manipulation functions.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)

    # Open project
    sHandle = "8c659a11cd429"
    assert nwGUI.openProject(nwMinimal) is True
    assert nwGUI.openDocument(sHandle) is True
    qtbot.wait(stepDelay)

    theText = "### A Scene\n\n%s" % "\n\n".join(ipsumText)
    assert nwGUI.docEditor.replaceText(theText) is True

    # Clear Surrounding
    # =================

    # No Selection
    theText = "### A Scene\n\n%s" % ipsumText[0]
    assert nwGUI.docEditor.replaceText(theText) is True
    assert nwGUI.docEditor.setCursorPosition(45) is True

    theCursor = nwGUI.docEditor.textCursor()
    assert nwGUI.docEditor._clearSurrounding(theCursor, 1) is False

    # Clear Characters, 1 Layer
    repText = theText.replace("consectetur", "=consectetur=")
    assert nwGUI.docEditor.replaceText(repText) is True
    assert nwGUI.docEditor.setCursorPosition(45) is True

    theCursor = nwGUI.docEditor.textCursor()
    theCursor.select(QTextCursor.WordUnderCursor)
    assert nwGUI.docEditor._clearSurrounding(theCursor, 1) is True
    assert nwGUI.docEditor.getText() == theText

    # Clear Characters, 2 Layers
    repText = theText.replace("consectetur", "==consectetur==")
    assert nwGUI.docEditor.replaceText(repText) is True
    assert nwGUI.docEditor.setCursorPosition(45) is True

    theCursor = nwGUI.docEditor.textCursor()
    theCursor.select(QTextCursor.WordUnderCursor)
    assert nwGUI.docEditor._clearSurrounding(theCursor, 2) is True
    assert nwGUI.docEditor.getText() == theText

    # Wrap Selection
    # ==============

    theText = "### A Scene\n\n%s" % "\n\n".join(ipsumText[0:2])
    assert nwGUI.docEditor.replaceText(theText) is True
    assert nwGUI.docEditor.setCursorPosition(45) is True

    # No Selection
    with monkeypatch.context() as mp:
        mp.setattr(nwGUI.docEditor, "_autoSelect", lambda: QTextCursor())
        assert nwGUI.docEditor._wrapSelection("=", "=") is False

    # Wrap Equal
    assert nwGUI.docEditor.replaceText(theText) is True
    assert nwGUI.docEditor.setCursorPosition(45) is True
    assert nwGUI.docEditor._wrapSelection("=") is True
    assert nwGUI.docEditor.getText() == theText.replace("consectetur", "=consectetur=")

    # Wrap Unequal
    assert nwGUI.docEditor.replaceText(theText) is True
    assert nwGUI.docEditor.setCursorPosition(45) is True
    assert nwGUI.docEditor._wrapSelection("=", "*") is True
    assert nwGUI.docEditor.getText() == theText.replace("consectetur", "=consectetur*")

    # Past Paragraph
    assert nwGUI.docEditor.replaceText(theText) is True
    theCursor = nwGUI.docEditor.textCursor()
    theCursor.setPosition(13, QTextCursor.MoveAnchor)
    theCursor.setPosition(1000, QTextCursor.KeepAnchor)
    nwGUI.docEditor.setTextCursor(theCursor)
    assert nwGUI.docEditor._wrapSelection("=") is True

    newText = nwGUI.docEditor.getText()
    newPara = list(filter(str.strip, newText.split("\n")))
    assert newPara[1] == "="+ipsumText[0]+"="
    assert newPara[2] == ipsumText[1]

    # Toggle Format
    # =============

    theText = "### A Scene\n\n%s" % "\n\n".join(ipsumText[0:2])
    assert nwGUI.docEditor.replaceText(theText) is True
    assert nwGUI.docEditor.setCursorPosition(45) is True

    # No Selection
    with monkeypatch.context() as mp:
        mp.setattr(nwGUI.docEditor, "_autoSelect", lambda: QTextCursor())
        assert nwGUI.docEditor._toggleFormat(2, "=") is False

    # Wrap Single Equal
    assert nwGUI.docEditor.replaceText(theText) is True
    assert nwGUI.docEditor.setCursorPosition(45) is True
    assert nwGUI.docEditor._toggleFormat(1, "=") is True
    assert nwGUI.docEditor.getText() == theText.replace("consectetur", "=consectetur=")

    # Past Paragraph
    assert nwGUI.docEditor.replaceText(theText) is True
    theCursor = nwGUI.docEditor.textCursor()
    theCursor.setPosition(13, QTextCursor.MoveAnchor)
    theCursor.setPosition(1000, QTextCursor.KeepAnchor)
    nwGUI.docEditor.setTextCursor(theCursor)
    assert nwGUI.docEditor._toggleFormat(1, "=") is True

    newText = nwGUI.docEditor.getText()
    newPara = list(filter(str.strip, newText.split("\n")))
    assert newPara[1] == "="+ipsumText[0]+"="
    assert newPara[2] == ipsumText[1]

    # Wrap Double Equal
    assert nwGUI.docEditor.replaceText(theText) is True
    assert nwGUI.docEditor.setCursorPosition(45) is True
    assert nwGUI.docEditor._toggleFormat(2, "=") is True
    assert nwGUI.docEditor.getText() == theText.replace("consectetur", "==consectetur==")

    # Toggle Double Equal
    assert nwGUI.docEditor.replaceText(theText) is True
    assert nwGUI.docEditor.setCursorPosition(45) is True
    assert nwGUI.docEditor._toggleFormat(2, "=") is True
    assert nwGUI.docEditor._toggleFormat(2, "=") is True
    assert nwGUI.docEditor.getText() == theText

    # Toggle Triple+Double Equal
    assert nwGUI.docEditor.replaceText(theText) is True
    assert nwGUI.docEditor.setCursorPosition(45) is True
    assert nwGUI.docEditor._toggleFormat(3, "=") is True
    assert nwGUI.docEditor._toggleFormat(2, "=") is True
    assert nwGUI.docEditor.getText() == theText.replace("consectetur", "=consectetur=")

    # Toggle Unequal
    repText = theText.replace("consectetur", "=consectetur==")
    assert nwGUI.docEditor.replaceText(repText) is True
    assert nwGUI.docEditor.setCursorPosition(45) is True
    assert nwGUI.docEditor._toggleFormat(1, "=") is True
    assert nwGUI.docEditor.getText() == theText.replace("consectetur", "consectetur=")
    assert nwGUI.docEditor._toggleFormat(1, "=") is True
    assert nwGUI.docEditor.getText() == repText

    # Replace Quotes
    # ==============

    # No Selection
    theText = "### A Scene\n\n%s" % ipsumText[0].replace("consectetur", "=consectetur=")
    assert nwGUI.docEditor.replaceText(theText) is True
    assert nwGUI.docEditor.setCursorPosition(45) is True
    assert nwGUI.docEditor._replaceQuotes("=", "<", ">") is False

    # First Paragraph Selected
    # This should not replace anything in second paragraph
    theText = "### A Scene\n\n%s" % "\n\n".join(ipsumText[0:2]).replace("ipsum", "=ipsum=")
    assert nwGUI.docEditor.replaceText(theText) is True
    assert nwGUI.docEditor.setCursorPosition(45) is True
    assert nwGUI.docEditor.docAction(nwDocAction.SEL_PARA)
    assert nwGUI.docEditor._replaceQuotes("=", "<", ">") is True

    newText = nwGUI.docEditor.getText()
    newPara = list(filter(str.strip, newText.split("\n")))
    assert newPara[1] == ipsumText[0].replace("ipsum", "<ipsum>")
    assert newPara[2] == ipsumText[1].replace("ipsum", "=ipsum=")

    # Edge of Document
    theText = ipsumText[0].replace("Lorem", "=Lorem=")
    assert nwGUI.docEditor.replaceText(theText) is True
    assert nwGUI.docEditor.setCursorPosition(45) is True
    assert nwGUI.docEditor.docAction(nwDocAction.SEL_ALL)
    assert nwGUI.docEditor._replaceQuotes("=", "<", ">") is True
    assert nwGUI.docEditor.getText() == theText.replace("=Lorem=", "<Lorem>")

    # Remove Line Breaks
    # ==================

    parOne = ipsumText[0].replace(" ", "\n", 5)
    parTwo = ipsumText[1].replace(" ", "\n", 5)

    # Remove All
    theText = "### A Scene\n\n%s\n\n%s" % (parOne, parTwo)
    assert nwGUI.docEditor.replaceText(theText) is True
    assert nwGUI.docEditor.setCursorPosition(45) is True
    assert nwGUI.docEditor._removeInParLineBreaks() is True
    assert nwGUI.docEditor.getText() == "### A Scene\n\n%s\n" % "\n\n".join(ipsumText[0:2])

    # Remove First Paragraph
    # Second paragraphs should remain unchanged
    theText = "### A Scene\n\n%s\n\n%s" % (parOne, parTwo)
    assert nwGUI.docEditor.replaceText(theText) is True
    theCursor = nwGUI.docEditor.textCursor()
    theCursor.setPosition(16, QTextCursor.MoveAnchor)
    theCursor.setPosition(680, QTextCursor.KeepAnchor)
    nwGUI.docEditor.setTextCursor(theCursor)
    assert nwGUI.docEditor._removeInParLineBreaks() is True

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

    # qtbot.stopForInteraction()

# END Test testGuiEditor_TextManipulation


@pytest.mark.gui
def testGuiEditor_BlockFormatting(qtbot, monkeypatch, nwGUI, nwMinimal, ipsumText):
    """Test the block formatting function.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)

    # Open project
    sHandle = "8c659a11cd429"
    assert nwGUI.openProject(nwMinimal) is True
    assert nwGUI.openDocument(sHandle) is True
    qtbot.wait(stepDelay)

    theText = "### A Scene\n\n%s" % "\n\n".join(ipsumText)
    assert nwGUI.docEditor.replaceText(theText) is True

    # Invalid and Generic
    # ===================

    theText = "### A Scene\n\n%s" % ipsumText[0]
    assert nwGUI.docEditor.replaceText(theText) is True

    # Invalid Block
    assert nwGUI.docEditor.setCursorPosition(0) is True
    with monkeypatch.context() as mp:
        mp.setattr(QTextBlock, "isValid", lambda *a, **k: False)
        assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is False

    # Empty Block
    assert nwGUI.docEditor.setCursorLine(1) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is False

    # Keyword
    assert nwGUI.docEditor.replaceText("@pov: Jane\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is False
    assert nwGUI.docEditor.getText() == "@pov: Jane\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 5

    # Unsupported Format
    assert nwGUI.docEditor.replaceText("% Comment\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.NO_ACTION) is False

    # Block Stripping : Left Side
    # ===========================

    # Strip Comment w/Space
    assert nwGUI.docEditor.replaceText("% Comment\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Comment\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 3

    # Strip Comment wo/Space
    assert nwGUI.docEditor.replaceText("%Comment\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Comment\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 4

    # Strip Header 1
    assert nwGUI.docEditor.replaceText("# Title\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Title\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 3

    # Strip Header 2
    assert nwGUI.docEditor.replaceText("## Title\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Title\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 2

    # Strip Header 3
    assert nwGUI.docEditor.replaceText("### Title\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Title\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 1

    # Strip Header 4
    assert nwGUI.docEditor.replaceText("#### Title\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Title\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 0

    # Strip Text
    assert nwGUI.docEditor.replaceText("Generic text\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Generic text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 5

    # Strip Left Angle Brackets : Double w/Space
    assert nwGUI.docEditor.replaceText(">> Some text\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 2

    # Strip Left Angle Brackets : Single w/Space
    assert nwGUI.docEditor.replaceText("> Some text\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 3

    # Strip Left Angle Brackets : Double wo/Space
    assert nwGUI.docEditor.replaceText(">>Some text\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 3

    # Strip Left Angle Brackets : Single wo/Space
    assert nwGUI.docEditor.replaceText(">Some text\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 4

    # Block Stripping : Right Side
    # ============================

    # Strip Right Angle Brackets : Double w/Space
    assert nwGUI.docEditor.replaceText("Some text <<\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 5

    # Strip Right Angle Brackets : Single w/Space
    assert nwGUI.docEditor.replaceText("Some text <\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 5

    # Strip Right Angle Brackets : Double wo/Space
    assert nwGUI.docEditor.replaceText("Some text<<\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 5

    # Strip Right Angle Brackets : Single wo/Space
    assert nwGUI.docEditor.replaceText("Some text<\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 5

    # Block Stripping : Both Sides
    # ============================

    assert nwGUI.docEditor.replaceText(">> Some text <<\n\n") is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"

    assert nwGUI.docEditor.replaceText(">Some text <<\n\n") is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"

    assert nwGUI.docEditor.replaceText(">Some text<\n\n") is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"

    # New Formats
    # ===========

    # Comment
    assert nwGUI.docEditor.replaceText("Some text\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_COM) is True
    assert nwGUI.docEditor.getText() == "% Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 7

    # Toggle Comment w/Space
    assert nwGUI.docEditor.replaceText("% Some text\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_COM) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 3

    # Toggle Comment wo/Space
    assert nwGUI.docEditor.replaceText("%Some text\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_COM) is True
    assert nwGUI.docEditor.getText() == "Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 4

    # Header 1
    assert nwGUI.docEditor.replaceText("Some text\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_H1) is True
    assert nwGUI.docEditor.getText() == "# Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 7

    # Header 2
    assert nwGUI.docEditor.replaceText("Some text\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_H2) is True
    assert nwGUI.docEditor.getText() == "## Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 8

    # Header 3
    assert nwGUI.docEditor.replaceText("Some text\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_H3) is True
    assert nwGUI.docEditor.getText() == "### Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 9

    # Header 4
    assert nwGUI.docEditor.replaceText("Some text\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_H4) is True
    assert nwGUI.docEditor.getText() == "#### Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 10

    # Left Indent
    assert nwGUI.docEditor.replaceText("Some text\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.INDENT_L) is True
    assert nwGUI.docEditor.getText() == "> Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 7

    # Right Indent
    assert nwGUI.docEditor.replaceText("Some text\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.INDENT_R) is True
    assert nwGUI.docEditor.getText() == "Some text <\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 5

    # Right/Left Indent
    assert nwGUI.docEditor.replaceText("Some text\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.INDENT_L) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.INDENT_R) is True
    assert nwGUI.docEditor.getText() == "> Some text <\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 7

    # Left Align
    assert nwGUI.docEditor.replaceText("Some text\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.ALIGN_L) is True
    assert nwGUI.docEditor.getText() == "Some text <<\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 5

    # Right Align
    assert nwGUI.docEditor.replaceText("Some text\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.ALIGN_R) is True
    assert nwGUI.docEditor.getText() == ">> Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 8

    # Centre Align
    assert nwGUI.docEditor.replaceText("Some text\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.ALIGN_C) is True
    assert nwGUI.docEditor.getText() == ">> Some text <<\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 8

    # Left/Right Align (Overrides)
    assert nwGUI.docEditor.replaceText("Some text\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(5) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.ALIGN_L) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.ALIGN_R) is True
    assert nwGUI.docEditor.getText() == ">> Some text\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 8

    # Other Checks
    # ============

    # Final Cursor Position Out of Range
    assert nwGUI.docEditor.replaceText("#### Title\n\n") is True
    assert nwGUI.docEditor.setCursorPosition(3) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert nwGUI.docEditor.getText() == "Title\n\n"
    assert nwGUI.docEditor.getCursorPosition() == 5

    # Second Line
    # This also needs to add a new block
    assert nwGUI.docEditor.replaceText("#### Title\n\nThe Text\n\n") is True
    assert nwGUI.docEditor.setCursorLine(2) is True
    assert nwGUI.docEditor._formatBlock(nwDocAction.BLOCK_COM) is True
    assert nwGUI.docEditor.getText() == "#### Title\n\n% The Text\n\n"

    # qtbot.stopForInteraction()

# END Test testGuiEditor_BlockFormatting


@pytest.mark.gui
def testGuiEditor_Tags(qtbot, monkeypatch, nwGUI, nwMinimal, ipsumText):
    """Test the document editor tags functionality.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)

    # Open project
    sHandle = "8c659a11cd429"
    assert nwGUI.openProject(nwMinimal) is True
    assert nwGUI.openDocument(sHandle) is True
    qtbot.wait(stepDelay)

    # Create Scene
    theText = "### A Scene\n\n@char: Jane, John\n\n" + ipsumText[0] + "\n\n"
    assert nwGUI.docEditor.replaceText(theText) is True

    # Create Character
    theText = "### Jane Doe\n\n@tag: Jane\n\n" + ipsumText[1] + "\n\n"
    cHandle = nwGUI.theProject.newFile("Jane Doe", nwItemClass.CHARACTER, "afb3043c7b2b3")
    assert nwGUI.openDocument(cHandle) is True
    assert nwGUI.docEditor.replaceText(theText) is True
    assert nwGUI.saveDocument() is True
    assert nwGUI.treeView.revealNewTreeItem(cHandle)
    nwGUI.docEditor.updateTagHighLighting()

    # Follow Tag
    # ==========
    assert nwGUI.openDocument(sHandle) is True

    # Empty Block
    assert nwGUI.docEditor.setCursorLine(1) is True
    assert nwGUI.docEditor._followTag() is False

    # Not On Tag
    assert nwGUI.docEditor.setCursorLine(0) is True
    assert nwGUI.docEditor._followTag() is False

    # On Tag Keyword
    assert nwGUI.docEditor.setCursorPosition(15) is True
    assert nwGUI.docEditor._followTag() is False

    # On Unknown Tag
    assert nwGUI.docEditor.setCursorPosition(28) is True
    assert nwGUI.docEditor._followTag() is True
    assert nwGUI.docViewer._docHandle is None

    # On Known Tag, No Follow
    assert nwGUI.docEditor.setCursorPosition(22) is True
    assert nwGUI.docEditor._followTag(loadTag=False) is True
    assert nwGUI.docViewer._docHandle is None

    # On Known Tag, Follow
    assert nwGUI.docEditor.setCursorPosition(22) is True
    assert nwGUI.docViewer._docHandle is None
    assert nwGUI.docEditor._followTag(loadTag=True) is True
    assert nwGUI.docViewer._docHandle == cHandle
    assert nwGUI.closeDocViewer() is True
    assert nwGUI.docViewer._docHandle is None

    # qtbot.stopForInteraction()

# END Test testGuiEditor_Tags


@pytest.mark.gui
def testGuiEditor_Search(qtbot, monkeypatch, nwGUI, nwLipsum):
    """Test the document editor search functionality.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(GuiDocEditor, "hasFocus", lambda *a: True)

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
    assert nwGUI.docEditor.getCursorPosition() < 3  # No result

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
    assert nwGUI.docEditor.docHandle() == "2426c6f0ca922"  # Next document
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 620) < 3
    nwGUI.mainMenu.aFindNext.activate(QAction.Trigger)
    assert abs(nwGUI.docEditor.getCursorPosition() - 1127) < 3

    # Toggle Replace
    nwGUI.docEditor.beginReplace()

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

# END Test testGuiEditor_Search
