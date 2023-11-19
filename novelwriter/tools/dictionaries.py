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
from PyQt5.QtCore import QUrl, Qt, pyqtSlot
from PyQt5.QtWidgets import (
    QAbstractItemView, QDialog, QDialogButtonBox, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPlainTextEdit, QPushButton, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QWidget, qApp
)

from novelwriter import CONFIG, SHARED
from novelwriter.error import logException
from novelwriter.common import formatInt, getFileSize
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
        self._availDicts = {}
        self._trHave = self.tr("Downloaded")
        self._trFailed = self.tr("Failed")

        # Info
        self.pathLabel = QLabel(self.tr("Download Path"))
        self.pathBox = QLineEdit(self)
        self.pathBox.setReadOnly(True)
        self.pathButton = QPushButton(self)
        self.pathButton.setIcon(SHARED.theme.getIcon("browse"))
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
        self.checkButton.setText("List Dictionaries")
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

        data = self._getJson("https://vkbo.github.io/dictionaries/dictionaries.json")
        dicts = {}
        if isinstance(data, dict):
            for code, entry in data.items():
                if isinstance(entry, dict):
                    name = entry.get("name", "")
                    aff = entry.get("aff", "")
                    dic = entry.get("dic", "")
                    if code and name and aff and dic:
                        dicts[code] = (name, aff, dic)

        self._availDicts = dicts
        self.infoBox.appendPlainText(self.tr(
            "{0} dictionaries available for download"
        ).format(len(dicts)))

        for code, (name, aff, dic) in dicts.items():
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
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception:
            logger.error("Failed to create download directory")
            logException()
            return

        code = items[0].text(self.C_CODE)
        _, aff, dic = self._availDicts.get(code, ("", "", ""))
        files = [
            (aff, path / f"{code}.aff"),
            (dic, path / f"{code}.dic"),
        ]
        for url, output in files:
            if self._downloadFile(url, output):
                self.infoBox.appendPlainText(self.tr(
                    "Downloaded '{0}' of size {1}B"
                ).format(output.name, formatInt(getFileSize(output))))

        if files[0][1].is_file() and files[1][1].is_file():
            items[0].setText(self.C_STATE, self._trHave)
            self._currDicts.add(code)
        else:
            items[0].setText(self.C_STATE, self._trFailed)

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
                self.infoBox.appendPlainText(self.tr(
                    "Deleted '{0}'"
                ).format(item.name))
            except Exception:
                logger.error("Could not delete: %s", item)
                return

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

    def _getJson(self, url: str) -> dict:
        """Make a call to the GitHub API."""
        req = Request(url)
        req.add_header("User-Agent", nwConst.USER_AGENT)
        req.add_header("Accept", "application/json")
        try:
            return json.loads(urlopen(req, timeout=30).read().decode())
        except Exception:
            logger.error("Failed to get JSON data")
            logException()
        return {}

    def _downloadFile(self, url: str, path: Path) -> bool:
        """Download a file to a specific location."""
        if url:
            req = Request(url)
            req.add_header("User-Agent", nwConst.USER_AGENT)
            req.add_header("Accept", "application/vnd.github.v3+json")
            try:
                with open(path, mode="wb") as of:
                    of.write(urlopen(req, timeout=60).read())
                return True
            except Exception:
                logger.error("Failed to get data from GitHub API")
                logException()
        return False

# END Class GuiDictionaries
