"""
novelWriter – GUI Item Details Panel
====================================

File History:
Created: 2019-04-24 [0.0.1] GuiItemDetails

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

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QGridLayout, QLabel, QWidget

from novelwriter import CONFIG, SHARED
from novelwriter.common import elide
from novelwriter.constants import nwLabels, trConst
from novelwriter.types import (
    QtAlignLeft, QtAlignLeftBase, QtAlignRight, QtAlignRightBase,
    QtAlignRightMiddle
)

logger = logging.getLogger(__name__)


class GuiItemDetails(QWidget):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiItemDetails")

        # Internal Variables
        self._handle = None

        # Sizes
        hSp = CONFIG.pxInt(6)
        vSp = CONFIG.pxInt(1)
        mPx = CONFIG.pxInt(6)
        fPt = SHARED.theme.fontPointSize

        fntLabel = self.font()
        fntLabel.setBold(True)
        fntLabel.setPointSizeF(0.9*fPt)

        fntValue = self.font()
        fntValue.setPointSizeF(0.9*fPt)

        # Label
        self.labelName = QLabel(self.tr("Label"), self)
        self.labelName.setFont(fntLabel)
        self.labelName.setAlignment(QtAlignLeftBase)

        self.labelIcon = QLabel("", self)
        self.labelIcon.setAlignment(QtAlignRightBase)

        self.labelData = QLabel("", self)
        self.labelData.setFont(fntValue)
        self.labelData.setAlignment(QtAlignLeftBase)
        self.labelData.setWordWrap(True)

        # Status
        self.statusName = QLabel(self.tr("Status"), self)
        self.statusName.setFont(fntLabel)
        self.statusName.setAlignment(QtAlignLeft)

        self.statusIcon = QLabel("", self)
        self.statusIcon.setAlignment(QtAlignRightMiddle)

        self.statusData = QLabel("", self)
        self.statusData.setFont(fntValue)
        self.statusData.setAlignment(QtAlignLeft)

        # Class
        self.className = QLabel(self.tr("Class"), self)
        self.className.setFont(fntLabel)
        self.className.setAlignment(QtAlignLeft)

        self.classIcon = QLabel("", self)
        self.classIcon.setAlignment(QtAlignRightMiddle)

        self.classData = QLabel("", self)
        self.classData.setFont(fntValue)
        self.classData.setAlignment(QtAlignLeft)

        # Layout
        self.usageName = QLabel(self.tr("Usage"), self)
        self.usageName.setFont(fntLabel)
        self.usageName.setAlignment(QtAlignLeft)

        self.usageIcon = QLabel("", self)
        self.usageIcon.setAlignment(QtAlignRightMiddle)

        self.usageData = QLabel("", self)
        self.usageData.setFont(fntValue)
        self.usageData.setAlignment(QtAlignLeft)
        self.usageData.setWordWrap(True)

        # Character Count
        self.cCountName = QLabel("  "+self.tr("Characters"), self)
        self.cCountName.setFont(fntLabel)
        self.cCountName.setAlignment(QtAlignRight)

        self.cCountData = QLabel("", self)
        self.cCountData.setFont(fntValue)
        self.cCountData.setAlignment(QtAlignRight)

        # Word Count
        self.wCountName = QLabel("  "+self.tr("Words"), self)
        self.wCountName.setFont(fntLabel)
        self.wCountName.setAlignment(QtAlignRight)

        self.wCountData = QLabel("", self)
        self.wCountData.setFont(fntValue)
        self.wCountData.setAlignment(QtAlignRight)

        # Paragraph Count
        self.pCountName = QLabel("  "+self.tr("Paragraphs"), self)
        self.pCountName.setFont(fntLabel)
        self.pCountName.setAlignment(QtAlignRight)

        self.pCountData = QLabel("", self)
        self.pCountData.setFont(fntValue)
        self.pCountData.setAlignment(QtAlignRight)

        # Assemble
        self.mainBox = QGridLayout(self)
        self.mainBox.addWidget(self.labelName,  0, 0, 1, 1)
        self.mainBox.addWidget(self.labelIcon,  0, 1, 1, 1)
        self.mainBox.addWidget(self.labelData,  0, 2, 1, 3)

        self.mainBox.addWidget(self.statusName, 1, 0, 1, 1)
        self.mainBox.addWidget(self.statusIcon, 1, 1, 1, 1)
        self.mainBox.addWidget(self.statusData, 1, 2, 1, 1)
        self.mainBox.addWidget(self.cCountName, 1, 3, 1, 1)
        self.mainBox.addWidget(self.cCountData, 1, 4, 1, 1)

        self.mainBox.addWidget(self.className,  2, 0, 1, 1)
        self.mainBox.addWidget(self.classIcon,  2, 1, 1, 1)
        self.mainBox.addWidget(self.classData,  2, 2, 1, 1)
        self.mainBox.addWidget(self.wCountName, 2, 3, 1, 1)
        self.mainBox.addWidget(self.wCountData, 2, 4, 1, 1)

        self.mainBox.addWidget(self.usageName,  3, 0, 1, 1)
        self.mainBox.addWidget(self.usageIcon,  3, 1, 1, 1)
        self.mainBox.addWidget(self.usageData,  3, 2, 1, 1)
        self.mainBox.addWidget(self.pCountName, 3, 3, 1, 1)
        self.mainBox.addWidget(self.pCountData, 3, 4, 1, 1)

        self.mainBox.setColumnStretch(0, 0)
        self.mainBox.setColumnStretch(1, 0)
        self.mainBox.setColumnStretch(2, 1)
        self.mainBox.setColumnStretch(3, 0)
        self.mainBox.setColumnStretch(4, 0)

        self.mainBox.setHorizontalSpacing(hSp)
        self.mainBox.setVerticalSpacing(vSp)
        self.mainBox.setContentsMargins(mPx, mPx, mPx, mPx)

        self.setLayout(self.mainBox)

        self.updateTheme()

        # Make sure the columns for flags and counts don't resize too often
        flagWidth  = SHARED.theme.getTextWidth("Mm", fntValue)
        countWidth = SHARED.theme.getTextWidth("99,999", fntValue)
        self.mainBox.setColumnMinimumWidth(1, flagWidth)
        self.mainBox.setColumnMinimumWidth(4, countWidth)

        logger.debug("Ready: GuiItemDetails")

        return

    ###
    #  Class Methods
    ##

    def clearDetails(self) -> None:
        """Clear all the data values."""
        self._handle = None
        self.labelIcon.clear()
        self.labelData.clear()
        self.statusIcon.clear()
        self.statusData.clear()
        self.classIcon.clear()
        self.classData.clear()
        self.usageIcon.clear()
        self.usageData.clear()
        self.cCountData.clear()
        self.wCountData.clear()
        self.pCountData.clear()
        return

    def refreshDetails(self) -> None:
        """Reload the content of the details panel."""
        self.updateViewBox(self._handle)

    def updateTheme(self) -> None:
        """Update theme elements."""
        self.updateViewBox(self._handle)
        return

    ##
    #  Public Slots
    ##

    @pyqtSlot(str)
    def updateViewBox(self, tHandle: str) -> None:
        """Populate the details box from a given handle."""
        if tHandle is None:
            self.clearDetails()
            return

        nwItem = SHARED.project.tree[tHandle]
        if nwItem is None:
            self.clearDetails()
            return

        self._handle = tHandle
        iPx = int(round(0.9*SHARED.theme.baseIconHeight))

        # Label
        # =====

        if nwItem.isFileType():
            if nwItem.isActive:
                self.labelIcon.setPixmap(SHARED.theme.getPixmap("checked", (iPx, iPx)))
            else:
                self.labelIcon.setPixmap(SHARED.theme.getPixmap("unchecked", (iPx, iPx)))
        else:
            self.labelIcon.setPixmap(SHARED.theme.getPixmap("noncheckable", (iPx, iPx)))

        self.labelData.setText(elide(nwItem.itemName, 100))

        # Status
        # ======

        status, icon = nwItem.getImportStatus()
        self.statusIcon.setPixmap(icon.pixmap(iPx, iPx))
        self.statusData.setText(status)

        # Class
        # =====

        classIcon = SHARED.theme.getIcon(nwLabels.CLASS_ICON[nwItem.itemClass])
        self.classIcon.setPixmap(classIcon.pixmap(iPx, iPx))
        self.classData.setText(trConst(nwLabels.CLASS_NAME[nwItem.itemClass]))

        # Layout
        # ======

        usageIcon = SHARED.theme.getItemIcon(
            nwItem.itemType, nwItem.itemClass, nwItem.itemLayout, nwItem.mainHeading
        )
        self.usageIcon.setPixmap(usageIcon.pixmap(iPx, iPx))
        self.usageData.setText(nwItem.describeMe())

        # Counts
        # ======

        if nwItem.isFileType():
            self.cCountData.setText(f"{nwItem.charCount:n}")
            self.wCountData.setText(f"{nwItem.wordCount:n}")
            self.pCountData.setText(f"{nwItem.paraCount:n}")
        else:
            self.cCountData.setText("–")
            self.wCountData.setText("–")
            self.pCountData.setText("–")

        return

    @pyqtSlot(str, int, int, int)
    def updateCounts(self, tHandle: str, cC: int, wC: int, pC: int) -> None:
        """Update the counts if the handle is the same as the one we're
        already showing. Otherwise, do nothing.
        """
        if tHandle == self._handle:
            self.cCountData.setText(f"{cC:n}")
            self.wCountData.setText(f"{wC:n}")
            self.pCountData.setText(f"{pC:n}")
        return
