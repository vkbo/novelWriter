"""
novelWriter – GUI Main Window
=============================

File History:
Created: 2018-09-22 [0.0.1] GuiMain

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

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

import logging
import sys

from datetime import datetime
from pathlib import Path
from time import time

from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QCloseEvent, QCursor, QIcon
from PyQt5.QtWidgets import (
    QApplication, QFileDialog, QHBoxLayout, QMainWindow, QMessageBox,
    QShortcut, QSplitter, QStackedWidget, QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED, __hexversion__, __version__
from novelwriter.common import formatFileFilter, formatVersion, hexToInt
from novelwriter.constants import nwConst
from novelwriter.dialogs.about import GuiAbout
from novelwriter.dialogs.preferences import GuiPreferences
from novelwriter.dialogs.projectsettings import GuiProjectSettings
from novelwriter.dialogs.wordlist import GuiWordList
from novelwriter.enum import nwDocAction, nwDocInsert, nwDocMode, nwFocus, nwItemType, nwView
from novelwriter.gui.doceditor import GuiDocEditor
from novelwriter.gui.docviewer import GuiDocViewer
from novelwriter.gui.docviewerpanel import GuiDocViewerPanel
from novelwriter.gui.itemdetails import GuiItemDetails
from novelwriter.gui.mainmenu import GuiMainMenu
from novelwriter.gui.noveltree import GuiNovelView
from novelwriter.gui.outline import GuiOutlineView
from novelwriter.gui.projtree import GuiProjectView
from novelwriter.gui.search import GuiProjectSearch
from novelwriter.gui.sidebar import GuiSideBar
from novelwriter.gui.statusbar import GuiMainStatus
from novelwriter.gui.theme import GuiTheme
from novelwriter.tools.dictionaries import GuiDictionaries
from novelwriter.tools.manuscript import GuiManuscript
from novelwriter.tools.noveldetails import GuiNovelDetails
from novelwriter.tools.welcome import GuiWelcome
from novelwriter.tools.writingstats import GuiWritingStats

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

        # Prepare Main Window
        self.resize(*CONFIG.mainWinSize)
        self._updateWindowTitle()

        nwIcon = CONFIG.assetPath("icons") / "novelwriter.svg"
        self.nwIcon = QIcon(str(nwIcon)) if nwIcon.is_file() else QIcon()
        self.setWindowIcon(self.nwIcon)
        QApplication.setWindowIcon(self.nwIcon)

        # Build the GUI
        # =============

        # Sizes
        mPx = CONFIG.pxInt(4)
        hWd = CONFIG.pxInt(4)

        # Main GUI Elements
        self.mainStatus     = GuiMainStatus(self)
        self.projView       = GuiProjectView(self)
        self.projSearch     = GuiProjectSearch(self)
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
        self.projStack.addWidget(self.projSearch)
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
        self.splitView = QSplitter(Qt.Orientation.Vertical, self)
        self.splitView.addWidget(self.docViewer)
        self.splitView.addWidget(self.docViewerPanel)
        self.splitView.setHandleWidth(hWd)
        self.splitView.setOpaqueResize(False)
        self.splitView.setSizes(CONFIG.viewPanePos)
        self.splitView.setCollapsible(0, False)
        self.splitView.setCollapsible(1, False)

        # Splitter : Document Editor / Document Viewer
        self.splitDocs = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitDocs.addWidget(self.docEditor)
        self.splitDocs.addWidget(self.splitView)
        self.splitDocs.setOpaqueResize(False)
        self.splitDocs.setHandleWidth(hWd)
        self.splitDocs.setCollapsible(0, False)
        self.splitDocs.setCollapsible(1, False)

        # Splitter : Project Tree / Document Area
        self.splitMain = QSplitter(Qt.Orientation.Horizontal)
        self.splitMain.setContentsMargins(0, 0, 0, 0)
        self.splitMain.addWidget(self.treePane)
        self.splitMain.addWidget(self.splitDocs)
        self.splitMain.setOpaqueResize(False)
        self.splitMain.setHandleWidth(hWd)
        self.splitMain.setSizes(CONFIG.mainPanePos)
        self.splitMain.setCollapsible(0, False)
        self.splitMain.setCollapsible(0, False)
        self.splitMain.setStretchFactor(1, 0)
        self.splitMain.setStretchFactor(1, 1)

        # Main Stack : Editor / Outline
        self.mainStack = QStackedWidget(self)
        self.mainStack.addWidget(self.splitMain)
        self.mainStack.addWidget(self.outlineView)
        self.mainStack.currentChanged.connect(self._mainStackChanged)

        # Editor / Viewer Default State
        self.splitView.setVisible(False)
        self.docEditor.closeSearch()

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
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)  # Issue #1147

        # Connect Signals
        # ===============

        SHARED.focusModeChanged.connect(self._focusModeChanged)
        SHARED.indexAvailable.connect(self.docViewerPanel.indexHasAppeared)
        SHARED.indexChangedTags.connect(self.docEditor.updateChangedTags)
        SHARED.indexChangedTags.connect(self.docViewerPanel.updateChangedTags)
        SHARED.indexCleared.connect(self.docViewerPanel.indexWasCleared)
        SHARED.indexScannedText.connect(self.docViewerPanel.projectItemChanged)
        SHARED.indexScannedText.connect(self.itemDetails.updateViewBox)
        SHARED.indexScannedText.connect(self.projView.updateItemValues)
        SHARED.mainClockTick.connect(self._timeTick)
        SHARED.projectStatusChanged.connect(self.mainStatus.updateProjectStatus)
        SHARED.projectStatusMessage.connect(self.mainStatus.setStatusMessage)
        SHARED.spellLanguageChanged.connect(self.mainStatus.setLanguage)
        SHARED.statusLabelsChanged.connect(self.docViewerPanel.updateStatusLabels)
        SHARED.statusLabelsChanged.connect(self.projView.refreshUserLabels)

        self.mainMenu.requestDocAction.connect(self._passDocumentAction)
        self.mainMenu.requestDocInsert.connect(self._passDocumentInsert)
        self.mainMenu.requestDocInsertText.connect(self._passDocumentInsert)
        self.mainMenu.requestDocKeyWordInsert.connect(self.docEditor.insertKeyWord)
        self.mainMenu.requestFocusChange.connect(self._switchFocus)
        self.mainMenu.requestViewChange.connect(self._changeView)

        self.sideBar.requestViewChange.connect(self._changeView)

        self.projView.openDocumentRequest.connect(self._openDocument)
        self.projView.projectSettingsRequest.connect(self.showProjectSettingsDialog)
        self.projView.rootFolderChanged.connect(self.novelView.updateRootItem)
        self.projView.rootFolderChanged.connect(self.outlineView.updateRootItem)
        self.projView.rootFolderChanged.connect(self.projView.updateRootItem)
        self.projView.selectedItemChanged.connect(self.itemDetails.updateViewBox)
        self.projView.treeItemChanged.connect(self.docEditor.updateDocInfo)
        self.projView.treeItemChanged.connect(self.docViewer.updateDocInfo)
        self.projView.treeItemChanged.connect(self.docViewerPanel.projectItemChanged)
        self.projView.treeItemChanged.connect(self.itemDetails.updateViewBox)
        self.projView.wordCountsChanged.connect(self._updateStatusWordCount)

        self.novelView.openDocumentRequest.connect(self._openDocument)
        self.novelView.selectedItemChanged.connect(self.itemDetails.updateViewBox)

        self.projSearch.openDocumentSelectRequest.connect(self._openDocumentSelection)
        self.projSearch.selectedItemChanged.connect(self.itemDetails.updateViewBox)

        self.docEditor.closeDocumentRequest.connect(self.closeDocEditor)
        self.docEditor.docCountsChanged.connect(self.itemDetails.updateCounts)
        self.docEditor.docCountsChanged.connect(self.projView.updateCounts)
        self.docEditor.docTextChanged.connect(self.projSearch.textChanged)
        self.docEditor.editedStatusChanged.connect(self.mainStatus.updateDocumentStatus)
        self.docEditor.loadDocumentTagRequest.connect(self._followTag)
        self.docEditor.novelItemMetaChanged.connect(self.novelView.updateNovelItemMeta)
        self.docEditor.novelStructureChanged.connect(self.novelView.refreshTree)
        self.docEditor.requestNewNoteCreation.connect(self.projView.createNewNote)
        self.docEditor.requestNextDocument.connect(self.openNextDocument)
        self.docEditor.requestProjectItemRenamed.connect(self.projView.renameTreeItem)
        self.docEditor.requestProjectItemSelected.connect(self.projView.setSelectedHandle)
        self.docEditor.spellCheckStateChanged.connect(self.mainMenu.setSpellCheckState)
        self.docEditor.statusMessage.connect(self.mainStatus.setStatusMessage)
        self.docEditor.toggleFocusModeRequest.connect(self.toggleFocusMode)

        self.docViewer.closeDocumentRequest.connect(self.closeDocViewer)
        self.docViewer.documentLoaded.connect(self.docViewerPanel.updateHandle)
        self.docViewer.loadDocumentTagRequest.connect(self._followTag)
        self.docViewer.reloadDocumentRequest.connect(self._reloadViewer)
        self.docViewer.requestProjectItemSelected.connect(self.projView.setSelectedHandle)
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

        # Initialise Main GUI
        self.initMain()
        self.asProjTimer.start()
        self.asDocTimer.start()
        self.mainStatus.clearStatus()
        self.showNormal()

        logger.debug("Ready: GUI")
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
        QApplication.processEvents()
        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.focusChanged.connect(self._appFocusChanged)

        # Check that config loaded fine
        if CONFIG.hasError:
            SHARED.error(CONFIG.errorText())

        if cmdOpen:
            QApplication.processEvents()
            logger.info("Command line path: %s", cmdOpen)
            self.openProject(cmdOpen)

        if not SHARED.hasProject:
            self.showWelcomeDialog()

        # If this is a new release, let the user know
        if hexToInt(CONFIG.lastNotes) < hexToInt(__hexversion__):
            CONFIG.lastNotes = __hexversion__
            trVersion = self.tr(
                "You are now running novelWriter version {0}."
            ).format(formatVersion(__version__))
            trRelease = self.tr(
                "Please check the {0}release notes{1} for further details."
            ).format(f"<a href='{nwConst.URL_RELEASES}'>", "</a>")
            SHARED.info(f"{trVersion}<br>{trRelease}")

        return

    ##
    #  Project Actions
    ##

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
            self.closeViewerPanel(byUser=False)

            self.docViewerPanel.closeProjectTasks()
            self.outlineView.closeProjectTasks()
            self.novelView.closeProjectTasks()
            self.projView.closeProjectTasks()
            self.projSearch.closeProjectTasks()
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

        # Make sure any open project is cleared out first
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
                    CONFIG.localDateTime(datetime.fromtimestamp(int(lockStatus[3])))
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
        self.docEditor.toggleSpellCheck(SHARED.project.data.spellCheck)
        self.mainStatus.setRefTime(SHARED.project.projOpened)
        self.projView.openProjectTasks()
        self.novelView.openProjectTasks()
        self.outlineView.openProjectTasks()
        self.docViewerPanel.openProjectTasks()
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
            QApplication.processEvents()
            self.openDocument(lastEdited, doScroll=True)

        lastViewed = SHARED.project.data.getLastHandle("viewer")
        if lastViewed is not None:
            QApplication.processEvents()
            self.viewDocument(lastViewed)

        # Check if we need to rebuild the index
        if SHARED.project.index.indexBroken:
            SHARED.info(self.tr("The project index is outdated or broken. Rebuilding index."))
            self.rebuildIndex()

        # Make sure the changed status is set to false on things opened
        QApplication.processEvents()
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

    def closeDocument(self, beforeOpen: bool = False) -> None:
        """Close the document and clear the editor and title field."""
        if SHARED.hasProject:
            # Disable focus mode if it is active
            if SHARED.focusMode:
                SHARED.setFocusMode(False)
            self.saveDocument()
            self.docEditor.clearEditor()
            if not beforeOpen:
                self.novelView.setActiveHandle(None)
        return

    def openDocument(
        self,
        tHandle: str | None,
        tLine: int | None = None,
        sTitle: str | None = None,
        changeFocus: bool = True,
        doScroll: bool = False
    ) -> bool:
        """Open a specific document, optionally at a given line."""
        if not SHARED.hasProject:
            logger.error("No project open")
            return False

        if not tHandle or not SHARED.project.tree.checkType(tHandle, nwItemType.FILE):
            logger.debug("Requested item '%s' is not a document", tHandle)
            return False

        if sTitle and tLine is None:
            if hItem := SHARED.project.index.getItemHeading(tHandle, sTitle):
                tLine = hItem.line

        self._changeView(nwView.EDITOR)
        if tHandle == self.docEditor.docHandle:
            self.docEditor.setCursorLine(tLine)
            if changeFocus:
                self.docEditor.setFocus()
            return True

        self.closeDocument(beforeOpen=True)
        if self.docEditor.loadText(tHandle, tLine):
            SHARED.project.data.setLastHandle(tHandle, "editor")
            self.projView.setSelectedHandle(tHandle, doScroll=doScroll)
            self.novelView.setActiveHandle(tHandle, doScroll=doScroll)
            if changeFocus:
                self.docEditor.setFocus()
        else:
            return False

        return True

    @pyqtSlot(str, bool)
    def openNextDocument(self, tHandle: str, wrapAround: bool) -> None:
        """Open the next document in the project tree, following the
        document with the given handle. Stop when reaching the end.
        """
        if SHARED.hasProject:
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
            elif wrapAround:
                self.openDocument(fHandle, tLine=1, doScroll=True)
        return

    def saveDocument(self, force: bool = False) -> None:
        """Save the current documents."""
        if SHARED.hasProject:
            self.docEditor.saveCursorPosition()
            if force or self.docEditor.docChanged:
                self.docEditor.saveText()
        return

    @pyqtSlot()
    def forceSaveDocument(self) -> None:
        """Save document even of it has not changed."""
        self.saveDocument(force=True)
        return

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

        # If we're loading the document in the editor, it may need to be saved
        if tHandle == self.docEditor.docHandle and self.docEditor.docChanged:
            self.saveDocument()

        logger.debug("Viewing document with handle '%s'", tHandle)
        updateHistory = tHandle != self.docViewer.docHandle
        if self.docViewer.loadText(tHandle, updateHistory=updateHistory):
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
                self.docViewer.navigateTo(f"#{tHandle}:{sTitle}")

        return True

    def importDocument(self) -> bool:
        """Import the text contained in an out-of-project text file, and
        insert the text into the currently open document.
        """
        if not SHARED.hasProject:
            logger.error("No project open")
            return False

        lastPath = CONFIG.lastPath("import")
        ffilter = formatFileFilter(["*.txt", "*.md", "*.nwd", "*"])
        loadFile, _ = QFileDialog.getOpenFileName(
            self, self.tr("Import File"), str(lastPath), filter=ffilter
        )
        if not loadFile:
            return False

        if loadFile.strip() == "":
            return False

        text = None
        try:
            with open(loadFile, mode="rt", encoding="utf-8") as inFile:
                text = inFile.read()
            CONFIG.setLastPath("import", loadFile)
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

        self.docEditor.replaceText(text)

        return True

    ##
    #  Tree Item Actions
    ##

    @pyqtSlot()
    def openSelectedItem(self) -> None:
        """Open the selected item from the tree that is currently
        active. It is not checked that the item is actually a document.
        That should be handled by the openDocument function.
        """
        if SHARED.hasProject:
            tHandle = None
            sTitle = None
            if self.projView.treeHasFocus():
                tHandle = self.projView.getSelectedHandle()
            elif self.novelView.treeHasFocus():
                tHandle, sTitle = self.novelView.getSelectedHandle()
            elif self.outlineView.treeHasFocus():
                tHandle, sTitle = self.outlineView.getSelectedHandle()
            else:
                logger.warning("No item selected")
                return

            if tHandle:
                self.openDocument(tHandle, sTitle=sTitle, changeFocus=False, doScroll=False)

        return

    def rebuildIndex(self, beQuiet: bool = False) -> None:
        """Rebuild the entire index."""
        if SHARED.hasProject:
            logger.info("Rebuilding index ...")
            QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
            tStart = time()

            self.projView.saveProjectTasks()
            SHARED.project.index.rebuildIndex()
            self.projView.populateTree()
            self.novelView.refreshTree()

            tEnd = time()
            self.mainStatus.setStatusMessage(
                self.tr("Indexing completed in {0} ms").format(f"{(tEnd - tStart)*1000.0:.1f}")
            )
            self._updateStatusWordCount()
            QApplication.restoreOverrideCursor()

            if not beQuiet:
                SHARED.info(self.tr("The project index has been successfully rebuilt."))

        return

    ##
    #  Main Dialogs
    ##

    @pyqtSlot()
    def showWelcomeDialog(self) -> None:
        """Open the welcome dialog."""
        dialog = GuiWelcome(self)
        dialog.openProjectRequest.connect(self._openProjectFromWelcome)
        dialog.exec()
        return

    @pyqtSlot()
    def showPreferencesDialog(self) -> None:
        """Open the preferences dialog."""
        dialog = GuiPreferences(self)
        dialog.newPreferencesReady.connect(self._processConfigChanges)
        dialog.exec()
        return

    @pyqtSlot()
    @pyqtSlot(int)
    def showProjectSettingsDialog(self, focusTab: int = GuiProjectSettings.PAGE_SETTINGS) -> None:
        """Open the project settings dialog."""
        if SHARED.hasProject:
            dialog = GuiProjectSettings(self, gotoPage=focusTab)
            dialog.newProjectSettingsReady.connect(self._processProjectSettingsChanges)
            dialog.exec()
        return

    @pyqtSlot()
    def showNovelDetailsDialog(self) -> None:
        """Open the novel details dialog."""
        if SHARED.hasProject:
            dialog = GuiNovelDetails(self)
            dialog.activateDialog()
            dialog.updateValues()
        return

    @pyqtSlot()
    def showBuildManuscriptDialog(self) -> None:
        """Open the build manuscript dialog."""
        if SHARED.hasProject:
            if not (dialog := SHARED.findTopLevelWidget(GuiManuscript)):
                dialog = GuiManuscript(self)
            dialog.activateDialog()
            dialog.loadContent()
        return

    @pyqtSlot()
    def showProjectWordListDialog(self) -> None:
        """Open the project word list dialog."""
        if SHARED.hasProject:
            dialog = GuiWordList(self)
            dialog.newWordListReady.connect(self._processWordListChanges)
            dialog.exec()
        return

    @pyqtSlot()
    def showWritingStatsDialog(self) -> None:
        """Open the session stats dialog."""
        if SHARED.hasProject:
            if not (dialog := SHARED.findTopLevelWidget(GuiWritingStats)):
                dialog = GuiWritingStats(self)
            dialog.activateDialog()
            dialog.populateGUI()
        return

    @pyqtSlot()
    def showAboutNWDialog(self) -> None:
        """Show the novelWriter about dialog."""
        dialog = GuiAbout(self)
        dialog.exec()
        return

    @pyqtSlot()
    def showAboutQtDialog(self) -> None:
        """Show the Qt about dialog."""
        msgBox = QMessageBox(self)
        msgBox.aboutQt(self, "About Qt")
        return

    @pyqtSlot()
    def showDictionariesDialog(self) -> None:
        """Show the download dictionaries dialog."""
        dialog = GuiDictionaries(self)
        dialog.activateDialog()
        if not dialog.initDialog():
            dialog.close()
            SHARED.error(self.tr("Could not initialise the dialog."))
        return

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

        if not SHARED.focusMode:
            CONFIG.setMainPanePos(self.splitMain.sizes())
            CONFIG.setOutlinePanePos(self.outlineView.splitSizes())
            if self.docViewerPanel.isVisible():
                CONFIG.setViewPanePos(self.splitView.sizes())

        CONFIG.showViewerPanel = self.docViewerPanel.isVisible()
        wFull = Qt.WindowState.WindowFullScreen
        if self.windowState() & wFull != wFull:
            # Ignore window size if in full screen mode
            CONFIG.setMainWinSize(self.width(), self.height())

        if SHARED.hasProject:
            self.closeProject(True)
        CONFIG.saveConfig()

        QApplication.quit()

        return True

    def closeViewerPanel(self, byUser: bool = True) -> bool:
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
        self.setWindowState(self.windowState() ^ Qt.WindowState.WindowFullScreen)
        return

    ##
    #  Events
    ##

    def closeEvent(self, event: QCloseEvent) -> None:
        """Capture the closing event of the GUI and call the close
        function to handle all the close process steps.
        """
        event.accept() if self.closeMain() else event.ignore()
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
    def closeDocViewer(self) -> None:
        """Close the document viewer."""
        self.closeViewerPanel()
        SHARED.project.data.setLastHandle(None, "viewer")
        return

    @pyqtSlot()
    def toggleFocusMode(self) -> None:
        """Toggle focus mode."""
        if self.docEditor.docHandle:
            SHARED.setFocusMode(not SHARED.focusMode)
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot("QWidget*", "QWidget*")
    def _appFocusChanged(self, old: QWidget, new: QWidget) -> None:
        """Alert main widgets that they have received or lost focus."""
        if isinstance(new, QWidget):
            docEditor = False
            docViewer = False
            if self.docEditor.isAncestorOf(new):
                docEditor = True
            elif self.docViewer.isAncestorOf(new):
                docViewer = True

            self.docEditor.changeFocusState(docEditor)
            self.docViewer.changeFocusState(docViewer)

            logger.debug("Main focus switched to: %s", type(new).__name__)

        return

    @pyqtSlot(bool)
    def _focusModeChanged(self, focusMode: bool) -> None:
        """Handle change of focus mode. The Main GUI Focus Mode hides
        tree, view, statusbar and menu.
        """
        if focusMode:
            logger.debug("Activating Focus Mode")
            self._changeView(nwView.EDITOR)
            self.docEditor.setFocus()
        else:
            logger.debug("Deactivating Focus Mode")

        cursorVisible = self.docEditor.cursorIsVisible()
        isVisible = not focusMode
        self.treePane.setVisible(isVisible)
        self.mainStatus.setVisible(isVisible)
        self.mainMenu.setVisible(isVisible)
        self.sideBar.setVisible(isVisible)

        hideDocFooter = focusMode and CONFIG.hideFocusFooter
        self.docEditor.docFooter.setVisible(not hideDocFooter)

        if self.splitView.isVisible():
            self.splitView.setVisible(False)
        elif self.docViewer.docHandle is not None:
            self.splitView.setVisible(True)

        if cursorVisible:
            self.docEditor.ensureCursorVisibleNoCentre()
        return

    @pyqtSlot(nwFocus)
    def _switchFocus(self, paneNo: nwFocus) -> None:
        """Switch focus between main GUI views."""
        if paneNo == nwFocus.TREE:
            # Decision Matrix
            #  vM | vP | fP | vN | fN | Focus
            # ----|----|----|----|----|---------
            #  T  | T  | T  | F  | F  | Novel
            #  T  | T  | F  | F  | F  | Project
            #  T  | F  | F  | T  | T  | Project
            #  T  | F  | F  | T  | F  | Novel
            #  T  | F  | F  | F  | F  | Project
            #  F  | T  | T  | F  | F  | Project
            #  F  | T  | F  | F  | F  | Project
            #  F  | F  | F  | T  | T  | Novel
            #  F  | F  | F  | T  | F  | Novel
            #  F  | F  | F  | F  | F  | Project

            vM = self.mainStack.currentWidget() is self.splitMain
            vP = self.projStack.currentWidget() is self.projView
            vN = self.projStack.currentWidget() is self.novelView
            fP = self.projView.treeHasFocus()
            fN = self.novelView.treeHasFocus()

            self._changeView(nwView.EDITOR)
            if (vM and (vP and fP or vN and not fN)) or (not vM and vN):
                self._changeView(nwView.NOVEL)
                self.novelView.setTreeFocus()
            else:
                self._changeView(nwView.PROJECT)
                self.projView.setTreeFocus()

        elif paneNo == nwFocus.DOCUMENT:
            self._changeView(nwView.EDITOR)
            hasViewer = self.splitView.isVisible()
            if hasViewer and self.docEditor.anyFocus():
                self.docViewer.setFocus()
            elif hasViewer and self.docViewer.anyFocus():
                self.docEditor.setFocus()
            else:
                self.docEditor.setFocus()

        elif paneNo == nwFocus.OUTLINE:
            self._changeView(nwView.OUTLINE)
            self.outlineView.setTreeFocus()

        return

    @pyqtSlot(bool, bool, bool, bool)
    def _processConfigChanges(self, restart: bool, tree: bool, theme: bool, syntax: bool) -> None:
        """Refresh GUI based on flags from the Preferences dialog."""
        logger.debug("Applying new preferences")
        self.initMain()
        self.saveDocument()

        if restart:
            SHARED.info(self.tr(
                "Some changes will not be applied until novelWriter has been restarted."
            ))

        if tree:
            self.projView.populateTree()

        if theme:
            # We are doing this manually instead of connecting to
            # paletteChanged since the processing order matters
            SHARED.theme.loadTheme()
            self.docEditor.updateTheme()
            self.docViewer.updateTheme()
            self.docViewerPanel.updateTheme()
            self.sideBar.updateTheme()
            self.projView.updateTheme()
            self.novelView.updateTheme()
            self.projSearch.updateTheme()
            self.outlineView.updateTheme()
            self.itemDetails.updateTheme()
            self.mainStatus.updateTheme()

        if syntax:
            SHARED.theme.loadSyntax()
            self.docEditor.updateSyntaxColours()

        self.docEditor.initEditor()
        self.docViewer.initViewer()
        self.projView.initSettings()
        self.novelView.initSettings()
        self.outlineView.initSettings()
        self._updateStatusWordCount()

        return

    @pyqtSlot()
    def _processProjectSettingsChanges(self) -> None:
        """Refresh data dependent on project settings."""
        logger.debug("Applying new project settings")
        SHARED.updateSpellCheckLanguage()
        self.itemDetails.refreshDetails()
        self._updateWindowTitle(SHARED.project.data.name)
        return

    @pyqtSlot()
    def _processWordListChanges(self) -> None:
        """Reload project word list."""
        logger.debug("Reloading word list")
        SHARED.updateSpellCheckLanguage(reload=True)
        self.docEditor.spellCheckDocument()
        return

    @pyqtSlot(str, nwDocMode)
    def _followTag(self, tag: str, mode: nwDocMode) -> None:
        """Follow a tag after user interaction with a link."""
        tHandle, sTitle = self._getTagSource(tag)
        if tHandle is not None:
            if mode == nwDocMode.EDIT:
                self.openDocument(tHandle, sTitle=sTitle)
            elif mode == nwDocMode.VIEW:
                self.viewDocument(tHandle=tHandle, sTitle=sTitle)
        return

    @pyqtSlot(Path)
    def _openProjectFromWelcome(self, path: Path) -> None:
        """Handle an open project request from the welcome dialog."""
        QApplication.processEvents()
        self.openProject(path)
        if not SHARED.hasProject:
            self.showWelcomeDialog()
        return

    @pyqtSlot(str, nwDocMode, str, bool)
    def _openDocument(self, tHandle: str, mode: nwDocMode, sTitle: str, setFocus: bool) -> None:
        """Handle an open document request."""
        if tHandle is not None:
            if mode == nwDocMode.EDIT:
                self.openDocument(tHandle, sTitle=sTitle, changeFocus=setFocus)
            elif mode == nwDocMode.VIEW:
                self.viewDocument(tHandle=tHandle, sTitle=sTitle)
        return

    @pyqtSlot(str, int, int, bool)
    def _openDocumentSelection(
        self, tHandle: str, selStart: int, selLength: int, changeFocus: bool
    ) -> None:
        """Open a document and select a section of the text."""
        if self.openDocument(tHandle, changeFocus=changeFocus):
            self.docEditor.setCursorSelection(selStart, selLength)
        return

    @pyqtSlot()
    def _reloadViewer(self) -> None:
        """Reload the document in the viewer."""
        if self.docEditor.docHandle == self.docViewer.docHandle:
            # If the two panels have the same document, save any changes in the editor
            self.saveDocument()
        self.docViewer.reloadText()
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
        elif view == nwView.SEARCH:
            self.mainStack.setCurrentWidget(self.splitMain)
            self.projStack.setCurrentWidget(self.projSearch)
            self.projSearch.beginSearch(
                self.docEditor.getSelectedText() if self.docEditor.anyFocus() else ""
            )
        elif view == nwView.OUTLINE:
            self.mainStack.setCurrentWidget(self.outlineView)
        return

    @pyqtSlot(nwDocAction)
    def _passDocumentAction(self, action: nwDocAction) -> None:
        """Pass on a document action to the editor or viewer based on
        which one has focus, or if neither has focus, ignore it.
        """
        if self.docEditor.hasFocus():
            self.docEditor.docAction(action)
        elif self.docViewer.hasFocus():
            self.docViewer.docAction(action)
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
    def _toggleViewerPanelVisibility(self) -> None:
        """Toggle the visibility of the document viewer panel."""
        CONFIG.showViewerPanel = not CONFIG.showViewerPanel
        self.docViewerPanel.setVisible(CONFIG.showViewerPanel)
        return

    @pyqtSlot()
    def _timeTick(self) -> None:
        """Process time tick of the main timer."""
        if SHARED.hasProject:
            currTime = time()
            editIdle = currTime - self.docEditor.lastActive > CONFIG.userIdleTime
            userIdle = QApplication.applicationState() != Qt.ApplicationState.ApplicationActive
            self.mainStatus.setUserIdle(editIdle or userIdle)
            SHARED.updateIdleTime(currTime, editIdle or userIdle)
            self.mainStatus.updateTime(idleTime=SHARED.projectIdleTime)
            if CONFIG.memInfo and int(currTime) % 5 == 0:  # pragma: no cover
                self.mainStatus.memInfo()
        return

    @pyqtSlot()
    def _autoSaveProject(self) -> None:
        """Autosave of the project. This is a timer-activated slot."""
        doSave  = SHARED.hasProject
        doSave &= SHARED.project.projChanged
        doSave &= SHARED.project.storage.isOpen()
        if doSave:
            logger.debug("Auto-saving project")
            self.saveProject(autoSave=True)
        return

    @pyqtSlot()
    def _autoSaveDocument(self) -> None:
        """Autosave of the document. This is a timer-activated slot."""
        if SHARED.hasProject and self.docEditor.docChanged:
            logger.debug("Auto-saving document")
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
        """Process a return or enter keypress in the main window."""
        if self.projStack.currentWidget() == self.projSearch:
            self.projSearch.processReturn()
        else:
            self.openSelectedItem()
        return

    @pyqtSlot()
    def _keyPressEscape(self) -> None:
        """Process an escape keypress in the main window."""
        if self.docEditor.searchVisible():
            self.docEditor.closeSearch()
        elif SHARED.focusMode:
            SHARED.setFocusMode(False)
        return

    @pyqtSlot(int)
    def _mainStackChanged(self, index: int) -> None:
        """Process main window tab change."""
        if self.mainStack.widget(index) == self.outlineView:
            if SHARED.hasProject:
                self.outlineView.refreshTree()
        return

    @pyqtSlot(int)
    def _projStackChanged(self, index: int) -> None:
        """Process project view tab change."""
        sHandle = None
        widget = self.projStack.widget(index)
        if widget == self.projView:
            sHandle = self.projView.getSelectedHandle()
        elif widget == self.novelView:
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
        self.addAction(self.mainMenu.aInsShort)

        for mAction, _ in self.mainMenu.mInsKWItems.values():
            self.addAction(mAction)

        # Search
        self.addAction(self.mainMenu.aFind)
        self.addAction(self.mainMenu.aReplace)
        self.addAction(self.mainMenu.aFindNext)
        self.addAction(self.mainMenu.aFindPrev)
        self.addAction(self.mainMenu.aReplaceNext)

        # Format
        self.addAction(self.mainMenu.aFmtItalic)
        self.addAction(self.mainMenu.aFmtBold)
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
        self.setWindowTitle(" - ".join(filter(None, [projName, CONFIG.appName])))
        return

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
