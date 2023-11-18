"""
novelWriter – Main GUI Viewer Class Tester
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

from mocked import causeException

from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QMenu, qApp, QAction

from novelwriter import CONFIG, SHARED
from novelwriter.enum import nwDocAction
from novelwriter.core.tohtml import ToHtml
from novelwriter.gui.docviewer import GuiDocViewer


@pytest.mark.gui
def testGuiViewer_Main(qtbot, monkeypatch, nwGUI, prjLipsum):
    """Test the document viewer."""
    # Open project
    assert nwGUI.openProject(prjLipsum)
    docViewer: GuiDocViewer = nwGUI.docViewer

    # Select a document in the project tree
    nwGUI.projView.setSelectedHandle("88243afbe5ed8")
    nwGUI.openDocument("88243afbe5ed8")

    # Can only open a document
    assert docViewer.loadText("b3643d0f92e32") is False

    # Middle-click the selected item
    item = nwGUI.projView.projTree._getTreeItem("88243afbe5ed8")
    rect = nwGUI.projView.projTree.visualItemRect(item)
    qtbot.mouseClick(nwGUI.projView.projTree.viewport(), Qt.MidButton, pos=rect.center())
    assert docViewer.docHandle == "88243afbe5ed8"

    # Clear selection
    nwGUI.projView.projTree.clearSelection()
    assert nwGUI.projView.projTree.getSelectedHandle() is None

    # Re-select via header click
    docViewer.docHeader.mousePressEvent(None)  # type: ignore
    assert nwGUI.projView.projTree.getSelectedHandle() == "88243afbe5ed8"

    # Reload the text
    origText = docViewer.toPlainText()
    docViewer.setPlainText("Oops, all gone!")
    docViewer.docHeader._refreshDocument()
    assert docViewer.toPlainText() == origText

    # Select word
    cursor = docViewer.textCursor()
    cursor.setPosition(100)
    docViewer.setTextCursor(cursor)
    docViewer._makeSelection(QTextCursor.WordUnderCursor)

    qClip = qApp.clipboard()
    qClip.clear()

    # Cut
    assert docViewer.docAction(nwDocAction.CUT) is True
    assert qClip.text() == "laoreet"
    qClip.clear()

    # Copy
    assert docViewer.docAction(nwDocAction.COPY) is True
    assert qClip.text() == "laoreet"
    qClip.clear()

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
    assert len(cursor.selectedText()) == 3061

    # Other actions
    assert docViewer.docAction(nwDocAction.NO_ACTION) is False

    # Close document
    docViewer.docHeader._closeDocument()
    assert docViewer.docHandle is None

    # Action on no document
    assert docViewer.docAction(nwDocAction.COPY) is False

    # Open again via menu
    assert nwGUI.projView.setSelectedHandle("88243afbe5ed8")
    nwGUI.mainMenu.aViewDoc.activate(QAction.Trigger)

    # Open context menu
    menuOpened = False

    def mockExec(*a):
        nonlocal menuOpened
        menuOpened = True

    cursor = docViewer.textCursor()
    cursor.setPosition(27)
    docViewer.setTextCursor(cursor)
    docViewer._makeSelection(QTextCursor.WordUnderCursor)
    with monkeypatch.context() as mp:
        mp.setattr(QMenu, "exec_", mockExec)
        docViewer._openContextMenu(docViewer.cursorRect().center())
        assert menuOpened

    # Select "Bod" link
    cursor = docViewer.textCursor()
    cursor.setPosition(27)
    docViewer.setTextCursor(cursor)
    docViewer._makeSelection(QTextCursor.WordUnderCursor)
    rect = docViewer.cursorRect()
    docViewer._linkClicked(QUrl("#char=Bod"))
    assert docViewer.docHandle == "4c4f28287af27"

    # Click mouse nav buttons
    qtbot.mouseClick(docViewer.viewport(), Qt.BackButton, pos=rect.center(), delay=100)
    assert docViewer.docHandle == "88243afbe5ed8"
    qtbot.mouseClick(docViewer.viewport(), Qt.ForwardButton, pos=rect.center(), delay=100)
    assert docViewer.docHandle == "4c4f28287af27"
    qtbot.mouseClick(docViewer.viewport(), Qt.LeftButton, pos=rect.center(), delay=100)
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
    docViewer.updateDocInfo("4c4f28287af27")
    assert docViewer.docHeader.docTitle.text() == "Characters  \u203a  Test Title"

    # Title without full path
    CONFIG.showFullPath = False
    docViewer.updateDocInfo("4c4f28287af27")
    assert docViewer.docHeader.docTitle.text() == "Test Title"
    CONFIG.showFullPath = True

    # Document footer show/hide synopsis
    assert nwGUI.viewDocument("f96ec11c6a3da") is True
    assert len(docViewer.toPlainText()) == 4315
    docViewer.docFooter._doToggleSynopsis(False)
    assert len(docViewer.toPlainText()) == 4099

    # Document footer show/hide comments
    assert nwGUI.viewDocument("846352075de7d") is True
    assert len(docViewer.toPlainText()) == 675
    docViewer.docFooter._doToggleComments(False)
    assert len(docViewer.toPlainText()) == 635

    # Crash the HTML rendering
    with monkeypatch.context() as mp:
        mp.setattr(ToHtml, "doConvert", causeException)
        assert docViewer.loadText("846352075de7d") is False
        assert docViewer.toPlainText() == "An error occurred while generating the preview."

    # Call the update theme function
    # This only checks that t doesn't fail, functionality tested elsewhere
    docViewer.updateTheme()

    # qtbot.stop()

# END Test testGuiViewer_Main
