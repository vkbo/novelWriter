# -*- coding: utf-8 -*-
"""
novelWriter – Custom Widgets and Layouts
========================================
Various custom widget and layout classes

File History:
Created: 2020-05-03 [0.4.5] QConfigLayout
Created: 2020-05-03 [0.4.5] QSwitch
Created: 2020-05-17 [0.5.1] PagedDialog

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

import nw
import logging

from PyQt5.QtGui import QColor, QPalette, QPainter
from PyQt5.QtCore import (
    Qt, QRect, QPoint, QRectF, QPropertyAnimation, pyqtProperty
)
from PyQt5.QtWidgets import (
    QGridLayout, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy,
    QAbstractButton, QDialog, QTabWidget, QTabBar, QStyle, QStylePainter,
    QStyleOptionTab, QLineEdit
)

from nw.constants import nwUnicode

logger = logging.getLogger(__name__)

# =============================================================================================== #
#  Config Form Layout
# =============================================================================================== #

class QConfigLayout(QGridLayout):

    def __init__(self):
        super().__init__()

        self._nextRow = 0
        self._helpCol = QColor(0, 0, 0)
        self._fontScale = 0.9

        self._itemMap = {}

        wSp = nw.CONFIG.pxInt(8)
        self.setHorizontalSpacing(wSp)
        self.setVerticalSpacing(wSp)
        self.setColumnStretch(0, 1)

        return

    ##
    #  Getters and Setters
    ##

    def setHelpTextStyle(self, helpCol, fontScale=0.9):
        """Set the text color for the help text.
        """
        if isinstance(helpCol, QColor):
            self._helpCol = helpCol
        else:
            self._helpCol = QColor(*helpCol)
        self._fontScale = fontScale
        return

    def setHelpText(self, intRow, theText):
        """Set the text for the help label.
        """
        if intRow in self._itemMap:
            self._itemMap[intRow]["help"].setText(theText)
        return

    def setLabelText(self, intRow, theText):
        """Set the text for the main label.
        """
        if intRow in self._itemMap:
            self._itemMap[intRow]["label"].setText(theText)
        return

    ##
    #  Class Methods
    ##

    def addGroupLabel(self, theLabel):
        """Adds a text label to separate groups of settings.
        """
        if isinstance(theLabel, QLabel):
            qLabel = theLabel
        elif isinstance(theLabel, str):
            qLabel = QLabel("<b>%s</b>" % theLabel)
        else:
            qLabel = None
            raise ValueError("theLabel must be a QLabel")

        hM = nw.CONFIG.pxInt(4)
        qLabel.setContentsMargins(0, hM, 0, hM)
        self.addWidget(qLabel, self._nextRow, 0, 1, 2, Qt.AlignLeft)

        self.setRowStretch(self._nextRow, 0)
        self.setRowStretch(self._nextRow + 1, 1)

        self._nextRow += 1

        return

    def addRow(self, theLabel, theWidget, helpText=None, theUnit=None, theButton=None):
        """Add a label and a widget as a new row of the grid.
        """
        thisEntry = {
            "label"  : None,
            "help"   : None,
            "widget" : None,
        }

        if isinstance(theLabel, QLabel):
            qLabel = theLabel
        elif isinstance(theLabel, str):
            qLabel = QLabel(theLabel)
        else:
            qLabel = None
            raise ValueError("theLabel must be a QLabel")

        if isinstance(theWidget, QWidget):
            qWidget = theWidget
        else:
            qWidget = None
            raise ValueError("theWidget must be a QWidget")

        wSp = nw.CONFIG.pxInt(8)
        qLabel.setIndent(wSp)
        if helpText is not None:
            qHelp = QHelpLabel(str(helpText), self._helpCol, self._fontScale)
            qHelp.setIndent(wSp)

            labelBox = QVBoxLayout()
            labelBox.addWidget(qLabel)
            labelBox.addWidget(qHelp)
            labelBox.setSpacing(0)
            labelBox.addStretch(1)

            thisEntry["help"] = qHelp
            self.addLayout(labelBox, self._nextRow, 0, 1, 1, Qt.AlignLeft | Qt.AlignTop)

        else:
            self.addWidget(qLabel, self._nextRow, 0, 1, 1, Qt.AlignLeft | Qt.AlignTop)

        if theUnit is not None:
            controlBox = QHBoxLayout()
            controlBox.addWidget(qWidget, 0, Qt.AlignVCenter)
            controlBox.addWidget(QLabel(theUnit), 0, Qt.AlignVCenter)
            controlBox.setSpacing(wSp)
            self.addLayout(controlBox, self._nextRow, 1, 1, 1, Qt.AlignRight | Qt.AlignTop)

        elif theButton is not None:
            controlBox = QHBoxLayout()
            controlBox.addWidget(qWidget, 0, Qt.AlignVCenter)
            controlBox.addWidget(theButton, 0, Qt.AlignVCenter)
            controlBox.setSpacing(wSp)
            self.addLayout(controlBox, self._nextRow, 1, 1, 1, Qt.AlignRight | Qt.AlignTop)

        else:
            if isinstance(theWidget, QLineEdit):
                qLayout = QHBoxLayout()
                qLayout.addWidget(theWidget)
                self.addLayout(qLayout, self._nextRow, 1, 1, 1, Qt.AlignRight | Qt.AlignTop)
            else:
                self.addWidget(qWidget, self._nextRow, 1, 1, 1, Qt.AlignRight | Qt.AlignTop)

        qLabel.setBuddy(qWidget)

        self.setRowStretch(self._nextRow, 0)
        self.setRowStretch(self._nextRow+1, 1)

        thisEntry["label"] = qLabel
        thisEntry["widget"] = qWidget

        self._itemMap[self._nextRow] = thisEntry

        self._nextRow += 1

        return self._nextRow - 1

# END Class QConfigLayout

class QHelpLabel(QLabel):

    def __init__(self, theText, textCol, fontSize=0.9):
        QLabel.__init__(self, theText)

        if isinstance(textCol, QColor):
            qCol = textCol
        else:
            qCol = QColor(*textCol)

        lblCol = self.palette()
        lblCol.setColor(QPalette.WindowText, qCol)
        self.setPalette(lblCol)

        lblFont = self.font()
        lblFont.setPointSizeF(fontSize*lblFont.pointSizeF())
        self.setFont(lblFont)

        self.setWordWrap(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return

# END Class QHelpLabel

# =============================================================================================== #
#  Switch Widget
# =============================================================================================== #

class QSwitch(QAbstractButton):

    def __init__(self, parent=None, width=None, height=None):
        super().__init__(parent=parent)

        if width is None:
            self._xW = nw.CONFIG.pxInt(40)
        else:
            self._xW = width

        if height is None:
            self._xH = nw.CONFIG.pxInt(20)
        else:
            self._xH = height

        self._xR = int(self._xH*0.5)
        self._xT = int(self._xH*0.6)
        self._rB = int(nw.CONFIG.guiScale*2)
        self._rH = self._xH - 2*self._rB
        self._rR = self._xR - self._rB

        self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedWidth(self._xW)
        self.setFixedHeight(self._xH)
        self._offset = self._xR

        return

    ##
    #  Properties
    ##

    @pyqtProperty(int)
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, theOffset):
        self._offset = theOffset
        self.update()
        return

    ##
    #  Getters and Setters
    ##

    def setChecked(self, isChecked):
        """Overload setChecked to also alter the offset.
        """
        super().setChecked(isChecked)
        if isChecked:
            self.offset = self._xW - self._xR
        else:
            self.offset = self._xR
        return

    ##
    #  Events
    ##

    def resizeEvent(self, theEvent):
        """Overload resize to ensure correct offset.
        """
        super().resizeEvent(theEvent)
        if self.isChecked():
            self.offset = self._xW - self._xR
        else:
            self.offset = self._xR
        return

    def paintEvent(self, event):
        """Drawing the switch itself.
        """
        qPaint = QPainter(self)
        qPaint.setRenderHint(QPainter.Antialiasing, True)
        qPaint.setPen(Qt.NoPen)

        qPalette = self.palette()
        if self.isChecked():
            trackBrush = qPalette.highlight()
            thumbBrush = qPalette.highlightedText()
            textColor  = qPalette.highlight().color()
            thumbText  = nwUnicode.U_CHECK
        else:
            trackBrush = qPalette.dark()
            thumbBrush = qPalette.light()
            textColor  = qPalette.dark().color()
            thumbText  = nwUnicode.U_CROSS

        if self.isEnabled():
            trackOpacity = 1.0
        else:
            trackOpacity = 0.6
            trackBrush = qPalette.shadow()
            thumbBrush = qPalette.mid()
            textColor  = qPalette.shadow().color()

        qPaint.setBrush(trackBrush)
        qPaint.setOpacity(trackOpacity)
        qPaint.drawRoundedRect(0, 0, self._xW, self._xH, self._xR, self._xR)

        qPaint.setBrush(thumbBrush)
        qPaint.drawEllipse(self.offset - self._rR, self._rB, self._rH, self._rH)

        theFont = qPaint.font()
        theFont.setPixelSize(self._xT)
        qPaint.setPen(textColor)
        qPaint.setFont(theFont)
        qPaint.drawText(
            QRectF(self.offset - self._rR, self._rB, self._rH, self._rH),
            Qt.AlignCenter, thumbText
        )

        return

    def mouseReleaseEvent(self, event):
        """Animate the switch on mouse release.
        """
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            doAnim = QPropertyAnimation(self, b"offset", self)
            doAnim.setDuration(120)
            doAnim.setStartValue(self.offset)
            if self.isChecked():
                doAnim.setEndValue(self._xW - self._xR)
            else:
                doAnim.setEndValue(self._xR)
            doAnim.start()
        return

    def enterEvent(self, event):
        """Change the cursor when hovering the button.
        """
        self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(event)
        return

# END Class QSwitch

# =============================================================================================== #
#  Paged Dialog w/Custom TabWidget
# =============================================================================================== #

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
        self._mW = nw.CONFIG.pxInt(150)
        return

    def tabSizeHint(self, theIndex):
        """Returns a transposed size hint for the rotated bar.
        """
        tSize = QTabBar.tabSizeHint(self, theIndex)
        tSize.transpose()
        tSize.setWidth(min(tSize.width(), self._mW))
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
