"""
novelWriter – GUI Build Manuscript
==================================
GUI classes for the Manuscript build tool

File History:
Created: 2023-02-13 [2.1b1]

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

import logging
import novelwriter

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (
    QAbstractItemView, QDialog, QHBoxLayout, QStackedWidget, QTreeWidget,
    QWidget
)

from novelwriter.extensions.pagedsidebar import NPagedSideBar

logger = logging.getLogger(__name__)


class GuiBuildManuscript(QDialog):

    OPT_FILTERS  = 1
    OPT_HEADINGS = 2
    OPT_FORMAT   = 3
    OPT_CONTENT  = 4
    BLD_HTML     = 5
    BLD_MARKDOWN = 6
    BLD_ODT      = 7

    def __init__(self, mainGui):
        super().__init__(parent=mainGui)

        self.mainConf   = novelwriter.CONFIG
        self.mainGui    = mainGui
        self.mainTheme  = mainGui.mainTheme
        self.theProject = mainGui.theProject

        self.setWindowTitle(self.tr("Build Manuscript"))
        self.setMinimumWidth(self.mainConf.pxInt(700))
        self.setMinimumHeight(self.mainConf.pxInt(600))

        # Style
        mPx = self.mainConf.pxInt(150)
        # tPx = int(self.mainTheme.fontPixelSize * 1.5)

        # Options SideBar
        # ===============

        self.optSideBar = NPagedSideBar(self)
        self.optSideBar.setMinimumWidth(mPx)
        self.optSideBar.setMaximumWidth(mPx)
        self.optSideBar.setLabelColor(self.mainTheme.helpText)

        self.optSideBar.addLabel(self.tr("Options"))
        self.optSideBar.addButton(self.tr("Filters"), self.OPT_FILTERS)
        self.optSideBar.addButton(self.tr("Headings"), self.OPT_HEADINGS)
        self.optSideBar.addButton(self.tr("Format"), self.OPT_FORMAT)
        self.optSideBar.addButton(self.tr("Content"), self.OPT_CONTENT)
        self.optSideBar.addSeparator()

        self.optSideBar.addLabel(self.tr("Build"))
        self.optSideBar.addButton(self.tr("HTML"), self.BLD_HTML)
        self.optSideBar.addButton(self.tr("Markdown"), self.BLD_MARKDOWN)
        self.optSideBar.addButton(self.tr("Open Document"), self.BLD_ODT)

        self.optSideBar.buttonClicked.connect(self._stackPageSelected)

        # Options Area
        # ============

        # Create Tabs
        self.optTabSelect = GuiBuildSelectionTab(self)
        self.optTabFormat = GuiBuildFormattingTab(self)

        # Add Tabs
        self.toolStack = QStackedWidget(self)
        self.toolStack.addWidget(self.optTabSelect)
        self.toolStack.addWidget(self.optTabFormat)

        # Assemble
        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.optSideBar)
        self.outerBox.addWidget(self.toolStack)

        self.setLayout(self.outerBox)

        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(int)
    def _stackPageSelected(self, pageId):
        """Process a user request to switch page.
        """
        if pageId == self.OPT_FILTERS:
            self.toolStack.setCurrentWidget(self.optTabSelect)
        elif pageId == self.OPT_FORMAT:
            self.toolStack.setCurrentWidget(self.optTabFormat)
        return

# END Class GuiBuildManuscript


class GuiBuildSelectionTab(QWidget):

    def __init__(self, buildMain):
        super().__init__(parent=buildMain)

        self.optTree = QTreeWidget(self)
        self.optTree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.optTree.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.optTree.setColumnCount(2)
        self.optTree.setHeaderLabels([
            self.tr("Setting"),
            self.tr("Value"),
        ])
        self.optTree.setRootIsDecorated(False)

        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.optTree)

        self.setLayout(self.outerBox)

        return

# END Class GuiBuildSelectionTab


class GuiBuildFormattingTab(QWidget):

    def __init__(self, buildMain):
        super().__init__(parent=buildMain)

        return

# END Class GuiBuildFormattingTab
