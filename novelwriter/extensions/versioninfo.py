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

from datetime import datetime
from time import sleep
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from PyQt5.QtCore import QObject, QRunnable, QUrl, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

from novelwriter import CONFIG, SHARED, __date__, __domain__, __version__
from novelwriter.common import formatVersion
from novelwriter.constants import nwConst

logger = logging.getLogger(__name__)

API_URL = "https://api.github.com/repos/vkbo/novelwriter/releases/latest"


class VersionInfoWidget(QWidget):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        # Label Strings
        self._trLatest = self.tr("Latest Version: {0}")
        self._trChecking = self.tr("Checking ...")
        self._trDownload = self.tr("Download from {0}")

        # Labels
        self._lblInfo = QLabel("{0} {1} \u2013 {2} {3} \u2013 {4}".format(
            self.tr("Version"), formatVersion(__version__),
            self.tr("Released on"), CONFIG.localDate(datetime.strptime(__date__, "%Y-%m-%d")),
            "<a href='#notes'>{0}</a>".format(self.tr("Release Notes")),
        ), self)
        self._lblInfo.linkActivated.connect(self._processLink)
        self._lblRelease = QLabel(self._trLatest.format(
            "<a href='#update'>{0}</a>".format(self.tr("Check Now"))
        ), self)
        self._lblRelease.linkActivated.connect(self._processLink)

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
            self._lblRelease.setText(self._trLatest.format(self._trChecking))
            lookup = _Retriever()
            lookup.signals.dataReady.connect(self._updateReleaseInfo)
            SHARED.runInThreadPool(lookup)
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(str, str)
    def _updateReleaseInfo(self, tag: str, reason: str) -> None:
        """Update the widget release info."""
        if version := tag.lstrip("v"):
            download = f"<a href='#website'>{__domain__}</a>"
            self._lblRelease.setText(self._trLatest.format(
                f"{version} \u2013 {self._trDownload.format(download)}"
            ))
        else:
            self._lblRelease.setText(self._trLatest.format(reason or self.tr("Failed")))
        return


class _Retriever(QRunnable):

    def __init__(self) -> None:
        super().__init__()
        self.signals = _RetrieverSignal()
        return

    @pyqtSlot()
    def run(self) -> None:
        """Poll the GitHub API in the background.
        Note: The GitHub API is rate limited at 60 requests per hour.
        """
        logger.info("Contacting: %s", API_URL)
        req = Request(API_URL)
        req.add_header("User-Agent", nwConst.USER_AGENT)
        req.add_header("Accept", "application/vnd.github.v3+json")
        sleep(0.2)
        try:
            with urlopen(req, timeout=15) as ret:
                if isinstance(raw := json.loads(ret.read().decode()), dict):
                    self.signals.dataReady.emit(raw.get("tag_name", ""), "")
        except HTTPError as e:
            reason = f"{e.reason.capitalize()} (HTTP {e.code})"
            logger.error(reason)
            self.signals.dataReady.emit("", reason)
        except Exception as e:
            logger.error("Failed to retrieve release info")
            self.signals.dataReady.emit("", str(e))
        return


class _RetrieverSignal(QObject):
    dataReady = pyqtSignal(str, str)
