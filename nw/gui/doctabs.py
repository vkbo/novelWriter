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

from os                   import path
from PyQt5.QtCore         import Qt
from PyQt5.QtWidgets      import QTabWidget, QWidget, QVBoxLayout

from nw.gui.doceditor     import GuiDocEditor
from nw.gui.projecteditor import GuiProjectEditor

logger = logging.getLogger(__name__)

class GuiDocTabs(QTabWidget):

    def __init__(self):
        QTabWidget.__init__(self)

        logger.debug("Initialising DocTabs ...")
        self.mainConf = nw.CONFIG
        self.tabList  = []

        self.resize(900,500)

        logger.debug("DocTabs initialisation complete")

        return

    def createTab(self, theName=None, tabType=None):
        if tabType == nw.DOCTYPE_DOC:
            self._createTabDoc(theName)
            return True
        elif tabType == nw.DOCTYPE_PROJECT:
            self._createTabProject(theName)
            return True
        return False

    #
    #  Internal Functions
    #

    def _createTabDoc(self, docName=None):
        if docName is None:
            tabName = "New Document"
        else:
            tabName = docName
        thisTab = GuiDocEditor()
        self.tabList.append(thisTab)
        self.addTab(self.tabList[-1],tabName)
        return True

    def _createTabProject(self, projectName=None):
        if projectName is None:
            tabName = "New Project"
        else:
            tabName = projectName
        thisTab = GuiProjectEditor()
        self.tabList.append(thisTab)
        self.addTab(self.tabList[-1],tabName)
        return True

# END Class GuiDocTabs
