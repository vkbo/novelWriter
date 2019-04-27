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
from PyQt5.QtCore         import Qt, QSize, pyqtSlot
from PyQt5.QtGui          import QIcon

from nw.gui.doctree       import GuiDocTree
from nw.gui.doctreectx    import GuiDocTreeCtx
from nw.gui.doceditor     import GuiDocEditor
from nw.gui.docdetails    import GuiDocDetails
from nw.gui.projecteditor import GuiProjectEditor
from nw.gui.statusbar     import GuiMainStatus
from nw.project.project   import NWProject
from nw.project.document  import NWDoc
from nw.project.item      import NWItem
from nw.enum              import nwItemType, nwItemClass, nwDocAction, nwItemAction

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

        # Main GUI Elements
        self.docEditor  = GuiDocEditor(self)
        self.docDetails = GuiDocDetails(self.theProject)
        self.treeView   = GuiDocTree(self.theProject)

        # Assemble Main Window
        self.stackPane = QStackedWidget()
        self.stackNone = self.stackPane.addWidget(QWidget())
        self.stackDoc  = self.stackPane.addWidget(self.docEditor)
        self.stackPane.setCurrentIndex(self.stackNone)

        self.treePane = QFrame()
        self.treeBox  = QVBoxLayout()
        self.treeBox.addWidget(self.treeView)
        self.treeBox.addWidget(self.docDetails)
        self.treePane.setLayout(self.treeBox)

        self.splitMain = QSplitter(Qt.Horizontal)
        self.splitMain.addWidget(self.treePane)
        self.splitMain.addWidget(self.stackPane)
        self.splitMain.setSizes(self.mainConf.mainPanePos)
        self.splitMain.splitterMoved.connect(self._splitMainMove)

        self.setCentralWidget(self.splitMain)

        # Build Menus
        self._buildMenu()
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self._openDocTreeContextMenu)
        self.treeView.itemSelectionChanged.connect(self._treeSingleClick)
        self.treeView.itemDoubleClicked.connect(self._treeDoubleClick)
        self.treeView.buildTree()

        # Build Status Bar
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

    ##
    #  Project Actions
    ##

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

    def openRecentProject(self, menuItem, recentItem):
        logger.verbose("User requested opening recent project #%d" % recentItem)
        self.theProject.openProject(self.mainConf.recentList[recentItem])
        self.treeView.buildTree()
        self._setWindowTitle(self.theProject.projName)
        return True

    ##
    #  Document Actions
    ##

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

    ##
    #  Internal Functions
    ##

    def _treeSingleClick(self):
        sHandle = self.treeView.getSelectedHandle()
        if sHandle is not None:
            self.docDetails.buildViewBox(sHandle)
        return

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

        # print(selHandle, selAction, selClass, selType, selTarget)

        if   selAction == nwItemAction.ADD_ROOT:
            self.treeView.newTreeItem(selHandle, selType, selClass)
        elif selAction == nwItemAction.ADD_FOLDER:
            self.treeView.newTreeItem(selHandle, selType, selClass)
        elif selAction == nwItemAction.ADD_FILE:
            self.treeView.newTreeItem(selHandle, selType, selClass)
        elif selAction == nwItemAction.MOVE_UP:
            self.treeView.moveTreeItem(selHandle, -1)
        elif selAction == nwItemAction.MOVE_DOWN:
            self.treeView.moveTreeItem(selHandle, 1)
        elif selAction == nwItemAction.MOVE_TO:
            pass
        elif selAction == nwItemAction.MOVE_TRASH:
            pass
        elif selAction == nwItemAction.SPLIT:
            pass
        elif selAction == nwItemAction.MERGE:
            pass
        elif selAction == nwItemAction.DELETE:
            pass
        elif selAction == nwItemAction.DELETE_ROOT:
            pass
        elif selAction == nwItemAction.EMPTY_TRASH:
            pass
        elif selAction == nwItemAction.RENAME:
            self.treeView.renameTreeItem(selHandle)

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

# END Class GuiMain
