"""
novelWriter – Main GUI Novel Tree Class Tester
==============================================

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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

import os
import pytest

from tools import C, buildTestProject, writeFile

from PyQt5.QtGui import QFocusEvent
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QToolTip

from novelwriter.enum import nwWidget, nwItemType
from novelwriter.gui.noveltree import NovelTreeColumn
from novelwriter.dialogs.editlabel import GuiEditLabel


@pytest.mark.gui
def testGuiNovelTree_TreeItems(qtbot, monkeypatch, nwGUI, fncProj, mockRnd):
    """Test navigating the novel tree.
    """
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    buildTestProject(nwGUI, fncProj)

    nwGUI.switchFocus(nwWidget.TREE)
    nwGUI.projView.projTree.clearSelection()
    nwGUI.projView.projTree._getTreeItem(C.hCharRoot).setSelected(True)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE)

    writeFile(
        os.path.join(nwGUI.theProject.projContent, "0000000000010.nwd"),
        "# Jane Doe\n\n@tag: Jane\n\n"
    )
    writeFile(
        os.path.join(nwGUI.theProject.projContent, "000000000000f.nwd"), (
            "### Scene One\n\n"
            "@pov: Jane\n"
            "@focus: Jane\n\n"
            "% Synopsis: This is a scene."
        )
    )

    novelView = nwGUI.novelView
    novelTree = novelView.novelTree
    novelBar  = novelView.novelBar

    # Show/Hide Scrollbars
    # ====================

    nwGUI.mainConf.hideVScroll = True
    nwGUI.mainConf.hideHScroll = True
    novelView.initSettings()
    assert not novelTree.verticalScrollBar().isVisible()
    assert not novelTree.horizontalScrollBar().isVisible()

    nwGUI.mainConf.hideVScroll = False
    nwGUI.mainConf.hideHScroll = False
    novelView.initSettings()
    assert novelTree.verticalScrollBar().isEnabled()
    assert novelTree.horizontalScrollBar().isEnabled()

    # Populate Tree
    # =============

    nwGUI.projStack.setCurrentIndex(nwGUI.idxNovelView)
    nwGUI.rebuildIndex()
    novelTree._populateTree(rootHandle=None)
    assert novelTree.topLevelItemCount() == 3

    # Rebuild should preserve selection
    topItem = novelTree.topLevelItem(0)
    assert not topItem.isSelected()
    topItem.setSelected(True)
    assert novelTree.selectedItems()[0] == topItem
    assert novelView.getSelectedHandle() == (C.hTitlePage, 0)

    # Refresh using the slot for the butoom
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
    qtbot.mouseClick(vPort, Qt.LeftButton, pos=vPort.rect().center(), delay=10)
    assert not scItem.isSelected()

    # Double-click item
    scItem.setSelected(True)
    assert scItem.isSelected()
    assert nwGUI.docEditor.docHandle() is None
    novelTree._treeDoubleClick(scItem, 0)
    assert nwGUI.docEditor.docHandle() == C.hSceneDoc

    # Open item with middle mouse button
    scItem.setSelected(True)
    assert scItem.isSelected()
    assert nwGUI.docViewer.docHandle() is None
    qtbot.mouseClick(vPort, Qt.MiddleButton, pos=vPort.rect().center(), delay=10)
    assert nwGUI.docViewer.docHandle() is None

    scRect = novelTree.visualItemRect(scItem)
    oldData = scItem.data(novelTree.C_TITLE, novelTree.D_HANDLE)
    scItem.setData(novelTree.C_TITLE, novelTree.D_HANDLE, None)
    qtbot.mouseClick(vPort, Qt.MiddleButton, pos=scRect.center(), delay=10)
    assert nwGUI.docViewer.docHandle() is None

    scItem.setData(novelTree.C_TITLE, novelTree.D_HANDLE, oldData)
    qtbot.mouseClick(vPort, Qt.MiddleButton, pos=scRect.center(), delay=10)
    assert nwGUI.docViewer.docHandle() == C.hSceneDoc

    # Last Column
    # ===========

    novelBar.setLastColType(NovelTreeColumn.HIDDEN)
    assert novelTree.isColumnHidden(novelTree.C_EXTRA) is True
    assert novelTree.lastColType == NovelTreeColumn.HIDDEN
    assert novelTree._getLastColumnText(C.hSceneDoc, "T000001") == ("", "")

    novelBar.setLastColType(NovelTreeColumn.POV)
    assert novelTree.isColumnHidden(novelTree.C_EXTRA) is False
    assert novelTree.lastColType == NovelTreeColumn.POV
    assert novelTree._getLastColumnText(C.hSceneDoc, "T000001") == (
        "Jane", "Point of View: Jane"
    )

    novelBar.setLastColType(NovelTreeColumn.FOCUS)
    assert novelTree.isColumnHidden(novelTree.C_EXTRA) is False
    assert novelTree.lastColType == NovelTreeColumn.FOCUS
    assert novelTree._getLastColumnText(C.hSceneDoc, "T000001") == (
        "Jane", "Focus: Jane"
    )

    novelBar.setLastColType(NovelTreeColumn.PLOT)
    assert novelTree.isColumnHidden(novelTree.C_EXTRA) is False
    assert novelTree.lastColType == NovelTreeColumn.PLOT
    assert novelTree._getLastColumnText(C.hSceneDoc, "T000001") == (
        "", "Plot: "
    )

    novelTree._lastCol = None
    assert novelTree._getLastColumnText("0000000000000", "T000000") == ("", "")

    # Item Meta
    # =========

    ttText = ""

    def showText(pos, text):
        nonlocal ttText
        ttText = text

    mIndex = novelTree.model().index(2, novelTree.C_MORE)
    with monkeypatch.context() as mp:
        mp.setattr(QToolTip, "showText", showText)
        novelTree._treeItemClicked(mIndex)
        assert ttText == (
            "<p><b>Point of View</b>: Jane<br><b>Focus</b>: Jane</p>"
            "<p><b>Synopsis</b>: This is a scene.</p>"
        )

    # Other Checks
    # ============

    scItem = novelTree.topLevelItem(2)
    scItem.setSelected(True)
    assert scItem.isSelected()
    novelTree.focusOutEvent(QFocusEvent(QEvent.None_, Qt.MouseFocusReason))
    assert not scItem.isSelected()

    # Close
    # =====

    # qtbot.stop()
    nwGUI.closeProject()

# END Test testGuiNovelTree_TreeItems
