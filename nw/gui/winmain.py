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
from PyQt5.QtWidgets import qApp, QWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QFrame, QSplitter, QAction, QToolBar
from PyQt5.QtCore    import Qt, QSize
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
        self.splitMain = QSplitter(Qt.Horizontal)
        self.splitMain.addWidget(self.treePane)
        self.splitMain.addWidget(self.docTabs)

        self.treeBox = QVBoxLayout()
        self.treeView = GuiDocTree()
        self.treeBox.addWidget(self.treeView)
        self.treePane.setLayout(self.treeBox)

        self.treeToolBar = QToolBar()
        self._buildTreeToolBar()
        self.treeBox.addWidget(self.treeToolBar)

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
        menuBar  = self.menuBar()

        # File
        fileMenu = menuBar.addMenu("&File")

        # File > New
        menuNew = QAction(QIcon.fromTheme("document-new"), "&New", menuBar)
        menuNew.setShortcut("Ctrl+N")
        menuNew.setStatusTip("Create new document")
        fileMenu.addAction(menuNew)

        # File > Open
        menuOpen = QAction(QIcon.fromTheme("document-open"), "&Open", menuBar)
        menuOpen.setShortcut("Ctrl+O")
        menuOpen.setStatusTip("Open document")
        fileMenu.addAction(menuOpen)

        # File > Save
        menuSave = QAction(QIcon.fromTheme("document-save"), "&Save", menuBar)
        menuSave.setShortcut("Ctrl+S")
        menuSave.setStatusTip("Save document")
        fileMenu.addAction(menuSave)

        # ---------------------
        fileMenu.addSeparator()

        # File > Exit
        menuExit = QAction(QIcon.fromTheme("application-exit"), "&Exit", menuBar)
        menuExit.setShortcut("Ctrl+Q")
        menuExit.setStatusTip("Exit %s" % nw.__package__)
        menuExit.triggered.connect(self._menuExit)
        fileMenu.addAction(menuExit)

        return

    def _buildTreeToolBar(self):
        toolBar = self.treeToolBar
        toolBar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        toolBar.setIconSize(QSize(16,16))

        # Folder > New
        tbFolderNew = QAction(QIcon.fromTheme("folder-new"), "New Folder (Ctrl+Shift+N)", toolBar)
        tbFolderNew.setShortcut("Ctrl+Shift+N")
        tbFolderNew.setStatusTip("Create new folder")
        toolBar.addAction(tbFolderNew)

        # Document > New
        tbDocNew = QAction(QIcon.fromTheme("document-new"), "New Document (Ctrl+N)", toolBar)
        tbDocNew.setShortcut("Ctrl+N")
        tbDocNew.setStatusTip("Create new document")
        toolBar.addAction(tbDocNew)

        return

    #
    #  Menu Action
    #

    def _menuExit(self):
        logger.info("Exiting %s" % nw.__package__)
        qApp.quit()
        return True

# END Class GuiMain
