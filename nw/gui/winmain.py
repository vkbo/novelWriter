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
from PyQt5.QtGui          import QIcon, QPixmap, QColor
from PyQt5.QtCore         import Qt, QTimer

from nw.gui.doctree       import GuiDocTree
from nw.gui.doceditor     import GuiDocEditor
from nw.gui.docviewer     import GuiDocViewer
from nw.gui.docdetails    import GuiDocDetails
from nw.gui.mainmenu      import GuiMainMenu
from nw.gui.projecteditor import GuiProjectEditor
from nw.gui.itemeditor    import GuiItemEditor
from nw.gui.statusbar     import GuiMainStatus
from nw.project.project   import NWProject
from nw.project.document  import NWDoc
from nw.project.item      import NWItem
from nw.convert.tokenizer import Tokenizer
from nw.convert.tohtml    import ToHtml
from nw.enum              import nwItemType, nwAlert

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
        self.docViewer  = GuiDocViewer(self)
        self.docDetails = GuiDocDetails(self, self.theProject)
        self.treeView   = GuiDocTree(self, self.theProject)
        self.mainMenu   = GuiMainMenu(self, self.theProject)
        self.statusBar  = GuiMainStatus(self)

        # Minor Gui Elements
        self.statusIcons  = []
        self.statusLabels = []
        self.importIcons  = []
        self.importLabels = []

        # Assemble Main Window
        self.treePane = QFrame()
        self.treeBox  = QVBoxLayout()
        self.treeBox.addWidget(self.treeView)
        self.treeBox.addWidget(self.docDetails)
        self.treePane.setLayout(self.treeBox)

        self.splitMain = QSplitter(Qt.Horizontal)
        self.splitMain.addWidget(self.treePane)
        self.splitMain.addWidget(self.docEditor)
        self.splitMain.addWidget(self.docViewer)
        self.splitMain.setSizes(self.mainConf.mainPanePos)
        self.splitMain.splitterMoved.connect(self._splitMainMove)

        self.setCentralWidget(self.splitMain)

        self.idxTree   = self.splitMain.indexOf(self.treePane)
        self.idxEditor = self.splitMain.indexOf(self.docEditor)
        self.idxViewer = self.splitMain.indexOf(self.docViewer)

        self.splitMain.setCollapsible(self.idxTree,   False)
        self.splitMain.setCollapsible(self.idxEditor, False)
        self.splitMain.setCollapsible(self.idxViewer, True)

        self.docViewer.setVisible(False)
        pPos = self.mainConf.mainPanePos
        tPos = [pPos[0], pPos[1]+pPos[2]]
        self.splitMain.setSizes(tPos)

        # Build GUI Elements
        self.treeView.itemSelectionChanged.connect(self._treeSingleClick)
        self.treeView.itemDoubleClicked.connect(self._treeDoubleClick)
        self.treeView.buildTree()
        self._makeStatusIcons()
        self._makeImportIcons()

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

        # Keyboard Shortcuts
        QShortcut(Qt.Key_Return, self.treeView, context=Qt.WidgetShortcut, activated=self._treeKeyPressReturn)

        # Forward Functions
        self.setStatus        = self.statusBar.setStatus
        self.setProjectStatus = self.statusBar.setProjectStatus

        if self.mainConf.showGUI:
            self.show()

        logger.debug("GUI initialisation complete")

        return

    def makeAlert(self, theMessage, theLevel=nwAlert.INFO):
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
        if theLevel == nwAlert.INFO:
            for msgLine in logMsg:
                logger.info(msgLine)
            msgBox.information(self, "Information", popMsg)
        elif theLevel == nwAlert.WARN:
            for msgLine in logMsg:
                logger.warning(msgLine)
            msgBox.warning(self, "Warning", popMsg)
        elif theLevel == nwAlert.ERROR:
            for msgLine in logMsg:
                logger.error(msgLine)
            msgBox.critical(self, "Error", popMsg)
        elif theLevel == nwAlert.BUG:
            for msgLine in logMsg:
                logger.error(msgLine)
            popMsg += "<br>This is a bug!"
            msgBox.critical(self, "Internal Error", popMsg)

        return

    ##
    #  Project Actions
    ##

    def newProject(self):
        logger.info("Creating new project")
        self.treeView.clearTree()
        if self.saveProject():
            self.theProject.newProject()
            self.treeView.buildTree()
        return True

    def openProject(self, projFile=None):
        if projFile is None:
            projFile = self.openProjectDialog()
        if projFile is None:
            return False
        self.treeView.clearTree()
        self.theProject.openProject(projFile)
        self.treeView.buildTree()
        self._setWindowTitle(self.theProject.projName)
        self._makeStatusIcons()
        self._makeImportIcons()
        self.docEditor.setPwl(path.join(self.theProject.projMeta,"wordlist.txt"))
        self.docEditor.setSpellCheck(self.theProject.spellCheck)
        self.mainMenu.updateMenu()
        if self.theProject.lastEdited is not None:
            self.openDocument(self.theProject.lastEdited)
        if self.theProject.lastViewed is not None:
            self.viewDocument(self.theProject.lastViewed)
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
        self.docEditor.setText(self.theDocument.openDocument(tHandle))
        self.docEditor.setReadOnly(False)
        self.docEditor.setCursorPosition(self.theDocument.theItem.cursorPos)
        self.docEditor.changeWidth()
        self.docEditor.setFocus()
        self.theProject.setLastEdited(tHandle)
        return True

    def saveDocument(self):
        if self.theDocument.theItem is not None:
            docHtml = self.docEditor.getText()
            cursPos = self.docEditor.getCursorPosition()
            self.theDocument.theItem.setCharCount(self.docEditor.charCount)
            self.theDocument.theItem.setWordCount(self.docEditor.wordCount)
            self.theDocument.theItem.setParaCount(self.docEditor.paraCount)
            self.theDocument.theItem.setCursorPos(cursPos)
            self.theDocument.saveDocument(docHtml)
            self.docEditor.setDocumentChanged(False)
        return True

    def viewDocument(self, tHandle=None):

        if tHandle is None:
            tHandle = self.treeView.getSelectedHandle()
        if tHandle is None:
            logger.warning("No document selected")
            return

        tItem = self.theProject.getItem(tHandle)
        if tItem.itemType == nwItemType.FILE:
            logger.debug("Generating preview for item %s" % tHandle)
            aDoc = ToHtml(self.theProject, self)
            aDoc.setText(tHandle)
            aDoc.tokenizeText()
            aDoc.doConvert()
            self.docViewer.setHtml(aDoc.theResult)
            self.theProject.setLastViewed(tHandle)

            bPos = self.splitMain.sizes()
            self.docViewer.setVisible(True)
            if bPos[2] == 0:
                bWidth  = bPos[1]+bPos[2]
                bPos[1] = int(bWidth/2)
                bPos[2] = bWidth-bPos[1]
            self.splitMain.setSizes(bPos)
            self.docEditor.changeWidth()

        return

    ##
    #  Tree Item Actions
    ##

    def openSelectedItem(self):
        tHandle = self.treeView.getSelectedHandle()
        if tHandle is None:
            logger.warning("No item selected")
            return False

        logger.verbose("Opening item %s" % tHandle)
        nwItem = self.theProject.getItem(tHandle)
        if nwItem.itemType == nwItemType.FILE:
            logger.verbose("Requested item %s is a file" % tHandle)
            self.openDocument(tHandle)
        else:
            logger.verbose("Requested item %s is not a file" % tHandle)

        return True

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
            self.docEditor.setFocus()
        elif paneNo == 3:
            self.docViewer.setFocus()
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
        if self.theDocument.theItem is None:
            return False
        if not self.docEditor.docChanged:
            return False
        return True

    def _makeStatusIcons(self):
        self.statusIcons  = []
        self.statusLabels = []
        for sLabel, sR, sG, sB in self.theProject.statusCols:
            theIcon = QPixmap(32,32)
            theIcon.fill(QColor(sR,sG,sB))
            self.statusIcons.append(QIcon(theIcon))
            self.statusLabels.append(sLabel)
        return

    def _makeImportIcons(self):
        self.importIcons  = []
        self.importLabels = []
        for sLabel, sR, sG, sB in self.theProject.importCols:
            theIcon = QPixmap(32,32)
            theIcon.fill(QColor(sR,sG,sB))
            self.importIcons.append(QIcon(theIcon))
            self.importLabels.append(sLabel)
        return

    ##
    #  Events
    ##

    def resizeEvent(self, theEvent):
        """Extend QMainWindow.resizeEvent to signal dependent GUI elements that its pane may have changed size.
        """
        QMainWindow.resizeEvent(self,theEvent)
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
        self.docEditor.changeWidth()
        return

# END Class GuiMain
