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
from PyQt5.QtWidgets      import qApp, QWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QFrame, QSplitter, QAction, QToolBar, QFileDialog, QStackedWidget
from PyQt5.QtCore         import Qt, QSize
from PyQt5.QtGui          import QIcon, QStandardItemModel

from nw.gui.doctree       import GuiDocTree
from nw.gui.doceditor     import GuiDocEditor
from nw.gui.projecteditor import GuiProjectEditor
from nw.project.project   import NWProject
from nw.project.item      import NWItem
from nw.project.document  import NWDoc

logger = logging.getLogger(__name__)

class GuiMain(QMainWindow):

    def __init__(self):
        QWidget.__init__(self)

        logger.debug("Initialising GUI ...")
        self.mainConf    = nw.CONFIG
        self.theProject  = NWProject()
        self.theDocument = NWDoc(self.theProject)

        self.resize(*self.mainConf.winGeometry)
        self._setWindowTitle()
        self.setWindowIcon(QIcon(path.join(self.mainConf.appPath,"..","novelWriter.svg")))

        self.docEditor = GuiDocEditor()

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
        self.treeView.itemDoubleClicked.connect(self._treeDoubleClick)
        self.treeView.buildTree()

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
        self.theProject.newProject()
        self.treeView.buildTree()
        return

    def openProject(self):
        dlgOpt  = QFileDialog.Options()
        dlgOpt |= QFileDialog.DontUseNativeDialog
        projPath, _ = QFileDialog.getOpenFileName(
                self,"Open novelWriter Project","","novelWriter Project File (nwProject.nwx);;All Files (*)", options=dlgOpt)
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
                self,"Save novelWriter Project","","novelWriter Project File (nwProject.nwx);;All Files (*)", options=dlgOpt)
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
        return

    def saveDocument(self):
        docHtml = self.docEditor.getText()
        self.theDocument.saveDocument(docHtml)
        return

    #
    #  Internal Functions
    #

    def _treeDoubleClick(self, tItem, colNo):
        tHandle = tItem.text(3)
        logger.verbose("User double clicked tree item with handle %s" % tHandle)
        nwItem = self.theProject.getItem(tHandle)
        if nwItem.itemType == NWItem.TYPE_FILE:
            logger.verbose("Requested item %s is a file" % tHandle)
            self.openDocument(tHandle)
        else:
            logger.verbose("Requested item %s is a folder" % tHandle)
        return

    def _closeMain(self):
        logger.info("Exiting %s" % nw.__package__)
        self.mainConf.setWinSize(self.width(), self.height())
        self.mainConf.setTreeColWidths(self.treeView.getColumnSizes())
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

    #
    #  GUI Builders
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

        # File > Separator
        fileMenu.addSeparator()

        # File > Project Settings
        menuProjectSettings = QAction(QIcon.fromTheme("document-properties"), "Project Settings", menuBar)
        menuProjectSettings.setStatusTip("Project Settings")
        menuProjectSettings.triggered.connect(self.editProject)
        fileMenu.addAction(menuProjectSettings)

        # File > Separator
        fileMenu.addSeparator()

        # File > New
        menuNew = QAction(QIcon.fromTheme("document-new"), "&New", menuBar)
        menuNew.setShortcut("Ctrl+N")
        menuNew.setStatusTip("Create new document")
        fileMenu.addAction(menuNew)

        # File > Save
        menuSave = QAction(QIcon.fromTheme("document-save"), "&Save", menuBar)
        menuSave.setShortcut("Ctrl+S")
        menuSave.setStatusTip("Save document")
        menuSave.triggered.connect(self.saveDocument)
        fileMenu.addAction(menuSave)

        # File > Separator
        fileMenu.addSeparator()

        # File > Exit
        menuExit = QAction(QIcon.fromTheme("application-exit"), "Exit", menuBar)
        menuExit.setShortcut("Ctrl+Q")
        menuExit.setStatusTip("Exit %s" % nw.__package__)
        menuExit.triggered.connect(self._menuExit)
        fileMenu.addAction(menuExit)

        ############################################################################################

        # Edit
        editMenu = menuBar.addMenu("&Edit")

        # Edit > Undo
        menuUndo = QAction(QIcon.fromTheme("edit-undo"), "Undo", menuBar)
        menuUndo.setShortcut("Ctrl+Z")
        menuUndo.setStatusTip("Undo Last Change")
        editMenu.addAction(menuUndo)

        # Edit > Redo
        menuRedo = QAction(QIcon.fromTheme("edit-redo"), "Redo", menuBar)
        menuRedo.setShortcut("Ctrl+Y")
        menuRedo.setStatusTip("Redo Last Change")
        editMenu.addAction(menuRedo)

        # Edit > Separator
        editMenu.addSeparator()

        # Edit > Cut
        menuCut = QAction(QIcon.fromTheme("edit-cut"), "Cut", menuBar)
        menuCut.setShortcut("Ctrl+X")
        menuCut.setStatusTip("Cut Selected Text")
        editMenu.addAction(menuCut)

        # Edit > Copy
        menuCopy = QAction(QIcon.fromTheme("edit-copy"), "Copy", menuBar)
        menuCopy.setShortcut("Ctrl+C")
        menuCopy.setStatusTip("Copy Selected Text")
        editMenu.addAction(menuCopy)

        # Edit > Paste
        menuPaste = QAction(QIcon.fromTheme("edit-paste"), "Paste", menuBar)
        menuPaste.setShortcut("Ctrl+V")
        menuPaste.setStatusTip("Paste Text from Clipboard")
        editMenu.addAction(menuPaste)

        # Edit > Paste Plain Text
        menuPastePlain = QAction(QIcon.fromTheme("edit-paste"), "Paste Plain Text", menuBar)
        menuPastePlain.setShortcut("Ctrl+Shift+V")
        menuPastePlain.setStatusTip("Paste Plain Text from Clipboard")
        editMenu.addAction(menuPastePlain)

        # Edit > Separator
        editMenu.addSeparator()

        # Edit > Settings
        menuSettings = QAction(QIcon.fromTheme("applications-system"), "Program Setting", menuBar)
        menuSettings.setStatusTip("Change %s Settings" % nw.__package__)
        editMenu.addAction(menuSettings)

        ############################################################################################

        # Format
        formatMenu = menuBar.addMenu("&Format")

        # Format > Font Style
        menuFont = QAction(QIcon.fromTheme("preferences-desktop-font"), "Font Family", menuBar)
        menuFont.setStatusTip("Set Font for Selected text")
        formatMenu.addAction(menuFont)

        # Format > Separator
        formatMenu.addSeparator()

        # Format > Bold
        menuBold = QAction(QIcon.fromTheme("format-text-bold"), "Bold Text", menuBar)
        menuBold.setShortcut("Ctrl+B")
        menuBold.setStatusTip("Toggle Bold for Selected Text")
        formatMenu.addAction(menuBold)

        # Format > Italic
        menuItalic = QAction(QIcon.fromTheme("format-text-italic"), "Italic Text", menuBar)
        menuItalic.setShortcut("Ctrl+I")
        menuItalic.setStatusTip("Toggle Italic for Selected Text")
        formatMenu.addAction(menuItalic)

        # Format > Underline
        menuUnderline = QAction(QIcon.fromTheme("format-text-underline"), "Underline Text", menuBar)
        menuUnderline.setShortcut("Ctrl+U")
        menuUnderline.setStatusTip("Toggle Underline for Selected Text")
        formatMenu.addAction(menuUnderline)

        # Format > Strikethrough
        menuStrikethrough = QAction(QIcon.fromTheme("format-text-strikethrough"), "Strikethrough Text", menuBar)
        menuStrikethrough.setShortcut("Ctrl+D")
        menuStrikethrough.setStatusTip("Toggle Strikethrough for Selected Text")
        formatMenu.addAction(menuStrikethrough)

        # Format > Separator
        formatMenu.addSeparator()

        # Format > Clear
        menuClear = QAction(QIcon.fromTheme("edit-clear"), "Clear Formatting", menuBar)
        menuClear.setStatusTip("Clear Formatting for Selected Text")
        formatMenu.addAction(menuClear)

        ############################################################################################

        # Help
        helpMenu = menuBar.addMenu("&Help")

        # Help > About
        menuAbout = QAction(QIcon.fromTheme("help-about"), "About %s" % nw.__package__, menuBar)
        menuAbout.setStatusTip("About %s" % nw.__package__)
        menuAbout.triggered.connect(self._showAbout)
        helpMenu.addAction(menuAbout)

        # Help > About Qt5
        menuAboutQt5 = QAction(QIcon.fromTheme("help-about"), "About Qt5", menuBar)
        menuAboutQt5.setStatusTip("About Qt5")
        helpMenu.addAction(menuAboutQt5)

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

# END Class GuiMain
