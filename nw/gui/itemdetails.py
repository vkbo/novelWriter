"""
novelWriter – GUI Item Details Panel
====================================
GUI class for the project tree item details panel

File History:
Created: 2019-04-24 [0.0.1]

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

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel

from nw.enum import nwItemClass, nwItemType
from nw.constants import trConst, nwLabels

logger = logging.getLogger(__name__)


class GuiItemDetails(QWidget):

    def __init__(self, theParent):
        QWidget.__init__(self, theParent)

        logger.debug("Initialising GuiItemDetails ...")
        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theParent.theProject
        self.theTheme   = theParent.theTheme

        # Internal Variables
        self._itemHandle  = None

        # Sizes
        hSp = self.mainConf.pxInt(6)
        vSp = self.mainConf.pxInt(1)
        mPx = self.mainConf.pxInt(6)
        iPx = self.theTheme.baseIconSize
        fPt = self.theTheme.fontPointSize

        self._expCheck = self.theTheme.getPixmap("check", (iPx, iPx))
        self._expCross = self.theTheme.getPixmap("cross", (iPx, iPx))

        fntLabel = QFont()
        fntLabel.setBold(True)
        fntLabel.setPointSizeF(0.9*fPt)

        fntValue = QFont()
        fntValue.setPointSizeF(0.9*fPt)

        # Label
        self.labelName = QLabel(self.tr("Label"))
        self.labelName.setFont(fntLabel)
        self.labelName.setAlignment(Qt.AlignLeft | Qt.AlignBaseline)

        self.labelIcon = QLabel("")
        self.labelIcon.setAlignment(Qt.AlignRight | Qt.AlignBaseline)

        self.labelData = QLabel("")
        self.labelData.setFont(fntValue)
        self.labelData.setAlignment(Qt.AlignLeft | Qt.AlignBaseline)
        self.labelData.setWordWrap(True)

        # Status
        self.statusName = QLabel(self.tr("Status"))
        self.statusName.setFont(fntLabel)
        self.statusName.setAlignment(Qt.AlignLeft)

        self.statusIcon = QLabel("")
        self.statusIcon.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.statusData = QLabel("")
        self.statusData.setFont(fntValue)
        self.statusData.setAlignment(Qt.AlignLeft)

        # Class
        self.className = QLabel(self.tr("Class"))
        self.className.setFont(fntLabel)
        self.className.setAlignment(Qt.AlignLeft)

        self.classIcon = QLabel("")
        self.classIcon.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.classData = QLabel("")
        self.classData.setFont(fntValue)
        self.classData.setAlignment(Qt.AlignLeft)

        # Layout
        self.usageName = QLabel(self.tr("Usage"))
        self.usageName.setFont(fntLabel)
        self.usageName.setAlignment(Qt.AlignLeft)

        self.usageIcon = QLabel("")
        self.usageIcon.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.usageData = QLabel("")
        self.usageData.setFont(fntValue)
        self.usageData.setAlignment(Qt.AlignLeft)

        # Character Count
        self.cCountName = QLabel("  "+self.tr("Characters"))
        self.cCountName.setFont(fntLabel)
        self.cCountName.setAlignment(Qt.AlignRight)

        self.cCountData = QLabel("")
        self.cCountData.setFont(fntValue)
        self.cCountData.setAlignment(Qt.AlignRight)

        # Word Count
        self.wCountName = QLabel("  "+self.tr("Words"))
        self.wCountName.setFont(fntLabel)
        self.wCountName.setAlignment(Qt.AlignRight)

        self.wCountData = QLabel("")
        self.wCountData.setFont(fntValue)
        self.wCountData.setAlignment(Qt.AlignRight)

        # Paragraph Count
        self.pCountName = QLabel("  "+self.tr("Paragraphs"))
        self.pCountName.setFont(fntLabel)
        self.pCountName.setAlignment(Qt.AlignRight)

        self.pCountData = QLabel("")
        self.pCountData.setFont(fntValue)
        self.pCountData.setAlignment(Qt.AlignRight)

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

        # Make sure the columns for flags and counts don't resize too often
        flagWidth  = self.theTheme.getTextWidth("Mm", fntValue)
        countWidth = self.theTheme.getTextWidth("99,999", fntValue)
        self.mainBox.setColumnMinimumWidth(1, flagWidth)
        self.mainBox.setColumnMinimumWidth(4, countWidth)

        logger.debug("GuiItemDetails initialisation complete")

        return

    ###
    #  Class Methods
    ##

    def clearDetails(self):
        """Clear all the data values.
        """
        self._itemHandle = None

        self.labelIcon.setPixmap(QPixmap(1, 1))
        self.statusIcon.setPixmap(QPixmap(1, 1))
        self.classIcon.setText("")
        self.usageIcon.setText("")

        self.labelData.setText("–")
        self.statusData.setText("–")
        self.classData.setText("–")
        self.usageData.setText("–")

        self.cCountData.setText("–")
        self.wCountData.setText("–")
        self.pCountData.setText("–")

        return

    def updateViewBox(self, tHandle):
        """Populate the details box from a given handle.
        """
        if tHandle is None:
            self.clearDetails()
            return

        nwItem = self.theProject.projTree[tHandle]
        if nwItem is None:
            self.clearDetails()
            return

        self._itemHandle = tHandle
        iPx = int(round(0.8*self.theTheme.baseIconSize))

        # Label
        # =====

        theLabel = nwItem.itemName
        if len(theLabel) > 100:
            theLabel = theLabel[:96].rstrip()+" ..."

        if nwItem.itemType == nwItemType.FILE:
            if nwItem.isExported:
                self.labelIcon.setPixmap(self._expCheck)
            else:
                self.labelIcon.setPixmap(self._expCross)
        else:
            self.labelIcon.setPixmap(QPixmap(1, 1))

        self.labelData.setText(theLabel)

        # Status
        # ======

        itStatus = nwItem.itemStatus
        if nwItem.itemClass == nwItemClass.NOVEL:
            itStatus = self.theProject.statusItems.checkEntry(itStatus)  # Make sure it's valid
            flagIcon = self.theParent.statusIcons[itStatus]
        else:
            itStatus = self.theProject.importItems.checkEntry(itStatus)  # Make sure it's valid
            flagIcon = self.theParent.importIcons[itStatus]

        self.statusIcon.setPixmap(flagIcon.pixmap(iPx, iPx))
        self.statusData.setText(nwItem.itemStatus)

        # Class
        # =====

        classIcon = self.theTheme.getIcon(nwLabels.CLASS_ICON[nwItem.itemClass])
        self.classIcon.setPixmap(classIcon.pixmap(iPx, iPx))
        self.classData.setText(trConst(nwLabels.CLASS_NAME[nwItem.itemClass]))

        # Layout
        # ======

        hLevel = self.theParent.theIndex.getHandleHeaderLevel(tHandle)
        usageIcon = self.theTheme.getItemIcon(
            nwItem.itemType, nwItem.itemClass, nwItem.itemLayout, hLevel
        )
        self.usageIcon.setPixmap(usageIcon.pixmap(iPx, iPx))
        self.usageData.setText(nwItem.describeMe(hLevel))

        # Counts
        # ======

        if nwItem.itemType == nwItemType.FILE:
            self.cCountData.setText(f"{nwItem.charCount:n}")
            self.wCountData.setText(f"{nwItem.wordCount:n}")
            self.pCountData.setText(f"{nwItem.paraCount:n}")
        else:
            self.cCountData.setText("–")
            self.wCountData.setText("–")
            self.pCountData.setText("–")

        return

    ##
    #  Slots
    ##

    @pyqtSlot(str, int, int, int)
    def doUpdateCounts(self, tHandle, cC, wC, pC):
        """Update the counts if the handle is the same as the one we're
        already showing. Otherwise, do nothing.
        """
        if tHandle == self._itemHandle:
            self.cCountData.setText(f"{cC:n}")
            self.wCountData.setText(f"{wC:n}")
            self.pCountData.setText(f"{pC:n}")

        return

# END Class GuiItemDetails
