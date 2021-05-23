# -*- coding: utf-8 -*-
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

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QAction, QMessageBox

from nw.gui.doceditor import GuiDocEditor
from nw.enum import nwDocAction

keyDelay = 2
typeDelay = 1
stepDelay = 20

@pytest.mark.gui
def testGuiEditor_Search(qtbot, monkeypatch, nwGUI, nwLipsum):
    """Test the document editor search functionality.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.Yes)
    monkeypatch.setattr(GuiDocEditor, "hasFocus", lambda *args: True)

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
    assert nwGUI.docEditor.getCursorPosition() < 3 # No result

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
    assert nwGUI.docEditor.docHandle() == "2426c6f0ca922" # Next document
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
