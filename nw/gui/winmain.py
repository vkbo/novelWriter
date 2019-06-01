# -*- coding: utf-8 -*-
"""novelWriter GUI Main Window

 novelWriter – GUI Main Window
===============================
 Class holding the main window

 File History:
 Created: 2018-09-22 [0.0.1]

"""

import logging
import time
import nw

from os                   import path
from PyQt5.QtCore         import Qt, QTimer
from PyQt5.QtGui          import QIcon, QPixmap, QColor
from PyQt5.QtWidgets      import (
    qApp, QWidget, QMainWindow, QVBoxLayout, QFrame, QSplitter, QFileDialog,
    QShortcut, QMessageBox, QProgressDialog
)

from nw.theme             import Theme
from nw.gui.doctree       import GuiDocTree
from nw.gui.doceditor     import GuiDocEditor
from nw.gui.docviewer     import GuiDocViewer
from nw.gui.docdetails    import GuiDocDetails
from nw.gui.mainmenu      import GuiMainMenu
from nw.gui.projecteditor import GuiProjectEditor
from nw.gui.itemeditor    import GuiItemEditor
from nw.gui.statusbar     import GuiMainStatus
from nw.gui.timelineview  import GuiTimeLineView
from nw.project.project   import NWProject
from nw.project.document  import NWDoc
from nw.project.item      import NWItem
from nw.project.index     import NWIndex
from nw.convert.tokenizer import Tokenizer
from nw.convert.tohtml    import ToHtml
from nw.enum              import nwItemType, nwAlert
from nw.constants         import nwFiles
from nw.tools.wordcount   import countWords

logger = logging.getLogger(__name__)

