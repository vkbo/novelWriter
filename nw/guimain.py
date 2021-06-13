# -*- coding: utf-8 -*-
"""
novelWriter – GUI Main Window
=============================
The main application window

File History:
Created: 2018-09-22 [0.0.1]

This file is a part of novelWriter
Copyright 2018–2021, Veronica Berglyd Olsen

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

from PyQt5.QtCore import Qt, QTimer, QSize, QThreadPool, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap, QColor, QKeySequence, QCursor
from PyQt5.QtWidgets import (
    qApp, QMainWindow, QVBoxLayout, QWidget, QSplitter, QFileDialog, QShortcut,
    QMessageBox, QDialog, QTabWidget, QToolBar, QAction
)

from nw.gui import (
    GuiDocEditor, GuiDocViewDetails, GuiDocViewer, GuiItemDetails, GuiMainMenu,
    GuiMainStatus, GuiNovelTree, GuiOutline, GuiOutlineDetails,
    GuiProjectDetails, GuiProjectTree, GuiTheme
)
from nw.dialogs import (
    GuiAbout, GuiDocMerge, GuiDocSplit, GuiItemEditor, GuiPreferences,
    GuiProjectLoad, GuiProjectSettings, GuiWordList
)
from nw.tools import GuiBuildNovel, GuiProjectWizard, GuiWritingStats
from nw.core import NWProject, NWIndex
from nw.enum import nwItemType, nwItemClass, nwAlert, nwWidget, nwState
from nw.common import getGuiItem, hexToInt
from nw.constants import nwLists

logger = logging.getLogger(__name__)

class GuiMain(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        logger.debug("Initialising GUI ...")
        self.setObjectName("GuiMain")
        self.mainConf = nw.CONFIG
        self.threadPool = QThreadPool()

        # System Info
        # ===========

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
        logger.info("GUI Language: %s" % self.mainConf.guiLang)

        # Core Classes
        # ============

        # Core Classes and Settings
        self.theTheme    = GuiTheme(self)
        self.theProject  = NWProject(self)
        self.theIndex    = NWIndex(self.theProject)
        self.hasProject  = False
        self.isFocusMode = False
        self.idleRefTime = time()
        self.idleTime    = 0.0

        # Prepare Main Window
        self.resize(*self.mainConf.getWinSize())
        self._updateWindowTitle()
        self.setWindowIcon(QIcon(self.mainConf.appIcon))

        # Build the GUI
        # =============

        # Sizes
        mPx = self.mainConf.pxInt(4)
        fPx = self.theTheme.fontPixelSize
        fPt = self.theTheme.fontPointSize

        # Main GUI Elements
        self.statusBar = GuiMainStatus(self)
        self.treeView  = GuiProjectTree(self)
        self.novelView = GuiNovelTree(self)
        self.docEditor = GuiDocEditor(self)
        self.viewMeta  = GuiDocViewDetails(self)
        self.docViewer = GuiDocViewer(self)
        self.treeMeta  = GuiItemDetails(self)
        self.projView  = GuiOutline(self)
        self.projMeta  = GuiOutlineDetails(self)
        self.mainMenu  = GuiMainMenu(self)

        # Connect Signals Between Main Elements
        self.docEditor.spellDictionaryChanged.connect(self.statusBar.setLanguage)
        self.docEditor.docEditedStatusChanged.connect(self.statusBar.doUpdateDocumentStatus)
        self.docEditor.docCountsChanged.connect(self.treeMeta.doUpdateCounts)
        self.docEditor.docCountsChanged.connect(self.treeView.doUpdateCounts)

        self.treeView.itemSelectionChanged.connect(self._treeSingleClick)
        self.treeView.itemDoubleClicked.connect(self._treeDoubleClick)
        self.treeView.novelItemChanged.connect(self._treeNovelItemChanged)
        self.treeView.projectWordCountChanged.connect(self.statusBar.doUpdateProjectStats)

        # Minor GUI Elements
        self.statusIcons = []
        self.importIcons = []

        # Project Tree Tabs
        self.projTabs = QTabWidget()
        self.projTabs.setTabPosition(QTabWidget.South)
        self.projTabs.setStyleSheet(r"QTabWidget::pane {border: 0;};")
        self.projTabs.addTab(self.treeView, self.tr("Project"))
        self.projTabs.addTab(self.novelView, self.tr("Novel"))
        self.projTabs.currentChanged.connect(self._projTabsChanged)

        tabFont = self.projTabs.tabBar().font()
        tabFont.setPointSizeF(0.9*fPt)
        self.projTabs.tabBar().setFont(tabFont)

        # Project Tree Action Buttons
        btnSize = int(round(0.7*fPx))
        self.treeButtons = QToolBar()
        self.treeButtons.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.treeButtons.setIconSize(QSize(btnSize, btnSize))
        self.treeButtons.setContentsMargins(0, 0, 0, 0)
        self.treeButtons.setStyleSheet(r"QToolBar {padding: 0;}")
        self.projTabs.setCornerWidget(self.treeButtons, Qt.BottomRightCorner)

        self.projDetailsBtn = QAction(self.tr("Project Details"))
        self.projDetailsBtn.setIcon(self.theTheme.getIcon("status_lines"))
        self.projDetailsBtn.triggered.connect(lambda: self.showProjectDetailsDialog())
        self.treeButtons.addAction(self.projDetailsBtn)

        self.projStatsBtn = QAction(self.tr("Writing Statistics"))
        self.projStatsBtn.setIcon(self.theTheme.getIcon("status_stats"))
        self.projStatsBtn.triggered.connect(lambda: self.showWritingStatsDialog())
        self.treeButtons.addAction(self.projStatsBtn)

        self.projSettingsBtn = QAction(self.tr("Project Settings"))
        self.projSettingsBtn.setIcon(self.theTheme.getIcon("settings"))
        self.projSettingsBtn.triggered.connect(lambda: self.showProjectSettingsDialog())
        self.treeButtons.addAction(self.projSettingsBtn)

        # Project Tree View
        self.treePane = QWidget()
        self.treeBox = QVBoxLayout()
        self.treeBox.setContentsMargins(0, 0, 0, 0)
        self.treeBox.setSpacing(mPx)
        self.treeBox.addWidget(self.projTabs)
        self.treeBox.addWidget(self.treeMeta)
        self.treePane.setLayout(self.treeBox)

        # Splitter : Document Viewer / Document Meta
        self.splitView = QSplitter(Qt.Vertical)
        self.splitView.addWidget(self.docViewer)
        self.splitView.addWidget(self.viewMeta)
        self.splitView.setSizes(self.mainConf.getViewPanePos())

        # Splitter : Document Editor / Document Viewer
        self.splitDocs = QSplitter(Qt.Horizontal)
        self.splitDocs.addWidget(self.docEditor)
        self.splitDocs.addWidget(self.splitView)

        # Splitter : Project Outlie / Outline Details
        self.splitOutline = QSplitter(Qt.Vertical)
        self.splitOutline.addWidget(self.projView)
        self.splitOutline.addWidget(self.projMeta)
        self.splitOutline.setSizes(self.mainConf.getOutlinePanePos())

        # Main Tabs : Editor / Outline
        self.mainTabs = QTabWidget()
        self.mainTabs.setTabPosition(QTabWidget.East)
        self.mainTabs.setStyleSheet(r"QTabWidget::pane {border: 0;}")
        self.mainTabs.addTab(self.splitDocs, self.tr("Editor"))
        self.mainTabs.addTab(self.splitOutline, self.tr("Outline"))
        self.mainTabs.currentChanged.connect(self._mainTabChanged)

        # Splitter : Project Tree / Main Tabs
        self.splitMain = QSplitter(Qt.Horizontal)
        self.splitMain.setContentsMargins(mPx, mPx, mPx, mPx)
        self.splitMain.addWidget(self.treePane)
        self.splitMain.addWidget(self.mainTabs)
        self.splitMain.setSizes(self.mainConf.getMainPanePos())

        # Indices of Splitter Widgets
        self.idxTree     = self.splitMain.indexOf(self.treePane)
        self.idxMain     = self.splitMain.indexOf(self.mainTabs)
        self.idxEditor   = self.splitDocs.indexOf(self.docEditor)
        self.idxViewer   = self.splitDocs.indexOf(self.splitView)
        self.idxViewDoc  = self.splitView.indexOf(self.docViewer)
        self.idxViewMeta = self.splitView.indexOf(self.viewMeta)

        # Indices of Tab Widgets
        self.idxTabEdit   = self.mainTabs.indexOf(self.splitDocs)
        self.idxTabProj   = self.mainTabs.indexOf(self.splitOutline)
        self.idxTreeView  = self.projTabs.indexOf(self.treeView)
        self.idxNovelView = self.projTabs.indexOf(self.novelView)

        # Splitter Behaviour
        self.splitMain.setCollapsible(self.idxTree, False)
        self.splitMain.setCollapsible(self.idxMain, False)
        self.splitDocs.setCollapsible(self.idxEditor, False)
        self.splitDocs.setCollapsible(self.idxViewer, True)
        self.splitView.setCollapsible(self.idxViewDoc, False)
        self.splitView.setCollapsible(self.idxViewMeta, False)

        # Editor / Viewer Default State
        self.splitView.setVisible(False)
        self.docEditor.closeSearch()

        # Initialise the Project Tree
        self.rebuildTrees()

        # Set Main Window Elements
        self.setMenuBar(self.mainMenu)
        self.setCentralWidget(self.splitMain)
        self.setStatusBar(self.statusBar)

        # Finalise Initialisation
        # =======================

        # Set Up Auto-Save Project Timer
        self.asProjTimer = QTimer()
        self.asProjTimer.timeout.connect(self._autoSaveProject)

        # Set Up Auto-Save Document Timer
        self.asDocTimer = QTimer()
        self.asDocTimer.timeout.connect(self._autoSaveDocument)

        # Main Clock
        self.mainTimer = QTimer()
        self.mainTimer.setInterval(1000)
        self.mainTimer.timeout.connect(self._timeTick)
        self.mainTimer.start()

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

        # Force a show of the GUI
        self.show()

        # Check that config loaded fine
        self.reportConfErr()

        # Initialise Main GUI
        self.initMain()
        self.asProjTimer.start()
        self.asDocTimer.start()
        self.statusBar.clearStatus()

        # Handle Windows Mode
        self.showNormal()
        if self.mainConf.isFullScreen:
            self.toggleFullScreenMode()

        logger.debug("GUI initialisation complete")

        # If a project path was provided at command line, open it
        if self.mainConf.cmdOpen is not None:
            logger.debug("Opening project from additional command line option")
            self.openProject(self.mainConf.cmdOpen)

        logger.debug("novelWriter is ready ...")
        self.setStatus(self.tr("novelWriter is ready ..."))

        return

    def clearGUI(self):
        """Wrapper function to clear all sub-elements of the main GUI.
        """
        # Project Area
        self.treeView.clearTree()
        self.novelView.clearTree()
        self.treeMeta.clearDetails()

        # Work Area
        self.docEditor.clearEditor()
        self.docEditor.setDictionaries()
        self.closeDocViewer()
        self.projMeta.clearDetails()

        # General
        self.statusBar.clearStatus()
        self._updateWindowTitle()

        return True

    def initMain(self):
        """Initialise elements that depend on user settings.
        """
        self.asProjTimer.setInterval(int(self.mainConf.autoSaveProj*1000))
        self.asDocTimer.setInterval(int(self.mainConf.autoSaveDoc*1000))
        return True

    def releaseNotes(self):
        """Determine whether release notes need to be shown, and show
        them by calling the About dialog.
        """
        if hexToInt(self.mainConf.lastNotes) < hexToInt(nw.__hexversion__):
            self.mainConf.lastNotes = nw.__hexversion__
            self.showAboutNWDialog(showNotes=True)
        return

    ##
    #  Project Actions
    ##

    def newProject(self, projData=None):
        """Create new project via the new project wizard.
        """
        if self.hasProject:
            if not self.closeProject():
                self.makeAlert(self.tr(
                    "Cannot create new project when another project is open."
                ), nwAlert.ERROR)
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
            self.makeAlert(self.tr(
                "A project already exists in that location. "
                "Please choose another folder."
            ), nwAlert.ERROR)
            return False

        logger.info("Creating new project")
        if self.theProject.newProject(projData):
            self.hasProject = True
            self.rebuildTrees()
            self.saveProject()
            self.docEditor.setDictionaries()
            self.rebuildIndex(beQuiet=True)
            self.statusBar.setRefTime(self.theProject.projOpened)
            self.statusBar.setProjectStatus(nwState.GOOD)
            self.statusBar.setDocumentStatus(nwState.NONE)
            self.statusBar.setStatus(self.tr("New project created ..."))
            self._updateWindowTitle(self.theProject.projName)
        else:
            self.theProject.clearProject()
            return False

        return True

    def closeProject(self, isYes=False):
        """Closes the project if one is open. isYes is passed on from
        the close application event so the user doesn't get prompted
        twice to confirm.
        """
        if not self.hasProject:
            # There is no project loaded, everything OK
            return True

        if not isYes:
            msgYes = self.askQuestion(
                self.tr("Close Project"),
                "%s<br>%s" % (
                    self.tr("Close the current project?"),
                    self.tr("Changes are saved automatically.")
                )
            )
            if not msgYes:
                return False

        if self.docEditor.docChanged():
            self.saveDocument()

        if self.theProject.projAltered:
            saveOK   = self.saveProject()
            doBackup = False
            if self.theProject.doBackup and self.mainConf.backupOnClose:
                doBackup = True
                if self.mainConf.askBeforeBackup:
                    msgYes = self.askQuestion(
                        self.tr("Backup Project"),
                        self.tr("Backup the current project?")
                    )
                    if not msgYes:
                        doBackup = False
            if doBackup:
                self.theProject.zipIt(False)
        else:
            saveOK = True

        if saveOK:
            self.closeDocument()
            self.docViewer.clearNavHistory()
            self.projView.closeOutline()

            self.theProject.closeProject(self.idleTime)
            self.idleRefTime = time()
            self.idleTime    = 0.0

            self.theIndex.clearIndex()
            self.clearGUI()
            self.hasProject = False
            self.mainTabs.setCurrentWidget(self.splitDocs)

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
        self.mainTabs.setCurrentWidget(self.splitDocs)

        # Try to open the project
        if not self.theProject.openProject(projFile):
            # The project open failed.

            if self.theProject.lockedBy is None:
                # The project is not locked, so failed for some other
                # reason handled by the project class.
                return False

            try:
                lockDetails = (
                    "<br>%s" % self.tr(
                        "The project was locked by the computer "
                        "'{0}' ({1} {2}), last active on {3}."
                    )
                ).format(
                    self.theProject.lockedBy[0],
                    self.theProject.lockedBy[1],
                    self.theProject.lockedBy[2],
                    datetime.fromtimestamp(int(self.theProject.lockedBy[3])).strftime("%x %X")
                )
            except Exception:
                lockDetails = ""

            msgBox = QMessageBox()
            msgRes = msgBox.warning(
                self, self.tr("Project Locked"),
                "%s<br><br>%s<br>%s" % (
                    self.tr(
                        "The project is already open by another instance of novelWriter, and "
                        "is therefore locked. Override lock and continue anyway?"
                    ),
                    self.tr(
                        "Note: If the program or the computer previously crashed, the lock "
                        "can safely be overridden. If, however, another instance of "
                        "novelWriter has the project open, overriding the lock may corrupt "
                        "the project, and is not recommended."
                    ),
                    lockDetails
                ),
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if msgRes == QMessageBox.Yes:
                if not self.theProject.openProject(projFile, overrideLock=True):
                    return False
            else:
                return False

        # Project is loaded
        self.hasProject  = True
        self.idleRefTime = time()
        self.idleTime    = 0.0

        # Load the tag index
        self.theIndex.loadIndex()

        # Update GUI
        self._updateWindowTitle(self.theProject.projName)
        self.rebuildTrees()
        self.docEditor.setDictionaries()
        self.docEditor.setSpellCheck(self.theProject.spellCheck)
        self.mainMenu.setAutoOutline(self.theProject.autoOutline)
        self.statusBar.setRefTime(self.theProject.projOpened)
        self.statusBar.doUpdateProjectStats(self.theProject.currWCount, 0)

        # Restore previously open documents, if any
        if self.theProject.lastEdited is not None:
            self.openDocument(self.theProject.lastEdited, doScroll=True)

        if self.theProject.lastViewed is not None:
            self.viewDocument(self.theProject.lastViewed)

        # Check if we need to rebuild the index
        if self.theIndex.indexBroken:
            self.makeAlert(self.tr(
                "The project index is outdated or broken. Rebuilding index."
            ), nwAlert.WARN)
            self.rebuildIndex()

        # Make sure the changed status is set to false on all that was
        # just opened
        qApp.processEvents()
        self.docEditor.setDocumentChanged(False)
        self.theProject.setProjectChanged(False)

        logger.debug("Project load complete")

        return True

    def saveProject(self, autoSave=False):
        """Save the current project.
        """
        if not self.hasProject:
            logger.error("No project open")
            return False

        self.treeView.saveTreeOrder()
        if self.theProject.saveProject(autoSave=autoSave):
            self.theIndex.saveIndex()

        return True

    ##
    #  Document Actions
    ##

    def closeDocument(self):
        """Close the document and clear the editor and title field.
        """
        if not self.hasProject:
            logger.error("No project open")
            return False

        # Disable focus mode if it is active
        if self.isFocusMode:
            self.toggleFocusMode()

        self.docEditor.saveCursorPosition()
        if self.docEditor.docChanged():
            self.saveDocument()
        self.docEditor.clearEditor()

        return True

    def openDocument(self, tHandle, tLine=None, changeFocus=True, doScroll=False):
        """Open a specific document, optionally at a given line.
        """
        if not self.hasProject:
            logger.error("No project open")
            return False

        self.closeDocument()
        self.mainTabs.setCurrentWidget(self.splitDocs)
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
        if not self.hasProject:
            logger.error("No project open")
            return False

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
        if not self.hasProject:
            logger.error("No project open")
            return False

        self.docEditor.saveText()

        return True

    def viewDocument(self, tHandle=None, tAnchor=None):
        """Load a document for viewing in the view panel.
        """
        if not self.hasProject:
            logger.error("No project open")
            return False

        if tHandle is None:
            logger.debug("Viewing document, but no handle provided")

            if self.docEditor.hasFocus():
                logger.verbose("Trying editor document")
                tHandle = self.docEditor.docHandle()

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
        self.mainTabs.setCurrentWidget(self.splitDocs)

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
        if not self.hasProject:
            logger.error("No project open")
            return False

        lastPath = self.mainConf.lastPath
        extFilter = [
            self.tr("Text files ({0})").format("*.txt"),
            self.tr("Markdown files ({0})").format("*.md"),
            self.tr("novelWriter files ({0})").format("*.nwd"),
            self.tr("All files ({0})").format("*"),
        ]
        loadFile, _ = QFileDialog.getOpenFileName(
            self, self.tr("Import File"), lastPath, filter=";;".join(extFilter)
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
            self.makeAlert([
                self.tr("Could not read file. The file must be an existing text file."), str(e)
            ], nwAlert.ERROR)
            return False

        if self.docEditor.docHandle() is None:
            self.makeAlert(self.tr(
                "Please open a document to import the text file into."
            ), nwAlert.ERROR)
            return False

        if not self.docEditor.isEmpty():
            msgYes = self.askQuestion(
                self.tr("Import Document"),
                self.tr(
                    "Importing the file will overwrite the current content of the document. "
                    "Do you want to proceed?"
                )
            )
            if not msgYes:
                return False

        self.docEditor.replaceText(theText)

        return True

    def mergeDocuments(self):
        """Merge multiple documents to one single new document.
        """
        if not self.hasProject:
            logger.error("No project open")
            return False

        dlgMerge = GuiDocMerge(self)
        dlgMerge.exec_()

        return True

    def splitDocument(self):
        """Split a single document into multiple documents.
        """
        if not self.hasProject:
            logger.error("No project open")
            return False

        dlgSplit = GuiDocSplit(self)
        dlgSplit.exec_()

        return True

    def passDocumentAction(self, theAction):
        """Pass on document action to the document viewer if it has
        focus, or pass it to the document editor if it or any of
        its clid widgets have focus. If neither has focus, ignore the
        action.
        """
        if self.docViewer.hasFocus():
            self.docViewer.docAction(theAction)
        elif self.docEditor.hasFocus():
            self.docEditor.docAction(theAction)
        else:
            logger.debug("Action cancelled as neither editor nor viewer has focus")
        return

    ##
    #  Tree Item Actions
    ##

    def openSelectedItem(self):
        """Open the selected documents.
        """
        if not self.hasProject:
            logger.error("No project open")
            return False

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
        if not self.hasProject:
            logger.error("No project open")
            return False

        if tHandle is None:
            if self.docEditor.anyFocus() or self.isFocusMode:
                tHandle = self.docEditor.docHandle()
            else:
                tHandle = self.treeView.getSelectedHandle()

        if tHandle is None:
            logger.warning("No item selected")
            return

        tItem = self.theProject.projTree[tHandle]
        if tItem is None:
            return
        if tItem.itemType not in nwLists.REG_TYPES:
            return

        logger.verbose("Requesting change to item %s" % tHandle)
        dlgProj = GuiItemEditor(self, tHandle)
        dlgProj.exec_()
        if dlgProj.result() == QDialog.Accepted:
            self.treeView.setTreeItemValues(tHandle)
            self.treeMeta.updateViewBox(tHandle)
            self.docEditor.updateDocInfo(tHandle)
            self.docViewer.updateDocInfo(tHandle)

        return

    def rebuildTrees(self):
        """Rebuild the project tree.
        """
        self._makeStatusIcons()
        self._makeImportIcons()
        self.treeView.buildTree()
        self.novelView.refreshTree()
        return

    def requestNovelTreeRefresh(self):
        """Update the novel tree, but only if it is visible.
        """
        if self.projTabs.currentIndex() == self.idxNovelView and self.hasProject:
            self.novelView.refreshTree()
            return True
        return False

    def rebuildIndex(self, beQuiet=False):
        """Rebuild the entire index.
        """
        if not self.hasProject:
            logger.error("No project open")
            return False

        logger.debug("Rebuilding index ...")
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        tStart = time()

        self.treeView.saveTreeOrder()
        self.theIndex.clearIndex()

        for tItem in self.theProject.projTree:

            if tItem is not None:
                self.setStatus(self.tr("Indexing: '{0}'").format(tItem.itemName))
            else:
                self.setStatus(self.tr("Indexing: '{0}'").format(self.tr("Unknown item")))

            if tItem is not None and tItem.itemType == nwItemType.FILE:
                logger.verbose("Scanning: %s" % tItem.itemName)
                self.theIndex.reIndexHandle(tItem.itemHandle)

                # Get Word Counts
                cC, wC, pC = self.theIndex.getCounts(tItem.itemHandle)
                tItem.setCharCount(cC)
                tItem.setWordCount(wC)
                tItem.setParaCount(pC)
                self.treeView.propagateCount(tItem.itemHandle, wC)
                self.treeView.projectWordCount()

        tEnd = time()
        self.setStatus(
            self.tr("Indexing completed in {0} ms").format(f"{(tEnd - tStart)*1000.0:.1f}")
        )
        self.docEditor.updateTagHighLighting()
        qApp.restoreOverrideCursor()

        if not beQuiet:
            self.makeAlert(self.tr(
                "The project index has been successfully rebuilt."
            ), nwAlert.INFO)

        return True

    def rebuildOutline(self):
        """Force a rebuild of the Outline view.
        """
        if not self.hasProject:
            logger.error("No project open")
            return False

        logger.verbose("Forcing a rebuild of the Project Outline")
        self.mainTabs.setCurrentWidget(self.splitOutline)
        self.projView.refreshTree(overRide=True)

        return True

    ##
    #  Main Dialogs
    ##

    def showProjectLoadDialog(self):
        """Opens the projects dialog for selecting either existing
        projects from a cache of recently opened projects, or provide a
        browse button for projects not yet cached. Selecting to create a
        new project is forwarded to the new project wizard.
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
        """Open the wizard and assemble a project options dict.
        """
        newProj = GuiProjectWizard(self)
        newProj.exec_()

        if newProj.result() == QDialog.Accepted:
            return self._assembleProjectWizardData(newProj)

        return None

    def showPreferencesDialog(self):
        """Open the preferences dialog.
        """
        dlgConf = GuiPreferences(self)
        dlgConf.exec_()

        if dlgConf.result() == QDialog.Accepted:
            logger.debug("Applying new preferences")
            self.initMain()
            self.theTheme.updateTheme()
            self.saveDocument()
            self.docEditor.initEditor()
            self.docViewer.initViewer()
            self.treeView.initTree()
            self.novelView.initTree()
            self.projView.initOutline()
            self.projMeta.initDetails()

        return

    def showProjectSettingsDialog(self):
        """Open the project settings dialog.
        """
        if not self.hasProject:
            logger.error("No project open")
            return

        dlgProj = GuiProjectSettings(self)
        dlgProj.exec_()

        if dlgProj.result() == QDialog.Accepted:
            logger.debug("Applying new project settings")
            self.docEditor.setDictionaries()
            self._updateWindowTitle(self.theProject.projName)

        return

    def showProjectDetailsDialog(self):
        """Open the project details dialog.
        """
        if not self.hasProject:
            logger.error("No project open")
            return

        self.treeView.flushTreeOrder()

        dlgDetails = GuiProjectDetails(self)
        dlgDetails.setModal(False)
        dlgDetails.show()

        return

    def showBuildProjectDialog(self):
        """Open the build project dialog.
        """
        if not self.hasProject:
            logger.error("No project open")
            return

        dlgBuild = getGuiItem("GuiBuildNovel")
        if dlgBuild is None:
            dlgBuild = GuiBuildNovel(self)

        dlgBuild.setModal(False)
        dlgBuild.show()
        qApp.processEvents()
        dlgBuild.viewCachedDoc()

        return

    def showProjectWordListDialog(self):
        """Open the project word list dialog.
        """
        if not self.hasProject:
            logger.error("No project open")
            return

        dlgWords = GuiWordList(self)
        dlgWords.exec_()

        if dlgWords.result() == QDialog.Accepted:
            logger.debug("Reloading word list")
            self.docEditor.setDictionaries()

        return

    def showWritingStatsDialog(self):
        """Open the session log dialog.
        """
        if not self.hasProject:
            logger.error("No project open")
            return

        dlgStats = getGuiItem("GuiWritingStats")
        if dlgStats is None:
            dlgStats = GuiWritingStats(self)

        dlgStats.setModal(False)
        dlgStats.show()
        qApp.processEvents()
        dlgStats.populateGUI()

        return

    def showAboutNWDialog(self, showNotes=False):
        """Show the about dialog for novelWriter.
        """
        dlgAbout = GuiAbout(self)
        dlgAbout.setModal(True)
        dlgAbout.show()
        qApp.processEvents()
        dlgAbout.populateGUI()

        if showNotes:
            dlgAbout.showReleaseNotes()

        return

    def showAboutQtDialog(self):
        """Show the about dialog for Qt.
        """
        msgBox = QMessageBox()
        msgBox.aboutQt(self, "About Qt")
        return

    def makeAlert(self, theMessage, theLevel=nwAlert.INFO):
        """Alert both the user and the logger at the same time. Message
        can be either a string or an array of strings.
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
        msgBox = QMessageBox()
        if theLevel == nwAlert.INFO:
            msgBox.information(self, self.tr("Information"), popMsg)
        elif theLevel == nwAlert.WARN:
            msgBox.warning(self, self.tr("Warning"), popMsg)
        elif theLevel == nwAlert.ERROR:
            msgBox.critical(self, self.tr("Error"), popMsg)
        elif theLevel == nwAlert.BUG:
            popMsg += "<br>%s" % self.tr("This is a bug!")
            msgBox.critical(self, self.tr("Internal Error"), popMsg)

        return

    def askQuestion(self, theTitle, theQuestion):
        """Ask the user a Yes/No question.
        """
        msgBox = QMessageBox()
        msgRes = msgBox.question(self, theTitle, theQuestion, QMessageBox.Yes | QMessageBox.No)
        return msgRes == QMessageBox.Yes

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
            msgYes = self.askQuestion(
                self.tr("Exit"),
                "%s<br>%s" % (
                    self.tr("Do you want to exit novelWriter?"),
                    self.tr("Changes are saved automatically.")
                )
            )
            if not msgYes:
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
        self.mainConf.setNovelColWidths(self.novelView.getColumnSizes())
        if not self.mainConf.isFullScreen:
            self.mainConf.setWinSize(self.width(), self.height())

        if self.hasProject:
            self.closeProject(True)

        self.mainConf.saveConfig()
        self.reportConfErr()
        self.mainMenu.closeHelp()

        qApp.quit()

        return True

    def switchFocus(self, paneNo):
        """Switch focus between main GUI views.
        """
        if paneNo == nwWidget.TREE:
            self.treeView.setFocus()
        elif paneNo == nwWidget.EDITOR:
            self.mainTabs.setCurrentWidget(self.splitDocs)
            self.docEditor.setFocus()
        elif paneNo == nwWidget.VIEWER:
            self.mainTabs.setCurrentWidget(self.splitDocs)
            self.docViewer.setFocus()
        elif paneNo == nwWidget.OUTLINE:
            self.mainTabs.setCurrentWidget(self.splitOutline)
            self.projView.setFocus()
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
        if self.docEditor.docHandle() is None:
            logger.error("No document open, so not activating Focus Mode")
            self.mainMenu.setFocusMode(self.isFocusMode)
            return False

        self.isFocusMode = not self.isFocusMode
        self.mainMenu.setFocusMode(self.isFocusMode)
        if self.isFocusMode:
            logger.debug("Activating Focus Mode")
            self.mainTabs.setCurrentWidget(self.splitDocs)
            self.switchFocus(nwWidget.EDITOR)
        else:
            logger.debug("Deactivating Focus Mode")

        isVisible = not self.isFocusMode
        self.treePane.setVisible(isVisible)
        self.statusBar.setVisible(isVisible)
        self.mainMenu.setVisible(isVisible)
        self.mainTabs.tabBar().setVisible(isVisible)

        hideDocFooter = self.isFocusMode and self.mainConf.hideFocusFooter
        self.docEditor.docFooter.setVisible(not hideDocFooter)
        self.docEditor.docHeader.updateFocusMode()

        if self.splitView.isVisible():
            self.splitView.setVisible(False)
        elif self.docViewer.docHandle() is not None:
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
        self.addAction(self.mainMenu.aEditItem)
        self.addAction(self.mainMenu.aExitNW)

        # Document
        self.addAction(self.mainMenu.aSaveDoc)
        self.addAction(self.mainMenu.aCloseDoc)

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
        self.addAction(self.mainMenu.aInsHorBar)
        self.addAction(self.mainMenu.aInsFigDash)
        self.addAction(self.mainMenu.aInsQuoteLS)
        self.addAction(self.mainMenu.aInsQuoteRS)
        self.addAction(self.mainMenu.aInsQuoteLD)
        self.addAction(self.mainMenu.aInsQuoteRD)
        self.addAction(self.mainMenu.aInsMSApos)
        self.addAction(self.mainMenu.aInsEllipsis)
        self.addAction(self.mainMenu.aInsPrime)
        self.addAction(self.mainMenu.aInsDPrime)
        self.addAction(self.mainMenu.aInsNBSpace)
        self.addAction(self.mainMenu.aInsThinSpace)
        self.addAction(self.mainMenu.aInsThinNBSpace)
        self.addAction(self.mainMenu.aInsBullet)
        self.addAction(self.mainMenu.aInsHyBull)
        self.addAction(self.mainMenu.aInsFlower)
        self.addAction(self.mainMenu.aInsPerMille)
        self.addAction(self.mainMenu.aInsDegree)
        self.addAction(self.mainMenu.aInsMinus)
        self.addAction(self.mainMenu.aInsTimes)
        self.addAction(self.mainMenu.aInsDivide)

        for mAction, _ in self.mainMenu.mInsKWItems.values():
            self.addAction(mAction)

        # Search
        self.addAction(self.mainMenu.aFind)
        self.addAction(self.mainMenu.aReplace)
        self.addAction(self.mainMenu.aFindNext)
        self.addAction(self.mainMenu.aFindPrev)
        self.addAction(self.mainMenu.aReplaceNext)

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
        self.addAction(self.mainMenu.aFmtAlignLeft)
        self.addAction(self.mainMenu.aFmtAlignCentre)
        self.addAction(self.mainMenu.aFmtAlignRight)
        self.addAction(self.mainMenu.aFmtIndentLeft)
        self.addAction(self.mainMenu.aFmtIndentRight)
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

    def _updateWindowTitle(self, projName=None):
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
        if self.hasProject and self.docEditor.docChanged():
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
    #  Slots
    ##

    @pyqtSlot()
    def _timeTick(self):
        """Triggered on every tick of the timer.
        """
        if not self.hasProject:
            return

        currTime = time()
        editIdle = currTime - self.docEditor.lastActive() > self.mainConf.userIdleTime
        userIdle = qApp.applicationState() != Qt.ApplicationActive

        if editIdle or userIdle:
            self.idleTime += currTime - self.idleRefTime
            self.statusBar.setUserIdle(True)
        else:
            self.statusBar.setUserIdle(False)

        self.idleRefTime = currTime
        self.statusBar.updateTime(idleTime=self.idleTime)

        return

    @pyqtSlot()
    def _treeSingleClick(self):
        """Single click on a project tree item just updates the details
        panel below the tree.
        """
        sHandle = self.treeView.getSelectedHandle()
        if sHandle is not None:
            self.treeMeta.updateViewBox(sHandle)
        return

    @pyqtSlot("QTreeWidgetItem*", int)
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

    @pyqtSlot()
    def _treeNovelItemChanged(self):
        """Triggered when there is a change to a novel item in the
        project tree.
        """
        if self.mainTabs.currentIndex() == self.idxTabProj:
            logger.verbose("Novel tree changed while Outline tab active")
            if self.hasProject:
                self.treeView.flushTreeOrder()
                self.projView.refreshTree(novelChanged=True)

        return

    @pyqtSlot()
    def _treeKeyPressReturn(self):
        """The user pressed return on an item in the tree. If it is a
        file, we open it. Otherwise, we do nothing. Pressing return does
        not change focus to the editor as double click does.
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

    @pyqtSlot()
    def _keyPressEscape(self):
        """When the escape key is pressed somewhere in the main window,
        do the following, in order:
        """
        if self.docEditor.docSearch.isVisible():
            self.docEditor.closeSearch()
        elif self.isFocusMode:
            self.toggleFocusMode()

        return

    @pyqtSlot(int)
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

    @pyqtSlot(int)
    def _projTabsChanged(self, tabIndex):
        """Activated when the project view tab is changed.
        """
        sHandle = None

        if tabIndex == self.idxTreeView:
            logger.verbose("Project tree tab activated")
            sHandle = self.treeView.getSelectedHandle()

        elif tabIndex == self.idxNovelView:
            logger.verbose("Novel tree tab activated")
            if self.hasProject:
                self.novelView.refreshTree()
                sHandle = self.novelView.getSelectedHandle()

        self.treeMeta.updateViewBox(sHandle)

        return

# END Class GuiMain
