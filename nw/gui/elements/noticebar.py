# -*- coding: utf-8 -*-
"""novelWriter GUI Main Window Notice Bar

 novelWriter – GUI Main Window Notice Bar
==========================================
 Class holding the main window notice bar for the doc editor

 File History:
 Created: 2019-10-31 [0.3.2]

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

from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

logger = logging.getLogger(__name__)

class GuiNoticeBar(QFrame):

    def __init__(self, theParent):
        QFrame.__init__(self, theParent)

        logger.debug("Initialising NoticeBar ...")

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

        logger.debug("NoticeBar initialisation complete")

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
