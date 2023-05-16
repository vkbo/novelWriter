"""
novelWriter – Custom Widget: Switch
===================================
A custom switch widget

File History:
Created: 2020-05-03 [0.4.5]

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

from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt, QRectF, QPropertyAnimation, pyqtProperty
from PyQt5.QtWidgets import QSizePolicy, QAbstractButton

from novelwriter import CONFIG
from novelwriter.constants import nwUnicode


class NSwitch(QAbstractButton):

    def __init__(self, parent=None, width=None, height=None):
        super().__init__(parent=parent)

        if width is None:
            self._xW = CONFIG.pxInt(40)
        else:
            self._xW = width

        if height is None:
            self._xH = CONFIG.pxInt(20)
        else:
            self._xH = height

        self._xR = int(self._xH*0.5)
        self._xT = int(self._xH*0.6)
        self._rB = int(CONFIG.guiScale*2)
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
    def offset(self, offset):
        self._offset = offset
        self.update()
        return

    ##
    #  Getters and Setters
    ##

    def setChecked(self, checked):
        """Overload setChecked to also alter the offset.
        """
        super().setChecked(checked)
        if checked:
            self.offset = self._xW - self._xR
        else:
            self.offset = self._xR
        return

    ##
    #  Events
    ##

    def resizeEvent(self, event):
        """Overload resize to ensure correct offset.
        """
        super().resizeEvent(event)
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
            textColor = qPalette.highlight().color()
            thumbText = nwUnicode.U_CHECK
        else:
            trackBrush = qPalette.dark()
            thumbBrush = qPalette.light()
            textColor = qPalette.dark().color()
            thumbText = nwUnicode.U_CROSS

        if self.isEnabled():
            trackOpacity = 1.0
        else:
            trackOpacity = 0.6
            trackBrush = qPalette.shadow()
            thumbBrush = qPalette.mid()
            textColor = qPalette.shadow().color()

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

# END Class NSwitch