class GuiMain(QMainWindow):

    def __init__(self):
        QWidget.__init__(self)

        logger.debug("Initialising GUI ...")
        self.mainConf    = nw.CONFIG
        self.theTheme    = Theme()
        self.theProject  = NWProject(self)
        self.theDocument = NWDoc(self.theProject, self)
        self.theIndex    = NWIndex(self.theProject, self)
        self.hasProject  = False

        self.resize(*self.mainConf.winGeometry)
        self._setWindowTitle()
        self.setWindowIcon(QIcon(path.join(self.mainConf.appRoot, nwFiles.APP_ICON)))
        self.theTheme.loadTheme()

        # Main GUI Elements
        self.docEditor  = GuiDocEditor(self)
        self.docViewer  = GuiDocViewer(self)
        self.docDetails = GuiDocDetails(self, self.theProject)
        self.treeView   = GuiDocTree(self, self.theProject)
        self.mainMenu   = GuiMainMenu(self, self.theProject)
        self.statusBar  = GuiMainStatus(self)

        # Minor Gui Elements
        self.statusIcons = []
        self.importIcons = []

        # Assemble Main Window
        self.treePane = QFrame()
        self.treeBox  = QVBoxLayout()
        self.treeBox.addWidget(self.treeView)
        self.treeBox.addWidget(self.docDetails)
        self.treePane.setLayout(self.treeBox)

        self.splitView = QSplitter(Qt.Horizontal)
        self.splitView.addWidget(self.docEditor)
        self.splitView.addWidget(self.docViewer)
        self.splitView.splitterMoved.connect(self._splitViewMove)

        self.splitMain = QSplitter(Qt.Horizontal)
        self.splitMain.addWidget(self.treePane)
        self.splitMain.addWidget(self.splitView)
        self.splitMain.setSizes(self.mainConf.mainPanePos)
        self.splitMain.splitterMoved.connect(self._splitMainMove)

        self.setCentralWidget(self.splitMain)

        self.idxTree   = self.splitMain.indexOf(self.treePane)
        self.idxMain   = self.splitMain.indexOf(self.splitView)
        self.idxEditor = self.splitView.indexOf(self.docEditor)
        self.idxViewer = self.splitView.indexOf(self.docViewer)

        self.splitMain.setCollapsible(self.idxTree,   False)
        self.splitMain.setCollapsible(self.idxMain,   False)
        self.splitView.setCollapsible(self.idxEditor, False)
        self.splitView.setCollapsible(self.idxViewer, True)

        self.docViewer.setVisible(False)

        # Build The Tree View
        self.treeView.itemSelectionChanged.connect(self._treeSingleClick)
        self.treeView.itemDoubleClicked.connect(self._treeDoubleClick)
        self.rebuildTree()

        # Set Main Window Elements
        self.setMenuBar(self.mainMenu)
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

        # Load Theme StyleSheet
        self.setStyleSheet(self.theTheme.cssData)

        # Set Up Autosaving Project Timer
        self.asProjTimer = QTimer()
        self.asProjTimer.setInterval(int(self.mainConf.autoSaveProj*1000))
        self.asProjTimer.timeout.connect(self._autoSaveProject)
        self.asProjTimer.start()

        # Set Up Autosaving Document Timer
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

    def clearGUI(self):
        self.treeView.clearTree()
        self.docEditor.clearEditor()
        self.closeDocViewer()
        self.statusBar.clearStatus()
        return True

    ##
    #  Project Actions
    ##

    def newProject(self, projPath=None, forceNew=False):

        if self.hasProject:
            msgBox = QMessageBox()
            msgRes = msgBox.warning(
                self, "New Project",
                "Please close the current project<br>before making a new one."
            )
            return False

        if projPath is None:
            projPath = self.newProjectDialog()
        if projPath is None:
            return False

        if path.isfile(path.join(projPath,self.theProject.projFile)) and not forceNew:
            msgBox = QMessageBox()
            msgRes = msgBox.critical(
                self, "New Project",
                "A project already exists in that location.<br>Please choose another folder."
            )
            return False

        logger.info("Creating new project")
        self.theProject.newProject()
        self.theProject.setProjectPath(projPath)
        self.rebuildTree()
        self.saveProject()
        self.hasProject = True
        self.statusBar.setRefTime(self.theProject.projOpened)

        return True

    def closeProject(self, isYes=False):
        """Closes the project if one is open.
        isYes is passed on from the close application event so the user doesn't get prompted twice.
        """
        if not self.hasProject:
            # There is no project loaded, everything OK
            return True

        if self.mainConf.showGUI and not isYes:
            msgBox = QMessageBox()
            msgRes = msgBox.question(
                self, "Close Project", "Save changes and close current project?"
            )
            if msgRes != QMessageBox.Yes:
                return False

        self.closeDocument()
        if self.theProject.projChanged:
            saveOK = self.saveProject()
        else:
            saveOK = True

        if saveOK:
            self.theProject.closeProject()
            self.theIndex.clearIndex()
            self.clearGUI()
            self.hasProject = False
    
        return saveOK

    def openProject(self, projFile=None):
        """Open a project.
        projFile is passed from the open recent projects menu, so can be set. If not, we pop the dialog.
        """
        if projFile is None:
            projFile = self.openProjectDialog()
        if projFile is None:
            return False

        # Make sure any open project is cleared out first before we load another one
        if not self.closeProject():
            return False

        # Try to open the project
        if not self.theProject.openProject(projFile):
            return False

        # Load the tag index
        self.theIndex.loadIndex()

        # Update GUI
        self._setWindowTitle(self.theProject.projName)
        self.rebuildTree()
        self.docEditor.setPwl(path.join(self.theProject.projMeta, nwFiles.PROJ_DICT))
        self.docEditor.setSpellCheck(self.theProject.spellCheck)
        self.statusBar.setRefTime(self.theProject.projOpened)
        self.mainMenu.updateMenu()

        # Restore previously open documents, if any
        if self.theProject.lastEdited is not None:
            self.openDocument(self.theProject.lastEdited)
        if self.theProject.lastViewed is not None:
            self.viewDocument(self.theProject.lastViewed)

        self.hasProject = True

        return True

    def saveProject(self):
        """Save the current project.
        """
        # If the project is new, it may not have a path, so we need one
        if self.theProject.projPath is None:
            projPath = self.saveProjectDialog()
            self.theProject.setProjectPath(projPath)
        if self.theProject.projPath is None:
            return False

        self.treeView.saveTreeOrder()
        self.theProject.saveProject()
        self.theIndex.saveIndex()
        self.mainMenu.updateRecentProjects()

        return True

    ##
    #  Document Actions
    ##

    def closeDocument(self):
        if self.docEditor.docChanged:
            self.saveDocument()
        self.theDocument.clearDocument()
        self.docEditor.clearEditor()
        return True

    def openDocument(self, tHandle):
        self.closeDocument()
        self.docEditor.loadText(tHandle)
        self.docEditor.changeWidth()
        self.docEditor.setFocus()
        self.theProject.setLastEdited(tHandle)
        return True

    def saveDocument(self):
        if self.theDocument.theItem is not None:
            docText = self.docEditor.getText()
            cursPos = self.docEditor.getCursorPosition()
            theItem = self.theDocument.theItem
            theItem.setCharCount(self.docEditor.charCount)
            theItem.setWordCount(self.docEditor.wordCount)
            theItem.setParaCount(self.docEditor.paraCount)
            theItem.setCursorPos(cursPos)
            self.theDocument.saveDocument(docText)
            self.docEditor.setDocumentChanged(False)
            self.theIndex.scanText(theItem.itemHandle, docText)
        return True

    def viewDocument(self, tHandle=None):

        if tHandle is None:
            tHandle = self.treeView.getSelectedHandle()
        if tHandle is None:
            logger.warning("No document selected")
            return False

        tItem = self.theProject.getItem(tHandle)
        if tItem is None:
            logger.warning("Item not found")
            return False

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
            vPos    = [0,0]
            vPos[0] = int(bPos[1]/2)
            vPos[1] = bPos[1]-vPos[0]
            self.splitView.setSizes(vPos)
            self.docEditor.changeWidth()

        return True

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
        if self.mainConf.showGUI:
            dlgProj = GuiItemEditor(self, self.theProject, tHandle)
            if dlgProj.exec_():
                self.treeView.setTreeItemValues(tHandle)

        return

    def rebuildTree(self):
        self._makeStatusIcons()
        self._makeImportIcons()
        self.treeView.clearTree()
        self.treeView.buildTree()
        return

    def rebuildIndex(self):

        logger.debug("Rebuilding indices ...")

        self.treeView.saveTreeOrder()
        self.theIndex.clearIndex()
        nItems = len(self.theProject.treeOrder)

        dlgProg = QProgressDialog("Scanning files ...", "Cancel", 0, nItems, self)
        dlgProg.setWindowModality(Qt.WindowModal)
        dlgProg.setMinimumDuration(0)
        dlgProg.setFixedWidth(480)
        dlgProg.setLabelText("Starting file scan ...")
        dlgProg.setValue(0)
        dlgProg.show()
        time.sleep(0.5)

        nDone = 0
        for tHandle in self.theProject.treeOrder:

            tItem = self.theProject.getItem(tHandle)

            dlgProg.setValue(nDone)
            dlgProg.setLabelText("Scanning: %s" % tItem.itemName)
            logger.verbose("Scanning: %s" % tItem.itemName)

            if tItem is not None and tItem.itemType == nwItemType.FILE:
                theDoc  = NWDoc(self.theProject, self)
                theText = theDoc.openDocument(tHandle, False)

                # Run Word Count
                cC, wC, pC = countWords(theText)
                tItem.setCharCount(cC)
                tItem.setWordCount(wC)
                tItem.setParaCount(pC)
                self.treeView.propagateCount(tHandle, wC)
                self.treeView.projectWordCount()

                # Build tag index
                self.theIndex.scanText(tHandle, theText)

            nDone += 1
            if dlgProg.wasCanceled():
                break

        dlgProg.setValue(nItems)

        return

    ##
    #  Main Dialogs
    ##

    def openProjectDialog(self):
        dlgOpt  = QFileDialog.Options()
        dlgOpt |= QFileDialog.DontUseNativeDialog
        projFile, _ = QFileDialog.getOpenFileName(
            self, "Open novelWriter Project", "",
            "novelWriter Project File (%s);;All Files (*)" % nwFiles.PROJ_FILE,
            options=dlgOpt
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

    def newProjectDialog(self):
        dlgOpt  = QFileDialog.Options()
        dlgOpt |= QFileDialog.ShowDirsOnly
        dlgOpt |= QFileDialog.DontUseNativeDialog
        projPath = QFileDialog.getExistingDirectory(
            self,"Select Location for New novelWriter Project","",options=dlgOpt
        )
        if projPath:
            return projPath
        return None

    def editProjectDialog(self):
        dlgProj = GuiProjectEditor(self, self.theProject)
        dlgProj.exec_()
        self._setWindowTitle(self.theProject.projName)
        return True

    def showTimeLineDialog(self):
        dlgTLine = GuiTimeLineView(self, self.theProject, self.theIndex)
        dlgTLine.exec_()
        return True

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
    #  Main Window Actions
    ##

    def closeMain(self):

        if self.mainConf.showGUI:
            msgBox = QMessageBox()
            msgRes = msgBox.question(
                self, "Exit", "Do you want to save changes and exit?"
            )
            if msgRes != QMessageBox.Yes:
                return False

        logger.info("Exiting %s" % nw.__package__)
        self.closeProject(True)

        self.mainConf.setWinSize(self.width(), self.height())
        self.mainConf.setTreeColWidths(self.treeView.getColumnSizes())
        self.mainConf.setMainPanePos(self.splitMain.sizes())
        self.mainConf.setDocPanePos(self.splitView.sizes())
        self.mainConf.saveConfig()

        qApp.quit()

        return True

    def setFocus(self, paneNo):
        if paneNo == 1:
            self.treeView.setFocus()
        elif paneNo == 2:
            self.docEditor.setFocus()
        elif paneNo == 3:
            self.docViewer.setFocus()
        return

    def closeDocEditor(self):
        self.closeDocument()
        self.theProject.setLastEdited(None)
        return

    def closeDocViewer(self):
        self.docViewer.clearViewer()
        self.theProject.setLastViewed(None)
        bPos = self.splitMain.sizes()
        self.docViewer.setVisible(False)
        vPos = [bPos[1],0]
        self.splitView.setSizes(vPos)
        self.docEditor.changeWidth()
        return not self.docViewer.isVisible()

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
        if self.hasProject and self.theProject.projChanged and self.theProject.projPath is not None:
            logger.debug("Autosaving project")
            self.saveProject()
        return

    def _autoSaveDocument(self):
        if self.hasProject and self.docEditor.docChanged and self.theDocument.theItem is not None:
            logger.debug("Autosaving document")
            self.saveDocument()
        return

    def _makeStatusIcons(self):
        self.statusIcons = {}
        for sLabel, sCol, _ in self.theProject.statusItems:
            theIcon = QPixmap(32,32)
            theIcon.fill(QColor(*sCol))
            self.statusIcons[sLabel] = QIcon(theIcon)
        return

    def _makeImportIcons(self):
        self.importIcons = {}
        for sLabel, sCol, _ in self.theProject.importItems:
            theIcon = QPixmap(32,32)
            theIcon.fill(QColor(*sCol))
            self.importIcons[sLabel] = QIcon(theIcon)
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
        if self.closeMain():
            theEvent.accept()
        else:
            theEvent.ignore()
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

    def _splitViewMove(self, pWidth, pHeight):
        """Alert dependent GUI elements that the main pane splitter has been moved.
        """
        self.docEditor.changeWidth()
        return

# END Class GuiMain
