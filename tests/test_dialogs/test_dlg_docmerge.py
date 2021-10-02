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

from novelwriter.dialogs import GuiDocMerge, GuiItemEditor
from novelwriter.enum import nwItemType, nwWidget
from novelwriter.core.tree import NWTree


@pytest.mark.gui
def testDlgMerge_Main(qtbot, monkeypatch, nwGUI, fncProj):
    """Test the merge documents tool.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Ok)

    # Create a new project
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": fncProj})

    # Handles for new objects
    hChapterDir = "31489056e0916"
    hChapterOne = "98010bd9270f9"
    hSceneOne   = "0e17daca5f3e1"
    hSceneTwo   = "1a6562590ef19"
    hSceneThree = "031b4af5197ec"
    hSceneFour  = "41cfc0d1f2d12"
    hMergedDoc  = "2858dcd1057d3"

    # Add Project Content
    monkeypatch.setattr(GuiItemEditor, "exec_", lambda *a: QDialog.Accepted)
    nwGUI.switchFocus(nwWidget.TREE)
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem(hChapterDir).setSelected(True)
    nwGUI.treeView.newTreeItem(nwItemType.FILE, None)
    nwGUI.treeView.newTreeItem(nwItemType.FILE, None)
    nwGUI.treeView.newTreeItem(nwItemType.FILE, None)

    assert nwGUI.saveProject() is True
    assert nwGUI.closeProject() is True

    tChapterOne = "## Chapter One\n\n% Chapter one comment\n"
    tSceneOne   = "### Scene One\n\nThere once was a man from Nantucket"
    tSceneTwo   = "### Scene Two\n\nWho kept all his cash in a bucket."
    tSceneThree = "### Scene Three\n\n\tBut his daughter, named Nan,  \n\tRan away with a man"
    tSceneFour  = "### Scene Four\n\nAnd as for the bucket, Nantucket."

    contentDir = os.path.join(fncProj, "content")
    writeFile(os.path.join(contentDir, hChapterOne+".nwd"), tChapterOne)
    writeFile(os.path.join(contentDir, hSceneOne+".nwd"), tSceneOne)
    writeFile(os.path.join(contentDir, hSceneTwo+".nwd"), tSceneTwo)
    writeFile(os.path.join(contentDir, hSceneThree+".nwd"), tSceneThree)
    writeFile(os.path.join(contentDir, hSceneFour+".nwd"), tSceneFour)

    assert nwGUI.openProject(fncProj) is True

    # Open the Merge tool
    nwGUI.switchFocus(nwWidget.TREE)
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem(hChapterDir).setSelected(True)

    monkeypatch.setattr(GuiDocMerge, "exec_", lambda *a: None)
    nwGUI.mainMenu.aMergeDocs.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiDocMerge") is not None, timeout=1000)

    nwMerge = getGuiItem("GuiDocMerge")
    assert isinstance(nwMerge, GuiDocMerge)
    nwMerge.show()
    qtbot.wait(50)

    # Populate List
    # =============

    nwMerge.listBox.clear()
    assert nwMerge.listBox.count() == 0

    # No item selected
    nwGUI.treeView.clearSelection()
    assert nwMerge._populateList() is False
    assert nwMerge.listBox.count() == 0

    # Non-existing item
    with monkeypatch.context() as mp:
        mp.setattr(NWTree, "__getitem__", lambda *a: None)
        nwGUI.treeView.clearSelection()
        nwGUI.treeView._getTreeItem(hChapterDir).setSelected(True)
        assert nwMerge._populateList() is False
        assert nwMerge.listBox.count() == 0

    # Select a non-folder
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem(hChapterOne).setSelected(True)
    assert nwMerge._populateList() is False
    assert nwMerge.listBox.count() == 0

    # Select the chapter folder
    nwGUI.treeView.clearSelection()
    nwGUI.treeView._getTreeItem(hChapterDir).setSelected(True)
    assert nwMerge._populateList() is True
    assert nwMerge.listBox.count() == 5

    # Merge Documents
    # ===============

    # First, a successful merge
    with monkeypatch.context() as mp:
        mp.setattr(GuiDocMerge, "_doClose", lambda *a: None)
        assert nwMerge._doMerge() is True
        assert nwGUI.saveProject() is True
        mergedFile = os.path.join(contentDir, hMergedDoc+".nwd")
        assert os.path.isfile(mergedFile)
        assert readFile(mergedFile) == (
            "%%%%~name: New Chapter\n"
            "%%%%~path: 73475cb40a568/2858dcd1057d3\n"
            "%%%%~kind: NOVEL/DOCUMENT\n"
            "%s\n\n"
            "%s\n\n"
            "%s\n\n"
            "%s\n\n"
            "%s\n\n"
        ) % (
            tChapterOne.strip(),
            tSceneOne.strip(),
            tSceneTwo.strip(),
            tSceneThree.strip(),
            tSceneFour.strip(),
        )

    # OS error
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert nwMerge._doMerge() is False

    # Can't find the source item
    with monkeypatch.context() as mp:
        mp.setattr(NWTree, "__getitem__", lambda *a: None)
        assert nwMerge._doMerge() is False

    # No source handle set
    nwMerge.sourceItem = None
    assert nwMerge._doMerge() is False

    # No documents to merge
    nwMerge.listBox.clear()
    assert nwMerge._doMerge() is False

    # Close up
    nwMerge._doClose()

    # qtbot.stopForInteraction()

# END Test testDlgMerge_Main
