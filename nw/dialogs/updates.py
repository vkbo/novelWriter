"""
novelWriter – GUI Updates
=========================
A dialog box for checking for latest updates

File History:
Created: 2021-08-21 [1.5-alpah0]

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

from datetime import datetime

from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGridLayout, qApp, QDialog, QHBoxLayout, QVBoxLayout, QDialogButtonBox, QLabel
)

logger = logging.getLogger(__name__)


class GuiUpdates(QDialog):

    def __init__(self, theParent):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiUpdates ...")
        self.setObjectName("GuiUpdates")

        self.mainConf  = nw.CONFIG
        self.theParent = theParent

        self.setWindowTitle(self.tr("Check for Updates"))
        # self.setMinimumWidth(self.mainConf.pxInt(650))
        # self.setMinimumHeight(self.mainConf.pxInt(600))

        # Left Box
        nPx = self.mainConf.pxInt(96)
        self.nwIcon = QLabel()
        self.nwIcon.setPixmap(self.theParent.theTheme.getPixmap("novelwriter", (nPx, nPx)))
        self.lblName = QLabel("<b>novelWriter</b>")
        self.lblVers = QLabel("v%s" % nw.__version__)
        self.lblDate = QLabel(datetime.strptime(nw.__date__, "%Y-%m-%d").strftime("%x"))

        self.leftBox = QVBoxLayout()
        self.leftBox.setSpacing(self.mainConf.pxInt(4))
        self.leftBox.addWidget(self.nwIcon,  0, Qt.AlignCenter)
        self.leftBox.addWidget(self.lblName, 0, Qt.AlignCenter)
        self.leftBox.addWidget(self.lblVers, 0, Qt.AlignCenter)
        self.leftBox.addWidget(self.lblDate, 0, Qt.AlignCenter)
        self.leftBox.addStretch(1)

        # Right Box
        self.currentLabel = QLabel(self.tr("Current Release"))
        self.currentValue = QLabel("v%s" % nw.__version__)

        self.latestLabel = QLabel(self.tr("Latest Release"))
        self.latestValue = QLabel("")

        self.rightBox = QGridLayout()
        self.rightBox.addWidget(self.currentLabel, 0, 0, Qt.AlignLeft)
        self.rightBox.addWidget(self.currentValue, 0, 1, Qt.AlignLeft)
        self.rightBox.addWidget(self.latestLabel,  1, 0, Qt.AlignLeft)
        self.rightBox.addWidget(self.latestValue,  1, 1, Qt.AlignLeft)
        self.rightBox.setRowStretch(2, 1)
        self.rightBox.setVerticalSpacing(self.mainConf.pxInt(4))
        self.rightBox.setHorizontalSpacing(self.mainConf.pxInt(16))

        # Buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self._doClose)

        # Assemble
        self.innerBox = QHBoxLayout()
        self.innerBox.addLayout(self.leftBox)
        self.innerBox.addLayout(self.rightBox)
        self.innerBox.setSpacing(self.mainConf.pxInt(16))

        self.outerBox = QVBoxLayout()
        self.outerBox.addLayout(self.innerBox)
        self.outerBox.addWidget(self.buttonBox)
        self.setLayout(self.outerBox)

        logger.debug("GuiUpdates initialisation complete")

        return

    def checkLatest(self):
        """Check for latest release.
        """
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        qApp.restoreOverrideCursor()
        return

    ##
    #  Internal Functions
    ##

    def _doClose(self):
        self.close()
        return

# END Class GuiUpdates
