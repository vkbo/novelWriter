"""
novelWriter – GUI Dictionary Downloader
=======================================

File History:
Created: 2023-11-19 [2.2rc1]

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, pathname2url, urlopen

from PyQt5.QtGui import QCloseEvent, QCursor, QDesktopServices
from PyQt5.QtCore import QLocale, QUrl, Qt, pyqtSlot
from PyQt5.QtWidgets import (
    QAbstractItemView, QDialog, QDialogButtonBox, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPlainTextEdit, QPushButton, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QWidget, qApp
)

from novelwriter import CONFIG, SHARED
from novelwriter.error import logException
from novelwriter.common import checkInt, formatInt
from novelwriter.constants import nwConst

logger = logging.getLogger(__name__)


class GuiDictionaries(QDialog):

    C_CODE  = 0
    C_NAME  = 1
    C_STATE = 2

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiDictionaries")
        self.setObjectName("GuiDictionaries")
        self.setWindowTitle(self.tr("Download Dictionaries"))

        vPx = CONFIG.pxInt(4)
        hPx = CONFIG.pxInt(8)
        sPx = CONFIG.pxInt(16)

        self.setMinimumWidth(CONFIG.pxInt(500))
        self.setMinimumHeight(CONFIG.pxInt(200))

        self._currDicts = set()
        self._trHave = self.tr("Downloaded")

        # Info
        self.pathLabel = QLabel(self.tr("Location"))
        self.pathBox = QLineEdit(self)
        self.pathBox.setReadOnly(True)
        self.pathButton = QPushButton(self)
        self.pathButton.setIcon(SHARED.theme.getIcon("browse"))
        self.pathButton.setToolTip(self.tr("Open Location"))
        self.pathButton.clicked.connect(self._openLocation)

        self.pathLayout = QHBoxLayout()
        self.pathLayout.addWidget(self.pathLabel)
        self.pathLayout.addWidget(self.pathBox)
        self.pathLayout.addWidget(self.pathButton)
        self.pathLayout.setSpacing(hPx)

        # List Box
        self.listBox = QTreeWidget(self)
        self.listBox.setHeaderLabels([self.tr("Code"), self.tr("Language"), self.tr("Status")])
        self.listBox.setIndentation(0)
        self.listBox.setUniformRowHeights(True)
        self.listBox.setSortingEnabled(True)
        self.listBox.sortByColumn(self.C_CODE, Qt.SortOrder.AscendingOrder)
        self.listBox.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.listBox.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        treeHeader = self.listBox.header()
        treeHeader.setStretchLastSection(True)
        treeHeader.setSectionResizeMode(self.C_CODE, QHeaderView.ResizeMode.ResizeToContents)
        treeHeader.setSectionResizeMode(self.C_NAME, QHeaderView.ResizeMode.ResizeToContents)

        # Info Box
        self.infoBox = QPlainTextEdit(self)
        self.infoBox.setReadOnly(True)
        self.infoBox.setFixedHeight(4*SHARED.theme.fontPixelSize)

        # Buttons
        self.checkButton = QPushButton(self)
        self.checkButton.setText("Check Dictionaries")
        self.checkButton.clicked.connect(self._loadDictionaries)

        self.downloadButton = QPushButton(self)
        self.downloadButton.setText("Download Selected")
        self.downloadButton.clicked.connect(self._downloadDictionary)

        self.deleteButton = QPushButton(self)
        self.deleteButton.setText("Delete Selected")
        self.deleteButton.clicked.connect(self._deleteDictionary)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.checkButton)
        self.buttonLayout.addWidget(self.downloadButton)
        self.buttonLayout.addWidget(self.deleteButton)
        self.buttonLayout.setSpacing(hPx)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttonBox.rejected.connect(self._doClose)

        # Assemble
        self.innerBox = QVBoxLayout()
        self.innerBox.addLayout(self.pathLayout)
        self.innerBox.addLayout(self.buttonLayout)
        self.innerBox.addWidget(self.listBox)
        self.innerBox.addWidget(self.infoBox)
        self.innerBox.setSpacing(vPx)

        self.outerBox = QVBoxLayout()
        self.outerBox.addLayout(self.innerBox)
        self.outerBox.addWidget(self.buttonBox)
        self.outerBox.setSpacing(sPx)

        self.setLayout(self.outerBox)

        logger.debug("Ready: GuiDictionaries")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiDictionaries")
        return

    def initDialog(self) -> bool:
        """Prepare and check that we can proceed."""
        try:
            import enchant
            path = Path(enchant.get_user_config_dir())
        except Exception:
            logger.error("Could not get enchant path")
            return False

        if path.is_dir():
            self.pathBox.setText(str(path))
            hunspell = path / "hunspell"
            if hunspell.is_dir():
                self._currDicts = set(i.stem for i in hunspell.iterdir() if i.is_file())
            self.infoBox.appendPlainText(self.tr(
                "{0} dictionaries currently installed"
            ).format(len(self._currDicts)))

        return True

    ##
    #  Events
    ##

    def closeEvent(self, event: QCloseEvent) -> None:
        """Capture the user closing the window."""
        event.accept()
        self.deleteLater()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _loadDictionaries(self) -> None:
        """Check for latest release."""
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))

        data = self._callGitHubAPI("contents/")
        dictionaries = []
        if isinstance(data, list):
            for entry in data:
                if isinstance(entry, dict) and entry.get("type", "") == "dir":
                    code = entry.get("name", "")
                    name = QLocale.languageToString(QLocale(code).language())
                    if code not in (".github", "util"):
                        dictionaries.append((code, code if name == "C" else name))

        self.infoBox.appendPlainText(self.tr(
            "{0} dictionaries available for download"
        ).format(len(dictionaries)))

        for code, name in dictionaries:
            trItem = QTreeWidgetItem()
            trItem.setText(self.C_CODE, code)
            trItem.setText(self.C_NAME, name)
            trItem.setText(self.C_STATE, self._trHave if code in self._currDicts else "")
            self.listBox.addTopLevelItem(trItem)

        qApp.restoreOverrideCursor()

        return

    @pyqtSlot()
    def _downloadDictionary(self) -> None:
        """Download selected dictionary."""
        items = self.listBox.selectedItems()
        if not items or not (temp := self.pathBox.text()):
            return

        path = Path(temp) / "hunspell"
        code = items[0].text(self.C_CODE)
        data = self._callGitHubAPI(f"contents/{code}")
        files = (f"{code}.aff", f"{code}.dic")

        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception:
            logger.error("Failed to create download directory")
            logException()
            return

        if isinstance(data, list):
            for entry in data:
                if isinstance(entry, dict) and entry.get("type", "") == "file":
                    name = entry.get("name", "")
                    url = entry.get("download_url")
                    size = checkInt(entry.get("size"), 0)
                    if url and name in files:
                        if self._downloadFile(url, path / name):
                            self.infoBox.appendPlainText(self.tr(
                                "Downloaded '{0}' of size {1}B"
                            ).format(name, formatInt(size)))

        items[0].setText(self.C_STATE, self._trHave)
        self._currDicts.add(code)

        return

    @pyqtSlot()
    def _deleteDictionary(self) -> None:
        """Delete selected dictionary."""
        items = self.listBox.selectedItems()
        if not items or not (temp := self.pathBox.text()):
            return

        code = items[0].text(self.C_CODE)
        files = (
            Path(temp) / "hunspell" / f"{code}.aff",
            Path(temp) / "hunspell" / f"{code}.dic",
        )
        for item in files:
            try:
                item.unlink()
            except Exception:
                logger.error("Could not delete: %s", item)

        items[0].setText(self.C_STATE, "")
        self._currDicts.remove(code)

        return

    @pyqtSlot()
    def _openLocation(self) -> None:
        """Open the dictionary folder."""
        path = self.pathBox.text()
        if Path(path).is_dir():
            QDesktopServices.openUrl(
                QUrl(urljoin("file:", pathname2url(path)))
            )
        else:
            SHARED.error("Path not found.")
        return

    @pyqtSlot()
    def _doClose(self) -> None:
        """Close the dialog."""
        self.close()
        return

    ##
    #  Internal Functions
    ##

    def _callGitHubAPI(self, path: str) -> dict:
        """Make a call to the GitHub API."""
        req = Request(f"https://api.github.com/repos/vkbo/dictionaries/{path}")
        req.add_header("User-Agent", nwConst.USER_AGENT)
        req.add_header("Accept", "application/vnd.github.v3+json")
        try:
            return json.loads(urlopen(req, timeout=30).read().decode())
        except Exception:
            logger.error("Failed to get data from GitHub API")
            logException()
        return {}

    def _downloadFile(self, url: str, path: Path) -> bool:
        """Download a file to a specific location."""
        req = Request(url)
        req.add_header("User-Agent", nwConst.USER_AGENT)
        # req.add_header("Accept", "application/vnd.github.v3+json")
        try:
            with open(path, mode="wb") as of:
                of.write(urlopen(req, timeout=60).read())
        except Exception:
            logger.error("Failed to get data from GitHub API")
            logException()
            return False
        return True

# END Class GuiDictionaries
