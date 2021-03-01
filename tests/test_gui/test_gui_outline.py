# -*- coding: utf-8 -*-
"""
novelWriter – Main GUI Outline Class Tester
===========================================

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

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QAction, QTreeWidgetItem, QMessageBox

from nw.constants import nwOutline

keyDelay = 2
typeDelay = 1
stepDelay = 20

@pytest.mark.gui
def testGuiOutline_Main(qtbot, monkeypatch, nwGUI, nwLipsum):
    """Test the outline view.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.Yes)

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
    assert not nwGUI.projView.colHidden[nwOutline.CCOUNT]

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
    assert nwGUI.projMeta.titleLabel.text() == "<b>Scene</b>"
    assert nwGUI.projMeta.titleValue.text() == "Scene One"
    assert nwGUI.projMeta.fileValue.text() == "Scene One"
    assert nwGUI.projMeta.itemValue.text() == "Finished"

    # Click POV Link
    assert nwGUI.projMeta.povKeyValue.text() == "<a href='#pov=Bod'>Bod</a>"
    nwGUI.projMeta._tagClicked("#pov=Bod")
    assert nwGUI.docViewer.theHandle == "4c4f28287af27"

    # qtbot.stopForInteraction()

# END Test testGuiOutline_Main
