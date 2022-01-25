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

import pytest
import os

from tools import writeFile

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox


@pytest.mark.gui
def testGuiNovelTree_TreeItems(qtbot, monkeypatch, nwGUI, nwMinimal):
    """Test navigating the novel tree.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Yes)

    nwGUI.openProject(nwMinimal)
    nwGUI.theProject.projTree.setSeed(42)
    nwTree = nwGUI.novelView

    ##
    #  Show/Hide Scrollbars
    ##

    nwTree.mainConf.hideVScroll = True
    nwTree.mainConf.hideHScroll = True
    nwTree.initTree()
    assert not nwTree.verticalScrollBar().isVisible()
    assert not nwTree.horizontalScrollBar().isVisible()

    nwTree.mainConf.hideVScroll = False
    nwTree.mainConf.hideHScroll = False
    nwTree.initTree()
    assert nwTree.verticalScrollBar().isEnabled()
    assert nwTree.horizontalScrollBar().isEnabled()

    ##
    #  Populate Tree
    ##

    nwGUI.projTabs.setCurrentIndex(nwGUI.idxNovelView)
    nwGUI.rebuildIndex()
    nwTree._populateTree()
    assert nwTree.topLevelItemCount() == 1

    # Rebuild should preserve selection
    topItem = nwTree.topLevelItem(0)
    assert not topItem.isSelected()
    topItem.setSelected(True)
    assert nwTree.selectedItems()[0] == topItem
    assert nwTree.getSelectedHandle() == ("a35baf2e93843", 0)

    nwTree.refreshTree()
    assert nwTree.topLevelItem(0).isSelected()

    ##
    #  Open Items
    ##

    # Clear selection
    nwTree.clearSelection()
    scItem = nwTree.topLevelItem(0).child(0).child(0)
    scItem.setSelected(True)
    assert scItem.isSelected()

    # Clear selection with mouse
    vPort = nwTree.viewport()
    qtbot.mouseClick(vPort, Qt.LeftButton, pos=vPort.rect().center(), delay=10)
    assert not scItem.isSelected()

    # Double-click item
    scItem.setSelected(True)
    assert scItem.isSelected()
    assert nwGUI.docEditor.docHandle() is None
    nwTree._treeDoubleClick(scItem, 0)
    assert nwGUI.docEditor.docHandle() == "8c659a11cd429"

    # Open item with middle mouse button
    scItem.setSelected(True)
    assert scItem.isSelected()
    assert nwGUI.docViewer.docHandle() is None
    qtbot.mouseClick(vPort, Qt.MiddleButton, pos=vPort.rect().center(), delay=10)
    assert nwGUI.docViewer.docHandle() is None

    scRect = nwTree.visualItemRect(scItem)
    oldData = scItem.data(nwTree.C_TITLE, Qt.UserRole)
    scItem.setData(nwTree.C_TITLE, Qt.UserRole, (None, "", ""))
    qtbot.mouseClick(vPort, Qt.MiddleButton, pos=scRect.center(), delay=10)
    assert nwGUI.docViewer.docHandle() is None

    scItem.setData(nwTree.C_TITLE, Qt.UserRole, oldData)
    qtbot.mouseClick(vPort, Qt.MiddleButton, pos=scRect.center(), delay=10)
    assert nwGUI.docViewer.docHandle() == "8c659a11cd429"

    ##
    #  Populate Tree
    ##

    # Add weird titles to first file to check hnadling of non-standard
    # order of title levels.
    writeFile(os.path.join(nwMinimal, "content", "a35baf2e93843.nwd"), (
        "#### Section wo/Scene\n\n"
        "### Scene wo/Chapter\n\n"
        "## Chapter wo/Title\n\n"
        "# Title\n\n"
        "#### Section w/Title, wo/Scene\n\n"
        "### Scene w/Title, wo/Chapter\n\n"
        "## Chapter\n\n"
        "#### Section w/Chapter, wo/Scene\n\n"
        "### Scene\n\n"
        "#### Section\n\n"
    ))
    nwGUI.rebuildIndex()
    nwTree._populateTree()
    assert nwTree.topLevelItem(0).text(nwTree.C_TITLE) == "Section wo/Scene"
    assert nwTree.topLevelItem(1).text(nwTree.C_TITLE) == "Scene wo/Chapter"
    assert nwTree.topLevelItem(2).text(nwTree.C_TITLE) == "Chapter wo/Title"
    assert nwTree.topLevelItem(3).text(nwTree.C_TITLE) == "Title"

    tTitle = nwTree.topLevelItem(3)
    assert tTitle.child(0).text(nwTree.C_TITLE) == "Section w/Title, wo/Scene"
    assert tTitle.child(1).text(nwTree.C_TITLE) == "Scene w/Title, wo/Chapter"
    assert tTitle.child(2).text(nwTree.C_TITLE) == "Chapter"

    tChap = tTitle.child(2)
    assert tChap.child(0).text(nwTree.C_TITLE) == "Section w/Chapter, wo/Scene"
    assert tChap.child(1).text(nwTree.C_TITLE) == "Scene"

    tScene = tChap.child(1)
    assert tScene.child(0).text(nwTree.C_TITLE) == "Section"

    ##
    #  Close
    ##

    # qtbot.stopForInteraction()
    nwGUI.closeProject()

# END Test testGuiNovelTree_TreeItems
