# -*- coding: utf-8 -*-
"""novelWriter GUI Main Window

 novelWriter – GUI Main Window
===============================
 Class holding the main window

 File History:
 Created: 2018-09-22 [0.0.1]

"""

import logging
import nw

from os                   import path
from PyQt5.QtWidgets      import qApp, QWidget, QMainWindow, QVBoxLayout, QFrame, QSplitter, QAction, QToolBar, QFileDialog, QStackedWidget
from PyQt5.QtCore         import Qt, QSize
from PyQt5.QtGui          import QIcon

from nw.gui.doctree       import GuiDocTree
from nw.gui.doctreectx    import GuiDocTreeCtx
from nw.gui.doceditor     import GuiDocEditor
from nw.gui.projecteditor import GuiProjectEditor
from nw.gui.statusbar     import GuiMainStatus
from nw.project.project   import NWProject
from nw.project.document  import NWDoc
from nw.enum              import nwItemType, nwDocAction

logger = logging.getLogger(__name__)

class GuiMain(QMainWindow):

    def __init__(self):
        QWidget.__init__(self)

        logger.debug("Initialising GUI ...")
        self.mainConf    = nw.CONFIG
        self.theProject  = NWProject()
        self.theDocument = NWDoc(self.theProject, self)

        self.resize(*self.mainConf.winGeometry)
        self._setWindowTitle()
        self.setWindowIcon(QIcon(path.join(self.mainConf.appPath,"..","novelWriter.svg")))

        self.docEditor = GuiDocEditor(self)

        self.treePane = QFrame()
        self.treePane.setFrameShape(QFrame.StyledPanel)
        self.splitMain = QSplitter(Qt.Horizontal)
        self.splitMain.addWidget(self.treePane)

        self.stackPane = QStackedWidget()
        self.stackNone = self.stackPane.addWidget(QWidget())
        self.stackDoc  = self.stackPane.addWidget(self.docEditor)
        self.splitMain.addWidget(self.stackPane)
        self.stackPane.setCurrentIndex(self.stackNone)

        self.treeBox  = QVBoxLayout()
        self.treeView = GuiDocTree(self.theProject)
        self.treeBox.addWidget(self.treeView)
        self.treePane.setLayout(self.treeBox)

        self.treeToolBar = QToolBar()
        self._buildTreeToolBar()
        self.treeBox.addWidget(self.treeToolBar)

        self.setCentralWidget(self.splitMain)

        self._buildMenu()
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self._openDocTreeContextMenu)
        self.treeView.itemDoubleClicked.connect(self._treeDoubleClick)
        self.treeView.buildTree()

        self.splitMain.setSizes(self.mainConf.mainPanePos)
        self.splitMain.splitterMoved.connect(self._splitMainMove)

        self.statusBar = GuiMainStatus()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

        # Load Theme StyleSheet
        cssFile = path.join(self.mainConf.themePath,self.mainConf.guiTheme+".css")
        if path.isfile(cssFile):
            with open(cssFile,mode="r") as inFile:
                theCss = inFile.read()
            self.setStyleSheet(theCss)

        self.show()

        logger.debug("GUI initialisation complete")

        return

    #
    #  Project Actions
    #

    def newProject(self):
        logger.info("Creating new project")
        self.theProject.newProject()
        self.treeView.buildTree()
        return

    def openProject(self):
        dlgOpt  = QFileDialog.Options()
        dlgOpt |= QFileDialog.DontUseNativeDialog
        projPath, _ = QFileDialog.getOpenFileName(
            self,"Open novelWriter Project","","novelWriter Project File (nwProject.nwx);;All Files (*)", options=dlgOpt
        )
        if projPath:
            self.theProject.openProject(projPath)
            self.treeView.buildTree()
            self._setWindowTitle(self.theProject.projName)
        else:
            return False
        return True

    def saveProject(self):
        if self.theProject.projPath is None:
            dlgOpt  = QFileDialog.Options()
            dlgOpt |= QFileDialog.DontUseNativeDialog
            projPath, _ = QFileDialog.getSaveFileName(
                self,"Save novelWriter Project","","novelWriter Project File (nwProject.nwx);;All Files (*)", options=dlgOpt
            )
            if projPath:
                self.theProject.setProjectPath(projPath)
            else:
                return False
        self.treeView.saveTreeOrder()
        self.theProject.saveProject()
        return True

    def editProject(self):
        dlgProj = GuiProjectEditor(self, self.theProject)
        dlgProj.exec_()
        return True

    def openRecentProject(self, recentItem):
        logger.verbose("User requested opening recent project #%d" % recentItem)
        self.theProject.openProject(self.mainConf.recentList[recentItem])
        self.treeView.buildTree()
        self._setWindowTitle(self.theProject.projName)
        return True

    #
    #  Document Actions
    #

    def openDocument(self, tHandle):
        self.stackPane.setCurrentIndex(self.stackDoc)
        self.docEditor.setText(self.theDocument.openDocument(tHandle))
        self.docEditor.changeWidth()
        return

    def saveDocument(self):
        docHtml = self.docEditor.getText()
        self.theDocument.theItem.setCharCount(self.docEditor.charCount)
        self.theDocument.theItem.setWordCount(self.docEditor.wordCount)
        self.theDocument.theItem.setParaCount(self.docEditor.paraCount)
        self.theDocument.saveDocument(docHtml)
        return

    #
    #  Internal Functions
    #

    def _treeDoubleClick(self, tItem, colNo):
        tHandle = tItem.text(3)
        logger.verbose("User double clicked tree item with handle %s" % tHandle)
        nwItem = self.theProject.getItem(tHandle)
        if nwItem.itemType == nwItemType.FILE:
            logger.verbose("Requested item %s is a file" % tHandle)
            self.openDocument(tHandle)
        else:
            logger.verbose("Requested item %s is a folder" % tHandle)
        return

    def _closeMain(self):
        logger.info("Exiting %s" % nw.__package__)
        self.mainConf.setWinSize(self.width(), self.height())
        self.mainConf.setTreeColWidths(self.treeView.getColumnSizes())
        self.mainConf.setMainPanePos(self.splitMain.sizes())
        self.mainConf.saveConfig()
        return

    def _setWindowTitle(self, projName=None):
        winTitle = "%s [%s]" % (nw.__package__, nw.__version__)
        if projName is not None:
            winTitle += " - %s" % projName
        self.setWindowTitle(winTitle)
        return True

    ##
    #  Menu Action
    ##

    def _menuExit(self):
        self._closeMain()
        qApp.quit()
        return True

    def _showAbout(self):
        self.docTabs.createTab(None,nw.DOCTYPE_ABOUT)
        return True

    ##
    #  DocTree Context Menu
    ##

    def _openDocTreeContextMenu(self, thePosition):

        ctxMenu   = GuiDocTreeCtx(self.treeView, self.theProject, thePosition)
        selHandle = ctxMenu.selHandle
        selAction = ctxMenu.selAction
        selClass  = ctxMenu.selClass
        selType   = ctxMenu.selType
        selTarget = ctxMenu.selTarget

        print(selHandle, selAction, selClass, selType, selTarget)

        return

    ##
    #  Events
    ##

    def resizeEvent(self, theEvent):
        """Extend QMainWindow.resizeEvent to signal dependent GUI elements that its pane may have changed size.
        """
        QMainWindow.resizeEvent(self,theEvent)
        if self.stackPane.currentIndex() == self.stackDoc:
            self.docEditor.changeWidth()
        return

    def closeEvent(self, theEvent):
        self._closeMain()
        QMainWindow.closeEvent(self,theEvent)
        return

    ##
    #  Signal Handlers
    ##

    def _splitMainMove(self, pWidth, pHeight):
        """Alert dependent GUI elements that the main pane splitter has been moved.
        """
        if self.stackPane.currentIndex() == self.stackDoc:
            self.docEditor.changeWidth()
        return

    #
    #  GUI Builders
    #

    def _buildMenu(self):
        menuBar = self.menuBar()

        # File
        fileMenu = menuBar.addMenu("&File")

        # File > New Project
        menuItem = QAction(QIcon.fromTheme("folder-new"), "New Project", menuBar)
        menuItem.setStatusTip("Create New Project")
        menuItem.triggered.connect(self.newProject)
        fileMenu.addAction(menuItem)

        # File > Open Project
        menuItem = QAction(QIcon.fromTheme("folder-open"), "Open Project", menuBar)
        menuItem.setStatusTip("Open Project")
        menuItem.triggered.connect(self.openProject)
        fileMenu.addAction(menuItem)

        # File > Save Project
        menuItem = QAction(QIcon.fromTheme("document-save"), "Save Project", menuBar)
        menuItem.setStatusTip("Save Project")
        menuItem.triggered.connect(self.saveProject)
        fileMenu.addAction(menuItem)

        # File > Recent Project
        recentMenu = fileMenu.addMenu(QIcon.fromTheme("document-open-recent"),"Recent Projects")
        itemCount = 0
        for recentProject in self.mainConf.recentList:
            if recentProject == "": continue
            menuItem = QAction(QIcon.fromTheme("folder-open"), "%d: %s" % (itemCount,recentProject), fileMenu)
            menuItem.triggered.connect(self.openRecentProject, itemCount)
            recentMenu.addAction(menuItem)
            itemCount += 1

        # File > Separator
        fileMenu.addSeparator()

        # File > Project Settings
        menuItem = QAction(QIcon.fromTheme("document-properties"), "Project Settings", menuBar)
        menuItem.setStatusTip("Project Settings")
        menuItem.triggered.connect(self.editProject)
        fileMenu.addAction(menuItem)

        # File > Separator
        fileMenu.addSeparator()

        # File > New
        menuItem = QAction(QIcon.fromTheme("document-new"), "&New", menuBar)
        menuItem.setStatusTip("Create new document")
        menuItem.setShortcut("Ctrl+N")
        fileMenu.addAction(menuItem)

        # File > Save
        menuItem = QAction(QIcon.fromTheme("document-save"), "&Save", menuBar)
        menuItem.setStatusTip("Save document")
        menuItem.setShortcut("Ctrl+S")
        menuItem.triggered.connect(self.saveDocument)
        fileMenu.addAction(menuItem)

        # File > Separator
        fileMenu.addSeparator()

        # File > Exit
        menuItem = QAction(QIcon.fromTheme("application-exit"), "Exit", menuBar)
        menuItem.setStatusTip("Exit %s" % nw.__package__)
        menuItem.setShortcut("Ctrl+Q")
        menuItem.triggered.connect(self._menuExit)
        fileMenu.addAction(menuItem)

        ############################################################################################

        # Edit
        editMenu = menuBar.addMenu("&Edit")

        # Edit > Undo
        menuItem = QAction(QIcon.fromTheme("edit-undo"), "Undo", menuBar)
        menuItem.setStatusTip("Undo Last Change")
        menuItem.setShortcut("Ctrl+Z")
        menuItem.triggered.connect(lambda: self.docEditor.docAction(nwDocAction.UNDO))
        editMenu.addAction(menuItem)

        # Edit > Redo
        menuItem = QAction(QIcon.fromTheme("edit-redo"), "Redo", menuBar)
        menuItem.setStatusTip("Redo Last Change")
        menuItem.setShortcut("Ctrl+Y")
        menuItem.triggered.connect(lambda: self.docEditor.docAction(nwDocAction.REDO))
        editMenu.addAction(menuItem)

        # Edit > Separator
        editMenu.addSeparator()

        # Edit > Cut
        menuItem = QAction(QIcon.fromTheme("edit-cut"), "Cut", menuBar)
        menuItem.setStatusTip("Cut Selected Text")
        menuItem.setShortcut("Ctrl+X")
        menuItem.triggered.connect(lambda: self.docEditor.docAction(nwDocAction.CUT))
        editMenu.addAction(menuItem)

        # Edit > Copy
        menuItem = QAction(QIcon.fromTheme("edit-copy"), "Copy", menuBar)
        menuItem.setStatusTip("Copy Selected Text")
        menuItem.setShortcut("Ctrl+C")
        menuItem.triggered.connect(lambda: self.docEditor.docAction(nwDocAction.COPY))
        editMenu.addAction(menuItem)

        # Edit > Paste
        menuItem = QAction(QIcon.fromTheme("edit-paste"), "Paste", menuBar)
        menuItem.setStatusTip("Paste Text from Clipboard")
        menuItem.setShortcut("Ctrl+V")
        menuItem.triggered.connect(lambda: self.docEditor.docAction(nwDocAction.PASTE))
        editMenu.addAction(menuItem)

        # Edit > Separator
        editMenu.addSeparator()

        # Edit > Settings
        menuItem = QAction(QIcon.fromTheme("applications-system"), "Program Setting", menuBar)
        menuItem.setStatusTip("Change %s Settings" % nw.__package__)
        editMenu.addAction(menuItem)

        ############################################################################################

        # Format
        fmtMenu = menuBar.addMenu("&Format")

        # Format > Bold Text
        menuItem = QAction(QIcon.fromTheme("format-text-bold"), "Bold Text", menuBar)
        menuItem.setStatusTip("Make Selected Text Bold")
        menuItem.setShortcut("Ctrl+B")
        menuItem.triggered.connect(lambda: self.docEditor.docAction(nwDocAction.BOLD))
        fmtMenu.addAction(menuItem)

        # Format > Italic Text
        menuItem = QAction(QIcon.fromTheme("format-text-italic"), "Italic Text", menuBar)
        menuItem.setStatusTip("Make Selected Text Italic")
        menuItem.setShortcut("Ctrl+I")
        menuItem.triggered.connect(lambda: self.docEditor.docAction(nwDocAction.ITALIC))
        fmtMenu.addAction(menuItem)

        # Format > Underline Text
        menuItem = QAction(QIcon.fromTheme("format-text-underline"), "Underline Text", menuBar)
        menuItem.setStatusTip("Underline Selected Text")
        menuItem.setShortcut("Ctrl+U")
        menuItem.triggered.connect(lambda: self.docEditor.docAction(nwDocAction.U_LINE))
        fmtMenu.addAction(menuItem)

        # Edit > Separator
        fmtMenu.addSeparator()

        # Format > Double Quotes
        menuItem = QAction(QIcon.fromTheme("insert-text"), "Wrap Double Quotes", menuBar)
        menuItem.setStatusTip("Wrap Selected Text in Double Quotes")
        menuItem.setShortcut("Ctrl+D")
        menuItem.triggered.connect(lambda: self.docEditor.docAction(nwDocAction.D_QUOTE))
        fmtMenu.addAction(menuItem)

        # Format > Single Quotes
        menuItem = QAction(QIcon.fromTheme("insert-text"), "Wrap Single Quotes", menuBar)
        menuItem.setStatusTip("Wrap Selected Text in Single Quotes")
        menuItem.setShortcut("Ctrl+Shift+D")
        menuItem.triggered.connect(lambda: self.docEditor.docAction(nwDocAction.S_QUOTE))
        fmtMenu.addAction(menuItem)

        ############################################################################################

        # Help
        helpMenu = menuBar.addMenu("&Help")

        # Help > About
        menuItem = QAction(QIcon.fromTheme("help-about"), "About %s" % nw.__package__, menuBar)
        menuItem.setStatusTip("About %s" % nw.__package__)
        menuItem.triggered.connect(self._showAbout)
        helpMenu.addAction(menuItem)

        # Help > About Qt5
        menuItem = QAction(QIcon.fromTheme("help-about"), "About Qt5", menuBar)
        menuItem.setStatusTip("About Qt5")
        helpMenu.addAction(menuItem)

        if not self.mainConf.debugGUI:
            return

        ############################################################################################

        # Debug GUI
        debugMenu = menuBar.addMenu("&Debug")

        return

    def _buildTreeToolBar(self):
        toolBar = self.treeToolBar
        toolBar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        toolBar.setIconSize(QSize(16,16))

        # Root > New
        tbRootNew = QAction(QIcon.fromTheme("folder-new"), "New Root Folder (Ctrl+Alt+N)", toolBar)
        tbRootNew.setShortcut("Ctrl+Alt+N")
        tbRootNew.setStatusTip("Create New Root Folder")
        tbRootNew.triggered.connect(lambda: self.treeView.newTreeItem(nwItemType.ROOT))
        toolBar.addAction(tbRootNew)

        # Folder > New
        tbFolderNew = QAction(QIcon.fromTheme("folder-new"), "New Folder (Ctrl+Shift+N)", toolBar)
        tbFolderNew.setShortcut("Ctrl+Shift+N")
        tbFolderNew.setStatusTip("Create New Chapter or Folder")
        tbFolderNew.triggered.connect(lambda: self.treeView.newTreeItem(nwItemType.FOLDER))
        toolBar.addAction(tbFolderNew)

        # Document > New
        tbDocNew = QAction(QIcon.fromTheme("document-new"), "New Document (Ctrl+N)", toolBar)
        tbDocNew.setShortcut("Ctrl+N")
        tbDocNew.setStatusTip("Create New Document")
        tbDocNew.triggered.connect(lambda: self.treeView.newTreeItem(nwItemType.FILE))
        toolBar.addAction(tbDocNew)

        return

# END Class GuiMain
