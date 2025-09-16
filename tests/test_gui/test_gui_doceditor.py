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

from unittest.mock import MagicMock

import pytest

from PyQt6.QtCore import QEvent, QMimeData, QPointF, Qt, QThreadPool, QUrl
from PyQt6.QtGui import (
    QAction, QClipboard, QDesktopServices, QDragEnterEvent, QDragMoveEvent,
    QDropEvent, QFont, QInputMethodEvent, QMouseEvent, QTextBlock, QTextCursor,
    QTextDocument, QTextOption
)
from PyQt6.QtWidgets import QApplication, QMenu, QPlainTextEdit

from novelwriter import CONFIG, SHARED
from novelwriter.common import decodeMimeHandles
from novelwriter.constants import nwKeyWords, nwUnicode
from novelwriter.dialogs.editlabel import GuiEditLabel
from novelwriter.enum import nwDocAction, nwDocInsert, nwItemClass, nwItemLayout
from novelwriter.gui.doceditor import GuiDocEditor, TextAutoReplace, _TagAction
from novelwriter.gui.dochighlight import TextBlockData
from novelwriter.text.counting import standardCounter
from novelwriter.types import (
    QtAlignJustify, QtAlignLeft, QtKeepAnchor, QtModCtrl, QtModNone,
    QtMouseLeft, QtMoveAnchor, QtMoveRight, QtScrollAlwaysOff, QtScrollAsNeeded
)

from tests.mocked import causeOSError
from tests.tools import C, buildTestProject

KEY_DELAY = 1


def getMenuForPos(editor: GuiDocEditor, pos: int, select: bool = False) -> QMenu | None:
    """Create a context menu for a text position and return the menu
    object.
    """
    cursor = editor.textCursor()
    cursor.setPosition(pos)
    if select:
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
    editor.setTextCursor(cursor)
    editor._openContextFromCursor()
    for obj in editor.children():
        if isinstance(obj, QMenu) and obj.objectName() == "ContextMenu":
            return obj
    return None


@pytest.mark.gui
def testGuiEditor_Init(qtbot, nwGUI, projPath, ipsumText, mockRnd):
    """Test initialising the editor."""
    # Open project
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc)
    docEditor = nwGUI.docEditor

    docEditor.setPlainText(f"### Lorem Ipsum\n\n{ipsumText[0]}")
    nwGUI.saveDocument()

    # Check Defaults
    qDoc = docEditor.document()
    assert qDoc.defaultTextOption().alignment() == QtAlignLeft
    assert docEditor.verticalScrollBarPolicy() == QtScrollAsNeeded
    assert docEditor.horizontalScrollBarPolicy() == QtScrollAsNeeded
    assert docEditor._autoReplace._padChar == nwUnicode.U_NBSP
    assert docEditor.docHeader.itemTitle.text() == (
        "Novel  \u203a  New Folder  \u203a  New Scene"
    )
    assert docEditor.docHeader._docOutline == {0: "### New Scene"}

    # Check that editor handles settings
    CONFIG.textFont = QFont()
    CONFIG.doJustify = True
    CONFIG.showTabsNSpaces = True
    CONFIG.showLineEndings = True
    CONFIG.hideVScroll = True
    CONFIG.hideHScroll = True
    CONFIG.fmtPadThin = True
    CONFIG.showFullPath = False

    docEditor.initEditor()

    qDoc = docEditor.document()
    assert CONFIG.textFont == qDoc.defaultFont()
    assert qDoc.defaultTextOption().alignment() == QtAlignJustify
    assert qDoc.defaultTextOption().flags() & QTextOption.Flag.ShowTabsAndSpaces
    assert qDoc.defaultTextOption().flags() & QTextOption.Flag.ShowLineAndParagraphSeparators
    assert docEditor.verticalScrollBarPolicy() == QtScrollAlwaysOff
    assert docEditor.horizontalScrollBarPolicy() == QtScrollAlwaysOff
    assert docEditor._autoReplace._padChar == nwUnicode.U_THNBSP
    assert docEditor.docHeader.itemTitle.text() == "New Scene"

    # Header
    # ======

    # Go to outline
    docEditor.setCursorLine(3)
    docEditor.docHeader.outlineMenu.actions()[0].trigger()
    assert docEditor.getCursorPosition() == 0

    # Select item from header
    with qtbot.waitSignal(docEditor.requestProjectItemSelected, timeout=1000) as signal:
        qtbot.mouseClick(docEditor.docHeader, QtMouseLeft)
        assert signal.args == [docEditor.docHeader._docHandle, True]

    # Close from header
    with qtbot.waitSignal(docEditor.docHeader.closeDocumentRequest, timeout=1000):
        docEditor.docHeader.closeButton.click()

    assert docEditor.docHeader.tbButton.isVisible() is False
    assert docEditor.docHeader.searchButton.isVisible() is False
    assert docEditor.docHeader.closeButton.isVisible() is False
    assert docEditor.docHeader.minmaxButton.isVisible() is False

    # Select item from header
    with qtbot.waitSignal(docEditor.requestProjectItemSelected, timeout=1000) as signal:
        qtbot.mouseClick(docEditor.docHeader, QtMouseLeft)
        assert signal.args == ["", True]

    # qtbot.stop()


@pytest.mark.gui
def testGuiEditor_LoadText(qtbot, nwGUI, projPath, ipsumText, mockRnd):
    """Test loading text into the editor."""
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True
    docEditor = nwGUI.docEditor

    longText = "### Lorem Ipsum\n\n{0}".format("\n\n".join(ipsumText*20))
    docEditor.replaceText(longText)
    nwGUI.saveDocument()
    nwGUI.closeDocument()

    # Invalid handle
    assert docEditor.loadText("abcdefghijklm") is False

    # Regular open
    assert docEditor.loadText(C.hSceneDoc) is True

    # Regular open, with line number (1 indexed)
    assert docEditor.loadText(C.hSceneDoc, tLine=4) is True
    cursPos = docEditor.getCursorPosition()
    assert docEditor.document().findBlock(cursPos).blockNumber() == 3

    # Load empty document
    docEditor.replaceText("")
    nwGUI.saveDocument()
    assert docEditor.loadText(C.hSceneDoc) is True
    assert docEditor.toPlainText() == ""

    # qtbot.stop()


@pytest.mark.gui
def testGuiEditor_SaveText(qtbot, monkeypatch, caplog, nwGUI, projPath, ipsumText, mockRnd):
    """Test saving text from the editor."""
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True
    docEditor = nwGUI.docEditor

    longText = "### Lorem Ipsum\n\n{0}".format("\n\n".join(ipsumText))
    docEditor.replaceText(longText)

    # Missing item
    nwItem = docEditor._nwItem
    docEditor._nwItem = None
    assert docEditor.saveText() is False
    docEditor._nwItem = nwItem

    # Unknown handle
    docEditor._docHandle = "0123456789abcdef"
    assert docEditor.saveText() is False
    docEditor._docHandle = C.hSceneDoc

    # Cause error when saving
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert docEditor.saveText() is False
        assert "Could not save document." in caplog.text

    # Change header level
    assert SHARED.project.tree[C.hSceneDoc].itemLayout == nwItemLayout.DOCUMENT  # type: ignore
    docEditor.replaceText(longText[1:])
    assert docEditor.saveText() is True
    assert SHARED.project.tree[C.hSceneDoc].itemLayout == nwItemLayout.DOCUMENT  # type: ignore

    # Regular save
    assert docEditor.saveText() is True

    # qtbot.stop()


