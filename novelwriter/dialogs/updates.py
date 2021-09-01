"""
novelWriter – GUI Updates
=========================
A dialog box for checking for latest updates

File History:
Created: 2021-08-21 [1.5a0]

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

import json
import logging
import novelwriter

from datetime import datetime
from urllib.request import Request, urlopen

from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    qApp, QDialog, QHBoxLayout, QVBoxLayout, QDialogButtonBox, QLabel
)

from novelwriter.common import logException

logger = logging.getLogger(__name__)


class GuiUpdates(QDialog):

    def __init__(self, theParent):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiUpdates ...")
        self.setObjectName("GuiUpdates")

        self.mainConf  = novelwriter.CONFIG
        self.theParent = theParent

        self.setWindowTitle(self.tr("Check for Updates"))

        nPx = self.mainConf.pxInt(96)
        sPx = self.mainConf.pxInt(16)
        tPx = self.mainConf.pxInt(8)
        mPx = self.mainConf.pxInt(4)

        # Left Box
        self.nwIcon = QLabel()
        self.nwIcon.setPixmap(self.theParent.theTheme.getPixmap("novelwriter", (nPx, nPx)))

        self.leftBox = QVBoxLayout()
        self.leftBox.addWidget(self.nwIcon)
        self.leftBox.addStretch(1)

        # Right Box
        self.currentLabel = QLabel(self.tr("Current Release"))
        self.currentValue = QLabel(self.tr(
            "novelWriter {0} released on {1}"
        ).format(
            "v%s" % novelwriter.__version__,
            datetime.strptime(novelwriter.__date__, "%Y-%m-%d").strftime("%x"))
        )

        self.latestLabel = QLabel(self.tr("Latest Release"))
        self.latestValue = QLabel(self.tr("Checking ..."))
        self.latestLink = QLabel("")
        self.latestLink.setOpenExternalLinks(True)

        self.rightBox = QVBoxLayout()
        self.rightBox.addWidget(self.currentLabel)
        self.rightBox.addWidget(self.currentValue)
        self.rightBox.addSpacing(tPx)
        self.rightBox.addWidget(self.latestLabel)
        self.rightBox.addWidget(self.latestValue)
        self.rightBox.addSpacing(tPx)
        self.rightBox.addWidget(self.latestLink)
        self.rightBox.setSpacing(mPx)

        hFont = self.currentLabel.font()
        hFont.setBold(True)
        self.currentLabel.setFont(hFont)
        self.latestLabel.setFont(hFont)

        # Buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self._doClose)

        # Assemble
        self.innerBox = QHBoxLayout()
        self.innerBox.addLayout(self.leftBox)
        self.innerBox.addLayout(self.rightBox)
        self.innerBox.setSpacing(sPx)

        self.outerBox = QVBoxLayout()
        self.outerBox.addLayout(self.innerBox)
        self.outerBox.addWidget(self.buttonBox)
        self.outerBox.setSpacing(sPx)

        self.setLayout(self.outerBox)

        logger.debug("GuiUpdates initialisation complete")

        return

    def checkLatest(self):
        """Check for latest release.
        """
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))

        urlReq = Request("https://api.github.com/repos/vkbo/novelwriter/releases/latest")
        urlReq.add_header("User-Agent", "Mozilla/5.0 (compatible; novelWriter (Python))")
        urlReq.add_header("Accept", "application/vnd.github.v3+json")

        rawData = {}
        try:
            urlData = urlopen(urlReq, timeout=10)
            rawData = json.loads(urlData.read().decode())
        except Exception:
            logger.error("Failed to contact GitHub API")
            logException()

        relVersion = rawData.get("tag_name", "Unknown")
        relDate = rawData.get("created_at", None)

        try:
            relDate = datetime.strptime(relDate[:10], "%Y-%m-%d").strftime("%x")
        except Exception:
            relDate = "Unknown"
            logException()

        self.latestValue.setText(self.tr(
            "novelWriter {0} released on {1}"
        ).format(
            relVersion, relDate
        ))

        self.latestLink.setText(self.tr(
            "Download: {0}"
        ).format(
            f'<a href="{novelwriter.__url__}">{novelwriter.__url__}</a>'
        ))

        qApp.restoreOverrideCursor()

        return

    ##
    #  Internal Functions
    ##

    def _doClose(self):
        self.close()
        return

# END Class GuiUpdates
