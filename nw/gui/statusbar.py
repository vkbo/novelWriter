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
from PyQt5.QtWidgets import QStatusBar, QLabel, QFrame

logger = logging.getLogger(__name__)

class GuiMainStatus(QStatusBar):

    def __init__(self):
        QStatusBar.__init__(self)

        logger.debug("Initialising GuiMainStatus ...")

        self.mainConf = nw.CONFIG

        self.boxCounts = QLabel()
        self.boxCounts.setFrameStyle(QFrame.Panel | QFrame.Sunken);
        self.addPermanentWidget(self.boxCounts)

        self.boxDocHandle = QLabel()
        self.boxDocHandle.setFrameStyle(QFrame.Panel | QFrame.Sunken);
        if self.mainConf.debugGUI:
            self.addPermanentWidget(self.boxDocHandle)

        logger.debug("GuiMainStatus initialisation complete")

        self.setCounts(0,0,0)
        self.setDocHandleCount(None)

        return

    def setCounts(self, cC, wC, pC):
        self.boxCounts.setText("<b>C:</b> {:n}&nbsp;&nbsp;<b>W:</b> {:n}&nbsp;&nbsp;<b>P:</b> {:n}".format(cC,wC,pC))
        return

    def setDocHandleCount(self, theHandle):
        if theHandle is None:
            self.boxDocHandle.setText("0000000000000")
        else:
            self.boxDocHandle.setText("%13s" % theHandle)
        return

# END Class GuiMainStatus
