"""
novelWriter – GUI Outline Tests
===============================

This file is a part of novelWriter
Copyright (C) 2020 Veronica Berglyd Olsen and novelWriter contributors

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

import time

from shutil import copyfile

import pytest

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QFileDialog, QWidget

from novelwriter import CONFIG, SHARED
from novelwriter.constants import nwKeyWords
from novelwriter.core.project import NWProject
from novelwriter.enum import nwItemClass, nwOutline, nwView
from novelwriter.types import QtScrollAlwaysOff, QtScrollAsNeeded

from tests.helpers import buildTestProject, cmpFiles, writeFile


@pytest.mark.gui
def testGuiOutline_Main(qtbot, monkeypatch, nwGUI, projPath):
    """Test the outline view."""
    # Create a project
    buildTestProject(NWProject(), projPath)
    nwGUI.openProject(projPath)

    nwGUI.rebuildIndex()
    nwGUI._changeView(nwView.OUTLINE)

    outlineView = nwGUI.outlineView
    outlineTree = outlineView.outlineTree
    outlineData = outlineView.outlineData
    outlineMenu = outlineView.outlineBar.mColumns

    # Toggle scrollbars
    CONFIG.hideVScroll = True
    CONFIG.hideHScroll = True
    outlineView.initViewport()
    assert outlineTree.verticalScrollBarPolicy() == QtScrollAlwaysOff
    assert outlineTree.horizontalScrollBarPolicy() == QtScrollAlwaysOff
    assert outlineData.verticalScrollBarPolicy() == QtScrollAlwaysOff
    assert outlineData.horizontalScrollBarPolicy() == QtScrollAlwaysOff

    CONFIG.hideVScroll = False
    CONFIG.hideHScroll = False
    outlineView.initViewport()
    assert outlineTree.verticalScrollBarPolicy() == QtScrollAsNeeded
    assert outlineTree.horizontalScrollBarPolicy() == QtScrollAsNeeded
    assert outlineData.verticalScrollBarPolicy() == QtScrollAsNeeded
    assert outlineData.horizontalScrollBarPolicy() == QtScrollAsNeeded

    # Check focus
    with monkeypatch.context() as mp:
        mp.setattr(QWidget, "hasFocus", lambda *a: True)
        assert outlineView.treeHasFocus() is True

    outlineView.setTreeFocus()  # Can't check. just ensures that it doesn't error

    # Option State
    # ============

    pOptions = SHARED.project.options
    colNames = [h.name for h in nwOutline]
    colItems = list(nwOutline)
    colWidth = {h: outlineTree.DEF_WIDTH[h] for h in nwOutline}
    colHidden = {h: outlineTree.DEF_HIDDEN[h] for h in nwOutline}

    assert outlineTree.topLevelItemCount() > 0

    # Save header state not allowed
    outlineTree._lastBuild = 0
    outlineTree._saveHeaderState()
    assert pOptions.getValue("GuiOutline", "columnState", {}) == {}

    # Allow saving header state
    outlineTree._lastBuild = time.time()
    outlineTree._saveHeaderState()
    assert list(pOptions.getValue("GuiOutline", "columnState", {}).keys()) == colNames
    assert outlineTree._treeOrder == colItems
    assert outlineTree._colWidth == colWidth
    assert outlineTree._colHidden == colHidden

    # Get default values
    columnState = pOptions.getValue("GuiOutline", "columnState", {})

    # Add invalid column name
    newState = columnState.copy()
    newState.update({"blabla": (False, 42)})
    pOptions.setValue("GuiOutline", "columnState", newState)
    outlineTree._loadHeaderState()
    assert outlineTree._treeOrder == colItems
    assert outlineTree._colHidden == colHidden

    # Invalid column width data
    newState = columnState.copy()
    newState.update({"TITLE": (False, None)})
    pOptions.setValue("GuiOutline", "columnState", newState)
    outlineTree._loadHeaderState()
    assert outlineTree._treeOrder == colItems
    assert outlineTree._colHidden == colHidden

    # Invalid column state data
    newState = columnState.copy()
    newState.update({"TITLE": None})
    pOptions.setValue("GuiOutline", "columnState", newState)
    outlineTree._loadHeaderState()
    assert outlineTree._treeOrder == colItems
    assert outlineTree._colHidden == colHidden

    # Drop a few columns
    newState = columnState.copy()
    del newState[nwOutline.CHAR.name]
    del newState[nwOutline.WORLD.name]
    del newState[nwOutline.LINE.name]
    pOptions.setValue("GuiOutline", "columnState", newState)
    outlineTree._loadHeaderState()
    assert len(outlineTree._treeOrder) == len(colItems)
    assert len(outlineTree._colHidden) == len(colHidden)
    assert nwOutline.CHAR in outlineTree._treeOrder
    assert nwOutline.CHAR in outlineTree._colHidden
    assert nwOutline.WORLD in outlineTree._treeOrder
    assert nwOutline.WORLD in outlineTree._colHidden
    assert nwOutline.LINE in outlineTree._treeOrder
    assert nwOutline.LINE in outlineTree._colHidden

    # Valid settings
    pOptions.setValue("GuiOutline", "columnState", columnState)
    outlineTree._loadHeaderState()
    assert outlineTree._treeOrder == colItems
    assert outlineTree._colHidden == colHidden

    # Header Menu
    # ===========

    # Trigger the menu entry for all hidden columns
    for hItem in nwOutline:
        if outlineTree.DEF_HIDDEN[hItem]:
            outlineMenu.actionMap[hItem].activate(QAction.ActionEvent.Trigger)

    # Now no columns should be hidden
    outlineTree._saveHeaderState()
    hiddenStates = [v[0] for v in pOptions.getValue("GuiOutline", "columnState", {}).values()]
    assert len(hiddenStates) == len(columnState)
    assert not any(hiddenStates)

    # Move Columns
    # ============

    # Current Order
    order = [outlineTree._colIdx[col] for col in outlineTree._treeOrder]
    assert order == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

    # Move 3 to 0
    outlineTree._columnMoved(0, 3, 0)
    order = [outlineTree._colIdx[col] for col in outlineTree._treeOrder]
    assert order == [3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

    # qtbot.stop()


@pytest.mark.gui
def testGuiOutline_Content(qtbot, monkeypatch, nwGUI, prjLipsum, fncPath, tstPaths):
    """Test the outline view."""
    assert nwGUI.openProject(prjLipsum)

    nwGUI.rebuildIndex()
    nwGUI._changeView(nwView.OUTLINE)

    outlineView = nwGUI.outlineView
    outlineBar = outlineView.outlineBar
    outlineTree = outlineView.outlineTree
    outlineData = outlineView.outlineData

    lipHandle = "b3643d0f92e32"

    # Check defaults in dropdown list
    assert outlineBar.novelValue.itemData(0) == lipHandle
    assert outlineBar.novelValue.itemData(1) is None  # Separator
    assert outlineBar.novelValue.itemData(2) == ""  # All novels

    # An invalid list format is rejected
    listFormat = outlineBar.novelValue._listFormat
    outlineBar.novelValue.setListFormat("No placeholder here")
    assert outlineBar.novelValue._listFormat == listFormat

    # Add a second novel folder
    with qtbot.waitSignal(SHARED.rootFolderChanged):
        newHandle = SHARED.project.newRoot(nwItemClass.NOVEL)

    # Check new values in dropdown list
    assert outlineBar.novelValue.itemData(0) == lipHandle
    assert outlineBar.novelValue.itemData(1) == newHandle
    assert outlineBar.novelValue.itemData(2) is None  # Separator
    assert outlineBar.novelValue.itemData(3) == ""  # All novels

    # Add a bunch of files in a header order that hits all tree combos
    docList = [
        ("Section 1", 4),
        ("Scene 1", 3),
        ("Chapter 1", 2),
        ("Part 1", 1),
        ("Section 2", 4),
        ("Scene 2", 3),
        ("Chapter 2", 2),
        ("Section 3", 4),
        ("Scene 3", 3),
        ("Section 4", 4),
    ]
    for dTitle, hLevel in docList:
        aHandle = SHARED.project.newFile(dTitle, newHandle)
        hHash = "#" * hLevel
        writeFile(prjLipsum / "content" / f"{aHandle}.nwd", f"{hHash} {dTitle}\n\n")

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
    assert outlineData.titleLabel.text() == "Title"
    assert outlineData.titleValue.text() == "Lorem Ipsum"
    assert outlineData.fileValue.text() == "Lorem Ipsum"
    assert outlineData.itemValue.text() == "Finished"

    assert outlineData.cCValue.text() == "259"
    assert outlineData.wCValue.text() == "44"
    assert outlineData.pCValue.text() == "5"

    # Scene One
    selItem = outlineTree.topLevelItem(4)

    outlineTree.clearSelection()
    assert outlineTree.getSelectedHandle() == (None, None)  # No selection
    outlineTree.setCurrentItem(selItem)
    tHandle, sTitle = outlineTree.getSelectedHandle()
    assert tHandle == "88243afbe5ed8"
    assert sTitle == "T0001"

    assert outlineData.titleLabel.text() == "Scene"
    assert outlineData.titleValue.text() == "Scene One"
    assert outlineData.fileValue.text() == "Scene One"
    assert outlineData.itemValue.text() == "Finished"

    # An invalid handle does not update the details
    outlineData.showItem("0000000000000", "T0001")
    assert outlineData.titleValue.text() == "Scene One"

    # Click POV Link
    povLabel = outlineData.tagValues[nwKeyWords.POV_KEY][1]
    assert povLabel.text() == "<a href='Bod'>Bod</a>"
    with qtbot.waitSignal(outlineData.itemTagClicked, timeout=1000) as signal:
        povLabel.linkActivated.emit("Bod")
    assert signal.args == ["Bod"]

    outlineView._tagClicked("Bod")
    assert nwGUI.docViewer.docHandle == "4c4f28287af27"

    # An empty link does nothing
    nwGUI.docViewer._docHandle = None
    outlineView._tagClicked("")
    assert nwGUI.docViewer.docHandle is None

    # Scene One, Section Two
    selItem = outlineTree.topLevelItem(5)

    outlineTree.setCurrentItem(selItem)
    tHandle, sTitle = outlineTree.getSelectedHandle()
    assert tHandle == "88243afbe5ed8"
    assert sTitle == "T0002"

    assert outlineData.titleLabel.text() == "Section"
    assert outlineData.titleValue.text() == "Scene One, Section Two"
    assert outlineData.fileValue.text() == "Scene One"
    assert outlineData.itemValue.text() == "Finished"

    outlineTree._onItemDoubleClicked(selItem, 0)
    assert nwGUI.docEditor.docHandle == "88243afbe5ed8"

    # Double-clicking with no selection does nothing
    nwGUI.docEditor._docHandle = None
    outlineTree.clearSelection()
    outlineTree._onItemDoubleClicked(selItem, 0)
    assert nwGUI.docEditor.docHandle is None

    # Dump to CSV
    # ===========

    # Cancelling the save dialog does nothing
    with monkeypatch.context() as mp:
        mp.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: ("", ""))
        outlineBar.aExport.trigger()

    with monkeypatch.context() as mp:
        csvFile = fncPath / "outline.csv"
        mp.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (str(csvFile), ""))
        outlineBar.aExport.trigger()

    testFile = tstPaths.outDir / "guiOutline_Content_outline.csv"
    compFile = tstPaths.refDir / "guiOutline_Content_outline.csv"

    copyfile(csvFile, testFile)
    assert cmpFiles(testFile, compFile)

    # Open Project Tasks
    # ==================

    # A valid, previously saved handle is kept as-is
    SHARED.project.data.setLastHandle(newHandle, "outline")
    outlineView.openProjectTasks()
    assert outlineBar.novelValue.handle == newHandle

    # An invalid or missing handle falls back to the first novel root
    SHARED.project.data.setLastHandle(None, "outline")
    outlineView.openProjectTasks()
    assert outlineBar.novelValue.handle == lipHandle

    # qtbot.stop()
