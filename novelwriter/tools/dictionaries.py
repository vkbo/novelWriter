"""
novelWriter – GUI Dictionary Downloader
=======================================

File History:
Created: 2023-11-19 [2.2rc1] GuiDictionaries

This file is a part of novelWriter
Copyright (C) 2023 Veronica Berglyd Olsen and novelWriter contributors

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

from pathlib import Path
from zipfile import ZipFile

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QCloseEvent, QTextCursor
from PyQt6.QtWidgets import (
    QApplication, QDialogButtonBox, QFileDialog, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import formatFileFilter, formatInt, getFileSize, openExternalPath
from novelwriter.error import formatException
from novelwriter.extensions.modified import NIconToolButton, NNonBlockingDialog
from novelwriter.types import QtDialogClose, QtHexArgb

logger = logging.getLogger(__name__)


class GuiDictionaries(NNonBlockingDialog):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiDictionaries")
        self.setObjectName("GuiDictionaries")
        self.setWindowTitle(self.tr("Add Dictionaries"))

        self._installPath = None
        self._currDicts = set()

        iSz = SHARED.theme.baseIconSize

        self.setMinimumWidth(500)
        self.setMinimumHeight(300)

        # Hunspell Dictionaries
        loUrl = "https://extensions.libreoffice.org"
        ooUrl = "https://extensions.openoffice.org"
        self.huInfo = QLabel("<br>".join([
            self.tr("Download a dictionary from one of the links, and add it below."),
            f"&nbsp;\u203a <a href='{loUrl}'>{loUrl}</a>",
            f"&nbsp;\u203a <a href='{ooUrl}'>{ooUrl}</a>",
        ]), self)
        self.huInfo.setOpenExternalLinks(True)
        self.huInfo.setWordWrap(True)
        self.huInput = QLineEdit(self)
        self.huBrowse = NIconToolButton(self, iSz, "browse")
        self.huBrowse.clicked.connect(self._doBrowseHunspell)
        self.huImport = QPushButton(self.tr("Add Dictionary"), self)
        self.huImport.setIcon(SHARED.theme.getIcon("add", "green"))
        self.huImport.clicked.connect(self._doImportHunspell)

        self.huPathBox = QHBoxLayout()
        self.huPathBox.addWidget(self.huInput)
        self.huPathBox.addWidget(self.huBrowse)
        self.huPathBox.setSpacing(4)
        self.huAddBox = QHBoxLayout()
        self.huAddBox.addStretch(1)
        self.huAddBox.addWidget(self.huImport)

        # Install Path
        self.inInfo = QLabel(self.tr("Dictionary install location"), self)
        self.inPath = QLineEdit(self)
        self.inPath.setReadOnly(True)
        self.inBrowse = NIconToolButton(self, iSz, "browse")
        self.inBrowse.clicked.connect(self._doOpenInstallLocation)

        self.inBox = QHBoxLayout()
        self.inBox.addWidget(self.inPath)
        self.inBox.addWidget(self.inBrowse)
        self.inBox.setSpacing(4)

        # Info Box
        self.infoBox = QPlainTextEdit(self)
        self.infoBox.setReadOnly(True)
        self.infoBox.setFrameStyle(QFrame.Shape.NoFrame)

        # Buttons
        self.buttonBox = QDialogButtonBox(QtDialogClose, self)
        self.buttonBox.rejected.connect(self.reject)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.huInfo, 0)
        self.outerBox.addLayout(self.huPathBox, 0)
        self.outerBox.addLayout(self.huAddBox, 0)
        self.outerBox.addSpacing(8)
        self.outerBox.addWidget(self.inInfo, 0)
        self.outerBox.addLayout(self.inBox, 0)
        self.outerBox.addWidget(self.infoBox, 1)
        self.outerBox.addSpacing(8)
        self.outerBox.addWidget(self.buttonBox, 0)

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
            self._installPath = Path(path).resolve()
            self._installPath.mkdir(exist_ok=True, parents=True)
        except Exception:
            logger.error("Could not get enchant path")
            return False

        if path.is_dir():
            self.inPath.setText(str(path))
            hunspell = path / "hunspell"
            if hunspell.is_dir():
                self._currDicts = set(
                    i.stem for i in hunspell.iterdir() if i.is_file() and i.suffix == ".aff"
                )
            self._appendLog(self.tr(
                "Additional dictionaries found: {0}"
            ).format(len(self._currDicts)))

        QApplication.processEvents()
        self.adjustSize()

        return True

    ##
    #  Events
    ##

    def closeEvent(self, event: QCloseEvent) -> None:
        """Capture the user closing the window."""
        event.accept()
        self.softDelete()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _doBrowseHunspell(self) -> None:
        """Browse for a Free/Libre Office dictionary."""
        ffilter = formatFileFilter([
            (self.tr("Free or Libre Office extension"), "*.sox *.oxt"), "*"
        ])
        soxFile, _ = QFileDialog.getOpenFileName(
            self, self.tr("Browse Files"), str(CONFIG.homePath()), filter=ffilter
        )
        if soxFile:
            path = Path(soxFile).absolute()
            self.huInput.setText(str(path))
        return

    @pyqtSlot()
    def _doImportHunspell(self) -> None:
        """Import a hunspell dictionary from .sox or .oxt file."""
        procErr = self.tr("Could not process dictionary file")
        if self._installPath:
            temp = self.huInput.text()
            if temp and (path := Path(temp)).is_file():
                try:
                    hunspell = self._installPath / "hunspell"
                    hunspell.mkdir(exist_ok=True)
                    nAff, nDic = self._extractDicts(path, hunspell)
                    if nAff == 0 or nDic == 0:
                        self._appendLog(procErr, err=True)
                except Exception as exc:
                    self._appendLog(procErr, err=True)
                    self._appendLog(formatException(exc), err=True)
            else:
                self._appendLog(procErr, err=True)
        return

    @pyqtSlot()
    def _doOpenInstallLocation(self) -> None:
        """Open the dictionary folder."""
        if not openExternalPath(Path(self.inPath.text())):
            SHARED.error("Path not found.")
        return

    ##
    #  Internal Functions
    ##

    def _extractDicts(self, path: Path, output: Path) -> tuple[int, int]:
        """Extract a zip archive and return the number of .aff and .dic
        files found in it.
        """
        nAff = nDic = 0
        with ZipFile(path, mode="r") as zipObj:
            for item in zipObj.namelist():
                zPath = Path(item)
                if zPath.suffix not in (".aff", ".dic"):
                    continue
                nAff += 1 if zPath.suffix == ".aff" else 0
                nDic += 1 if zPath.suffix == ".dic" else 0
                with zipObj.open(item) as zF:
                    oPath = output / zPath.name
                    oPath.write_bytes(zF.read())
                    size = getFileSize(oPath)
                    self._appendLog(self.tr(
                        "Added: {0} [{1}B]"
                    ).format(zPath.name, formatInt(size)))
        return nAff, nDic

    def _appendLog(self, text: str, err: bool = False) -> None:
        """Append a line to the log output."""
        cursor = self.infoBox.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        if cursor.position() > 0:
            cursor.insertText("\n")
        textCol = SHARED.theme.errorText if err else self.palette().text().color()
        cursor.insertHtml(f"<font style='color: {textCol.name(QtHexArgb)}'>{text}</font>")
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.deleteChar()
        self.infoBox.setTextCursor(cursor)
        return
