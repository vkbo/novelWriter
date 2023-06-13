"""
novelWriter – GUI User Wordlist
===============================

File History:
Created: 2021-02-12 [1.2rc1]

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

from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAbstractItemView, QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout
)

from novelwriter import CONFIG
from novelwriter.enum import nwAlert
from novelwriter.core.spellcheck import UserDictionary

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


class GuiWordList(QDialog):

    def __init__(self, mainGui: GuiMain):
        super().__init__(parent=mainGui)

        logger.debug("Create: GuiWordList")
        self.setObjectName("GuiWordList")

        self.mainGui    = mainGui
        self.mainTheme  = mainGui.mainTheme
        self.theProject = mainGui.theProject

        self.setWindowTitle(self.tr("Project Word List"))

        mS = CONFIG.pxInt(250)
        wW = CONFIG.pxInt(320)
        wH = CONFIG.pxInt(340)
        pOptions = self.theProject.options

        self.setMinimumWidth(mS)
        self.setMinimumHeight(mS)
        self.resize(
            CONFIG.pxInt(pOptions.getInt("GuiWordList", "winWidth",  wW)),
            CONFIG.pxInt(pOptions.getInt("GuiWordList", "winHeight", wH))
        )

        # Main Widgets
        # ============

        self.headLabel = QLabel("<b>%s</b>" % self.tr("Project Word List"))

        self.listBox = QListWidget()
        self.listBox.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.listBox.setSortingEnabled(True)

        self.newEntry = QLineEdit()

        self.addButton = QPushButton(self.mainTheme.getIcon("add"), "")
        self.addButton.clicked.connect(self._doAdd)

        self.delButton = QPushButton(self.mainTheme.getIcon("remove"), "")
        self.delButton.clicked.connect(self._doDelete)

        self.editBox = QHBoxLayout()
        self.editBox.addWidget(self.newEntry, 1)
        self.editBox.addWidget(self.addButton, 0)
        self.editBox.addWidget(self.delButton, 0)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Close)
        self.buttonBox.accepted.connect(self._doSave)
        self.buttonBox.rejected.connect(self._doClose)

        # Assemble
        # ========

        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.headLabel)
        self.outerBox.addSpacing(CONFIG.pxInt(8))
        self.outerBox.addWidget(self.listBox, 1)
        self.outerBox.addLayout(self.editBox, 0)
        self.outerBox.addSpacing(CONFIG.pxInt(12))
        self.outerBox.addWidget(self.buttonBox, 0)

        self.setLayout(self.outerBox)

        self._loadWordList()

        logger.debug("Ready: GuiWordList")

        return

    def __del__(self):  # pragma: no cover
        logger.debug("Delete: GuiWordList")
        return

    ##
    #  Slots
    ##

    def _doAdd(self):
        """Add a new word to the word list."""
        word = self.newEntry.text().strip()
        if word == "":
            self.mainGui.makeAlert(self.tr(
                "Cannot add a blank word."
            ), nwAlert.ERROR)
            return

        if self.listBox.findItems(word, Qt.MatchExactly):
            self.mainGui.makeAlert(self.tr(
                "The word '{0}' is already in the word list."
            ).format(word), nwAlert.ERROR)
            return

        self.listBox.addItem(word)
        self.newEntry.setText("")

        return

    def _doDelete(self):
        """Delete the selected item."""
        selItem = self.listBox.selectedItems()
        if selItem:
            self.listBox.takeItem(self.listBox.row(selItem[0]))
        return

    def _doSave(self):
        """Save the new word list and close."""
        self._saveGuiSettings()
        userDict = UserDictionary(self.theProject)
        for i in range(self.listBox.count()):
            item = self.listBox.item(i)
            if isinstance(item, QListWidgetItem):
                word = item.text().strip()
                if word:
                    userDict.add(word)
        userDict.save()
        self.accept()
        return True

    def _doClose(self):
        """Close without saving the word list."""
        self._saveGuiSettings()
        self.reject()
        return

    ##
    #  Internal Functions
    ##

    def _loadWordList(self):
        """Load the project's word list, if it exists."""
        userDict = UserDictionary(self.theProject)
        userDict.load()
        self.listBox.clear()
        for word in userDict:
            if word:
                self.listBox.addItem(word)
        return

    def _saveGuiSettings(self):
        """Save GUI settings."""
        winWidth  = CONFIG.rpxInt(self.width())
        winHeight = CONFIG.rpxInt(self.height())

        pOptions = self.theProject.options
        pOptions.setValue("GuiWordList", "winWidth",  winWidth)
        pOptions.setValue("GuiWordList", "winHeight", winHeight)

        return

# END Class GuiWordList
