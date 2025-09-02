"""
novelWriter – Main GUI Novel Tree Class Tester
==============================================

This file is a part of novelWriter
Copyright (C) 2021 Veronica Berglyd Olsen and novelWriter contributors

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

from pathlib import Path

import pytest

from PyQt6.QtCore import QModelIndex, QPoint, Qt
from PyQt6.QtWidgets import QInputDialog, QToolTip

from novelwriter import CONFIG, SHARED
from novelwriter.core.novelmodel import NovelModel
from novelwriter.dialogs.editlabel import GuiEditLabel
from novelwriter.enum import nwFocus, nwItemType, nwNovelExtra, nwView

from tests.tools import C, buildTestProject


@pytest.mark.gui
def testGuiNovelView_Content(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test navigating the novel tree."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    buildTestProject(nwGUI, projPath)

    nwGUI._switchFocus(nwFocus.TREE)
    nwGUI.projView.projTree.clearSelection()
    nwGUI.projView.projTree.setSelectedHandle(C.hCharRoot)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE)

    contentPath = SHARED.project.storage.contentPath
    assert isinstance(contentPath, Path)
    cHandle = "0000000000010"

    (contentPath / f"{cHandle}.nwd").write_text(
        "# Jane Doe\n\n@tag: Jane\n\n", encoding="utf-8"
    )
    (contentPath / f"{C.hSceneDoc}.nwd").write_text((
        "### Scene One\n\n"
        "@pov: Jane\n"
        "@focus: Jane\n\n"
        "% Synopsis: This is a scene.\n\n"
        "This is some text in the edited scene."
    ), encoding="utf-8")

    novelView = nwGUI.novelView
    novelTree = nwGUI.novelView.novelTree
    novelBar  = nwGUI.novelView.novelBar

    # Show/Hide Scrollbars
    # ====================

    CONFIG.hideVScroll = True
    CONFIG.hideHScroll = True
    novelView.initSettings()
    assert not novelTree.verticalScrollBar().isVisible()
    assert not novelTree.horizontalScrollBar().isVisible()

    CONFIG.hideVScroll = False
    CONFIG.hideHScroll = False
    novelView.initSettings()
    assert novelTree.verticalScrollBar().isEnabled()
    assert novelTree.horizontalScrollBar().isEnabled()

    # Populate Tree
    # =============
    root = QModelIndex()

    novelView.setTreeFocus()
    nwGUI._changeView(nwView.NOVEL)

    # Clear tree
    novelView.setCurrentNovel(None)
    assert novelTree._getModel() is None

    # Reload
    novelView.refreshCurrentTree()
    model = novelTree._getModel()
    assert isinstance(model, NovelModel)

    # Check the items
    assert model.rowCount(root) == 3
    assert model.columnCount(root) == 3
    assert model.data(model.createIndex(2, 1), Qt.ItemDataRole.DisplayRole) == "2"  # Word Count

    nwGUI.rebuildIndex()  # This should update the word count to the edited scene
    assert model.data(model.createIndex(2, 1), Qt.ItemDataRole.DisplayRole) == "10"  # Word Count

    # Extra Column
    # ============
    novelBar.setLastColType(nwNovelExtra.POV)
    assert model.rowCount(root) == 3
    assert model.columnCount(root) == 4

    # Scene column should contain the POV character
    assert model.data(model.createIndex(2, 2), Qt.ItemDataRole.DisplayRole) == "Jane"

    # Resize the last column
    assert novelTree.lastColSize == 25
    with monkeypatch.context() as mp:
        mp.setattr(QInputDialog, "getInt", lambda *a, **k: (40, True))
        novelBar._selectLastColumnSize()
    assert novelTree.lastColSize == 40

    # Open Items
    # ==========

    # Clear selection
    novelTree.clearSelection()
    assert novelView.getSelectedHandle() == (None, None)

    # Select scene
    novelTree.setCurrentIndex(model.createIndex(2, 0))
    assert novelView.getSelectedHandle() == (C.hSceneDoc, "T0001")

    # Double-click item
    novelTree._onDoubleClick(model.createIndex(2, 0))
    assert nwGUI.docEditor.docHandle == C.hSceneDoc

    # Middle-click item
    novelTree._onMiddleClick(model.createIndex(2, 0))
    assert nwGUI.docViewer.docHandle == C.hSceneDoc

    # Item Meta
    # =========

    toolTip = ""

    def showText(pos, text):
        nonlocal toolTip
        toolTip = text

    with monkeypatch.context() as mp:
        mp.setattr(QToolTip, "showText", showText)

        toolTip = ""
        novelTree._onSingleClick(model.createIndex(2, 3))
        assert toolTip == (
            "<p><b>Point of View:</b> Jane<br><b>Focus:</b> Jane</p>"
            "<p><b>Synopsis:</b> This is a scene.</p>"
        )

        toolTip = ""
        novelTree._popMetaBox(QPoint(1, 1), C.hInvalid, "T0001")
        assert toolTip == ""

    # Active Status
    # =============
    assert novelBar._refresh == {C.hNovelRoot: False}

    # Add a document while tree in focus
    nwGUI._changeView(nwView.PROJECT)
    assert novelBar._active is False
    nwGUI.projView.projTree.setSelectedHandle(C.hChapterDir)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE, hLevel=3)
    assert novelBar._refresh == {C.hNovelRoot: True}

    # Switch back and check that the refresh status is reset
    nwGUI._changeView(nwView.NOVEL)
    assert novelBar._refresh == {C.hNovelRoot: False}

    # Close
    # qtbot.stop()
    nwGUI.closeProject()
