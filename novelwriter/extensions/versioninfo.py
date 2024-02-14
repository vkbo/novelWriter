"""
novelWriter – Custom Widget: Version Info
=========================================

File History:
Created: 2024-02-14 [2.3b1] VersionInfoWidget

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

from random import shuffle
from datetime import datetime
from urllib.request import Request, urlopen

from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl, pyqtSlot
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

from novelwriter import CONFIG, __version__, __date__, __domain__
from novelwriter.common import formatVersion
from novelwriter.constants import nwConst

logger = logging.getLogger(__name__)

LOOKUPS = [
    "https://novelwriter.io/release-latest.json",
    "https://vkbo.github.io/novelWriter.io/release-latest.json",
    "https://raw.githubusercontent.com/vkbo/novelWriter.io/main/source/_extra/release-latest.json",
]


class VersionInfoWidget(QWidget):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        # Labels
        self._lblInfo = QLabel("{0} {1} \u2013 {2} {3} \u2013 {4}".format(
            self.tr("Version"), formatVersion(__version__),
            self.tr("Released on"), datetime.strptime(__date__, "%Y-%m-%d").strftime("%x"),
            "<a href='#notes'>{0}</a>".format(self.tr("Release Notes")),
        ), self)
        self._lblInfo.linkActivated.connect(self._processLink)
        self._lblRelease = QLabel(self.tr("Latest Version: {0}").format(
            "<a href='#update'>{0}</a>".format(self.tr("Check Now"))
        ), self)
        self._lblRelease.linkActivated.connect(self._processLink)

        # New Release
        self._trRelease = self.tr("Latest Version: {0} {1} Download from {2}")
        self._trFail = self.tr("Could not retrieve version information.")

        # Assemble
        self._layout = QVBoxLayout()
        self._layout.addWidget(self._lblInfo)
        self._layout.addWidget(self._lblRelease)
        self._layout.setSpacing(CONFIG.pxInt(2))
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self._layout)

        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(str)
    def _processLink(self, link: str) -> None:
        """Process an activated link."""
        if link == "#notes":
            QDesktopServices.openUrl(QUrl(nwConst.URL_RELEASES))
        elif link == "#website":
            QDesktopServices.openUrl(QUrl(nwConst.URL_WEB))
        elif link == "#update":
            shuffle(LOOKUPS)
            for url in LOOKUPS:
                if result := self._pullJson(url):
                    self._updateReleaseInfo(result)
                    break
            else:
                self._updateReleaseInfo({})
        return

    ##
    #  Internal Functions
    ##

    def _updateReleaseInfo(self, result: dict) -> None:
        """Update the widget release info."""
        if version := result.get("version"):
            download = f"<a href='#website'>{__domain__}</a>"
            self._lblRelease.setText(self._trRelease.format(version, "\u2013", download))
        else:
            self._lblRelease.setText(self._trFail)
        return

    def _pullJson(self, url: str) -> dict | None:
        """Pull a JSON file from a URL."""
        urlReq = Request(url)
        urlReq.add_header("User-Agent", nwConst.USER_AGENT)
        urlReq.add_header("Accept", "application/json")

        try:
            logger.info("Contacting: %s", url)
            urlData = urlopen(urlReq, timeout=10)
            return json.loads(urlData.read().decode()).get("release")
        except Exception:
            logger.error("Failed to retrieve data")

        return None

# END Class VersionInfoWidget
