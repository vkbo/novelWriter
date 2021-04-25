# -*- coding: utf-8 -*-
"""
novelWriter – GUI Quotes Dialog
===============================
GUI class for quotes dialog

File History:
Created: 2020-06-18 [0.9]

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

from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QDialog, QDialogButtonBox,
    QListWidget, QListWidgetItem, QFrame
)

from nw.constants import trConst, nwQuotes

logger = logging.getLogger(__name__)

class GuiQuoteSelect(QDialog):

    selectedQuote = ""

    def __init__(self, theParent=None, currentQuote='"'):
        QDialog.__init__(self, parent=theParent)

        self.mainConf = nw.CONFIG

        self.outerBox = QVBoxLayout()
        self.innerBox = QHBoxLayout()
        self.labelBox = QVBoxLayout()

        self.selectedQuote = currentQuote

        qMetrics = QFontMetrics(self.font())
        pxW = 7*qMetrics.boundingRectChar("M").width()
        pxH = 7*qMetrics.boundingRectChar("M").height()
        pxH = 7*qMetrics.boundingRectChar("M").height()

        lblFont = self.font()
        lblFont.setPointSizeF(4*lblFont.pointSizeF())

        # Preview Label
        self.previewLabel = QLabel(currentQuote)
        self.previewLabel.setFont(lblFont)
        self.previewLabel.setFixedSize(QSize(pxW, pxH))
        self.previewLabel.setAlignment(Qt.AlignCenter)
        self.previewLabel.setFrameStyle(QFrame.Box | QFrame.Plain)

        # Quote Symbols
        self.listBox = QListWidget()
        self.listBox.itemSelectionChanged.connect(self._selectedSymbol)

        minSize = 100
        for sKey, sLabel in nwQuotes.SYMBOLS.items():
            theText = "[ %s ] %s" % (sKey, trConst(sLabel))
            minSize = max(minSize, qMetrics.boundingRect(theText).width())
            qtItem = QListWidgetItem(theText)
            qtItem.setData(Qt.UserRole, sKey)
            self.listBox.addItem(qtItem)
            if sKey == currentQuote:
                self.listBox.setCurrentItem(qtItem)

        self.listBox.setMinimumWidth(minSize + self.mainConf.pxInt(40))
        self.listBox.setMinimumHeight(self.mainConf.pxInt(150))

        # Buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._doAccept)
        self.buttonBox.rejected.connect(self._doReject)

        # Assemble
        self.labelBox.addWidget(self.previewLabel, 0, Qt.AlignTop)
        self.labelBox.addStretch(1)

        self.innerBox.addLayout(self.labelBox)
        self.innerBox.addWidget(self.listBox)

        self.outerBox.addLayout(self.innerBox)
        self.outerBox.addWidget(self.buttonBox)

        self.setLayout(self.outerBox)

        return

    ##
    #  Slots
    ##

    def _selectedSymbol(self):
        """Update the preview label and the selected quote style.
        """
        selItems = self.listBox.selectedItems()
        if selItems:
            theSymbol = selItems[0].data(Qt.UserRole)
            self.previewLabel.setText(theSymbol)
            self.selectedQuote = theSymbol
        return

    def _doAccept(self):
        """Ok button clicked.
        """
        self.accept()
        return

    def _doReject(self):
        """Cancel button clicked.
        """
        self.reject()
        return

# END Class GuiQuoteSelect
