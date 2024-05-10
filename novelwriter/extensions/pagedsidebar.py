"""
novelWriter – Custom Widget: Paged SideBar
==========================================

File History:
Created: 2023-02-21 [2.1b1] NPagedSideBar
Created: 2023-02-21 [2.1b1] NPagedToolButton
Created: 2023-02-21 [2.1b1] NPagedToolLabel

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

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
from __future__ import annotations

from PyQt5.QtCore import QPoint, QRectF, QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QPainter, QPaintEvent, QPolygon
from PyQt5.QtWidgets import (
    QAbstractButton, QAction, QButtonGroup, QLabel, QStyle,
    QStyleOptionToolButton, QToolBar, QToolButton, QWidget
)

from novelwriter.types import (
    QtAlignLeft, QtMouseOver, QtNoBrush, QtNoPen, QtPaintAnitAlias,
    QtSizeExpanding, QtSizeFixed
)


class NPagedSideBar(QToolBar):
    """Extensions: Paged Side Bar

    A side bar widget that holds buttons that mimic tabs. It is designed
    to be used in combination with a QStackedWidget for options panels.
    """

    buttonClicked = pyqtSignal(int)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        self._labelCol = None
        self._spacerHeight = self.fontMetrics().height() // 2
        self._buttons: dict[int, _NPagedToolButton] = {}

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._group.buttonClicked.connect(self._buttonClicked)

        self.setMovable(False)
        self.setOrientation(Qt.Orientation.Vertical)

        stretch = QWidget(self)
        stretch.setSizePolicy(QtSizeExpanding, QtSizeExpanding)
        self._stretchAction = self.addWidget(stretch)

        return

    def button(self, buttonId: int) -> _NPagedToolButton:
        """Return a specific button."""
        return self._buttons[buttonId]

    def setLabelColor(self, color: QColor) -> None:
        """Set the text color for the labels."""
        self._labelCol = color
        return

    def addLabel(self, text: str) -> None:
        """Add a new label to the toolbar."""
        label = _NPagedToolLabel(self, self._labelCol)
        label.setText(text)
        self.insertWidget(self._stretchAction, label)
        return

    def addButton(self, text: str, buttonId: int = -1) -> QAction:
        """Add a new button to the toolbar."""
        button = _NPagedToolButton(self)
        button.setText(text)

        action = self.insertWidget(self._stretchAction, button)
        self._group.addButton(button, id=buttonId)

        self._buttons[buttonId] = button

        return action

    def setSelected(self, buttonId: int) -> None:
        """Set the selected button."""
        self._group.button(buttonId).setChecked(True)
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot("QAbstractButton*")
    def _buttonClicked(self, button: QAbstractButton) -> None:
        """A button was clicked in the group, emit its id."""
        buttonId = self._group.id(button)
        if buttonId != -1:
            self.buttonClicked.emit(buttonId)
        return


class _NPagedToolButton(QToolButton):

    __slots__ = ("_bH", "_tM", "_lM", "_cR", "_aH")

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        self.setSizePolicy(QtSizeExpanding, QtSizeFixed)
        self.setCheckable(True)

        fH = self.fontMetrics().height()
        self._bH = round(fH * 1.7)
        self._tM = (self._bH - fH)//2
        self._lM = 3*self.style().pixelMetric(QStyle.PixelMetric.PM_ButtonMargin)//2
        self._cR = self._lM//2
        self._aH = 2*fH//7
        self.setFixedHeight(self._bH)

        return

    def sizeHint(self) -> QSize:
        """Return a size hint that includes the arrow."""
        return super().sizeHint() + QSize(4*self._aH, 0)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Overload the paint event to draw a simple, left aligned text
        label, with a highlight when selected and a transparent base
        colour when hovered.
        """
        opt = QStyleOptionToolButton()
        opt.initFrom(self)

        paint = QPainter(self)
        paint.setRenderHint(QtPaintAnitAlias, True)
        paint.setPen(QtNoPen)
        paint.setBrush(QtNoBrush)

        width = self.width()
        height = self.height()
        palette = self.palette()

        if opt.state & QtMouseOver == QtMouseOver:
            backCol = palette.base()
            paint.setBrush(backCol)
            paint.setOpacity(0.75)
            paint.drawRoundedRect(0, 0, width, height, self._cR, self._cR)

        if self.isChecked():
            backCol = palette.highlight()
            paint.setBrush(backCol)
            paint.setOpacity(0.35)
            paint.drawRoundedRect(0, 0, width, height, self._cR, self._cR)
            textCol = palette.highlightedText().color()
        else:
            textCol = palette.text().color()

        tW = width - 2*self._lM
        tH = height - 2*self._tM

        paint.setPen(textCol)
        paint.setOpacity(1.0)
        paint.drawText(QRectF(self._lM, self._tM, tW, tH), QtAlignLeft, self.text())

        tC = self.height()//2
        tW = self.width() - self._aH - self._lM
        if self.isChecked():
            paint.setBrush(textCol)
        paint.drawPolygon(QPolygon([
            QPoint(tW, tC - self._aH),
            QPoint(tW + self._aH, tC),
            QPoint(tW, tC + self._aH),
        ]))

        return


class _NPagedToolLabel(QLabel):

    __slots__ = ("_bH", "_tM", "_lM", "_textCol")

    def __init__(self, parent: QWidget, textColor: QColor | None = None) -> None:
        super().__init__(parent=parent)

        self.setSizePolicy(QtSizeExpanding, QtSizeFixed)

        fH = self.fontMetrics().height()
        self._bH = round(fH * 1.7)
        self._tM = (self._bH - fH)//2
        self._lM = self.style().pixelMetric(QStyle.PixelMetric.PM_ButtonMargin)//2
        self.setFixedHeight(self._bH)

        self._textCol = textColor or self.palette().text().color()

        return

    def paintEvent(self, event: QPaintEvent) -> None:
        """Overload the paint event to draw a simple, left aligned text
        label that matches the button style.
        """
        paint = QPainter(self)
        paint.setRenderHint(QtPaintAnitAlias, True)
        paint.setPen(QtNoPen)

        width = self.width()
        height = self.height()

        tW = width - 2*self._lM
        tH = height - 2*self._tM

        paint.setPen(self._textCol)
        paint.setOpacity(1.0)
        paint.drawText(QRectF(self._lM, self._tM, tW, tH), QtAlignLeft, self.text())

        return
