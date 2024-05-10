"""
novelWriter – Merge and Split Dialog Classes Tester
===================================================

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

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
from __future__ import annotations

import pytest

from novelwriter import SHARED
from novelwriter.dialogs.docsplit import GuiDocSplit
from novelwriter.dialogs.editlabel import GuiEditLabel

from tests.tools import C, buildTestProject


@pytest.mark.gui
def testDlgSplit_Main(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test the split document tool."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    # Create a new project
    buildTestProject(nwGUI, projPath)

    project = SHARED.project
    projTree = nwGUI.projView.projTree

    docText = (
        "Text\n\n"
        "##! Prologue\n\nText\n\n"
        "## Chapter One\n\nText\n\n"
        "### Scene One\n\nText\n\n"
        "### Scene Two\n\nText\n\n"
        "## Chapter Two\n\nText\n\n"
        "### Scene Three\n\nText\n\n"
        "### Scene Four\n\nText\n\n"
        "#! New Title\n\nText\n\n"
        "## New Chapter\n\nText\n\n"
        "### New Scene\n\nText\n\n"
        "#### New Section\n\nText\n\n"
    )

    hSplitDoc = project.newFile("Split Doc", C.hNovelRoot)
    assert hSplitDoc is not None
    project.writeNewFile(hSplitDoc, 1, True, docText)
    projTree.revealNewTreeItem(hSplitDoc, nHandle=C.hNovelRoot, wordCount=True)

    docText = f"# Split Doc\n\n{docText}"

    nwSplit = GuiDocSplit(nwGUI, hSplitDoc)
    nwSplit.show()
    qtbot.addWidget(nwSplit)

    # By default, only up to level three headings should be listed
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
    assert data["headerList"][3] == (12, 3, "Scene One")
    assert data["headerList"][4] == (16, 3, "Scene Two")
    assert data["headerList"][5] == (20, 2, "Chapter Two")
    assert data["headerList"][6] == (24, 3, "Scene Three")
    assert data["headerList"][7] == (28, 3, "Scene Four")
    assert data["headerList"][8] == (32, 1, "New Title")
    assert data["headerList"][9] == (36, 2, "New Chapter")
    assert data["headerList"][10] == (40, 3, "New Scene")
    assert data["headerList"][11] == (44, 4, "New Section")

    # Loading the dialog on a non-file item produces an empty list
    nwSplit._loadContent(C.hNovelRoot)
    assert nwSplit.listBox.count() == 0

    nwSplit.reject()
    # qtbot.stop()
