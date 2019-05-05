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
from PyQt5.QtWidgets      import QWidget, QMainWindow, QVBoxLayout, QFrame, QSplitter, QFileDialog, QStackedWidget, QShortcut, QMessageBox
from PyQt5.QtGui          import QIcon
from PyQt5.QtCore         import Qt, QTimer

from nw.gui.doctree       import GuiDocTree
from nw.gui.doceditor     import GuiDocEditor
from nw.gui.docdetails    import GuiDocDetails
from nw.gui.mainmenu      import GuiMainMenu
from nw.gui.projecteditor import GuiProjectEditor
from nw.gui.itemeditor    import GuiItemEditor
from nw.gui.statusbar     import GuiMainStatus
from nw.project.project   import NWProject
from nw.project.document  import NWDoc
from nw.project.item      import NWItem
from nw.convert.tokenizer import Tokenizer
from nw.enum              import nwItemType

logger = logging.getLogger(__name__)

class GuiMain(QMainWindow):

    def __init__(self):
        QWidget.__init__(self)

        logger.debug("Initialising GUI ...")
        self.mainConf    = nw.CONFIG
        self.theProject  = NWProject(self)
        self.theDocument = NWDoc(self.theProject, self)

        self.resize(*self.mainConf.winGeometry)
        self._setWindowTitle()
        self.setWindowIcon(QIcon(path.join(self.mainConf.appPath,"..","novelWriter.svg")))

        # Main GUI Elements
        self.docEditor  = GuiDocEditor(self)
        self.docDetails = GuiDocDetails(self, self.theProject)
        self.treeView   = GuiDocTree(self, self.theProject)
        self.mainMenu   = GuiMainMenu(self, self.theProject)
        self.statusBar  = GuiMainStatus(self)

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

        # Build GUI Elements
        self.treeView.itemSelectionChanged.connect(self._treeSingleClick)
        self.treeView.itemDoubleClicked.connect(self._treeDoubleClick)
        self.treeView.buildTree()
        QShortcut(Qt.Key_Return, self.treeView, context=Qt.WidgetShortcut, activated=self._treeKeyPressReturn)

        # Set Main Window Elements
        self.setMenuBar(self.mainMenu)
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

        # Load Theme StyleSheet
        cssFile = path.join(self.mainConf.themePath,self.mainConf.guiTheme+".css")
        if path.isfile(cssFile):
            with open(cssFile,mode="r") as inFile:
                theCss = inFile.read()
            self.setStyleSheet(theCss)

        self.asProjTimer = QTimer()
        self.asProjTimer.setInterval(int(self.mainConf.autoSaveProj*1000))
        self.asProjTimer.timeout.connect(self._autoSaveProject)
        self.asProjTimer.start()

        self.asDocTimer = QTimer()
        self.asDocTimer.setInterval(int(self.mainConf.autoSaveDoc*1000))
        self.asDocTimer.timeout.connect(self._autoSaveDocument)
        self.asDocTimer.start()

        self.show()

        logger.debug("GUI initialisation complete")

        return

    def makeAlert(self, theMessage, theLevel):
        """Alert both the user and the logger at the same time. Message can be either a string or an
        array of strings. Severity level is 0 = info, 1 = warning, and 2 = error.
        """

        if isinstance(theMessage, list):
            popMsg = "<br>".join(theMessage)
            logMsg = theMessage
        else:
            popMsg = theMessage
            logMsg = [theMessage]

        msgBox = QMessageBox()
        if theLevel == 0:
            for msgLine in logMsg:
                logger.info(msgLine)
            msgBox.information(self, "Information", popMsg)
        elif theLevel == 1:
            for msgLine in logMsg:
                logger.warning(msgLine)
            msgBox.warning(self, "Warning", popMsg)
        elif theLevel == 2:
            for msgLine in logMsg:
                logger.error(msgLine)
            msgBox.critical(self, "Error", popMsg)

        return

    ##
    #  Project Actions
    ##

    def newProject(self):
        logger.info("Creating new project")
        self.treeView.clearTree()
        self.theProject.newProject()
        self.treeView.buildTree()
        return

    def openProject(self, projFile=None):
        if projFile is None:
            projFile = self.openProjectDialog()
        if projFile is None:
            return False
        self.treeView.clearTree()
        self.theProject.openProject(projFile)
        self.treeView.buildTree()
        self.mainMenu.updateRecentProjects()
        self._setWindowTitle(self.theProject.projName)
        return True

    def saveProject(self):
        if self.theProject.projPath is None:
            projPath = self.saveProjectDialog()
            self.theProject.setProjectPath(projPath)
        self.treeView.saveTreeOrder()
        self.theProject.saveProject()
        self.mainMenu.updateRecentProjects()
        return True

    ##
    #  Document Actions
    ##

    def openDocument(self, tHandle):
        if self._takeDocumentAction():
            self.saveDocument()
        self.stackPane.setCurrentIndex(self.stackDoc)
        self.docEditor.setText(self.theDocument.openDocument(tHandle))
        self.docEditor.changeWidth()
        return

    def saveDocument(self):
        if self.theDocument.theItem is not None:
            docHtml = self.docEditor.getText()
            self.theDocument.theItem.setCharCount(self.docEditor.charCount)
            self.theDocument.theItem.setWordCount(self.docEditor.wordCount)
            self.theDocument.theItem.setParaCount(self.docEditor.paraCount)
            self.theDocument.saveDocument(docHtml)
            self.docEditor.setDocumentChanged(False)
        return

    def _previewDocument(self):

        theHandles = self.treeView.getSelectedHandles()
        if len(theHandles) == 0:
            return

        theDocs = []
        self.treeView.saveTreeOrder()
        for tHandle in self.theProject.treeOrder:
            if tHandle not in theHandles:
                continue
            aDoc = Tokenizer(self.theProject, self)
            aDoc.tokenizeText(tHandle)

        return

    ##
    #  Tree Item Actions
    ##

    def openSelectedItem(self):
        tHandle = self.treeView.getSelectedHandle()
        if tHandle is None:
            logger.warning("No item selected")
            return

        logger.verbose("Opening item %s" % tHandle)
        nwItem = self.theProject.getItem(tHandle)
        if nwItem.itemType == nwItemType.FILE:
            logger.verbose("Requested item %s is a file" % tHandle)
            self.openDocument(tHandle)
        else:
            logger.verbose("Requested item %s is not a file" % tHandle)
        return

    def editItem(self):
        tHandle = self.treeView.getSelectedHandle()
        if tHandle is None:
            logger.warning("No item selected")
            return

        logger.verbose("Requesting change to item %s" % tHandle)
        dlgProj = GuiItemEditor(self, self.theProject, tHandle)
        if dlgProj.exec_():
            self.treeView.setTreeItemValues(tHandle)

        return

    ##
    #  Main Dialogs
    ##

    def openProjectDialog(self):
        dlgOpt  = QFileDialog.Options()
        dlgOpt |= QFileDialog.DontUseNativeDialog
        projFile, _ = QFileDialog.getOpenFileName(
            self,"Open novelWriter Project","","novelWriter Project File (nwProject.nwx);;All Files (*)",options=dlgOpt
        )
        if projFile:
            return projFile
        return None

    def saveProjectDialog(self):
        dlgOpt  = QFileDialog.Options()
        dlgOpt |= QFileDialog.ShowDirsOnly
        dlgOpt |= QFileDialog.DontUseNativeDialog
        projPath = QFileDialog.getExistingDirectory(
            self,"Save novelWriter Project","",options=dlgOpt
        )
        if projPath:
            return projPath
        return None

    def editProjectDialog(self):
        dlgProj = GuiProjectEditor(self, self.theProject)
        dlgProj.exec_()
        self._setWindowTitle(self.theProject.projName)
        return True

    ##
    #  Main Window Actions
    ##

    def closeMain(self):
        logger.info("Exiting %s" % nw.__package__)
        if self._takeDocumentAction():
            self.saveDocument()
        if self._takeProjectAction():
            self.saveProject()
        self.mainConf.setWinSize(self.width(), self.height())
        self.mainConf.setTreeColWidths(self.treeView.getColumnSizes())
        self.mainConf.setMainPanePos(self.splitMain.sizes())
        self.mainConf.saveConfig()
        return

    def setFocus(self, paneNo):
        if paneNo == 1:
            self.treeView.setFocus()
        elif paneNo == 2:
            if self.stackPane.currentIndex() == self.stackDoc:
                self.docEditor.setFocus()
        return

    ##
    #  Internal Functions
    ##

    def _setWindowTitle(self, projName=None):
        winTitle = "%s [%s]" % (nw.__package__, nw.__version__)
        if projName is not None:
            winTitle += " - %s" % projName
        self.setWindowTitle(winTitle)
        return True

    def _autoSaveProject(self):
        if self._takeProjectAction():
            logger.debug("Autosaving project")
            self.saveProject()
        return

    def _autoSaveDocument(self):
        if self._takeDocumentAction():
            logger.debug("Autosaving document")
            self.saveDocument()
        return

    def _takeProjectAction(self):
        if self.theProject.projPath is None:
            return False
        if not self.theProject.projChanged:
            return False
        return True

    def _takeDocumentAction(self):
        if self.stackPane.currentIndex() != self.stackDoc:
            return False
        if self.theDocument.theItem is None:
            return False
        if not self.docEditor.docChanged:
            return False
        return True

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
        self.closeMain()
        QMainWindow.closeEvent(self,theEvent)
        return

    ##
    #  Signal Handlers
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

    def _treeKeyPressReturn(self):
        tHandle = self.treeView.getSelectedHandle()
        logger.verbose("User pressed return on tree item with handle %s" % tHandle)
        nwItem = self.theProject.getItem(tHandle)
        if nwItem.itemType == nwItemType.FILE:
            logger.verbose("Requested item %s is a file" % tHandle)
            self.openDocument(tHandle)
        else:
            logger.verbose("Requested item %s is a folder" % tHandle)
        return

    def _splitMainMove(self, pWidth, pHeight):
        """Alert dependent GUI elements that the main pane splitter has been moved.
        """
        if self.stackPane.currentIndex() == self.stackDoc:
            self.docEditor.changeWidth()
        return

# END Class GuiMain
