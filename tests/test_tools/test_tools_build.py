"""
novelWriter – Build Dialog Class Tester
=======================================

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

import pytest

from shutil import copyfile

from tools import ODT_IGNORE, cmpFiles, getGuiItem

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QFileDialog

from novelwriter import CONFIG
from novelwriter.tools.build import GuiBuildNovel


@pytest.mark.gui
@pytest.mark.skip
def testToolBuild_Main(qtbot, monkeypatch, nwGUI, prjLipsum, tstPaths):
    """Test the build tool.
    """
    # Block message box
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda a, b, c, **k: (c, None))

    # Check that we cannot open when there is no project
    nwGUI.mainMenu.aBuildProject.activate(QAction.Trigger)
    assert getGuiItem("GuiBuildNovel") is None

    # Open a project
    assert nwGUI.openProject(prjLipsum)

    # Open the tool
    nwGUI.mainMenu.aBuildProject.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiBuildNovel") is not None, timeout=1000)

    nwBuild = getGuiItem("GuiBuildNovel")
    assert isinstance(nwBuild, GuiBuildNovel)

    nwBuild.textFont.setText("DejaVu Sans")
    nwBuild.textSize.setValue(11)

    # Test Save
    # =========

    # Invalid file format
    assert not nwBuild._saveDocument(-1)

    # No path selected
    with monkeypatch.context() as mp:
        mp.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: ("", ""))
        assert not nwBuild._saveDocument(nwBuild.FMT_NWD)

    # Default Settings
    CONFIG._lastPath = prjLipsum
    qtbot.mouseClick(nwBuild.buildNovel, Qt.LeftButton)

    assert nwBuild._saveDocument(nwBuild.FMT_NWD)
    projFile = prjLipsum / "Lorem Ipsum.nwd"
    testFile = tstPaths.outDir / "guiBuild_Tool_Step1_Lorem_Ipsum.nwd"
    compFile = tstPaths.refDir / "guiBuild_Tool_Step1_Lorem_Ipsum.nwd"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    assert nwBuild._saveDocument(nwBuild.FMT_HTM)
    projFile = prjLipsum / "Lorem Ipsum.htm"
    testFile = tstPaths.outDir / "guiBuild_Tool_Step1_Lorem_Ipsum.htm"
    compFile = tstPaths.refDir / "guiBuild_Tool_Step1_Lorem_Ipsum.htm"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    assert nwBuild._saveDocument(nwBuild.FMT_MD)
    projFile = prjLipsum / "Lorem Ipsum.md"
    testFile = tstPaths.outDir / "guiBuild_Tool_Step1_Lorem_Ipsum.md"
    compFile = tstPaths.refDir / "guiBuild_Tool_Step1_Lorem_Ipsum.md"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    assert nwBuild._saveDocument(nwBuild.FMT_GH)
    projFile = prjLipsum / "Lorem Ipsum.md"
    testFile = tstPaths.outDir / "guiBuild_Tool_Step1G_Lorem_Ipsum.md"
    compFile = tstPaths.refDir / "guiBuild_Tool_Step1G_Lorem_Ipsum.md"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    assert nwBuild._saveDocument(nwBuild.FMT_FODT)
    projFile = prjLipsum / "Lorem Ipsum.fodt"
    testFile = tstPaths.outDir / "guiBuild_Tool_Step1_Lorem_Ipsum.fodt"
    compFile = tstPaths.refDir / "guiBuild_Tool_Step1_Lorem_Ipsum.fodt"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=ODT_IGNORE)

    # Change Title Formats and Flip Switches
    nwBuild.fmtChapter.setText(r"Chapter %chw%: %title%")
    nwBuild.fmtScene.setText(r"Scene %ch%.%sc%: %title%")
    nwBuild.fmtSection.setText(r"%ch%.%sc%.1: %title%")

    qtbot.mouseClick(nwBuild.justifyText, Qt.LeftButton)
    qtbot.mouseClick(nwBuild.includeSynopsis, Qt.LeftButton)
    qtbot.mouseClick(nwBuild.includeComments, Qt.LeftButton)
    qtbot.mouseClick(nwBuild.includeKeywords, Qt.LeftButton)
    qtbot.mouseClick(nwBuild.replaceUCode, Qt.LeftButton)

    qtbot.mouseClick(nwBuild.noteFiles, Qt.LeftButton)
    qtbot.mouseClick(nwBuild.ignoreFlag, Qt.LeftButton)

    qtbot.mouseClick(nwBuild.buildNovel, Qt.LeftButton)

    assert nwBuild._saveDocument(nwBuild.FMT_NWD)
    projFile = prjLipsum / "Lorem Ipsum.nwd"
    testFile = tstPaths.outDir / "guiBuild_Tool_Step2_Lorem_Ipsum.nwd"
    compFile = tstPaths.refDir / "guiBuild_Tool_Step2_Lorem_Ipsum.nwd"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    assert nwBuild._saveDocument(nwBuild.FMT_HTM)
    projFile = prjLipsum / "Lorem Ipsum.htm"
    testFile = tstPaths.outDir / "guiBuild_Tool_Step2_Lorem_Ipsum.htm"
    compFile = tstPaths.refDir / "guiBuild_Tool_Step2_Lorem_Ipsum.htm"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    assert nwBuild._saveDocument(nwBuild.FMT_MD)
    projFile = prjLipsum / "Lorem Ipsum.md"
    testFile = tstPaths.outDir / "guiBuild_Tool_Step2_Lorem_Ipsum.md"
    compFile = tstPaths.refDir / "guiBuild_Tool_Step2_Lorem_Ipsum.md"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    assert nwBuild._saveDocument(nwBuild.FMT_FODT)
    projFile = prjLipsum / "Lorem Ipsum.fodt"
    testFile = tstPaths.outDir / "guiBuild_Tool_Step2_Lorem_Ipsum.fodt"
    compFile = tstPaths.refDir / "guiBuild_Tool_Step2_Lorem_Ipsum.fodt"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=ODT_IGNORE)

    # Replace Tabs with Spaces
    qtbot.mouseClick(nwBuild.replaceTabs, Qt.LeftButton)

    qtbot.mouseClick(nwBuild.buildNovel, Qt.LeftButton)

    # Save files that can be compared
    assert nwBuild._saveDocument(nwBuild.FMT_NWD)
    projFile = prjLipsum / "Lorem Ipsum.nwd"
    testFile = tstPaths.outDir / "guiBuild_Tool_Step3_Lorem_Ipsum.nwd"
    compFile = tstPaths.refDir / "guiBuild_Tool_Step3_Lorem_Ipsum.nwd"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    assert nwBuild._saveDocument(nwBuild.FMT_HTM)
    projFile = prjLipsum / "Lorem Ipsum.htm"
    testFile = tstPaths.outDir / "guiBuild_Tool_Step3_Lorem_Ipsum.htm"
    compFile = tstPaths.refDir / "guiBuild_Tool_Step3_Lorem_Ipsum.htm"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    assert nwBuild._saveDocument(nwBuild.FMT_MD)
    projFile = prjLipsum / "Lorem Ipsum.md"
    testFile = tstPaths.outDir / "guiBuild_Tool_Step3_Lorem_Ipsum.md"
    compFile = tstPaths.refDir / "guiBuild_Tool_Step3_Lorem_Ipsum.md"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    assert nwBuild._saveDocument(nwBuild.FMT_FODT)
    projFile = prjLipsum / "Lorem Ipsum.fodt"
    testFile = tstPaths.outDir / "guiBuild_Tool_Step3_Lorem_Ipsum.fodt"
    compFile = tstPaths.refDir / "guiBuild_Tool_Step3_Lorem_Ipsum.fodt"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=ODT_IGNORE)

    # Putline Mode
    nwBuild.fmtChapter.setText(r"Chapter %chw%: %title%")
    nwBuild.fmtScene.setText(r"Scene %sca%: %title%")
    nwBuild.fmtSection.setText(r"Section: %title%")

    qtbot.mouseClick(nwBuild.includeComments, Qt.LeftButton)
    qtbot.mouseClick(nwBuild.noteFiles, Qt.LeftButton)
    qtbot.mouseClick(nwBuild.ignoreFlag, Qt.LeftButton)
    qtbot.mouseClick(nwBuild.includeBody, Qt.LeftButton)

    qtbot.mouseClick(nwBuild.buildNovel, Qt.LeftButton)

    # Save files that can be compared
    assert nwBuild._saveDocument(nwBuild.FMT_NWD)
    projFile = prjLipsum / "Lorem Ipsum.nwd"
    testFile = tstPaths.outDir / "guiBuild_Tool_Step4_Lorem_Ipsum.nwd"
    compFile = tstPaths.refDir / "guiBuild_Tool_Step4_Lorem_Ipsum.nwd"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    assert nwBuild._saveDocument(nwBuild.FMT_HTM)
    projFile = prjLipsum / "Lorem Ipsum.htm"
    testFile = tstPaths.outDir / "guiBuild_Tool_Step4_Lorem_Ipsum.htm"
    compFile = tstPaths.refDir / "guiBuild_Tool_Step4_Lorem_Ipsum.htm"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    # Check the JSON files too at this stage
    assert nwBuild._saveDocument(nwBuild.FMT_JSON_H)
    projFile = prjLipsum / "Lorem Ipsum.json"
    testFile = tstPaths.outDir / "guiBuild_Tool_Step4H_Lorem_Ipsum.json"
    compFile = tstPaths.refDir / "guiBuild_Tool_Step4H_Lorem_Ipsum.json"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, [6])

    assert nwBuild._saveDocument(nwBuild.FMT_JSON_M)
    projFile = prjLipsum / "Lorem Ipsum.json"
    testFile = tstPaths.outDir / "guiBuild_Tool_Step4M_Lorem_Ipsum.json"
    compFile = tstPaths.refDir / "guiBuild_Tool_Step4M_Lorem_Ipsum.json"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, [6])

    # Since odt and fodt is built by the same code, we don't check the
    # output. but just that the different format can be written as well
    assert nwBuild._saveDocument(nwBuild.FMT_ODT)
    assert (prjLipsum / "Lorem Ipsum.odt").is_file()

    # Print to PDF
    if not CONFIG.osDarwin:
        assert nwBuild._saveDocument(nwBuild.FMT_PDF)
        assert (prjLipsum / "Lorem Ipsum.pdf").is_file()

    # Close the build tool
    htmlText  = nwBuild.htmlText
    htmlStyle = nwBuild.htmlStyle
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
    assert nwBuild.buildTime == buildTime

    nwBuild._doClose()

    # qtbot.stop()

# END Test testToolBuild_Main
