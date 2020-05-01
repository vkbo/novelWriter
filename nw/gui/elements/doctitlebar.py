# -*- coding: utf-8 -*-
"""novelWriter GUI Document Title Bar

 novelWriter – GUI Document Title Bar
======================================
 Class holding the document title bar class

 File History:
 Created: 2020-04-25 [0.4.5]

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
 along with this program. If not, see https://www.gnu.org/licenses/.
"""

import logging
import nw

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QLabel

from nw.constants import nwUnicode

logger = logging.getLogger(__name__)

class GuiDocTitleBar(QLabel):

    def __init__(self, theParent, theProject):
        QLabel.__init__(self, theParent)

        logger.debug("Initialising DocTitleBar ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.theTheme   = theParent.theTheme
        self.theHandle  = None

        self.setText("")
        self.setContentsMargins(8,2,8,2)
        self.setAutoFillBackground(True)
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        docPalette = self.palette()
        docPalette.setColor(QPalette.Window, QColor(*self.theTheme.colBack))
        docPalette.setColor(QPalette.Text, QColor(*self.theTheme.colText))
        self.setPalette(docPalette)

        logger.debug("DocTitleBar initialisation complete")

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

        if True:
            tTitle = []
            tTree = self.theProject.getItemPath(tHandle)
            for aHandle in reversed(tTree):
                nwItem = self.theProject.getItem(aHandle)
                if nwItem is not None:
                    tTitle.append(nwItem.itemName)
            sSep = " %s " % nwUnicode.U_RTRI
            self.setText(sSep.join(tTitle))
        else:
            nwItem = self.theProject.getItem(tHandle)
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
        self.theParent.treeView.setSelectedHandle(self.theHandle)
        return

# END Class GuiDocTitleBar
