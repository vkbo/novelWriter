"""
novelWriter – GUI Main Window
=============================

File History:
Created: 2018-09-22 [0.0.1] GuiMain

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
from __future__ import annotations

import sys
import logging

from time import time
from pathlib import Path
from datetime import datetime

from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QCloseEvent, QCursor, QIcon
from PyQt5.QtWidgets import (
    QDialog, QFileDialog, QHBoxLayout, QMainWindow, QMessageBox, QShortcut,
    QSplitter, QStackedWidget, QVBoxLayout, QWidget, qApp
)

from novelwriter import CONFIG, SHARED, __hexversion__
from novelwriter.gui.theme import GuiTheme
from novelwriter.gui.sidebar import GuiSideBar
from novelwriter.gui.outline import GuiOutlineView
from novelwriter.gui.mainmenu import GuiMainMenu
from novelwriter.gui.projtree import GuiProjectView
from novelwriter.gui.doceditor import GuiDocEditor
from novelwriter.gui.docviewer import GuiDocViewer
from novelwriter.gui.noveltree import GuiNovelView
from novelwriter.gui.statusbar import GuiMainStatus
from novelwriter.gui.itemdetails import GuiItemDetails
from novelwriter.gui.docviewerpanel import GuiDocViewerPanel
from novelwriter.dialogs.about import GuiAbout
from novelwriter.dialogs.updates import GuiUpdates
from novelwriter.dialogs.projload import GuiProjectLoad
from novelwriter.dialogs.wordlist import GuiWordList
from novelwriter.dialogs.preferences import GuiPreferences
from novelwriter.dialogs.projdetails import GuiProjectDetails
from novelwriter.dialogs.projsettings import GuiProjectSettings
from novelwriter.tools.lipsum import GuiLipsum
from novelwriter.tools.manuscript import GuiManuscript
from novelwriter.tools.projwizard import GuiProjectWizard
from novelwriter.tools.dictionaries import GuiDictionaries
from novelwriter.tools.writingstats import GuiWritingStats
from novelwriter.core.coretools import ProjectBuilder

from novelwriter.enum import (
    nwDocAction, nwDocInsert, nwDocMode, nwItemType, nwItemClass, nwWidget, nwView
)
from novelwriter.common import getGuiItem, hexToInt
from novelwriter.constants import nwFiles

logger = logging.getLogger(__name__)


class GuiMain(QMainWindow):
    """Main GUI Window

    The Main GUI window class. It is the entry point of the
    application, and holds all runtime objects aside from the main
    Config instance, which is created before the Main GUI.

    The Main GUI is split up into GUI components, assembled in the init
    function. Also, the project instance and theme instance are created
    here. These should be passed around to all other objects who need
    them and new instances of them should generally not be created.

      * All other GUI classes that depend on any components from the
        main GUI should be passed a reference to the instance of this
        class.
      * All non-GUI classes can be passed a reference to the NWProject
        instance if the Main GUI is not needed (which it generally
        shouldn't need).
    """

    def __init__(self) -> None:
        super().__init__()

        logger.debug("Create: GUI")
        self.setObjectName("GuiMain")

        # System Info
        # ===========

        logger.info("OS: %s", CONFIG.osType)
        logger.info("Kernel: %s", CONFIG.kernelVer)
        logger.info("Host: %s", CONFIG.hostName)
        logger.info("Qt5: %s (0x%06x)", CONFIG.verQtString, CONFIG.verQtValue)
        logger.info("PyQt5: %s (0x%06x)", CONFIG.verPyQtString, CONFIG.verPyQtValue)
        logger.info("Python: %s (0x%08x)", CONFIG.verPyString, sys.hexversion)
        logger.info("GUI Language: %s", CONFIG.guiLocale)

        # Core Classes
        # ============

        # Initialise UserData Instance
        SHARED.initSharedData(self, GuiTheme())

        # Core Settings
        self.isFocusMode = False

        # Prepare Main Window
        self.resize(*CONFIG.mainWinSize)
        self._updateWindowTitle()

        nwIcon = CONFIG.assetPath("icons") / "novelwriter.svg"
        self.nwIcon = QIcon(str(nwIcon)) if nwIcon.is_file() else QIcon()
        self.setWindowIcon(self.nwIcon)
        qApp.setWindowIcon(self.nwIcon)

        # Build the GUI
        # =============

        # Sizes
        mPx = CONFIG.pxInt(4)
        hWd = CONFIG.pxInt(4)

        # Main GUI Elements
        self.mainStatus     = GuiMainStatus(self)
        self.projView       = GuiProjectView(self)
        self.novelView      = GuiNovelView(self)
        self.docEditor      = GuiDocEditor(self)
        self.docViewer      = GuiDocViewer(self)
        self.docViewerPanel = GuiDocViewerPanel(self)
        self.itemDetails    = GuiItemDetails(self)
        self.outlineView    = GuiOutlineView(self)
        self.mainMenu       = GuiMainMenu(self)
        self.sideBar        = GuiSideBar(self)

        # Project Tree Stack
        self.projStack = QStackedWidget(self)
        self.projStack.addWidget(self.projView)
        self.projStack.addWidget(self.novelView)
        self.projStack.currentChanged.connect(self._projStackChanged)

        # Project Tree View
        self.treePane = QWidget(self)
        self.treeBox = QVBoxLayout()
        self.treeBox.setContentsMargins(0, 0, 0, 0)
        self.treeBox.setSpacing(mPx)
        self.treeBox.addWidget(self.projStack)
        self.treeBox.addWidget(self.itemDetails)
        self.treePane.setLayout(self.treeBox)

        # Splitter : Document Viewer / Document Meta
        self.splitView = QSplitter(Qt.Vertical, self)
        self.splitView.addWidget(self.docViewer)
        self.splitView.addWidget(self.docViewerPanel)
        self.splitView.setHandleWidth(hWd)
        self.splitView.setOpaqueResize(False)
        self.splitView.setSizes(CONFIG.viewPanePos)

        # Splitter : Document Editor / Document Viewer
        self.splitDocs = QSplitter(Qt.Horizontal, self)
        self.splitDocs.addWidget(self.docEditor)
        self.splitDocs.addWidget(self.splitView)
        self.splitDocs.setOpaqueResize(False)
        self.splitDocs.setHandleWidth(hWd)

        # Splitter : Project Tree / Document Area
        self.splitMain = QSplitter(Qt.Horizontal)
        self.splitMain.setContentsMargins(0, 0, 0, 0)
        self.splitMain.addWidget(self.treePane)
        self.splitMain.addWidget(self.splitDocs)
        self.splitMain.setOpaqueResize(False)
        self.splitMain.setHandleWidth(hWd)
        self.splitMain.setSizes(CONFIG.mainPanePos)

        # Main Stack : Editor / Outline
        self.mainStack = QStackedWidget(self)
        self.mainStack.addWidget(self.splitMain)
        self.mainStack.addWidget(self.outlineView)
        self.mainStack.currentChanged.connect(self._mainStackChanged)

        # Indices of Splitter Widgets
        self.idxTree         = self.splitMain.indexOf(self.treePane)
        self.idxMain         = self.splitMain.indexOf(self.splitDocs)
        self.idxEditor       = self.splitDocs.indexOf(self.docEditor)
        self.idxViewer       = self.splitDocs.indexOf(self.splitView)
        self.idxViewDoc      = self.splitView.indexOf(self.docViewer)
        self.idxViewDocPanel = self.splitView.indexOf(self.docViewerPanel)

        # Indices of Stack Widgets
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
        self.splitView.setCollapsible(self.idxViewDocPanel, False)

        self.splitMain.setStretchFactor(self.idxTree, 0)
        self.splitMain.setStretchFactor(self.idxMain, 1)

        # Editor / Viewer Default State
        self.splitView.setVisible(False)
        self.docEditor.closeSearch()

        # Initialise the Project Tree
        self.rebuildTrees()

        # Assemble Main Window Elements
        self.mainBox = QHBoxLayout()
        self.mainBox.addWidget(self.sideBar)
        self.mainBox.addWidget(self.mainStack)
        self.mainBox.setContentsMargins(0, 0, 0, 0)
        self.mainBox.setSpacing(0)

        self.mainWidget = QWidget(self)
        self.mainWidget.setLayout(self.mainBox)

        self.setMenuBar(self.mainMenu)
        self.setCentralWidget(self.mainWidget)
        self.setStatusBar(self.mainStatus)
        self.setContextMenuPolicy(Qt.NoContextMenu)  # Issue #1147

        # Connect Signals
        # ===============

        SHARED.projectStatusChanged.connect(self.mainStatus.updateProjectStatus)
        SHARED.projectStatusMessage.connect(self.mainStatus.setStatusMessage)
        SHARED.spellLanguageChanged.connect(self.mainStatus.setLanguage)
        SHARED.indexChangedTags.connect(self.docViewerPanel.updateChangedTags)
        SHARED.indexScannedText.connect(self.docViewerPanel.projectItemChanged)
        SHARED.indexScannedText.connect(self.projView.updateItemValues)
        SHARED.indexScannedText.connect(self.itemDetails.updateViewBox)
        SHARED.indexCleared.connect(self.docViewerPanel.indexWasCleared)
        SHARED.indexAvailable.connect(self.docViewerPanel.indexHasAppeared)

        self.mainMenu.requestDocAction.connect(self._passDocumentAction)
        self.mainMenu.requestDocInsert.connect(self._passDocumentInsert)
        self.mainMenu.requestDocInsertText.connect(self._passDocumentInsert)
        self.mainMenu.requestDocKeyWordInsert.connect(self.docEditor.insertKeyWord)
        self.mainMenu.requestFocusChange.connect(self.switchFocus)

        self.sideBar.viewChangeRequested.connect(self._changeView)

        self.projView.selectedItemChanged.connect(self.itemDetails.updateViewBox)
        self.projView.openDocumentRequest.connect(self._openDocument)
        self.projView.wordCountsChanged.connect(self._updateStatusWordCount)
        self.projView.treeItemChanged.connect(self.docEditor.updateDocInfo)
        self.projView.treeItemChanged.connect(self.docViewer.updateDocInfo)
        self.projView.treeItemChanged.connect(self.itemDetails.updateViewBox)
        self.projView.treeItemChanged.connect(self.docViewerPanel.projectItemChanged)
        self.projView.rootFolderChanged.connect(self.outlineView.updateRootItem)
        self.projView.rootFolderChanged.connect(self.novelView.updateRootItem)
        self.projView.rootFolderChanged.connect(self.projView.updateRootItem)
        self.projView.projectSettingsRequest.connect(self.showProjectSettingsDialog)

        self.novelView.selectedItemChanged.connect(self.itemDetails.updateViewBox)
        self.novelView.openDocumentRequest.connect(self._openDocument)

        self.docEditor.editedStatusChanged.connect(self.mainStatus.updateDocumentStatus)
        self.docEditor.docCountsChanged.connect(self.itemDetails.updateCounts)
        self.docEditor.docCountsChanged.connect(self.projView.updateCounts)
        self.docEditor.loadDocumentTagRequest.connect(self._followTag)
        self.docEditor.novelStructureChanged.connect(self.novelView.refreshTree)
        self.docEditor.novelItemMetaChanged.connect(self.novelView.updateNovelItemMeta)
        self.docEditor.statusMessage.connect(self.mainStatus.setStatusMessage)
        self.docEditor.spellCheckStateChanged.connect(self.mainMenu.setSpellCheckState)
        self.docEditor.closeDocumentRequest.connect(self.closeDocEditor)
        self.docEditor.toggleFocusModeRequest.connect(self.toggleFocusMode)

        self.docViewer.documentLoaded.connect(self.docViewerPanel.updateHandle)
        self.docViewer.loadDocumentTagRequest.connect(self._followTag)
        self.docViewer.togglePanelVisibility.connect(self._toggleViewerPanelVisibility)

        self.docViewerPanel.loadDocumentTagRequest.connect(self._followTag)
        self.docViewerPanel.openDocumentRequest.connect(self._openDocument)

        self.outlineView.loadDocumentTagRequest.connect(self._followTag)
        self.outlineView.openDocumentRequest.connect(self._openDocument)

        # Finalise Initialisation
        # =======================

        # Set Up Auto-Save Project Timer
        self.asProjTimer = QTimer(self)
        self.asProjTimer.timeout.connect(self._autoSaveProject)

        # Set Up Auto-Save Document Timer
        self.asDocTimer = QTimer(self)
        self.asDocTimer.timeout.connect(self._autoSaveDocument)

        # Main Clock
        self.mainTimer = QTimer(self)
        self.mainTimer.setInterval(1000)
        self.mainTimer.timeout.connect(self._timeTick)
        self.mainTimer.start()

        # Shortcuts and Actions
        self._connectMenuActions()

        self.keyReturn = QShortcut(self)
        self.keyReturn.setKey(Qt.Key.Key_Return)
        self.keyReturn.activated.connect(self._keyPressReturn)

        self.keyEnter = QShortcut(self)
        self.keyEnter.setKey(Qt.Key.Key_Enter)
        self.keyEnter.activated.connect(self._keyPressReturn)

        self.keyEscape = QShortcut(self)
        self.keyEscape.setKey(Qt.Key.Key_Escape)
        self.keyEscape.activated.connect(self._keyPressEscape)

        # Check that config loaded fine
        self.reportConfErr()

        # Initialise Main GUI
        self.initMain()
        self.asProjTimer.start()
        self.asDocTimer.start()
        self.mainStatus.clearStatus()

        # Handle Windows Mode
        self.showNormal()

        logger.debug("Ready: GUI")

        if __hexversion__[-2] == "a" and not CONFIG.isDebug:
            SHARED.warn(self.tr(
                "You are running an untested development version of novelWriter. "
                "Please be careful when working on a live project "
                "and make sure you take regular backups."
            ))

        logger.info("novelWriter is ready ...")
        self.mainStatus.setStatusMessage(self.tr("novelWriter is ready ..."))

        return

    def initMain(self) -> None:
        """Initialise elements that depend on user settings."""
        self.asProjTimer.setInterval(int(CONFIG.autoSaveProj*1000))
        self.asDocTimer.setInterval(int(CONFIG.autoSaveDoc*1000))
        return

    def postLaunchTasks(self, cmdOpen: str | None) -> None:
        """Process tasks after the main window has been created."""
        if cmdOpen:
            qApp.processEvents()
            logger.info("Command line path: %s", cmdOpen)
            self.openProject(cmdOpen)

        if not SHARED.hasProject:
            self.showProjectLoadDialog()

        # Determine whether release notes need to be shown or not
        if hexToInt(CONFIG.lastNotes) < hexToInt(__hexversion__):
            CONFIG.lastNotes = __hexversion__
            self.showAboutNWDialog(showNotes=True)

        return

    ##
    #  Project Actions
    ##

    def newProject(self, projData: dict | None = None) -> bool:
        """Create a new project via the new project wizard."""
        if SHARED.hasProject:
            if not self.closeProject():
                SHARED.error(self.tr(
                    "Cannot create a new project when another project is open."
                ))
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
            SHARED.error(self.tr(
                "A project already exists in that location. "
                "Please choose another folder."
            ))
            return False

        logger.info("Creating new project")
        nwProject = ProjectBuilder()
        if nwProject.buildProject(projData):
            self.openProject(projPath)
        else:
            return False

        return True

    def closeProject(self, isYes: bool = False) -> bool:
        """Close the project if one is open. isYes is passed on from the
        close application event so the user doesn't get prompted twice
        to confirm.
        """
        if not SHARED.hasProject:
            # There is no project loaded, everything OK
            return True

        if not isYes:
            msgYes = SHARED.question("%s<br>%s" % (
                self.tr("Close the current project?"),
                self.tr("Changes are saved automatically.")
            ))
            if not msgYes:
                return False

        if self.docEditor.docChanged:
            self.saveDocument()

        saveOK = self.saveProject()
        doBackup = False
        if SHARED.project.data.doBackup and CONFIG.backupOnClose:
            doBackup = True
            if CONFIG.askBeforeBackup:
                doBackup = SHARED.question(self.tr("Backup the current project?"))

        if doBackup:
            SHARED.project.backupProject(False)

        if saveOK:
            self.closeDocument()
            self.docViewer.clearNavHistory()
            self.closeDocViewer(byUser=False)

            self.outlineView.closeProjectTasks()
            self.novelView.closeProjectTasks()
            self.projView.clearProjectView()
            self.itemDetails.clearDetails()
            self.mainStatus.clearStatus()

            SHARED.closeProject()

            self._updateWindowTitle()
            self._changeView(nwView.PROJECT)

        return saveOK

    def openProject(self, projFile: str | Path | None) -> bool:
        """Open a project from a projFile path."""
        if projFile is None:
            return False

        # Make sure any open project is cleared out first before we load
        # another one
        if not self.closeProject():
            return False

        # Switch main tab to editor view
        self._changeView(nwView.PROJECT)

        # Try to open the project
        tStart = time()
        if not SHARED.openProject(projFile):
            # The project open failed.
            lockStatus = SHARED.projectLock
            if lockStatus is None:
                # The project is not locked, so failed for some other
                # reason handled by the project class.
                return False

            lockText = self.tr(
                "The project is already open by another instance of "
                "novelWriter, and is therefore locked. Override lock "
                "and continue anyway?"
            )
            lockInfo = self.tr(
                "Note: If the program or the computer previously "
                "crashed, the lock can safely be overridden. However, "
                "overriding it is not recommended if the project is "
                "open in another instance of novelWriter. Doing so "
                "may corrupt the project."
            )
            try:
                lockDetails = self.tr(
                    "The project was locked by the computer "
                    "'{0}' ({1} {2}), last active on {3}."
                ).format(
                    lockStatus[0], lockStatus[1], lockStatus[2],
                    datetime.fromtimestamp(int(lockStatus[3])).strftime("%x %X")
                )
            except Exception:
                lockDetails = ""

            if SHARED.question(lockText, info=lockInfo, details=lockDetails, warn=True):
                if not SHARED.openProject(projFile, clearLock=True):
                    return False
            else:
                return False

        # Update GUI
        self._updateWindowTitle(SHARED.project.data.name)
        self.rebuildTrees()
        self.docEditor.toggleSpellCheck(SHARED.project.data.spellCheck)
        self.mainStatus.setRefTime(SHARED.project.projOpened)
        self.projView.openProjectTasks()
        self.novelView.openProjectTasks()
        self.outlineView.openProjectTasks()
        self._updateStatusWordCount()

        # Restore previously open documents, if any
        # If none was recorded, open the first document found
        lastEdited = SHARED.project.data.getLastHandle("editor")
        if lastEdited is None:
            for nwItem in SHARED.project.tree:
                if nwItem and nwItem.isFileType():
                    lastEdited = nwItem.itemHandle
                    break

        if lastEdited is not None:
            qApp.processEvents()
            self.openDocument(lastEdited, doScroll=True)

        lastViewed = SHARED.project.data.getLastHandle("viewer")
        if lastViewed is not None:
            qApp.processEvents()
            self.viewDocument(lastViewed)

        # Check if we need to rebuild the index
        if SHARED.project.index.indexBroken:
            SHARED.info(self.tr("The project index is outdated or broken. Rebuilding index."))
            self.rebuildIndex()

        # Make sure the changed status is set to false on things opened
        qApp.processEvents()
        self.docEditor.setDocumentChanged(False)
        SHARED.project.setProjectChanged(False)

        logger.debug("Project loaded in %.3f ms", (time() - tStart)*1000)

        return True

    def saveProject(self, autoSave: bool = False) -> bool:
        """Save the current project."""
        if not SHARED.hasProject:
            logger.error("No project open")
            return False
        self.projView.saveProjectTasks()
        return SHARED.saveProject(autoSave=autoSave)

    ##
    #  Document Actions
    ##

    def closeDocument(self, beforeOpen: bool = False) -> bool:
        """Close the document and clear the editor and title field."""
        if not SHARED.hasProject:
            logger.error("No project open")
            return False

        # Disable focus mode if it is active
        if self.isFocusMode:
            self.toggleFocusMode()

        self.docEditor.saveCursorPosition()
        if self.docEditor.docChanged:
            self.saveDocument()
        self.docEditor.clearEditor()
        if not beforeOpen:
            self.novelView.setActiveHandle(None)

        return True

    def openDocument(self, tHandle: str | None, tLine: int | None = None,
                     changeFocus: bool = True, doScroll: bool = False) -> bool:
        """Open a specific document, optionally at a given line."""
        if not SHARED.hasProject:
            logger.error("No project open")
            return False

        if not tHandle or not SHARED.project.tree.checkType(tHandle, nwItemType.FILE):
            logger.debug("Requested item '%s' is not a document", tHandle)
            return False

        self._changeView(nwView.EDITOR)
        cHandle = self.docEditor.docHandle
        if cHandle == tHandle:
            self.docEditor.setCursorLine(tLine)
            if changeFocus:
                self.docEditor.setFocus()
            return True

        self.closeDocument(beforeOpen=True)
        if self.docEditor.loadText(tHandle, tLine):
            SHARED.project.data.setLastHandle(tHandle, "editor")
            self.projView.setSelectedHandle(tHandle, doScroll=doScroll)
            self.novelView.setActiveHandle(tHandle)
            if changeFocus:
                self.docEditor.setFocus()
        else:
            return False

        return True

    def openNextDocument(self, tHandle: str, wrapAround: bool = False) -> bool:
        """Open the next document in the project tree, following the
        document with the given handle. Stop when reaching the end.
        """
        if not SHARED.hasProject:
            logger.error("No project open")
            return False

        nHandle = None   # The next handle after tHandle
        fHandle = None   # The first file handle we encounter
        foundIt = False  # We've found tHandle, pick the next we see
        for tItem in SHARED.project.tree:
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
            self.openDocument(nHandle, tLine=1, doScroll=True)
            return True
        elif wrapAround:
            self.openDocument(fHandle, tLine=1, doScroll=True)
            return False

        return False

    def saveDocument(self) -> bool:
        """Save the current documents."""
        if not SHARED.hasProject:
            logger.error("No project open")
            return False
        self.docEditor.saveText()
        return True

    def viewDocument(self, tHandle: str | None = None, sTitle: str | None = None) -> bool:
        """Load a document for viewing in the view panel."""
        if not SHARED.hasProject:
            logger.error("No project open")
            return False

        if tHandle is None:
            logger.debug("Viewing document, but no handle provided")

            if self.docEditor.hasFocus():
                tHandle = self.docEditor.docHandle

            if tHandle is not None:
                self.saveDocument()
            else:
                tHandle = self.projView.getSelectedHandle()

            if tHandle is None:
                tHandle = SHARED.project.data.getLastHandle("viewer")

            if tHandle is None:
                logger.debug("No document to view, giving up")
                return False

        # Make sure main tab is in Editor view
        self._changeView(nwView.EDITOR)

        logger.debug("Viewing document with handle '%s'", tHandle)
        if self.docViewer.loadText(tHandle):
            if not self.splitView.isVisible():
                cursorVisible = self.docEditor.cursorIsVisible()
                bPos = self.splitMain.sizes()
                self.splitView.setVisible(True)
                vPos = [0, 0]
                vPos[0] = int(bPos[1]/2)
                vPos[1] = bPos[1] - vPos[0]
                self.splitDocs.setSizes(vPos)
                self.docViewerPanel.setVisible(CONFIG.showViewerPanel)

                # Since editor width changes, we need to make sure we
                # restore cursor visibility in the editor. See #1302
                if cursorVisible:
                    self.docEditor.ensureCursorVisibleNoCentre()

            if sTitle:
                self.docViewer.navigateTo(f"#{sTitle}")

        return True

    def importDocument(self) -> bool:
        """Import the text contained in an out-of-project text file, and
        insert the text into the currently open document.
        """
        if not SHARED.hasProject:
            logger.error("No project open")
            return False

        lastPath = CONFIG.lastPath()
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
            CONFIG.setLastPath(loadFile)
        except Exception as exc:
            SHARED.error(self.tr(
                "Could not read file. The file must be an existing text file."
            ), exc=exc)
            return False

        if self.docEditor.docHandle is None:
            SHARED.error(self.tr(
                "Please open a document to import the text file into."
            ))
            return False

        if not self.docEditor.isEmpty:
            msgYes = SHARED.question(self.tr(
                "Importing the file will overwrite the current content of "
                "the document. Do you want to proceed?"
            ))
            if not msgYes:
                return False

        self.docEditor.replaceText(theText)

        return True

    ##
    #  Tree Item Actions
    ##

    def openSelectedItem(self) -> bool:
        """Open the selected item from the tree that is currently
        active. It is not checked that the item is actually a document.
        That should be handled by the openDocument function.
        """
        if not SHARED.hasProject:
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
            hItem = SHARED.project.index.getItemHeader(tHandle, sTitle)
            if hItem is not None:
                tLine = hItem.line

        if tHandle is not None:
            self.openDocument(tHandle, tLine=tLine, changeFocus=False, doScroll=False)

        return True

    def editItemLabel(self, tHandle: str | None = None) -> bool:
        """Open the edit item dialog."""
        if not SHARED.hasProject:
            logger.error("No project open")
            return False
        if tHandle is None and (self.docEditor.anyFocus() or self.isFocusMode):
            tHandle = self.docEditor.docHandle
        self.projView.renameTreeItem(tHandle)
        return True

    def rebuildTrees(self) -> None:
        """Rebuild the project tree."""
        self.projView.populateTree()
        return

    def rebuildIndex(self, beQuiet: bool = False) -> bool:
        """Rebuild the entire index."""
        if not SHARED.hasProject:
            logger.error("No project open")
            return False

        logger.info("Rebuilding index ...")
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        tStart = time()

        self.projView.saveProjectTasks()
        SHARED.project.index.rebuildIndex()
        self.projView.populateTree()
        self.novelView.refreshTree()

        tEnd = time()
        self.mainStatus.setStatusMessage(
            self.tr("Indexing completed in {0} ms").format(f"{(tEnd - tStart)*1000.0:.1f}")
        )
        self.docEditor.updateTagHighLighting()
        self._updateStatusWordCount()
        qApp.restoreOverrideCursor()

        if not beQuiet:
            SHARED.info(self.tr("The project index has been successfully rebuilt."))

        return True

    ##
    #  Main Dialogs
    ##

    def showProjectLoadDialog(self) -> None:
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

        return

    def showNewProjectDialog(self) -> dict | None:
        """Open the wizard and assemble a project options dict."""
        newProj = GuiProjectWizard(self)
        newProj.exec_()

        if newProj.result() == QDialog.Accepted:
            return self._assembleProjectWizardData(newProj)

        return None

    def showPreferencesDialog(self) -> None:
        """Open the preferences dialog."""
        dlgConf = GuiPreferences(self)
        dlgConf.exec_()

        if dlgConf.result() == QDialog.Accepted:
            logger.debug("Applying new preferences")
            self.initMain()
            self.saveDocument()

            if dlgConf.needsRestart:
                SHARED.info(self.tr(
                    "Some changes will not be applied until novelWriter has been restarted."
                ))

            if dlgConf.refreshTree:
                self.projView.populateTree()

            if dlgConf.updateTheme:
                # We are doing this manually instead of connecting to
                # qApp.paletteChanged since the processing order matters
                SHARED.theme.loadTheme()
                self.docEditor.updateTheme()
                self.docViewer.updateTheme()
                self.docViewerPanel.updateTheme()
                self.sideBar.updateTheme()
                self.projView.updateTheme()
                self.novelView.updateTheme()
                self.outlineView.updateTheme()
                self.itemDetails.updateTheme()
                self.mainStatus.updateTheme()

            if dlgConf.updateSyntax:
                SHARED.theme.loadSyntax()
                self.docEditor.updateSyntaxColours()

            self.docEditor.initEditor()
            self.docViewer.initViewer()
            self.projView.initSettings()
            self.novelView.initSettings()
            self.outlineView.initSettings()

            self._updateStatusWordCount()

        return

    @pyqtSlot(int)
    def showProjectSettingsDialog(self, focusTab: int = GuiProjectSettings.TAB_MAIN) -> bool:
        """Open the project settings dialog."""
        if not SHARED.hasProject:
            logger.error("No project open")
            return False

        dlgProj = GuiProjectSettings(self, focusTab=focusTab)
        dlgProj.exec_()

        if dlgProj.result() == QDialog.Accepted:
            logger.debug("Applying new project settings")
            SHARED.updateSpellCheckLanguage()
            self.itemDetails.refreshDetails()
            self._updateWindowTitle(SHARED.project.data.name)

        return True

    def showProjectDetailsDialog(self) -> bool:
        """Open the project details dialog."""
        if not SHARED.hasProject:
            logger.error("No project open")
            return False

        dlgDetails = getGuiItem("GuiProjectDetails")
        if dlgDetails is None:
            dlgDetails = GuiProjectDetails(self)
        assert isinstance(dlgDetails, GuiProjectDetails)

        dlgDetails.setModal(True)
        dlgDetails.show()
        dlgDetails.raise_()
        dlgDetails.updateValues()

        return True

    @pyqtSlot()
    def showBuildManuscriptDialog(self) -> bool:
        """Open the build manuscript dialog."""
        if not SHARED.hasProject:
            logger.error("No project open")
            return False

        dlgBuild = getGuiItem("GuiManuscript")
        if dlgBuild is None:
            dlgBuild = GuiManuscript(self)
        assert isinstance(dlgBuild, GuiManuscript)

        dlgBuild.setModal(False)
        dlgBuild.show()
        dlgBuild.raise_()
        qApp.processEvents()

        dlgBuild.loadContent()

        return True

    def showLoremIpsumDialog(self) -> bool:
        """Open the insert lorem ipsum text dialog."""
        if not SHARED.hasProject:
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

    def showProjectWordListDialog(self) -> bool:
        """Open the project word list dialog."""
        if not SHARED.hasProject:
            logger.error("No project open")
            return False

        dlgWords = GuiWordList(self)
        dlgWords.exec_()

        if dlgWords.result() == QDialog.Accepted:
            logger.debug("Reloading word list")
            SHARED.updateSpellCheckLanguage(reload=True)
            self.docEditor.spellCheckDocument()

        return True

    def showWritingStatsDialog(self) -> bool:
        """Open the session stats dialog."""
        if not SHARED.hasProject:
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

    def showAboutNWDialog(self, showNotes: bool = False) -> bool:
        """Show the about dialog for novelWriter."""
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

    def showAboutQtDialog(self) -> None:
        """Show the about dialog for Qt."""
        msgBox = QMessageBox(self)
        msgBox.aboutQt(self, "About Qt")
        return

    def showUpdatesDialog(self) -> None:
        """Show the check for updates dialog."""
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

    @pyqtSlot()
    def showDictionariesDialog(self) -> None:
        """Show the download dictionaries dialog."""
        dlgDicts = GuiDictionaries(self)
        dlgDicts.setModal(True)
        dlgDicts.show()
        dlgDicts.raise_()
        qApp.processEvents()
        if not dlgDicts.initDialog():
            dlgDicts.close()
            SHARED.error(self.tr("Could not initialise the dialog."))

        return

    def reportConfErr(self) -> bool:
        """Checks if the Config module has any errors to report, and let
        the user know if this is the case. The Config module caches
        errors since it is initialised before the GUI itself.
        """
        if CONFIG.hasError:
            SHARED.error(CONFIG.errorText())
            return True
        return False

    ##
    #  Main Window Actions
    ##

    def closeMain(self) -> bool:
        """Save everything, and close novelWriter."""
        if SHARED.hasProject:
            msgYes = SHARED.question("%s<br>%s" % (
                self.tr("Do you want to exit novelWriter?"),
                self.tr("Changes are saved automatically.")
            ))
            if not msgYes:
                return False

        logger.info("Exiting novelWriter")

        if not self.isFocusMode:
            CONFIG.setMainPanePos(self.splitMain.sizes())
            CONFIG.setOutlinePanePos(self.outlineView.splitSizes())
            if self.docViewerPanel.isVisible():
                CONFIG.setViewPanePos(self.splitView.sizes())

        CONFIG.showViewerPanel = self.docViewerPanel.isVisible()
        if self.windowState() & Qt.WindowFullScreen != Qt.WindowFullScreen:
            # Ignore window size if in full screen mode
            CONFIG.setMainWinSize(self.width(), self.height())

        if SHARED.hasProject:
            self.closeProject(True)

        CONFIG.saveConfig()
        self.reportConfErr()

        qApp.quit()

        return True

    def closeDocViewer(self, byUser: bool = True) -> bool:
        """Close the document view panel."""
        self.docViewer.clearViewer()
        if byUser:
            # Only reset the last handle if the user called this
            SHARED.project.data.setLastHandle(None, "viewer")

        cursorVisible = self.docEditor.cursorIsVisible()

        # Hide the panel
        bPos = self.splitMain.sizes()
        self.splitView.setVisible(False)
        self.splitDocs.setSizes([bPos[1], 0])

        # Since editor width changes, we need to make sure we restore
        # cursor visibility in the editor. See #1302
        if cursorVisible:
            self.docEditor.ensureCursorVisibleNoCentre()

        return not self.splitView.isVisible()

    def toggleFullScreenMode(self) -> None:
        """Toggle full screen mode"""
        self.setWindowState(self.windowState() ^ Qt.WindowFullScreen)
        return

    ##
    #  Events
    ##

    def closeEvent(self, event: QCloseEvent):
        """Capture the closing event of the GUI and call the close
        function to handle all the close process steps.
        """
        if self.closeMain():
            event.accept()
        else:
            event.ignore()
        return

    ##
    #  Public Slots
    ##

    @pyqtSlot()
    def closeDocEditor(self) -> None:
        """Close the document editor. This does not hide the editor."""
        self.closeDocument()
        SHARED.project.data.setLastHandle(None, "editor")
        return

    @pyqtSlot()
    def toggleFocusMode(self) -> None:
        """Handle toggle focus mode. The Main GUI Focus Mode hides tree,
        view, statusbar and menu.
        """
        if self.docEditor.docHandle is None:
            logger.error("No document open, so not activating Focus Mode")
            return

        self.isFocusMode = not self.isFocusMode
        if self.isFocusMode:
            logger.debug("Activating Focus Mode")
            self.switchFocus(nwWidget.EDITOR)
        else:
            logger.debug("Deactivating Focus Mode")

        cursorVisible = self.docEditor.cursorIsVisible()
        isVisible = not self.isFocusMode
        self.treePane.setVisible(isVisible)
        self.mainStatus.setVisible(isVisible)
        self.mainMenu.setVisible(isVisible)
        self.sideBar.setVisible(isVisible)

        hideDocFooter = self.isFocusMode and CONFIG.hideFocusFooter
        self.docEditor.docFooter.setVisible(not hideDocFooter)
        self.docEditor.docHeader.updateFocusMode()

        if self.splitView.isVisible():
            self.splitView.setVisible(False)
        elif self.docViewer.docHandle is not None:
            self.splitView.setVisible(True)

        if cursorVisible:
            self.docEditor.ensureCursorVisibleNoCentre()

        return

    @pyqtSlot(nwWidget)
    def switchFocus(self, paneNo: nwWidget) -> None:
        """Switch focus between main GUI views."""
        if paneNo == nwWidget.TREE:
            if self.projStack.currentWidget() is self.projView:
                if self.projView.treeHasFocus():
                    self._changeView(nwView.NOVEL)
                    self.novelView.setTreeFocus()
                else:
                    self.projView.setTreeFocus()
            else:
                if self.novelView.treeHasFocus():
                    self._changeView(nwView.PROJECT)
                    self.projView.setTreeFocus()
                else:
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

    ##
    #  Private Slots
    ##

    @pyqtSlot(str, nwDocMode)
    def _followTag(self, tag: str, mode: nwDocMode) -> None:
        """Follow a tag after user interaction with a link."""
        tHandle, sTitle = self._getTagSource(tag)
        if tHandle is not None:
            if mode == nwDocMode.EDIT:
                self.openDocument(tHandle)
            elif mode == nwDocMode.VIEW:
                self.viewDocument(tHandle=tHandle, sTitle=sTitle)
        return

    @pyqtSlot(str, nwDocMode, str, bool)
    def _openDocument(self, tHandle: str, mode: nwDocMode, sTitle: str, setFocus: bool) -> None:
        """Handle an open document request."""
        if tHandle is not None:
            if mode == nwDocMode.EDIT:
                tLine = None
                hItem = SHARED.project.index.getItemHeader(tHandle, sTitle)
                if hItem is not None:
                    tLine = hItem.line
                self.openDocument(tHandle, tLine=tLine, changeFocus=setFocus)
            elif mode == nwDocMode.VIEW:
                self.viewDocument(tHandle=tHandle, sTitle=sTitle)
        return

    @pyqtSlot(nwView)
    def _changeView(self, view: nwView) -> None:
        """Handle the requested change of view from the GuiViewBar."""
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

    @pyqtSlot(nwDocAction)
    def _passDocumentAction(self, action: nwDocAction) -> None:
        """Pass on a document action to the document viewer if it has
        focus, or pass it to the document editor if it or any of its
        child widgets have focus. If neither has focus, ignore it.
        """
        if self.docViewer.hasFocus():
            self.docViewer.docAction(action)
        elif self.docEditor.hasFocus():
            self.docEditor.docAction(action)
        else:
            logger.debug("Action cancelled as neither editor nor viewer has focus")
        return

    @pyqtSlot(str)
    @pyqtSlot(nwDocInsert)
    def _passDocumentInsert(self, content: str | nwDocInsert) -> None:
        """Pass on a document insert action to the document editor if it
        has focus. If not, ignore it.
        """
        if self.docEditor.hasFocus():
            self.docEditor.insertText(content)
        return

    @pyqtSlot()
    def _toggleViewerPanelVisibility(self):
        """Toggle the visibility of the document viewer panel."""
        CONFIG.showViewerPanel = not CONFIG.showViewerPanel
        self.docViewerPanel.setVisible(CONFIG.showViewerPanel)
        return

    @pyqtSlot()
    def _timeTick(self) -> None:
        """Process time tick of the main timer."""
        if not SHARED.hasProject:
            return
        currTime = time()
        editIdle = currTime - self.docEditor.lastActive > CONFIG.userIdleTime
        userIdle = qApp.applicationState() != Qt.ApplicationActive
        self.mainStatus.setUserIdle(editIdle or userIdle)
        SHARED.updateIdleTime(currTime, editIdle or userIdle)
        self.mainStatus.updateTime(idleTime=SHARED.projectIdleTime)
        return

    @pyqtSlot()
    def _autoSaveProject(self) -> None:
        """Autosave of the project. This is a timer-activated slot."""
        doSave  = SHARED.hasProject
        doSave &= SHARED.project.projChanged
        doSave &= SHARED.project.storage.isOpen()
        if doSave:
            logger.debug("Autosaving project")
            self.saveProject(autoSave=True)
        return

    @pyqtSlot()
    def _autoSaveDocument(self) -> None:
        """Autosave of the document. This is a timer-activated slot."""
        if SHARED.hasProject and self.docEditor.docChanged:
            logger.debug("Autosaving document")
            self.saveDocument()
        return

    @pyqtSlot()
    def _updateStatusWordCount(self) -> None:
        """Update the word count on the status bar."""
        if not SHARED.hasProject:
            self.mainStatus.setProjectStats(0, 0)

        SHARED.project.updateWordCounts()
        if CONFIG.incNotesWCount:
            iTotal = sum(SHARED.project.data.initCounts)
            cTotal = sum(SHARED.project.data.currCounts)
            self.mainStatus.setProjectStats(cTotal, cTotal - iTotal)
        else:
            iNovel, _ = SHARED.project.data.initCounts
            cNovel, _ = SHARED.project.data.currCounts
            self.mainStatus.setProjectStats(cNovel, cNovel - iNovel)

        return

    @pyqtSlot()
    def _keyPressReturn(self) -> None:
        """Forward the return/enter keypress to the function that opens
        the currently selected item.
        """
        self.openSelectedItem()
        return

    @pyqtSlot()
    def _keyPressEscape(self) -> None:
        """Process escape keypress in the main window."""
        if self.docEditor.docSearch.isVisible():
            self.docEditor.closeSearch()
        elif self.isFocusMode:
            self.toggleFocusMode()
        return

    @pyqtSlot(int)
    def _mainStackChanged(self, index: int) -> None:
        """Process main window tab change."""
        if index == self.idxOutlineView:
            if SHARED.hasProject:
                self.outlineView.refreshTree()
        return

    @pyqtSlot(int)
    def _projStackChanged(self, index: int) -> None:
        """Process project view tab change."""
        sHandle = None
        if index == self.idxProjView:
            sHandle = self.projView.getSelectedHandle()
        elif index == self.idxNovelView:
            sHandle, _ = self.novelView.getSelectedHandle()
        self.itemDetails.updateViewBox(sHandle)
        return

    ##
    #  Internal Functions
    ##

    def _connectMenuActions(self) -> None:
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
        if isinstance(CONFIG.pdfDocs, Path):
            self.addAction(self.mainMenu.aPdfDocs)

        return

    def _updateWindowTitle(self, projName: str | None = None) -> None:
        """Set the window title and add the project's name."""
        winTitle = CONFIG.appName
        if projName is not None:
            winTitle += " - %s" % projName
        self.setWindowTitle(winTitle)
        return

    def _assembleProjectWizardData(self, newProj: GuiProjectWizard) -> dict:
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

        try:
            langIdx = newProj.field("projLang")
            projData["projLang"] = CONFIG.listLanguages(CONFIG.LANG_PROJ)[langIdx][0]
        except Exception:
            projData["projLang"] = "en_GB"

        return projData

    def _getTagSource(self, tag: str) -> tuple[str | None, str | None]:
        """Handle the index lookup of a tag and display an alert if the
        tag cannot be found.
        """
        tHandle, sTitle = SHARED.project.index.getTagSource(tag)
        if tHandle is None:
            SHARED.error(self.tr(
                "Could not find the reference for tag '{0}'. It either doesn't "
                "exist, or the index is out of date. The index can be updated "
                "from the Tools menu, or by pressing {1}."
            ).format(
                tag, "F9"
            ))
            return None, None
        return tHandle, sTitle

# END Class GuiMain
