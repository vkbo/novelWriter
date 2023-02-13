"""
novelWriter – GUI Build Manuscript
==================================
GUI classes for the Manuscript build tool

File History:
Created: 2023-02-13 [2.1-a0]

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

from PyQt5.QtWidgets import QDialog, QHBoxLayout, QTabWidget, QWidget

from novelwriter.custom import VerticalTabBar

logger = logging.getLogger(__name__)


class GuiBuildManuscript(QDialog):

    def __init__(self, mainGui):
        super().__init__(parent=mainGui)

        self.mainConf   = novelwriter.CONFIG
        self.mainGui    = mainGui
        self.theProject = mainGui.theProject

        self.setWindowTitle(self.tr("Build Manuscript"))
        self.setMinimumWidth(self.mainConf.pxInt(700))
        self.setMinimumHeight(self.mainConf.pxInt(600))

        # Optiuons Area
        # =============

        self.optTabBar = VerticalTabBar(self)
        self.optTabBar.setExpanding(False)

        self.optTabBox = QTabWidget(self)
        self.optTabBox.setTabBar(self.optTabBar)
        self.optTabBox.setTabPosition(QTabWidget.West)

        # Create Tabs
        self.optTabSelect = GuiBuildSelectionTab(self)
        self.optTabFormat = GuiBuildFormattingTab(self)

        # Add Tabs
        self.optTabBox.addTab(self.optTabSelect, self.tr("Selection"))
        self.optTabBox.addTab(self.optTabFormat, self.tr("Formatting"))

        # Assemble
        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.optTabBox)

        self.setLayout(self.outerBox)

        return

# END Class GuiBuildManuscript


class GuiBuildSelectionTab(QWidget):

    def __init__(self, buildMain):
        super().__init__(parent=buildMain)

        return

# END Class GuiBuildSelectionTab


class GuiBuildFormattingTab(QWidget):

    def __init__(self, buildMain):
        super().__init__(parent=buildMain)

        return

# END Class GuiBuildFormattingTab