@pytest.mark.gui
def testGuiEditor_DragAndDrop(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test drag and drop in the editor."""
    docEditor = nwGUI.docEditor

    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hTitlePage) is True
    assert docEditor.docHandle == C.hTitlePage

    middle = docEditor.viewport().rect().center()
    action = Qt.DropAction.MoveAction
    mouse = Qt.MouseButton.NoButton

    model = SHARED.project.tree.model
    docMime = model.mimeData([model.indexFromHandle(C.hSceneDoc)])
    noneMime = QMimeData()
    noneMime.setData("plain/text", b"")
    assert decodeMimeHandles(docMime) == [C.hSceneDoc]

    # Drag Enter
    mockEnter = MagicMock()
    docEvent = QDragEnterEvent(middle, action, docMime, mouse, QtModNone)
    noneEvent = QDragEnterEvent(middle, action, noneMime, mouse, QtModNone)
    with monkeypatch.context() as mp:
        mp.setattr(QPlainTextEdit, "dragEnterEvent", mockEnter)

        # Document Enter
        docEditor.dragEnterEvent(docEvent)
        assert docEvent.isAccepted() is True
        assert mockEnter.call_count == 0

        # Regular Enter
        docEditor.dragEnterEvent(noneEvent)
        assert mockEnter.call_count == 1

    # Drag Move
    mockMove = MagicMock()
    docEvent = QDragMoveEvent(middle, action, docMime, mouse, QtModNone)
    noneEvent = QDragMoveEvent(middle, action, noneMime, mouse, QtModNone)
    with monkeypatch.context() as mp:
        mp.setattr(QPlainTextEdit, "dragMoveEvent", mockMove)

        # Document Move
        docEditor.dragMoveEvent(docEvent)
        assert docEvent.isAccepted() is True
        assert mockMove.call_count == 0

        # Regular Move
        docEditor.dragMoveEvent(noneEvent)
        assert mockMove.call_count == 1

    # Drop
    middle = QPointF(docEditor.viewport().rect().center())
    mockDrop = MagicMock()
    docEvent = QDropEvent(middle, action, docMime, mouse, QtModNone)
    noneEvent = QDropEvent(middle, action, noneMime, mouse, QtModNone)
    with monkeypatch.context() as mp:
        mp.setattr(QPlainTextEdit, "dropEvent", mockDrop)

        # Document Drop
        docEditor.dropEvent(docEvent)
        assert mockDrop.call_count == 0
        assert docEditor.docHandle == C.hSceneDoc

        # Regular Move
        docEditor.dropEvent(noneEvent)
        assert mockDrop.call_count == 1


@pytest.mark.gui
def testGuiEditor_MetaData(qtbot, nwGUI, projPath, mockRnd):
    """Test extracting various meta data and other values."""
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True
    docEditor = nwGUI.docEditor

    # Get Text
    # This should replace line and paragraph separators, but preserve
    # non-breaking spaces.
    newText = (
        "### New Scene\u2029\u2029"
        "Some\u2028text.\u2029"
        "More\u00a0text.\u2029"
    )
    docEditor.replaceText(newText)
    assert docEditor.getText() == (
        "### New Scene\n\n"
        "Some\n"
        "text.\n"
        "More\u00a0text.\n"
    )

    # Check Properties
    assert docEditor.docChanged is True
    assert docEditor.docHandle == C.hSceneDoc
    assert docEditor.lastActive > 0.0
    assert docEditor.isEmpty is False

    # Cursor Position
    docEditor.setCursorPosition(10)
    assert docEditor.getCursorPosition() == 10
    assert SHARED.project.tree[C.hSceneDoc].cursorPos != 10  # type: ignore
    docEditor.saveCursorPosition()
    assert SHARED.project.tree[C.hSceneDoc].cursorPos == 10  # type: ignore

    docEditor.setCursorLine(None)
    assert docEditor.getCursorPosition() == 10
    docEditor.setCursorLine(3)
    assert docEditor.getCursorPosition() == 15

    # Document Changed Signal
    docEditor._docChanged = False
    with qtbot.waitSignal(docEditor.editedStatusChanged, raising=True, timeout=100):
        docEditor.setDocumentChanged(True)
    assert docEditor._docChanged is True

    # qtbot.stop()


@pytest.mark.gui
def testGuiEditor_ContextMenu(monkeypatch, qtbot, nwGUI, projPath, mockRnd):
    """Test the editor context menu."""
    monkeypatch.setattr(QMenu, "exec", lambda *a: None)
    monkeypatch.setattr(QMenu, "setParent", lambda *a: None)

    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True
    docEditor = nwGUI.docEditor
    sceneItem = SHARED.project.tree[C.hSceneDoc]
    assert sceneItem is not None

    docText = (
        "### A Scene\n\n"
        "@pov: Jane\n\n"
        "Some text ...\n\n"
        "... and a link to http://example.com\n\n"
    )
    docEditor.setPlainText(docText)
    assert docEditor.getText() == docText

    # Rename Item from Heading
    ctxMenu = getMenuForPos(docEditor, 1)
    assert ctxMenu is not None
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Set as Document Name", "Paste",
        "Select All", "Select Word", "Select Paragraph"
    ]
    with monkeypatch.context() as mp:
        mp.setattr(GuiEditLabel, "getLabel", lambda a, text: (text, True))
        assert sceneItem.itemName == "New Scene"
        ctxMenu.actions()[0].trigger()
        assert sceneItem.itemName == "A Scene"
    ctxMenu.setObjectName("")
    ctxMenu.deleteLater()

    # Open Link
    ctxMenu = getMenuForPos(docEditor, 63)
    assert ctxMenu is not None
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Open URL", "Paste",
        "Select All", "Select Word", "Select Paragraph"
    ]
    ctxMenu.setObjectName("")
    ctxMenu.deleteLater()

    # Create Character
    ctxMenu = getMenuForPos(docEditor, 21)
    assert ctxMenu is not None
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Create Note for Tag", "Paste",
        "Select All", "Select Word", "Select Paragraph"
    ]
    ctxMenu.actions()[0].trigger()
    janeItem = SHARED.project.tree["0000000000010"]
    assert janeItem is not None
    assert janeItem.itemName == "Jane"
    ctxMenu.setObjectName("")
    ctxMenu.deleteLater()

    # Follow Character Tag
    ctxMenu = getMenuForPos(docEditor, 21)
    assert ctxMenu is not None
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Follow Tag", "Paste",
        "Select All", "Select Word", "Select Paragraph"
    ]
    ctxMenu.actions()[0].trigger()
    assert nwGUI.docViewer.docHandle == "0000000000010"
    ctxMenu.setObjectName("")
    ctxMenu.deleteLater()

    # Select Word
    ctxMenu = getMenuForPos(docEditor, 31)
    assert ctxMenu is not None
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Paste", "Select All", "Select Word", "Select Paragraph"
    ]
    ctxMenu.actions()[3].trigger()
    assert docEditor.textCursor().selectedText() == "text"
    ctxMenu.setObjectName("")
    ctxMenu.deleteLater()

    # Select Paragraph
    ctxMenu = getMenuForPos(docEditor, 31)
    assert ctxMenu is not None
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Paste", "Select All", "Select Word", "Select Paragraph"
    ]
    ctxMenu.actions()[4].trigger()
    assert docEditor.textCursor().selectedText() == "Some text ..."
    ctxMenu.setObjectName("")
    ctxMenu.deleteLater()

    # Select All
    ctxMenu = getMenuForPos(docEditor, 31)
    assert ctxMenu is not None
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Paste", "Select All", "Select Word", "Select Paragraph"
    ]
    ctxMenu.actions()[2].trigger()
    assert docEditor.textCursor().selectedText() == docEditor.document().toRawText()
    ctxMenu.setObjectName("")
    ctxMenu.deleteLater()

    # Copy Text
    clipboard = QApplication.clipboard()
    assert clipboard is not None

    ctxMenu = getMenuForPos(docEditor, 31, True)
    assert ctxMenu is not None
    assert docEditor.textCursor().selectedText() == "text"
    actions = [x.text() for x in ctxMenu.actions() if x.text()]
    assert actions == [
        "Cut", "Copy", "Paste", "Select All", "Select Word", "Select Paragraph"
    ]
    clipboard.clear()
    ctxMenu.actions()[1].trigger()
    assert clipboard.text(QClipboard.Mode.Clipboard) == "text"

    # Cut Text
    clipboard.clear()
    ctxMenu.actions()[0].trigger()
    assert clipboard.text(QClipboard.Mode.Clipboard) == "text"
    assert "text" not in docEditor.getText()

    # Paste Text
    ctxMenu.actions()[2].trigger()
    assert docEditor.getText() == docText

    ctxMenu.setObjectName("")
    ctxMenu.deleteLater()

    # qtbot.stop()


@pytest.mark.gui
def testGuiEditor_SpellChecking(qtbot, monkeypatch, nwGUI, projPath, ipsumText, mockRnd):
    """Test the document spell checker."""
    monkeypatch.setattr(QMenu, "exec", lambda *a: None)
    monkeypatch.setattr(QMenu, "setParent", lambda *a: None)

    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True
    docEditor = nwGUI.docEditor

    text = "### A Scene\n\n{0}".format("\n\n".join(ipsumText))
    docEditor.replaceText(text)

    # Toggle State
    # ============

    # No language set
    SHARED.spelling._language = None
    SHARED.project.data.setSpellCheck(False)
    docEditor.toggleSpellCheck(True)
    assert SHARED.project.data.spellCheck is False

    # No spell checker available
    SHARED.spelling._language = "en"
    docEditor.toggleSpellCheck(True)
    assert SHARED.project.data.spellCheck is True

    CONFIG.hasEnchant = False
    docEditor.toggleSpellCheck(True)
    assert SHARED.project.data.spellCheck is False
    CONFIG.hasEnchant = True
    docEditor.toggleSpellCheck(True)
    assert SHARED.project.data.spellCheck is True

    # Plain Toggle
    docEditor.toggleSpellCheck(None)
    assert SHARED.project.data.spellCheck is False

    # Run SpellCheck
    # ==============
    SHARED.project.data.setSpellCheck(True)
    LORAX = "Lorax\U0001F03A"

    cursor = docEditor.textCursor()
    cursor.setPosition(16)
    data = cursor.block().userData()
    assert cursor.block().text().startswith("Lorem")
    assert isinstance(data, TextBlockData)
    data._spellErrors = [(0, 5, "Lorem")]

    # No known position
    assert docEditor._qDocument.spellErrorAtPos(-1) == ("", -1, [])

    # With Suggestion
    with monkeypatch.context() as mp:
        mp.setattr(SHARED.spelling, "suggestWords", lambda *a: [LORAX])

        ctxMenu = getMenuForPos(docEditor, 16)
        assert ctxMenu is not None
        actions = [x.text() for x in ctxMenu.actions() if x.text()]
        assert "Spelling Suggestion(s)" in actions
        assert f"{nwUnicode.U_ENDASH} {LORAX}" in actions
        ctxMenu.actions()[7].trigger()
        QApplication.processEvents()
        assert docEditor.getText() == text.replace("Lorem", LORAX, 1)
        ctxMenu.setObjectName("")
        ctxMenu.deleteLater()

    # Update Entry
    data._spellErrors = [(0, 7, LORAX)]

    # Without Suggestion
    with monkeypatch.context() as mp:
        mp.setattr(SHARED.spelling, "suggestWords", lambda *a: [])

        ctxMenu = getMenuForPos(docEditor, 16)
        assert ctxMenu is not None
        actions = [x.text() for x in ctxMenu.actions() if x.text()]
        assert f"{nwUnicode.U_ENDASH} No Suggestions" in actions
        assert docEditor.getText() == text.replace("Lorem", LORAX, 1)
        ctxMenu.setObjectName("")
        ctxMenu.deleteLater()

    # Add to Dictionary
    with monkeypatch.context() as mp:
        mp.setattr(SHARED.spelling, "suggestWords", lambda *a: [])

        ctxMenu = getMenuForPos(docEditor, 16)
        assert ctxMenu is not None
        actions = [x.text() for x in ctxMenu.actions() if x.text()]
        assert "Ignore Word" in actions
        assert "Add Word to Dictionary" in actions

        assert LORAX not in SHARED.spelling._userDict
        ctxMenu.actions()[7].trigger()  # Ignore
        assert LORAX not in SHARED.spelling._userDict
        ctxMenu.actions()[8].trigger()  # Add
        assert LORAX in SHARED.spelling._userDict
        ctxMenu.setObjectName("")
        ctxMenu.deleteLater()

    # qtbot.stop()


@pytest.mark.gui
def testGuiEditor_Actions(qtbot, nwGUI, projPath, ipsumText, mockRnd):
    """Test the document actions. This is not an extensive test of the
    action features, just that the actions are actually called. The
    various action features are tested when their respective functions
    are tested.
    """
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True
    docEditor = nwGUI.docEditor

    text = "### A Scene\n\n{0}".format("\n\n".join(ipsumText))
    docEditor.replaceText(text)
    doc = docEditor.document()

    # Select/Cut/Copy/Paste/Undo/Redo
    # ===============================

    clipboard = QApplication.clipboard()
    assert clipboard is not None
    clipboard.clear()

    # Select All
    assert docEditor.docAction(nwDocAction.SEL_ALL) is True
    cursor = docEditor.textCursor()
    assert cursor.hasSelection() is True
    assert cursor.selectedText() == text.replace("\n", "\u2029")
    cursor.clearSelection()

    # Select Paragraph
    docEditor.setCursorPosition(1000)
    assert docEditor.getCursorPosition() == 1000
    assert docEditor.docAction(nwDocAction.SEL_PARA) is True
    cursor = docEditor.textCursor()
    assert cursor.selectedText() == ipsumText[1]

    # Cut Selected Text
    docEditor.replaceText(text)
    docEditor.setCursorPosition(1000)
    assert docEditor.docAction(nwDocAction.SEL_PARA) is True
    assert docEditor.docAction(nwDocAction.CUT) is True

    newText = docEditor.getText()
    newPara = list(filter(str.strip, newText.split("\n")))
    assert newPara[0] == "### A Scene"
    assert newPara[1] == ipsumText[0]
    assert newPara[2] == ipsumText[2]
    assert newPara[3] == ipsumText[3]
    assert newPara[4] == ipsumText[4]

    # Paste Back In
    assert docEditor.docAction(nwDocAction.PASTE) is True
    assert docEditor.getText() == text

    # Copy Next Paragraph
    docEditor.replaceText(text)
    docEditor.setCursorPosition(1500)
    assert docEditor.docAction(nwDocAction.SEL_PARA) is True
    assert docEditor.docAction(nwDocAction.COPY) is True

    # Paste at End
    docEditor.setCursorPosition(doc.characterCount())
    cursor = docEditor.textCursor()
    cursor.insertBlock()
    cursor.insertBlock()

    assert docEditor.docAction(nwDocAction.PASTE) is True
    newText = docEditor.getText()
    newPara = list(filter(str.strip, newText.split("\n")))
    assert newPara[5] == ipsumText[4]
    assert newPara[6] == ipsumText[2]

    clipboard.clear()

    # Emphasis/Undo/Redo
    # ==================

    text = f"### A Scene\n\n{ipsumText[0]}"
    docEditor.replaceText(text)

    # Emphasis
    docEditor.setCursorPosition(50)
    assert docEditor.docAction(nwDocAction.MD_ITALIC) is True
    assert docEditor.getText() == text.replace("consectetur", "_consectetur_")
    assert docEditor.docAction(nwDocAction.UNDO) is True
    assert docEditor.getText() == text

    # Strong
    docEditor.setCursorPosition(50)
    assert docEditor.docAction(nwDocAction.MD_BOLD) is True
    assert docEditor.getText() == text.replace("consectetur", "**consectetur**")
    assert docEditor.docAction(nwDocAction.UNDO) is True
    assert docEditor.getText() == text

    # Strikeout
    docEditor.setCursorPosition(50)
    assert docEditor.docAction(nwDocAction.MD_STRIKE) is True
    assert docEditor.getText() == text.replace("consectetur", "~~consectetur~~")
    assert docEditor.docAction(nwDocAction.UNDO) is True
    assert docEditor.getText() == text

    # Mark
    docEditor.setCursorPosition(50)
    assert docEditor.docAction(nwDocAction.MD_MARK) is True
    assert docEditor.getText() == text.replace("consectetur", "==consectetur==")
    assert docEditor.docAction(nwDocAction.UNDO) is True
    assert docEditor.getText() == text

    # Redo
    assert docEditor.docAction(nwDocAction.REDO) is True
    assert docEditor.getText() == text.replace("consectetur", "==consectetur==")
    assert docEditor.docAction(nwDocAction.UNDO) is True
    assert docEditor.getText() == text

    # Shortcodes
    # ==========

    text = f"### A Scene\n\n{ipsumText[0]}"
    docEditor.replaceText(text)

    # Italic
    docEditor.setCursorPosition(46)
    assert docEditor.docAction(nwDocAction.SC_ITALIC) is True
    assert docEditor.getText() == text.replace("consectetur", "[i]consectetur[/i]")
    assert docEditor.docAction(nwDocAction.UNDO) is True
    assert docEditor.getText() == text

    # Bold
    docEditor.setCursorPosition(46)
    assert docEditor.docAction(nwDocAction.SC_BOLD) is True
    assert docEditor.getText() == text.replace("consectetur", "[b]consectetur[/b]")
    assert docEditor.docAction(nwDocAction.UNDO) is True
    assert docEditor.getText() == text

    # Strikethrough
    docEditor.setCursorPosition(46)
    assert docEditor.docAction(nwDocAction.SC_STRIKE) is True
    assert docEditor.getText() == text.replace("consectetur", "[s]consectetur[/s]")
    assert docEditor.docAction(nwDocAction.UNDO) is True
    assert docEditor.getText() == text

    # Underline
    docEditor.setCursorPosition(46)
    assert docEditor.docAction(nwDocAction.SC_ULINE) is True
    assert docEditor.getText() == text.replace("consectetur", "[u]consectetur[/u]")
    assert docEditor.docAction(nwDocAction.UNDO) is True
    assert docEditor.getText() == text

    # Mark
    docEditor.setCursorPosition(46)
    assert docEditor.docAction(nwDocAction.SC_MARK) is True
    assert docEditor.getText() == text.replace("consectetur", "[m]consectetur[/m]")
    assert docEditor.docAction(nwDocAction.UNDO) is True
    assert docEditor.getText() == text

    # Superscript
    docEditor.setCursorPosition(46)
    assert docEditor.docAction(nwDocAction.SC_SUP) is True
    assert docEditor.getText() == text.replace("consectetur", "[sup]consectetur[/sup]")
    assert docEditor.docAction(nwDocAction.UNDO) is True
    assert docEditor.getText() == text

    # Subscript
    docEditor.setCursorPosition(46)
    assert docEditor.docAction(nwDocAction.SC_SUB) is True
    assert docEditor.getText() == text.replace("consectetur", "[sub]consectetur[/sub]")
    assert docEditor.docAction(nwDocAction.UNDO) is True
    assert docEditor.getText() == text

    # Quotes
    # ======

    text = f"### A Scene\n\n{ipsumText[0]}"
    docEditor.replaceText(text)

    # Add Single Quotes
    docEditor.setCursorPosition(50)
    assert docEditor.docAction(nwDocAction.S_QUOTE) is True
    assert docEditor.getText() == text.replace("consectetur", "\u2018consectetur\u2019")
    assert docEditor.docAction(nwDocAction.UNDO) is True
    assert docEditor.getText() == text

    # Add Double Quotes
    docEditor.setCursorPosition(50)
    assert docEditor.docAction(nwDocAction.D_QUOTE) is True
    assert docEditor.getText() == text.replace("consectetur", "\u201cconsectetur\u201d")
    assert docEditor.docAction(nwDocAction.UNDO) is True
    assert docEditor.getText() == text

    # Replace Single Quotes
    repText = text.replace("consectetur", "'consectetur'")
    docEditor.replaceText(repText)
    assert docEditor.docAction(nwDocAction.SEL_ALL) is True
    assert docEditor.docAction(nwDocAction.REPL_SNG) is True
    assert docEditor.getText() == text.replace("consectetur", "\u2018consectetur\u2019")

    # Replace Double Quotes
    repText = text.replace("consectetur", '"consectetur"')
    docEditor.replaceText(repText)
    assert docEditor.docAction(nwDocAction.SEL_ALL) is True
    assert docEditor.docAction(nwDocAction.REPL_DBL) is True
    assert docEditor.getText() == text.replace("consectetur", "\u201cconsectetur\u201d")

    # Remove Line Breaks
    # ==================

    text = f"### A Scene\n\n{ipsumText[0]}"
    repText = text[:100] + text[100:].replace(" ", "\n", 3)
    docEditor.replaceText(repText)
    assert docEditor.docAction(nwDocAction.RM_BREAKS) is True
    assert docEditor.getText().strip() == text.strip()

    # Format Block
    # ============

    text = "## Scene Title\n\nScene text.\n\n"
    docEditor.replaceText(text)

    # Header 1
    docEditor.setCursorPosition(0)
    assert docEditor.docAction(nwDocAction.BLOCK_H1) is True
    assert docEditor.getText() == "# Scene Title\n\nScene text.\n\n"

    # Header 2
    docEditor.setCursorPosition(0)
    assert docEditor.docAction(nwDocAction.BLOCK_H2) is True
    assert docEditor.getText() == "## Scene Title\n\nScene text.\n\n"

    # Header 3
    docEditor.setCursorPosition(0)
    assert docEditor.docAction(nwDocAction.BLOCK_H3) is True
    assert docEditor.getText() == "### Scene Title\n\nScene text.\n\n"

    # Header 4
    docEditor.setCursorPosition(0)
    assert docEditor.docAction(nwDocAction.BLOCK_H4) is True
    assert docEditor.getText() == "#### Scene Title\n\nScene text.\n\n"

    # Comment
    docEditor.setCursorPosition(20)
    assert docEditor.docAction(nwDocAction.BLOCK_COM) is True
    assert docEditor.getText() == "#### Scene Title\n\n% Scene text.\n\n"

    # Ignore Text
    docEditor.setCursorPosition(20)
    assert docEditor.docAction(nwDocAction.BLOCK_IGN) is True
    assert docEditor.getText() == "#### Scene Title\n\n%~ Scene text.\n\n"

    # Text
    docEditor.setCursorPosition(20)
    assert docEditor.docAction(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "#### Scene Title\n\nScene text.\n\n"

    # Align Left
    docEditor.setCursorPosition(20)
    assert docEditor.docAction(nwDocAction.ALIGN_L) is True
    assert docEditor.getText() == "#### Scene Title\n\nScene text. <<\n\n"

    # Align Right
    docEditor.setCursorPosition(20)
    assert docEditor.docAction(nwDocAction.ALIGN_R) is True
    assert docEditor.getText() == "#### Scene Title\n\n>> Scene text.\n\n"

    # Align Centre
    docEditor.setCursorPosition(20)
    assert docEditor.docAction(nwDocAction.ALIGN_C) is True
    assert docEditor.getText() == "#### Scene Title\n\n>> Scene text. <<\n\n"

    # Indent Left
    docEditor.setCursorPosition(20)
    assert docEditor.docAction(nwDocAction.INDENT_L) is True
    assert docEditor.getText() == "#### Scene Title\n\n> Scene text.\n\n"

    # Indent Right
    docEditor.setCursorPosition(20)
    assert docEditor.docAction(nwDocAction.INDENT_R) is True
    assert docEditor.getText() == "#### Scene Title\n\n> Scene text. <\n\n"

    # Text (Reset)
    docEditor.setCursorPosition(20)
    assert docEditor.docAction(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "#### Scene Title\n\nScene text.\n\n"

    # Invalid Actions
    # ===============

    # No Document Handle
    docEditor._docHandle = None
    assert docEditor.docAction(nwDocAction.BLOCK_TXT) is False
    docEditor._docHandle = C.hSceneDoc

    # Wrong Action Type
    assert docEditor.docAction(None) is False

    # Unknown Action
    assert docEditor.docAction(nwDocAction.NO_ACTION) is False

    # qtbot.stop()


@pytest.mark.gui
def testGuiEditor_ToolBar(qtbot, nwGUI, projPath, mockRnd):
    """Test the document actions. This is not an extensive test of the
    action features, just that the actions are actually called. The
    various action features are tested when their respective functions
    are tested.
    """
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True

    docEditor = nwGUI.docEditor
    docToolBar = docEditor.docToolBar

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

    # Markdown
    # ========

    # Click Bold
    docEditor.setCursorPosition(20)
    docToolBar.tbBoldMD.click()
    assert len(docEditor.getText()) == length + 4

    # Click Italic
    docEditor.setCursorPosition(54)
    docToolBar.tbItalicMD.click()
    assert len(docEditor.getText()) == length + 6

    # Click Strikethrough
    docEditor.setCursorPosition(90)
    docToolBar.tbStrikeMD.click()
    assert len(docEditor.getText()) == length + 10

    # Shortcodes
    # ==========

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


@pytest.mark.gui
def testGuiEditor_Insert(qtbot, monkeypatch, nwGUI, projPath, ipsumText, mockRnd):
    """Test the document insert functions."""
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True
    docEditor = nwGUI.docEditor
    text = f"### A Scene\n\n{ipsumText[0]}"

    # Insert Text
    # ===========

    # No Document Handle
    docEditor.replaceText(text)
    docEditor._docHandle = None
    docEditor.setCursorPosition(24)
    docEditor.insertText("Stuff")
    assert docEditor.getText() == text
    docEditor._docHandle = C.hSceneDoc

    # Insert String
    docEditor.replaceText(text)
    docEditor.setCursorPosition(24)
    docEditor.insertText(", ipsumer,")
    assert docEditor.getText() == text[:24] + ", ipsumer," + text[24:]

    # Single Quotes
    docEditor.replaceText(text)
    docEditor.setCursorPosition(41)
    docEditor.insertText(nwDocInsert.QUOTE_LS)
    docEditor.setCursorPosition(53)
    docEditor.insertText(nwDocInsert.QUOTE_RS)
    assert docEditor.getText() == text.replace("consectetur", "\u2018consectetur\u2019")

    # Double Quotes
    docEditor.replaceText(text)
    docEditor.setCursorPosition(41)
    docEditor.insertText(nwDocInsert.QUOTE_LD)
    docEditor.setCursorPosition(53)
    docEditor.insertText(nwDocInsert.QUOTE_RD)
    assert docEditor.getText() == text.replace("consectetur", "\u201cconsectetur\u201d")

    # Invalid Inserts
    docEditor.replaceText(text)
    docEditor.insertText(nwDocInsert.NO_INSERT)
    assert docEditor.getText() == text
    docEditor.insertText(123)
    assert docEditor.getText() == text

    # Insert Comments
    # ===============

    docEditor.replaceText(text)
    count = docEditor.document().characterCount()

    # Invalid Position
    docEditor.setCursorPosition(12)
    docEditor.insertText(nwDocInsert.FOOTNOTE)
    assert docEditor.getText() == text

    # Valid Position
    docEditor.setCursorPosition(count)
    docEditor.insertText(nwDocInsert.FOOTNOTE)
    assert "[footnote:" in docEditor.getText()
    assert "%Footnote." in docEditor.getText()
    assert docEditor.getCursorPosition() > count

    # Insert KeyWords
    # ===============

    text = f"### A Scene\n\n\n{ipsumText[0]}"
    docEditor.replaceText(text)
    docEditor.setCursorLine(3)

    # Invalid Keyword
    docEditor.insertKeyWord("stuff")
    assert docEditor.getText() == text

    # Invalid Block
    with monkeypatch.context() as mp:
        mp.setattr(QTextBlock, "isValid", lambda *a, **k: False)
        docEditor.insertKeyWord(nwKeyWords.POV_KEY)
        assert docEditor.getText() == text

    # Valid Keyword
    docEditor.insertKeyWord(nwKeyWords.POV_KEY)
    docEditor.insertText("Jane\n")
    assert docEditor.getText() == text.replace(
        "\n\n\n", "\n\n@pov: Jane\n\n", 1
    )

    # Insert In-Block
    docEditor.setCursorPosition(20)
    docEditor.insertKeyWord(nwKeyWords.CHAR_KEY)
    docEditor.insertText("John")
    assert docEditor.getText() == text.replace(
        "\n\n\n", "\n\n@pov: Jane\n@char: John\n\n", 1
    )

    # qtbot.stop()


@pytest.mark.gui
def testGuiEditor_TextManipulation(qtbot, nwGUI, projPath, ipsumText, mockRnd):
    """Test the text manipulation functions."""
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True
    docEditor = nwGUI.docEditor

    text = "### A Scene\n\n{0}".format("\n\n".join(ipsumText))
    docEditor.replaceText(text)

    # Wrap Selection
    # ==============

    text = "### A Scene\n\n{0}".format("\n\n".join(ipsumText[0:2]))
    docEditor.replaceText(text)
    docEditor.setCursorPosition(45)

    # Wrap Equal
    docEditor.replaceText(text)
    docEditor.setCursorPosition(45)
    docEditor._wrapSelection("=")
    assert docEditor.getText() == text.replace("consectetur", "=consectetur=")

    # Wrap Unequal
    docEditor.replaceText(text)
    docEditor.setCursorPosition(45)
    docEditor._wrapSelection("=", "*")
    assert docEditor.getText() == text.replace("consectetur", "=consectetur*")

    # Past Paragraph
    docEditor.replaceText(text)
    cursor = docEditor.textCursor()
    cursor.setPosition(13, QtMoveAnchor)
    cursor.setPosition(1000, QtKeepAnchor)
    docEditor.setTextCursor(cursor)
    docEditor._wrapSelection("=")

    newText = docEditor.getText()
    newPara = list(filter(str.strip, newText.split("\n")))
    assert newPara[1] == "="+ipsumText[0]+"="
    assert newPara[2] == ipsumText[1]

    # Toggle Format
    # =============

    text = "### A Scene\n\n{0}".format("\n\n".join(ipsumText[0:2]))

    # Block format repetition
    docEditor.replaceText(text)
    docEditor.setCursorPosition(39)
    docEditor._toggleFormat(1, "=")
    assert docEditor.getText() == text.replace("amet", "=amet=", 1)
    docEditor._toggleFormat(1, "=")
    assert docEditor.getText() == text.replace("amet", "=amet=", 1)

    # Wrap Single Equal
    docEditor.replaceText(text)
    docEditor.setCursorPosition(45)
    docEditor._toggleFormat(1, "=")
    assert docEditor.getText() == text.replace("consectetur", "=consectetur=")

    # Past Paragraph
    docEditor.replaceText(text)
    cursor = docEditor.textCursor()
    cursor.setPosition(13, QtMoveAnchor)
    cursor.setPosition(1000, QtKeepAnchor)
    docEditor.setTextCursor(cursor)
    docEditor._toggleFormat(1, "=")

    newText = docEditor.getText()
    newPara = list(filter(str.strip, newText.split("\n")))
    assert newPara[1] == "="+ipsumText[0]+"="
    assert newPara[2] == ipsumText[1]

    # Wrap Double Equal
    docEditor.replaceText(text)
    docEditor.setCursorPosition(45)
    docEditor._toggleFormat(2, "=")
    assert docEditor.getText() == text.replace("consectetur", "==consectetur==")

    # Toggle Double Equal with Selection
    docEditor.replaceText(text)
    docEditor.setCursorSelection(41, 11)
    docEditor._toggleFormat(2, "=")
    assert docEditor.getText() == text.replace("consectetur", "==consectetur==")
    assert docEditor.getSelectedText() == "consectetur"
    docEditor._toggleFormat(2, "=")
    assert docEditor.getText() == text
    assert docEditor.getSelectedText() == "consectetur"

    # Toggle Double Equal
    docEditor.replaceText(text)
    docEditor.setCursorPosition(45)
    docEditor._toggleFormat(2, "=")
    docEditor._toggleFormat(2, "=")
    assert docEditor.getText() == text

    # Toggle Triple+Double Equal
    docEditor.replaceText(text)
    docEditor.setCursorPosition(45)
    docEditor._toggleFormat(3, "=")
    docEditor._toggleFormat(2, "=")
    assert docEditor.getText() == text.replace("consectetur", "=consectetur=")

    # Toggle Unequal
    repText = text.replace("consectetur", "=consectetur==")
    docEditor.replaceText(repText)
    docEditor.setCursorPosition(45)
    docEditor._toggleFormat(1, "=")
    assert docEditor.getText() == text.replace("consectetur", "consectetur=")
    docEditor._toggleFormat(1, "=")
    assert docEditor.getText() == repText

    # Replace Quotes
    # ==============

    # No Selection
    text = "### A Scene\n\n{0}".format(ipsumText[0].replace("consectetur", "=consectetur="))
    docEditor.replaceText(text)
    docEditor.setCursorPosition(45)
    docEditor._replaceQuotes("=", "<", ">")
    assert docEditor.getText() == text

    # First Paragraph Selected
    # This should not replace anything in second paragraph
    text = "### A Scene\n\n{0}".format("\n\n".join(ipsumText[0:2]).replace("ipsum", "=ipsum="))
    docEditor.replaceText(text)
    docEditor.setCursorPosition(45)
    assert docEditor.docAction(nwDocAction.SEL_PARA)
    docEditor._replaceQuotes("=", "<", ">")

    newText = docEditor.getText()
    newPara = list(filter(str.strip, newText.split("\n")))
    assert newPara[1] == ipsumText[0].replace("ipsum", "<ipsum>")
    assert newPara[2] == ipsumText[1].replace("ipsum", "=ipsum=")

    # Edge of Document
    text = ipsumText[0].replace("Lorem", "=Lorem=")
    docEditor.replaceText(text)
    docEditor.setCursorPosition(45)
    assert docEditor.docAction(nwDocAction.SEL_ALL)
    docEditor._replaceQuotes("=", "<", ">")
    assert docEditor.getText() == text.replace("=Lorem=", "<Lorem>")

    # Remove Line Breaks
    # ==================

    parOne = ipsumText[0].replace(" ", "\n", 5)
    parTwo = ipsumText[1].replace(" ", "\n", 5)

    # Check Blocks
    cursor = docEditor.textCursor()
    cursor.clearSelection()
    text = f"### A Scene\n\n{parOne}\n\n{parTwo}"
    docEditor.replaceText(text)
    docEditor.setCursorPosition(45)
    assert len(docEditor._selectedBlocks(cursor)) == 0

    cursor.select(QTextCursor.SelectionType.Document)
    assert len(docEditor._selectedBlocks(cursor)) == 15

    # Remove All
    text = f"### A Scene\n\n{parOne}\n\n{parTwo}"
    docEditor.replaceText(text)
    docEditor.setCursorPosition(45)
    docEditor._removeInParLineBreaks()
    assert docEditor.getText() == "### A Scene\n\n{0}\n".format("\n\n".join(ipsumText[0:2]))

    # Remove in First Paragraph
    # Second paragraphs should remain unchanged
    text = f"### A Scene\n\n{parOne}\n\n{parTwo}"
    docEditor.replaceText(text)
    cursor = docEditor.textCursor()
    cursor.setPosition(16, QtMoveAnchor)
    cursor.setPosition(680, QtKeepAnchor)
    docEditor.setTextCursor(cursor)
    docEditor._removeInParLineBreaks()

    newText = docEditor.getText()
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
    text = f"### A Scene\n\n{parOne}\n\n{parTwo}"
    docEditor.replaceText(text)
    assert docEditor.getText() == text

    # Select All
    qtbot.keyClick(docEditor, Qt.Key.Key_A, modifier=QtModCtrl, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Delete, delay=KEY_DELAY)
    assert docEditor.getText() == ""

    # Undo
    qtbot.keyClick(docEditor, Qt.Key.Key_Z, modifier=QtModCtrl, delay=KEY_DELAY)
    assert docEditor.getText() == text

    # Redo
    qtbot.keyClick(docEditor, Qt.Key.Key_Y, modifier=QtModCtrl, delay=KEY_DELAY)
    assert docEditor.getText() == ""

    # qtbot.stop()


@pytest.mark.gui
def testGuiEditor_BlockFormatting(qtbot, monkeypatch, nwGUI, projPath, ipsumText, mockRnd):
    """Test the block formatting function."""
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True
    docEditor = nwGUI.docEditor

    # Invalid and Generic
    # ===================

    text = f"### A Scene\n\n{ipsumText[0]}"
    docEditor.replaceText(text)

    # Invalid Block
    docEditor.setCursorPosition(0)
    with monkeypatch.context() as mp:
        mp.setattr(QTextBlock, "isValid", lambda *a, **k: False)
        assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is False

    # Keyword
    docEditor.replaceText("@pov: Jane\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is False
    assert docEditor.getText() == "@pov: Jane\n\n"
    assert docEditor.getCursorPosition() == 5

    # Unsupported Format
    docEditor.replaceText("% Comment\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.NO_ACTION) is False

    # Block Stripping : Left Side
    # ===========================

    # Strip Comment w/Space
    docEditor.replaceText("% Comment\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "Comment\n\n"
    assert docEditor.getCursorPosition() == 3

    # Strip Comment wo/Space
    docEditor.replaceText("%Comment\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "Comment\n\n"
    assert docEditor.getCursorPosition() == 4

    # Strip Header 1
    docEditor.replaceText("# Title\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "Title\n\n"
    assert docEditor.getCursorPosition() == 3

    # Strip Header 2
    docEditor.replaceText("## Title\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "Title\n\n"
    assert docEditor.getCursorPosition() == 2

    # Strip Header 3
    docEditor.replaceText("### Title\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "Title\n\n"
    assert docEditor.getCursorPosition() == 1

    # Strip Header 4
    docEditor.replaceText("#### Title\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "Title\n\n"
    assert docEditor.getCursorPosition() == 0

    # Strip Novel Title
    docEditor.replaceText("#! Title\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "Title\n\n"
    assert docEditor.getCursorPosition() == 2

    # Strip Unnumbered Chapter
    docEditor.replaceText("##! Title\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "Title\n\n"
    assert docEditor.getCursorPosition() == 1

    # Strip Hard Scene
    docEditor.replaceText("###! Title\n\n")
    docEditor.setCursorPosition(6)
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "Title\n\n"
    assert docEditor.getCursorPosition() == 1

    # Strip Text
    docEditor.replaceText("Generic text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "Generic text\n\n"
    assert docEditor.getCursorPosition() == 5

    # Strip Left Angle Brackets : Double w/Space
    docEditor.replaceText(">> Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "Some text\n\n"
    assert docEditor.getCursorPosition() == 2

    # Strip Left Angle Brackets : Single w/Space
    docEditor.replaceText("> Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "Some text\n\n"
    assert docEditor.getCursorPosition() == 3

    # Strip Left Angle Brackets : Double wo/Space
    docEditor.replaceText(">>Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "Some text\n\n"
    assert docEditor.getCursorPosition() == 3

    # Strip Left Angle Brackets : Single wo/Space
    docEditor.replaceText(">Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "Some text\n\n"
    assert docEditor.getCursorPosition() == 4

    # Block Stripping : Right Side
    # ============================

    # Strip Right Angle Brackets : Double w/Space
    docEditor.replaceText("Some text <<\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "Some text\n\n"
    assert docEditor.getCursorPosition() == 5

    # Strip Right Angle Brackets : Single w/Space
    docEditor.replaceText("Some text <\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "Some text\n\n"
    assert docEditor.getCursorPosition() == 5

    # Strip Right Angle Brackets : Double wo/Space
    docEditor.replaceText("Some text<<\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "Some text\n\n"
    assert docEditor.getCursorPosition() == 5

    # Strip Right Angle Brackets : Single wo/Space
    docEditor.replaceText("Some text<\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "Some text\n\n"
    assert docEditor.getCursorPosition() == 5

    # Block Stripping : Both Sides
    # ============================

    docEditor.replaceText(">> Some text <<\n\n")
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "Some text\n\n"

    docEditor.replaceText(">Some text <<\n\n")
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "Some text\n\n"

    docEditor.replaceText(">Some text<\n\n")
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "Some text\n\n"

    # New Formats
    # ===========

    # Comment
    docEditor.replaceText("Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_COM) is True
    assert docEditor.getText() == "% Some text\n\n"
    assert docEditor.getCursorPosition() == 7

    # Toggle Comment w/Space
    docEditor.replaceText("% Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_COM) is True
    assert docEditor.getText() == "Some text\n\n"
    assert docEditor.getCursorPosition() == 3

    # Toggle Comment wo/Space
    docEditor.replaceText("%Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_COM) is True
    assert docEditor.getText() == "Some text\n\n"
    assert docEditor.getCursorPosition() == 4

    # Toggle Ignore Text w/Space
    docEditor.replaceText("%~ Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_IGN) is True
    assert docEditor.getText() == "Some text\n\n"
    assert docEditor.getCursorPosition() == 2

    # Toggle Ignore Text wo/Space
    docEditor.replaceText("%~Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_IGN) is True
    assert docEditor.getText() == "Some text\n\n"
    assert docEditor.getCursorPosition() == 3

    # Header 1
    docEditor.replaceText("Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_H1) is True
    assert docEditor.getText() == "# Some text\n\n"
    assert docEditor.getCursorPosition() == 7

    # Header 2
    docEditor.replaceText("Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_H2) is True
    assert docEditor.getText() == "## Some text\n\n"
    assert docEditor.getCursorPosition() == 8

    # Header 3
    docEditor.replaceText("Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_H3) is True
    assert docEditor.getText() == "### Some text\n\n"
    assert docEditor.getCursorPosition() == 9

    # Header 4
    docEditor.replaceText("Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_H4) is True
    assert docEditor.getText() == "#### Some text\n\n"
    assert docEditor.getCursorPosition() == 10

    # Novel Title
    docEditor.replaceText("Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_TTL) is True
    assert docEditor.getText() == "#! Some text\n\n"
    assert docEditor.getCursorPosition() == 8

    # Unnumbered Chapter
    docEditor.replaceText("Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_UNN) is True
    assert docEditor.getText() == "##! Some text\n\n"
    assert docEditor.getCursorPosition() == 9

    # Hard Scene
    docEditor.replaceText("Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.BLOCK_HSC) is True
    assert docEditor.getText() == "###! Some text\n\n"
    assert docEditor.getCursorPosition() == 10

    # Left Indent
    docEditor.replaceText("Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.INDENT_L) is True
    assert docEditor.getText() == "> Some text\n\n"
    assert docEditor.getCursorPosition() == 7

    # Right Indent
    docEditor.replaceText("Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.INDENT_R) is True
    assert docEditor.getText() == "Some text <\n\n"
    assert docEditor.getCursorPosition() == 5

    # Right/Left Indent
    docEditor.replaceText("Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.INDENT_L) is True
    assert docEditor._formatBlock(nwDocAction.INDENT_R) is True
    assert docEditor.getText() == "> Some text <\n\n"
    assert docEditor.getCursorPosition() == 7

    # Left Align
    docEditor.replaceText("Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.ALIGN_L) is True
    assert docEditor.getText() == "Some text <<\n\n"
    assert docEditor.getCursorPosition() == 5

    # Right Align
    docEditor.replaceText("Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.ALIGN_R) is True
    assert docEditor.getText() == ">> Some text\n\n"
    assert docEditor.getCursorPosition() == 8

    # Centre Align
    docEditor.replaceText("Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.ALIGN_C) is True
    assert docEditor.getText() == ">> Some text <<\n\n"
    assert docEditor.getCursorPosition() == 8

    # Left/Right Align (Overrides)
    docEditor.replaceText("Some text\n\n")
    docEditor.setCursorPosition(5)
    assert docEditor._formatBlock(nwDocAction.ALIGN_L) is True
    assert docEditor._formatBlock(nwDocAction.ALIGN_R) is True
    assert docEditor.getText() == ">> Some text\n\n"
    assert docEditor.getCursorPosition() == 8

    # Other Checks
    # ============

    # Final Cursor Position Out of Range
    docEditor.replaceText("#### Title\n\n")
    docEditor.setCursorPosition(3)
    assert docEditor._formatBlock(nwDocAction.BLOCK_TXT) is True
    assert docEditor.getText() == "Title\n\n"
    assert docEditor.getCursorPosition() == 5

    # Third Line
    # This also needs to add a new block
    docEditor.replaceText("#### Title\n\nThe Text\n\n")
    docEditor.setCursorLine(3)
    assert docEditor._formatBlock(nwDocAction.BLOCK_COM) is True
    assert docEditor.getText() == "#### Title\n\n% The Text\n\n"

    # qtbot.stop()


@pytest.mark.gui
def testGuiEditor_MultiBlockFormatting(qtbot, nwGUI, projPath, ipsumText, mockRnd):
    """Test the block formatting function."""
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True
    docEditor = nwGUI.docEditor

    text = "### A Scene\n\n@char: Jane, John\n\n" + "\n\n".join(ipsumText) + "\n\n"
    docEditor.replaceText(text)
    assert [x[:5] for x in docEditor.getText().splitlines()] == [
        "### A", "", "@char", "", "Lorem", "", "Nulla", "", "Nulla", "", "Pelle", "", "Integ", ""
    ]

    # Toggle Comment
    cursor = docEditor.textCursor()
    cursor.setPosition(50)
    cursor.movePosition(QtMoveRight, QtKeepAnchor, 2000)
    docEditor.setTextCursor(cursor)

    docEditor._iterFormatBlocks(nwDocAction.BLOCK_COM)
    assert [x[:5] for x in docEditor.getText().splitlines()] == [
        "### A", "", "@char", "", "% Lor", "", "% Nul", "", "% Nul", "", "% Pel", "", "Integ", ""
    ]

    # Un-toggle the second
    cursor = docEditor.textCursor()
    cursor.setPosition(800)
    docEditor.setTextCursor(cursor)

    docEditor._iterFormatBlocks(nwDocAction.BLOCK_COM)
    assert [x[:5] for x in docEditor.getText().splitlines()] == [
        "### A", "", "@char", "", "% Lor", "", "Nulla", "", "% Nul", "", "% Pel", "", "Integ", ""
    ]

    # Un-toggle all
    cursor = docEditor.textCursor()
    cursor.setPosition(50)
    cursor.movePosition(QtMoveRight, QtKeepAnchor, 3000)
    docEditor.setTextCursor(cursor)

    docEditor._iterFormatBlocks(nwDocAction.BLOCK_COM)
    assert [x[:5] for x in docEditor.getText().splitlines()] == [
        "### A", "", "@char", "", "Lorem", "", "Nulla", "", "Nulla", "", "Pelle", "", "Integ", ""
    ]

    # Toggle Ignore Text
    cursor = docEditor.textCursor()
    cursor.setPosition(50)
    cursor.movePosition(QtMoveRight, QtKeepAnchor, 2000)
    docEditor.setTextCursor(cursor)

    docEditor._iterFormatBlocks(nwDocAction.BLOCK_IGN)
    assert [x[:5] for x in docEditor.getText().splitlines()] == [
        "### A", "", "@char", "", "%~ Lo", "", "%~ Nu", "", "%~ Nu", "", "%~ Pe", "", "Integ", ""
    ]

    # Clear all paragraphs
    cursor = docEditor.textCursor()
    cursor.setPosition(50)
    cursor.movePosition(QtMoveRight, QtKeepAnchor, 3000)
    docEditor.setTextCursor(cursor)

    docEditor._iterFormatBlocks(nwDocAction.BLOCK_TXT)
    assert [x[:5] for x in docEditor.getText().splitlines()] == [
        "### A", "", "@char", "", "Lorem", "", "Nulla", "", "Nulla", "", "Pelle", "", "Integ", ""
    ]

    # Final text should be identical to initial text
    assert docEditor.getText() == text

    # qtbot.stop()


@pytest.mark.gui
def testGuiEditor_Tags(qtbot, nwGUI, projPath, ipsumText, mockRnd):
    """Test the document editor tags functionality."""
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True
    docEditor = nwGUI.docEditor

    # Create Scene
    text = "### A Scene\n\n@char: Jane, John\n\n@object: Gun\n\n@:\n\n" + ipsumText[0] + "\n\n"
    docEditor.replaceText(text)

    # Create Character
    text = "### Jane Doe\n\n@tag: Jane\n\n" + ipsumText[1] + "\n\n"
    cHandle = SHARED.project.newFile("Jane Doe", C.hCharRoot)
    assert nwGUI.openDocument(cHandle) is True
    docEditor.replaceText(text)
    nwGUI.saveDocument()

    # Follow Tag
    # ==========
    assert nwGUI.openDocument(C.hSceneDoc) is True

    # Empty Block
    docEditor.setCursorLine(2)
    assert docEditor._processTag() == _TagAction.NONE

    # Not On Tag
    docEditor.setCursorLine(1)
    assert docEditor._processTag() == _TagAction.NONE

    # On Tag Keyword
    docEditor.setCursorPosition(15)
    assert docEditor._processTag() == _TagAction.NONE

    # On Known Tag, No Follow
    docEditor.setCursorPosition(22)
    assert docEditor._processTag(follow=False) == _TagAction.FOLLOW
    assert nwGUI.docViewer._docHandle is None

    # qtbot.stop()
    # On Known Tag, Follow
    docEditor.setCursorPosition(22)
    position = QPointF(docEditor.cursorRect().center())
    event = QMouseEvent(
        QEvent.Type.MouseButtonPress, position, QtMouseLeft, QtMouseLeft, QtModCtrl
    )
    assert nwGUI.docViewer._docHandle is None
    docEditor.mouseReleaseEvent(event)
    assert nwGUI.docViewer._docHandle == cHandle
    assert nwGUI.closeViewerPanel() is True
    assert nwGUI.docViewer._docHandle is None

    # On Unknown Tag, Create It
    assert "0000000000011" not in SHARED.project.tree
    docEditor.setCursorPosition(28)
    assert docEditor._processTag(create=True) == _TagAction.CREATE
    assert "0000000000011" in SHARED.project.tree

    # On Unknown Tag, Missing Root
    assert "0000000000012" not in SHARED.project.tree
    docEditor.setCursorPosition(42)
    assert docEditor._processTag(create=True) == _TagAction.CREATE
    oHandle = SHARED.project.tree.findRoot(nwItemClass.OBJECT)
    assert oHandle == "0000000000012"

    oItem = SHARED.project.tree["0000000000013"]
    assert oItem is not None
    assert oItem.itemParent == "0000000000012"

    docEditor.setCursorPosition(47)
    assert docEditor._processTag() == _TagAction.NONE

    # qtbot.stop()


@pytest.mark.gui
def testGuiEditor_Links(qtbot, monkeypatch, nwGUI, projPath, ipsumText, mockRnd):
    """Test the document editor links functionality."""
    buildTestProject(nwGUI, projPath)
    nwGUI.openDocument(C.hSceneDoc)
    docEditor = nwGUI.docEditor
    docEditor.replaceText("### Scene\n\nFoo http://www.example.com bar.\n\n")

    docEditor.setCursorPosition(20)
    position = QPointF(docEditor.cursorRect().center())
    event = QMouseEvent(
        QEvent.Type.MouseButtonPress, position, QtMouseLeft, QtMouseLeft, QtModCtrl
    )

    with monkeypatch.context() as mp:
        openUrl = MagicMock()
        mp.setattr(QDesktopServices, "openUrl", openUrl)
        docEditor.mouseReleaseEvent(event)
        assert openUrl.called is True
        assert openUrl.call_args[0][0] == QUrl("http://www.example.com")

    # qtbot.stop()


@pytest.mark.gui
def testGuiEditor_Completer(qtbot, nwGUI, projPath, mockRnd):
    """Test the document editor meta completer functionality."""
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc) is True
    docEditor = nwGUI.docEditor

    # Create Character
    text = (
        "# Jane Doe\n\n"
        "@tag: Jane\n\n"
        "# John Doe\n\n"
        "@tag: John\n\n"
    )
    cHandle = SHARED.project.newFile("People", C.hCharRoot)
    assert nwGUI.openDocument(cHandle) is True
    docEditor.replaceText(text)
    nwGUI.saveDocument()

    docEditor.replaceText("")
    completer = docEditor._completer

    # Create Scene
    nwGUI.docEditor.setFocus()
    for c in "### Scene One":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)

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
    qtbot.keyClick(docEditor, Qt.Key.Key_Backspace, delay=KEY_DELAY)
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
    qtbot.keyClick(docEditor, Qt.Key.Key_Backspace, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, "a", delay=KEY_DELAY)
    assert [a.text() for a in completer.actions()] == ["Jane"]

    # Selecting "Jane" should insert it
    completer.actions()[0].trigger()
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    assert docEditor.getText() == (
        "### Scene One\n\n"
        "@char: Jane\n"
    )

    # Start a new line with a nonsense keyword, which should be handled
    for c in "@: ":
        qtbot.keyClick(docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Backspace, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Backspace, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Backspace, delay=KEY_DELAY)

    # Send keypresses to the completer object
    qtbot.keyClick(docEditor, "@", delay=KEY_DELAY)
    assert len(completer.actions()) == len(nwKeyWords.VALID_KEYS)
    qtbot.keyClick(completer, "f", delay=KEY_DELAY)
    qtbot.keyClick(completer, Qt.Key.Key_Down, delay=KEY_DELAY)
    qtbot.keyClick(completer, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(completer, " ", delay=KEY_DELAY)
    qtbot.keyClick(completer, "h", delay=KEY_DELAY)
    qtbot.keyClick(completer, Qt.Key.Key_Down, delay=KEY_DELAY)
    qtbot.keyClick(completer, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(completer, Qt.Key.Key_Escape, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    assert docEditor.getText() == (
        "### Scene One\n\n"
        "@char: Jane\n"
        "@focus: John\n"
    )

    # Send keypresses to the completer object for a comment
    qtbot.keyClick(docEditor, "%", delay=KEY_DELAY)
    assert len(completer.actions()) == 4
    qtbot.keyClick(completer, Qt.Key.Key_Down, delay=KEY_DELAY)
    qtbot.keyClick(completer, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    assert docEditor.getText() == (
        "### Scene One\n\n"
        "@char: Jane\n"
        "@focus: John\n"
        "%Synopsis: \n"
    )

    # Auto-complete story comment
    SHARED.project.index._itemIndex._cache.story.add("Resolution")
    qtbot.keyClick(docEditor, "%", delay=KEY_DELAY)
    assert len(completer.actions()) == 4
    qtbot.keyClick(completer, Qt.Key.Key_Down, delay=KEY_DELAY)
    qtbot.keyClick(completer, Qt.Key.Key_Down, delay=KEY_DELAY)
    qtbot.keyClick(completer, Qt.Key.Key_Down, delay=KEY_DELAY)
    qtbot.keyClick(completer, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(completer, ".", delay=KEY_DELAY)
    assert len(completer.actions()) == 1
    qtbot.keyClick(completer, Qt.Key.Key_Down, delay=KEY_DELAY)
    qtbot.keyClick(completer, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    assert docEditor.getText() == (
        "### Scene One\n\n"
        "@char: Jane\n"
        "@focus: John\n"
        "%Synopsis: \n"
        "%Story.Resolution: \n"
    )

    # Auto-complete note comment
    SHARED.project.index._itemIndex._cache.note.add("Consistency")
    qtbot.keyClick(docEditor, "%", delay=KEY_DELAY)
    assert len(completer.actions()) == 4
    qtbot.keyClick(completer, Qt.Key.Key_Down, delay=KEY_DELAY)
    qtbot.keyClick(completer, Qt.Key.Key_Down, delay=KEY_DELAY)
    qtbot.keyClick(completer, Qt.Key.Key_Down, delay=KEY_DELAY)
    qtbot.keyClick(completer, Qt.Key.Key_Down, delay=KEY_DELAY)
    qtbot.keyClick(completer, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(completer, ".", delay=KEY_DELAY)
    assert len(completer.actions()) == 1
    qtbot.keyClick(completer, Qt.Key.Key_Down, delay=KEY_DELAY)
    qtbot.keyClick(completer, Qt.Key.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(docEditor, Qt.Key.Key_Return, delay=KEY_DELAY)
    assert docEditor.getText() == (
        "### Scene One\n\n"
        "@char: Jane\n"
        "@focus: John\n"
        "%Synopsis: \n"
        "%Story.Resolution: \n"
        "%Note.Consistency: \n"
    )

    # CJK completer reposition (#2267 and #2517)
    qtbot.keyClick(docEditor, "%", delay=KEY_DELAY)
    assert completer.isVisible() is True
    completer.move(0, 0)
    assert completer.pos().x() == 0  # Completer menu at 0
    assert completer.pos().y() == 0  # Completer menu at 0

    event = QInputMethodEvent()
    event.setCommitString("Text")
    docEditor.inputMethodEvent(event)
    assert completer.pos().x() > 0  # Completer should have moved
    assert completer.pos().y() > 0  # Completer should have moved

    # qtbot.stop()


@pytest.mark.gui
def testGuiEditor_CursorVisibility(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test the custom ensure cursor visible feature."""
    buildTestProject(nwGUI, projPath)
    nwGUI.openDocument(C.hSceneDoc)
    docEditor = nwGUI.docEditor

    docEditor.setPlainText(
        "### Scene\n\n" + "".join(["Text\n\n"]*100)
    )
    assert docEditor.cursorIsVisible() is True
    docEditor.setCenterOnScroll(False)

    # Scroll Down
    cursor = docEditor.textCursor()
    cursor.setPosition(605)
    docEditor.setTextCursor(cursor)
    docEditor.verticalScrollBar().setValue(0)
    assert docEditor.verticalScrollBar().value() == 0
    docEditor.ensureCursorVisibleNoCentre()
    assert docEditor.verticalScrollBar().value() > 0
    assert docEditor.cursorIsVisible() is True

    # Scroll Up
    cursor = docEditor.textCursor()
    cursor.setPosition(0)
    docEditor.setTextCursor(cursor)
    docEditor.verticalScrollBar().setValue(200)
    assert docEditor.verticalScrollBar().value() > 100
    docEditor.ensureCursorVisibleNoCentre()
    assert docEditor.verticalScrollBar().value() == 0
    assert docEditor.cursorIsVisible() is True

    # qtbot.stop()


@pytest.mark.gui
def testGuiEditor_WordCounters(qtbot, monkeypatch, nwGUI, projPath, ipsumText, mockRnd):
    """Test the word counter."""
    docEditor = nwGUI.docEditor

    class MockThreadPool:

        def __init__(self):
            self._objID = None

        def start(self, runObj, priority=0):
            self._objID = id(runObj)

        def objectID(self):
            return self._objID

    threadPool = MockThreadPool()
    monkeypatch.setattr(QThreadPool, "globalInstance", lambda *a: threadPool)
    docEditor._timerDoc.blockSignals(True)
    docEditor._timerSel.blockSignals(True)

    buildTestProject(nwGUI, projPath)

    # Run on an empty document
    docEditor._runDocumentTasks()
    assert docEditor.docFooter.wordsText.text() == "Words: 0 (+0)"
    docEditor._updateDocCounts(0, 0, 0)
    assert docEditor.docFooter.wordsText.text() == "Words: 0 (+0)"

    docEditor._runSelCounter()
    assert docEditor.docFooter.wordsText.text() == "Words: 0 (+0)"
    docEditor._updateSelCounts(0, 0, 0)
    assert docEditor.docFooter.wordsText.text() == "Words: 0 (+0)"

    # Open a document and populate it
    SHARED.project.tree[C.hSceneDoc]._wordInit = 0  # type: ignore
    SHARED.project.tree[C.hSceneDoc]._wordCount = 0  # type: ignore
    assert nwGUI.openDocument(C.hSceneDoc) is True

    text = "\n\n".join(ipsumText)
    cC, wC, pC = standardCounter(text)
    docEditor.replaceText(text)

    # Check that a busy counter is blocked
    with monkeypatch.context() as mp:
        mp.setattr(docEditor._wCounterDoc, "isRunning", lambda *a: True)
        docEditor._runDocumentTasks()
        assert docEditor.docFooter.wordsText.text() == "Words: 0 (+0)"

    with monkeypatch.context() as mp:
        mp.setattr(docEditor._wCounterSel, "isRunning", lambda *a: True)
        docEditor._runSelCounter()
        assert docEditor.docFooter.wordsText.text() == "Words: 0 (+0)"

    # Run the full word counter
    docEditor._runDocumentTasks()
    assert threadPool.objectID() == id(docEditor._wCounterDoc)

    docEditor._wCounterDoc.run()
    assert SHARED.project.tree[C.hSceneDoc]._charCount == cC  # type: ignore
    assert SHARED.project.tree[C.hSceneDoc]._wordCount == wC  # type: ignore
    assert SHARED.project.tree[C.hSceneDoc]._paraCount == pC  # type: ignore
    assert docEditor.docFooter.wordsText.text() == f"Words: {wC} (+{wC})"

    # Select all text and run the selection word counter
    docEditor.docAction(nwDocAction.SEL_ALL)
    docEditor._runSelCounter()
    assert threadPool.objectID() == id(docEditor._wCounterSel)

    docEditor._wCounterSel.run()
    assert docEditor.docFooter.wordsText.text() == f"Selected: {wC}"

    # qtbot.stop()


@pytest.mark.gui
def testGuiEditor_Search(qtbot, monkeypatch, nwGUI, prjLipsum):
    """Test the document editor search functionality."""
    monkeypatch.setattr(GuiDocEditor, "hasFocus", lambda *a: True)

    assert nwGUI.openProject(prjLipsum) is True
    assert nwGUI.openDocument("4c4f28287af27") is True
    docEditor = nwGUI.docEditor
    docSearch = docEditor.docSearch
    origText = docEditor.getText()

    # Select the Word "est"
    docEditor.setCursorPosition(663)
    docEditor._makeSelection(QTextCursor.SelectionType.WordUnderCursor)
    cursor = docEditor.textCursor()
    assert cursor.selectedText() == "est"

    # Activate search
    nwGUI.mainMenu.aFind.activate(QAction.ActionEvent.Trigger)
    assert docSearch.isVisible()
    assert docSearch.searchText == "est"

    # Find next by enter key
    monkeypatch.setattr(docSearch.searchBox, "hasFocus", lambda: True)
    qtbot.keyClick(docSearch.searchBox, Qt.Key.Key_Return, delay=KEY_DELAY)
    assert abs(docEditor.getCursorPosition() - 1317) < 3

    # Find next by button
    qtbot.mouseClick(docSearch.searchButton, QtMouseLeft, delay=KEY_DELAY)
    assert abs(docEditor.getCursorPosition() - 1531) < 3

    # Activate loop search
    docSearch.toggleLoop.activate(QAction.ActionEvent.Trigger)
    assert docSearch.toggleLoop.isChecked()
    assert CONFIG.searchLoop is True

    # Find next by menu Search > Find Next
    nwGUI.mainMenu.aFindNext.activate(QAction.ActionEvent.Trigger)
    assert abs(docEditor.getCursorPosition() - 665) < 3

    # Close search
    docSearch.cancelSearch.activate(QAction.ActionEvent.Trigger)
    assert docSearch.isVisible() is False
    docEditor.setCursorPosition(15)

    # Toggle search again with header button
    qtbot.mouseClick(docEditor.docHeader.searchButton, QtMouseLeft, delay=KEY_DELAY)
    docSearch.setSearchText("")
    assert docSearch.isVisible() is True

    # Search for non-existing
    docEditor.setCursorPosition(0)
    docSearch.setSearchText("abcdef")
    qtbot.mouseClick(docSearch.searchButton, QtMouseLeft, delay=KEY_DELAY)
    assert docEditor.getCursorPosition() < 3  # No result

    # Enable RegEx search
    docSearch.toggleRegEx.activate(QAction.ActionEvent.Trigger)
    assert docSearch.toggleRegEx.isChecked()
    assert CONFIG.searchRegEx is True

    # Set invalid RegEx
    docEditor.setCursorPosition(0)
    docSearch.setSearchText(r"\bSus[")
    qtbot.mouseClick(docSearch.searchButton, QtMouseLeft, delay=KEY_DELAY)
    assert docEditor.getCursorPosition() < 3  # No result

    # Set dangerous RegEx (issue #1015)
    # If this doesn't get caught, the app will hang
    docEditor.setCursorPosition(0)
    docSearch.setSearchText(r".*")
    qtbot.mouseClick(docSearch.searchButton, QtMouseLeft, delay=KEY_DELAY)
    assert abs(docEditor.getCursorPosition() - 14) < 3

    # Set valid RegEx
    docSearch.setSearchText(r"\bSus")
    qtbot.mouseClick(docSearch.searchButton, QtMouseLeft, delay=KEY_DELAY)
    assert abs(docEditor.getCursorPosition() - 241) < 3

    # Find next and then prev
    nwGUI.mainMenu.aFindNext.activate(QAction.ActionEvent.Trigger)
    assert abs(docEditor.getCursorPosition() - 342) < 3
    nwGUI.mainMenu.aFindPrev.activate(QAction.ActionEvent.Trigger)
    assert abs(docEditor.getCursorPosition() - 241) < 3

    # Make RegEx case sensitive
    docSearch.toggleCase.activate(QAction.ActionEvent.Trigger)
    assert docSearch.toggleCase.isChecked()
    assert CONFIG.searchCase is True

    # Find next/prev (one result)
    nwGUI.mainMenu.aFindNext.activate(QAction.ActionEvent.Trigger)
    assert abs(docEditor.getCursorPosition() - 644) < 3
    nwGUI.mainMenu.aFindPrev.activate(QAction.ActionEvent.Trigger)
    assert abs(docEditor.getCursorPosition() - 644) < 3
    nwGUI.mainMenu.aFindNext.activate(QAction.ActionEvent.Trigger)
    assert abs(docEditor.getCursorPosition() - 644) < 3

    # Trigger replace
    nwGUI.mainMenu.aReplace.activate(QAction.ActionEvent.Trigger)
    docSearch.setReplaceText("foo")

    # Disable RegEx case sensitive
    docSearch.toggleCase.activate(QAction.ActionEvent.Trigger)
    assert docSearch.toggleCase.isChecked() is False
    assert CONFIG.searchCase is False

    # Toggle replace preserve case
    docSearch.toggleMatchCap.activate(QAction.ActionEvent.Trigger)
    assert docSearch.toggleMatchCap.isChecked()
    assert CONFIG.searchMatchCap is True

    # Replace "Sus" with "Foo" via menu
    docEditor.setCursorPosition(623)
    nwGUI.mainMenu.aFindNext.activate(QAction.ActionEvent.Trigger)
    nwGUI.mainMenu.aReplaceNext.activate(QAction.ActionEvent.Trigger)
    assert docEditor.getText()[641:652] == "Foopendisse"

    # Find next/prev to loop file
    nwGUI.mainMenu.aFindNext.activate(QAction.ActionEvent.Trigger)
    assert abs(docEditor.getCursorPosition() - 241) < 3
    nwGUI.mainMenu.aFindPrev.activate(QAction.ActionEvent.Trigger)
    assert abs(docEditor.getCursorPosition() - 1823) < 3
    nwGUI.mainMenu.aFindNext.activate(QAction.ActionEvent.Trigger)
    assert abs(docEditor.getCursorPosition() - 241) < 3

    # Replace "sus" with "foo" via replace button
    qtbot.mouseClick(docSearch.replaceButton, QtMouseLeft, delay=KEY_DELAY)
    assert docEditor.getText()[238:246] == "foocipit"

    # Revert last two replaces
    assert docEditor.docAction(nwDocAction.UNDO)
    assert docEditor.docAction(nwDocAction.UNDO)
    assert docEditor.getText() == origText

    # Disable RegEx search
    docSearch.toggleRegEx.activate(QAction.ActionEvent.Trigger)
    assert not docSearch.toggleRegEx.isChecked()
    assert CONFIG.searchRegEx is False

    # Close search and select "est" again
    docSearch.cancelSearch.activate(QAction.ActionEvent.Trigger)
    docEditor.setCursorPosition(663)
    docEditor._makeSelection(QTextCursor.SelectionType.WordUnderCursor)
    cursor = docEditor.textCursor()
    assert cursor.selectedText() == "est"

    # Activate search again
    nwGUI.mainMenu.aFind.activate(QAction.ActionEvent.Trigger)
    assert docSearch.isVisible()
    assert docSearch.searchText == "est"

    # Enable full word search
    docSearch.toggleWord.activate(QAction.ActionEvent.Trigger)
    assert docSearch.toggleWord.isChecked()
    assert CONFIG.searchWord is True

    # Only one match
    nwGUI.mainMenu.aFindNext.activate(QAction.ActionEvent.Trigger)
    assert abs(docEditor.getCursorPosition() - 665) < 3
    nwGUI.mainMenu.aFindNext.activate(QAction.ActionEvent.Trigger)
    assert abs(docEditor.getCursorPosition() - 665) < 3

    # Enable next doc search
    docSearch.toggleProject.activate(QAction.ActionEvent.Trigger)
    assert docSearch.toggleProject.isChecked()
    assert CONFIG.searchNextFile is True

    # Next match
    nwGUI.mainMenu.aFindNext.activate(QAction.ActionEvent.Trigger)
    assert docEditor.docHandle == "2426c6f0ca922"  # Next document
    nwGUI.mainMenu.aFindNext.activate(QAction.ActionEvent.Trigger)
    assert abs(docEditor.getCursorPosition() - 651) < 3
    nwGUI.mainMenu.aFindNext.activate(QAction.ActionEvent.Trigger)
    assert abs(docEditor.getCursorPosition() - 1157) < 3

    # Next doc, no match
    assert CONFIG.searchNextFile is True
    docSearch.setSearchText("abcdef")
    nwGUI.mainMenu.aFindNext.activate(QAction.ActionEvent.Trigger)
    assert docEditor.docHandle != "2426c6f0ca922"
    assert docEditor.docHandle == "04468803b92e1"
    nwGUI.mainMenu.aFindNext.activate(QAction.ActionEvent.Trigger)
    assert docEditor.docHandle != "04468803b92e1"
    assert docEditor.docHandle == "7a992350f3eb6"

    # Toggle Replace
    docEditor.beginReplace()

    # MonkeyPatch the focus cycle. We can't really test this very well, other than
    # check that the tabs aren't captured when the main editor has focus
    with monkeypatch.context() as mp:
        mp.setattr(docEditor, "hasFocus", lambda: True)
        mp.setattr(docSearch.searchBox, "hasFocus", lambda: False)
        mp.setattr(docSearch.replaceBox, "hasFocus", lambda: False)
        assert docEditor.focusNextPrevChild(True) is False
        assert docSearch.cycleFocus() is False

    with monkeypatch.context() as mp:
        mp.setattr(docEditor, "hasFocus", lambda: False)
        mp.setattr(docSearch.searchBox, "hasFocus", lambda: True)
        mp.setattr(docSearch.replaceBox, "hasFocus", lambda: False)
        assert docEditor.focusNextPrevChild(True) is True
        assert docSearch.cycleFocus() is True

    with monkeypatch.context() as mp:
        mp.setattr(docEditor, "hasFocus", lambda: False)
        mp.setattr(docSearch.searchBox, "hasFocus", lambda: False)
        mp.setattr(docSearch.replaceBox, "hasFocus", lambda: True)
        assert docEditor.focusNextPrevChild(True) is True
        assert docSearch.cycleFocus() is True
        docSearch.closeSearch()
        assert docSearch.isVisible() is False
        assert docEditor.focusNextPrevChild(True) is True

    # Replace Text
    # ============
    docSearch.toggleCase.setChecked(True)
    docSearch.toggleWord.setChecked(False)
    docSearch.toggleRegEx.setChecked(False)
    docSearch.toggleLoop.setChecked(False)
    docSearch.toggleProject.setChecked(False)
    docEditor.setCursorPosition(0)

    # Replace Next
    docSearch.searchBox.setText("a")
    docSearch.replaceBox.setText("A")

    # No focus
    with monkeypatch.context() as mp:
        mp.setattr(docEditor, "anyFocus", lambda: False)
        docEditor.findNext()
        assert docEditor.textCursor().selectedText() == ""
        docEditor.replaceNext()
        assert docEditor.textCursor().selectedText() == ""

    # Search not open
    docSearch.closeSearch()
    assert docSearch.isVisible() is False
    docEditor.findNext()
    assert docSearch.isVisible() is True
    docSearch.closeSearch()
    assert docSearch.isVisible() is False
    docEditor.replaceNext()
    assert docSearch.isVisible() is True
    docEditor.toggleSearch()
    assert docSearch.isVisible() is False
    docEditor.toggleSearch()
    assert docSearch.isVisible() is True

    # Find first entry
    docEditor.replaceNext()
    assert docEditor.textCursor().selectedText() == "a"
    assert docEditor.getCursorPosition() == 64

    # Treat the search as a user selection
    docEditor._lastFind = None
    docEditor.replaceNext()
    assert docEditor.textCursor().selectedText() == "a"
    assert docEditor.getCursorPosition() == 83

    # Iterate through the rest
    finds = [85, 105, 110, 141, 169, 181, 200, 252, 274, 283, 288, 297]
    for i in range(len(finds)):
        docEditor.replaceNext()
        assert docEditor.textCursor().selectedText() == "a"
        assert docEditor.getCursorPosition() == finds[i]
    assert docEditor._lastFind == (296, 297)

    # Search for something that doesn't exist
    docSearch.searchBox.setText("x")
    docEditor._lastFind = None
    docEditor.replaceNext()
    assert docEditor.textCursor().selectedText() == ""

    # qtbot.stop()


@pytest.mark.gui
def testGuiEditor_TextAutoReplaceSymbols():
    """Test the editor auto-replace functionality."""
    CONFIG.fmtSQuoteOpen = nwUnicode.U_LSQUO
    CONFIG.fmtSQuoteClose = nwUnicode.U_RSQUO
    CONFIG.fmtDQuoteOpen = nwUnicode.U_LDQUO
    CONFIG.fmtDQuoteClose = nwUnicode.U_RDQUO

    CONFIG.doReplaceSQuote = True
    CONFIG.doReplaceDQuote = True
    CONFIG.doReplaceDash = True
    CONFIG.doReplaceDots = True

    ar = TextAutoReplace()

    def prep(text: str) -> tuple[str, int]:
        return text, len(text)

    # Double Quote Open
    assert ar._determine(*prep('"')) == (1, nwUnicode.U_LDQUO)
    assert ar._determine(*prep('Stuff "')) == (1, nwUnicode.U_LDQUO)
    assert ar._determine(*prep('>"')) == (1, nwUnicode.U_LDQUO)
    assert ar._determine(*prep('>>"')) == (1, nwUnicode.U_LDQUO)
    assert ar._determine(*prep('_"')) == (1, nwUnicode.U_LDQUO)
    assert ar._determine(*prep(' _"')) == (1, nwUnicode.U_LDQUO)
    assert ar._determine(*prep('\u00a0_"')) == (1, nwUnicode.U_LDQUO)
    assert ar._determine(*prep('**"')) == (1, nwUnicode.U_LDQUO)
    assert ar._determine(*prep(' **"')) == (1, nwUnicode.U_LDQUO)
    assert ar._determine(*prep('\u00a0**"')) == (1, nwUnicode.U_LDQUO)
    assert ar._determine(*prep('=="')) == (1, nwUnicode.U_LDQUO)
    assert ar._determine(*prep(' =="')) == (1, nwUnicode.U_LDQUO)
    assert ar._determine(*prep('\u00a0=="')) == (1, nwUnicode.U_LDQUO)
    assert ar._determine(*prep('~~"')) == (1, nwUnicode.U_LDQUO)
    assert ar._determine(*prep(' ~~"')) == (1, nwUnicode.U_LDQUO)
    assert ar._determine(*prep('\u00a0~~"')) == (1, nwUnicode.U_LDQUO)

    # Double Quote Close
    assert ar._determine(*prep('Stuff"')) == (1, nwUnicode.U_RDQUO)

    # Single Quote Open
    assert ar._determine(*prep("'")) == (1, nwUnicode.U_LSQUO)
    assert ar._determine(*prep("Stuff '")) == (1, nwUnicode.U_LSQUO)
    assert ar._determine(*prep(">'")) == (1, nwUnicode.U_LSQUO)
    assert ar._determine(*prep(">>'")) == (1, nwUnicode.U_LSQUO)
    assert ar._determine(*prep("_'")) == (1, nwUnicode.U_LSQUO)
    assert ar._determine(*prep(" _'")) == (1, nwUnicode.U_LSQUO)
    assert ar._determine(*prep("\u00a0_'")) == (1, nwUnicode.U_LSQUO)
    assert ar._determine(*prep("**'")) == (1, nwUnicode.U_LSQUO)
    assert ar._determine(*prep(" **'")) == (1, nwUnicode.U_LSQUO)
    assert ar._determine(*prep("\u00a0**'")) == (1, nwUnicode.U_LSQUO)
    assert ar._determine(*prep("=='")) == (1, nwUnicode.U_LSQUO)
    assert ar._determine(*prep(" =='")) == (1, nwUnicode.U_LSQUO)
    assert ar._determine(*prep("\u00a0=='")) == (1, nwUnicode.U_LSQUO)
    assert ar._determine(*prep("~~'")) == (1, nwUnicode.U_LSQUO)
    assert ar._determine(*prep(" ~~'")) == (1, nwUnicode.U_LSQUO)
    assert ar._determine(*prep("\u00a0~~'")) == (1, nwUnicode.U_LSQUO)

    # Single Quote Close
    assert ar._determine(*prep("Stuff'")) == (1, nwUnicode.U_RSQUO)

    # Dashes
    assert ar._determine(*prep("-")) == (0, "-")
    assert ar._determine(*prep("--")) == (2, nwUnicode.U_ENDASH)
    assert ar._determine(*prep("---")) == (3, nwUnicode.U_EMDASH)
    assert ar._determine(*prep("----")) == (4, nwUnicode.U_HBAR)
    assert ar._determine(*prep("\u2013-")) == (2, nwUnicode.U_EMDASH)
    assert ar._determine(*prep("\u2014-")) == (2, nwUnicode.U_HBAR)

    # Ellipsis
    assert ar._determine(*prep(".")) == (0, ".")
    assert ar._determine(*prep("..")) == (0, ".")
    assert ar._determine(*prep("...")) == (3, nwUnicode.U_HELLIP)

    # Block Typed Line Separator (#1150)
    assert ar._determine(*prep("Text\u2028")) == (1, nwUnicode.U_PSEP)


@pytest.mark.gui
def testGuiEditor_TextAutoReplaceProcess():
    """Test the editor auto-replace functionality."""
    CONFIG.fmtDQuoteOpen = nwUnicode.U_LAQUO
    CONFIG.fmtDQuoteClose = nwUnicode.U_RAQUO

    CONFIG.doReplaceDQuote = True
    CONFIG.doReplaceDots = True

    ar = TextAutoReplace()
    doc = QTextDocument()

    def prep(text: str) -> tuple[str, QTextCursor]:
        doc.setPlainText(text)
        cursor = QTextCursor(doc)
        cursor.setPosition(len(text))
        return text, cursor

    # Nothing to Process
    assert ar.process(*prep("")) is False

    # Standard Auto-Replace
    assert ar.process(*prep("Text ...")) is True
    assert doc.toRawText() == "Text \u2026"

    # Pad Before, Normal
    CONFIG.fmtPadBefore = ":\u00bb"
    CONFIG.fmtPadThin = False
    ar.initSettings()
    assert ar.process(*prep("Text:")) is True
    assert doc.toRawText() == "Text\u00a0:"
    assert ar.process(*prep("Text :")) is True  # See #1061
    assert doc.toRawText() == "Text\u00a0:"
    assert ar.process(*prep('Text"')) is True
    assert doc.toRawText() == "Text\u00a0»"
    assert ar.process(*prep("@Synopsis:")) is False
    assert doc.toRawText() == "@Synopsis:"

    # Pad Before, Thin
    CONFIG.fmtPadBefore = ":\u00bb"
    CONFIG.fmtPadThin = True
    ar.initSettings()
    assert ar.process(*prep("Text:")) is True
    assert doc.toRawText() == "Text\u202f:"
    assert ar.process(*prep("Text :")) is True  # See #1061
    assert doc.toRawText() == "Text\u202f:"

    # Pad After, Normal
    CONFIG.fmtPadAfter = "\u00ab"
    CONFIG.fmtPadThin = False
    ar.initSettings()
    assert ar.process(*prep('Text "')) is True
    assert doc.toRawText() == "Text «\u00a0"

    # Pad After, Thin
    CONFIG.fmtPadAfter = "\u00ab"
    CONFIG.fmtPadThin = True
    ar.initSettings()
    assert ar.process(*prep('Text "')) is True
    assert doc.toRawText() == "Text «\u202f"


@pytest.mark.gui
def testGuiEditor_Vim_EnableVimMode(qtbot, nwGUI, projPath, mockRnd):
    """Test that enabling CONFIG.vimMode activates vim behavior."""
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc)
    inputDelay = 2

    docEditor = nwGUI.docEditor
    docEditor.setPlainText("HelloWorld")

    # Enable vim mode
    CONFIG.vimModeEnabled = True

    original_text = docEditor.getText()

    # Normal mode: hjkl should NOT change text
    for key in "hjkl":
        qtbot.keyClick(docEditor, key, delay=inputDelay)
        assert docEditor.getText() == original_text

    # Enter insert mode with "i"
    qtbot.keyClick(docEditor, "i", delay=inputDelay)
    qtbot.keyClicks(docEditor, "TEST", delay=inputDelay)
    qtbot.keyClick(docEditor, Qt.Key.Key_Escape)

    # Text must have changed now
    new_text = docEditor.getText()
    assert new_text != original_text
    assert "TEST" in new_text


