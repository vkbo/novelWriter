"""
novelWriter – GUI Quotes Dialog
===============================

File History:
Created: 2020-06-18 [0.9.0] GuiQuoteSelect

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

import logging

from PyQt5.QtCore import QSize, pyqtSlot
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import (
    QDialogButtonBox, QFrame, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QVBoxLayout, QWidget
)

from novelwriter import CONFIG
from novelwriter.constants import nwQuotes, trConst
from novelwriter.extensions.modified import NDialog
from novelwriter.types import (
    QtAccepted, QtAlignCenter, QtAlignTop, QtDialogCancel, QtDialogOk,
    QtUserRole
)

logger = logging.getLogger(__name__)


class GuiQuoteSelect(NDialog):

    _selected = ""

    D_KEY = QtUserRole

    def __init__(self, parent: QWidget, current: str = '"') -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiQuoteSelect")
        self.setObjectName("GuiQuoteSelect")
        self.setWindowTitle(self.tr("Select Quote Style"))

        self.outerBox = QVBoxLayout()
        self.innerBox = QHBoxLayout()
        self.labelBox = QVBoxLayout()

        self._selected = current

        qMetrics = QFontMetrics(self.font())
        pxW = 7*qMetrics.boundingRectChar("M").width()
        pxH = 7*qMetrics.boundingRectChar("M").height()
        pxH = 7*qMetrics.boundingRectChar("M").height()

        lblFont = self.font()
        lblFont.setPointSizeF(4*lblFont.pointSizeF())

        # Preview Label
        self.previewLabel = QLabel(current, self)
        self.previewLabel.setFont(lblFont)
        self.previewLabel.setFixedSize(QSize(pxW, pxH))
        self.previewLabel.setAlignment(QtAlignCenter)
        self.previewLabel.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)

        # Quote Symbols
        self.listBox = QListWidget(self)
        self.listBox.itemSelectionChanged.connect(self._selectedSymbol)

        minSize = 100
        for sKey, sLabel in nwQuotes.SYMBOLS.items():
            text = "[ %s ] %s" % (sKey, trConst(sLabel))
            minSize = max(minSize, qMetrics.boundingRect(text).width())
            qtItem = QListWidgetItem(text)
            qtItem.setData(self.D_KEY, sKey)
            self.listBox.addItem(qtItem)
            if sKey == current:
                self.listBox.setCurrentItem(qtItem)

        self.listBox.setMinimumWidth(minSize + CONFIG.pxInt(40))
        self.listBox.setMinimumHeight(CONFIG.pxInt(150))

        # Buttons
        self.buttonBox = QDialogButtonBox(QtDialogOk | QtDialogCancel, self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # Assemble
        self.labelBox.addWidget(self.previewLabel, 0, QtAlignTop)
        self.labelBox.addStretch(1)

        self.innerBox.addLayout(self.labelBox)
        self.innerBox.addWidget(self.listBox)

        self.outerBox.addLayout(self.innerBox)
        self.outerBox.addWidget(self.buttonBox)

        self.setLayout(self.outerBox)

        logger.debug("Ready: GuiQuoteSelect")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiQuoteSelect")
        return

    @property
    def selectedQuote(self) -> str:
        """Return the selected quote symbol."""
        return self._selected

    @classmethod
    def getQuote(cls, parent: QWidget, current: str = "") -> tuple[str, bool]:
        """Pop the dialog and return the result."""
        cls = GuiQuoteSelect(parent, current=current)
        cls.exec()
        quote = cls._selected
        accepted = cls.result() == QtAccepted
        cls.softDelete()
        return quote, accepted

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _selectedSymbol(self) -> None:
        """Update the preview label and the selected quote style."""
        if items := self.listBox.selectedItems():
            quote = items[0].data(self.D_KEY)
            self.previewLabel.setText(quote)
            self._selected = quote
        return
