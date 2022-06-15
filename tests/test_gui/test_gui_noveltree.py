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

from tools import buildTestProject, writeFile

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

from novelwriter.enum import nwWidget, nwItemType
from novelwriter.dialogs import GuiEditLabel
from novelwriter.gui.noveltree import NovelTreeColumn


@pytest.mark.gui
def testGuiNovelTree_TreeItems(qtbot, monkeypatch, nwGUI, fncProj, mockRnd):
    """Test navigating the novel tree.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    buildTestProject(nwGUI, fncProj)

    nwGUI.switchFocus(nwWidget.TREE)
    nwGUI.projView.projTree.clearSelection()
    nwGUI.projView.projTree._getTreeItem("000000000000a").setSelected(True)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE)

    writeFile(
        os.path.join(nwGUI.theProject.projContent, "0000000000010.nwd"),
        "# Jane Doe\n\n@tag: Jane\n\n"
    )
    writeFile(
        os.path.join(nwGUI.theProject.projContent, "000000000000f.nwd"),
        "### Scene One\n\n@pov: Jane\n@focus: Jane\n\n"
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
    assert novelView.getSelectedHandle() == ("000000000000c", 0)

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
    assert nwGUI.docEditor.docHandle() == "000000000000f"

    # Open item with middle mouse button
    scItem.setSelected(True)
    assert scItem.isSelected()
    assert nwGUI.docViewer.docHandle() is None
    qtbot.mouseClick(vPort, Qt.MiddleButton, pos=vPort.rect().center(), delay=10)
    assert nwGUI.docViewer.docHandle() is None

    scRect = novelTree.visualItemRect(scItem)
    oldData = scItem.data(novelTree.C_TITLE, Qt.UserRole)
    scItem.setData(novelTree.C_TITLE, Qt.UserRole, (None, "", ""))
    qtbot.mouseClick(vPort, Qt.MiddleButton, pos=scRect.center(), delay=10)
    assert nwGUI.docViewer.docHandle() is None

    scItem.setData(novelTree.C_TITLE, Qt.UserRole, oldData)
    qtbot.mouseClick(vPort, Qt.MiddleButton, pos=scRect.center(), delay=10)
    assert nwGUI.docViewer.docHandle() == "000000000000f"

    # Last Column
    # ===========

    novelBar.setLastColType(NovelTreeColumn.HIDDEN)
    assert novelTree.isColumnHidden(novelTree.C_EXTRA) is True
    assert novelTree.lastColType == NovelTreeColumn.HIDDEN
    assert novelTree._getLastColumnText("000000000000f", "T000001") == ("", "")

    novelBar.setLastColType(NovelTreeColumn.POV)
    assert novelTree.isColumnHidden(novelTree.C_EXTRA) is False
    assert novelTree.lastColType == NovelTreeColumn.POV
    assert novelTree._getLastColumnText("000000000000f", "T000001") == (
        "Jane", "Point of View: Jane"
    )

    novelBar.setLastColType(NovelTreeColumn.FOCUS)
    assert novelTree.isColumnHidden(novelTree.C_EXTRA) is False
    assert novelTree.lastColType == NovelTreeColumn.FOCUS
    assert novelTree._getLastColumnText("000000000000f", "T000001") == (
        "Jane", "Focus: Jane"
    )

    novelBar.setLastColType(NovelTreeColumn.PLOT)
    assert novelTree.isColumnHidden(novelTree.C_EXTRA) is False
    assert novelTree.lastColType == NovelTreeColumn.PLOT
    assert novelTree._getLastColumnText("000000000000f", "T000001") == (
        "", "Plot: "
    )

    novelTree._lastCol = None
    assert novelTree._getLastColumnText("0000000000000", "T000000") == ("", "")

    # Close
    # =====

    # qtbot.stop()
    nwGUI.closeProject()

# END Test testGuiNovelTree_TreeItems