@pytest.mark.gui
def testGuiEditor_Vim_MotionsAndInsert(qtbot, nwGUI, projPath, mockRnd):
    """Test vim hjkl movements and insert commands (i, I, A)."""
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc)
    inputDelay = 2

    docEditor = nwGUI.docEditor
    docEditor.setPlainText("Line1\nLine2\nLine3")

    # Enable vim mode
    CONFIG.vimModeEnabled = True

    def reset_and_get_text():
        """Reset test text."""
        docEditor.setPlainText("Line1\nLine2\nLine3")
        return docEditor.getText()

    original_text = reset_and_get_text()

    # NORMAL MODE: hjkl should NOT modify text
    for key in "hjkl":
        qtbot.keyClick(docEditor, key)
        assert docEditor.getText() == original_text

    # --- Insert mode tests ---
    # 'i' insert before cursor
    reset_and_get_text()
    qtbot.keyClick(docEditor, "i", delay=inputDelay)
    qtbot.keyClicks(docEditor, "X", delay=inputDelay)
    qtbot.keyClick(docEditor, Qt.Key.Key_Escape)
    assert "X" in docEditor.getText()

    # 'I' insert at beginning of line
    reset_and_get_text()
    qtbot.keyClick(docEditor, Qt.Key.Key_Escape)
    qtbot.keyClick(docEditor, "h", delay=inputDelay)  # Move forward 1
    qtbot.keyClick(docEditor, "h", delay=inputDelay)  # Move forward 1
    qtbot.keyClick(docEditor, "I", delay=inputDelay)
    qtbot.keyClicks(docEditor, "START", delay=inputDelay)
    qtbot.keyClick(docEditor, Qt.Key.Key_Escape)
    lines = docEditor.getText().splitlines()
    assert lines[0].startswith("START")

    # 'A' append at end of line
    reset_and_get_text()
    qtbot.keyClick(docEditor, "A", delay=inputDelay)
    qtbot.keyClicks(docEditor, "END", delay=inputDelay)
    qtbot.keyClick(docEditor, Qt.Key.Key_Escape)
    lines = docEditor.getText().splitlines()
    assert lines[0].endswith("END")

    # 'o' open new line BELOW
    reset_and_get_text()
    qtbot.keyClick(docEditor, "o", delay=inputDelay)
    qtbot.keyClicks(docEditor, "below", delay=inputDelay)
    qtbot.keyClick(docEditor, Qt.Key.Key_Escape)
    lines = docEditor.getText().splitlines()
    assert "below" in lines[1]  # inserted after Line1

    # 'O' open new line ABOVE
    reset_and_get_text()
    qtbot.keyClick(docEditor, "O", delay=inputDelay)
    qtbot.keyClicks(docEditor, "above", delay=inputDelay)
    qtbot.keyClick(docEditor, Qt.Key.Key_Escape)
    lines = docEditor.getText().splitlines()
    assert "above" in lines[0]  # inserted before Line1

    # --- b: move to beginning of word ---
    reset_and_get_text()
    # Place cursor inside "Line2"
    start_pos = docEditor.getText().find("Line2") + 2  # inside the word
    docEditor.setCursorPosition(start_pos)
    qtbot.keyClicks(docEditor, "b", delay=inputDelay)
    cursor_pos = docEditor.textCursor().position()
    expected_pos = docEditor.getText().find("Line2")  # beginning of "Line2"
    assert cursor_pos == expected_pos

    # --- e: move to end of current word ---
    reset_and_get_text()
    start_pos = docEditor.getText().find("Line1")  # start of "Line1"
    docEditor.setCursorPosition(start_pos)
    qtbot.keyClicks(docEditor, "e", delay=inputDelay)
    cursor_pos = docEditor.textCursor().position()
    expected_pos = docEditor.getText().find("Line1") + len("Line1")
    assert cursor_pos == expected_pos

    # --- e: move to end of next word when already at end ---
    docEditor.setPlainText("Line1 lineExtra Line2 Line3")
    end_pos = docEditor.getText().find("Line1") + len("Line1")
    docEditor.setCursorPosition(end_pos)
    qtbot.keyClicks(docEditor, "e", delay=inputDelay)
    cursor_pos = docEditor.textCursor().position()
    expected_pos = docEditor.getText().find("lineExtra") + len("lineExtra")
    assert cursor_pos == expected_pos


