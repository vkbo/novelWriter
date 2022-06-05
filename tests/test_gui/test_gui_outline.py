"""
novelWriter – Main GUI Outline Class Tester
===========================================

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

from PyQt5.QtWidgets import QTreeWidgetItem, QMessageBox

keyDelay = 2
typeDelay = 1
stepDelay = 20


@pytest.mark.gui
def testGuiOutline_Main(qtbot, monkeypatch, nwGUI, nwLipsum):
    """Test the outline view.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Yes)

    assert nwGUI.openProject(nwLipsum)
    nwGUI.mainConf.lastPath = nwLipsum

    nwGUI.rebuildIndex()
    nwGUI.mainStack.setCurrentIndex(nwGUI.idxOutlineView)

    outlineView = nwGUI.projView.outlineView
    outlineData = nwGUI.projView.outlineData

    assert outlineView.topLevelItemCount() > 0

    # Context Menu
    # outlineView._headerRightClick(QPoint(1, 1))
    # outlineView.headerMenu.actionMap[nwOutline.CCOUNT].activate(QAction.Trigger)
    # outlineView.headerMenu.close()
    # qtbot.mouseClick(outlineView, Qt.LeftButton)

    # outlineView._loadHeaderState()
    # assert not outlineView._colHidden[nwOutline.CCOUNT]

    # First Item
    outlineView.refreshTree()
    selItem = outlineView.topLevelItem(0)
    assert isinstance(selItem, QTreeWidgetItem)

    outlineView.setCurrentItem(selItem)
    assert outlineData.titleLabel.text() == "<b>Title</b>"
    assert outlineData.titleValue.text() == "Lorem Ipsum"
    assert outlineData.fileValue.text() == "Lorem Ipsum"
    assert outlineData.itemValue.text() == "Finished"

    assert outlineData.cCValue.text() == "230"
    assert outlineData.wCValue.text() == "40"
    assert outlineData.pCValue.text() == "3"

    # Scene One
    actItem = outlineView.topLevelItem(1)
    chpItem = actItem.child(0)
    selItem = chpItem.child(0)

    outlineView.setCurrentItem(selItem)
    tHandle, tLine = outlineView.getSelectedHandle()
    assert tHandle == "88243afbe5ed8"
    assert tLine == 0

    assert outlineData.titleLabel.text() == "<b>Scene</b>"
    assert outlineData.titleValue.text() == "Scene One"
    assert outlineData.fileValue.text() == "Scene One"
    assert outlineData.itemValue.text() == "Finished"

    # Click POV Link
    assert outlineData.povKeyValue.text() == "<a href='Bod'>Bod</a>"
    outlineData._tagClicked("#pov=Bod")
    assert nwGUI.docViewer.docHandle() == "4c4f28287af27"

    # Scene One, Section Two
    actItem = outlineView.topLevelItem(1)
    chpItem = actItem.child(0)
    scnItem = chpItem.child(0)
    selItem = scnItem.child(0)

    outlineView.setCurrentItem(selItem)
    tHandle, tLine = outlineView.getSelectedHandle()
    assert tHandle == "88243afbe5ed8"
    assert tLine == 12

    assert outlineData.titleLabel.text() == "<b>Section</b>"
    assert outlineData.titleValue.text() == "Scene One, Section Two"
    assert outlineData.fileValue.text() == "Scene One"
    assert outlineData.itemValue.text() == "Finished"

    outlineView._treeDoubleClick(selItem, 0)
    assert nwGUI.docEditor.docHandle() == "88243afbe5ed8"

    # qtbot.stopForInteraction()

# END Test testGuiOutline_Main
