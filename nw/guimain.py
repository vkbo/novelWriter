# -*- coding: utf-8 -*-
"""novelWriter GUI Main Window

 novelWriter – GUI Main Window
===============================
 Class holding the main window

 File History:
 Created: 2018-09-22 [0.0.1]

 This file is a part of novelWriter
 Copyright 2018–2020, Veronica Berglyd Olsen

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import nw
import logging
import os

from datetime import datetime
from time import time

from PyQt5.QtCore import Qt, QTimer, QThreadPool
from PyQt5.QtGui import QIcon, QPixmap, QColor, QKeySequence, QCursor
from PyQt5.QtWidgets import (
    qApp, QMainWindow, QVBoxLayout, QWidget, QSplitter, QFileDialog, QShortcut,
    QMessageBox, QDialog, QTabWidget
)

from nw.gui import (
    GuiAbout, GuiBuildNovel, GuiDocEditor, GuiDocMerge, GuiDocSplit,
    GuiDocViewDetails, GuiDocViewer, GuiItemDetails, GuiItemEditor,
    GuiMainMenu, GuiMainStatus, GuiOutline, GuiOutlineDetails, GuiPreferences,
    GuiProjectLoad, GuiProjectSettings, GuiProjectTree, GuiProjectWizard,
    GuiTheme, GuiWritingStats
)
from nw.core import NWProject, NWDoc, NWIndex
from nw.constants import nwItemType, nwItemClass, nwAlert
from nw.common import getGuiItem

logger = logging.getLogger(__name__)

class GuiMain(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        logger.debug("Initialising GUI ...")
        self.setObjectName("GuiMain")
        self.mainConf = nw.CONFIG
        self.threadPool = QThreadPool()

        # Some runtime info useful for debugging
        logger.info("OS: %s" % self.mainConf.osType)
        logger.info("Kernel: %s" % self.mainConf.kernelVer)
        logger.info("Host: %s" % self.mainConf.hostName)
        logger.info("Qt5 Version: %s (%d)" % (
            self.mainConf.verQtString, self.mainConf.verQtValue)
        )
        logger.info("PyQt5 Version: %s (%d)" % (
            self.mainConf.verPyQtString, self.mainConf.verPyQtValue)
        )
        logger.info("Python Version: %s (0x%x)" % (
            self.mainConf.verPyString, self.mainConf.verPyHexVal)
        )

        # Core Classes and settings
        self.theTheme    = GuiTheme(self)
        self.theProject  = NWProject(self)
        self.theIndex    = NWIndex(self.theProject, self)
        self.hasProject  = False
        self.isFocusMode = False

        # Prepare main window
        self.resize(*self.mainConf.getWinSize())
        self._setWindowTitle()
        self.setWindowIcon(QIcon(self.mainConf.appIcon))

        # Build the GUI
        ################

        # Main GUI Elements
        self.statusBar = GuiMainStatus(self)
        self.treeView  = GuiProjectTree(self)
        self.docEditor = GuiDocEditor(self)
        self.viewMeta  = GuiDocViewDetails(self)
        self.docViewer = GuiDocViewer(self)
        self.treeMeta  = GuiItemDetails(self)
        self.projView  = GuiOutline(self)
        self.projMeta  = GuiOutlineDetails(self)
        self.mainMenu  = GuiMainMenu(self)

        # Minor Gui Elements
        self.statusIcons = []
        self.importIcons = []

        # Assemble Main Window
        self.treePane = QWidget()
        self.treeBox = QVBoxLayout()
        self.treeBox.setContentsMargins(0, 0, 0, 0)
        self.treeBox.addWidget(self.treeView)
        self.treeBox.addWidget(self.treeMeta)
        self.treePane.setLayout(self.treeBox)

        self.splitView = QSplitter(Qt.Vertical)
        self.splitView.addWidget(self.docViewer)
        self.splitView.addWidget(self.viewMeta)
        self.splitView.setSizes(self.mainConf.getViewPanePos())

        self.splitDocs = QSplitter(Qt.Horizontal)
        self.splitDocs.addWidget(self.docEditor)
        self.splitDocs.addWidget(self.splitView)

        self.splitOutline = QSplitter(Qt.Vertical)
        self.splitOutline.addWidget(self.projView)
        self.splitOutline.addWidget(self.projMeta)
        self.splitOutline.setSizes(self.mainConf.getOutlinePanePos())

        self.tabWidget = QTabWidget()
        self.tabWidget.setTabPosition(QTabWidget.East)
        self.tabWidget.setStyleSheet("QTabWidget::pane {border: 0;}")
        self.tabWidget.addTab(self.splitDocs, "Editor")
        self.tabWidget.addTab(self.splitOutline, "Outline")
        self.tabWidget.currentChanged.connect(self._mainTabChanged)

        xCM = self.mainConf.pxInt(4)
        self.splitMain = QSplitter(Qt.Horizontal)
        self.splitMain.setContentsMargins(xCM, xCM, xCM, xCM)
        self.splitMain.addWidget(self.treePane)
        self.splitMain.addWidget(self.tabWidget)
        self.splitMain.setSizes(self.mainConf.getMainPanePos())

        self.idxTree     = self.splitMain.indexOf(self.treePane)
        self.idxMain     = self.splitMain.indexOf(self.tabWidget)
        self.idxEditor   = self.splitDocs.indexOf(self.docEditor)
        self.idxViewer   = self.splitDocs.indexOf(self.splitView)
        self.idxViewDoc  = self.splitView.indexOf(self.docViewer)
        self.idxViewMeta = self.splitView.indexOf(self.viewMeta)
        self.idxTabEdit  = self.tabWidget.indexOf(self.splitDocs)
        self.idxTabProj  = self.tabWidget.indexOf(self.splitOutline)

        self.splitMain.setCollapsible(self.idxTree, False)
        self.splitMain.setCollapsible(self.idxMain, False)
        self.splitDocs.setCollapsible(self.idxEditor, False)
        self.splitDocs.setCollapsible(self.idxViewer, True)
        self.splitView.setCollapsible(self.idxViewDoc, False)
        self.splitView.setCollapsible(self.idxViewMeta, False)

        self.splitView.setVisible(False)
        self.docEditor.closeSearch()

        # Build the Tree View
        self.treeView.itemSelectionChanged.connect(self._treeSingleClick)
        self.treeView.itemDoubleClicked.connect(self._treeDoubleClick)
        self.rebuildTree()

        # Set Main Window Elements
        self.setMenuBar(self.mainMenu)
        self.setCentralWidget(self.splitMain)
        self.setStatusBar(self.statusBar)

        # Finalise Initialisation
        ##########################

        # Set Up Autosaving Project Timer
        self.asProjTimer = QTimer()
        self.asProjTimer.timeout.connect(self._autoSaveProject)

        # Set Up Autosaving Document Timer
        self.asDocTimer = QTimer()
        self.asDocTimer.timeout.connect(self._autoSaveDocument)

        # Shortcuts and Actions
        self._connectMenuActions()

        keyReturn = QShortcut(self.treeView)
        keyReturn.setKey(QKeySequence(Qt.Key_Return))
        keyReturn.activated.connect(self._treeKeyPressReturn)

        keyEscape = QShortcut(self)
        keyEscape.setKey(QKeySequence(Qt.Key_Escape))
        keyEscape.activated.connect(self._keyPressEscape)

        # Forward Functions
        self.setStatus = self.statusBar.setStatus
        self.setProjectStatus = self.statusBar.setProjectStatus

        # Force a show of the GUI
        self.show()

        # Check that config loaded fine
        self.reportConfErr()

        self.initMain()
        self.asProjTimer.start()
        self.asDocTimer.start()
        self.statusBar.clearStatus()

        self.showNormal()
        if self.mainConf.isFullScreen:
            self.toggleFullScreenMode()

        logger.debug("GUI initialisation complete")

        # Check if a project path was provided at command line, and if
        # not, open the project manager instead.
        if self.mainConf.cmdOpen is not None:
            logger.debug("Opening project from additional command line option")
            self.openProject(self.mainConf.cmdOpen)
        else:
            if self.mainConf.showGUI:
                self.showProjectLoadDialog()

        logger.debug("novelWriter is ready ...")
        self.statusBar.setStatus("novelWriter is ready ...")

        return

    def clearGUI(self):
        """Wrapper function to clear all sub-elements of the main GUI.
        """
        self.treeView.clearTree()
        self.docEditor.clearEditor()
        self.closeDocViewer()
        self.statusBar.clearStatus()
        return True

    def initMain(self):
        """Initialise elements that depend on user settings.
        """
        self.asProjTimer.setInterval(int(self.mainConf.autoSaveProj*1000))
        self.asDocTimer.setInterval(int(self.mainConf.autoSaveDoc*1000))
        return True

    ##
    #  Project Actions
    ##

    def newProject(self, projData=None):
        """Create new project with a few default files and folders.
        The variable forceNew is used for testing.
        """
        if self.hasProject:
            self.makeAlert(
                "Please close the current project before making a new one.",
                nwAlert.ERROR
            )
            return False

        if projData is None:
            projData = self.showNewProjectDialog()

        if projData is None:
            return False

        projPath = projData.get("projPath", None)
        if projPath is None or projData is None:
            logger.error("No projData or projPath set")
            return False

        if os.path.isfile(os.path.join(projPath, self.theProject.projFile)):
            self.makeAlert(
                "A project already exists in that location. Please choose another folder.",
                nwAlert.ERROR
            )
            return False

        logger.info("Creating new project")
        if self.theProject.newProject(projData):
            self.rebuildTree()
            self.saveProject()
            self.hasProject = True
            self.statusBar.setRefTime(self.theProject.projOpened)
            self.rebuildIndex(beQuiet=True)
        else:
            self.theProject.clearProject()
            return False

        return True

    def closeProject(self, isYes=False):
        """Closes the project if one is open. isYes is passed on from
        the close application event so the user doesn't get prompted
        twice.
        """
        if not self.hasProject:
            # There is no project loaded, everything OK
            return True

        if not isYes:
            msgBox = QMessageBox()
            msgRes = msgBox.question(
                self, "Close Project", "Save changes and close current project?"
            )
            if msgRes != QMessageBox.Yes:
                return False

        if self.docEditor.docChanged:
            self.saveDocument()

        if self.theProject.projAltered:
            saveOK   = self.saveProject()
            doBackup = False
            if self.theProject.doBackup and self.mainConf.backupOnClose:
                doBackup = True
                if self.mainConf.askBeforeBackup:
                    msgBox = QMessageBox()
                    msgRes = msgBox.question(
                        self, "Backup Project", "Backup current project?"
                    )
                    if msgRes != QMessageBox.Yes:
                        doBackup = False
            if doBackup:
                self.theProject.zipIt(False)
        else:
            saveOK = True

        if saveOK:
            self.closeDocument()
            self.docViewer.clearNavHistory()
            self.projView.closeOutline()
            self.theProject.closeProject()
            self.theIndex.clearIndex()
            self.clearGUI()
            self.hasProject = False
            self.tabWidget.setCurrentWidget(self.splitDocs)

        return saveOK

    def openProject(self, projFile):
        """Open a project from a projFile path.
        """
        if projFile is None:
            return False

        # Make sure any open project is cleared out first before we load
        # another one
        if not self.closeProject():
            return False

        # Switch main tab to editor view
        self.tabWidget.setCurrentWidget(self.splitDocs)

        # Try to open the project
        if not self.theProject.openProject(projFile):
            # The project open failed.

            if self.theProject.lockedBy is None:
                # The project is not locked, so failed for some other
                # reason handled by the project class.
                return False

            try:
                lockDetails = (
                    "<br><br>The project was locked by the computer "
                    "'%s' (%s %s), last active on %s"
                ) % (
                    self.theProject.lockedBy[0],
                    self.theProject.lockedBy[1],
                    self.theProject.lockedBy[2],
                    datetime.fromtimestamp(
                        int(self.theProject.lockedBy[3])
                    ).strftime("%x %X")
                )
            except Exception:
                lockDetails = ""

            msgBox = QMessageBox()
            msgRes = msgBox.warning(
                self, "Project Locked", (
                    "The project is already open by another instance of novelWriter, and "
                    "is therefore locked. Override lock and continue anyway?<br><br>"
                    "Note: If the program or the computer previously crashed, the lock "
                    "can safely be overridden. If, however, another instance of "
                    "novelWriter has the project open, overriding the lock may corrupt "
                    "the project, and is not recommended.%s"
                ) % lockDetails,
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if msgRes == QMessageBox.Yes:
                if not self.theProject.openProject(projFile, overrideLock=True):
                    return False
            else:
                return False

        # Project is loaded
        self.hasProject = True

        # Load the tag index
        self.theIndex.loadIndex()

        # Update GUI
        self._setWindowTitle(self.theProject.projName)
        self.rebuildTree()
        self.docEditor.setDictionaries()
        self.docEditor.setSpellCheck(self.theProject.spellCheck)
        self.mainMenu.setAutoOutline(self.theProject.autoOutline)
        self.statusBar.setRefTime(self.theProject.projOpened)

        # Restore previously open documents, if any
        if self.theProject.lastEdited is not None:
            self.openDocument(self.theProject.lastEdited, doScroll=True)
        if self.theProject.lastViewed is not None:
            self.viewDocument(self.theProject.lastViewed)

        # Check if we need to rebuild the index
        if self.theIndex.indexBroken:
            self.rebuildIndex()

        logger.debug("Project load complete")

        return True

    def saveProject(self, autoSave=False):
        """Save the current project.
        """
        if not self.hasProject:
            return False

        # If the project is new, it may not have a path, so we need one
        if self.theProject.projPath is None:
            projPath = self.selectProjectPath()
            self.theProject.setProjectPath(projPath)
        if self.theProject.projPath is None:
            return False

        self.treeView.saveTreeOrder()
        self.theProject.saveProject(autoSave)
        self.theIndex.saveIndex()

        return True

    ##
    #  Document Actions
    ##

    def closeDocument(self):
        """Close the document and clear the editor and title field.
        """
        if self.hasProject:
            self.docEditor.saveCursorPosition()
            if self.docEditor.docChanged:
                self.saveDocument()
            self.docEditor.clearEditor()
        return True

    def openDocument(self, tHandle, tLine=None, changeFocus=True, doScroll=False):
        """Open a specific document, optionally at a given line.
        """
        if self.hasProject:
            self.closeDocument()
            self.tabWidget.setCurrentWidget(self.splitDocs)
            if self.docEditor.loadText(tHandle, tLine):
                if changeFocus:
                    self.docEditor.setFocus()
                self.theProject.setLastEdited(tHandle)
                self.treeView.setSelectedHandle(tHandle, doScroll=doScroll)
            else:
                return False
        return True

    def openNextDocument(self, tHandle, wrapAround=False):
        """Opens the next document in the project tree, following the
        document with the given handle. Stops when reaching the end.
        """
        if self.hasProject:
            self.treeView.flushTreeOrder()
            nHandle = None  # The next handle after tHandle
            fHandle = None  # The first file handle we encounter
            foundIt = False # We've found tHandle, pick the next we see
            for tItem in self.theProject.projTree:
                if tItem is None:
                    continue
                if tItem.itemType != nwItemType.FILE:
                    continue
                if fHandle is None:
                    fHandle = tItem.itemHandle
                if tItem.itemHandle == tHandle:
                    foundIt = True
                elif foundIt:
                    nHandle = tItem.itemHandle
                    break

            if nHandle is not None:
                self.openDocument(nHandle, tLine=0, doScroll=True)
                return True
            elif wrapAround:
                self.openDocument(fHandle, tLine=0, doScroll=True)
                return False

        return False

    def saveDocument(self):
        """Save the current documents.
        """
        if self.hasProject:
            self.docEditor.saveText()
        return True

    def viewDocument(self, tHandle=None, tAnchor=None):
        """Load a document for viewing in the view panel.
        """
        if tHandle is None:
            logger.debug("Viewing document, but no handle provided")

            if self.docEditor.hasFocus():
                logger.verbose("Trying editor document")
                tHandle = self.docEditor.theHandle

            if tHandle is not None:
                self.saveDocument()
            else:
                logger.verbose("Trying selected document")
                tHandle = self.treeView.getSelectedHandle()

            if tHandle is None:
                logger.verbose("Trying last viewed document")
                tHandle = self.theProject.lastViewed

            if tHandle is None:
                logger.verbose("No document to view, giving up")
                return False

        # Make sure main tab is in Editor view
        self.tabWidget.setCurrentWidget(self.splitDocs)

        logger.debug("Viewing document with handle %s" % tHandle)
        if self.docViewer.loadText(tHandle):
            if not self.splitView.isVisible():
                bPos = self.splitMain.sizes()
                self.splitView.setVisible(True)
                vPos = [0, 0]
                vPos[0] = int(bPos[1]/2)
                vPos[1] = bPos[1] - vPos[0]
                self.splitDocs.setSizes(vPos)
                self.viewMeta.setVisible(self.mainConf.showRefPanel)
            self.docViewer.navigateTo(tAnchor)

        return True

    def importDocument(self):
        """Import the text contained in an out-of-project text file, and
        insert the text into the currently open document.
        """
        lastPath = self.mainConf.lastPath

        extFilter = [
            "Text files (*.txt)",
            "Markdown files (*.md)",
            "novelWriter files (*.nwd)",
            "All files (*.*)",
        ]
        dlgOpt  = QFileDialog.Options()
        dlgOpt |= QFileDialog.DontUseNativeDialog
        loadFile, _ = QFileDialog.getOpenFileName(
            self, "Import File", lastPath, options=dlgOpt, filter=";;".join(extFilter)
        )
        if not loadFile:
            return False

        if loadFile.strip() == "":
            return False

        theText = None
        try:
            with open(loadFile, mode="rt", encoding="utf8") as inFile:
                theText = inFile.read()
            self.mainConf.setLastPath(loadFile)
        except Exception as e:
            self.makeAlert(
                ["Could not read file. The file must be an existing text file.", str(e)],
                nwAlert.ERROR
            )
            return False

        if self.docEditor.theHandle is None:
            self.makeAlert(
                "Please open a document to import the text file into.",
                nwAlert.ERROR
            )
            return False

        if not self.docEditor.isEmpty():
            msgBox = QMessageBox()
            msgRes = msgBox.question(self, "Import Document", (
                "Importing the file will overwrite the current content of the document. "
                "Do you want to proceed?"
            ))
            if msgRes != QMessageBox.Yes:
                return False

        self.docEditor.replaceText(theText)

        return True

    def mergeDocuments(self):
        """Merge multiple documents to one single new document.
        """
        dlgMerge = GuiDocMerge(self, self.theProject)
        dlgMerge.exec_()
        return

    def splitDocument(self):
        """Split a single document into multiple documents.
        """
        dlgSplit = GuiDocSplit(self, self.theProject)
        dlgSplit.exec_()
        return

    def passDocumentAction(self, theAction):
        """Pass on document action theAction to the document viewer if
        it has focus, otherwise pass it to the document editor.
        """
        if self.docViewer.hasFocus():
            self.docViewer.docAction(theAction)
        else:
            self.docEditor.docAction(theAction)
        return True

    ##
    #  Tree Item Actions
    ##

    def openSelectedItem(self):
        """Open the selected documents.
        """
        tHandle = self.treeView.getSelectedHandle()
        if tHandle is None:
            logger.warning("No item selected")
            return False

        logger.verbose("Opening item %s" % tHandle)
        nwItem = self.theProject.projTree[tHandle]
        if nwItem.itemType == nwItemType.FILE:
            logger.verbose("Requested item %s is a file" % tHandle)
            self.openDocument(tHandle, doScroll=False)
        else:
            logger.verbose("Requested item %s is not a file" % tHandle)

        return True

    def editItem(self, tHandle=None):
        """Open the edit item dialog.
        """
        if tHandle is None:
            tHandle = self.treeView.getSelectedHandle()
        if tHandle is None:
            logger.warning("No item selected")
            return

        logger.verbose("Requesting change to item %s" % tHandle)
        dlgProj = GuiItemEditor(self, self.theProject, tHandle)
        dlgProj.exec_()
        if dlgProj.result() == QDialog.Accepted:
            self.treeView.setTreeItemValues(tHandle)
            self.treeMeta.updateViewBox(tHandle)
            self.docEditor.updateDocInfo(tHandle)
            self.docViewer.updateDocInfo(tHandle)

        return

    def rebuildTree(self):
        """Rebuild the project tree.
        """
        self._makeStatusIcons()
        self._makeImportIcons()
        self.treeView.clearTree()
        self.treeView.buildTree()
        return

    def rebuildIndex(self, beQuiet=False):
        """Rebuild the entire index.
        """
        if not self.hasProject:
            return False

        logger.debug("Rebuilding index ...")
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        tStart = time()

        self.treeView.saveTreeOrder()
        self.theIndex.clearIndex()

        theDoc = NWDoc(self.theProject, self)
        for nDone, tItem in enumerate(self.theProject.projTree):

            if tItem is not None:
                self.statusBar.setStatus("Indexing: '%s'" % tItem.itemName)
            else:
                self.statusBar.setStatus("Indexing: Unknown item")

            if tItem is not None and tItem.itemType == nwItemType.FILE:
                logger.verbose("Scanning: %s" % tItem.itemName)
                theText = theDoc.openDocument(tItem.itemHandle, showStatus=False)

                # Build tag index
                self.theIndex.scanText(tItem.itemHandle, theText)

                # Get Word Counts
                cC, wC, pC = self.theIndex.getCounts(tItem.itemHandle)
                tItem.setCharCount(cC)
                tItem.setWordCount(wC)
                tItem.setParaCount(pC)
                self.treeView.propagateCount(tItem.itemHandle, wC)
                self.treeView.projectWordCount()

        tEnd = time()
        self.statusBar.setStatus("Indexing completed in %.1f ms" % ((tEnd - tStart)*1000.0))
        self.docEditor.updateTagHighLighting()
        qApp.restoreOverrideCursor()

        if not beQuiet:
            self.makeAlert("The project index has been successfully rebuilt.", nwAlert.INFO)

        return True

    def rebuildOutline(self):
        """Force a rebuild of the Outline view.
        """
        logger.verbose("Forcing a rebuild of the Project Outline")
        self.tabWidget.setCurrentWidget(self.splitOutline)
        self.projView.refreshTree(overRide=True)
        return True

    ##
    #  Main Dialogs
    ##

    def selectProjectPath(self):
        """Select where to save project.
        """
        dlgOpt  = QFileDialog.Options()
        dlgOpt |= QFileDialog.ShowDirsOnly
        dlgOpt |= QFileDialog.DontUseNativeDialog
        projPath = QFileDialog.getExistingDirectory(
            self, "Save novelWriter Project", "", options=dlgOpt
        )
        if projPath:
            return projPath
        return None

    def showProjectLoadDialog(self):
        """Opens the projects dialog for selecting either existing
        projects from a cache of recently opened projects, or provide a
        browse button for projects not yet cached.
        """
        dlgProj = GuiProjectLoad(self)
        dlgProj.exec_()
        if dlgProj.result() == QDialog.Accepted:
            if dlgProj.openState == GuiProjectLoad.OPEN_STATE:
                self.openProject(dlgProj.openPath)
            elif dlgProj.openState == GuiProjectLoad.NEW_STATE:
                self.newProject()

        return True

    def showNewProjectDialog(self):
        """Open the wizard and assemble the project options dict.
        """
        newProj = GuiProjectWizard(self)
        newProj.exec_()

        if newProj.result() == QDialog.Accepted:
            return self._assembleProjectWizardData(newProj)

        return None

    def showPreferencesDialog(self):
        """Open the preferences dialog.
        """
        dlgConf = GuiPreferences(self, self.theProject)
        dlgConf.exec_()

        if dlgConf.result() == QDialog.Accepted:
            logger.debug("Applying new preferences")
            self.initMain()
            self.theTheme.updateTheme()
            self.saveDocument()
            self.docEditor.initEditor()
            self.docViewer.initViewer()

        return

    def showProjectSettingsDialog(self):
        """Open the project settings dialog.
        """
        if not self.hasProject:
            logger.error("No project open")
            return

        dlgProj = GuiProjectSettings(self, self.theProject)
        dlgProj.exec_()

        if dlgProj.result() == QDialog.Accepted:
            logger.debug("Applying new project settings")
            self.docEditor.setDictionaries()
            self._setWindowTitle(self.theProject.projName)

        return

    def showBuildProjectDialog(self):
        """Open the build project dialog.
        """
        if not self.hasProject:
            logger.error("No project open")
            return

        dlgBuild = getGuiItem("GuiBuildNovel")
        if dlgBuild is None:
            dlgBuild = GuiBuildNovel(self, self.theProject)

        dlgBuild.setModal(False)
        dlgBuild.show()
        qApp.processEvents()
        dlgBuild.viewCachedDoc()

        return

    def showWritingStatsDialog(self):
        """Open the session log dialog.
        """
        if not self.hasProject:
            logger.error("No project open")
            return

        dlgStats = getGuiItem("GuiWritingStats")
        if dlgStats is None:
            dlgStats = GuiWritingStats(self, self.theProject)

        dlgStats.setModal(False)
        dlgStats.show()
        qApp.processEvents()
        dlgStats.populateGUI()

        return

    def showAboutNWDialog(self):
        """Show the about dialog for novelWriter.
        """
        dlgAbout = GuiAbout(self)
        dlgAbout.exec_()
        return

    def showAboutQtDialog(self):
        """Show the about dialog for Qt.
        """
        msgBox = QMessageBox()
        msgBox.aboutQt(self, "About Qt")
        return

    def makeAlert(self, theMessage, theLevel=nwAlert.INFO):
        """Alert both the user and the logger at the same time. Message
        can be either a string or an array of strings. Severity level is
        0 = info, 1 = warning, and 2 = error.
        """
        if isinstance(theMessage, list):
            popMsg = "<br>".join(theMessage)
            logMsg = theMessage
        else:
            popMsg = theMessage
            logMsg = [theMessage]

        # Write to Log
        if theLevel == nwAlert.INFO:
            for msgLine in logMsg:
                logger.info(msgLine)
        elif theLevel == nwAlert.WARN:
            for msgLine in logMsg:
                logger.warning(msgLine)
        elif theLevel == nwAlert.ERROR:
            for msgLine in logMsg:
                logger.error(msgLine)
        elif theLevel == nwAlert.BUG:
            for msgLine in logMsg:
                logger.error(msgLine)

        # Popup
        if self.mainConf.showGUI:
            msgBox = QMessageBox()
            if theLevel == nwAlert.INFO:
                msgBox.information(self, "Information", popMsg)
            elif theLevel == nwAlert.WARN:
                msgBox.warning(self, "Warning", popMsg)
            elif theLevel == nwAlert.ERROR:
                msgBox.critical(self, "Error", popMsg)
            elif theLevel == nwAlert.BUG:
                popMsg += "<br>This is a bug!"
                msgBox.critical(self, "Internal Error", popMsg)

        return

    def reportConfErr(self):
        """Checks if the Config module has any errors to report, and let
        the user know if this is the case. The Config module caches
        errors since it is initialised before the GUI itself.
        """
        if self.mainConf.hasError:
            self.makeAlert(self.mainConf.getErrData(), nwAlert.ERROR)
            return True
        return False

    ##
    #  Main Window Actions
    ##

    def closeMain(self):
        """Save everything, and close novelWriter.
        """
        if self.hasProject:
            msgBox = QMessageBox()
            msgRes = msgBox.question(
                self, "Exit", "Do you want to save changes and exit?"
            )
            if msgRes != QMessageBox.Yes:
                return False

        logger.info("Exiting novelWriter")

        if not self.isFocusMode:
            self.mainConf.setMainPanePos(self.splitMain.sizes())
            self.mainConf.setDocPanePos(self.splitDocs.sizes())
            self.mainConf.setOutlinePanePos(self.splitOutline.sizes())
            if self.viewMeta.isVisible():
                self.mainConf.setViewPanePos(self.splitView.sizes())

        self.mainConf.setShowRefPanel(self.viewMeta.isVisible())
        self.mainConf.setTreeColWidths(self.treeView.getColumnSizes())
        if not self.mainConf.isFullScreen:
            self.mainConf.setWinSize(self.width(), self.height())

        if self.hasProject:
            self.closeProject(True)

        self.mainConf.saveConfig()
        self.reportConfErr()
        self.mainMenu.closeHelp()

        qApp.quit()

        return True

    def setFocus(self, paneNo):
        """Switch focus to one of the three main gUi panes.
        """
        if paneNo == 1:
            self.treeView.setFocus()
        elif paneNo == 2:
            self.docEditor.setFocus()
        elif paneNo == 3:
            self.docViewer.setFocus()
        return

    def closeDocEditor(self):
        """Close the document edit panel. This does not hide the editor.
        """
        self.closeDocument()
        self.theProject.setLastEdited(None)
        return

    def closeDocViewer(self):
        """Close the document view panel.
        """
        self.docViewer.clearViewer()
        self.theProject.setLastViewed(None)
        bPos = self.splitMain.sizes()
        self.splitView.setVisible(False)
        vPos = [bPos[1], 0]
        self.splitDocs.setSizes(vPos)
        return not self.splitView.isVisible()

    def toggleFocusMode(self):
        """Main GUI Focus Mode hides tree, view pane and optionally also
        statusbar and menu.
        """
        if self.docEditor.theHandle is None:
            logger.error("No document open, so not activating Focus Mode")
            return False

        self.isFocusMode = not self.isFocusMode
        if self.isFocusMode:
            logger.debug("Activating Focus mode")
            self.tabWidget.setCurrentWidget(self.splitDocs)
        else:
            logger.debug("Deactivating Focus mode")

        isVisible = not self.isFocusMode
        self.treePane.setVisible(isVisible)
        self.statusBar.setVisible(isVisible)
        self.mainMenu.setVisible(isVisible)
        self.tabWidget.tabBar().setVisible(isVisible)

        hideDocFooter = self.isFocusMode and self.mainConf.hideFocusFooter
        self.docEditor.docFooter.setVisible(not hideDocFooter)

        if self.splitView.isVisible():
            self.splitView.setVisible(False)
        elif self.docViewer.theHandle is not None:
            self.splitView.setVisible(True)

        return True

    def toggleFullScreenMode(self):
        """Main GUI full screen mode. The mode is tracked by the flag
        in config. This only tracks whether the window has been
        maximised using the internal commands, and may not be correct
        if the user uses the system window manager. Currently, Qt
        doesn't have access to the exact state of the window.
        """
        self.setWindowState(self.windowState() ^ Qt.WindowFullScreen)

        winState = self.windowState() & Qt.WindowFullScreen == Qt.WindowFullScreen
        if winState:
            logger.debug("Activated full screen mode")
        else:
            logger.debug("Deactivated full screen mode")

        self.mainConf.isFullScreen = winState

        return

    ##
    #  Internal Functions
    ##

    def _connectMenuActions(self):
        """Connect to the main window all menu actions that need to be
        available also when the main menu is hidden.
        """
        # Project
        self.addAction(self.mainMenu.aSaveProject)
        self.addAction(self.mainMenu.aExitNW)

        # Document
        self.addAction(self.mainMenu.aSaveDoc)
        self.addAction(self.mainMenu.aFileDetails)

        # Edit
        self.addAction(self.mainMenu.aEditUndo)
        self.addAction(self.mainMenu.aEditRedo)
        self.addAction(self.mainMenu.aEditCut)
        self.addAction(self.mainMenu.aEditCopy)
        self.addAction(self.mainMenu.aEditPaste)
        self.addAction(self.mainMenu.aSelectAll)
        self.addAction(self.mainMenu.aSelectPar)

        # View
        self.addAction(self.mainMenu.aFocusMode)
        self.addAction(self.mainMenu.aFullScreen)

        # Insert
        self.addAction(self.mainMenu.aInsENDash)
        self.addAction(self.mainMenu.aInsEMDash)
        self.addAction(self.mainMenu.aInsEllipsis)
        self.addAction(self.mainMenu.aInsQuoteLS)
        self.addAction(self.mainMenu.aInsQuoteRS)
        self.addAction(self.mainMenu.aInsQuoteLD)
        self.addAction(self.mainMenu.aInsQuoteRD)
        self.addAction(self.mainMenu.aInsMSApos)
        self.addAction(self.mainMenu.aInsHardBreak)
        self.addAction(self.mainMenu.aInsNBSpace)
        self.addAction(self.mainMenu.aInsThinSpace)
        self.addAction(self.mainMenu.aInsThinNBSpace)

        # Format
        self.addAction(self.mainMenu.aFmtEmph)
        self.addAction(self.mainMenu.aFmtStrong)
        self.addAction(self.mainMenu.aFmtStrike)
        self.addAction(self.mainMenu.aFmtDQuote)
        self.addAction(self.mainMenu.aFmtSQuote)
        self.addAction(self.mainMenu.aFmtHead1)
        self.addAction(self.mainMenu.aFmtHead2)
        self.addAction(self.mainMenu.aFmtHead3)
        self.addAction(self.mainMenu.aFmtHead4)
        self.addAction(self.mainMenu.aFmtComment)
        self.addAction(self.mainMenu.aFmtNoFormat)

        # Tools
        self.addAction(self.mainMenu.aSpellCheck)
        self.addAction(self.mainMenu.aReRunSpell)
        self.addAction(self.mainMenu.aPreferences)

        # Help
        if self.mainConf.hasHelp and self.mainConf.hasAssistant:
            self.addAction(self.mainMenu.aHelpLoc)
        self.addAction(self.mainMenu.aHelpWeb)

        return True

    def _setWindowTitle(self, projName=None):
        """Set the window title and add the project's working title.
        """
        winTitle = self.mainConf.appName
        if projName is not None:
            winTitle += " - %s" % projName
        self.setWindowTitle(winTitle)
        return True

    def _autoSaveProject(self):
        """Triggered by the auto-save project timer to save the project.
        """
        doSave  = self.hasProject
        doSave &= self.theProject.projChanged
        doSave &= self.theProject.projPath is not None

        if doSave:
            logger.debug("Autosaving project")
            self.saveProject(autoSave=True)

        return

    def _autoSaveDocument(self):
        """Triggered by the auto-save document timer to save the
        document.
        """
        if self.hasProject and self.docEditor.docChanged:
            logger.debug("Autosaving document")
            self.saveDocument()
        return

    def _makeStatusIcons(self):
        """Generate all the item status icons based on project settings.
        """
        self.statusIcons = {}
        iPx = self.mainConf.pxInt(32)
        for sLabel, sCol, _ in self.theProject.statusItems:
            theIcon = QPixmap(iPx, iPx)
            theIcon.fill(QColor(*sCol))
            self.statusIcons[sLabel] = QIcon(theIcon)
        return

    def _makeImportIcons(self):
        """Generate all the item importance icons based on project
        settings.
        """
        self.importIcons = {}
        iPx = self.mainConf.pxInt(32)
        for sLabel, sCol, _ in self.theProject.importItems:
            theIcon = QPixmap(iPx, iPx)
            theIcon.fill(QColor(*sCol))
            self.importIcons[sLabel] = QIcon(theIcon)
        return

    def _assembleProjectWizardData(self, newProj):
        """Extract the user choices from the New Project Wizard and
        store them in a dictionary.
        """
        projData = {
            "projName": newProj.field("projName"),
            "projTitle": newProj.field("projTitle"),
            "projAuthors": newProj.field("projAuthors"),
            "projPath": newProj.field("projPath"),
            "popSample": newProj.field("popSample"),
            "popMinimal": newProj.field("popMinimal"),
            "popCustom": newProj.field("popCustom"),
            "addRoots": [],
            "numChapters": 0,
            "numScenes": 0,
            "chFolders": False,
        }
        if newProj.field("popCustom"):
            addRoots = []
            if newProj.field("addPlot"):
                addRoots.append(nwItemClass.PLOT)
            if newProj.field("addChar"):
                addRoots.append(nwItemClass.CHARACTER)
            if newProj.field("addWorld"):
                addRoots.append(nwItemClass.WORLD)
            if newProj.field("addTime"):
                addRoots.append(nwItemClass.TIMELINE)
            if newProj.field("addObject"):
                addRoots.append(nwItemClass.OBJECT)
            if newProj.field("addEntity"):
                addRoots.append(nwItemClass.ENTITY)
            projData["addRoots"] = addRoots
            projData["numChapters"] = newProj.field("numChapters")
            projData["numScenes"] = newProj.field("numScenes")
            projData["chFolders"] = newProj.field("chFolders")

        return projData

    ##
    #  Events
    ##

    def closeEvent(self, theEvent):
        """Capture the closing event of the GUI and call the close
        function to handle all the close process steps.
        """
        if self.closeMain():
            theEvent.accept()
        else:
            theEvent.ignore()
        return

    ##
    #  Signal Handlers
    ##

    def _treeSingleClick(self):
        """Single click on a project tree item just updates the details
        panel below the tree.
        """
        sHandle = self.treeView.getSelectedHandle()
        if sHandle is not None:
            self.treeMeta.updateViewBox(sHandle)
        return

    def _treeDoubleClick(self, tItem, colNo):
        """The user double-clicked an item in the tree. If it is a file,
        we open it. Otherwise, we do nothing.
        """
        tHandle = tItem.data(self.treeView.C_NAME, Qt.UserRole)
        logger.verbose("User double clicked tree item with handle %s" % tHandle)
        nwItem = self.theProject.projTree[tHandle]
        if nwItem is not None:
            if nwItem.itemType == nwItemType.FILE:
                logger.verbose("Requested item %s is a file" % tHandle)
                self.openDocument(tHandle, changeFocus=False, doScroll=False)
            else:
                logger.verbose("Requested item %s is a folder" % tHandle)
        return

    def _treeKeyPressReturn(self):
        """The user pressed return an item in the tree. If it is a file,
        we open it. Otherwise, we do nothing. Pressing return does not
        change focus to the editor as double click does.
        """
        tHandle = self.treeView.getSelectedHandle()
        logger.verbose("User pressed return on tree item with handle %s" % tHandle)
        nwItem = self.theProject.projTree[tHandle]
        if nwItem is not None:
            if nwItem.itemType == nwItemType.FILE:
                logger.verbose("Requested item %s is a file" % tHandle)
                self.openDocument(tHandle, changeFocus=False, doScroll=False)
            else:
                logger.verbose("Requested item %s is a folder" % tHandle)
        return

    def _keyPressEscape(self):
        """When the escape key is pressed somewhere in the main window,
        do the following, in order:
        """
        if self.docEditor.docSearch.isVisible():
            self.docEditor.closeSearch()
            return
        elif self.isFocusMode:
            self.toggleFocusMode()
        return

    def _mainTabChanged(self, tabIndex):
        """Activated when the main window tab is changed.
        """
        if tabIndex == self.idxTabEdit:
            logger.verbose("Editor tab activated")
        elif tabIndex == self.idxTabProj:
            logger.verbose("Project outline tab activated")
            if self.hasProject:
                self.projView.refreshTree()
        return

# END Class GuiMain