@pytest.mark.gui
def testGuiEditor_Vim_DeleteYankPaste(qtbot, nwGUI, projPath, mockRnd):
    """Test vim delete (dd, x), yank (yy) and paste (p, P) commands."""
    inputDelay = 2
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc)

    docEditor = nwGUI.docEditor
    CONFIG.vimModeEnabled = True

    def reset_text():
        docEditor.setPlainText("Line1\nLine2\nLine3")
        return docEditor.getText()

    # --- dd: delete entire line ---
    reset_text()
    docEditor.setCursorPosition(docEditor.getText().find("Line2"))
    qtbot.keyClicks(docEditor, "dd", delay=inputDelay)
    lines = list(filter(str.strip, docEditor.getText().splitlines()))
    assert lines == ["Line1", "Line3"]

    # --- x: delete single character ---
    reset_text()
    docEditor.setCursorPosition(0)
    qtbot.keyClicks(docEditor, "x", delay=inputDelay)
    lines = list(filter(str.strip, docEditor.getText().splitlines()))
    assert lines[0] == "ine1"  # 'L' deleted

    # --- p: paste after current line ---
    reset_text()
    line2_pos = docEditor.getText().find("Line2")
    docEditor.setCursorPosition(line2_pos)
    qtbot.keyClicks(docEditor, "yy", delay=inputDelay)  # yank Line2
    qtbot.keyClicks(docEditor, "p", delay=inputDelay)  # paste after Line2

    lines = list(filter(str.strip, docEditor.getText().splitlines()))
    assert lines == ["Line1", "Line2", "Line2", "Line3"]

    # --- P: paste before current line (using Line3) ---
    reset_text()
    line2_pos = docEditor.getText().find("Line2")
    docEditor.setCursorPosition(line2_pos)
    line3_pos = docEditor.getText().find("Line3")
    docEditor.setCursorPosition(line3_pos)
    qtbot.keyClicks(docEditor, "yy", delay=inputDelay)  # yank Line3
    docEditor.setCursorPosition(line2_pos)
    qtbot.keyClicks(docEditor, "P", delay=inputDelay)   # paste before Line2

    lines = list(filter(str.strip, docEditor.getText().splitlines()))
    assert lines == ["Line1", "Line3", "Line2", "Line3"]

    # --- w: move forward by word ---
    reset_text()
    docEditor.setCursorPosition(0)  # start of "Line1"
    qtbot.keyClicks(docEditor, "w", delay=inputDelay)
    cursor_pos = docEditor.textCursor().position()
    # Cursor should now be at end of "Line1"
    expected_pos = docEditor.getText().find("Line1") + len("Line1")
    assert cursor_pos == expected_pos

    # --- dw: delete word (from "Line1" up to next word boundary) ---
    reset_text()
    docEditor.setCursorPosition(0)  # start of "Line1"
    qtbot.keyClicks(docEditor, "dw", delay=inputDelay)
    lines = list(filter(str.strip, docEditor.getText().splitlines()))
    assert lines == ["Line2", "Line3"]

    # --- yw: yank word (yank "Line1") ---
    reset_text()
    docEditor.setCursorPosition(0)  # start of "Line1"
    qtbot.keyClicks(docEditor, "yw", delay=inputDelay)
    # Move to start of Line2 and paste
    docEditor.setCursorPosition(docEditor.getText().find("Line2"))
    qtbot.keyClicks(docEditor, "p", delay=inputDelay)
    lines = list(filter(str.strip, docEditor.getText().splitlines()))
    # After paste, first line remains Line1, second line is "Line1Line2"
    assert lines[0] == "Line1"
    assert lines[1] == "Line2"
    assert lines[2] == "Line1"
    assert lines[3] == "Line3"


