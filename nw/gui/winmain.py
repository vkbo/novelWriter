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

from os                   import path
from PyQt5.QtWidgets      import qApp, QWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QFrame, QSplitter, QAction, QToolBar, QFileDialog
from PyQt5.QtCore         import Qt, QSize
from PyQt5.QtGui          import QIcon, QStandardItemModel

from nw.gui.doctree       import GuiDocTree
from nw.gui.doceditor     import GuiDocEditor
from nw.gui.projecteditor import GuiProjectEditor
from nw.project.project   import NWProject

logger = logging.getLogger(__name__)

class GuiMain(QMainWindow):

    def __init__(self):
        QWidget.__init__(self)

        logger.debug("Initialising GUI ...")
        self.mainConf   = nw.CONFIG
        self.theProject = NWProject()

        self.resize(1100,650)
        self._setWindowTitle()
        self.setWindowIcon(QIcon(path.join(self.mainConf.appPath,"..","novelWriter.svg")))

        self.docEditor = GuiDocEditor()

        self.treePane = QFrame()
        self.treePane.setFrameShape(QFrame.StyledPanel)
        self.splitMain = QSplitter(Qt.Horizontal)
        self.splitMain.addWidget(self.treePane)
        self.splitMain.addWidget(self.docEditor)

        self.treeBox = QVBoxLayout()
        self.treeView = GuiDocTree()
        self.treeBox.addWidget(self.treeView)
        self.treePane.setLayout(self.treeBox)

        self.treeToolBar = QToolBar()
        self._buildTreeToolBar()
        self.treeBox.addWidget(self.treeToolBar)

        self.setCentralWidget(self.splitMain)

        self._buildMenu()

        # self.docTabs.createTab()

        self.show()

        logger.debug("GUI initialisation complete")

        statBar = self.statusBar()
        statBar.showMessage("Ready")

        return

    #
    #  Project Actions
    #

    def newProject(self):
        logger.info("Creating new project")
        self.docTabs.createTab(tabType=nw.DOCTYPE_PROJECT)
        return

    def openProject(self):
        dlgOpt  = QFileDialog.Options()
        dlgOpt |= QFileDialog.DontUseNativeDialog
        projPath, _ = QFileDialog.getOpenFileName(
                self,"Open novelWriter Project","","novelWriter Project File (nwProject.nwx);;All Files (*)", options=dlgOpt)
        if projPath:
            self.theProject.openProject(projPath)
            self._setWindowTitle(self.theProject.projName)
        else:
            return False
        return True

    def saveProject(self):
        if self.theProject.projPath is None:
            dlgOpt  = QFileDialog.Options()
            dlgOpt |= QFileDialog.DontUseNativeDialog
            projPath, _ = QFileDialog.getSaveFileName(
                self,"Save novelWriter Project","","novelWriter Project File (nwProject.nwx);;All Files (*)", options=dlgOpt)
            if projPath:
                self.theProject.setProjectPath(projPath)
            else:
                return False
        self.theProject.saveProject()
        return True

    def editProject(self):
        dlgProj = GuiProjectEditor(self, self.theProject)
        dlgProj.exec_()
        return True

    def openRecentProject(self, recentItem):
        logger.vverbose("User requested opening recent project #%d" % recentItem)
        self.theProject.openProject(self.mainConf.recentList[recentItem])
        self._setWindowTitle(self.theProject.projName)
        return True

    #
    #  Document Actions
    #

    def saveDocument(self):
        self.docEditor.getText()
        return

    #
    #  Internal Functions
    #

    def _buildMenu(self):
        menuBar = self.menuBar()

        # File
        fileMenu = menuBar.addMenu("&File")

        # File > New Project
        menuNewProject = QAction(QIcon.fromTheme("folder-new"), "New Project", menuBar)
        menuNewProject.setStatusTip("Create New Project")
        menuNewProject.triggered.connect(self.newProject)
        fileMenu.addAction(menuNewProject)

        # File > Open Project
        menuOpenProject = QAction(QIcon.fromTheme("folder-open"), "Open Project", menuBar)
        menuOpenProject.setStatusTip("Open Project")
        menuOpenProject.triggered.connect(self.openProject)
        fileMenu.addAction(menuOpenProject)

        # File > Save Project
        menuSaveProject = QAction(QIcon.fromTheme("document-save"), "Save Project", menuBar)
        menuSaveProject.setStatusTip("Save Project")
        menuSaveProject.triggered.connect(self.saveProject)
        fileMenu.addAction(menuSaveProject)

        # File > Recent Project
        recentMenu = fileMenu.addMenu(QIcon.fromTheme("document-open-recent"),"Recent Projects")
        itemCount = 0
        for recentProject in self.mainConf.recentList:
            if recentProject == "": continue
            menuRecentProject = QAction(QIcon.fromTheme("folder-open"), "%d: %s" % (itemCount,recentProject), fileMenu)
            menuRecentProject.triggered.connect(self.openRecentProject, itemCount)
            recentMenu.addAction(menuRecentProject)
            itemCount += 1

        # ---------------------
        fileMenu.addSeparator()

        # File > Project Settings
        menuProjectSettings = QAction(QIcon.fromTheme("document-properties"), "Project Settings", menuBar)
        menuProjectSettings.setStatusTip("Project Settings")
        menuProjectSettings.triggered.connect(self.editProject)
        fileMenu.addAction(menuProjectSettings)

        # ---------------------
        fileMenu.addSeparator()

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
        menuSave.triggered.connect(self.saveDocument)
        fileMenu.addAction(menuSave)

        # ---------------------
        fileMenu.addSeparator()

        # File > Exit
        menuExit = QAction(QIcon.fromTheme("application-exit"), "&Exit", menuBar)
        menuExit.setShortcut("Ctrl+Q")
        menuExit.setStatusTip("Exit %s" % nw.__package__)
        menuExit.triggered.connect(self._menuExit)
        fileMenu.addAction(menuExit)

        # Help
        helpMenu = menuBar.addMenu("&Help")

        # Help > About
        menuAbout = QAction(QIcon.fromTheme("help-about"), "About", menuBar)
        menuAbout.setStatusTip("About")
        menuAbout.triggered.connect(self._showAbout)
        helpMenu.addAction(menuAbout)

        if not self.mainConf.debugGUI:
            return

        # Debug GUI
        debugMenu = menuBar.addMenu("&Debug")

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

    def _closeMain(self):
        logger.info("Exiting %s" % nw.__package__)
        self.mainConf.setWinSize(self.frameGeometry().width(), self.frameGeometry().height())
        self.mainConf.saveConfig()
        return

    def _setWindowTitle(self, projName=None):
        winTitle = "%s [%s]" % (nw.__package__, nw.__version__)
        if projName is not None:
            winTitle += " - %s" % projName
        self.setWindowTitle(winTitle)
        return True

    #
    #  Menu Action
    #

    def _menuExit(self):
        self._closeMain()
        qApp.quit()
        return True

    def _showAbout(self):
        self.docTabs.createTab(None,nw.DOCTYPE_ABOUT)
        return True

    #
    #  Events
    #

    def closeEvent(self, guiEvent):
        self._closeMain()
        guiEvent.accept()

# END Class GuiMain
