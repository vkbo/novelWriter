# -*- coding: utf-8 -*-
"""
novelWriter – Main GUI Viewer Class Tester
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

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import qApp, QAction, QMessageBox

from nw.enum import nwDocAction

keyDelay = 2
typeDelay = 1
stepDelay = 20

@pytest.mark.gui
def testGuiViewer_Main(qtbot, monkeypatch, nwGUI, nwLipsum):
    """Test the document viewer.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *args: QMessageBox.Yes)

    # Open project
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.openProject(nwLipsum)

    # Rebuild the index as it isn't automatically copied
    assert nwGUI.theIndex._tagIndex == {}
    assert nwGUI.theIndex._refIndex == {}
    nwGUI.mainMenu.aRebuildIndex.activate(QAction.Trigger)
    assert nwGUI.theIndex._tagIndex != {}
    assert nwGUI.theIndex._refIndex != {}

    # Select a document in the project tree
    assert nwGUI.treeView.setSelectedHandle("88243afbe5ed8")

    # Middle-click the selected item
    theItem = nwGUI.treeView._getTreeItem("88243afbe5ed8")
    theRect = nwGUI.treeView.visualItemRect(theItem)
    qtbot.mouseClick(nwGUI.treeView.viewport(), Qt.MidButton, pos=theRect.center())
    assert nwGUI.docViewer.theHandle == "88243afbe5ed8"

    # Reload the text
    origText = nwGUI.docViewer.toPlainText()
    nwGUI.docViewer.setPlainText("Oops, all gone!")
    nwGUI.docViewer.docHeader._refreshDocument()
    assert nwGUI.docViewer.toPlainText() == origText

    # Cursor line
    assert not nwGUI.docViewer.setCursorLine("not a number")
    assert nwGUI.docViewer.setCursorLine(3)
    theCursor = nwGUI.docViewer.textCursor()
    assert theCursor.position() == 40

    # Cursor position
    assert not nwGUI.docViewer.setCursorPosition("not a number")
    assert nwGUI.docViewer.setCursorPosition(100)

    # Select word
    nwGUI.docViewer._makeSelection(QTextCursor.WordUnderCursor)

    qClip = qApp.clipboard()
    qClip.clear()

    # Cut
    assert nwGUI.docViewer.docAction(nwDocAction.CUT)
    assert qClip.text() == "laoreet"
    qClip.clear()

    # Copy
    assert nwGUI.docViewer.docAction(nwDocAction.COPY)
    assert qClip.text() == "laoreet"
    qClip.clear()

    # Select Paragraph
    assert nwGUI.docViewer.docAction(nwDocAction.SEL_PARA)
    theCursor = nwGUI.docViewer.textCursor()
    assert theCursor.selectedText() == (
        "Synopsis: Aenean ut placerat velit. Etiam laoreet ullamcorper risus, "
        "eget lobortis enim scelerisque non. Suspendisse id maximus nunc, et "
        "mollis sapien. Curabitur vel semper sapien, non pulvinar dolor. "
        "Etiam finibus nisi vel mi molestie consectetur."
    )

    # Select All
    assert nwGUI.docViewer.docAction(nwDocAction.SEL_ALL)
    theCursor = nwGUI.docViewer.textCursor()
    assert len(theCursor.selectedText()) == 3061

    # Other actions
    assert not nwGUI.docViewer.docAction(nwDocAction.NO_ACTION)

    # Close document
    nwGUI.docViewer.docHeader._closeDocument()
    assert nwGUI.docViewer.theHandle is None

    # Action on no document
    assert not nwGUI.docViewer.docAction(nwDocAction.COPY)

    # Open again via menu
    assert nwGUI.treeView.setSelectedHandle("88243afbe5ed8")
    nwGUI.mainMenu.aViewDoc.activate(QAction.Trigger)

    # Select "Bod" link
    assert nwGUI.docViewer.setCursorPosition(27)
    nwGUI.docViewer._makeSelection(QTextCursor.WordUnderCursor)
    theRect = nwGUI.docViewer.cursorRect()
    # qtbot.mouseClick(nwGUI.docViewer.viewport(), Qt.LeftButton, pos=theRect.center(), delay=100)
    nwGUI.docViewer._linkClicked(QUrl("#char=Bod"))
    assert nwGUI.docViewer.theHandle == "4c4f28287af27"

    # Click mouse nav buttons
    qtbot.mouseClick(nwGUI.docViewer.viewport(), Qt.BackButton, pos=theRect.center(), delay=100)
    assert nwGUI.docViewer.theHandle == "88243afbe5ed8"
    qtbot.mouseClick(nwGUI.docViewer.viewport(), Qt.ForwardButton, pos=theRect.center(), delay=100)
    assert nwGUI.docViewer.theHandle == "4c4f28287af27"

    # Scroll bar default on empty document
    nwGUI.docViewer.clear()
    assert nwGUI.docViewer.getScrollPosition() == 0
    nwGUI.docViewer.reloadText()

    # Change document title
    nwItem = nwGUI.theProject.projTree["4c4f28287af27"]
    nwItem.setName("Test Title")
    assert nwItem.itemName == "Test Title"
    nwGUI.docViewer.updateDocInfo("4c4f28287af27")
    assert nwGUI.docViewer.docHeader.theTitle.text() == "Characters  ›  Test Title"

    # Ttile without full path
    nwGUI.mainConf.showFullPath = False
    nwGUI.docViewer.updateDocInfo("4c4f28287af27")
    assert nwGUI.docViewer.docHeader.theTitle.text() == "Test Title"
    nwGUI.mainConf.showFullPath = True

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
    assert nwGUI.viewDocument("f96ec11c6a3da")
    assert len(nwGUI.docViewer.toPlainText()) == 4315
    nwGUI.docViewer.docFooter._doToggleSynopsis(False)
    assert len(nwGUI.docViewer.toPlainText()) == 4099

    # Document footer show/hide comments
    assert nwGUI.viewDocument("846352075de7d")
    assert len(nwGUI.docViewer.toPlainText()) == 675
    nwGUI.docViewer.docFooter._doToggleComments(False)
    assert len(nwGUI.docViewer.toPlainText()) == 635

    # qtbot.stopForInteraction()

# END Test testGuiViewer_Main
