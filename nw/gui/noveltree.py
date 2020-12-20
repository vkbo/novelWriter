# -*- coding: utf-8 -*-
"""novelWriter GUI Novel Tree

 novelWriter – GUI Novel Tree
==============================
 Class holding the project's novel files tree view

 File History:
 Created: 2020-12-20 [1.1a0]

 This file is a part of novelWriter
 Copyright 2018–2020, Veronica Berglyd Olsen

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

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QTreeWidget

logger = logging.getLogger(__name__)

class GuiNovelTree(QTreeWidget):

    C_TITLE = 0
    C_WORDS = 1
    C_PAGES = 2

    def __init__(self, theParent):
        QTreeWidget.__init__(self, theParent)

        logger.debug("Initialising GuiNovelTree ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
        self.theProject = theParent.theProject
        self.theIndex   = theParent.theIndex

        # Build GUI
        iPx = self.theTheme.baseIconSize
        self.setIconSize(QSize(iPx, iPx))
        self.setExpandsOnDoubleClick(True)
        self.setIndentation(iPx)
        self.setColumnCount(3)
        self.setHeaderLabels(["Title", "Words", "Pages"])

        # Get user's column width preferences for NAME and COUNT
        treeColWidth = self.mainConf.getNovelColWidths()
        if len(treeColWidth) <= 3:
            for colN, colW in enumerate(treeColWidth):
                self.setColumnWidth(colN, colW)

        # The last column should just auto-scale
        self.resizeColumnToContents(self.C_PAGES)

        # Set custom settings
        self.initTree()

        logger.debug("GuiNovelTree initialisation complete")

        # Internal Mapping
        self.makeAlert = self.theParent.makeAlert

        return

    def initTree(self):
        """Set or update tree widget settings.
        """
        # Scroll bars
        if self.mainConf.hideVScroll:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        if self.mainConf.hideHScroll:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        return

    ##
    #  Class Methods
    ##

    def clearTree(self):
        """Clear the GUI content and the related maps.
        """
        self.clear()
        return

    def getColumnSizes(self):
        """Return the column widths for the tree columns.
        """
        retVals = [
            self.columnWidth(self.C_TITLE),
            self.columnWidth(self.C_WORDS),
        ]
        return retVals

    ##
    #  Slots
    ##

# END Class GuiNovelTree
