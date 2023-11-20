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

import logging

from pathlib import Path
from zipfile import ZipFile
from urllib.parse import urljoin
from urllib.request import pathname2url

from PyQt5.QtGui import QCloseEvent, QDesktopServices, QTextCursor
from PyQt5.QtCore import QUrl, pyqtSlot
from PyQt5.QtWidgets import (
    QDialog, QDialogButtonBox, QFileDialog, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget, qApp
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import formatInt, getFileSize

logger = logging.getLogger(__name__)


class GuiDictionaries(QDialog):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiDictionaries")
        self.setObjectName("GuiDictionaries")
        self.setWindowTitle(self.tr("Add Dictionaries"))

        self._installPath = None
        self._currDicts = set()

        iPx = CONFIG.pxInt(4)
        mPx = CONFIG.pxInt(8)
        sPx = CONFIG.pxInt(16)

        self.setMinimumWidth(CONFIG.pxInt(500))
        self.setMinimumHeight(CONFIG.pxInt(300))

        # Hunspell Dictionaries
        foUrl = "https://www.freeoffice.com/en/download/dictionaries"
        loUrl = "https://extensions.libreoffice.org"
        self.huInfo = QLabel("<br>".join([
            self.tr("Download a dictionary from one of the links, and add it below."),
            f"&nbsp;\u203a <a href='{foUrl}'>{foUrl}</a>",
            f"&nbsp;\u203a <a href='{loUrl}'>{loUrl}</a>",
        ]))
        self.huInfo.setOpenExternalLinks(True)
        self.huInfo.setWordWrap(True)
        self.huInput = QLineEdit(self)
        self.huBrowse = QPushButton(self)
        self.huBrowse.setIcon(SHARED.theme.getIcon("browse"))
        self.huBrowse.clicked.connect(self._doBrowseHunspell)
        self.huImport = QPushButton(self.tr("Add Dictionary"), self)
        self.huImport.setIcon(SHARED.theme.getIcon("add"))
        self.huImport.clicked.connect(self._doImportHunspell)

        self.huPathBox = QHBoxLayout()
        self.huPathBox.addWidget(self.huInput)
        self.huPathBox.addWidget(self.huBrowse)
        self.huPathBox.setSpacing(iPx)
        self.huAddBox = QHBoxLayout()
        self.huAddBox.addStretch(1)
        self.huAddBox.addWidget(self.huImport)

        # Install Path
        self.inInfo = QLabel(self.tr("Dictionary install location"))
        self.inPath = QLineEdit(self)
        self.inPath.setReadOnly(True)
        self.inBrowse = QPushButton(self)
        self.inBrowse.setIcon(SHARED.theme.getIcon("browse"))
        self.inBrowse.clicked.connect(self._doOpenInstallLocation)

        self.inBox = QHBoxLayout()
        self.inBox.addWidget(self.inPath)
        self.inBox.addWidget(self.inBrowse)
        self.inBox.setSpacing(iPx)

        # Info Box
        self.infoBox = QPlainTextEdit(self)
        self.infoBox.setReadOnly(True)
        self.infoBox.setFixedHeight(4*SHARED.theme.fontPixelSize)
        self.infoBox.setFrameStyle(QFrame.Shape.NoFrame)

        # Buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttonBox.rejected.connect(self._doClose)

        # Assemble
        self.innerBox = QVBoxLayout()
        self.innerBox.addWidget(self.huInfo)
        self.innerBox.addLayout(self.huPathBox)
        self.innerBox.addLayout(self.huAddBox)
        self.innerBox.addSpacing(mPx)
        self.innerBox.addWidget(self.inInfo)
        self.innerBox.addLayout(self.inBox)
        self.innerBox.addWidget(self.infoBox)
        self.innerBox.setSpacing(iPx)

        self.outerBox = QVBoxLayout()
        self.outerBox.addLayout(self.innerBox, 0)
        self.outerBox.addStretch(1)
        self.outerBox.addWidget(self.buttonBox, 0)
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

        self._installPath = Path(path).resolve()
        if path.is_dir():
            self.inPath.setText(str(path))
            hunspell = path / "hunspell"
            if hunspell.is_dir():
                self._currDicts = set(
                    i.stem for i in hunspell.iterdir() if i.is_file() and i.suffix == ".aff"
                )
            self._appendLog(self.tr(
                "{0} additional dictionaries currently installed"
            ).format(len(self._currDicts)))

        qApp.processEvents()
        self.adjustSize()

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
    def _doBrowseHunspell(self):
        """Browse for a Free/Libre Office dictionary."""
        extFilter = [
            self.tr("Free or Libre Office extension ({0})").format("*.sox *.oxt"),
            self.tr("All files ({0})").format("*"),
        ]
        soxFile, _ = QFileDialog.getOpenFileName(
            self, self.tr("Browse Files"), "", filter=";;".join(extFilter)
        )
        if soxFile:
            path = Path(soxFile).absolute()
            self.huInput.setText(str(path))
        return

    @pyqtSlot()
    def _doImportHunspell(self):
        """Import a hunspell dictionary from .sox or .oxt file."""
        temp = self.huInput.text()
        output = self._installPath
        if not output:
            return
        if output and temp and (path := Path(temp)).is_file():
            hunspell = output / "hunspell"
            hunspell.mkdir(exist_ok=True)
            try:
                with ZipFile(path, mode="r") as zipObj:
                    for item in zipObj.namelist():
                        zPath = Path(item)
                        if zPath.suffix in (".aff", ".dic"):
                            with zipObj.open(item) as zF:
                                oPath = hunspell / zPath.name
                                oPath.write_bytes(zF.read())
                                size = getFileSize(oPath)
                                self._appendLog(self.tr(
                                    "Added: {0} [{1}B]"
                                ).format(zPath.name, formatInt(size)))
            except Exception as exc:
                SHARED.error(self.tr("Could not process dictionary file."), exc=exc)
        else:
            SHARED.error(self.tr("File not found."))
        return

    @pyqtSlot()
    def _doOpenInstallLocation(self) -> None:
        """Open the dictionary folder."""
        path = self.inPath.text()
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

    def _appendLog(self, text: str) -> None:
        """Append a line to the log output."""
        self.infoBox.moveCursor(QTextCursor.MoveOperation.End)
        if self.infoBox.textCursor().position() > 0:
            self.infoBox.insertPlainText("\n")
        self.infoBox.insertPlainText(text)
        self.infoBox.moveCursor(QTextCursor.MoveOperation.End)
        return

# END Class GuiDictionaries
