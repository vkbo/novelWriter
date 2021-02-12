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

from PyQt5.QtWidgets import (
    QDialog, QDialogButtonBox, QVBoxLayout, QListWidget, QAbstractItemView
)

from nw.constants import nwFiles

logger = logging.getLogger(__name__)

class GuiWordList(QDialog):

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiWordList ...")
        self.setObjectName("GuiWordList")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.optState   = theProject.optState

        self.setWindowTitle("Project Word List")

        wW = self.mainConf.pxInt(250)
        wH = self.mainConf.pxInt(300)

        self.setMinimumWidth(wW)
        self.setMinimumHeight(wH)
        self.resize(
            self.mainConf.pxInt(self.optState.getInt("GuiWordList", "winWidth",  wW)),
            self.mainConf.pxInt(self.optState.getInt("GuiWordList", "winHeight", wH))
        )

        # Main Widgets
        # ============

        self.listBox = QListWidget()
        self.listBox.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.listBox.setSortingEnabled(True)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Close)
        self.buttonBox.accepted.connect(self._doSave)
        self.buttonBox.rejected.connect(self._doClose)

        # Assemble
        # ========

        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.listBox, 1)
        self.outerBox.addWidget(self.buttonBox, 0)

        self.setLayout(self.outerBox)

        self._loadWordList()

        logger.debug("GuiWordList initialisation complete")

        return

    ##
    #  Slots
    ##

    def _doSave(self):
        """Save the new word list and close.
        """
        self._saveGuiSettings()
        self.accept()
        return

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
