# -*- coding: utf-8 -*-
"""novelWriter GUI Main Window SearchBar

 novelWriter – GUI Main Window SearchBar
=========================================
 Class holding the main window search bar

 File History:
 Created: 2019-09-29 [0.2.1] GuiSearchBar
 Created: 2019-10-31 [0.3.2] GuiNoticeBar
 Created: 2020-04-25 [0.4.5] GuiDocTitleBar

 This file is a part of novelWriter
 Copyright 2020, Veronica Berglyd Olsen

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

import logging
import nw

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import (
    qApp, QFrame, QGridLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout
)

from nw.constants import nwDocAction, nwUnicode

logger = logging.getLogger(__name__)

class GuiSearchBar(QFrame):

    def __init__(self, theParent):
        QFrame.__init__(self, theParent)

        logger.debug("Initialising GuiSearchBar ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
        self.repVisible = False

        self.setContentsMargins(0,0,0,0)

        self.mainBox = QGridLayout(self)
        self.setLayout(self.mainBox)

        self.searchBox     = QLineEdit()
        self.replaceBox    = QLineEdit()
        self.searchLabel   = QLabel("Search")
        self.replaceLabel  = QLabel("Replace")
        self.closeButton   = QPushButton(self.theTheme.getIcon("close"),"")
        self.searchButton  = QPushButton(self.theTheme.getIcon("search"),"")
        self.replaceButton = QPushButton(self.theTheme.getIcon("search-replace"),"")

        self.closeButton.clicked.connect(self._doClose)
        self.searchButton.clicked.connect(self._doSearch)
        self.replaceButton.clicked.connect(self._doReplace)
        self.searchBox.returnPressed.connect(self._doSearch)
        self.replaceBox.returnPressed.connect(self._doSearch)

        self.mainBox.addWidget(QLabel(""),         0,0)
        self.mainBox.addWidget(self.searchLabel,   0,1)
        self.mainBox.addWidget(self.searchBox,     0,2)
        self.mainBox.addWidget(self.searchButton,  0,3)
        self.mainBox.addWidget(self.closeButton,   0,4)
        self.mainBox.addWidget(self.replaceLabel,  1,1)
        self.mainBox.addWidget(self.replaceBox,    1,2)
        self.mainBox.addWidget(self.replaceButton, 1,3)

        self.mainBox.setColumnStretch(0,1)
        self.mainBox.setColumnStretch(1,0)
        self.mainBox.setColumnStretch(2,0)
        self.mainBox.setColumnStretch(3,0)
        self.mainBox.setColumnStretch(4,0)
        self.mainBox.setContentsMargins(0,0,0,0)

        self.searchBox.setMinimumWidth(180)
        self.replaceBox.setMinimumWidth(180)

        self._replaceVisible(False)

        logger.debug("GuiSearchBar initialisation complete")

        return

    ##
    #  Get and Set Functions
    ##

    def setSearchText(self, theText):
        """Open the search bar and set the search text to the text
        provided, if any.
        """
        if not self.isVisible():
            self.setVisible(True)
        self.searchBox.setText(theText)
        self.searchBox.setFocus()
        logger.verbose("Setting search text to '%s'" % theText)
        return True

    def setReplaceText(self, theText):
        """Set the replace text.
        """
        self._replaceVisible(True)
        self.replaceBox.setFocus()
        self.replaceBox.setText(theText)
        return True

    def getSearchText(self):
        """Return the current search text.
        """
        return self.searchBox.text()

    def getReplaceText(self):
        """Return the current replace text.
        """
        return self.replaceBox.text()

    ##
    #  Internal Functions
    ##

    def _doClose(self):
        """Hide the search/replace bar.
        """
        self._replaceVisible(False)
        self.setVisible(False)
        return

    def _doSearch(self):
        """Call the search action function for the document editor.
        """
        modKey = qApp.keyboardModifiers()
        if modKey == Qt.ShiftModifier:
            self.theParent.docEditor.docAction(nwDocAction.GO_PREV)
        else:
            self.theParent.docEditor.docAction(nwDocAction.GO_NEXT)
        return

    def _doReplace(self):
        """Call the replace action function for the document editor.
        """
        self.theParent.docEditor.docAction(nwDocAction.REPL_NEXT)
        return

    def _replaceVisible(self, isVisible):
        """Set the visibility of all the replace widgets.
        """
        self.replaceLabel.setVisible(isVisible)
        self.replaceBox.setVisible(isVisible)
        self.replaceButton.setVisible(isVisible)
        self.repVisible = isVisible
        return True

# END Class GuiSearchBar

class GuiNoticeBar(QFrame):

    def __init__(self, theParent):
        QFrame.__init__(self, theParent)

        logger.debug("Initialising GuiNoticeBar ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme

        self.setContentsMargins(0,0,0,0)
        self.setFrameShape(QFrame.Box)

        self.mainBox = QHBoxLayout(self)
        self.mainBox.setContentsMargins(8,2,2,2)

        self.noteLabel = QLabel("")

        self.closeButton = QPushButton(self.theTheme.getIcon("close"),"")
        self.closeButton.clicked.connect(self.hideNote)

        self.mainBox.addWidget(self.noteLabel)
        self.mainBox.addWidget(self.closeButton)
        self.mainBox.setStretch(0, 1)

        self.setLayout(self.mainBox)

        self.hideNote()

        logger.debug("GuiNoticeBar initialisation complete")

        return

    def showNote(self, theNote):
        """Show the note on the noticebar.
        """
        self.noteLabel.setText("<b>Note:</b> %s" % theNote)
        self.setVisible(True)
        return

    def hideNote(self):
        """Clear the noticebar and hide it.
        """
        self.noteLabel.setText("")
        self.setVisible(False)
        return

# END Class GuiNoticeBar

class GuiDocTitleBar(QLabel):

    def __init__(self, theParent, theProject):
        QLabel.__init__(self, theParent)

        logger.debug("Initialising GuiDocTitleBar ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.theTheme   = theParent.theTheme
        self.theHandle  = None

        self.setText("")
        self.setIndent(0)
        self.setMargin(0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setLineWidth(0)

        lblPalette = self.palette()
        lblPalette.setColor(QPalette.Window, QColor(*self.theTheme.colBack))
        lblPalette.setColor(QPalette.Text, QColor(*self.theTheme.colText))
        self.setPalette(lblPalette)

        lblFont = self.font()
        lblFont.setPointSizeF(0.9*self.theTheme.fontPointSize)
        self.setFont(lblFont)

        logger.debug("GuiDocTitleBar initialisation complete")

        return

    ##
    #  Setters
    ##

    def setTitleFromHandle(self, tHandle):
        """Sets the document title from the handle, or alternatively,
        set the whole document path.
        """
        self.setText("")
        self.theHandle = tHandle
        if tHandle is None:
            return False

        if self.mainConf.showFullPath:
            tTitle = []
            tTree = self.theProject.projTree.getItemPath(tHandle)
            for aHandle in reversed(tTree):
                nwItem = self.theProject.projTree[aHandle]
                if nwItem is not None:
                    tTitle.append(nwItem.itemName)
            sSep = "  %s  " % nwUnicode.U_RSAQUO
            self.setText(sSep.join(tTitle))
        else:
            nwItem = self.theProject.projTree[tHandle]
            if nwItem is None:
                return False

            self.setText(nwItem.itemName)

        return True

    ##
    #  Events
    ##

    def mousePressEvent(self, theEvent):
        """Capture a click on the title and ensure that the item is
        selected in the project tree.
        """
        self.theParent.setSelectedHandle(self.theHandle)
        return

# END Class GuiDocTitleBar
