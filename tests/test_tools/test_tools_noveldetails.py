"""
novelWriter – Novel Details Tool Tester
=======================================

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

from PyQt5.QtWidgets import QAction

from novelwriter import SHARED
from novelwriter.enum import nwItemClass
from novelwriter.tools.noveldetails import GuiNovelDetails


@pytest.mark.gui
def testToolNovelDetails_Main(qtbot, nwGUI, prjLipsum, ipsumText):
    """Test the Novel Details main dialog."""
    nwGUI.openProject(prjLipsum)
    nHandle = "b3643d0f92e32"

    # Add a second Novel folder
    project = SHARED.project
    secondText = "#! Second\n\n" + "\n\n".join(ipsumText)
    sHandle = project.newRoot(nwItemClass.NOVEL, "Second")
    dHandle = project.newFile("Document", sHandle)
    project.storage.getDocument(dHandle).writeDocument(secondText)
    project.index.reIndexHandle(dHandle)
    nwGUI.projView.projTree.revealNewTreeItem(sHandle)
    nwGUI.projView.projTree.revealNewTreeItem(dHandle)

    # Create the dialog
    nwGUI.mainMenu.aNovelDetails.activate(QAction.ActionEvent.Trigger)
    qtbot.waitUntil(lambda: SHARED.findTopLevelWidget(GuiNovelDetails) is not None, timeout=1000)
    details = SHARED.findTopLevelWidget(GuiNovelDetails)
    assert isinstance(details, GuiNovelDetails)

    # Overview Page
    # =============
    overview = details.overviewPage

    # The selector should default to the first entry
    assert details.novelSelector.handle == nHandle

    # Check project data
    assert overview.projName.text() == "Lorem Ipsum"
    assert overview.projWords.text() == f"{4376:n}"
    assert overview.projNovels.text() == f"{3638:n}"
    assert overview.projNotes.text() == f"{738:n}"
    assert overview.projRevisions.text() != ""
    assert overview.projEditTime.text() != ""

    # Check novel data for "Novel"
    assert overview.novelName.text() == "Novel"
    assert overview.novelWords.text() == f"{3000:n}"
    assert overview.novelChapters.text() == f"{3:n}"
    assert overview.novelScenes.text() == f"{5:n}"

    # Check novel data for "Second"
    details.novelSelector.setHandle(sHandle, blockSignal=False)
    assert overview.novelName.text() == "Second"
    assert overview.novelWords.text() == f"{529:n}"
    assert overview.novelChapters.text() == f"{0:n}"
    assert overview.novelScenes.text() == f"{0:n}"

    # Contents Page
    # =============
    details.novelSelector.setHandle(nHandle, blockSignal=False)
    details.sidebar.button(details.PAGE_CONTENTS).click()
    assert details.mainStack.currentIndex() == 1
    contents = details.contentsPage

    # Check defaults
    words = [f"{v:n}" for v in [40, 176, 92, 6, 1071, 1615, 0]]
    pages = [f"{v:n}" for v in [2, 2, 2, 2, 4, 6, 0]]
    page = [f"{v:n}" for v in [1, 3, 5, 7, 9, 13, 19]]
    for i in range(6):
        item = contents.tocTree.topLevelItem(i)
        assert item is not None
        assert item.text(contents.C_WORDS) == words[i]
        assert item.text(contents.C_PAGES) == pages[i]
        assert item.text(contents.C_PAGE) == page[i]

    # Change Settings
    contents.poValue.setValue(7)
    contents.wpValue.setValue(50)
    words = [f"{v:n}" for v in [40, 176, 92, 6, 1071, 1615, 0]]
    pages = [f"{v:n}" for v in [2, 4, 2, 2, 22, 34, 0]]
    page = ["i", "iii"] + [f"{v:n}" for v in [1, 3, 5, 27, 61]]
    for i in range(6):
        item = contents.tocTree.topLevelItem(i)
        assert item is not None
        assert item.text(contents.C_WORDS) == words[i]
        assert item.text(contents.C_PAGES) == pages[i]
        assert item.text(contents.C_PAGE) == page[i]

    # Turn off use odd pages
    contents.dblValue.setChecked(False)
    contents.poValue.setValue(0)
    contents.wpValue.setValue(100)
    words = [f"{v:n}" for v in [40, 176, 92, 6, 1071, 1615, 0]]
    pages = [f"{v:n}" for v in [1, 2, 1, 1, 11, 17, 0]]
    page = [f"{v:n}" for v in [1, 2, 4, 5, 6, 17, 34]]
    for i in range(6):
        item = contents.tocTree.topLevelItem(i)
        assert item is not None
        assert item.text(contents.C_WORDS) == words[i]
        assert item.text(contents.C_PAGES) == pages[i]
        assert item.text(contents.C_PAGE) == page[i]

    # Revert to Overview page
    details.sidebar.button(details.PAGE_OVERVIEW).click()
    assert details.mainStack.currentIndex() == 0

    # qtbot.stop()
    details.close()
