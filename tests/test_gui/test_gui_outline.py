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

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QAction, QTreeWidgetItem, QMessageBox

from novelwriter.enum import nwOutline

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
    nwGUI.mainTabs.setCurrentIndex(nwGUI.idxTabProj)

    assert nwGUI.projView.topLevelItemCount() > 0

    # Context Menu
    nwGUI.projView._headerRightClick(QPoint(1, 1))
    nwGUI.projView.headerMenu.actionMap[nwOutline.CCOUNT].activate(QAction.Trigger)
    nwGUI.projView.headerMenu.close()
    qtbot.mouseClick(nwGUI.projView, Qt.LeftButton)

    nwGUI.projView._loadHeaderState()
    assert not nwGUI.projView._colHidden[nwOutline.CCOUNT]

    # First Item
    nwGUI.rebuildOutline()
    selItem = nwGUI.projView.topLevelItem(0)
    assert isinstance(selItem, QTreeWidgetItem)

    nwGUI.projView.setCurrentItem(selItem)
    assert nwGUI.projMeta.titleLabel.text() == "<b>Title</b>"
    assert nwGUI.projMeta.titleValue.text() == "Lorem Ipsum"
    assert nwGUI.projMeta.fileValue.text() == "Lorem Ipsum"
    assert nwGUI.projMeta.itemValue.text() == "Finished"

    assert nwGUI.projMeta.cCValue.text() == "230"
    assert nwGUI.projMeta.wCValue.text() == "40"
    assert nwGUI.projMeta.pCValue.text() == "3"

    # Scene One
    actItem = nwGUI.projView.topLevelItem(1)
    chpItem = actItem.child(0)
    selItem = chpItem.child(0)

    nwGUI.projView.setCurrentItem(selItem)
    tHandle, tLine = nwGUI.projView.getSelectedHandle()
    assert tHandle == "88243afbe5ed8"
    assert tLine == 0

    assert nwGUI.projMeta.titleLabel.text() == "<b>Scene</b>"
    assert nwGUI.projMeta.titleValue.text() == "Scene One"
    assert nwGUI.projMeta.fileValue.text() == "Scene One"
    assert nwGUI.projMeta.itemValue.text() == "Finished"

    # Click POV Link
    assert nwGUI.projMeta.povKeyValue.text() == "<a href='#pov=Bod'>Bod</a>"
    nwGUI.projMeta._tagClicked("#pov=Bod")
    assert nwGUI.docViewer.docHandle() == "4c4f28287af27"

    # Scene One, Section Two
    actItem = nwGUI.projView.topLevelItem(1)
    chpItem = actItem.child(0)
    scnItem = chpItem.child(0)
    selItem = scnItem.child(0)

    nwGUI.projView.setCurrentItem(selItem)
    tHandle, tLine = nwGUI.projView.getSelectedHandle()
    assert tHandle == "88243afbe5ed8"
    assert tLine == 12

    assert nwGUI.projMeta.titleLabel.text() == "<b>Section</b>"
    assert nwGUI.projMeta.titleValue.text() == "Scene One, Section Two"
    assert nwGUI.projMeta.fileValue.text() == "Scene One"
    assert nwGUI.projMeta.itemValue.text() == "Finished"

    nwGUI.projView._treeDoubleClick(selItem, 0)
    assert nwGUI.docEditor.docHandle() == "88243afbe5ed8"

    # qtbot.stopForInteraction()

# END Test testGuiOutline_Main
