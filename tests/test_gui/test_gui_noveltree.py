"""
novelWriter – Main GUI Novel Tree Class Tester
==============================================

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

from pathlib import Path

import pytest

from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtGui import QFocusEvent
from PyQt5.QtWidgets import QInputDialog, QToolTip

from novelwriter import CONFIG, SHARED
from novelwriter.dialogs.editlabel import GuiEditLabel
from novelwriter.enum import nwFocus, nwItemType
from novelwriter.gui.noveltree import GuiNovelTree, NovelTreeColumn
from novelwriter.types import QtMouseLeft

from tests.tools import C, buildTestProject


@pytest.mark.gui
def testGuiNovelTree_TreeItems(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test navigating the novel tree."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    buildTestProject(nwGUI, projPath)

    nwGUI._switchFocus(nwFocus.TREE)
    nwGUI.projView.projTree.clearSelection()
    nwGUI.projView.projTree._getTreeItem(C.hCharRoot).setSelected(True)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE)

    contentPath = SHARED.project.storage.contentPath
    assert isinstance(contentPath, Path)

    (contentPath / "0000000000010.nwd").write_text(
        "# Jane Doe\n\n@tag: Jane\n\n", encoding="utf-8"
    )
    (contentPath / "000000000000f.nwd").write_text((
        "### Scene One\n\n"
        "@pov: Jane\n"
        "@focus: Jane\n\n"
        "% Synopsis: This is a scene."
    ), encoding="utf-8")

    novelView = nwGUI.novelView
    novelTree = novelView.novelTree
    novelBar  = novelView.novelBar

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

    novelView.setTreeFocus()

    nwGUI.projStack.setCurrentWidget(nwGUI.novelView)
    nwGUI.rebuildIndex()
    novelTree._populateTree(rootHandle=None)
    assert novelTree.topLevelItemCount() == 3

    # Rebuild should preserve selection
    topItem = novelTree.topLevelItem(0)
    assert not topItem.isSelected()
    topItem.setSelected(True)
    assert novelTree.selectedItems()[0] == topItem
    assert novelView.getSelectedHandle() == (C.hTitlePage, "T0001")

    # Refresh using the slot for the button
    novelBar._refreshNovelTree()
    assert novelTree.topLevelItem(0).isSelected()

    # Open Items
    # ==========

    # Clear selection
    novelTree.clearSelection()
    scItem = novelTree.topLevelItem(2)
    scItem.setSelected(True)
    assert scItem.isSelected()

    # Clear selection with mouse
    vPort = novelTree.viewport()
    qtbot.mouseClick(vPort, QtMouseLeft, pos=vPort.rect().center(), delay=10)
    assert not scItem.isSelected()

    # Double-click item
    scItem.setSelected(True)
    assert scItem.isSelected()
    assert nwGUI.docEditor.docHandle is None
    novelTree._treeDoubleClick(scItem, 0)
    assert nwGUI.docEditor.docHandle == C.hSceneDoc

    # Open item with middle mouse button
    scItem.setSelected(True)
    assert scItem.isSelected()
    assert nwGUI.docViewer.docHandle is None
    qtbot.mouseClick(vPort, Qt.MiddleButton, pos=vPort.rect().center(), delay=10)
    assert nwGUI.docViewer.docHandle is None

    scRect = novelTree.visualItemRect(scItem)
    oldData = scItem.data(novelTree.C_TITLE, novelTree.D_HANDLE)
    scItem.setData(novelTree.C_TITLE, novelTree.D_HANDLE, None)
    qtbot.mouseClick(vPort, Qt.MiddleButton, pos=scRect.center(), delay=10)
    assert nwGUI.docViewer.docHandle is None

    scItem.setData(novelTree.C_TITLE, novelTree.D_HANDLE, oldData)
    qtbot.mouseClick(vPort, Qt.MiddleButton, pos=scRect.center(), delay=10)
    assert nwGUI.docViewer.docHandle == C.hSceneDoc

    # Last Column
    # ===========

    novelBar.setLastColType(NovelTreeColumn.HIDDEN)
    assert novelTree.isColumnHidden(novelTree.C_EXTRA) is True
    assert novelTree.lastColType == NovelTreeColumn.HIDDEN
    assert novelTree._getLastColumnText(C.hSceneDoc, "T0001") == ("", "")

    novelBar.setLastColType(NovelTreeColumn.PLOT)
    assert novelTree.isColumnHidden(novelTree.C_EXTRA) is False
    assert novelTree.lastColType == NovelTreeColumn.PLOT
    assert novelTree._getLastColumnText(C.hSceneDoc, "T0001") == (
        "", ""
    )

    novelBar.setLastColType(NovelTreeColumn.FOCUS)
    assert novelTree.isColumnHidden(novelTree.C_EXTRA) is False
    assert novelTree.lastColType == NovelTreeColumn.FOCUS
    assert novelTree._getLastColumnText(C.hSceneDoc, "T0001") == (
        "Jane", "Focus: Jane"
    )

    novelBar.setLastColType(NovelTreeColumn.POV)
    assert novelTree.isColumnHidden(novelTree.C_EXTRA) is False
    assert novelTree.lastColType == NovelTreeColumn.POV
    assert novelTree._getLastColumnText(C.hSceneDoc, "T0001") == (
        "Jane", "Point of View: Jane"
    )

    novelTree._lastCol = None
    assert novelTree._getLastColumnText("0000000000000", "T0000") == ("", "")

    # This forces the resizeEvent function to process labels
    spSize = nwGUI.splitMain.sizes()
    nwGUI.splitMain.setSizes([spSize[0] + 10, spSize[1] - 10])

    # Resize the last column
    with monkeypatch.context() as mp:
        mp.setattr(QInputDialog, "getInt", lambda *a, **k: (40, True))
        novelBar._selectLastColumnSize()

    # Item Meta
    # =========

    ttText = ""

    def showText(pos, text):
        nonlocal ttText
        ttText = text

    mIndex = novelTree.model().index(2, novelTree.C_MORE)
    with monkeypatch.context() as mp:
        mp.setattr(QToolTip, "showText", showText)

        ttText = ""
        novelTree._treeItemClicked(mIndex)
        assert ttText == (
            "<p><b>Point of View</b>: Jane<br><b>Focus</b>: Jane</p>"
            "<p><b>Synopsis</b>: This is a scene.</p>"
        )

        ttText = ""
        novelTree._popMetaBox(QPoint(1, 1), C.hInvalid, "T0001")
        assert ttText == ""

    # Set Default Root
    # ================
    SHARED.project.data.setLastHandle(C.hInvalid, "novelTree")
    novelView.openProjectTasks()
    assert novelBar.novelValue.handle == C.hNovelRoot

    # Tree Focus
    # ==========
    with monkeypatch.context() as mp:
        mp.setattr(GuiNovelTree, "hasFocus", lambda *a: False)
        assert novelView.treeHasFocus() is False
        mp.setattr(GuiNovelTree, "hasFocus", lambda *a: True)
        assert novelView.treeHasFocus() is True

    # Other Checks
    # ============

    scItem = novelTree.topLevelItem(2)
    scItem.setSelected(True)
    assert scItem.isSelected()
    novelTree.focusOutEvent(QFocusEvent(QEvent.Type.None_, Qt.MouseFocusReason))
    assert not scItem.isSelected()

    # Close
    # =====

    # qtbot.stop()
    nwGUI.closeProject()
