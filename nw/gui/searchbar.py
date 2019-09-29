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

from PyQt5.QtGui     import QIcon
from PyQt5.QtWidgets import QFrame, QGridLayout, QLabel, QLineEdit, QPushButton

logger = logging.getLogger(__name__)

class GuiSearchBar(QFrame):

    def __init__(self, theParent):
        QFrame.__init__(self, theParent)

        logger.debug("Initialising GuiSearchBar ...")

        self.mainConf  = nw.CONFIG
        self.theParent = theParent

        self.setContentsMargins(0,0,0,0)

        self.mainBox = QGridLayout(self)
        self.setLayout(self.mainBox)

        self.searchBox    = QLineEdit()
        self.searchButton = QPushButton(QIcon.fromTheme("edit-find"),"")

        self.mainBox.addWidget(QLabel(""),0,0)
        self.mainBox.addWidget(QLabel("Search"),0,1)
        self.mainBox.addWidget(self.searchBox,0,2)
        self.mainBox.addWidget(self.searchButton,0,3)

        self.mainBox.setColumnStretch(0,1)
        self.mainBox.setColumnStretch(1,0)
        self.mainBox.setColumnStretch(2,0)
        self.mainBox.setColumnStretch(3,0)
        self.mainBox.setContentsMargins(0,0,0,0)

        logger.debug("GuiSearchBar initialisation complete")

        return

    def setSearchText(self, theText):

        if not self.isVisible():
            self.setVisible(True)

        self.searchBox.setText(theText)
        self.searchBox.setFocus(True)

        logger.debug("Setting search text to '%s'" % theText)

        return True

    def getSearchText(self):
        return self.searchBox.text()

# END Class GuiSearchBar
