# -*- coding: utf-8 -*-
"""
novelWriter – GUI User Wordlist
===============================
Class holding the user's wordlist dialog

File History:
Created: 2021-02-12 [1.2b1]

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

import nw
import logging
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QListWidget,
    QAbstractItemView, QPushButton, QLineEdit, QLabel
)

from nw.constants import nwFiles, nwAlert

logger = logging.getLogger(__name__)

class GuiWordList(QDialog):

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiWordList ...")
        self.setObjectName("GuiWordList")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
        self.theProject = theProject
        self.optState   = theProject.optState

        self.setWindowTitle("Project Word List")

        mS = self.mainConf.pxInt(250)
        wW = self.mainConf.pxInt(320)
        wH = self.mainConf.pxInt(340)

        self.setMinimumWidth(mS)
        self.setMinimumHeight(mS)
        self.resize(
            self.mainConf.pxInt(self.optState.getInt("GuiWordList", "winWidth",  wW)),
            self.mainConf.pxInt(self.optState.getInt("GuiWordList", "winHeight", wH))
        )

        # Main Widgets
        # ============

        self.headLabel = QLabel("<b>Project Word List</b>")

        self.listBox = QListWidget()
        self.listBox.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.listBox.setSortingEnabled(True)

        self.newEntry = QLineEdit()

        self.addButton = QPushButton(self.theTheme.getIcon("add"), "")
        self.addButton.setToolTip("Add new entry")
        self.addButton.clicked.connect(self._doAdd)

        self.delButton = QPushButton(self.theTheme.getIcon("remove"), "")
        self.delButton.setToolTip("Delete selected entry")
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
        self.outerBox.addSpacing(self.mainConf.pxInt(8))
        self.outerBox.addWidget(self.listBox, 1)
        self.outerBox.addLayout(self.editBox, 0)
        self.outerBox.addSpacing(self.mainConf.pxInt(12))
        self.outerBox.addWidget(self.buttonBox, 0)

        self.setLayout(self.outerBox)

        self._loadWordList()

        logger.debug("GuiWordList initialisation complete")

        return

    ##
    #  Slots
    ##

    def _doAdd(self):
        """Add a new word to the word list.
        """
        newWord = self.newEntry.text().strip()
        if newWord == "":
            self.theParent.makeAlert("Cannot add a blank word.", nwAlert.ERROR)
            return False

        if self.listBox.findItems(newWord, Qt.MatchExactly):
            self.theParent.makeAlert(
                "The word '%s' is already in the word list." % newWord, nwAlert.ERROR
            )
            return False

        self.listBox.addItem(newWord)
        self.newEntry.setText("")

        return True

    def _doDelete(self):
        """Delete the selected item.
        """
        selItem = self.listBox.selectedItems()
        if selItem:
            self.listBox.takeItem(self.listBox.row(selItem[0]))
        return

    def _doSave(self):
        """Save the new word list and close.
        """
        self._saveGuiSettings()

        dctFile = os.path.join(self.theProject.projMeta, nwFiles.PROJ_DICT)
        tmpFile = dctFile + "~"

        try:
            with open(tmpFile, mode="w", encoding="utf8") as outFile:
                for i in range(self.listBox.count()):
                    outFile.write(self.listBox.item(i).text() + "\n")

        except Exception:
            logger.error("Could not save new word list")
            nw.logException()
            self.reject()
            return False

        if os.path.isfile(dctFile):
            os.unlink(dctFile)
        os.rename(tmpFile, dctFile)
        self.accept()

        return True

    def _doClose(self):
        """Close without saving the word list.
        """
        self._saveGuiSettings()
        self.reject()
        return

    ##
    #  Internal Functions
    ##

    def _loadWordList(self):
        """Load the project's word list, if it exists.
        """
        self.listBox.clear()

        wordList = os.path.join(self.theProject.projMeta, nwFiles.PROJ_DICT)
        if not os.path.isfile(wordList):
            logger.debug("No project dictionary file found")
            return False

        with open(wordList, mode="r", encoding="utf8") as inFile:
            for inLine in inFile:
                theWord = inLine.strip()
                if len(theWord) == 0:
                    continue
                self.listBox.addItem(theWord)

        return True

    def _saveGuiSettings(self):
        """Save GUI settings.
        """
        winWidth  = self.mainConf.rpxInt(self.width())
        winHeight = self.mainConf.rpxInt(self.height())

        self.optState.setValue("GuiWordList", "winWidth",  winWidth)
        self.optState.setValue("GuiWordList", "winHeight", winHeight)

        return

# END Class GuiWordList
