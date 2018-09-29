# -*- coding: utf-8 -*
"""novelWriter GUI Document Tabs

 novelWriter – GUI Document Tabs
=================================
 Class holding the document tab view

 File History:
 Created: 2018-09-29 [0.1.0]

"""

import logging
import nw

from os               import path
from PyQt5.QtCore     import Qt
from PyQt5.QtWidgets  import QTabWidget, QWidget, QVBoxLayout

from nw.gui.doceditor import GuiDocEditor

logger = logging.getLogger(__name__)

class GuiDocTabs(QTabWidget):

    def __init__(self):
        QTabWidget.__init__(self)

        logger.debug("Initialising DocTabs ...")
        self.mainConf = nw.CONFIG
        self.docList  = []
        self.tabList  = []

        self.resize(900,500)

        logger.debug("DocTabs initialisation complete")

        return

    def createTab(self, docFile=None):
        if docFile is None:
            tabName = "New Document"
        else:
            tabName = docFile
        thisTab = QWidget()
        tabBox  = QVBoxLayout()
        thisDoc = GuiDocEditor()
        tabBox.addWidget(thisDoc)
        thisTab.setLayout(tabBox)
        self.tabList.append(thisTab)
        self.docList.append(thisDoc)
        self.addTab(self.tabList[-1],tabName)
        return True

# END Class GuiDocTabs
