"""
novelWriter – Custom Widget: Paged Dialog
=========================================
A custom dialog with tabs and a vertical tab bar

File History:
Created: 2020-05-17 [0.5.1]

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

from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QStyle, QStyleOptionTab, QStylePainter, QTabBar,
    QTabWidget, QVBoxLayout
)

from novelwriter import CONFIG


class NPagedDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._tabBar = NVerticalTabBar(self)
        self._tabBar.setExpanding(False)

        self._tabBox = QTabWidget(self)
        self._tabBox.setTabBar(self._tabBar)
        self._tabBox.setTabPosition(QTabWidget.West)

        self._buttonBox = QHBoxLayout()

        self._outerBox = QVBoxLayout()
        self._outerBox.addWidget(self._tabBox)
        self._outerBox.addLayout(self._buttonBox)

        # Default Margins
        thisStyle = self.style()
        mL = thisStyle.pixelMetric(QStyle.PM_LayoutLeftMargin)
        mR = thisStyle.pixelMetric(QStyle.PM_LayoutRightMargin)
        mT = thisStyle.pixelMetric(QStyle.PM_LayoutLeftMargin)
        mB = thisStyle.pixelMetric(QStyle.PM_LayoutBottomMargin)

        # Set Margins
        self.setContentsMargins(0, 0, 0, 0)
        self._outerBox.setContentsMargins(0, 0, 0, mB)
        self._buttonBox.setContentsMargins(mL, 0, mR, 0)
        self._outerBox.setSpacing(mT)

        self.setLayout(self._outerBox)

        return

    def addTab(self, widget, label):
        """Forward the adding of tabs to the QTabWidget.
        """
        self._tabBox.addTab(widget, label)
        return

    def addControls(self, buttonBar):
        """Add a button bar to the dialog.
        """
        self._buttonBox.addWidget(buttonBar)
        return

    def setCurrentWidget(self, widget):
        """Forward the changing of tab to the QTabWidget.
        """
        self._tabBox.setCurrentWidget(widget)
        return

# END Class NPagedDialog


class NVerticalTabBar(QTabBar):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._mW = CONFIG.pxInt(150)
        return

    def tabSizeHint(self, index):
        """Return a transposed size hint for the rotated bar.
        """
        tSize = super().tabSizeHint(index)
        tSize.transpose()
        tSize.setWidth(min(tSize.width(), self._mW))
        return tSize

    def paintEvent(self, event):
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

# END Class NVerticalTabBar
