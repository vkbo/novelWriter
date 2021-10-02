"""
novelWriter – Merge and Split Dialog Classes Tester
===================================================

This file is a part of novelWriter
Copyright 2018–2021, Veronica Berglyd Olsen

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

from tools import getGuiItem, readFile, writeFile
from mock import causeOSError

from PyQt5.QtWidgets import QAction, QMessageBox, QDialog

from novelwriter.dialogs import GuiDocSplit, GuiItemEditor
from novelwriter.enum import nwItemType, nwWidget
from novelwriter.core.document import NWDoc
from novelwriter.core.tree import NWTree


@pytest.mark.gui
def testDlgSplit_Main(qtbot, monkeypatch, nwGUI, fncProj):
    """Test the split document tool.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Ok)

    # Create a new project
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": fncProj}) is True

    # Handles for new objects
    hNovelRoot  = "73475cb40a568"
    hChapterDir = "31489056e0916"
    hToSplit    = "1a6562590ef19"
    hPartition  = "41cfc0d1f2d12"
    hChapterOne = "2858dcd1057d3"
    hSceneOne   = "2fca346db6561"
    hSceneTwo   = "02d20bbd7e394"
    hSceneThree = "7688b6ef52555"
    hSceneFour  = "c837649cce43f"
    hSceneFive  = "6208ef0f7750c"

    # Add Project Content
    monkeypatch.setattr(GuiItemEditor, "exec_", lambda *a: QDialog.Accepted)
    nwGUI.switchFocus(nwWidget.TREE)
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem(hNovelRoot).setSelected(True)
    nwGUI.treeView.newTreeItem(nwItemType.FILE, None)

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
            "%%%%~path: 031b4af5197ec/%s\n"
            "%%%%~kind: NOVEL/DOCUMENT\n"
            "%s\n\n"
        ) % (hPartition, tPartition)

        assert readFile(os.path.join(contentDir, hChapterOne+".nwd")) == (
            "%%%%~name: Chapter One\n"
            "%%%%~path: 031b4af5197ec/%s\n"
            "%%%%~kind: NOVEL/DOCUMENT\n"
            "%s\n\n"
        ) % (hChapterOne, tChapterOne)

        assert readFile(os.path.join(contentDir, hSceneOne+".nwd")) == (
            "%%%%~name: Scene One\n"
            "%%%%~path: 031b4af5197ec/%s\n"
            "%%%%~kind: NOVEL/DOCUMENT\n"
            "%s\n\n"
        ) % (hSceneOne, tSceneOne)

        assert readFile(os.path.join(contentDir, hSceneTwo+".nwd")) == (
            "%%%%~name: Scene Two\n"
            "%%%%~path: 031b4af5197ec/%s\n"
            "%%%%~kind: NOVEL/DOCUMENT\n"
            "%s\n\n"
        ) % (hSceneTwo, tSceneTwo)

        assert readFile(os.path.join(contentDir, hSceneThree+".nwd")) == (
            "%%%%~name: Scene Three\n"
            "%%%%~path: 031b4af5197ec/%s\n"
            "%%%%~kind: NOVEL/DOCUMENT\n"
            "%s\n\n"
        ) % (hSceneThree, tSceneThree)

        assert readFile(os.path.join(contentDir, hSceneFour+".nwd")) == (
            "%%%%~name: Scene Four\n"
            "%%%%~path: 031b4af5197ec/%s\n"
            "%%%%~kind: NOVEL/DOCUMENT\n"
            "%s\n\n"
        ) % (hSceneFour, tSceneFour)

        assert readFile(os.path.join(contentDir, hSceneFive+".nwd")) == (
            "%%%%~name: The End\n"
            "%%%%~path: 031b4af5197ec/%s\n"
            "%%%%~kind: NOVEL/DOCUMENT\n"
            "%s\n\n"
        ) % (hSceneFive, tSceneFive)

    # OS error
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert nwSplit._doSplit() is False

    # Select to not split
    with monkeypatch.context() as mp:
        mp.setattr(QMessageBox, "question", lambda *a: QMessageBox.No)
        assert nwSplit._doSplit() is False

    # Block folder creation by returning that the folder has a depth
    # of 50 items in the tree
    with monkeypatch.context() as mp:
        mp.setattr(NWTree, "getItemPath", lambda *a: [""]*50)
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
