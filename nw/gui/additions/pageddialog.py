# -*- coding: utf-8 -*-
"""novelWriter Paged Dialog

 novelWriter – Paged Dialog
============================
 A custom QDialog with a built-in QTabWidget and vertical tabs.

 File History:
 Created: 2020-05-17 [0.5.1]

 This file is a part of novelWriter
 Copyright 2020, Veronica Berglyd Olsen

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
import nw

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QTabWidget
)

from nw.constants import nwUnicode

logger = logging.getLogger(__name__)

class PagedDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._outerBox = QVBoxLayout()
        self._innerBox = QHBoxLayout()
        self._navBox   = QVBoxLayout()
        self._tabBox   = QTabWidget()

        self._outerBox.addLayout(self._innerBox)
        self._innerBox.addLayout(self._navBox)
        self._innerBox.addWidget(self._tabBox)
        self.setLayout(self._outerBox)

        return

    def addPage(self, tabWidget, tabLabel):
        self._tabBox.addTab(tabWidget, tabLabel)
        return

    def addControls(self, buttonBar):
        self._outerBox.addWidget(buttonBar)
        return

# END Class PagedDialog
