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

import pytest

from tools import C, buildTestProject

from PyQt5.QtWidgets import QMessageBox

from novelwriter.dialogs import GuiDocSplit, GuiEditLabel


@pytest.mark.gui
def testDlgSplit_Main(qtbot, monkeypatch, nwGUI, fncProj, mockRnd):
    """Test the split document tool.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Ok)
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    # Create a new project
    buildTestProject(nwGUI, fncProj)

    theProject = nwGUI.theProject
    projTree = nwGUI.projView.projTree

    docText = (
        "Text\n\n"
        "##! Prologue\n\n"
        "Text\n\n"
        "## Chapter One\n\n"
        "### Scene One\n\n"
        "Text\n\n"
        "### Scene Two\n\n"
        "Text\n\n"
        "## Chapter Two\n\n"
        "### Scene Three\n\n"
        "Text\n\n"
        "### Scene Four\n\n"
        "Text\n\n"
        "#! New Title\n\n"
        "## New Chapter\n\n"
        "### New Scene\n\n"
        "#### New Section\n\n"
    )

    hSplitDoc = theProject.newFile("Split Doc", C.hNovelRoot)
    theProject.writeNewFile(hSplitDoc, 1, True, docText)
    projTree.revealNewTreeItem(hSplitDoc, nHandle=C.hNovelRoot, wordCount=True)

    docText = f"# Split Doc\n\n{docText}"

    nwSplit = GuiDocSplit(nwGUI, hSplitDoc)
    nwSplit.show()
    qtbot.addWidget(nwSplit)

    # By default, only up to level three headinsg should be listed
    assert nwSplit.splitLevel.currentData() == 3
    assert nwSplit.listBox.count() == 11

    # Changing to level 4, should reload and add the last section
    nwSplit.splitLevel.setCurrentIndex(3)
    assert nwSplit.listBox.count() == 12

    data, text = nwSplit.getData()
    assert text == docText.splitlines()
    assert data["sHandle"] == hSplitDoc
    assert data["spLevel"] == 4
    assert data["intoFolder"] is True
    assert data["docHierarchy"] is True
    assert data["headerList"][0] == (0, 1, "Split Doc")
    assert data["headerList"][1] == (4, 2, "Prologue")
    assert data["headerList"][2] == (8, 2, "Chapter One")
    assert data["headerList"][3] == (10, 3, "Scene One")
    assert data["headerList"][4] == (14, 3, "Scene Two")
    assert data["headerList"][5] == (18, 2, "Chapter Two")
    assert data["headerList"][6] == (20, 3, "Scene Three")
    assert data["headerList"][7] == (24, 3, "Scene Four")
    assert data["headerList"][8] == (28, 1, "New Title")
    assert data["headerList"][9] == (30, 2, "New Chapter")
    assert data["headerList"][10] == (32, 3, "New Scene")
    assert data["headerList"][11] == (34, 4, "New Section")

    # Loading the dialog on a non-file item produces an empty list
    nwSplit._loadContent(C.hNovelRoot)
    assert nwSplit.listBox.count() == 0

    nwSplit.reject()
    # qtbot.stop()

# END Test testDlgSplit_Main