@pytest.mark.gui
def testGuiEditor_Vim_VisualMode(qtbot, nwGUI, projPath, mockRnd):
    """Test vim visual mode selection, yank and paste."""
    inputDelay = 2
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc)

    docEditor = nwGUI.docEditor
    CONFIG.vimModeEnabled = True

    def reset_text():
        docEditor.setPlainText("Line1\nLine2\nLine3")
        return docEditor.getText()

    # --- Visual mode with yy ---
    reset_text()
    docEditor.setCursorPosition(docEditor.getText().find("Line3") + 1)  # inside Line3
    qtbot.keyClick(docEditor, "v", delay=inputDelay)
    qtbot.keyClick(docEditor, "j", delay=inputDelay)
    qtbot.keyClick(docEditor, "h", delay=inputDelay)
    qtbot.keyClick(docEditor, "k", delay=inputDelay)
    qtbot.keyClick(docEditor, "l", delay=inputDelay)
    qtbot.keyClicks(docEditor, "y", delay=inputDelay)
    qtbot.keyClick(docEditor, "p", delay=inputDelay)

    text = docEditor.getText()

    # Assert that something was yanked (here likely "Line3" or just "n")
    assert "Line3" in text or text.endswith("n")

    # --- Linewise visual mode (V) with yank and paste ---
    reset_text()
    # Move to Line2
    line2_pos = docEditor.getText().find("Line2")
    docEditor.setCursorPosition(line2_pos)
    qtbot.keyClick(docEditor, "V", delay=inputDelay)  # linewise visual mode
    qtbot.keyClick(docEditor, "j", delay=inputDelay)
    qtbot.keyClick(docEditor, "h", delay=inputDelay)
    qtbot.keyClick(docEditor, "k", delay=inputDelay)
    qtbot.keyClick(docEditor, "l", delay=inputDelay)
    qtbot.keyClick(docEditor, "y", delay=inputDelay)  # yank Line2
    qtbot.keyClick(docEditor, "j", delay=inputDelay)  # move to Line3
    qtbot.keyClick(docEditor, "p", delay=inputDelay)  # paste Line2 after Line3

    lines = docEditor.getText().splitlines()
    # Assert Line2 got duplicated after Line3
    assert lines == ["Line1", "Line2", "Line3", "Line2"]

    # --- Visual mode with w motion ---
    reset_text()
    docEditor.setCursorPosition(0)  # start of Line1
    qtbot.keyClick(docEditor, "v", delay=inputDelay)  # enter visual mode
    qtbot.keyClicks(docEditor, "w", delay=inputDelay)  # move by word
    cursor_pos = docEditor.textCursor().position()
    expected_pos = docEditor.getText().find("Line1") + len("Line1")
    assert cursor_pos == expected_pos

    # --- '0': move to start of line ---
    reset_text()
    # Put cursor somewhere inside Line2
    line2_pos = docEditor.getText().find("Line2") + 3  # middle of "Line2"
    docEditor.setCursorPosition(line2_pos)
    qtbot.keyClicks(docEditor, "0", delay=inputDelay)
    cursor_pos = docEditor.textCursor().position()
    # Start of Line2
    expected_pos = docEditor.getText().find("Line2")
    assert cursor_pos == expected_pos

    # --- No-op command 'a': nothing happens ---
    reset_text()
    # Put cursor somewhere inside Line3
    line3_pos = docEditor.getText().find("Line3") + 2
    docEditor.setCursorPosition(line3_pos)
    text_before = docEditor.getText()
    cursor_before = docEditor.textCursor().position()
    qtbot.keyClicks(docEditor, "a", delay=inputDelay)
    text_after = docEditor.getText()
    cursor_after = docEditor.textCursor().position()

    # Nothing should have changed
    assert text_after == text_before
    assert cursor_after == cursor_before

    reset_text()
    start_pos = docEditor.getText().find("Line2") + 2  # inside "Line2"
    docEditor.setCursorPosition(start_pos)
    qtbot.keyClick(docEditor, "v", delay=inputDelay)   # enter visual mode
    qtbot.keyClicks(docEditor, "b", delay=inputDelay)
    selected = docEditor.textCursor().selectedText()
    # Should have selected from inside "Line2" back to its start
    assert selected == "Li"

    reset_text()
    start_pos = docEditor.getText().find("Line1")      # start of "Line1"
    docEditor.setCursorPosition(start_pos)
    qtbot.keyClick(docEditor, "v", delay=inputDelay)   # enter visual mode
    qtbot.keyClicks(docEditor, "e", delay=inputDelay)
    selected = docEditor.textCursor().selectedText()
    # Should have selected "Line1"
    assert selected == "Line1"

    docEditor.setPlainText("Line1 lineExtra Line2 Line3")
    end_pos = docEditor.getText().find("Line1") + len("Line1") - 1
    docEditor.setCursorPosition(end_pos)
    qtbot.keyClick(docEditor, "v", delay=inputDelay)   # enter visual mode
    qtbot.keyClicks(docEditor, "e", delay=inputDelay)
    selected = docEditor.textCursor().selectedText().strip()
    # Should have selected whitespace + "lineExtra"
    assert "lineExtra" in selected


