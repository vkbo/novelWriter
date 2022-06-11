"""
novelWriter – Main GUI Outline Class Tester
===========================================

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
import time
import pytest

from tools import buildTestProject, writeFile

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QMessageBox, QAction

from novelwriter.enum import nwItemClass, nwOutline, nwView


@pytest.mark.gui
def testGuiOutline_Main(qtbot, monkeypatch, nwGUI, fncDir):
    """Test the outline view.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Yes)

    # Create a project
    prjDir = os.path.join(fncDir, "project")
    buildTestProject(nwGUI, prjDir)

    nwGUI.rebuildIndex()
    nwGUI._changeView(nwView.OUTLINE)

    outlineMain = nwGUI.outlineView
    outlineView = outlineMain.outlineView
    outlineData = outlineMain.outlineData
    outlineMenu = outlineMain.outlineBar.mColumns

    # Toggle scrollbars
    nwGUI.mainConf.hideVScroll = True
    nwGUI.mainConf.hideHScroll = True
    outlineMain.initOutline()
    assert outlineView.verticalScrollBarPolicy() == Qt.ScrollBarAlwaysOff
    assert outlineView.horizontalScrollBarPolicy() == Qt.ScrollBarAlwaysOff
    assert outlineData.verticalScrollBarPolicy() == Qt.ScrollBarAlwaysOff
    assert outlineData.horizontalScrollBarPolicy() == Qt.ScrollBarAlwaysOff

    nwGUI.mainConf.hideVScroll = False
    nwGUI.mainConf.hideHScroll = False
    outlineMain.initOutline()
    assert outlineView.verticalScrollBarPolicy() == Qt.ScrollBarAsNeeded
    assert outlineView.horizontalScrollBarPolicy() == Qt.ScrollBarAsNeeded
    assert outlineData.verticalScrollBarPolicy() == Qt.ScrollBarAsNeeded
    assert outlineData.horizontalScrollBarPolicy() == Qt.ScrollBarAsNeeded

    # Check focus
    with monkeypatch.context() as mp:
        mp.setattr(QWidget, "hasFocus", lambda *a: True)
        assert outlineMain.treeFocus() is True

    outlineMain.setTreeFocus()  # Can't check. just ensures that it doesn't error

    # Option State
    # ============
    pOptions = nwGUI.theProject.options
    colNames = [h.name for h in nwOutline]
    colItems = [h for h in nwOutline]
    colWidth = {h: outlineView.DEF_WIDTH[h] for h in nwOutline}
    colHidden = {h: outlineView.DEF_HIDDEN[h] for h in nwOutline}

    assert outlineView.topLevelItemCount() > 0

    # Save header state not allowed
    outlineView._lastBuild = 0
    outlineView._saveHeaderState()
    assert pOptions.getValue("GuiOutline", "headerOrder", []) == []

    # Allow saving header state
    outlineView._lastBuild = time.time()
    outlineView._saveHeaderState()
    assert pOptions.getValue("GuiOutline", "headerOrder", []) == colNames
    assert outlineView._treeOrder == colItems
    assert outlineView._colWidth == colWidth
    assert outlineView._colHidden == colHidden

    # Get default values
    optItems = pOptions.getValue("GuiOutline", "headerOrder", [])
    optWidth = pOptions.getValue("GuiOutline", "columnWidth", {})
    optHidden = pOptions.getValue("GuiOutline", "columnHidden", {})

    # Add invalid column name
    pOptions.setValue("GuiOutline", "headerOrder", optItems + ["blabla"])
    outlineView._loadHeaderState()
    assert outlineView._treeOrder == colItems
    assert outlineView._colHidden == colHidden

    # Add duplicate column name
    pOptions.setValue("GuiOutline", "headerOrder", optItems + [optItems[-1]])
    outlineView._loadHeaderState()
    assert outlineView._treeOrder == colItems
    assert outlineView._colHidden == colHidden

    # Invalid column width data
    pOptions.setValue("GuiOutline", "headerOrder", optItems)
    pOptions.setValue("GuiOutline", "columnWidth", {"blabla": None})
    outlineView._loadHeaderState()
    assert outlineView._treeOrder == colItems
    assert outlineView._colHidden == colHidden

    # Invalid column width data
    pOptions.setValue("GuiOutline", "headerOrder", optItems)
    pOptions.setValue("GuiOutline", "columnWidth", optWidth)
    pOptions.setValue("GuiOutline", "columnHidden", {"bloabla": None})
    outlineView._loadHeaderState()
    assert outlineView._treeOrder == colItems
    assert outlineView._colHidden == colHidden

    # Valid settings
    pOptions.setValue("GuiOutline", "headerOrder", optItems)
    pOptions.setValue("GuiOutline", "columnWidth", optWidth)
    pOptions.setValue("GuiOutline", "columnHidden", optHidden)
    outlineView._loadHeaderState()
    assert outlineView._treeOrder == colItems
    assert outlineView._colHidden == colHidden

    # Header Menu
    # ===========

    # Trigger the menu entry for all hidden columns
    for hItem in nwOutline:
        if outlineView.DEF_HIDDEN[hItem]:
            outlineMenu.actionMap[hItem].activate(QAction.Trigger)

    # Now no columns should be hidden
    outlineView._saveHeaderState()
    assert not any(pOptions.getValue("GuiOutline", "columnHidden", None).values())

    # qtbot.stop()

