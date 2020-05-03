# -*- coding: utf-8 -*-
"""novelWriter Addition QSwitch

 novelWriter – Addition QSwitch
================================
 A custom Qt switch button

 File History:
 Created: 2020-05-03 [0.4.5]

 This class is based on Stack Overflow code by Stefan Scherfke, based
 again on contribution by IMAN4K, published under license CC BY-SA 4.0.
 https://stackoverflow.com/a/51825815/5825851

 The above code has been modified to integrate with novelWriter, and
 re-released under compatible GPLv3 (see creativecommons.org).

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
 along with this program. If not, see https://www.gnu.org/licenses/.
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

        self._trackRadius = 10
        self._thumbRadius = 8

        self._margin = max(0, self._thumbRadius - self._trackRadius)
        self._baseOffset = max(self._thumbRadius, self._trackRadius)
        self._endOffset = {
            True: lambda: self.width() - self._baseOffset,
            False: lambda: self._baseOffset,
        }
        self._offset = self._baseOffset

        palette = self.palette()
        if self._thumbRadius > self._trackRadius:
            self._trackColor = {
                True: palette.highlight(),
                False: palette.dark(),
            }
            self._thumbColor = {
                True: palette.highlight(),
                False: palette.light(),
            }
            self._textColor = {
                True: palette.highlightedText().color(),
                False: palette.dark().color(),
            }
            self._thumbText = {
                True: '',
                False: '',
            }
            self._trackOpacity = 0.5
        else:
            self._thumbColor = {
                True: palette.highlightedText(),
                False: palette.light(),
            }
            self._trackColor = {
                True: palette.highlight(),
                False: palette.dark(),
            }
            self._textColor = {
                True: palette.highlight().color(),
                False: palette.dark().color(),
            }
            self._thumbText = {
                True: nwUnicode.U_CHECK,
                False: nwUnicode.U_MULT,
            }
            self._trackOpacity = 1.0

        return

    ##
    #  Properties
    ##

    @pyqtProperty(int)
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value
        self.update()
        return

    ##
    #  Getters and Setters
    ##

    def trackRadius(self):
        return self._trackRadius

    def setTrackRadius(self, theValue):
        if isinstance(theValue, int):
            if theValue > 0:
                self._trackRadius = theValue
                return
        raise ValueError("trackRadius must be an integer > 0")
        self.update()
        return

    def thumbRadius(self):
        return self._thumbRadius

    def setThumbRadius(self, theValue):
        if isinstance(theValue, int):
            if theValue > 0:
                self._thumbRadius = theValue
                return
        raise ValueError("thumbRadius must be an integer > 0")
        self.update()
        return

    def setChecked(self, checked):
        super().setChecked(checked)
        self.offset = self._endOffset[checked]()

    def sizeHint(self):
        return QSize(
            4 * self._trackRadius + 2 * self._margin,
            2 * self._trackRadius + 2 * self._margin,
        )

    ##
    #  Events
    ##

    def resizeEvent(self, event):
        """Overload resize to ensure correct offset.
        """
        super().resizeEvent(event)
        self.offset = self._endOffset[self.isChecked()]()
        return

    def paintEvent(self, event):
        """Drawing the switch itself.
        """
        qPaint = QPainter(self)
        qPaint.setRenderHint(QPainter.Antialiasing, True)
        qPaint.setPen(Qt.NoPen)
        trackOpacity = self._trackOpacity
        thumbOpacity = 1.0
        textOpacity = 1.0
        if self.isEnabled():
            trackBrush = self._trackColor[self.isChecked()]
            thumbBrush = self._thumbColor[self.isChecked()]
            textColor = self._textColor[self.isChecked()]
        else:
            trackOpacity *= 0.8
            trackBrush = self.palette().shadow()
            thumbBrush = self.palette().mid()
            textColor = self.palette().shadow().color()

        qPaint.setBrush(trackBrush)
        qPaint.setOpacity(trackOpacity)
        qPaint.drawRoundedRect(
            self._margin,
            self._margin,
            self.width() - 2*self._margin,
            self.height() - 2*self._margin,
            self._trackRadius,
            self._trackRadius,
        )
        qPaint.setBrush(thumbBrush)
        qPaint.setOpacity(thumbOpacity)
        qPaint.drawEllipse(
            self.offset - self._thumbRadius,
            self._baseOffset - self._thumbRadius,
            2*self._thumbRadius,
            2*self._thumbRadius,
        )
        qPaint.setPen(textColor)
        qPaint.setOpacity(textOpacity)
        theFont = qPaint.font()
        theFont.setPixelSize(1.5*self._thumbRadius)
        qPaint.setFont(theFont)
        qPaint.drawText(
            QRectF(
                self.offset - self._thumbRadius,
                self._baseOffset - self._thumbRadius,
                2*self._thumbRadius,
                2*self._thumbRadius,
            ),
            Qt.AlignCenter,
            self._thumbText[self.isChecked()],
        )
        return

    def mouseReleaseEvent(self, event):
        """Animate the switch.
        """
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            doAnim = QPropertyAnimation(self, b'offset', self)
            doAnim.setDuration(120)
            doAnim.setStartValue(self.offset)
            doAnim.setEndValue(self._endOffset[self.isChecked()]())
            doAnim.start()
        return

    def enterEvent(self, event):
        """Change the cursor when hovering the button.
        """
        self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(event)
        return

# END Class QSwitch
