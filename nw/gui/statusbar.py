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

from PyQt5.QtGui     import QIcon, QColor, QPixmap
from PyQt5.QtWidgets import QStatusBar, QLabel, QFrame

logger = logging.getLogger(__name__)

class GuiMainStatus(QStatusBar):

    def __init__(self, theParent):
        QStatusBar.__init__(self, theParent)

        logger.debug("Initialising GuiMainStatus ...")

        self.mainConf = nw.CONFIG

        self.iconGrey   = QPixmap(16,16)
        self.iconGrey.fill(QColor(120,120,120))
        self.iconYellow = QPixmap(16,16)
        self.iconYellow.fill(QColor(120,120, 40))
        self.iconGreen  = QPixmap(16,16)
        self.iconGreen.fill(QColor( 40,120,  0))


        self.boxStats = QLabel()
        self.boxStats.setToolTip("Project Word Count | Session Word Count")

        self.boxCounts = QLabel()
        self.boxCounts.setToolTip("Document Character | Word | Paragraph Count")

        self.projChanged = QLabel("")
        self.projChanged.setFixedHeight(16)
        self.projChanged.setFixedWidth(16)
        self.projChanged.setToolTip("Project Changes Saved")

        self.docChanged = QLabel("")
        self.docChanged.setFixedHeight(16)
        self.docChanged.setFixedWidth(16)
        self.docChanged.setToolTip("Document Changes Saved")

        self.boxDocHandle = QLabel()
        self.boxDocHandle.setFrameStyle(QFrame.Panel | QFrame.Sunken);

        # Add Them
        self.addPermanentWidget(self.docChanged)
        self.addPermanentWidget(self.boxCounts)
        self.addPermanentWidget(QLabel("  "))
        self.addPermanentWidget(self.projChanged)
        self.addPermanentWidget(self.boxStats)
        if self.mainConf.debugGUI:
            self.addPermanentWidget(self.boxDocHandle)

        self.setSizeGripEnabled(True)

        logger.debug("GuiMainStatus initialisation complete")

        self.clearStatus()

        return

    def clearStatus(self):
        self.setStats(0,0)
        self.setCounts(0,0,0)
        self.setDocHandleCount(None)
        self.setProjectStatus(None)
        self.setDocumentStatus(None)
        return True

    def setStatus(self, theMessage, timeOut=10.0):
        self.showMessage(theMessage, int(timeOut*1000))
        return

    def setProjectStatus(self, isChanged):
        if isChanged is None:
            self.projChanged.setPixmap(self.iconGrey)
        elif isChanged == True:
            self.projChanged.setPixmap(self.iconYellow)
        elif isChanged == False:
            self.projChanged.setPixmap(self.iconGreen)
        else:
            self.projChanged.setPixmap(self.iconGrey)
        return

    def setDocumentStatus(self, isChanged):
        if isChanged is None:
            self.docChanged.setPixmap(self.iconGrey)
        elif isChanged == True:
            self.docChanged.setPixmap(self.iconYellow)
        elif isChanged == False:
            self.docChanged.setPixmap(self.iconGreen)
        else:
            self.docChanged.setPixmap(self.iconGrey)
        return

    def setStats(self, pWC, sWC):
        self.boxStats.setText("<b>Project:</b> {:d} : {:d}".format(pWC,sWC))
        return

    def setCounts(self, cC, wC, pC):
        self.boxCounts.setText("<b>Document:</b> {:d} : {:d} : {:d}".format(cC,wC,pC))
        return

    def setDocHandleCount(self, theHandle):
        if theHandle is None:
            self.boxDocHandle.setText("0000000000000")
        else:
            self.boxDocHandle.setText("%13s" % theHandle)
        return

# END Class GuiMainStatus
