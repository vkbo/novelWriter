"""
novelWriter – Main GUI Outline Class Tester
===========================================

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

import time
import pytest

from tools import buildTestProject, writeFile

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QAction

from novelwriter import CONFIG
from novelwriter.enum import nwItemClass, nwOutline, nwView


@pytest.mark.gui
def testGuiOutline_Main(qtbot, monkeypatch, nwGUI, projPath):
    """Test the outline view.
    """
    # Create a project
    buildTestProject(nwGUI, projPath)

    nwGUI.rebuildIndex()
    nwGUI._changeView(nwView.OUTLINE)

    outlineView = nwGUI.outlineView
    outlineTree = outlineView.outlineTree
    outlineData = outlineView.outlineData
    outlineMenu = outlineView.outlineBar.mColumns

    # Toggle scrollbars
    CONFIG.hideVScroll = True
    CONFIG.hideHScroll = True
    outlineView.initSettings()
    assert outlineTree.verticalScrollBarPolicy() == Qt.ScrollBarAlwaysOff
    assert outlineTree.horizontalScrollBarPolicy() == Qt.ScrollBarAlwaysOff
    assert outlineData.verticalScrollBarPolicy() == Qt.ScrollBarAlwaysOff
    assert outlineData.horizontalScrollBarPolicy() == Qt.ScrollBarAlwaysOff

    CONFIG.hideVScroll = False
    CONFIG.hideHScroll = False
    outlineView.initSettings()
    assert outlineTree.verticalScrollBarPolicy() == Qt.ScrollBarAsNeeded
    assert outlineTree.horizontalScrollBarPolicy() == Qt.ScrollBarAsNeeded
    assert outlineData.verticalScrollBarPolicy() == Qt.ScrollBarAsNeeded
    assert outlineData.horizontalScrollBarPolicy() == Qt.ScrollBarAsNeeded

    # Check focus
    with monkeypatch.context() as mp:
        mp.setattr(QWidget, "hasFocus", lambda *a: True)
        assert outlineView.treeHasFocus() is True

    outlineView.setTreeFocus()  # Can't check. just ensures that it doesn't error

    # Option State
    # ============
    pOptions = nwGUI.theProject.options
    colNames = [h.name for h in nwOutline]
    colItems = [h for h in nwOutline]
    colWidth = {h: outlineTree.DEF_WIDTH[h] for h in nwOutline}
    colHidden = {h: outlineTree.DEF_HIDDEN[h] for h in nwOutline}

    assert outlineTree.topLevelItemCount() > 0

    # Save header state not allowed
    outlineTree._lastBuild = 0
    outlineTree._saveHeaderState()
    assert pOptions.getValue("GuiOutline", "headerOrder", []) == []

    # Allow saving header state
    outlineTree._lastBuild = time.time()
    outlineTree._saveHeaderState()
    assert pOptions.getValue("GuiOutline", "headerOrder", []) == colNames
    assert outlineTree._treeOrder == colItems
    assert outlineTree._colWidth == colWidth
    assert outlineTree._colHidden == colHidden

    # Get default values
    optItems = pOptions.getValue("GuiOutline", "headerOrder", [])
    optWidth = pOptions.getValue("GuiOutline", "columnWidth", {})
    optHidden = pOptions.getValue("GuiOutline", "columnHidden", {})

    # Add invalid column name
    pOptions.setValue("GuiOutline", "headerOrder", optItems + ["blabla"])
    outlineTree._loadHeaderState()
    assert outlineTree._treeOrder == colItems
    assert outlineTree._colHidden == colHidden

    # Add duplicate column name
    pOptions.setValue("GuiOutline", "headerOrder", optItems + [optItems[-1]])
    outlineTree._loadHeaderState()
    assert outlineTree._treeOrder == colItems
    assert outlineTree._colHidden == colHidden

    # Invalid column width data
    pOptions.setValue("GuiOutline", "headerOrder", optItems)
    pOptions.setValue("GuiOutline", "columnWidth", {"blabla": None})
    outlineTree._loadHeaderState()
    assert outlineTree._treeOrder == colItems
    assert outlineTree._colHidden == colHidden

    # Invalid column width data
    pOptions.setValue("GuiOutline", "headerOrder", optItems)
    pOptions.setValue("GuiOutline", "columnWidth", optWidth)
    pOptions.setValue("GuiOutline", "columnHidden", {"bloabla": None})
    outlineTree._loadHeaderState()
    assert outlineTree._treeOrder == colItems
    assert outlineTree._colHidden == colHidden

    # Valid settings
    pOptions.setValue("GuiOutline", "headerOrder", optItems)
    pOptions.setValue("GuiOutline", "columnWidth", optWidth)
    pOptions.setValue("GuiOutline", "columnHidden", optHidden)
    outlineTree._loadHeaderState()
    assert outlineTree._treeOrder == colItems
    assert outlineTree._colHidden == colHidden

    # Header Menu
    # ===========

    # Trigger the menu entry for all hidden columns
    for hItem in nwOutline:
        if outlineTree.DEF_HIDDEN[hItem]:
            outlineMenu.actionMap[hItem].activate(QAction.Trigger)

    # Now no columns should be hidden
    outlineTree._saveHeaderState()
    assert not any(pOptions.getValue("GuiOutline", "columnHidden", None).values())

    # qtbot.stop()

# END Test testGuiOutline_Main


@pytest.mark.gui
def testGuiOutline_Content(qtbot, nwGUI, prjLipsum):
    """Test the outline view.
    """
    assert nwGUI.openProject(prjLipsum)

    nwGUI.rebuildIndex()
    nwGUI._changeView(nwView.OUTLINE)

    outlineView = nwGUI.outlineView
    outlineBar  = outlineView.outlineBar
    outlineTree = outlineView.outlineTree
    outlineData = outlineView.outlineData

    lipHandle = "b3643d0f92e32"

    # Check defaults in dropdown list
    assert outlineBar.novelValue.itemData(0) == lipHandle
    assert outlineBar.novelValue.itemData(1) is None  # Separator
    assert outlineBar.novelValue.itemData(2) == ""    # All novels

    # Add a second novel folder
    newHandle = nwGUI.theProject.newRoot(nwItemClass.NOVEL)
    nwGUI.projView.projTree.revealNewTreeItem(newHandle)

    # Check new values in dropdown list
    assert outlineBar.novelValue.itemData(0) == lipHandle
    assert outlineBar.novelValue.itemData(1) == newHandle
    assert outlineBar.novelValue.itemData(2) is None  # Separator
    assert outlineBar.novelValue.itemData(3) == ""    # All novels

    # Add a bunch of files in a header order that hits all tree combos
    docList = [
        ("Section 1", 4), ("Scene 1", 3), ("Chapter 1", 2), ("Part 1", 1),
        ("Section 2", 4), ("Scene 2", 3), ("Chapter 2", 2),
        ("Section 3", 4), ("Scene 3", 3),
        ("Section 4", 4),
    ]
    for dTitle, hLevel in docList:
        aHandle = nwGUI.theProject.newFile(dTitle, newHandle)
        hHash = "#"*hLevel
        writeFile(prjLipsum / "content" / f"{aHandle}.nwd", f"{hHash} {dTitle}\n\n")
        nwGUI.projView.projTree.revealNewTreeItem(aHandle)

    nwGUI.rebuildIndex()

    # Build the second novel
    outlineBar.novelValue.setCurrentIndex(1)
    outlineBar._refreshRequested()

    # Go back to Lipsum
    outlineBar.novelValue.setCurrentIndex(0)
    outlineBar._refreshRequested()

    # Check Details
    # =============

    # First Item
    outlineTree.refreshTree()
    selItem = outlineTree.topLevelItem(0)

    outlineTree.setCurrentItem(selItem)
    assert outlineData.titleLabel.text() == "<b>Title</b>"
    assert outlineData.titleValue.text() == "Lorem Ipsum"
    assert outlineData.fileValue.text() == "Lorem Ipsum"
    assert outlineData.itemValue.text() == "Finished"

    assert outlineData.cCValue.text() == "230"
    assert outlineData.wCValue.text() == "40"
    assert outlineData.pCValue.text() == "3"

    # Scene One
    selItem = outlineTree.topLevelItem(4)

    outlineTree.setCurrentItem(selItem)
    tHandle, sTitle = outlineTree.getSelectedHandle()
    assert tHandle == "88243afbe5ed8"
    assert sTitle == "T0001"

    assert outlineData.titleLabel.text() == "<b>Scene</b>"
    assert outlineData.titleValue.text() == "Scene One"
    assert outlineData.fileValue.text() == "Scene One"
    assert outlineData.itemValue.text() == "Finished"

    # Click POV Link
    assert outlineData.povKeyValue.text() == "<a href='Bod'>Bod</a>"
    outlineView._tagClicked("Bod")
    assert nwGUI.docViewer.docHandle() == "4c4f28287af27"

    # Scene One, Section Two
    selItem = outlineTree.topLevelItem(5)

    outlineTree.setCurrentItem(selItem)
    tHandle, sTitle = outlineTree.getSelectedHandle()
    assert tHandle == "88243afbe5ed8"
    assert sTitle == "T0002"

    assert outlineData.titleLabel.text() == "<b>Section</b>"
    assert outlineData.titleValue.text() == "Scene One, Section Two"
    assert outlineData.fileValue.text() == "Scene One"
    assert outlineData.itemValue.text() == "Finished"

    outlineTree._treeDoubleClick(selItem, 0)
    assert nwGUI.docEditor.docHandle() == "88243afbe5ed8"

    # qtbot.stop()

# END Test testGuiOutline_Content
