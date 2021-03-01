# -*- coding: utf-8 -*-
"""
novelWriter – Build Dialog Class Tester
=======================================

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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QMessageBox, QFileDialog

from nw.gui import GuiBuildNovel

keyDelay = 2
typeDelay = 1
stepDelay = 20

@pytest.mark.gui
def testGuiBuild_Tool(qtbot, monkeypatch, nwGUI, nwLipsum, refDir, outDir):
    """Test the build tool.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *args: QMessageBox.Yes)
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda a, b, c, **kwargs: (c, None))

    # Check that we cannot open when there is no project
    nwGUI.mainMenu.aBuildProject.activate(QAction.Trigger)
    assert getGuiItem("GuiBuildNovel") is None

    # Open a project
    assert nwGUI.openProject(nwLipsum)
    nwGUI.mainConf.lastPath = nwLipsum

    # Open the tool
    nwGUI.mainMenu.aBuildProject.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiBuildNovel") is not None, timeout=1000)

    nwBuild = getGuiItem("GuiBuildNovel")
    assert isinstance(nwBuild, GuiBuildNovel)

    # Default Settings
    qtbot.mouseClick(nwBuild.buildNovel, Qt.LeftButton)

    assert nwBuild._saveDocument(nwBuild.FMT_NWD)
    assert nwBuild._saveDocument(nwBuild.FMT_HTM)

    projFile = os.path.join(nwLipsum, "Lorem Ipsum.nwd")
    testFile = os.path.join(outDir, "guiBuild_Tool_Step1_Lorem_Ipsum.nwd")
    compFile = os.path.join(refDir, "guiBuild_Tool_Step1_Lorem_Ipsum.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    projFile = os.path.join(nwLipsum, "Lorem Ipsum.htm")
    testFile = os.path.join(outDir, "guiBuild_Tool_Step1_Lorem_Ipsum.htm")
    compFile = os.path.join(refDir, "guiBuild_Tool_Step1_Lorem_Ipsum.htm")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    # Change Title Formats and Flip Switches
    nwBuild.fmtChapter.setText(r"Chapter %chw%: %title%")
    qtbot.wait(stepDelay)
    nwBuild.fmtScene.setText(r"Scene %ch%.%sc%: %title%")
    qtbot.wait(stepDelay)
    nwBuild.fmtSection.setText(r"%ch%.%sc%.1: %title%")
    qtbot.wait(stepDelay)

    qtbot.mouseClick(nwBuild.justifyText, Qt.LeftButton)
    qtbot.wait(stepDelay)
    qtbot.mouseClick(nwBuild.includeSynopsis, Qt.LeftButton)
    qtbot.wait(stepDelay)
    qtbot.mouseClick(nwBuild.includeComments, Qt.LeftButton)
    qtbot.wait(stepDelay)
    qtbot.mouseClick(nwBuild.includeKeywords, Qt.LeftButton)
    qtbot.wait(stepDelay)

    qtbot.mouseClick(nwBuild.noteFiles, Qt.LeftButton)
    qtbot.wait(stepDelay)
    qtbot.mouseClick(nwBuild.ignoreFlag, Qt.LeftButton)
    qtbot.wait(stepDelay)

    qtbot.mouseClick(nwBuild.buildNovel, Qt.LeftButton)

    assert nwBuild._saveDocument(nwBuild.FMT_NWD)
    assert nwBuild._saveDocument(nwBuild.FMT_HTM)

    projFile = os.path.join(nwLipsum, "Lorem Ipsum.nwd")
    testFile = os.path.join(outDir, "guiBuild_Tool_Step2_Lorem_Ipsum.nwd")
    compFile = os.path.join(refDir, "guiBuild_Tool_Step2_Lorem_Ipsum.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    projFile = os.path.join(nwLipsum, "Lorem Ipsum.htm")
    testFile = os.path.join(outDir, "guiBuild_Tool_Step2_Lorem_Ipsum.htm")
    compFile = os.path.join(refDir, "guiBuild_Tool_Step2_Lorem_Ipsum.htm")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    # Replace Tabs with Spaces
    qtbot.mouseClick(nwBuild.replaceTabs, Qt.LeftButton)
    qtbot.wait(stepDelay)

    qtbot.mouseClick(nwBuild.buildNovel, Qt.LeftButton)

    # Save files that can be compared
    assert nwBuild._saveDocument(nwBuild.FMT_NWD)
    projFile = os.path.join(nwLipsum, "Lorem Ipsum.nwd")
    testFile = os.path.join(outDir, "guiBuild_Tool_Step3_Lorem_Ipsum.nwd")
    compFile = os.path.join(refDir, "guiBuild_Tool_Step3_Lorem_Ipsum.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    assert nwBuild._saveDocument(nwBuild.FMT_HTM)
    projFile = os.path.join(nwLipsum, "Lorem Ipsum.htm")
    testFile = os.path.join(outDir, "guiBuild_Tool_Step3_Lorem_Ipsum.htm")
    compFile = os.path.join(refDir, "guiBuild_Tool_Step3_Lorem_Ipsum.htm")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    # Putline Mode
    nwBuild.fmtChapter.setText(r"Chapter %chw%: %title%")
    qtbot.wait(stepDelay)
    nwBuild.fmtScene.setText(r"Scene %sca%: %title%")
    qtbot.wait(stepDelay)
    nwBuild.fmtSection.setText(r"Section: %title%")
    qtbot.wait(stepDelay)

    qtbot.mouseClick(nwBuild.includeComments, Qt.LeftButton)
    qtbot.wait(stepDelay)
    qtbot.mouseClick(nwBuild.noteFiles, Qt.LeftButton)
    qtbot.wait(stepDelay)
    qtbot.mouseClick(nwBuild.ignoreFlag, Qt.LeftButton)
    qtbot.wait(stepDelay)
    qtbot.mouseClick(nwBuild.includeBody, Qt.LeftButton)
    qtbot.wait(stepDelay)

    qtbot.mouseClick(nwBuild.buildNovel, Qt.LeftButton)

    # Save files that can be compared
    assert nwBuild._saveDocument(nwBuild.FMT_NWD)
    projFile = os.path.join(nwLipsum, "Lorem Ipsum.nwd")
    testFile = os.path.join(outDir, "guiBuild_Tool_Step4_Lorem_Ipsum.nwd")
    compFile = os.path.join(refDir, "guiBuild_Tool_Step4_Lorem_Ipsum.nwd")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    assert nwBuild._saveDocument(nwBuild.FMT_HTM)
    projFile = os.path.join(nwLipsum, "Lorem Ipsum.htm")
    testFile = os.path.join(outDir, "guiBuild_Tool_Step4_Lorem_Ipsum.htm")
    compFile = os.path.join(refDir, "guiBuild_Tool_Step4_Lorem_Ipsum.htm")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    # Check the JSON files too at this stage
    assert nwBuild._saveDocument(nwBuild.FMT_JSON_H)
    projFile = os.path.join(nwLipsum, "Lorem Ipsum.json")
    testFile = os.path.join(outDir, "guiBuild_Tool_Step4H_Lorem_Ipsum.json")
    compFile = os.path.join(refDir, "guiBuild_Tool_Step4H_Lorem_Ipsum.json")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, [8])

    assert nwBuild._saveDocument(nwBuild.FMT_JSON_M)
    projFile = os.path.join(nwLipsum, "Lorem Ipsum.json")
    testFile = os.path.join(outDir, "guiBuild_Tool_Step4M_Lorem_Ipsum.json")
    compFile = os.path.join(refDir, "guiBuild_Tool_Step4M_Lorem_Ipsum.json")
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, [8])

    # Save other file types handled by Qt
    # We assume the export itself by the Qt library works, so we just
    # check that novelWriter successfully writes the files.
    assert nwBuild._saveDocument(nwBuild.FMT_ODT)
    assert os.path.isfile(os.path.join(nwLipsum, "Lorem Ipsum.odt"))

    if not nwGUI.mainConf.osDarwin:
        assert nwBuild._saveDocument(nwBuild.FMT_PDF)
        assert os.path.isfile(os.path.join(nwLipsum, "Lorem Ipsum.pdf"))

    assert nwBuild._saveDocument(nwBuild.FMT_MD)
    assert os.path.isfile(os.path.join(nwLipsum, "Lorem Ipsum.md"))

    assert nwBuild._saveDocument(nwBuild.FMT_TXT)
    assert os.path.isfile(os.path.join(nwLipsum, "Lorem Ipsum.txt"))

    # Close the build tool
    htmlText  = nwBuild.htmlText
    htmlStyle = nwBuild.htmlStyle
    nwdText   = nwBuild.nwdText
    buildTime = nwBuild.buildTime
    nwBuild._doClose()

    # Re-open build dialog from cahce
    nwGUI.mainMenu.aBuildProject.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiBuildNovel") is not None, timeout=1000)

    nwBuild = getGuiItem("GuiBuildNovel")
    assert isinstance(nwBuild, GuiBuildNovel)

    assert nwBuild.viewCachedDoc()
    assert nwBuild.htmlText  == htmlText
    assert nwBuild.htmlStyle == htmlStyle
    assert nwBuild.nwdText   == nwdText
    assert nwBuild.buildTime == buildTime

    nwBuild._doClose()

    # qtbot.stopForInteraction()

# END Test testGuiBuild_Tool
