"""
novelWriter – GUI Components Module
===================================
A module of various small GUI components

File History:
Created: 2020-05-17 [0.5.1] StatusLED
Created: 2022-11-17 [2.0]   NovelSelector

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

from PyQt5.QtGui import QPainter
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QAbstractButton, QComboBox

from novelwriter.enum import nwItemClass
from novelwriter.constants import nwLabels

logger = logging.getLogger(__name__)


class NovelSelector(QComboBox):

    novelSelectionChanged = pyqtSignal(str)

    def __init__(self, parent, project, mainGui):
        super().__init__(parent=parent)

        self._mainGui = mainGui
        self._project = project
        self._theme = mainGui.mainTheme
        self._blockSignal = False
        self._firstHandle = None

        self.currentIndexChanged.connect(self._indexChanged)

        return

    ##
    #  Properties
    ##

    @property
    def handle(self):
        return self.currentData()

    @property
    def firstHandle(self):
        return self._firstHandle

    ##
    #  Methods
    ##

    def setHandle(self, tHandle, blockSignal=True):
        """Set the currently selected handle.
        """
        self._blockSignal = blockSignal
        if tHandle is None:
            index = self.count() - 1
        else:
            index = self.findData(tHandle)
        if index >= 0:
            self.setCurrentIndex(index)
        self._blockSignal = False
        return

    def updateList(self, includeAll=False, prefix=None):
        """Rebuild the list of novel items.
        """
        self._blockSignal = True
        self._firstHandle = None
        self.clear()

        icon = self._theme.getIcon(nwLabels.CLASS_ICON[nwItemClass.NOVEL])
        handle = self.currentData()
        for tHandle, nwItem in self._project.tree.iterRoots(nwItemClass.NOVEL):
            if prefix:
                name = prefix.format(nwItem.itemName)
                self.addItem(name, tHandle)
            else:
                name = nwItem.itemName
                self.addItem(icon, nwItem.itemName, tHandle)
            if self._firstHandle is None:
                self._firstHandle = tHandle

        if includeAll:
            self.insertSeparator(self.count())
            self.addItem(icon, self.tr("All Novel Folders"), "")

        self.setHandle(handle)
        self.setEnabled(self.count() > 1)
        self._blockSignal = False

        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(int)
    def _indexChanged(self, index):
        """Re-emit the change of selected novel signal, unless blocked.
        """
        if not self._blockSignal:
            self.novelSelectionChanged.emit(self.currentData())
        return

# END Class NovelSelector


class StatusLED(QAbstractButton):

    S_NONE = 0
    S_BAD  = 1
    S_GOOD = 2

    def __init__(self, colNone, colGood, colBad, sW, sH, parent=None):
        super().__init__(parent=parent)

        self._colNone = colNone
        self._colGood = colGood
        self._colBad = colBad
        self._theCol = colNone

        self.setFixedWidth(sW)
        self.setFixedHeight(sH)

        return

    ##
    #  Setters
    ##

    def setState(self, theState):
        """Set the colour state.
        """
        if theState == self.S_GOOD:
            self._theCol = self._colGood
        elif theState == self.S_BAD:
            self._theCol = self._colBad
        else:
            self._theCol = self._colNone

        self.update()

        return

    ##
    #  Events
    ##

    def paintEvent(self, _):
        """Drawing the LED.
        """
        qPalette = self.palette()
        qPaint = QPainter(self)
        qPaint.setRenderHint(QPainter.Antialiasing, True)
        qPaint.setPen(qPalette.dark().color())
        qPaint.setBrush(self._theCol)
        qPaint.setOpacity(1.0)
        qPaint.drawEllipse(1, 1, self.width() - 2, self.height() - 2)
        return

# END Class StatusLED
