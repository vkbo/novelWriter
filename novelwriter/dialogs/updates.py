"""
novelWriter – GUI Updates
=========================

File History:
Created: 2021-08-21 [1.5b1] GuiUpdates

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

import json
import logging

from datetime import datetime
from urllib.request import Request, urlopen

from PyQt5.QtGui import QCloseEvent, QCursor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, qApp, QDialog, QHBoxLayout, QVBoxLayout, QDialogButtonBox, QLabel
)

from novelwriter import CONFIG, SHARED, __version__, __date__
from novelwriter.common import logException
from novelwriter.constants import nwConst

logger = logging.getLogger(__name__)


class GuiUpdates(QDialog):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiUpdates")
        self.setObjectName("GuiUpdates")
        self.setWindowTitle(self.tr("Check for Updates"))

        nPx = CONFIG.pxInt(96)
        sPx = CONFIG.pxInt(16)
        tPx = CONFIG.pxInt(8)
        mPx = CONFIG.pxInt(4)

        # Left Box
        self.nwIcon = QLabel()
        self.nwIcon.setPixmap(SHARED.theme.getPixmap("novelwriter", (nPx, nPx)))

        self.leftBox = QVBoxLayout()
        self.leftBox.addWidget(self.nwIcon)
        self.leftBox.addStretch(1)

        # Right Box
        self.currentLabel = QLabel(self.tr("Current Release"))
        self.currentValue = QLabel(self.tr(
            "novelWriter {0} released on {1}"
        ).format(
            "v%s" % __version__,
            datetime.strptime(__date__, "%Y-%m-%d").strftime("%x"))
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
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttonBox.rejected.connect(self.close)

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

        logger.debug("Ready: GuiUpdates")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiUpdates")
        return

    def checkLatest(self) -> None:
        """Check for latest release."""
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))

        urlReq = Request("https://api.github.com/repos/vkbo/novelwriter/releases/latest")
        urlReq.add_header("User-Agent", nwConst.USER_AGENT)
        urlReq.add_header("Accept", "application/vnd.github.v3+json")

        rawData = {}
        try:
            urlData = urlopen(urlReq, timeout=10)
            rawData = json.loads(urlData.read().decode())
        except Exception:
            logger.error("Failed to contact GitHub API")
            logException()

        relVersion = rawData.get("tag_name", "Unknown")
        relDate = rawData.get("created_at", "")

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
            f'<a href="{nwConst.URL_WEB}">{nwConst.URL_WEB}</a>'
        ))

        qApp.restoreOverrideCursor()

        return

    ##
    #  Events
    ##

    def closeEvent(self, event: QCloseEvent) -> None:
        """Capture the user closing the window."""
        event.accept()
        self.deleteLater()
        return

# END Class GuiUpdates
