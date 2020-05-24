# -*- coding: utf-8 -*-
"""novelWriter Addition QSwitch

 novelWriter – Addition QSwitch
================================
 A custom Qt switch button

 File History:
 Created: 2020-05-03 [0.4.5]

 The core code of this class is based on Stack Overflow example by
 Stefan Scherfke: https://stackoverflow.com/a/51825815/5825851

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

from PyQt5.QtCore import Qt, QSize, QRectF, QPropertyAnimation, pyqtProperty
from PyQt5.QtWidgets import QAbstractButton, QSizePolicy
from PyQt5.QtGui import QPainter

from nw.constants import nwUnicode

logger = logging.getLogger(__name__)

class QSwitch(QAbstractButton):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedWidth(40)
        self.setFixedHeight(20)
        self._offset = 10

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
            self.offset = 30
        else:
            self.offset = 10
        return

    ##
    #  Events
    ##

    def resizeEvent(self, theEvent):
        """Overload resize to ensure correct offset.
        """
        super().resizeEvent(theEvent)
        if self.isChecked():
            self.offset = 30
        else:
            self.offset = 10
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
            thumbText  = nwUnicode.U_MULT

        if self.isEnabled():
            trackOpacity = 1.0
        else:
            trackOpacity = 0.6
            trackBrush = qPalette.shadow()
            thumbBrush = qPalette.mid()
            textColor  = qPalette.shadow().color()

        qPaint.setBrush(trackBrush)
        qPaint.setOpacity(trackOpacity)
        qPaint.drawRoundedRect(0, 0, 40, 20, 10, 10)

        qPaint.setBrush(thumbBrush)
        qPaint.drawEllipse(self.offset - 8, 2, 16, 16)

        theFont = qPaint.font()
        theFont.setPixelSize(12)
        qPaint.setPen(textColor)
        qPaint.setFont(theFont)
        qPaint.drawText(
            QRectF(self.offset - 8, 2, 16, 16),
            Qt.AlignCenter, thumbText
        )

        return

    def mouseReleaseEvent(self, event):
        """Animate the switch on mouse release.
        """
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            doAnim = QPropertyAnimation(self, b'offset', self)
            doAnim.setDuration(120)
            doAnim.setStartValue(self.offset)
            if self.isChecked():
                doAnim.setEndValue(30)
            else:
                doAnim.setEndValue(10)
            doAnim.start()
        return

    def enterEvent(self, event):
        """Change the cursor when hovering the button.
        """
        self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(event)
        return

# END Class QSwitch
