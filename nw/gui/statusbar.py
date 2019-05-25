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

from PyQt5.QtWidgets import QStatusBar, QLabel, QFrame

logger = logging.getLogger(__name__)

class GuiMainStatus(QStatusBar):

    def __init__(self, theParent):
        QStatusBar.__init__(self, theParent)

        logger.debug("Initialising GuiMainStatus ...")

        self.mainConf = nw.CONFIG

        self.boxCounts = QLabel()
        self.boxCounts.setToolTip("Character, Word, Paragraph Count")
        self.boxCounts.setFrameStyle(QFrame.Panel | QFrame.Sunken);
        self.addPermanentWidget(self.boxCounts)

        self.projChanged = QLabel("P")
        self.projChanged.setToolTip("Project Changes Saved")
        self.projChanged.setFrameStyle(QFrame.Panel | QFrame.Sunken);
        self.addPermanentWidget(self.projChanged)

        self.docChanged = QLabel("D")
        self.docChanged.setToolTip("Document Changes Saved")
        self.docChanged.setFrameStyle(QFrame.Panel | QFrame.Sunken);
        self.addPermanentWidget(self.docChanged)

        self.boxDocHandle = QLabel()
        self.boxDocHandle.setFrameStyle(QFrame.Panel | QFrame.Sunken);
        if self.mainConf.debugGUI:
            self.addPermanentWidget(self.boxDocHandle)

        logger.debug("GuiMainStatus initialisation complete")

        self.setCounts(0,0,0)
        self.setDocHandleCount(None)
        self.setProjectStatus(None)
        self.setDocumentStatus(None)

        self.setSizeGripEnabled(True)

        return

    def setStatus(self, theMessage, timeOut=10.0):
        self.showMessage(theMessage, int(timeOut*1000))
        return

    def setProjectStatus(self, isChanged):
        if isChanged is None:
            self.projChanged.setStyleSheet("QLabel {background-color: rgba(120,120,120,1.0);}")
        elif isChanged == True:
            self.projChanged.setStyleSheet("QLabel {background-color: rgba(120,120,40,1.0);}")
        elif isChanged == False:
            self.projChanged.setStyleSheet("QLabel {background-color: rgba(40,120,0,1.0);}")
        else:
            self.projChanged.setStyleSheet("QLabel {background-color: rgba(120,120,120,1.0);}")
        return

    def setDocumentStatus(self, isChanged):
        if isChanged is None:
            self.docChanged.setStyleSheet("QLabel {background-color: rgba(120,120,120,1.0);}")
        elif isChanged == True:
            self.docChanged.setStyleSheet("QLabel {background-color: rgba(120,120,40,1.0);}")
        elif isChanged == False:
            self.docChanged.setStyleSheet("QLabel {background-color: rgba(40,120,0,1.0);}")
        else:
            self.docChanged.setStyleSheet("QLabel {background-color: rgba(120,120,120,1.0);}")
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
