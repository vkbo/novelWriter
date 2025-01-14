"""
novelWriter – Main GUI Viewer Class Tester
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
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from PyQt6.QtCore import QEvent, QMimeData, QPointF, Qt, QUrl
from PyQt6.QtGui import (
    QAction, QDesktopServices, QDragEnterEvent, QDragMoveEvent, QDropEvent,
    QMouseEvent, QTextCursor
)
from PyQt6.QtWidgets import QApplication, QMenu, QTextBrowser

from novelwriter import CONFIG, SHARED
from novelwriter.common import decodeMimeHandles
from novelwriter.enum import nwChange, nwDocAction
from novelwriter.formats.toqdoc import ToQTextDocument
from novelwriter.types import QtModNone, QtMouseLeft, QtMouseMiddle

from tests.mocked import causeException
from tests.tools import C, buildTestProject


@pytest.mark.gui
def testGuiViewer_Main(qtbot, monkeypatch, nwGUI, prjLipsum):
    """Test the document viewer."""
    # Open project
    assert nwGUI.openProject(prjLipsum)
    docEditor = nwGUI.docEditor
    docViewer = nwGUI.docViewer

    # Select a document in the project tree
    nwGUI.projView.setSelectedHandle("88243afbe5ed8")
    nwGUI.openDocument("88243afbe5ed8")

    # Can only open a document
    assert docViewer.loadText("b3643d0f92e32") is False

    # Middle-click the selected item
    index = SHARED.project.tree.model.indexFromHandle("88243afbe5ed8")
    rect = nwGUI.projView.projTree.visualRect(index)
    qtbot.mouseClick(nwGUI.projView.projTree.viewport(), QtMouseMiddle, pos=rect.center())
    assert docViewer.docHandle == "88243afbe5ed8"

    # Clear selection
    nwGUI.projView.projTree.clearSelection()
    assert nwGUI.projView.projTree.getSelectedHandle() is None

    # Re-select via header click
    button = QtMouseLeft
    modifier = QtModNone
    event = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(), button, button, modifier)
    docViewer.docHeader.mousePressEvent(event)
    assert nwGUI.projView.projTree.getSelectedHandle() == "88243afbe5ed8"

    # Reload the text
    origText = docViewer.toPlainText()
    docViewer.setPlainText("Oops, all gone!")
    docViewer.docHeader._refreshDocument()
    assert docViewer.toPlainText() == origText

    # Open in editor
    nwGUI.closeDocument()
    assert docEditor.docHandle is None
    docViewer.docHeader._editDocument()
    assert docEditor.docHandle == docViewer.docHandle

    # Select word
    cursor = docViewer.textCursor()
    cursor.setPosition(100)
    docViewer.setTextCursor(cursor)
    docViewer._makeSelection(QTextCursor.SelectionType.WordUnderCursor)

    clipboard = QApplication.clipboard()
    assert clipboard is not None
    clipboard.clear()

    # Cut
    assert docViewer.docAction(nwDocAction.CUT) is True
    assert clipboard.text() == "laoreet"
    clipboard.clear()

    # Copy
    assert docViewer.docAction(nwDocAction.COPY) is True
    assert clipboard.text() == "laoreet"
    clipboard.clear()

    # Select Paragraph
    assert docViewer.docAction(nwDocAction.SEL_PARA) is True
    cursor = docViewer.textCursor()
    assert cursor.selectedText() == (
        "Synopsis: Aenean ut placerat velit. Etiam laoreet ullamcorper risus, "
        "eget lobortis enim scelerisque non. Suspendisse id maximus nunc, et "
        "mollis sapien. Curabitur vel semper sapien, non pulvinar dolor. "
        "Etiam finibus nisi vel mi molestie consectetur."
    )
    cursor.clearSelection()
    docViewer.setTextCursor(cursor)

    docViewer._makePosSelection(
        QTextCursor.SelectionType.BlockUnderCursor, docViewer.cursorRect().center()
    )
    cursor = docViewer.textCursor()
    assert cursor.selectedText() == (
        "Synopsis: Aenean ut placerat velit. Etiam laoreet ullamcorper risus, "
        "eget lobortis enim scelerisque non. Suspendisse id maximus nunc, et "
        "mollis sapien. Curabitur vel semper sapien, non pulvinar dolor. "
        "Etiam finibus nisi vel mi molestie consectetur."
    )
    cursor.clearSelection()
    docViewer.setTextCursor(cursor)

    # Select All
    assert docViewer.docAction(nwDocAction.SEL_ALL) is True
    cursor = docViewer.textCursor()
    assert len(cursor.selectedText()) == 3060

    # Other actions
    assert docViewer.docAction(nwDocAction.NO_ACTION) is False

    # Close document
    docViewer.docHeader._closeDocument()
    assert docViewer.docHandle is None

    # Action on no document
    assert docViewer.docAction(nwDocAction.COPY) is False

    # Open again via menu
    nwGUI.projView.projTree.setSelectedHandle("88243afbe5ed8")
    nwGUI.mainMenu.aViewDoc.activate(QAction.ActionEvent.Trigger)

    # Open context menu
    menuOpened = False

    def mockExec(*a):
        nonlocal menuOpened
        menuOpened = True

    cursor = docViewer.textCursor()
    cursor.setPosition(27)
    docViewer.setTextCursor(cursor)
    docViewer._makeSelection(QTextCursor.SelectionType.WordUnderCursor)
    with monkeypatch.context() as mp:
        mp.setattr(QMenu, "exec", mockExec)
        docViewer._openContextMenu(docViewer.cursorRect().center())
        assert menuOpened

    # Select "Bod" link
    cursor = docViewer.textCursor()
    cursor.setPosition(27)
    docViewer.setTextCursor(cursor)
    docViewer._makeSelection(QTextCursor.SelectionType.WordUnderCursor)
    rect = docViewer.cursorRect()
    docViewer._linkClicked(QUrl("#tag_bod"))
    assert docViewer.docHandle == "4c4f28287af27"

    # Other links should just trigger a navigate call
    with qtbot.waitSignal(docViewer.sourceChanged, timeout=1000) as signal:
        docViewer._linkClicked(QUrl("#somewhere_else"))
        assert signal.args[0].url() == "#somewhere_else"

    # Web links should trigger the browser
    with monkeypatch.context() as mp:
        openUrl = MagicMock()
        mp.setattr(QDesktopServices, "openUrl", openUrl)
        docViewer._linkClicked(QUrl("http://www.example.com"))
        assert openUrl.called is True
        assert openUrl.call_args[0][0] == QUrl("http://www.example.com")

    # Click mouse nav buttons
    viewport = docViewer.viewport()
    qtbot.mouseClick(viewport, Qt.MouseButton.BackButton, pos=rect.center(), delay=100)
    assert docViewer.docHandle == "88243afbe5ed8"
    qtbot.mouseClick(viewport, Qt.MouseButton.ForwardButton, pos=rect.center(), delay=100)
    assert docViewer.docHandle == "4c4f28287af27"
    qtbot.mouseClick(viewport, QtMouseLeft, pos=rect.center(), delay=100)
    assert docViewer.docHandle == "4c4f28287af27"

    # Scroll bar default on empty document
    docViewer.clear()
    assert docViewer.scrollPosition == 0
    docViewer.reloadText()

    # Flip some settings
    CONFIG.doJustify = True
    CONFIG.hideVScroll = True
    CONFIG.hideHScroll = True
    docViewer.initViewer()
    assert docViewer.verticalScrollBar().isVisible() is False
    assert docViewer.horizontalScrollBar().isVisible() is False

    # Change document title
    nwItem = SHARED.project.tree["4c4f28287af27"]
    nwItem.setName("Test Title")  # type: ignore
    assert nwItem.itemName == "Test Title"  # type: ignore
    docViewer.onProjectItemChanged("4c4f28287af27", nwChange.UPDATE)
    assert docViewer.docHeader.itemTitle.text() == "Characters  \u203a  Test Title"

    # Title without full path
    CONFIG.showFullPath = False
    docViewer.onProjectItemChanged("4c4f28287af27", nwChange.UPDATE)
    assert docViewer.docHeader.itemTitle.text() == "Test Title"
    CONFIG.showFullPath = True

    # Document footer show/hide synopsis
    assert nwGUI.viewDocument("f96ec11c6a3da") is True
    assert len(docViewer.toPlainText()) == 4314
    docViewer.docFooter._doToggleSynopsis(False)
    assert len(docViewer.toPlainText()) == 4098

    # Document footer show/hide comments
    assert nwGUI.viewDocument("846352075de7d") is True
    assert len(docViewer.toPlainText()) == 683
    docViewer.docFooter._doToggleComments(False)
    assert len(docViewer.toPlainText()) == 634

    # Crash the HTML rendering
    with monkeypatch.context() as mp:
        mp.setattr(ToQTextDocument, "doConvert", causeException)
        assert docViewer.loadText("846352075de7d") is False
        assert docViewer.toPlainText() == "An error occurred while generating the preview."

    # Call the update theme function
    # This only checks that t doesn't fail, functionality tested elsewhere
    docViewer.updateTheme()

    # qtbot.stop()


@pytest.mark.gui
def testGuiViewer_DragAndDrop(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test drag and drop in the viewer."""
    docViewer = nwGUI.docViewer

    buildTestProject(nwGUI, projPath)
    assert nwGUI.openDocument(C.hTitlePage) is True
    assert nwGUI.viewDocument(C.hTitlePage) is True
    assert docViewer.docHandle == C.hTitlePage

    middle = docViewer.viewport().rect().center()
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
        mp.setattr(QTextBrowser, "dragEnterEvent", mockEnter)

        # Document Enter
        docViewer.dragEnterEvent(docEvent)
        assert docEvent.isAccepted() is True
        assert mockEnter.call_count == 0

        # Regular Enter
        docViewer.dragEnterEvent(noneEvent)
        assert mockEnter.call_count == 1

    # Drag Move
    mockMove = MagicMock()
    docEvent = QDragMoveEvent(middle, action, docMime, mouse, QtModNone)
    noneEvent = QDragMoveEvent(middle, action, noneMime, mouse, QtModNone)
    with monkeypatch.context() as mp:
        mp.setattr(QTextBrowser, "dragMoveEvent", mockMove)

        # Document Move
        docViewer.dragMoveEvent(docEvent)
        assert docEvent.isAccepted() is True
        assert mockMove.call_count == 0

        # Regular Move
        docViewer.dragMoveEvent(noneEvent)
        assert mockMove.call_count == 1

    # Drop
    mockDrop = MagicMock()
    middle = QPointF(docViewer.viewport().rect().center())
    docEvent = QDropEvent(middle, action, docMime, mouse, QtModNone)
    noneEvent = QDropEvent(middle, action, noneMime, mouse, QtModNone)
    with monkeypatch.context() as mp:
        mp.setattr(QTextBrowser, "dropEvent", mockDrop)

        # Document Drop
        docViewer.dropEvent(docEvent)
        assert mockDrop.call_count == 0
        assert docViewer.docHandle == C.hSceneDoc

        # Regular Move
        docViewer.dropEvent(noneEvent)
        assert mockDrop.call_count == 1