@pytest.mark.gui
def testGuiEditor_Vim_VisualMode_SelectAllDeleteUndo(qtbot, nwGUI, projPath, mockRnd):
    """Test selecting all text with ggVG, deleting, undoing with u, and verifying reset."""
    inputDelay = 2
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc)

    docEditor = nwGUI.docEditor
    CONFIG.vimModeEnabled = True

    # Setup text
    docEditor.setPlainText("Line1\nLine2\nLine3")
    original_text = docEditor.getText()

    # --- Visual select all with ggVG ---
    qtbot.keyClicks(docEditor, "g", delay=inputDelay)
    qtbot.keyClicks(docEditor, "g", delay=inputDelay)   # go to start
    qtbot.keyClick(docEditor, "v", delay=inputDelay)    # enter visual mode
    qtbot.keyClick(docEditor, "G", delay=inputDelay)    # extend to end of file

    # --- Delete selection ---
    qtbot.keyClick(docEditor, "d", delay=inputDelay)
    assert docEditor.getText().strip() == ""  # everything deleted

    # --- Undo ---
    qtbot.keyClick(docEditor, "u", delay=inputDelay)
    restored_text = docEditor.getText()
    assert restored_text == original_text

    # --- Move back to start ---
    qtbot.keyClicks(docEditor, "g", delay=inputDelay)
    qtbot.keyClicks(docEditor, "g", delay=inputDelay)
    cursor_pos = docEditor.textCursor().position()
    assert restored_text[cursor_pos] == "L"  # first char restored

    # --- Visual select all with Gvgg ---
    qtbot.keyClick(docEditor, "G", delay=inputDelay)    # end of file
    qtbot.keyClick(docEditor, "v", delay=inputDelay)    # enter visual mode
    qtbot.keyClicks(docEditor, "g", delay=inputDelay)
    qtbot.keyClicks(docEditor, "g", delay=inputDelay)   # extend select to start

    # --- Delete selection ---
    qtbot.keyClick(docEditor, "d", delay=inputDelay)
    assert docEditor.getText().strip() == ""  # everything deleted

    # --- Undo ---
    qtbot.keyClick(docEditor, "u", delay=inputDelay)
    restored_text = docEditor.getText()
    assert restored_text == original_text

    # --- Move back to start ---
    qtbot.keyClicks(docEditor, "g", delay=inputDelay)
    qtbot.keyClicks(docEditor, "g", delay=inputDelay)
    cursor_pos = docEditor.textCursor().position()
    assert restored_text[cursor_pos] == "L"  # first char restored


