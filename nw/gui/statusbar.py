# -*- coding: utf-8 -*-
"""novelWriter GUI Main Window StatusBar

 novelWriter – GUI Main Window StatusBar
=========================================
 Class holding the main window status bar

 File History:
 Created: 2019-04-20 [0.0.1]

"""

import logging
import nw

from os              import path
from PyQt5.QtWidgets import QStatusBar, QLabel

logger = logging.getLogger(__name__)

class GuiMainStatus(QStatusBar):

    def __init__(self):
        QStatusBar.__init__(self)

        logger.debug("Initialising GuiMainStatus ...")

        self.mainConf = nw.CONFIG

        self.boxWordCount = QLabel()
        self.boxCharCount = QLabel()
        self.boxDocHandle = QLabel()

        self.addPermanentWidget(self.boxWordCount)
        self.addPermanentWidget(self.boxCharCount)
        if self.mainConf.debugGUI:
            self.addPermanentWidget(self.boxDocHandle)

        logger.debug("GuiMainStatus initialisation complete")

        self.setWordCount(None)
        self.setCharCount(None)
        self.setDocHandleCount(None)

        return

    def setWordCount(self, theCount):
        if theCount is None:
            self.boxWordCount.setText("<b>Words:</b> --")
        else:
            self.boxWordCount.setText("<b>Words:</b> {:n}".format(theCount))
        return

    def setCharCount(self, theCount):
        if theCount is None:
            self.boxCharCount.setText("<b>Chars:</b> --")
        else:
            self.boxCharCount.setText("<b>Chars:</b> {:n}".format(theCount))
        return

    def setDocHandleCount(self, theHandle):
        if theHandle is None:
            self.boxDocHandle.setText("0000000000000")
        else:
            self.boxDocHandle.setText("%13s" % theHandle)
        return

# END Class GuiMainStatus
