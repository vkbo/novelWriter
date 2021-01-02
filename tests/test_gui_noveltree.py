# -*- coding: utf-8 -*-
"""novelWriter Main GUI Project Tree Class Tester
"""

import pytest
import os

from tools import writeFile

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

@pytest.mark.gui
def testGuiNovelTree_TreeItems(qtbot, caplog, monkeypatch, nwGUI, nwMinimal):
    """Test navigating the novel tree.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *args: QMessageBox.Yes)

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

    # The tree should be empty as there is no index
    assert nwTree.topLevelItemCount() == 0

    nwGUI.rebuildIndex()
    nwTree._populateTree()
    assert nwTree.topLevelItemCount() == 1

    # Rebuild should preserve selection
    topItem = nwTree.topLevelItem(0)
    assert not topItem.isSelected()
    topItem.setSelected(True)
    assert nwTree.selectedItems()[0] == topItem
    assert nwTree.getSelectedHandle() == "a35baf2e93843"

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
    assert nwGUI.docEditor.theHandle is None
    nwTree._treeDoubleClick(scItem, 0)
    assert nwGUI.docEditor.theHandle == "8c659a11cd429"

    # Open item with middle mouse button
    scItem.setSelected(True)
    assert scItem.isSelected()
    assert nwGUI.docViewer.theHandle is None
    qtbot.mouseClick(vPort, Qt.MiddleButton, pos=vPort.rect().center(), delay=10)
    assert nwGUI.docViewer.theHandle is None

    scRect = nwTree.visualItemRect(scItem)
    oldData = scItem.data(nwTree.C_TITLE, Qt.UserRole)
    scItem.setData(nwTree.C_TITLE, Qt.UserRole, (None, "", ""))
    qtbot.mouseClick(vPort, Qt.MiddleButton, pos=scRect.center(), delay=10)
    assert nwGUI.docViewer.theHandle is None

    scItem.setData(nwTree.C_TITLE, Qt.UserRole, oldData)
    qtbot.mouseClick(vPort, Qt.MiddleButton, pos=scRect.center(), delay=10)
    assert nwGUI.docViewer.theHandle == "8c659a11cd429"

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

    qtbot.stopForInteraction()
    nwGUI.closeProject()

# END Test testGuiNovelTree_TreeItems
