"""
novelWriter – Merge and Split Dialog Classes Tester
===================================================

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

from mock import causeOSError
from tools import getGuiItem, readFile, writeFile, buildTestProject

from PyQt5.QtWidgets import QAction, QMessageBox, QDialog

from novelwriter.enum import nwItemType, nwWidget
from novelwriter.dialogs import GuiDocSplit, GuiItemEditor
from novelwriter.core.tree import NWTree
from novelwriter.core.document import NWDoc


@pytest.mark.gui
def testDlgSplit_Main(qtbot, monkeypatch, nwGUI, fncProj, mockRnd):
    """Test the split document tool.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Ok)

    # Create a new project
    buildTestProject(nwGUI, fncProj)

    # Handles for new objects
    hNovelRoot  = "0000000000008"
    hChapterDir = "000000000000d"
    hToSplit    = "0000000000010"
    hNewFolder  = "0000000000021"
    hPartition  = "0000000000022"
    hChapterOne = "0000000000023"
    hSceneOne   = "0000000000024"
    hSceneTwo   = "0000000000025"
    hSceneThree = "0000000000026"
    hSceneFour  = "0000000000027"
    hSceneFive  = "0000000000028"

    # Add Project Content
    monkeypatch.setattr(GuiItemEditor, "exec_", lambda *a: QDialog.Accepted)
    nwGUI.switchFocus(nwWidget.TREE)
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem(hNovelRoot).setSelected(True)
    nwGUI.treeView.newTreeItem(nwItemType.FILE)

    assert nwGUI.saveProject() is True
    assert nwGUI.closeProject() is True

    tPartition  = "# Nantucket"
    tChapterOne = "## Chapter One\n\n% Chapter one comment"
    tSceneOne   = "### Scene One\n\nThere once was a man from Nantucket"
    tSceneTwo   = "### Scene Two\n\nWho kept all his cash in a bucket."
    tSceneThree = "### Scene Three\n\n\tBut his daughter, named Nan,  \n\tRan away with a man"
    tSceneFour  = "### Scene Four\n\nAnd as for the bucket, Nantucket."
    tSceneFive  = "#### The End\n\nend"

    tToSplit = (
        f"{tPartition}\n\n{tChapterOne}\n\n"
        f"{tSceneOne}\n\n{tSceneTwo}\n\n"
        f"{tSceneThree}\n\n{tSceneFour}\n\n"
        f"{tSceneFive}\n\n"
    )

    contentDir = os.path.join(fncProj, "content")
    writeFile(os.path.join(contentDir, hToSplit+".nwd"), tToSplit)

    assert nwGUI.openProject(fncProj) is True

    # Open the Split tool
    nwGUI.switchFocus(nwWidget.TREE)
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem(hToSplit).setSelected(True)

    monkeypatch.setattr(GuiDocSplit, "exec_", lambda *a: None)
    nwGUI.mainMenu.aSplitDoc.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiDocSplit") is not None, timeout=1000)

    nwSplit = getGuiItem("GuiDocSplit")
    assert isinstance(nwSplit, GuiDocSplit)
    nwSplit.show()
    qtbot.wait(50)

    # Populate List
    # =============

    nwSplit.listBox.clear()
    assert nwSplit.listBox.count() == 0

    # No item selected
    nwSplit.sourceItem = None
    nwGUI.treeView.clearSelection()
    assert nwSplit._populateList() is False
    assert nwSplit.listBox.count() == 0

    # Non-existing item
    with monkeypatch.context() as mp:
        mp.setattr(NWTree, "__getitem__", lambda *a: None)
        nwSplit.sourceItem = None
        nwGUI.treeView.clearSelection()
        nwGUI.treeView._getTreeItem(hToSplit).setSelected(True)
        assert nwSplit._populateList() is False
        assert nwSplit.listBox.count() == 0

    # Select a non-file
    nwSplit.sourceItem = None
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem(hChapterDir).setSelected(True)
    assert nwSplit._populateList() is False
    assert nwSplit.listBox.count() == 0

    # Error when reading documents
    with monkeypatch.context() as mp:
        mp.setattr(NWDoc, "readDocument", lambda *a: None)
        nwSplit.sourceItem = hToSplit
        assert nwSplit._populateList() is False
        assert nwSplit.listBox.count() == 0

    # Read properly, and check split levels

    # Level 1
    nwSplit.splitLevel.setCurrentIndex(0)
    nwSplit.sourceItem = hToSplit
    assert nwSplit._populateList() is True
    assert nwSplit.listBox.count() == 1

    # Level 2
    nwSplit.splitLevel.setCurrentIndex(1)
    nwSplit.sourceItem = hToSplit
    assert nwSplit._populateList() is True
    assert nwSplit.listBox.count() == 2

    # Level 3
    nwSplit.splitLevel.setCurrentIndex(2)
    nwSplit.sourceItem = hToSplit
    assert nwSplit._populateList() is True
    assert nwSplit.listBox.count() == 6

    # Level 4
    nwSplit.splitLevel.setCurrentIndex(3)
    nwSplit.sourceItem = hToSplit
    assert nwSplit._populateList() is True
    assert nwSplit.listBox.count() == 7

    # Split Document
    # ==============

    # Test a proper split first
    with monkeypatch.context() as mp:
        mp.setattr(GuiDocSplit, "_doClose", lambda *a: None)
        assert nwSplit._doSplit() is True
        assert nwGUI.saveProject()

        assert readFile(os.path.join(contentDir, hPartition+".nwd")) == (
            "%%%%~name: Nantucket\n"
            "%%%%~path: %s/%s\n"
            "%%%%~kind: NOVEL/DOCUMENT\n"
            "%s\n\n"
        ) % (hNewFolder, hPartition, tPartition)

        assert readFile(os.path.join(contentDir, hChapterOne+".nwd")) == (
            "%%%%~name: Chapter One\n"
            "%%%%~path: %s/%s\n"
            "%%%%~kind: NOVEL/DOCUMENT\n"
            "%s\n\n"
        ) % (hNewFolder, hChapterOne, tChapterOne)

        assert readFile(os.path.join(contentDir, hSceneOne+".nwd")) == (
            "%%%%~name: Scene One\n"
            "%%%%~path: %s/%s\n"
            "%%%%~kind: NOVEL/DOCUMENT\n"
            "%s\n\n"
        ) % (hNewFolder, hSceneOne, tSceneOne)

        assert readFile(os.path.join(contentDir, hSceneTwo+".nwd")) == (
            "%%%%~name: Scene Two\n"
            "%%%%~path: %s/%s\n"
            "%%%%~kind: NOVEL/DOCUMENT\n"
            "%s\n\n"
        ) % (hNewFolder, hSceneTwo, tSceneTwo)

        assert readFile(os.path.join(contentDir, hSceneThree+".nwd")) == (
            "%%%%~name: Scene Three\n"
            "%%%%~path: %s/%s\n"
            "%%%%~kind: NOVEL/DOCUMENT\n"
            "%s\n\n"
        ) % (hNewFolder, hSceneThree, tSceneThree)

        assert readFile(os.path.join(contentDir, hSceneFour+".nwd")) == (
            "%%%%~name: Scene Four\n"
            "%%%%~path: %s/%s\n"
            "%%%%~kind: NOVEL/DOCUMENT\n"
            "%s\n\n"
        ) % (hNewFolder, hSceneFour, tSceneFour)

        assert readFile(os.path.join(contentDir, hSceneFive+".nwd")) == (
            "%%%%~name: The End\n"
            "%%%%~path: %s/%s\n"
            "%%%%~kind: NOVEL/DOCUMENT\n"
            "%s\n\n"
        ) % (hNewFolder, hSceneFive, tSceneFive)

    # OS error
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert nwSplit._doSplit() is False

    # Select to not split
    with monkeypatch.context() as mp:
        mp.setattr(QMessageBox, "question", lambda *a: QMessageBox.No)
        assert nwSplit._doSplit() is False

    # Clear the list
    nwSplit.listBox.clear()
    assert nwSplit._doSplit() is False

    # Can't find sourcv item
    with monkeypatch.context() as mp:
        mp.setattr(NWTree, "__getitem__", lambda *a: None)
        assert nwSplit._doSplit() is False

    # No source item set
    nwSplit.sourceItem = None
    assert nwSplit._doSplit() is False

    # Close
    nwSplit._doClose()

    # qtbot.stopForInteraction()

# END Test testDlgSplit_Main
