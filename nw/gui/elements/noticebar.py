# -*- coding: utf-8 -*-
"""novelWriter GUI Main Window Notice Bar

 novelWriter – GUI Main Window Notice Bar
==========================================
 Class holding the main window notice bar for the doc editor

 File History:
 Created: 2019-10-31 [0.3.2]

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

        self.noteLabel = QLabel("Hi there!")

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
        self.noteLabel.setText("<b>Note:</b> %s" % theNote)
        self.setVisible(True)
        return

    def hideNote(self):
        self.noteLabel.setText("")
        self.setVisible(False)
        return

# END Class GuiNoticeBar
