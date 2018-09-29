# -*- coding: utf-8 -*
"""novelWriter GUI Main Window

 novelWriter – GUI Main Window
===============================
 Class holding the main window

 File History:
 Created: 2018-09-22 [0.1.0]

"""

import logging
import nw

from os              import path
from PyQt5.QtWidgets import QWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QFrame, QSplitter, QTreeView
from PyQt5.QtCore    import Qt
from PyQt5.QtGui     import QIcon, QStandardItemModel

from nw.gui.doctree  import GuiDocTree
from nw.gui.doctabs  import GuiDocTabs

logger = logging.getLogger(__name__)

class GuiMain(QMainWindow):

    def __init__(self):
        QWidget.__init__(self)

        logger.debug("Initialising GUI ...")
        self.mainConf = nw.CONFIG

        self.resize(1100,650)
        self.setTitle()
        self.setWindowIcon(QIcon(path.join(self.mainConf.appPath,"..","novelWriter.svg")))

        self.statBar = self.statusBar()
        self.statBar.showMessage("Hello Kitty!")

        self.docTabs = GuiDocTabs()

        self.treePane = QFrame()
        self.treePane.setFrameShape(QFrame.StyledPanel)
        # self.textPane = QFrame()
        # self.textPane.setFrameShape(QFrame.StyledPanel)
        self.splitMain = QSplitter(Qt.Horizontal)
        self.splitMain.addWidget(self.treePane)
        self.splitMain.addWidget(self.docTabs)

        self.treeBox = QVBoxLayout()
        self.treeView = GuiDocTree()
        self.treeBox.addWidget(self.treeView)
        self.treePane.setLayout(self.treeBox)

        self.setCentralWidget(self.splitMain)

        self._buildMenu()

        self.docTabs.createTab()

        self.show()

        logger.debug("GUI initialisation complete")

        return

    #
    #  Set and Get Methods
    #

    def setTitle(self, projName=None):
        winTitle = "%s [%s]" % (nw.__package__, nw.__version__)
        if projName is not None:
            winTitle += " - %s" % projName
        self.setWindowTitle(winTitle)
        return True

    #
    #  Internal Functions
    #

    def _buildMenu(self):
        menuBar = self.menuBar()
        menuBar.addMenu("File")
        return

# END Class GuiMain
