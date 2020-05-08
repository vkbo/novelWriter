# -*- coding: utf-8 -*-
"""novelWriter GUI Document Details

 novelWriter – GUI Document Details
====================================
 Class holding the left side document details panel

 File History:
 Created: 2019-04-24 [0.0.1]

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

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QGridLayout, QLabel

from nw.constants import nwLabels

logger = logging.getLogger(__name__)

class GuiDocDetails(QFrame):

    def __init__(self, theParent, theProject):
        QFrame.__init__(self, theParent)

        logger.debug("Initialising DocDetails ...")
        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject

        self.mainBox = QGridLayout(self)
        self.mainBox.setVerticalSpacing(1)
        self.mainBox.setHorizontalSpacing(15)
        self.setLayout(self.mainBox)

        self.fntOne = QFont()
        self.fntOne.setPointSize(10)
        self.fntOne.setBold(True)

        self.fntTwo = QFont()
        self.fntTwo.setPointSize(10)
        self.colTwo = [
            QLabel(""),
            QLabel(""),
            QLabel(""),
            QLabel("")
        ]

        colOne = ["Label","Status","Class","Layout"]
        for nRow in range(4):
            lblOne = QLabel(colOne[nRow])
            lblOne.setFont(self.fntOne)
            lblOne.setAlignment(Qt.AlignTop)
            self.mainBox.addWidget(lblOne,nRow,0)
            self.mainBox.addWidget(self.colTwo[nRow],nRow,1)
            self.colTwo[nRow].setWordWrap(True)
            self.colTwo[nRow].setAlignment(Qt.AlignTop)

        self.mainBox.setColumnStretch(0,0)
        self.mainBox.setColumnStretch(1,1)

        logger.debug("DocDetails initialisation complete")

        return

    def buildViewBox(self, tHandle):

        nwItem = self.theProject.projTree[tHandle]

        if nwItem is None:
            colTwo = [""]*4
        else:
            theLabel = nwItem.itemName
            if len(theLabel) > 100:
                theLabel = theLabel[:96].rstrip()+" ..."
            colTwo = [
                theLabel,
                nwItem.itemStatus,
                nwLabels.CLASS_NAME[nwItem.itemClass],
                nwLabels.LAYOUT_NAME[nwItem.itemLayout],
            ]

        for nRow in range(4):
            self.colTwo[nRow].setText(colTwo[nRow])

        return

# END Class GuiDocDetails
