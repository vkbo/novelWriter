"""
novelWriter – GUI Main Window
=============================
The main application window

File History:
Created: 2018-09-22 [0.0.1]

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

import logging
import novelwriter

from enum import Enum
from time import time
from pathlib import Path
from datetime import datetime

from PyQt5.QtCore import Qt, QTimer, QThreadPool, pyqtSlot
from PyQt5.QtGui import QIcon, QKeySequence, QCursor
from PyQt5.QtWidgets import (
    qApp, QMainWindow, QVBoxLayout, QWidget, QSplitter, QFileDialog, QShortcut,
    QMessageBox, QDialog, QStackedWidget
)

from novelwriter.gui.theme import GuiTheme
from novelwriter.gui.sidebar import GuiSideBar
from novelwriter.gui.outline import GuiOutlineView
from novelwriter.gui.mainmenu import GuiMainMenu
from novelwriter.gui.projtree import GuiProjectView
from novelwriter.gui.doceditor import GuiDocEditor
from novelwriter.gui.docviewer import GuiDocViewDetails, GuiDocViewer
from novelwriter.gui.noveltree import GuiNovelView
from novelwriter.gui.statusbar import GuiMainStatus
from novelwriter.gui.itemdetails import GuiItemDetails
from novelwriter.dialogs.about import GuiAbout
from novelwriter.dialogs.updates import GuiUpdates
from novelwriter.dialogs.projload import GuiProjectLoad
from novelwriter.dialogs.wordlist import GuiWordList
from novelwriter.dialogs.preferences import GuiPreferences
from novelwriter.dialogs.projdetails import GuiProjectDetails
from novelwriter.dialogs.projsettings import GuiProjectSettings
from novelwriter.tools.build import GuiBuildNovel
from novelwriter.tools.lipsum import GuiLipsum
from novelwriter.tools.projwizard import GuiProjectWizard
from novelwriter.tools.writingstats import GuiWritingStats
from novelwriter.core.project import NWProject
from novelwriter.core.coretools import ProjectBuilder

from novelwriter.enum import (
    nwDocMode, nwItemType, nwItemClass, nwAlert, nwWidget, nwView
)
from novelwriter.common import getGuiItem, hexToInt
from novelwriter.constants import nwFiles

logger = logging.getLogger(__name__)


class GuiMain(QMainWindow):

    def __init__(self):
        super().__init__()

        logger.debug("Initialising GUI ...")
        self.setObjectName("GuiMain")
        self.mainConf = novelwriter.CONFIG
        self.threadPool = QThreadPool()

        # System Info
        # ===========

        logger.info("OS: %s", self.mainConf.osType)
        logger.info("Kernel: %s", self.mainConf.kernelVer)
        logger.info("Host: %s", self.mainConf.hostName)
        logger.info("Qt5: %s (0x%06x)", self.mainConf.verQtString, self.mainConf.verQtValue)
        logger.info("PyQt5: %s (0x%06x)", self.mainConf.verPyQtString, self.mainConf.verPyQtValue)
        logger.info("Python: %s (0x%08x)", self.mainConf.verPyString, self.mainConf.verPyHexVal)
        logger.info("GUI Language: %s", self.mainConf.guiLocale)

        # Core Classes
        # ============

        # Core Classes and Settings
        self.mainTheme   = GuiTheme()
        self.theProject  = NWProject(self)
        self.hasProject  = False
        self.isFocusMode = False
        self.idleRefTime = time()
        self.idleTime    = 0.0

        # Prepare Main Window
        self.resize(*self.mainConf.mainWinSize)
        self._updateWindowTitle()

        nwIcon = self.mainConf.assetPath("icons") / "novelwriter.svg"
        self.nwIcon = QIcon(str(nwIcon)) if nwIcon.is_file() else QIcon()
        self.setWindowIcon(self.nwIcon)
        qApp.setWindowIcon(self.nwIcon)

        # Build the GUI
        # =============

        # Sizes
        mPx = self.mainConf.pxInt(4)
        hWd = self.mainConf.pxInt(4)

        # Main GUI Elements
        self.mainStatus  = GuiMainStatus(self)
        self.projView    = GuiProjectView(self)
        self.novelView   = GuiNovelView(self)
        self.docEditor   = GuiDocEditor(self)
        self.viewMeta    = GuiDocViewDetails(self)
        self.docViewer   = GuiDocViewer(self)
        self.itemDetails = GuiItemDetails(self)
        self.outlineView = GuiOutlineView(self)
        self.mainMenu    = GuiMainMenu(self)
        self.viewsBar    = GuiSideBar(self)

        # Project Tree Stack
        self.projStack = QStackedWidget()
        self.projStack.addWidget(self.projView)
        self.projStack.addWidget(self.novelView)
        self.projStack.currentChanged.connect(self._projStackChanged)

        # Project Tree View
        self.treePane = QWidget()
        self.treeBox = QVBoxLayout()
        self.treeBox.setContentsMargins(0, 0, 0, 0)
        self.treeBox.setSpacing(mPx)
        self.treeBox.addWidget(self.projStack)
        self.treeBox.addWidget(self.itemDetails)
        self.treePane.setLayout(self.treeBox)

        # Splitter : Document Viewer / Document Meta
        self.splitView = QSplitter(Qt.Vertical)
        self.splitView.addWidget(self.docViewer)
        self.splitView.addWidget(self.viewMeta)
        self.splitView.setHandleWidth(hWd)
        self.splitView.setOpaqueResize(False)
        self.splitView.setSizes(self.mainConf.viewPanePos)

        # Splitter : Document Editor / Document Viewer
        self.splitDocs = QSplitter(Qt.Horizontal)
        self.splitDocs.addWidget(self.docEditor)
        self.splitDocs.addWidget(self.splitView)
        self.splitDocs.setOpaqueResize(False)
        self.splitDocs.setHandleWidth(hWd)

        # Splitter : Project Tree / Main Tabs
        self.splitMain = QSplitter(Qt.Horizontal)
        self.splitMain.setContentsMargins(0, 0, 0, 0)
        self.splitMain.addWidget(self.treePane)
        self.splitMain.addWidget(self.splitDocs)
        self.splitMain.setOpaqueResize(False)
        self.splitMain.setHandleWidth(hWd)
        self.splitMain.setSizes(self.mainConf.mainPanePos)

        # Main Stack : Editor / Outline
        self.mainStack = QStackedWidget()
        self.mainStack.addWidget(self.splitMain)
        self.mainStack.addWidget(self.outlineView)
        self.mainStack.currentChanged.connect(self._mainStackChanged)

        # Indices of Splitter Widgets
        self.idxTree     = self.splitMain.indexOf(self.treePane)
        self.idxMain     = self.splitMain.indexOf(self.splitDocs)
        self.idxEditor   = self.splitDocs.indexOf(self.docEditor)
        self.idxViewer   = self.splitDocs.indexOf(self.splitView)
        self.idxViewDoc  = self.splitView.indexOf(self.docViewer)
        self.idxViewMeta = self.splitView.indexOf(self.viewMeta)

        # Indices of Tab Widgets
        self.idxEditorView  = self.mainStack.indexOf(self.splitMain)
        self.idxOutlineView = self.mainStack.indexOf(self.outlineView)
        self.idxProjView    = self.projStack.indexOf(self.projView)
        self.idxNovelView   = self.projStack.indexOf(self.novelView)

        # Splitter Behaviour
        self.splitMain.setCollapsible(self.idxTree, False)
        self.splitMain.setCollapsible(self.idxMain, False)
        self.splitDocs.setCollapsible(self.idxEditor, False)
        self.splitDocs.setCollapsible(self.idxViewer, False)
        self.splitView.setCollapsible(self.idxViewDoc, False)
        self.splitView.setCollapsible(self.idxViewMeta, False)

        # Editor / Viewer Default State
        self.splitView.setVisible(False)
        self.docEditor.closeSearch()

        # Initialise the Project Tree
        self.rebuildTrees()

        # Set Main Window Elements
        self.setMenuBar(self.mainMenu)
        self.setCentralWidget(self.mainStack)
        self.setStatusBar(self.mainStatus)
        self.addToolBar(Qt.LeftToolBarArea, self.viewsBar)
        self.setContextMenuPolicy(Qt.NoContextMenu)  # Issue #1147

        # Connect Signals
        # ===============

        self.theProject.projectStatusChanged.connect(self.mainStatus.doUpdateProjectStatus)

        self.viewsBar.viewChangeRequested.connect(self._changeView)

        self.projView.selectedItemChanged.connect(self.itemDetails.updateViewBox)
        self.projView.openDocumentRequest.connect(self._openDocument)
        self.projView.wordCountsChanged.connect(self._updateStatusWordCount)
        self.projView.treeItemChanged.connect(self.docEditor.updateDocInfo)
        self.projView.treeItemChanged.connect(self.docViewer.updateDocInfo)
        self.projView.treeItemChanged.connect(self.itemDetails.updateViewBox)
        self.projView.rootFolderChanged.connect(self.outlineView.updateRootItem)
        self.projView.rootFolderChanged.connect(self.novelView.updateRootItem)
        self.projView.rootFolderChanged.connect(self.projView.updateRootItem)
        self.projView.projectSettingsRequest.connect(self.showProjectSettingsDialog)

        self.novelView.selectedItemChanged.connect(self.itemDetails.updateViewBox)
        self.novelView.openDocumentRequest.connect(self._openDocument)

        self.docEditor.spellDictionaryChanged.connect(self.mainStatus.setLanguage)
        self.docEditor.docEditedStatusChanged.connect(self.mainStatus.doUpdateDocumentStatus)
        self.docEditor.docCountsChanged.connect(self.itemDetails.updateCounts)
        self.docEditor.docCountsChanged.connect(self.projView.updateCounts)
        self.docEditor.loadDocumentTagRequest.connect(self._followTag)
        self.docEditor.novelStructureChanged.connect(self.novelView.refreshTree)
        self.docEditor.novelItemMetaChanged.connect(self.novelView.updateNovelItemMeta)

        self.docViewer.loadDocumentTagRequest.connect(self._followTag)

        self.outlineView.loadDocumentTagRequest.connect(self._followTag)
        self.outlineView.openDocumentRequest.connect(self._openDocument)

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

        keyReturn = QShortcut(self)
        keyReturn.setKey(QKeySequence(Qt.Key_Return))
        keyReturn.activated.connect(self._keyPressReturn)

        keyEnter = QShortcut(self)
        keyEnter.setKey(QKeySequence(Qt.Key_Enter))
        keyEnter.activated.connect(self._keyPressReturn)

        keyEscape = QShortcut(self)
        keyEscape.setKey(QKeySequence(Qt.Key_Escape))
        keyEscape.activated.connect(self._keyPressEscape)

        # Forward Functions
        self.setStatus = self.mainStatus.setStatus

        # Force a show of the GUI
        self.show()

        # Check that config loaded fine
        self.reportConfErr()

        # Initialise Main GUI
        self.initMain()
        self.asProjTimer.start()
        self.asDocTimer.start()
        self.mainStatus.clearStatus()

        # Handle Windows Mode
        self.showNormal()
        if self.mainConf.isFullScreen:
            self.toggleFullScreenMode()

        logger.debug("GUI initialisation complete")

        if novelwriter.__hexversion__[-2] == "a" and logger.getEffectiveLevel() > logging.DEBUG:
            self.makeAlert(self.tr(
                "You are running an untested development version of novelWriter. "
                "Please be careful when working on a live project "
                "and make sure you take regular backups."
            ), nwAlert.WARN)

        logger.info("novelWriter is ready ...")
        self.setStatus(self.tr("novelWriter is ready ..."))

        return

    def clearGUI(self):
        """Wrapper function to clear all sub-elements of the main GUI.
        """
        # Project Area
        self.projView.clearProject()
        self.novelView.clearProject()
        self.itemDetails.clearDetails()

        # Work Area
        self.docEditor.clearEditor()
        self.docEditor.setDictionaries()
        self.closeDocViewer(byUser=False)
        self.outlineView.clearProject()

        # General
        self.mainStatus.clearStatus()
        self._updateWindowTitle()

        return True

    def initMain(self):
        """Initialise elements that depend on user settings.
        """
        self.asProjTimer.setInterval(int(self.mainConf.autoSaveProj*1000))
        self.asDocTimer.setInterval(int(self.mainConf.autoSaveDoc*1000))
        return True

    def postLaunchTasks(self, cmdOpen):
        """This function is called after the main window is created to
        determine what to open or show after initialisation.
        """
        if cmdOpen:
            logger.info("Command line path: %s", cmdOpen)
            self.openProject(cmdOpen)

        if not self.hasProject:
            self.showProjectLoadDialog()

        # Determine whether release notes need to be shown or not
        if hexToInt(self.mainConf.lastNotes) < hexToInt(novelwriter.__hexversion__):
            self.mainConf.lastNotes = novelwriter.__hexversion__
            self.showAboutNWDialog(showNotes=True)

        return

    ##
    #  Project Actions
    ##

    def newProject(self, projData=None):
        """Create a new project via the new project wizard.
        """
        if self.hasProject:
            if not self.closeProject():
                self.makeAlert(self.tr(
                    "Cannot create a new project when another project is open."
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

        if (Path(projPath) / nwFiles.PROJ_FILE).is_file():
            self.makeAlert(self.tr(
                "A project already exists in that location. "
                "Please choose another folder."
            ), nwAlert.ERROR)
            return False

        logger.info("Creating new project")
        nwProject = ProjectBuilder(self)
        if nwProject.buildProject(projData):
            self.openProject(projPath)
        else:
            return False

        return True

    def closeProject(self, isYes=False):
        """Close the project if one is open. isYes is passed on from the
        close application event so the user doesn't get prompted twice
        to confirm.
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

        saveOK = self.saveProject()
        doBackup = False
        if self.theProject.data.doBackup and self.mainConf.backupOnClose:
            doBackup = True
            if self.mainConf.askBeforeBackup:
                msgYes = self.askQuestion(
                    self.tr("Backup Project"),
                    self.tr("Backup the current project?")
                )
                if not msgYes:
                    doBackup = False

        if doBackup:
            self.theProject.backupProject(False)

        if saveOK:
            self.closeDocument()
            self.docViewer.clearNavHistory()
            self.outlineView.closeProjectTasks()
            self.novelView.closeProjectTasks()

            self.theProject.closeProject(self.idleTime)
            self.idleRefTime = time()
            self.idleTime = 0.0

            self.clearGUI()
            self.hasProject = False
            self._changeView(nwView.PROJECT)

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
        self._changeView(nwView.PROJECT)

        # Try to open the project
        if not self.theProject.openProject(projFile):
            # The project open failed.

            lockStatus = self.theProject.getLockStatus()
            if lockStatus is None:
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
                    lockStatus[0], lockStatus[1], lockStatus[2],
                    datetime.fromtimestamp(int(lockStatus[3])).strftime("%x %X")
                )
            except Exception:
                lockDetails = ""

            msgBox = QMessageBox()
            msgRes = msgBox.warning(
                self, self.tr("Project Locked"),
                "%s<br><br>%s<br>%s" % (
                    self.tr(
                        "The project is already open by another instance of "
                        "novelWriter, and is therefore locked. Override lock "
                        "and continue anyway?"
                    ),
                    self.tr(
                        "Note: If the program or the computer previously "
                        "crashed, the lock can safely be overridden. However, "
                        "overriding it is not recommended if the project is "
                        "open in another instance of novelWriter. Doing so "
                        "may corrupt the project."
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
        self.hasProject = True
        self.idleRefTime = time()
        self.idleTime = 0.0

        # Update GUI
        self._updateWindowTitle(self.theProject.data.name)
        self.rebuildTrees()
        self.docEditor.setDictionaries()
        self.docEditor.toggleSpellCheck(self.theProject.data.spellCheck)
        self.mainStatus.setRefTime(self.theProject.projOpened)
        self.projView.openProjectTasks()
        self.novelView.openProjectTasks()
        self.outlineView.openProjectTasks()
        self._updateStatusWordCount()

        # Restore previously open documents, if any
        # If none was recorded, open the first document found
        lastEdited = self.theProject.data.getLastHandle("editor")
        if lastEdited is None:
            for nwItem in self.theProject.tree:
                if nwItem and nwItem.isFileType():
                    lastEdited = nwItem.itemHandle
                    break

        if lastEdited is not None:
            self.openDocument(lastEdited, doScroll=True)

        lastViewed = self.theProject.data.getLastHandle("viewer")
        if lastViewed is not None:
            self.viewDocument(lastViewed)

        # Check if we need to rebuild the index
        if self.theProject.index.indexBroken:
            self.makeAlert(self.tr(
                "The project index is outdated or broken. Rebuilding index."
            ), nwAlert.INFO)
            self.rebuildIndex()

        # Make sure the changed status is set to false on things opened
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

        self.projView.saveProjectTasks()
        self.theProject.saveProject(autoSave=autoSave)

        return True

    ##
    #  Document Actions
    ##

    def closeDocument(self, beforeOpen=False):
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
        if not beforeOpen:
            self.novelView.setActiveHandle(None)

        return True

    def openDocument(self, tHandle, tLine=None, changeFocus=True, doScroll=False):
        """Open a specific document, optionally at a given line.
        """
        if not self.hasProject:
            logger.error("No project open")
            return False

        if not self.theProject.tree.checkType(tHandle, nwItemType.FILE):
            logger.debug("Requested item '%s' is not a document", tHandle)
            return False

        self._changeView(nwView.EDITOR)
        cHandle = self.docEditor.docHandle()
        if cHandle == tHandle:
            self.docEditor.setCursorLine(tLine)
            if changeFocus:
                self.docEditor.setFocus()
            return True

        self.closeDocument(beforeOpen=True)
        if self.docEditor.loadText(tHandle, tLine):
            self.theProject.data.setLastHandle(tHandle, "editor")
            self.projView.setSelectedHandle(tHandle, doScroll=doScroll)
            self.novelView.setActiveHandle(tHandle)
            if changeFocus:
                self.docEditor.setFocus()
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

        nHandle = None   # The next handle after tHandle
        fHandle = None   # The first file handle we encounter
        foundIt = False  # We've found tHandle, pick the next we see
        for tItem in self.theProject.tree:
            if not tItem.isFileType():
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

    def viewDocument(self, tHandle=None, sTitle=None):
        """Load a document for viewing in the view panel.
        """
        if not self.hasProject:
            logger.error("No project open")
            return False

        if tHandle is None:
            logger.debug("Viewing document, but no handle provided")

            if self.docEditor.hasFocus():
                tHandle = self.docEditor.docHandle()

            if tHandle is not None:
                self.saveDocument()
            else:
                tHandle = self.projView.getSelectedHandle()

            if tHandle is None:
                tHandle = self.theProject.data.getLastHandle("viewer")

            if tHandle is None:
                logger.debug("No document to view, giving up")
                return False

        # Make sure main tab is in Editor view
        self._changeView(nwView.EDITOR)

        logger.debug("Viewing document with handle '%s'", tHandle)
        if self.docViewer.loadText(tHandle):
            if not self.splitView.isVisible():
                bPos = self.splitMain.sizes()
                self.splitView.setVisible(True)
                vPos = [0, 0]
                vPos[0] = int(bPos[1]/2)
                vPos[1] = bPos[1] - vPos[0]
                self.splitDocs.setSizes(vPos)
                self.viewMeta.setVisible(self.mainConf.showRefPanel)

            if sTitle:
                self.docViewer.navigateTo(f"#{sTitle}")

        return True

    def importDocument(self):
        """Import the text contained in an out-of-project text file, and
        insert the text into the currently open document.
        """
        if not self.hasProject:
            logger.error("No project open")
            return False

        lastPath = self.mainConf.lastPath()
        extFilter = [
            self.tr("Text files ({0})").format("*.txt"),
            self.tr("Markdown files ({0})").format("*.md"),
            self.tr("novelWriter files ({0})").format("*.nwd"),
            self.tr("All files ({0})").format("*"),
        ]
        loadFile, _ = QFileDialog.getOpenFileName(
            self, self.tr("Import File"), str(lastPath), filter=";;".join(extFilter)
        )
        if not loadFile:
            return False

        if loadFile.strip() == "":
            return False

        theText = None
        try:
            with open(loadFile, mode="rt", encoding="utf-8") as inFile:
                theText = inFile.read()
            self.mainConf.setLastPath(loadFile)
        except Exception as exc:
            self.makeAlert(self.tr(
                "Could not read file. The file must be an existing text file."
            ), nwAlert.ERROR, exception=exc)
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
                    "Importing the file will overwrite the current content of "
                    "the document. Do you want to proceed?"
                )
            )
            if not msgYes:
                return False

        self.docEditor.replaceText(theText)

        return True

    def passDocumentAction(self, theAction):
        """Pass on document action to the document viewer if it has
        focus, or pass it to the document editor if it or any of
        its child widgets have focus. If neither has focus, ignore the
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
        """Open the selected item from the tree that is currently
        active. It is not checked that the item is actually a document.
        That should be handled by the openDocument function.
        """
        if not self.hasProject:
            logger.error("No project open")
            return False

        tHandle = None
        sTitle = None
        tLine = None
        if self.projView.treeHasFocus():
            tHandle = self.projView.getSelectedHandle()
        elif self.novelView.treeHasFocus():
            tHandle, sTitle = self.novelView.getSelectedHandle()
        elif self.outlineView.treeHasFocus():
            tHandle, sTitle = self.outlineView.getSelectedHandle()
        else:
            logger.warning("No item selected")
            return False

        if tHandle is not None and sTitle is not None:
            hItem = self.theProject.index.getItemHeader(tHandle, sTitle)
            if hItem is not None:
                tLine = hItem.line

        if tHandle is not None:
            self.openDocument(tHandle, tLine=tLine, changeFocus=False, doScroll=False)

        return True

    def editItemLabel(self, tHandle=None):
        """Open the edit item dialog.
        """
        if not self.hasProject:
            logger.error("No project open")
            return False

        if tHandle is None and (self.docEditor.anyFocus() or self.isFocusMode):
            tHandle = self.docEditor.docHandle()
        self.projView.renameTreeItem(tHandle)

        return True

    def rebuildTrees(self):
        """Rebuild the project tree.
        """
        self.projView.populateTree()
        return

    def rebuildIndex(self, beQuiet=False):
        """Rebuild the entire index.
        """
        if not self.hasProject:
            logger.error("No project open")
            return False

        logger.info("Rebuilding index ...")
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        tStart = time()

        self.projView.saveProjectTasks()
        self.theProject.index.rebuildIndex()
        self.projView.populateTree()
        self.novelView.refreshTree()

        tEnd = time()
        self.setStatus(
            self.tr("Indexing completed in {0} ms").format(f"{(tEnd - tStart)*1000.0:.1f}")
        )
        self.docEditor.updateTagHighLighting()
        self._updateStatusWordCount()
        qApp.restoreOverrideCursor()

        if not beQuiet:
            self.makeAlert(self.tr(
                "The project index has been successfully rebuilt."
            ), nwAlert.INFO)

        return True

    ##
    #  Main Dialogs
    ##

    def showProjectLoadDialog(self):
        """Open the projects dialog for selecting either existing
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
            self.saveDocument()

            if dlgConf.needsRestart:
                self.makeAlert(self.tr(
                    "Some changes will not be applied until novelWriter has been restarted."
                ), nwAlert.INFO)

            if dlgConf.refreshTree:
                self.projView.populateTree()

            if dlgConf.updateTheme:
                # We are doing this manually instead of connecting to
                # qApp.paletteChanged since the processing order matters
                self.mainTheme.loadTheme()
                self.docEditor.updateTheme()
                self.docViewer.updateTheme()
                self.viewsBar.updateTheme()
                self.projView.updateTheme()
                self.novelView.updateTheme()
                self.outlineView.updateTheme()
                self.itemDetails.updateTheme()
                self.mainStatus.updateTheme()

            if dlgConf.updateSyntax:
                self.mainTheme.loadSyntax()
                self.docEditor.updateSyntaxColours()

            self.docEditor.initEditor()
            self.docViewer.initViewer()
            self.projView.initSettings()
            self.novelView.initSettings()
            self.outlineView.initSettings()

            self._updateStatusWordCount()

        return

    @pyqtSlot(int)
    def showProjectSettingsDialog(self, focusTab=GuiProjectSettings.TAB_MAIN):
        """Open the project settings dialog.
        """
        if not self.hasProject:
            logger.error("No project open")
            return False

        dlgProj = GuiProjectSettings(self, focusTab=focusTab)
        dlgProj.exec_()

        if dlgProj.result() == QDialog.Accepted:
            logger.debug("Applying new project settings")
            if dlgProj.spellChanged:
                self.docEditor.setDictionaries()
            self.itemDetails.refreshDetails()
            self._updateWindowTitle(self.theProject.data.name)

        return True

    def showProjectDetailsDialog(self):
        """Open the project details dialog.
        """
        if not self.hasProject:
            logger.error("No project open")
            return False

        dlgDetails = getGuiItem("GuiProjectDetails")
        if dlgDetails is None:
            dlgDetails = GuiProjectDetails(self)
        assert isinstance(dlgDetails, GuiProjectDetails)

        dlgDetails.setModal(False)
        dlgDetails.show()
        dlgDetails.raise_()
        dlgDetails.updateValues()

        return True

    def showBuildProjectDialog(self):
        """Open the build project dialog.
        """
        if not self.hasProject:
            logger.error("No project open")
            return False

        dlgBuild = getGuiItem("GuiBuildNovel")
        if dlgBuild is None:
            dlgBuild = GuiBuildNovel(self)
        assert isinstance(dlgBuild, GuiBuildNovel)

        dlgBuild.setModal(False)
        dlgBuild.show()
        dlgBuild.raise_()
        qApp.processEvents()
        dlgBuild.viewCachedDoc()

        return True

    def showLoremIpsumDialog(self):
        """Open the insert lorem ipsum text dialog.
        """
        if not self.hasProject:
            logger.error("No project open")
            return False

        dlgLipsum = getGuiItem("GuiLipsum")
        if dlgLipsum is None:
            dlgLipsum = GuiLipsum(self)
        assert isinstance(dlgLipsum, GuiLipsum)

        dlgLipsum.setModal(False)
        dlgLipsum.show()
        dlgLipsum.raise_()
        qApp.processEvents()

        return True

    def showProjectWordListDialog(self):
        """Open the project word list dialog.
        """
        if not self.hasProject:
            logger.error("No project open")
            return False

        dlgWords = GuiWordList(self)
        dlgWords.exec_()

        if dlgWords.result() == QDialog.Accepted:
            logger.debug("Reloading word list")
            self.docEditor.setDictionaries()

        return True

    def showWritingStatsDialog(self):
        """Open the session stats dialog.
        """
        if not self.hasProject:
            logger.error("No project open")
            return False

        dlgStats = getGuiItem("GuiWritingStats")
        if dlgStats is None:
            dlgStats = GuiWritingStats(self)
        assert isinstance(dlgStats, GuiWritingStats)

        dlgStats.setModal(False)
        dlgStats.show()
        dlgStats.raise_()
        qApp.processEvents()
        dlgStats.populateGUI()

        return True

    def showAboutNWDialog(self, showNotes=False):
        """Show the about dialog for novelWriter.
        """
        dlgAbout = getGuiItem("GuiAbout")
        if dlgAbout is None:
            dlgAbout = GuiAbout(self)
        assert isinstance(dlgAbout, GuiAbout)

        dlgAbout.setModal(True)
        dlgAbout.show()
        dlgAbout.raise_()
        qApp.processEvents()
        dlgAbout.populateGUI()

        if showNotes:
            dlgAbout.showReleaseNotes()

        return True

    def showAboutQtDialog(self):
        """Show the about dialog for Qt.
        """
        msgBox = QMessageBox()
        msgBox.aboutQt(self, "About Qt")
        return True

    def showUpdatesDialog(self):
        """Show the check for updates dialog.
        """
        dlgUpdate = getGuiItem("GuiUpdates")
        if dlgUpdate is None:
            dlgUpdate = GuiUpdates(self)
        assert isinstance(dlgUpdate, GuiUpdates)

        dlgUpdate.setModal(True)
        dlgUpdate.show()
        dlgUpdate.raise_()
        qApp.processEvents()
        dlgUpdate.checkLatest()

        return

    def makeAlert(self, message, level=nwAlert.INFO, exception=None):
        """Alert both the user and the logger at the same time. The
        message can be either a string or a list of strings.
        """
        if isinstance(message, list):
            message = list(filter(None, message))  # Strip empty strings
            popMsg = "<br>".join(message)
            logMsg = " ".join(message)
        else:
            popMsg = str(message)
            logMsg = str(message)

        kw = {}
        if exception is not None:
            kw["exc_info"] = exception
            popMsg = f"{popMsg}<br>{type(exception).__name__}: {str(exception)}"

        # Write to Log
        if level == nwAlert.INFO:
            logger.info(logMsg, **kw)
        elif level == nwAlert.WARN:
            logger.warning(logMsg, **kw)
        elif level == nwAlert.ERROR:
            logger.error(logMsg, **kw)
        elif level == nwAlert.BUG:
            logger.error(logMsg, **kw)

        # Popup
        msgBox = QMessageBox()
        if level == nwAlert.INFO:
            msgBox.information(self, self.tr("Information"), popMsg)
        elif level == nwAlert.WARN:
            msgBox.warning(self, self.tr("Warning"), popMsg)
        elif level == nwAlert.ERROR:
            msgBox.critical(self, self.tr("Error"), popMsg)
        elif level == nwAlert.BUG:
            popMsg += "<br>%s" % self.tr("This is a bug!")
            msgBox.critical(self, self.tr("Internal Error"), popMsg)

        return

    def askQuestion(self, title, question):
        """Ask the user a Yes/No question.
        """
        msgBox = QMessageBox()
        msgRes = msgBox.question(self, title, question, QMessageBox.Yes | QMessageBox.No)
        return msgRes == QMessageBox.Yes

    def reportConfErr(self):
        """Checks if the Config module has any errors to report, and let
        the user know if this is the case. The Config module caches
        errors since it is initialised before the GUI itself.
        """
        if self.mainConf.hasError:
            self.makeAlert(self.mainConf.errorText(), nwAlert.ERROR)
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
            self.mainConf.setOutlinePanePos(self.outlineView.splitSizes())
            if self.viewMeta.isVisible():
                self.mainConf.setViewPanePos(self.splitView.sizes())

        self.mainConf.showRefPanel = self.viewMeta.isVisible()
        if not self.mainConf.isFullScreen:
            self.mainConf.setMainWinSize(self.width(), self.height())

        if self.hasProject:
            self.closeProject(True)

        self.mainConf.saveConfig()
        self.reportConfErr()

        qApp.quit()

        return True

    def switchFocus(self, paneNo):
        """Switch focus between main GUI views.
        """
        if paneNo == nwWidget.TREE:
            tabIdx = self.projStack.currentIndex()
            if tabIdx == self.idxProjView:
                self.projView.setFocus()
            elif tabIdx == self.idxNovelView:
                self.novelView.setTreeFocus()
        elif paneNo == nwWidget.EDITOR:
            self._changeView(nwView.EDITOR)
            self.docEditor.setFocus()
        elif paneNo == nwWidget.VIEWER:
            self._changeView(nwView.EDITOR)
            self.docViewer.setFocus()
        elif paneNo == nwWidget.OUTLINE:
            self._changeView(nwView.OUTLINE)
            self.outlineView.setTreeFocus()
        return

    def closeDocEditor(self):
        """Close the document edit panel. This does not hide the editor.
        """
        self.closeDocument()
        self.theProject.data.setLastHandle(None, "editor")
        return

    def closeDocViewer(self, byUser=True):
        """Close the document view panel.
        """
        self.docViewer.clearViewer()
        if byUser:
            # Only reset the last handle if the user called this
            self.theProject.data.setLastHandle(None, "viewer")

        # Hide the panel
        bPos = self.splitMain.sizes()
        self.splitView.setVisible(False)
        self.splitDocs.setSizes([bPos[1], 0])

        return not self.splitView.isVisible()

    def toggleFocusMode(self):
        """Main GUI Focus Mode hides tree, view, statusbar and menu.
        """
        if self.docEditor.docHandle() is None:
            logger.error("No document open, so not activating Focus Mode")
            return False

        self.isFocusMode = not self.isFocusMode
        if self.isFocusMode:
            logger.debug("Activating Focus Mode")
            self.switchFocus(nwWidget.EDITOR)
        else:
            logger.debug("Deactivating Focus Mode")

        isVisible = not self.isFocusMode
        self.treePane.setVisible(isVisible)
        self.mainStatus.setVisible(isVisible)
        self.mainMenu.setVisible(isVisible)
        self.viewsBar.setVisible(isVisible)

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
        self.addAction(self.mainMenu.aInsSynopsis)

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
        self.addAction(self.mainMenu.aHelpDocs)
        if isinstance(self.mainConf.pdfDocs, Path):
            self.addAction(self.mainMenu.aPdfDocs)

        return True

    def _updateWindowTitle(self, projName=None):
        """Set the window title and add the project's name.
        """
        winTitle = self.mainConf.appName
        if projName is not None:
            winTitle += " - %s" % projName
        self.setWindowTitle(winTitle)
        return True

    def _autoSaveProject(self):
        """Triggered by the autosave project timer to save the project.
        """
        doSave  = self.hasProject
        doSave &= self.theProject.projChanged
        doSave &= self.theProject.storage.isOpen()

        if doSave:
            logger.debug("Autosaving project")
            self.saveProject(autoSave=True)

        return

    def _autoSaveDocument(self):
        """Triggered by the autosave document timer to save the
        document.
        """
        if self.hasProject and self.docEditor.docChanged():
            logger.debug("Autosaving document")
            self.saveDocument()
        return

    def _assembleProjectWizardData(self, newProj):
        """Extract the user choices from the New Project Wizard and
        store them in a dictionary.
        """
        projData = {
            "projName": newProj.field("projName"),
            "projTitle": newProj.field("projTitle"),
            "projAuthor": newProj.field("projAuthor"),
            "projPath": newProj.field("projPath"),
            "popSample": newProj.field("popSample"),
            "popMinimal": newProj.field("popMinimal"),
            "popCustom": newProj.field("popCustom"),
            "addRoots": [],
            "addNotes": False,
            "numChapters": 0,
            "numScenes": 0,
        }
        if newProj.field("popCustom"):
            addRoots = []
            if newProj.field("addPlot"):
                addRoots.append(nwItemClass.PLOT)
            if newProj.field("addChar"):
                addRoots.append(nwItemClass.CHARACTER)
            if newProj.field("addWorld"):
                addRoots.append(nwItemClass.WORLD)
            projData["addRoots"] = addRoots
            projData["addNotes"] = newProj.field("addNotes")
            projData["numChapters"] = newProj.field("numChapters")
            projData["numScenes"] = newProj.field("numScenes")

        return projData

    def _getTagSource(self, tTag):
        """A wrapper function for the index lookup of a tag that will
        display an alert if the tag cannot be found.
        """
        tHandle, sTitle = self.theProject.index.getTagSource(tTag)
        if tHandle is None:
            self.makeAlert(self.tr(
                "Could not find the reference for tag '{0}'. It either doesn't "
                "exist, or the index is out of date. The index can be updated "
                "from the Tools menu, or by pressing {1}."
            ).format(
                tTag, "F9"
            ), nwAlert.ERROR)
            return None, None

        return tHandle, sTitle

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
    #  Private Slots
    ##

    @pyqtSlot(str, Enum)
    def _followTag(self, tTag, tMode):
        """Follow a tag after user interaction with a link.
        """
        tHandle, sTitle = self._getTagSource(tTag)
        if tHandle is not None:
            if tMode == nwDocMode.EDIT:
                self.openDocument(tHandle)
            elif tMode == nwDocMode.VIEW:
                self.viewDocument(tHandle=tHandle, sTitle=sTitle)
        return

    @pyqtSlot(str, Enum, str, bool)
    def _openDocument(self, tHandle, tMode, sTitle, setFocus):
        """Handle an open document request from one of the tree views.
        """
        if tHandle is not None:
            if tMode == nwDocMode.EDIT:
                tLine = None
                hItem = self.theProject.index.getItemHeader(tHandle, sTitle)
                if hItem is not None:
                    tLine = hItem.line
                self.openDocument(tHandle, tLine=tLine, changeFocus=setFocus)
            elif tMode == nwDocMode.VIEW:
                self.viewDocument(tHandle=tHandle, sTitle=sTitle)
        return

    @pyqtSlot(nwView)
    def _changeView(self, view):
        """Handle the requested change of view from the GuiViewBar.
        """
        if view == nwView.EDITOR:
            # Only change the main stack, but not the project stack
            self.mainStack.setCurrentWidget(self.splitMain)

        elif view == nwView.PROJECT:
            self.mainStack.setCurrentWidget(self.splitMain)
            self.projStack.setCurrentWidget(self.projView)

        elif view == nwView.NOVEL:
            self.mainStack.setCurrentWidget(self.splitMain)
            self.projStack.setCurrentWidget(self.novelView)

        elif view == nwView.OUTLINE:
            self.mainStack.setCurrentWidget(self.outlineView)

        return

    @pyqtSlot()
    def _timeTick(self):
        """Triggered on every tick of the main timer.
        """
        if not self.hasProject:
            return

        currTime = time()
        editIdle = currTime - self.docEditor.lastActive() > self.mainConf.userIdleTime
        userIdle = qApp.applicationState() != Qt.ApplicationActive

        if editIdle or userIdle:
            self.idleTime += currTime - self.idleRefTime
            self.mainStatus.setUserIdle(True)
        else:
            self.mainStatus.setUserIdle(False)

        self.idleRefTime = currTime
        self.mainStatus.updateTime(idleTime=self.idleTime)

        return

    @pyqtSlot()
    def _updateStatusWordCount(self):
        """Update the word count on the status bar.
        """
        if not self.hasProject:
            self.mainStatus.setProjectStats(0, 0)

        self.theProject.updateWordCounts()
        if self.mainConf.incNotesWCount:
            iTotal = sum(self.theProject.data.initCounts)
            cTotal = sum(self.theProject.data.currCounts)
            self.mainStatus.setProjectStats(cTotal, cTotal - iTotal)
        else:
            iNovel, _ = self.theProject.data.initCounts
            cNovel, _ = self.theProject.data.currCounts
            self.mainStatus.setProjectStats(cNovel, cNovel - iNovel)

        return

    @pyqtSlot()
    def _keyPressReturn(self):
        """Forward the return/enter keypress to the function that opens
        the currently selected item.
        """
        self.openSelectedItem()
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
    def _mainStackChanged(self, stIndex):
        """Activated when the main window tab is changed.
        """
        if stIndex == self.idxOutlineView:
            if self.hasProject:
                self.outlineView.refreshTree()
        return

    @pyqtSlot(int)
    def _projStackChanged(self, stIndex):
        """Activated when the project view tab is changed.
        """
        sHandle = None
        if stIndex == self.idxProjView:
            sHandle = self.projView.getSelectedHandle()
        elif stIndex == self.idxNovelView:
            sHandle, _ = self.novelView.getSelectedHandle()
        self.itemDetails.updateViewBox(sHandle)
        return

# END Class GuiMain
