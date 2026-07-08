"""
novelWriter – Main GUI Project Search Tester
============================================

This file is a part of novelWriter
Copyright (C) 2024 Veronica Berglyd Olsen and novelWriter contributors

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

from time import time

import pytest

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from novelwriter.enum import nwChange, nwDocMode, nwView
from novelwriter.gui.search import GuiProjectSearch
from novelwriter.types import QtKeyDown, QtKeyReturn, QtKeyRight, QtKeyUp


@pytest.mark.gui
def testGuiProjectSearch_Main(qtbot, monkeypatch, nwGUI, prjLipsum):
    """Test navigating the novel tree."""
    nwGUI.openProject(prjLipsum)
    nwGUI._changeView(nwView.SEARCH)
    search = nwGUI.projSearch

    def totalCount():
        res = search.searchResult
        return sum(
            int(res.topLevelItem(i).text(GuiProjectSearch.C_COUNT).strip("()")) for i in range(res.topLevelItemCount())
        )

    # Plain search
    search.searchText.setText("Lorem")
    search.searchAction.activate(QAction.ActionEvent.Trigger)
    assert search.searchResult.topLevelItemCount() == 14
    assert totalCount() == 43

    firstDoc = search.searchResult.topLevelItem(0)
    firstResult = firstDoc.child(0)
    assert firstDoc is not None
    handle = firstDoc.data(GuiProjectSearch.C_RESULT, GuiProjectSearch.D_HANDLE)
    result = firstResult.data(GuiProjectSearch.C_RESULT, GuiProjectSearch.D_RESULT)
    assert result == (handle, 3, 5)

    # Move down
    search.searchText.setFocus()
    qtbot.keyClick(search, QtKeyDown)
    assert firstDoc.isSelected() is True

    # Move up
    qtbot.keyClick(search, QtKeyUp)
    assert firstDoc.isSelected() is False

    # Move right does nothing
    qtbot.keyClick(search, QtKeyRight)
    assert firstDoc.isSelected() is False

    # Selecting updates details
    firstDoc.setSelected(True)
    assert nwGUI.itemDetails._handle == handle

    # Other change types for the selected item are ignored
    nwGUI.itemDetails.onProjectItemChanged(handle, nwChange.CREATE)

    # Press return
    search.searchResult.setFocus()
    search.searchResult.clearSelection()
    firstResult.setSelected(True)
    with monkeypatch.context() as mp:
        mp.setattr(search.searchResult, "hasFocus", lambda *a: True)
        with qtbot.waitSignal(search.openDocumentSelectRequest, timeout=1000) as signal:
            qtbot.keyClick(search, QtKeyReturn)
            assert signal.args == [handle, 3, 5, False]
        with qtbot.waitSignal(search.openDocumentRequest, timeout=1000) as signal:
            qtbot.keyClick(search, QtKeyReturn, Qt.KeyboardModifier.ShiftModifier)
            assert signal.args == [handle, nwDocMode.VIEW, "", True]

    assert nwGUI.docEditor.docHandle == handle
    assert nwGUI.docEditor.textCursor().selectedText() == "Lorem"

    # Double-click
    with qtbot.waitSignal(search.openDocumentSelectRequest, timeout=1000) as signal:
        search._searchResultDoubleClicked(firstResult, 0)
        assert signal.args == [handle, 3, 5, True]

    # Double-click on a document-level entry does nothing
    with qtbot.assertNotEmitted(search.openDocumentSelectRequest):
        search._searchResultDoubleClicked(firstDoc, 0)

    # Press return with no selection does nothing
    search.searchResult.clearSelection()
    with monkeypatch.context() as mp:
        mp.setattr(search.searchResult, "hasFocus", lambda *a: True)
        with qtbot.assertNotEmitted(search.openDocumentSelectRequest):
            qtbot.keyClick(search, QtKeyReturn)

    # Case Sensitive
    search.toggleCase.setChecked(True)
    search.searchAction.activate(QAction.ActionEvent.Trigger)
    assert search.searchResult.topLevelItemCount() == 7
    assert totalCount() == 18
    search.toggleCase.setChecked(False)

    # Whole Words
    search.searchText.setText("dolor")
    with monkeypatch.context() as mp:
        mp.setattr(search.searchText, "hasFocus", lambda *a: True)
        qtbot.keyClick(search, QtKeyReturn)

    assert search.searchResult.topLevelItemCount() == 10
    assert totalCount() == 34

    search.toggleWord.setChecked(True)
    search.searchAction.activate(QAction.ActionEvent.Trigger)
    assert search.searchResult.topLevelItemCount() == 10
    assert totalCount() == 33

    # RegEx
    search.toggleRegEx.setChecked(True)
    search.beginSearch("(dolor|dolorem)")
    search.searchAction.activate(QAction.ActionEvent.Trigger)
    assert search.searchResult.topLevelItemCount() == 10
    assert totalCount() == 34

    # Re-run search should not change the result
    search.textChanged(handle, time() + 1000.0)
    assert search.searchResult.topLevelItemCount() == 10
    assert totalCount() == 34

    # A re-entrant search call is a no-op
    search._blocked = True
    search._processSearch()
    assert search.searchResult.topLevelItemCount() == 10
    search._blocked = False

    # An empty search text clears the result without searching
    search.searchText.setText("")
    search.searchAction.activate(QAction.ActionEvent.Trigger)
    assert search.searchResult.topLevelItemCount() == 0

    # Refresh with no prior search does nothing
    search.refreshCurrentSearch()
    assert search.searchResult.topLevelItemCount() == 0

    # qtbot.stop()
    nwGUI.closeProject()
