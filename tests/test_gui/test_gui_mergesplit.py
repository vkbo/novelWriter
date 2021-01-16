# -*- coding: utf-8 -*-
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

from shutil import copyfile
from tools import cmpFiles, getGuiItem

from PyQt5.QtWidgets import QAction, QMessageBox

from nw.gui import GuiDocMerge, GuiDocSplit

keyDelay = 2
typeDelay = 1
stepDelay = 20

@pytest.mark.gui
def testGuiMergeSplit_Tools(qtbot, monkeypatch, nwGUI, nwLipsum, refDir, outDir):
    """Test the full merge and split tools.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.Yes)

    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.openProject(nwLipsum)
    qtbot.wait(stepDelay)

    assert nwGUI.treeView.setSelectedHandle("45e6b01ca35c1")
    qtbot.wait(stepDelay)

    monkeypatch.setattr(GuiDocMerge, "exec_", lambda *args: None)
    nwGUI.mainMenu.aMergeDocs.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiDocMerge") is not None, timeout=1000)

    nwMerge = getGuiItem("GuiDocMerge")
    assert isinstance(nwMerge, GuiDocMerge)
    nwMerge.show()
    qtbot.wait(stepDelay)

    nwMerge._doMerge()
    qtbot.wait(stepDelay)

    assert nwGUI.theProject.projTree["73475cb40a568"] is not None

    projFile = os.path.join(nwLipsum, "content", "73475cb40a568.nwd")
    testFile = os.path.join(outDir, "guiMerge_73475cb40a568.nwd")
    compFile = os.path.join(refDir, "guiMerge_73475cb40a568.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    # Split By Chapter
    assert nwGUI.treeView.setSelectedHandle("73475cb40a568")
    qtbot.wait(stepDelay)

    monkeypatch.setattr(GuiDocSplit, "exec_", lambda *args: None)
    nwGUI.mainMenu.aSplitDoc.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiDocSplit") is not None, timeout=1000)

    nwSplit = getGuiItem("GuiDocSplit")
    assert isinstance(nwSplit, GuiDocSplit)
    nwSplit.show()
    qtbot.wait(stepDelay)

    nwSplit.splitLevel.setCurrentIndex(1)
    qtbot.wait(stepDelay)

    nwSplit._doSplit()
    assert nwGUI.theProject.projTree["71ee45a3c0db9"] is not None

    # This should give us back the file as it was before
    projFile = os.path.join(nwLipsum, "content", "71ee45a3c0db9.nwd")
    testFile = os.path.join(outDir, "guiMerge_71ee45a3c0db9.nwd")
    compFile = os.path.join(refDir, "guiMerge_73475cb40a568.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, [1, 2, 3])

    # Split By Scene
    assert nwGUI.treeView.setSelectedHandle("73475cb40a568")
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aSplitDoc.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiDocSplit") is not None, timeout=1000)

    nwSplit = getGuiItem("GuiDocSplit")
    assert isinstance(nwSplit, GuiDocSplit)
    qtbot.wait(stepDelay)
    nwSplit.splitLevel.setCurrentIndex(2)
    qtbot.wait(stepDelay)

    nwSplit._doSplit()

    assert nwGUI.theProject.projTree["25fc0e7096fc6"] is not None
    assert nwGUI.theProject.projTree["31489056e0916"] is not None
    assert nwGUI.theProject.projTree["98010bd9270f9"] is not None

    projFile = os.path.join(nwLipsum, "content", "25fc0e7096fc6.nwd")
    testFile = os.path.join(outDir, "guiSplit_25fc0e7096fc6.nwd")
    compFile = os.path.join(refDir, "guiSplit_25fc0e7096fc6.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    projFile = os.path.join(nwLipsum, "content", "31489056e0916.nwd")
    testFile = os.path.join(outDir, "guiSplit_31489056e0916.nwd")
    compFile = os.path.join(refDir, "guiSplit_31489056e0916.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    projFile = os.path.join(nwLipsum, "content", "98010bd9270f9.nwd")
    testFile = os.path.join(outDir, "guiSplit_98010bd9270f9.nwd")
    compFile = os.path.join(refDir, "guiSplit_98010bd9270f9.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    # Split By Section
    assert nwGUI.treeView.setSelectedHandle("73475cb40a568")
    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aSplitDoc.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiDocSplit") is not None, timeout=1000)

    nwSplit = getGuiItem("GuiDocSplit")
    assert isinstance(nwSplit, GuiDocSplit)
    qtbot.wait(stepDelay)
    nwSplit.splitLevel.setCurrentIndex(3)
    qtbot.wait(stepDelay)

    nwSplit._doSplit()

    assert nwGUI.theProject.projTree["1a6562590ef19"] is not None
    assert nwGUI.theProject.projTree["031b4af5197ec"] is not None
    assert nwGUI.theProject.projTree["41cfc0d1f2d12"] is not None
    assert nwGUI.theProject.projTree["2858dcd1057d3"] is not None
    assert nwGUI.theProject.projTree["2fca346db6561"] is not None

    projFile = os.path.join(nwLipsum, "content", "1a6562590ef19.nwd")
    testFile = os.path.join(outDir, "guiSplit_1a6562590ef19.nwd")
    compFile = os.path.join(refDir, "guiSplit_25fc0e7096fc6.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, [1, 2, 3])

    projFile = os.path.join(nwLipsum, "content", "031b4af5197ec.nwd")
    testFile = os.path.join(outDir, "guiSplit_031b4af5197ec.nwd")
    compFile = os.path.join(refDir, "guiSplit_031b4af5197ec.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    projFile = os.path.join(nwLipsum, "content", "41cfc0d1f2d12.nwd")
    testFile = os.path.join(outDir, "guiSplit_41cfc0d1f2d12.nwd")
    compFile = os.path.join(refDir, "guiSplit_41cfc0d1f2d12.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    projFile = os.path.join(nwLipsum, "content", "2858dcd1057d3.nwd")
    testFile = os.path.join(outDir, "guiSplit_2858dcd1057d3.nwd")
    compFile = os.path.join(refDir, "guiSplit_2858dcd1057d3.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    projFile = os.path.join(nwLipsum, "content", "2fca346db6561.nwd")
    testFile = os.path.join(outDir, "guiSplit_2fca346db6561.nwd")
    compFile = os.path.join(refDir, "guiSplit_2fca346db6561.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    # qtbot.stopForInteraction()

# END Test testGuiMergeSplit_Tools
