"""
novelWriter – Main GUI Project Search Tester
============================================

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

import pytest

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction

from novelwriter.enum import nwView
from novelwriter.gui.search import GuiProjectSearch


@pytest.mark.gui
def testGuiDocSearch_Main(qtbot, monkeypatch, nwGUI, prjLipsum):
    """Test navigating the novel tree."""
    nwGUI.openProject(prjLipsum)
    nwGUI._changeView(nwView.SEARCH)
    search = nwGUI.projSearch

    def totalCount():
        nonlocal search
        res = search.searchResult
        return sum(
            int(res.topLevelItem(i).text(GuiProjectSearch.C_COUNT).strip("()"))
            for i in range(res.topLevelItemCount())
        )

    # Plain search
    search.searchText.setText("Lorem")
    search.searchAction.activate(QAction.ActionEvent.Trigger)
    assert search.searchResult.topLevelItemCount() == 14
    assert totalCount() == 42

    firstDoc = search.searchResult.topLevelItem(0)
    firstResult = firstDoc.child(0)
    assert firstDoc is not None
    handle = firstDoc.data(GuiProjectSearch.C_RESULT, GuiProjectSearch.D_HANDLE)
    result = firstResult.data(GuiProjectSearch.C_RESULT, GuiProjectSearch.D_RESULT)
    assert result == (handle, 3, 5)

    # Move down
    qtbot.keyClick(search, Qt.Key.Key_Down)
    assert firstDoc.isSelected() is True

    # Move up
    qtbot.keyClick(search, Qt.Key.Key_Up)
    assert firstDoc.isSelected() is False

    # Move right does nothing
    qtbot.keyClick(search, Qt.Key.Key_Right)
    assert firstDoc.isSelected() is False

    # Selecting updates details
    firstDoc.setSelected(True)
    assert nwGUI.itemDetails._handle == handle

    # Press return
    search.searchResult.setFocus()
    search.searchResult.clearSelection()
    firstResult.setSelected(True)
    with monkeypatch.context() as mp:
        mp.setattr(search.searchResult, "hasFocus", lambda *a: True)
        with qtbot.waitSignal(search.openDocumentSelectRequest, timeout=1000) as signal:
            qtbot.keyClick(search, Qt.Key.Key_Return)
            assert signal.args == [handle, 3, 5, False]

    assert nwGUI.docEditor.docHandle == handle
    assert nwGUI.docEditor.textCursor().selectedText() == "Lorem"

    # Double-click
    with qtbot.waitSignal(search.openDocumentSelectRequest, timeout=1000) as signal:
        search._searchResultDoubleClicked(firstResult, 0)
        assert signal.args == [handle, 3, 5, True]

    # Case Sensitive
    search.toggleCase.setChecked(True)
    search.searchAction.activate(QAction.ActionEvent.Trigger)
    assert search.searchResult.topLevelItemCount() == 7
    assert totalCount() == 17
    search.toggleCase.setChecked(False)

    # Whole Words
    search.searchText.setText("dolor")
    with monkeypatch.context() as mp:
        mp.setattr(search.searchText, "hasFocus", lambda *a: True)
        qtbot.keyClick(search, Qt.Key.Key_Return)

    assert search.searchResult.topLevelItemCount() == 10
    assert totalCount() == 34

    search.toggleWord.setChecked(True)
    search.searchAction.activate(QAction.ActionEvent.Trigger)
    assert search.searchResult.topLevelItemCount() == 10
    assert totalCount() == 33

    # RegEx
    search.toggleRegEx.setChecked(True)
    search.searchText.setText("(dolor|dolorem)")
    search.searchAction.activate(QAction.ActionEvent.Trigger)
    assert search.searchResult.topLevelItemCount() == 10
    assert totalCount() == 34

    # qtbot.stop()
    nwGUI.closeProject()

# END Test testGuiDocSearch_Main