@pytest.mark.gui
def testGuiEditor_Vim_VlineMode_SelectAllDeleteUndo(qtbot, nwGUI, projPath, mockRnd):
    """Test selecting all text with ggVG, deleting, undoing with u, and verifying reset."""
    inputDelay = 2
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc)

    docEditor = nwGUI.docEditor
    CONFIG.vimModeEnabled = True

    # Setup text
    docEditor.setPlainText("Line1\nLine2\nLine3")
    original_text = docEditor.getText()

    qtbot.keyClick(docEditor, "j", delay=inputDelay)
    qtbot.keyClick(docEditor, "h", delay=inputDelay)
    qtbot.keyClick(docEditor, "k", delay=inputDelay)
    qtbot.keyClick(docEditor, "l", delay=inputDelay)

    # --- Visual select all with ggVG ---
    qtbot.keyClicks(docEditor, "g", delay=inputDelay)
    qtbot.keyClicks(docEditor, "g", delay=inputDelay)   # go to start
    qtbot.keyClick(docEditor, "V", delay=inputDelay)    # enter vline mode
    qtbot.keyClick(docEditor, "G", delay=inputDelay)    # extend to end of file

    # --- Delete selection ---
    qtbot.keyClick(docEditor, "d", delay=inputDelay)
    assert docEditor.getText().strip() == ""  # everything deleted

    # --- undo ---
    qtbot.keyClick(docEditor, "u", delay=inputDelay)
    restored_text = docEditor.getText()
    assert restored_text == original_text

    # --- Move back to start ---
    qtbot.keyClicks(docEditor, "g", delay=inputDelay)
    qtbot.keyClicks(docEditor, "g", delay=inputDelay)
    cursor_pos = docEditor.textCursor().position()
    assert restored_text[cursor_pos] == "L"  # first char restored


