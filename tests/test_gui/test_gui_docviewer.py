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

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import qApp, QAction

from novelwriter import CONFIG
from novelwriter.enum import nwDocAction
from novelwriter.core.tohtml import ToHtml


@pytest.mark.gui
def testGuiViewer_Main(qtbot, monkeypatch, nwGUI, prjLipsum):
    """Test the document viewer."""
    # Open project
    assert nwGUI.openProject(prjLipsum)

    # Rebuild the index
    nwGUI.mainMenu.aRebuildIndex.activate(QAction.Trigger)
    assert nwGUI.project.index._tagsIndex._tags != {}
    assert nwGUI.project.index._itemIndex._items != {}

    # Select a document in the project tree
    nwGUI.projView.setSelectedHandle("88243afbe5ed8")

    # Middle-click the selected item
    theItem = nwGUI.projView.projTree._getTreeItem("88243afbe5ed8")
    theRect = nwGUI.projView.projTree.visualItemRect(theItem)
    qtbot.mouseClick(nwGUI.projView.projTree.viewport(), Qt.MidButton, pos=theRect.center())
    assert nwGUI.docViewer.docHandle() == "88243afbe5ed8"

    # Reload the text
    origText = nwGUI.docViewer.toPlainText()
    nwGUI.docViewer.setPlainText("Oops, all gone!")
    nwGUI.docViewer.docHeader._refreshDocument()
    assert nwGUI.docViewer.toPlainText() == origText

    # Select word
    theCursor = nwGUI.docViewer.textCursor()
    theCursor.setPosition(100)
    nwGUI.docViewer.setTextCursor(theCursor)
    nwGUI.docViewer._makeSelection(QTextCursor.WordUnderCursor)

    qClip = qApp.clipboard()
    qClip.clear()

    # Cut
    assert nwGUI.docViewer.docAction(nwDocAction.CUT) is True
    assert qClip.text() == "laoreet"
    qClip.clear()

    # Copy
    assert nwGUI.docViewer.docAction(nwDocAction.COPY) is True
    assert qClip.text() == "laoreet"
    qClip.clear()

    # Select Paragraph
    assert nwGUI.docViewer.docAction(nwDocAction.SEL_PARA) is True
    theCursor = nwGUI.docViewer.textCursor()
    assert theCursor.selectedText() == (
        "Synopsis: Aenean ut placerat velit. Etiam laoreet ullamcorper risus, "
        "eget lobortis enim scelerisque non. Suspendisse id maximus nunc, et "
        "mollis sapien. Curabitur vel semper sapien, non pulvinar dolor. "
        "Etiam finibus nisi vel mi molestie consectetur."
    )

    # Select All
    assert nwGUI.docViewer.docAction(nwDocAction.SEL_ALL) is True
    theCursor = nwGUI.docViewer.textCursor()
    assert len(theCursor.selectedText()) == 3061

    # Other actions
    assert nwGUI.docViewer.docAction(nwDocAction.NO_ACTION) is False

    # Close document
    nwGUI.docViewer.docHeader._closeDocument()
    assert nwGUI.docViewer.docHandle() is None

    # Action on no document
    assert nwGUI.docViewer.docAction(nwDocAction.COPY) is False

    # Open again via menu
    assert nwGUI.projView.setSelectedHandle("88243afbe5ed8")
    nwGUI.mainMenu.aViewDoc.activate(QAction.Trigger)

    # Select "Bod" link
    theCursor = nwGUI.docViewer.textCursor()
    theCursor.setPosition(27)
    nwGUI.docViewer.setTextCursor(theCursor)
    nwGUI.docViewer._makeSelection(QTextCursor.WordUnderCursor)
    theRect = nwGUI.docViewer.cursorRect()
    # qtbot.mouseClick(nwGUI.docViewer.viewport(), Qt.LeftButton, pos=theRect.center(), delay=100)
    nwGUI.docViewer._linkClicked(QUrl("#char=Bod"))
    assert nwGUI.docViewer.docHandle() == "4c4f28287af27"

    # Click mouse nav buttons
    qtbot.mouseClick(nwGUI.docViewer.viewport(), Qt.BackButton, pos=theRect.center(), delay=100)
    assert nwGUI.docViewer.docHandle() == "88243afbe5ed8"
    qtbot.mouseClick(nwGUI.docViewer.viewport(), Qt.ForwardButton, pos=theRect.center(), delay=100)
    assert nwGUI.docViewer.docHandle() == "4c4f28287af27"

    # Scroll bar default on empty document
    nwGUI.docViewer.clear()
    assert nwGUI.docViewer.getScrollPosition() == 0
    nwGUI.docViewer.reloadText()

    # Change document title
    nwItem = nwGUI.project.tree["4c4f28287af27"]
    nwItem.setName("Test Title")
    assert nwItem.itemName == "Test Title"
    nwGUI.docViewer.updateDocInfo("4c4f28287af27")
    assert nwGUI.docViewer.docHeader.theTitle.text() == "Characters  ›  Test Title"

    # Title without full path
    CONFIG.showFullPath = False
    nwGUI.docViewer.updateDocInfo("4c4f28287af27")
    assert nwGUI.docViewer.docHeader.theTitle.text() == "Test Title"
    CONFIG.showFullPath = True

    # Document footer show/hide references
    viewState = nwGUI.viewMeta.isVisible()
    nwGUI.docViewer.docFooter._doShowHide()
    assert nwGUI.viewMeta.isVisible() is not viewState
    nwGUI.docViewer.docFooter._doShowHide()
    assert nwGUI.viewMeta.isVisible() is viewState

    # Document footer sticky
    viewState = nwGUI.docViewer.stickyRef
    nwGUI.docViewer.docFooter._doToggleSticky(not viewState)
    assert nwGUI.docViewer.stickyRef is not viewState
    nwGUI.docViewer.docFooter._doToggleSticky(viewState)
    assert nwGUI.docViewer.stickyRef is viewState

    # Document footer show/hide synopsis
    assert nwGUI.viewDocument("f96ec11c6a3da") is True
    assert len(nwGUI.docViewer.toPlainText()) == 4315
    nwGUI.docViewer.docFooter._doToggleSynopsis(False)
    assert len(nwGUI.docViewer.toPlainText()) == 4099

    # Document footer show/hide comments
    assert nwGUI.viewDocument("846352075de7d") is True
    assert len(nwGUI.docViewer.toPlainText()) == 675
    nwGUI.docViewer.docFooter._doToggleComments(False)
    assert len(nwGUI.docViewer.toPlainText()) == 635

    # Crash the HTML rendering
    with monkeypatch.context() as mp:
        mp.setattr(ToHtml, "doConvert", causeException)
        assert nwGUI.docViewer.loadText("846352075de7d") is False
        assert nwGUI.docViewer.toPlainText() == "An error occurred while generating the preview."

    # Check reference panel (issue #1378)
    assert nwGUI.viewDocument("4c4f28287af27") is True
    assert nwGUI.docViewer.toPlainText().startswith("Nobody Owens")

    nwGUI.viewMeta._linkClicked("fb609cd8319dc")
    assert nwGUI.docViewer.toPlainText().startswith("Chapter One")

    nwGUI.viewMeta._linkClicked("88243afbe5ed8#T0001")
    assert nwGUI.docViewer.toPlainText().startswith("Scene One")

    nwGUI.viewMeta._linkClicked("88243afbe5ed8#ABCD")
    assert nwGUI.docViewer.toPlainText().startswith("Scene One")

    # qtbot.stop()

# END Test testGuiViewer_Main
