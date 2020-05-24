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

from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QTabWidget, QTabBar, QStyle,
    QStylePainter, QStyleOptionTab
)

logger = logging.getLogger(__name__)

class PagedDialog(QDialog):

    def __init__(self, theParent=None):
        QDialog.__init__(self, parent=theParent)

        self._outerBox  = QVBoxLayout()
        self._buttonBox = QHBoxLayout()
        self._tabBox    = QTabWidget()

        self._tabBar = VerticalTabBar(self)
        self._tabBox.setTabBar(self._tabBar)
        self._tabBox.setTabPosition(QTabWidget.West)
        self._tabBar.setExpanding(False)

        self._outerBox.addWidget(self._tabBox)
        self._outerBox.addLayout(self._buttonBox)
        self.setLayout(self._outerBox)

        # Default Margins
        qM = self._outerBox.contentsMargins()
        mL = qM.left()
        mR = qM.right()
        mT = qM.top()
        mB = qM.bottom()

        self.setContentsMargins(0, 0, 0, 0)
        self._outerBox.setContentsMargins(0, 0, 0, mB)
        self._buttonBox.setContentsMargins(mL, 0, mR, 0)
        self._outerBox.setSpacing(mT)

        return

    def addTab(self, tabWidget, tabLabel):
        """Forwards the adding of tabs to the QTabWidget.
        """
        self._tabBox.addTab(tabWidget, tabLabel)
        return

    def addControls(self, buttonBar):
        """Adds a button bar to the dialog.
        """
        self._buttonBox.addWidget(buttonBar)
        return

# END Class PagedDialog

class VerticalTabBar(QTabBar):

    def __init__(self, theParent=None):
        QTabBar.__init__(self, parent=theParent)
        return

    def tabSizeHint(self, theIndex):
        """Returns a transposed size hint for the rotated bar.
        """
        tSize = QTabBar.tabSizeHint(self, theIndex)
        tSize.transpose()
        return tSize

    def paintEvent(self, theEvent):
        """Custom implementation of the label painter that rotates the
        label 90 degrees.
        """
        pObj = QStylePainter(self)
        oObj = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(oObj, i)
            pObj.drawControl(QStyle.CE_TabBarTabShape, oObj)
            pObj.save()

            oSize = oObj.rect.size()
            oSize.transpose()
            oRect = QRect(QPoint(), oSize)
            oRect.moveCenter(oObj.rect.center())
            oObj.rect = oRect

            oCenter = self.tabRect(i).center()
            pObj.translate(oCenter)
            pObj.rotate(90)
            pObj.translate(-oCenter)
            pObj.drawControl(QStyle.CE_TabBarTabLabel, oObj)
            pObj.restore()

        return

# END Class VerticalTabBar