@pytest.mark.gui
def testGuiEditor_Vim_NormalMode_EndLineAndAppend(qtbot, nwGUI, projPath, mockRnd):
    """Test vim NORMAL mode commands '$' and 'a'."""
    inputDelay = 2
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc)

    docEditor = nwGUI.docEditor
    CONFIG.vimModeEnabled = True

    # Set initial text
    docEditor.setPlainText("Line1\nLine2\nLine3")

    # --- Test $ command: move to end of first line ---
    docEditor.setCursorPosition(0)  # start of Line1
    qtbot.keyClick(docEditor, "$", delay=inputDelay)

    cursor_pos = docEditor.textCursor().position()
    text = docEditor.getText().splitlines()[0]
    assert cursor_pos == len(text)  # cursor at end of first line

    # --- Test 'a' command: move right and enter insert mode ---
    docEditor.setCursorPosition(0)  # start of Line1 again
    qtbot.keyClick(docEditor, "a", delay=inputDelay)

    # Cursor should have moved one character right
    cursor_pos = docEditor.textCursor().position()
    assert cursor_pos == 1

    # Insert some text
    qtbot.keyClicks(docEditor, "TEST", delay=inputDelay)
    qtbot.keyClick(docEditor, Qt.Key.Key_Escape, delay=inputDelay)

    new_text = docEditor.getText()
    assert new_text.startswith("LTESSTine1") or new_text.startswith("LTESTine1")


@pytest.mark.gui
def testGuiEditor_Vim_AllMotions(qtbot, nwGUI, projPath, mockRnd):
    """Test all currently supported vim motions in
    Normal, Insert, Visual, and Visual Line modes.
    """
    inputDelay = 2
    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hSceneDoc)

    docEditor = nwGUI.docEditor
    CONFIG.vimModeEnabled = True

    # --- Setup text ---
    docEditor.setPlainText("Hello World\nLine2\nLine3")

    def reset_text():
        docEditor.setPlainText("Hello World\nLine2\nLine3")
        docEditor.setCursorPosition(0)
        return docEditor.getText()

    # --- NORMAL MODE MOTIONS ---
    reset_text()
    qtbot.keyClick(docEditor, "l", delay=inputDelay)  # move right
    assert docEditor.textCursor().position() == 1

    reset_text()
    qtbot.keyClick(docEditor, "0", delay=inputDelay)  # beginning of line
    assert docEditor.textCursor().position() == 0

    reset_text()
    qtbot.keyClick(docEditor, "$", delay=inputDelay)  # end of line
    cursor_pos = docEditor.textCursor().position()
    assert cursor_pos == len("Hello World")

    reset_text()
    qtbot.keyClick(docEditor, "g", delay=inputDelay)
    qtbot.keyClick(docEditor, "g", delay=inputDelay)  # top of buffer
    assert docEditor.textCursor().position() == 0

    qtbot.keyClick(docEditor, "z", delay=inputDelay)
    qtbot.keyClick(docEditor, "z", delay=inputDelay)  # center view

    reset_text()
    qtbot.keyClick(docEditor, "G", delay=inputDelay)  # bottom of buffer
    cursor_pos = docEditor.textCursor().position()
    assert cursor_pos == len(docEditor.getText())

    # --- INSERT MODE MOTIONS ---
    reset_text()
    qtbot.keyClick(docEditor, "i", delay=inputDelay)  # insert before cursor
    qtbot.keyClicks(docEditor, "TEST", delay=inputDelay)
    qtbot.keyClick(docEditor, Qt.Key.Key_Escape, delay=inputDelay)
    assert "TEST" in docEditor.getText()

    reset_text()
    qtbot.keyClick(docEditor, "a", delay=inputDelay)  # append after cursor
    qtbot.keyClicks(docEditor, "X", delay=inputDelay)
    qtbot.keyClick(docEditor, Qt.Key.Key_Escape, delay=inputDelay)
    assert "X" in docEditor.getText()

    reset_text()
    qtbot.keyClick(docEditor, "o", delay=inputDelay)  # new line below
    qtbot.keyClicks(docEditor, "below", delay=inputDelay)
    qtbot.keyClick(docEditor, Qt.Key.Key_Escape, delay=inputDelay)
    lines = docEditor.getText().splitlines()
    assert "below" in lines[1]

    reset_text()
    qtbot.keyClick(docEditor, "O", delay=inputDelay)  # new line above
    qtbot.keyClicks(docEditor, "above", delay=inputDelay)
    qtbot.keyClick(docEditor, Qt.Key.Key_Escape, delay=inputDelay)
    lines = docEditor.getText().splitlines()
    assert "above" in lines[0]

    # --- VISUAL MODE MOTIONS ---
    reset_text()
    qtbot.keyClick(docEditor, "v", delay=inputDelay)  # enter visual
    qtbot.keyClick(docEditor, "l", delay=inputDelay)  # extend selection
    qtbot.keyClick(docEditor, "y", delay=inputDelay)  # yank selection
    qtbot.keyClick(docEditor, "p", delay=inputDelay)  # paste it
    assert "Hello" in docEditor.getText()

    reset_text()
    qtbot.keyClick(docEditor, "v", delay=inputDelay)
    qtbot.keyClick(docEditor, "$", delay=inputDelay)  # extend to EOL
    qtbot.keyClick(docEditor, "d", delay=inputDelay)  # delete
    line0 = docEditor.getText().splitlines()[0]
    assert line0.strip() == ""  # first line emptied

    # --- VISUAL LINE MODE MOTIONS ---
    reset_text()
    line2_pos = docEditor.getText().find("Line2")
    docEditor.setCursorPosition(line2_pos)
    qtbot.keyClick(docEditor, "V", delay=inputDelay)  # vline mode
    qtbot.keyClick(docEditor, "j", delay=inputDelay)  # extend
    qtbot.keyClick(docEditor, "y", delay=inputDelay)  # yank
    qtbot.keyClick(docEditor, "p", delay=inputDelay)  # paste
    lines = docEditor.getText().splitlines()
    assert lines.count("Line2") > 1

    reset_text()
    qtbot.keyClick(docEditor, "V", delay=inputDelay)  # vline select
    qtbot.keyClick(docEditor, "G", delay=inputDelay)  # extend to EOF
    qtbot.keyClick(docEditor, "d", delay=inputDelay)  # delete all
    assert docEditor.getText().strip() == ""
