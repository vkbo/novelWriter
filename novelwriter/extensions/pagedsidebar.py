"""
novelWriter – Custom Widget: Paged SideBar
==========================================
A custom widget for making a sidebar for flipping through pages

File History:
Created: 2023-02-21 [2.1b1] NPagedSideBar
Created: 2023-02-21 [2.1b1] NPagedToolButton
Created: 2023-02-21 [2.1b1] NPagedToolLabel

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

from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtCore import QRectF, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QButtonGroup, QLabel, QSizePolicy, QStyle, QStyleOptionToolButton, QToolBar,
    QToolButton, QWidget
)


class NPagedSideBar(QToolBar):

    buttonClicked = pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent=parent)

        self._buttons = []
        self._actions = []
        self._labelCol = None
        self._spacerHeight = self.fontMetrics().height() // 2

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._group.buttonClicked.connect(self._buttonClicked)

        self.setMovable(False)
        self.setOrientation(Qt.Vertical)

        stretch = QWidget(self)
        stretch.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._stretchAction = self.addWidget(stretch)

        return

    def setLabelColor(self, color):
        """Set the text color for the labels."""
        if isinstance(color, list):
            self._labelCol = QColor(*color)
        elif isinstance(color, QColor):
            self._labelCol = color
        return

    def addSeparator(self):
        """Add a spacer widget."""
        spacer = QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        spacer.setFixedHeight(self._spacerHeight)
        self.insertWidget(self._stretchAction, spacer)
        return

    def addLabel(self, text):
        """Add a new label to the toolbar."""
        label = NPagedToolLabel(self, self._labelCol)
        label.setText(text)
        self.insertWidget(self._stretchAction, label)
        return

    def addButton(self, text, buttonId=-1):
        """Add a new button to the toolbar."""
        button = NPagedToolButton(self)
        button.setText(text)

        action = self.insertWidget(self._stretchAction, button)
        self._group.addButton(button, id=buttonId)

        self._buttons.append(button)
        self._actions.append(action)

        return action

    def setSelected(self, buttonId):
        """Set the selected button."""
        self._group.button(buttonId).setChecked(True)
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot("QAbstractButton*")
    def _buttonClicked(self, button):
        """A button was clicked in the group, emit its id."""
        buttonId = self._group.id(button)
        if buttonId != -1:
            self.buttonClicked.emit(buttonId)
        return

# END Class NPagedSideBar


class NPagedToolButton(QToolButton):

    __slots__ = ("_bH", "_tM", "_lM", "_cR")

    def __init__(self, parent):
        super().__init__(parent=parent)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCheckable(True)

        fH = self.fontMetrics().height()
        self._bH = round(fH * 1.7)
        self._tM = (self._bH - fH) // 2
        self._lM = self.style().pixelMetric(QStyle.PM_ButtonMargin)
        self._cR = self._lM // 2
        self.setFixedHeight(self._bH)

        return

    def paintEvent(self, event):
        """Overload the paint event to draw a simple, left aligned text
        label, with a highlight when selected and a transparent base
        colour when hovered.
        """
        opt = QStyleOptionToolButton()
        opt.initFrom(self)

        paint = QPainter(self)
        paint.setRenderHint(QPainter.Antialiasing, True)
        paint.setPen(Qt.NoPen)

        width = self.width()
        height = self.height()
        palette = self.palette()

        if opt.state & QStyle.State_MouseOver == QStyle.State_MouseOver:
            backCol = palette.base()
            paint.setBrush(backCol)
            paint.setOpacity(0.75)
            paint.drawRoundedRect(0, 0, width, height, self._cR, self._cR)

        if self.isChecked():
            backCol = palette.highlight()
            paint.setBrush(backCol)
            paint.setOpacity(0.5)
            paint.drawRoundedRect(0, 0, width, height, self._cR, self._cR)
            textCol = palette.highlightedText().color()
        else:
            textCol = palette.text().color()

        tW = width - 2*self._lM
        tH = height - 2*self._tM

        paint.setPen(textCol)
        paint.setOpacity(1.0)
        paint.drawText(QRectF(self._lM, self._tM, tW, tH), Qt.AlignLeft, self.text())

        return

# END Class NPagedToolButton


class NPagedToolLabel(QLabel):

    __slots__ = ("_bH", "_tM", "_lM", "_textCol")

    def __init__(self, parent, textColor=None):
        super().__init__(parent=parent)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        fH = self.fontMetrics().height()
        self._bH = round(fH * 1.7)
        self._tM = (self._bH - fH) // 2
        self._lM = self.style().pixelMetric(QStyle.PM_ButtonMargin)
        self.setFixedHeight(self._bH)

        self._textCol = textColor or self.palette().text().color()

        return

    def paintEvent(self, event):
        """Overload the paint event to draw a simple, left aligned text
        label that matches the button style.
        """
        paint = QPainter(self)
        paint.setRenderHint(QPainter.Antialiasing, True)
        paint.setPen(Qt.NoPen)

        width = self.width()
        height = self.height()

        tW = width - 2*self._lM
        tH = height - 2*self._tM

        paint.setPen(self._textCol)
        paint.setOpacity(1.0)
        paint.drawText(QRectF(self._lM, self._tM, tW, tH), Qt.AlignLeft, self.text())

        return

# END Class NPagedToolLabel
