"""
novelWriter – Main GUI Viewer Panel Class Tester
================================================

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

from PyQt5.QtGui import QIcon

from novelwriter import SHARED
from novelwriter.constants import nwLists
from novelwriter.core.item import NWItem
from novelwriter.dialogs.editlabel import GuiEditLabel

from tests.tools import C, buildTestProject


@pytest.mark.gui
def testGuiViewerPanel_BackRefs(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test the document viewer backreference panel."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    buildTestProject(nwGUI, projPath)
    projTree = nwGUI.projView.projTree
    projTree._getTreeItem(C.hChapterDir).setExpanded(True)
    viewPanel = nwGUI.docViewerPanel
    tabBackRefs = viewPanel.tabBackRefs

    nwGUI.openDocument(C.hSceneDoc)
    nwGUI.viewDocument(C.hSceneDoc)

    # Hide/Show
    nwGUI._toggleViewerPanelVisibility()
    assert viewPanel.isVisible() is False
    nwGUI._toggleViewerPanelVisibility()
    assert viewPanel.isVisible() is True

    # Initial State
    assert tabBackRefs.topLevelItemCount() == 0

    # Add Two Tags
    hJane = "0000000000010"
    nwGUI.docEditor.setPlainText("### New Scene\n\n@char: Jane, John\n\n")
    nwGUI.saveDocument()
    cursor = nwGUI.docEditor.textCursor()
    cursor.setPosition(22)
    nwGUI.docEditor._processTag(cursor, create=True)
    cursor.setPosition(28)
    nwGUI.docEditor._processTag(cursor, create=True)
    nwGUI.viewDocument(hJane)
    assert tabBackRefs.topLevelItemCount() == 1

    # Check Backreference
    item = tabBackRefs.topLevelItem(0)
    assert item.text(tabBackRefs.C_DOC) == "New Scene"
    assert item.text(tabBackRefs.C_TITLE) == "New Scene"

    # Update Title
    nwGUI.docEditor.setPlainText("### Scene One\n\n@char: Jane, John\n\n")
    nwGUI.saveDocument()
    item = tabBackRefs.topLevelItem(0)
    assert item.text(tabBackRefs.C_DOC) == "New Scene"
    assert item.text(tabBackRefs.C_TITLE) == "Scene One"

    # Update Label
    SHARED.project.tree[C.hSceneDoc].setName("First Scene")  # type: ignore
    projTree.renameTreeItem(C.hSceneDoc)
    item = tabBackRefs.topLevelItem(0)
    assert item.text(tabBackRefs.C_DOC) == "First Scene"
    assert item.text(tabBackRefs.C_TITLE) == "Scene One"

    # Clear Index
    SHARED.project.index.clearIndex()
    assert tabBackRefs.topLevelItemCount() == 0

    # Rebuild Index
    SHARED.project.index.rebuildIndex()
    assert tabBackRefs.topLevelItemCount() == 1

    # Test Update Theme
    tabBackRefs._editIcon = None
    tabBackRefs._viewIcon = None
    tabBackRefs.updateTheme()
    assert isinstance(tabBackRefs._editIcon, QIcon)
    assert isinstance(tabBackRefs._viewIcon, QIcon)

    # Click the Edit Button
    nwGUI.openDocument(C.hChapterDoc)
    assert nwGUI.docEditor.docHandle == C.hChapterDoc
    tabBackRefs._treeItemClicked(tabBackRefs.model().index(0, tabBackRefs.C_EDIT))
    assert nwGUI.docEditor.docHandle == C.hSceneDoc

    # Click the View Button
    assert nwGUI.docViewer.docHandle == hJane
    tabBackRefs._treeItemClicked(tabBackRefs.model().index(0, tabBackRefs.C_VIEW))
    assert nwGUI.docViewer.docHandle == C.hSceneDoc

    # Double-Click
    nwGUI.viewDocument(hJane)
    assert nwGUI.docViewer.docHandle == hJane
    tabBackRefs._treeItemDoubleClicked(tabBackRefs.model().index(0, tabBackRefs.C_DOC))
    assert nwGUI.docViewer.docHandle == C.hSceneDoc

    # qtbot.stop()


@pytest.mark.gui
def testGuiViewerPanel_Tags(qtbot, monkeypatch, caplog, nwGUI, projPath, mockRnd):
    """Test the document viewer tags panels."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    buildTestProject(nwGUI, projPath)
    projTree = nwGUI.projView.projTree
    projTree._getTreeItem(C.hChapterDir).setExpanded(True)
    viewPanel = nwGUI.docViewerPanel

    nwGUI.openDocument(C.hSceneDoc)
    nwGUI.viewDocument(C.hSceneDoc)

    assert len(viewPanel.kwTabs) == len(nwLists.USER_CLASSES)
    assert len(viewPanel.idTabs) == len(nwLists.USER_CLASSES)

    # Add Two Tags
    hJane = "0000000000010"
    hJohn = "0000000000011"
    nwGUI.docEditor.setPlainText("### New Scene\n\n@char: Jane, John\n\n")
    nwGUI.saveDocument()
    cursor = nwGUI.docEditor.textCursor()
    cursor.setPosition(22)
    nwGUI.docEditor._processTag(cursor, create=True)
    cursor.setPosition(28)
    nwGUI.docEditor._processTag(cursor, create=True)

    # Check Panel Tab Visibility
    assert viewPanel.mainTabs.isTabVisible(viewPanel.idTabs["CHARACTER"]) is True
    assert viewPanel.mainTabs.isTabVisible(viewPanel.idTabs["PLOT"]) is False
    assert viewPanel.mainTabs.isTabVisible(viewPanel.idTabs["WORLD"]) is False
    assert viewPanel.mainTabs.isTabVisible(viewPanel.idTabs["TIMELINE"]) is False
    assert viewPanel.mainTabs.isTabVisible(viewPanel.idTabs["OBJECT"]) is False
    assert viewPanel.mainTabs.isTabVisible(viewPanel.idTabs["ENTITY"]) is False
    assert viewPanel.mainTabs.isTabVisible(viewPanel.idTabs["CUSTOM"]) is False

    # Check Character Tab
    charTab = viewPanel.kwTabs["CHARACTER"]
    viewPanel.mainTabs.setCurrentIndex(viewPanel.idTabs["CHARACTER"])
    assert charTab.topLevelItemCount() == 2
    item = charTab.topLevelItem(0)
    assert item.text(charTab.C_NAME) == "Jane"
    assert item.text(charTab.C_DOC) == "Jane"
    assert item.text(charTab.C_TITLE) == "Jane"
    item = charTab.topLevelItem(1)
    assert item.text(charTab.C_NAME) == "John"
    assert item.text(charTab.C_DOC) == "John"
    assert item.text(charTab.C_TITLE) == "John"

    # Edit Jane
    nwGUI.openDocument(hJane)
    nwGUI.docEditor.setPlainText("# Jane Smith\n\n@tag: Janey\n\n")
    nwGUI.saveDocument()
    SHARED.project.tree[hJane].setName("Awesome Jane")  # type: ignore
    projTree.renameTreeItem(hJane)
    item = charTab.topLevelItem(0)
    assert item.text(charTab.C_NAME) == "Janey"
    assert item.text(charTab.C_DOC) == "Awesome Jane"
    assert item.text(charTab.C_TITLE) == "Jane Smith"

    # Clear Index
    SHARED.project.index.clearIndex()
    assert charTab.topLevelItemCount() == 0

    # Rebuild Index
    SHARED.project.index.rebuildIndex()
    assert charTab.topLevelItemCount() == 2

    # Test Update Theme
    charTab._classIcon = None
    charTab._editIcon = None
    charTab._viewIcon = None
    charTab.updateTheme()
    assert isinstance(charTab._classIcon, QIcon)
    assert isinstance(charTab._editIcon, QIcon)
    assert isinstance(charTab._viewIcon, QIcon)

    # Remove Non-Existing Tag
    caplog.clear()
    viewPanel.updateChangedTags(["foo"], ["bar"])
    assert charTab.topLevelItemCount() == 2
    assert "Could not remove tag" in caplog.text

    # View/Edit John
    assert nwGUI.docEditor.docHandle == hJane
    charTab._treeItemClicked(charTab.model().index(1, charTab.C_EDIT))
    assert nwGUI.docEditor.docHandle == hJohn
    assert nwGUI.docViewer.docHandle == C.hSceneDoc
    charTab._treeItemClicked(charTab.model().index(1, charTab.C_VIEW))
    assert nwGUI.docViewer.docHandle == hJohn
    charTab._treeItemDoubleClicked(charTab.model().index(0, charTab.C_NAME))
    assert nwGUI.docViewer.docHandle == hJane

    # Hide Inactive Tags
    viewPanel.aInactive.setChecked(True)
    assert charTab.topLevelItemCount() == 2

    nwJohn = SHARED.project.tree[hJohn]
    assert isinstance(nwJohn, NWItem)
    nwJohn.setActive(False)
    projTree.setTreeItemValues(hJohn)
    projTree._alertTreeChange(hJohn, flush=False)
    assert charTab.topLevelItemCount() == 1

    # qtbot.stop()
