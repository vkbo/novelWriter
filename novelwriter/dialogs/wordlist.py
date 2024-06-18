"""
novelWriter – GUI User Wordlist
===============================

File History:
Created: 2021-02-12 [1.2rc1] GuiWordList

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

import logging

from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import (
    QAbstractItemView, QApplication, QDialogButtonBox, QFileDialog,
    QHBoxLayout, QLineEdit, QListWidget, QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import formatFileFilter
from novelwriter.core.spellcheck import UserDictionary
from novelwriter.extensions.configlayout import NColourLabel
from novelwriter.extensions.modified import NDialog, NIconToolButton
from novelwriter.types import QtDialogClose, QtDialogSave

logger = logging.getLogger(__name__)


class GuiWordList(NDialog):

    newWordListReady = pyqtSignal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiWordList")
        self.setObjectName("GuiWordList")
        self.setWindowTitle(self.tr("Project Word List"))

        iSz = SHARED.theme.baseIconSize
        mS = CONFIG.pxInt(250)
        wW = CONFIG.pxInt(320)
        wH = CONFIG.pxInt(340)

        self.setMinimumWidth(mS)
        self.setMinimumHeight(mS)
        self.resize(
            CONFIG.pxInt(SHARED.project.options.getInt("GuiWordList", "winWidth",  wW)),
            CONFIG.pxInt(SHARED.project.options.getInt("GuiWordList", "winHeight", wH))
        )

        # Header
        self.headLabel = NColourLabel(
            self.tr("Project Word List"), self, color=SHARED.theme.helpText,
            scale=NColourLabel.HEADER_SCALE
        )

        self.importButton = NIconToolButton(self, iSz, "import")
        self.importButton.setToolTip(self.tr("Import words from text file"))
        self.importButton.clicked.connect(self._importWords)

        self.exportButton = NIconToolButton(self, iSz, "export")
        self.exportButton.setToolTip(self.tr("Export words to text file"))
        self.exportButton.clicked.connect(self._exportWords)

        self.headerBox = QHBoxLayout()
        self.headerBox.addWidget(self.headLabel, 1)
        self.headerBox.addWidget(self.importButton, 0)
        self.headerBox.addWidget(self.exportButton, 0)

        # List Box
        self.listBox = QListWidget(self)
        self.listBox.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)
        self.listBox.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.listBox.setSortingEnabled(True)

        # Add/Remove Form
        self.newEntry = QLineEdit(self)

        self.addButton = NIconToolButton(self, iSz, "add")
        self.addButton.clicked.connect(self._doAdd)

        self.delButton = NIconToolButton(self, iSz, "remove")
        self.delButton.clicked.connect(self._doDelete)

        self.editBox = QHBoxLayout()
        self.editBox.addWidget(self.newEntry, 1)
        self.editBox.addWidget(self.addButton, 0)
        self.editBox.addWidget(self.delButton, 0)

        # Buttons
        self.buttonBox = QDialogButtonBox(QtDialogSave | QtDialogClose, self)
        self.buttonBox.accepted.connect(self._doSave)
        self.buttonBox.rejected.connect(self.reject)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.addLayout(self.headerBox, 0)
        self.outerBox.addWidget(self.listBox, 1)
        self.outerBox.addLayout(self.editBox, 0)
        self.outerBox.addSpacing(CONFIG.pxInt(12))
        self.outerBox.addWidget(self.buttonBox, 0)
        self.outerBox.setSpacing(CONFIG.pxInt(4))

        self.setLayout(self.outerBox)

        self._loadWordList()

        logger.debug("Ready: GuiWordList")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiWordList")
        return

    ##
    #  Events
    ##

    def closeEvent(self, event: QCloseEvent) -> None:
        """Capture the close event and perform cleanup."""
        self._saveGuiSettings()
        event.accept()
        self.softDelete()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _doAdd(self) -> None:
        """Add a new word to the word list."""
        word = self.newEntry.text().strip()
        self.newEntry.setText("")
        self.listBox.clearSelection()
        self._addWord(word)
        if items := self.listBox.findItems(word, Qt.MatchFlag.MatchExactly):
            self.listBox.setCurrentItem(items[0])
            self.listBox.scrollToItem(items[0], QAbstractItemView.ScrollHint.PositionAtCenter)
        return

    @pyqtSlot()
    def _doDelete(self) -> None:
        """Delete the selected items."""
        for item in self.listBox.selectedItems():
            self.listBox.takeItem(self.listBox.row(item))
        return

    @pyqtSlot()
    def _doSave(self) -> None:
        """Save the new word list and close."""
        userDict = UserDictionary(SHARED.project)
        for word in self._listWords():
            userDict.add(word)
        userDict.save()
        self.newWordListReady.emit()
        QApplication.processEvents()
        self.close()
        return

    @pyqtSlot()
    def _importWords(self) -> None:
        """Import words from file."""
        SHARED.info(self.tr(
            "Note: The import file must be a plain text file with UTF-8 or ASCII encoding."
        ))
        ffilter = formatFileFilter(["*.txt", "*"])
        path, _ = QFileDialog.getOpenFileName(
            self, self.tr("Import File"), str(CONFIG.homePath()), filter=ffilter
        )
        if path:
            try:
                with open(path, mode="r", encoding="utf-8") as fo:
                    words = set(w.strip() for w in fo.read().split())
            except Exception as exc:
                SHARED.error("Could not read file.", exc=exc)
                return
            for word in words:
                self._addWord(word)
        return

    @pyqtSlot()
    def _exportWords(self) -> None:
        """Export words to file."""
        path, _ = QFileDialog.getSaveFileName(
            self, self.tr("Export File"), str(CONFIG.homePath())
        )
        if path:
            try:
                path = Path(path).with_suffix(".txt")
                with open(path, mode="w", encoding="utf-8") as fo:
                    fo.write("\n".join(self._listWords()))
            except Exception as exc:
                SHARED.error("Could not write file.", exc=exc)
        return

    ##
    #  Internal Functions
    ##

    def _loadWordList(self) -> None:
        """Load the project's word list, if it exists."""
        userDict = UserDictionary(SHARED.project)
        userDict.load()
        self.listBox.clear()
        for word in userDict:
            self.listBox.addItem(word)
        return

    def _saveGuiSettings(self) -> None:
        """Save GUI settings."""
        winWidth  = CONFIG.rpxInt(self.width())
        winHeight = CONFIG.rpxInt(self.height())

        logger.debug("Saving State: GuiWordList")
        pOptions = SHARED.project.options
        pOptions.setValue("GuiWordList", "winWidth",  winWidth)
        pOptions.setValue("GuiWordList", "winHeight", winHeight)

        return

    def _addWord(self, word: str) -> None:
        """Add a single word to the list."""
        if word and not self.listBox.findItems(word, Qt.MatchFlag.MatchExactly):
            self.listBox.addItem(word)
            self._changed = True
        return

    def _listWords(self) -> list[str]:
        """List all words in the list box."""
        result = []
        for i in range(self.listBox.count()):
            if (item := self.listBox.item(i)) and (word := item.text().strip()):
                result.append(word)
        return result
