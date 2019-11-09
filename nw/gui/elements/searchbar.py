# -*- coding: utf-8 -*-
"""novelWriter GUI Main Window SearchBar

 novelWriter – GUI Main Window SearchBar
=========================================
 Class holding the main window search bar

 File History:
 Created: 2019-09-29 [0.2.1]

"""

import logging
import nw

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame, QGridLayout, QLabel, QLineEdit, QPushButton, QApplication
)

from nw.constants import nwDocAction

logger = logging.getLogger(__name__)

class GuiSearchBar(QFrame):

    def __init__(self, theParent):
        QFrame.__init__(self, theParent)

        logger.debug("Initialising SearchBar ...")

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
        self.replaceButton = QPushButton(self.theTheme.getIcon("replace"),"")

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

        logger.debug("SearchBar initialisation complete")

        return

    ##
    #  Get and Set Functions
    ##

    def setSearchText(self, theText):
        if not self.isVisible():
            self.setVisible(True)
        self.searchBox.setText(theText)
        self.searchBox.setFocus(True)
        logger.verbose("Setting search text to '%s'" % theText)
        return True

    def setReplaceText(self, theText):
        self._replaceVisible(True)
        self.replaceBox.setFocus(True)
        self.replaceBox.setText(theText)
        return True

    def getSearchText(self):
        return self.searchBox.text()

    def getReplaceText(self):
        return self.replaceBox.text()

    ##
    #  Internal Functions
    ##

    def _doClose(self):
        self._replaceVisible(False)
        self.setVisible(False)
        return

    def _doSearch(self):
        modKey = QApplication.keyboardModifiers()
        if modKey == Qt.ShiftModifier:
            self.theParent.docEditor.docAction(nwDocAction.GO_PREV)
        else:
            self.theParent.docEditor.docAction(nwDocAction.GO_NEXT)
        return

    def _doReplace(self):
        self.theParent.docEditor.docAction(nwDocAction.REPL_NEXT)
        return

    def _replaceVisible(self, isVisible):
        self.replaceLabel.setVisible(isVisible)
        self.replaceBox.setVisible(isVisible)
        self.replaceButton.setVisible(isVisible)
        self.repVisible = isVisible
        return True

# END Class GuiSearchBar
