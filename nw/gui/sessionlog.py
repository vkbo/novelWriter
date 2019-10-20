# -*- coding: utf-8 -*-
"""novelWriter GUI Session Log Viewer

 novelWriter – GUI Session Log Viewer
======================================
 Class holding the session log view window

 File History:
 Created: 2019-10-20 [0.3]

"""

import logging
import nw

from os              import path
from datetime        import datetime
from PyQt5.QtCore    import Qt
from PyQt5.QtGui     import QIcon, QColor, QPixmap, QFont
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QDialogButtonBox, QHeaderView
)

from nw.enum      import nwAlert
from nw.constants import nwConst, nwFiles

logger = logging.getLogger(__name__)

class GuiSessionLogView(QDialog):

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising SessionLogView ...")

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent

        self.outerBox   = QVBoxLayout()
        self.bottomBox  = QHBoxLayout()

        self.setWindowTitle("Session Log")
        self.setMinimumWidth(420)
        self.setMinimumHeight(400)

        self.listBox = QTreeWidget()
        self.listBox.setHeaderLabels(["Session Start","Length","Words",""])
        self.listBox.setIndentation(0)
        self.listBox.setColumnWidth(0,180)
        self.listBox.setColumnWidth(1,80)
        self.listBox.setColumnWidth(2,80)
        self.listBox.setColumnWidth(3,0)

        hHeader = self.listBox.headerItem()
        hHeader.setTextAlignment(1,Qt.AlignRight)
        hHeader.setTextAlignment(2,Qt.AlignRight)

        self.listFont = QFont("Monospace",10)

        self.listBox.sortByColumn(0, Qt.DescendingOrder)
        self.listBox.setSortingEnabled(True)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttonBox.rejected.connect(self._doClose)

        self.outerBox.addWidget(self.listBox)
        self.outerBox.addWidget(self.buttonBox)

        self.setLayout(self.outerBox)

        self.show()

        logger.debug("SessionLogView initialisation complete")

        self._loadSessionLog()

        return

    def _loadSessionLog(self):

        logFile = path.join(self.theProject.projMeta, nwFiles.SESS_INFO)
        if not path.isfile(logFile):
            logger.warning("No session log file found for this project.")
            return False

        logger.debug("Loading session log file")
        try:
            with open(logFile,mode="r") as inFile:
                for inLine in inFile:
                    inData = inLine.split()
                    if len(inData) != 8:
                        continue
                    dStart  = datetime.strptime("%s %s" % (inData[1],inData[2]),nwConst.tStampFmt)
                    dEnd    = datetime.strptime("%s %s" % (inData[4],inData[5]),nwConst.tStampFmt)
                    nWords  = int(inData[7])
                    newItem = QTreeWidgetItem([str(dStart),str(dEnd-dStart),str(nWords),""])
                    newItem.setTextAlignment(1,Qt.AlignRight)
                    newItem.setTextAlignment(2,Qt.AlignRight)
                    newItem.setFont(0,self.listFont)
                    newItem.setFont(1,self.listFont)
                    newItem.setFont(2,self.listFont)
                    self.listBox.addTopLevelItem(newItem)
        except Exception as e:
            self.theParent.makeAlert(["Failed to read session log file.",str(e)], nwAlert.ERROR)
            return False

        return True

    def _doClose(self):
        self.close()
        return

# END Class GuiSessionLogView