# END Test testGuiOutline_Main


@pytest.mark.gui
def testGuiOutline_Content(qtbot, monkeypatch, nwGUI, nwLipsum):
    """Test the outline view.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Yes)

    assert nwGUI.openProject(nwLipsum)
    nwGUI.mainConf.lastPath = nwLipsum

    nwGUI.rebuildIndex()
    nwGUI._changeView(nwView.OUTLINE)

    outlineMain = nwGUI.outlineView
    outlineBar  = outlineMain.outlineBar
    outlineView = outlineMain.outlineView
    outlineData = outlineMain.outlineData

    lipHandle = "b3643d0f92e32"

    # Check defaults in dropdown list
    assert outlineBar.novelValue.itemData(0) == lipHandle
    assert outlineBar.novelValue.itemData(1) is None  # Separator
    assert outlineBar.novelValue.itemData(2) == ""    # All novels

    # Add a second novel folder
    newHandle = nwGUI.theProject.newRoot(nwItemClass.NOVEL)
    nwGUI.projView.revealNewTreeItem(newHandle)

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
        writeFile(os.path.join(nwLipsum, "content", f"{aHandle}.nwd"), f"{hHash} {dTitle}\n\n")
        nwGUI.projView.revealNewTreeItem(aHandle)

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
    outlineView.refreshTree()
    selItem = outlineView.topLevelItem(0)

    outlineView.setCurrentItem(selItem)
    assert outlineData.titleLabel.text() == "<b>Title</b>"
    assert outlineData.titleValue.text() == "Lorem Ipsum"
    assert outlineData.fileValue.text() == "Lorem Ipsum"
    assert outlineData.itemValue.text() == "Finished"

    assert outlineData.cCValue.text() == "230"
    assert outlineData.wCValue.text() == "40"
    assert outlineData.pCValue.text() == "3"

    # Scene One
    actItem = outlineView.topLevelItem(1)
    chpItem = actItem.child(0)
    selItem = chpItem.child(0)

    outlineView.setCurrentItem(selItem)
    tHandle, tLine = outlineView.getSelectedHandle()
    assert tHandle == "88243afbe5ed8"
    assert tLine == 0

    assert outlineData.titleLabel.text() == "<b>Scene</b>"
    assert outlineData.titleValue.text() == "Scene One"
    assert outlineData.fileValue.text() == "Scene One"
    assert outlineData.itemValue.text() == "Finished"

    # Click POV Link
    assert outlineData.povKeyValue.text() == "<a href='Bod'>Bod</a>"
    outlineMain._tagClicked("Bod")
    assert nwGUI.docViewer.docHandle() == "4c4f28287af27"

    # Scene One, Section Two
    actItem = outlineView.topLevelItem(1)
    chpItem = actItem.child(0)
    scnItem = chpItem.child(0)
    selItem = scnItem.child(0)

    outlineView.setCurrentItem(selItem)
    tHandle, tLine = outlineView.getSelectedHandle()
    assert tHandle == "88243afbe5ed8"
    assert tLine == 12

    assert outlineData.titleLabel.text() == "<b>Section</b>"
    assert outlineData.titleValue.text() == "Scene One, Section Two"
    assert outlineData.fileValue.text() == "Scene One"
    assert outlineData.itemValue.text() == "Finished"

    outlineView._treeDoubleClick(selItem, 0)
    assert nwGUI.docEditor.docHandle() == "88243afbe5ed8"

    # qtbot.stop()

# END Test testGuiOutline_Content
