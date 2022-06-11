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

from PyQt5.QtWidgets import QAction, QMessageBox, QDialog, QInputDialog

from novelwriter.enum import nwItemType, nwWidget
from novelwriter.dialogs import GuiDocMerge, GuiItemEditor
from novelwriter.core.tree import NWTree


@pytest.mark.gui
def testDlgMerge_Main(qtbot, monkeypatch, nwGUI, fncProj, mockRnd):
    """Test the merge documents tool.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Ok)
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, text: (text, True))

    # Create a new project
    buildTestProject(nwGUI, fncProj)

    # Handles for new objects
    hNovelRoot  = "0000000000008"
    hChapterDir = "000000000000d"
    hChapterOne = "000000000000e"
    hSceneOne   = "000000000000f"
    hSceneTwo   = "0000000000010"
    hSceneThree = "0000000000011"
    hSceneFour  = "0000000000012"
    hMergedDoc  = "0000000000023"

    # Add Project Content
    monkeypatch.setattr(GuiItemEditor, "exec_", lambda *a: QDialog.Accepted)
    nwGUI.switchFocus(nwWidget.TREE)
    nwGUI.projView.projTree.clearSelection()
    nwGUI.projView.projTree._getTreeItem(hChapterDir).setSelected(True)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE)

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
    nwGUI.projView.projTree.clearSelection()
    nwGUI.projView.projTree._getTreeItem(hChapterDir).setSelected(True)

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
    nwGUI.projView.projTree.clearSelection()
    assert nwMerge._populateList() is False
    assert nwMerge.listBox.count() == 0

    # Non-existing item
    with monkeypatch.context() as mp:
        mp.setattr(NWTree, "__getitem__", lambda *a: None)
        nwGUI.projView.projTree.clearSelection()
        nwGUI.projView.projTree._getTreeItem(hChapterDir).setSelected(True)
        assert nwMerge._populateList() is False
        assert nwMerge.listBox.count() == 0

    # Select a non-folder
    nwGUI.projView.projTree.clearSelection()
    nwGUI.projView.projTree._getTreeItem(hChapterOne).setSelected(True)
    assert nwMerge._populateList() is False
    assert nwMerge.listBox.count() == 0

    # Select the chapter folder
    nwGUI.projView.projTree.clearSelection()
    nwGUI.projView.projTree._getTreeItem(hChapterDir).setSelected(True)
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
            "%%%%~path: %s/%s\n"
            "%%%%~kind: NOVEL/DOCUMENT\n"
            "%s\n\n"
            "%s\n\n"
            "%s\n\n"
            "%s\n\n"
            "%s\n\n"
        ) % (
            hNovelRoot,
            hMergedDoc,
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
