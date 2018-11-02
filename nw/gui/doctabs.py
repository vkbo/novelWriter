# -*- coding: utf-8 -*
"""novelWriter GUI Document Tabs

 novelWriter – GUI Document Tabs
=================================
 Class holding the document tab view

 File History:
 Created: 2018-09-29 [0.0.1]

"""

import logging
import nw

from PyQt5.QtCore         import Qt
from PyQt5.QtWidgets      import QTabWidget, QWidget, QVBoxLayout

from nw.gui.doceditor     import GuiDocEditor
from nw.gui.projecteditor import GuiProjectEditor
from nw.gui.aboutview     import GuiAboutView

logger = logging.getLogger(__name__)

class GuiDocTabs(QTabWidget):

    def __init__(self):
        QTabWidget.__init__(self)

        logger.debug("Initialising DocTabs ...")
        self.mainConf = nw.CONFIG
        self.tabList  = []

        self.resize(900,500)
        self.setTabsClosable(True)

        self.tabBar().tabCloseRequested.connect(self._doCloseTab)

        self.createTab(None,nw.DOCTYPE_ABOUT)

        logger.debug("DocTabs initialisation complete")

        return

    def createTab(self, theName=None, tabType=None):
        if tabType == nw.DOCTYPE_ABOUT:
            self._createTabAbout()
            return True
        elif tabType == nw.DOCTYPE_PROJECT:
            self._createTabProject(theName)
            return True
        elif tabType == nw.DOCTYPE_DOC:
            self._createTabDoc(theName)
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
        self.addTab(thisTab,tabName)
        self.setCurrentWidget(thisTab)
        return True

    def _createTabProject(self, projectName=None):
        """Display or create the project settings page.
        """
        for i in range(self.count()):
            thisTab = self.widget(i)
            if isinstance(thisTab, GuiProjectEditor):
                self.setCurrentWidget(thisTab)
                return True
        if projectName is None:
            tabName = "New Project"
        else:
            tabName = projectName
        thisTab = GuiProjectEditor()
        self.addTab(thisTab,tabName)
        self.setCurrentWidget(thisTab)
        return True

    def _createTabAbout(self):
        """Display or create the About tab.
        """
        for i in range(self.count()):
            thisTab = self.widget(i)
            if isinstance(thisTab, GuiAboutView):
                self.setCurrentWidget(thisTab)
                return True
        thisTab = GuiAboutView()
        self.addTab(thisTab,"About")
        self.setCurrentWidget(thisTab)
        return True

    #
    #  Signals
    #

    def _doCloseTab(self, tabIdx):
        logger.verbose("User requested tab %d to be closed." % tabIdx)
        self.removeTab(tabIdx)
        logger.verbose("Tab %d closed." % tabIdx)
        return

# END Class GuiDocTabs
