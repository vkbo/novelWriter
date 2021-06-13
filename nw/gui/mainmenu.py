# -*- coding: utf-8 -*-
"""
novelWriter – GUI Main Menu
===========================
GUI class for the main window menu

File History:
Created: 2019-04-27 [0.0.1]

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

from PyQt5.QtCore import QUrl, QProcess
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QMenuBar, QAction

from nw.enum import nwItemType, nwItemClass, nwDocAction, nwDocInsert, nwWidget
from nw.constants import trConst, nwKeyWords, nwLabels, nwUnicode

logger = logging.getLogger(__name__)

class GuiMainMenu(QMenuBar):

    def __init__(self, theParent):
        QMenuBar.__init__(self, theParent)

        logger.debug("Initialising GuiMainMenu ...")
        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theParent.theProject

        # Internals
        self.assistProc = None

        # Build Menu
        self._buildProjectMenu()
        self._buildDocumentMenu()
        self._buildEditMenu()
        self._buildViewMenu()
        self._buildInsertMenu()
        self._buildFormatMenu()
        self._buildSearchMenu()
        self._buildToolsMenu()
        self._buildHelpMenu()

        # Function Pointers
        self._docAction     = self.theParent.passDocumentAction
        self._moveTreeItem  = self.theParent.treeView.moveTreeItem
        self._newTreeItem   = self.theParent.treeView.newTreeItem
        self._docInsert     = self.theParent.docEditor.insertText
        self._insertKeyWord = self.theParent.docEditor.insertKeyWord

        logger.debug("GuiMainMenu initialisation complete")

        return

    ##
    #  Methods
    ##

    def setAvailableRoot(self):
        """Update the list of available root folders and set the ones
        that are active.
        """
        for itemClass in nwItemClass:
            if itemClass == nwItemClass.NO_CLASS:
                continue
            if itemClass == nwItemClass.TRASH:
                continue
            self.rootItems[itemClass].setEnabled(
                self.theProject.projTree.checkRootUnique(itemClass)
            )
        return

    def closeHelp(self):
        """Close the process used for the Qt Assistant, if it is open.
        """
        if self.assistProc is None:
            return

        if self.assistProc.state() == QProcess.Starting:
            if self.assistProc.waitForStarted(10000):
                self.assistProc.terminate()
            else:
                self.assistProc.kill()

        elif self.assistProc.state() == QProcess.Running:
            self.assistProc.terminate()
            if not self.assistProc.waitForFinished(10000):
                self.assistProc.kill()

        return

    ##
    #  Update Menu on Settings Changed
    ##

    def setSpellCheck(self, theMode):
        """Forward spell check check state to its action.
        """
        self.aSpellCheck.setChecked(theMode)
        return

    def setAutoOutline(self, theMode):
        """Forward auto outline check state to its action.
        """
        self.aAutoOutline.setChecked(theMode)
        return

    def setFocusMode(self, theMode):
        """Forward focus mode check state to its action.
        """
        self.aFocusMode.setChecked(theMode)
        return

    ##
    #  Slots
    ##

    def _toggleSpellCheck(self, isChecked=False):
        """Toggle spell checking. The active status of the spell check
        flag is handled by the document editor class, so we make no
        decision, just pass a None to the function and let it decide.
        """
        self.theParent.docEditor.setSpellCheck(None)
        return True

    def _toggleAutoOutline(self, theMode):
        """Toggle auto outline when the menu entry is checked.
        """
        self.theProject.setAutoOutline(theMode)
        return True

    def _openAssistant(self, isChecked=False):
        """Open the documentation in Qt Assistant.
        """
        if not self.mainConf.hasHelp:
            self._openWebsite(nw.__docurl__)
            return False

        self.assistProc = QProcess(self)
        self.assistProc.start("assistant", ["-collectionFile", self.mainConf.helpPath])

        if not self.assistProc.waitForStarted(10000):
            self._openWebsite(nw.__docurl__)
            return False

        return True

    def _openWebsite(self, theUrl):
        """Open a URL in the system's default browser.
        """
        QDesktopServices.openUrl(QUrl(theUrl))
        return True

    ##
    #  Menu Builders
    ##

    def _buildProjectMenu(self):
        """Assemble the Project menu.
        """
        # Project
        self.projMenu = self.addMenu(self.tr("&Project"))

        # Project > New Project
        self.aNewProject = QAction(self.tr("New Project"), self)
        self.aNewProject.setStatusTip(self.tr("Create new project"))
        self.aNewProject.triggered.connect(lambda: self.theParent.newProject(None))
        self.projMenu.addAction(self.aNewProject)

        # Project > Open Project
        self.aOpenProject = QAction(self.tr("Open Project"), self)
        self.aOpenProject.setStatusTip(self.tr("Open project"))
        self.aOpenProject.setShortcut("Ctrl+Shift+O")
        self.aOpenProject.triggered.connect(lambda: self.theParent.showProjectLoadDialog())
        self.projMenu.addAction(self.aOpenProject)

        # Project > Save Project
        self.aSaveProject = QAction(self.tr("Save Project"), self)
        self.aSaveProject.setStatusTip(self.tr("Save project"))
        self.aSaveProject.setShortcut("Ctrl+Shift+S")
        self.aSaveProject.triggered.connect(lambda: self.theParent.saveProject())
        self.projMenu.addAction(self.aSaveProject)

        # Project > Close Project
        self.aCloseProject = QAction(self.tr("Close Project"), self)
        self.aCloseProject.setStatusTip(self.tr("Close project"))
        self.aCloseProject.setShortcut("Ctrl+Shift+W")
        self.aCloseProject.triggered.connect(lambda: self.theParent.closeProject(False))
        self.projMenu.addAction(self.aCloseProject)

        # Project > Separator
        self.projMenu.addSeparator()

        # Project > Project Settings
        self.aProjectSettings = QAction(self.tr("Project Settings"), self)
        self.aProjectSettings.setStatusTip(self.tr("Project settings"))
        self.aProjectSettings.setShortcut("Ctrl+Shift+,")
        self.aProjectSettings.triggered.connect(lambda: self.theParent.showProjectSettingsDialog())
        self.projMenu.addAction(self.aProjectSettings)

        # Project > Project Details
        self.aProjectDetails = QAction(self.tr("Project Details"), self)
        self.aProjectDetails.setStatusTip(self.tr("Project details"))
        self.aProjectDetails.setShortcut("Shift+F6")
        self.aProjectDetails.triggered.connect(lambda: self.theParent.showProjectDetailsDialog())
        self.projMenu.addAction(self.aProjectDetails)

        # Project > Separator
        self.projMenu.addSeparator()

        # Project > New Root
        self.rootMenu = self.projMenu.addMenu(self.tr("Create Root Folder"))
        self.rootItems = {}
        self.rootItems[nwItemClass.NOVEL]     = QAction(self.tr("Novel Root"),     self.rootMenu)
        self.rootItems[nwItemClass.PLOT]      = QAction(self.tr("Plot Root"),      self.rootMenu)
        self.rootItems[nwItemClass.CHARACTER] = QAction(self.tr("Character Root"), self.rootMenu)
        self.rootItems[nwItemClass.WORLD]     = QAction(self.tr("Location Root"),  self.rootMenu)
        self.rootItems[nwItemClass.TIMELINE]  = QAction(self.tr("Timeline Root"),  self.rootMenu)
        self.rootItems[nwItemClass.OBJECT]    = QAction(self.tr("Object Root"),    self.rootMenu)
        self.rootItems[nwItemClass.ENTITY]    = QAction(self.tr("Entity Root"),    self.rootMenu)
        self.rootItems[nwItemClass.CUSTOM]    = QAction(self.tr("Custom Root"),    self.rootMenu)
        self.rootItems[nwItemClass.ARCHIVE]   = QAction(self.tr("Outtakes Root"),  self.rootMenu)
        nCount = 0
        for itemClass in self.rootItems.keys():
            nCount += 1 # This forces the lambdas to be unique
            self.rootItems[itemClass].triggered.connect(
                lambda nCount, itemClass=itemClass: self._newTreeItem(nwItemType.ROOT, itemClass)
            )
            self.rootMenu.addAction(self.rootItems[itemClass])

        # Project > New Folder
        self.aCreateFolder = QAction(self.tr("Create Folder"), self)
        self.aCreateFolder.setStatusTip(self.tr("Create folder"))
        self.aCreateFolder.setShortcut("Ctrl+Shift+N")
        self.aCreateFolder.triggered.connect(lambda: self._newTreeItem(nwItemType.FOLDER, None))
        self.projMenu.addAction(self.aCreateFolder)

        # Project > Separator
        self.projMenu.addSeparator()

        # Project > Edit
        self.aEditItem = QAction(self.tr("Edit Item"), self)
        self.aEditItem.setStatusTip(self.tr("Change project item settings"))
        self.aEditItem.setShortcuts(["Ctrl+E", "F2"])
        self.aEditItem.triggered.connect(lambda: self.theParent.editItem(None))
        self.projMenu.addAction(self.aEditItem)

        # Project > Delete
        self.aDeleteItem = QAction(self.tr("Delete Item"), self)
        self.aDeleteItem.setStatusTip(self.tr("Delete selected project item"))
        self.aDeleteItem.setShortcut("Ctrl+Shift+Del")
        self.aDeleteItem.triggered.connect(lambda: self.theParent.treeView.deleteItem(None))
        self.projMenu.addAction(self.aDeleteItem)

        # Project > Move Up
        self.aMoveUp = QAction(self.tr("Move Item Up"), self)
        self.aMoveUp.setStatusTip(self.tr("Move project item up"))
        self.aMoveUp.setShortcut("Ctrl+Up")
        self.aMoveUp.triggered.connect(lambda: self._moveTreeItem(-1))
        self.projMenu.addAction(self.aMoveUp)

        # Project > Move Down
        self.aMoveDown = QAction(self.tr("Move Item Down"), self)
        self.aMoveDown.setStatusTip(self.tr("Move project item down"))
        self.aMoveDown.setShortcut("Ctrl+Down")
        self.aMoveDown.triggered.connect(lambda: self._moveTreeItem(1))
        self.projMenu.addAction(self.aMoveDown)

        # Project > Undo Last Action
        self.aMoveUndo = QAction(self.tr("Undo Last Move"), self)
        self.aMoveUndo.setStatusTip(self.tr("Undo last item move"))
        self.aMoveUndo.setShortcut("Ctrl+Shift+Z")
        self.aMoveUndo.triggered.connect(lambda: self.theParent.treeView.undoLastMove())
        self.projMenu.addAction(self.aMoveUndo)

        # Project > Empty Trash
        self.aEmptyTrash = QAction(self.tr("Empty Trash"), self)
        self.aEmptyTrash.setStatusTip(self.tr("Permanently delete all files in the Trash folder"))
        self.aEmptyTrash.triggered.connect(lambda: self.theParent.treeView.emptyTrash())
        self.projMenu.addAction(self.aEmptyTrash)

        # Project > Separator
        self.projMenu.addSeparator()

        # Project > Exit
        self.aExitNW = QAction(self.tr("Exit"), self)
        self.aExitNW.setStatusTip(self.tr("Exit novelWriter"))
        self.aExitNW.setShortcut("Ctrl+Q")
        self.aExitNW.setMenuRole(QAction.QuitRole)
        self.aExitNW.triggered.connect(lambda: self.theParent.closeMain())
        self.projMenu.addAction(self.aExitNW)

        return

    def _buildDocumentMenu(self):
        """Assemble the Document menu.
        """
        # Document
        self.docuMenu = self.addMenu(self.tr("&Document"))

        # Document > New
        self.aNewDoc = QAction(self.tr("New Document"), self)
        self.aNewDoc.setStatusTip(self.tr("Create new document"))
        self.aNewDoc.setShortcut("Ctrl+N")
        self.aNewDoc.triggered.connect(lambda: self._newTreeItem(nwItemType.FILE, None))
        self.docuMenu.addAction(self.aNewDoc)

        # Document > Open
        self.aOpenDoc = QAction(self.tr("Open Document"), self)
        self.aOpenDoc.setStatusTip(self.tr("Open selected document"))
        self.aOpenDoc.setShortcut("Ctrl+O")
        self.aOpenDoc.triggered.connect(lambda: self.theParent.openSelectedItem())
        self.docuMenu.addAction(self.aOpenDoc)

        # Document > Save
        self.aSaveDoc = QAction(self.tr("Save Document"), self)
        self.aSaveDoc.setStatusTip(self.tr("Save current document"))
        self.aSaveDoc.setShortcut("Ctrl+S")
        self.aSaveDoc.triggered.connect(lambda: self.theParent.saveDocument())
        self.docuMenu.addAction(self.aSaveDoc)

        # Document > Close
        self.aCloseDoc = QAction(self.tr("Close Document"), self)
        self.aCloseDoc.setStatusTip(self.tr("Close current document"))
        self.aCloseDoc.setShortcut("Ctrl+W")
        self.aCloseDoc.triggered.connect(lambda: self.theParent.closeDocEditor())
        self.docuMenu.addAction(self.aCloseDoc)

        # Document > Separator
        self.docuMenu.addSeparator()

        # Document > Preview
        self.aViewDoc = QAction(self.tr("View Document"), self)
        self.aViewDoc.setStatusTip(self.tr("View document as HTML"))
        self.aViewDoc.setShortcut("Ctrl+R")
        self.aViewDoc.triggered.connect(lambda: self.theParent.viewDocument(None))
        self.docuMenu.addAction(self.aViewDoc)

        # Document > Close Preview
        self.aCloseView = QAction(self.tr("Close Document View"), self)
        self.aCloseView.setStatusTip(self.tr("Close document view pane"))
        self.aCloseView.setShortcut("Ctrl+Shift+R")
        self.aCloseView.triggered.connect(lambda: self.theParent.closeDocViewer())
        self.docuMenu.addAction(self.aCloseView)

        # Document > Separator
        self.docuMenu.addSeparator()

        # Document > Show File Details
        self.aFileDetails = QAction(self.tr("Show File Details"), self)
        self.aFileDetails.setStatusTip(
            self.tr("Shows a message box with the document location in the project folder")
        )
        self.aFileDetails.triggered.connect(lambda: self.theParent.docEditor.revealLocation())
        self.docuMenu.addAction(self.aFileDetails)

        # Document > Import From File
        self.aImportFile = QAction(self.tr("Import from File"), self)
        self.aImportFile.setStatusTip(self.tr("Import document from a text or markdown file"))
        self.aImportFile.setShortcut("Ctrl+Shift+I")
        self.aImportFile.triggered.connect(lambda: self.theParent.importDocument())
        self.docuMenu.addAction(self.aImportFile)

        # Document > Merge Documents
        self.aMergeDocs = QAction(self.tr("Merge Folder to Document"), self)
        self.aMergeDocs.setStatusTip(self.tr("Merge a folder of documents to a single document"))
        self.aMergeDocs.triggered.connect(lambda: self.theParent.mergeDocuments())
        self.docuMenu.addAction(self.aMergeDocs)

        # Document > Split Document
        self.aSplitDoc = QAction(self.tr("Split Document to Folder"), self)
        self.aSplitDoc.setStatusTip(
            self.tr("Split a document into a folder of multiple documents")
        )
        self.aSplitDoc.triggered.connect(lambda: self.theParent.splitDocument())
        self.docuMenu.addAction(self.aSplitDoc)

        return

    def _buildEditMenu(self):
        """Assemble the Edit menu.
        """
        # Edit
        self.editMenu = self.addMenu(self.tr("&Edit"))

        # Edit > Undo
        self.aEditUndo = QAction(self.tr("Undo"), self)
        self.aEditUndo.setStatusTip(self.tr("Undo last change"))
        self.aEditUndo.setShortcut("Ctrl+Z")
        self.aEditUndo.triggered.connect(lambda: self._docAction(nwDocAction.UNDO))
        self.editMenu.addAction(self.aEditUndo)

        # Edit > Redo
        self.aEditRedo = QAction(self.tr("Redo"), self)
        self.aEditRedo.setStatusTip(self.tr("Redo last change"))
        self.aEditRedo.setShortcut("Ctrl+Y")
        self.aEditRedo.triggered.connect(lambda: self._docAction(nwDocAction.REDO))
        self.editMenu.addAction(self.aEditRedo)

        # Edit > Separator
        self.editMenu.addSeparator()

        # Edit > Cut
        self.aEditCut = QAction(self.tr("Cut"), self)
        self.aEditCut.setStatusTip(self.tr("Cut selected text"))
        self.aEditCut.setShortcut("Ctrl+X")
        self.aEditCut.triggered.connect(lambda: self._docAction(nwDocAction.CUT))
        self.editMenu.addAction(self.aEditCut)

        # Edit > Copy
        self.aEditCopy = QAction(self.tr("Copy"), self)
        self.aEditCopy.setStatusTip(self.tr("Copy selected text"))
        self.aEditCopy.setShortcut("Ctrl+C")
        self.aEditCopy.triggered.connect(lambda: self._docAction(nwDocAction.COPY))
        self.editMenu.addAction(self.aEditCopy)

        # Edit > Paste
        self.aEditPaste = QAction(self.tr("Paste"), self)
        self.aEditPaste.setStatusTip(self.tr("Paste text from clipboard"))
        self.aEditPaste.setShortcut("Ctrl+V")
        self.aEditPaste.triggered.connect(lambda: self._docAction(nwDocAction.PASTE))
        self.editMenu.addAction(self.aEditPaste)

        # Edit > Separator
        self.editMenu.addSeparator()

        # Edit > Select All
        self.aSelectAll = QAction(self.tr("Select All"), self)
        self.aSelectAll.setStatusTip(self.tr("Select all text in document"))
        self.aSelectAll.setShortcut("Ctrl+A")
        self.aSelectAll.triggered.connect(lambda: self._docAction(nwDocAction.SEL_ALL))
        self.editMenu.addAction(self.aSelectAll)

        # Edit > Select Paragraph
        self.aSelectPar = QAction(self.tr("Select Paragraph"), self)
        self.aSelectPar.setStatusTip(self.tr("Select all text in paragraph"))
        self.aSelectPar.setShortcut("Ctrl+Shift+A")
        self.aSelectPar.triggered.connect(lambda: self._docAction(nwDocAction.SEL_PARA))
        self.editMenu.addAction(self.aSelectPar)

        return

    def _buildViewMenu(self):
        """Assemble the View menu.
        """
        # View
        self.viewMenu = self.addMenu(self.tr("&View"))

        # View > TreeView
        self.aFocusTree = QAction(self.tr("Focus Project Tree"), self)
        self.aFocusTree.setStatusTip(self.tr("Move focus to project tree"))
        if self.mainConf.osWindows:
            self.aFocusTree.setShortcut("Ctrl+Alt+1")
        else:
            self.aFocusTree.setShortcut("Alt+1")
        self.aFocusTree.triggered.connect(lambda: self.theParent.switchFocus(nwWidget.TREE))
        self.viewMenu.addAction(self.aFocusTree)

        # View > Document Pane 1
        self.aFocusEditor = QAction(self.tr("Focus Document Editor"), self)
        self.aFocusEditor.setStatusTip(self.tr("Move focus to left document pane"))
        if self.mainConf.osWindows:
            self.aFocusEditor.setShortcut("Ctrl+Alt+2")
        else:
            self.aFocusEditor.setShortcut("Alt+2")
        self.aFocusEditor.triggered.connect(lambda: self.theParent.switchFocus(nwWidget.EDITOR))
        self.viewMenu.addAction(self.aFocusEditor)

        # View > Document Pane 2
        self.aFocusView = QAction(self.tr("Focus Document Viewer"), self)
        self.aFocusView.setStatusTip(self.tr("Move focus to right document pane"))
        if self.mainConf.osWindows:
            self.aFocusView.setShortcut("Ctrl+Alt+3")
        else:
            self.aFocusView.setShortcut("Alt+3")
        self.aFocusView.triggered.connect(lambda: self.theParent.switchFocus(nwWidget.VIEWER))
        self.viewMenu.addAction(self.aFocusView)

        # View > Outline
        self.aFocusOutline = QAction(self.tr("Focus Outline"), self)
        self.aFocusOutline.setStatusTip(self.tr("Move focus to outline"))
        if self.mainConf.osWindows:
            self.aFocusOutline.setShortcut("Ctrl+Alt+4")
        else:
            self.aFocusOutline.setShortcut("Alt+4")
        self.aFocusOutline.triggered.connect(lambda: self.theParent.switchFocus(nwWidget.OUTLINE))
        self.viewMenu.addAction(self.aFocusOutline)

        # View > Separator
        self.viewMenu.addSeparator()

        # View > Go Backward
        self.aViewPrev = QAction(self.tr("Go Backward"), self)
        self.aViewPrev.setStatusTip(self.tr("Move backward in the view history of the right pane"))
        self.aViewPrev.setShortcut("Alt+Left")
        self.aViewPrev.triggered.connect(lambda: self.theParent.docViewer.navBackward())
        self.viewMenu.addAction(self.aViewPrev)

        # View > Go Forward
        self.aViewNext = QAction(self.tr("Go Forward"), self)
        self.aViewNext.setStatusTip(self.tr("Move forward in the view history of the right pane"))
        self.aViewNext.setShortcut("Alt+Right")
        self.aViewNext.triggered.connect(lambda: self.theParent.docViewer.navForward())
        self.viewMenu.addAction(self.aViewNext)

        # View > Separator
        self.viewMenu.addSeparator()

        # View > Focus Mode
        self.aFocusMode = QAction(self.tr("Focus Mode"), self)
        self.aFocusMode.setStatusTip(
            self.tr("Toggles a distraction free mode, only showing text editor")
        )
        self.aFocusMode.setShortcut("F8")
        self.aFocusMode.setCheckable(True)
        self.aFocusMode.setChecked(self.theParent.isFocusMode)
        self.aFocusMode.triggered.connect(lambda: self.theParent.toggleFocusMode())
        self.viewMenu.addAction(self.aFocusMode)

        # View > Toggle Full Screen
        self.aFullScreen = QAction(self.tr("Full Screen Mode"), self)
        self.aFullScreen.setStatusTip(self.tr("Maximises the main window"))
        self.aFullScreen.setShortcut("F11")
        self.aFullScreen.triggered.connect(lambda: self.theParent.toggleFullScreenMode())
        self.viewMenu.addAction(self.aFullScreen)

        return

    def _buildInsertMenu(self):
        """Assemble the Insert menu.
        """
        # Insert
        self.insertMenu = self.addMenu(self.tr("&Insert"))

        # Insert > Dashes and Dots
        self.mInsDashes = self.insertMenu.addMenu(self.tr("Dashes"))

        # Insert > Short Dash
        self.aInsENDash = QAction(self.tr("Short Dash"), self)
        self.aInsENDash.setStatusTip(self.tr("Insert short dash (en dash)"))
        self.aInsENDash.setShortcut("Ctrl+K, -")
        self.aInsENDash.triggered.connect(lambda: self._docInsert(nwUnicode.U_ENDASH))
        self.mInsDashes.addAction(self.aInsENDash)

        # Insert > Long Dash
        self.aInsEMDash = QAction(self.tr("Long Dash"), self)
        self.aInsEMDash.setStatusTip(self.tr("Insert long dash (em dash)"))
        self.aInsEMDash.setShortcut("Ctrl+K, _")
        self.aInsEMDash.triggered.connect(lambda: self._docInsert(nwUnicode.U_EMDASH))
        self.mInsDashes.addAction(self.aInsEMDash)

        # Insert > Long Dash
        self.aInsHorBar = QAction(self.tr("Horizontal Bar"), self)
        self.aInsHorBar.setStatusTip(self.tr("Insert a horizontal bar (quotation dash)"))
        self.aInsHorBar.setShortcut("Ctrl+K, Ctrl+_")
        self.aInsHorBar.triggered.connect(lambda: self._docInsert(nwUnicode.U_HBAR))
        self.mInsDashes.addAction(self.aInsHorBar)

        # Insert > Figure Dash
        self.aInsFigDash = QAction(self.tr("Figure Dash"), self)
        self.aInsFigDash.setStatusTip(
            self.tr("Insert figure dash (same width as a number character)")
        )
        self.aInsFigDash.setShortcut("Ctrl+K, ~")
        self.aInsFigDash.triggered.connect(lambda: self._docInsert(nwUnicode.U_FGDASH))
        self.mInsDashes.addAction(self.aInsFigDash)

        # Insert > Quote Marks
        self.mInsQuotes = self.insertMenu.addMenu(self.tr("Quote Marks"))

        # Insert > Left Single Quote
        self.aInsQuoteLS = QAction(self.tr("Left Single Quote"), self)
        self.aInsQuoteLS.setStatusTip(self.tr("Insert left single quote"))
        self.aInsQuoteLS.setShortcut("Ctrl+K, 1")
        self.aInsQuoteLS.triggered.connect(lambda: self._docInsert(nwDocInsert.QUOTE_LS))
        self.mInsQuotes.addAction(self.aInsQuoteLS)

        # Insert > Right Single Quote
        self.aInsQuoteRS = QAction(self.tr("Right Single Quote"), self)
        self.aInsQuoteRS.setStatusTip(self.tr("Insert right single quote"))
        self.aInsQuoteRS.setShortcut("Ctrl+K, 2")
        self.aInsQuoteRS.triggered.connect(lambda: self._docInsert(nwDocInsert.QUOTE_RS))
        self.mInsQuotes.addAction(self.aInsQuoteRS)

        # Insert > Left Double Quote
        self.aInsQuoteLD = QAction(self.tr("Left Double Quote"), self)
        self.aInsQuoteLD.setStatusTip(self.tr("Insert left double quote"))
        self.aInsQuoteLD.setShortcut("Ctrl+K, 3")
        self.aInsQuoteLD.triggered.connect(lambda: self._docInsert(nwDocInsert.QUOTE_LD))
        self.mInsQuotes.addAction(self.aInsQuoteLD)

        # Insert > Right Double Quote
        self.aInsQuoteRD = QAction(self.tr("Right Double Quote"), self)
        self.aInsQuoteRD.setStatusTip(self.tr("Insert right double quote"))
        self.aInsQuoteRD.setShortcut("Ctrl+K, 4")
        self.aInsQuoteRD.triggered.connect(lambda: self._docInsert(nwDocInsert.QUOTE_RD))
        self.mInsQuotes.addAction(self.aInsQuoteRD)

        # Insert > Alternative Apostrophe
        self.aInsMSApos = QAction(self.tr("Alternative Apostrophe"), self)
        self.aInsMSApos.setStatusTip(self.tr("Insert modifier letter single apostrophe"))
        self.aInsMSApos.setShortcut("Ctrl+K, '")
        self.aInsMSApos.triggered.connect(lambda: self._docInsert(nwUnicode.U_MAPOSS))
        self.mInsQuotes.addAction(self.aInsMSApos)

        # Insert > Symbols
        self.mInsPunct = self.insertMenu.addMenu(self.tr("General Punctuation"))

        # Insert > Ellipsis
        self.aInsEllipsis = QAction(self.tr("Ellipsis"), self)
        self.aInsEllipsis.setStatusTip(self.tr("Insert ellipsis"))
        self.aInsEllipsis.setShortcut("Ctrl+K, .")
        self.aInsEllipsis.triggered.connect(lambda: self._docInsert(nwUnicode.U_HELLIP))
        self.mInsPunct.addAction(self.aInsEllipsis)

        # Insert > Prime
        self.aInsPrime = QAction(self.tr("Prime"), self)
        self.aInsPrime.setStatusTip(self.tr("Insert a prime symbol"))
        self.aInsPrime.setShortcut("Ctrl+K, Ctrl+'")
        self.aInsPrime.triggered.connect(lambda: self._docInsert(nwUnicode.U_PRIME))
        self.mInsPunct.addAction(self.aInsPrime)

        # Insert > Double Prime
        self.aInsDPrime = QAction(self.tr("Double Prime"), self)
        self.aInsDPrime.setStatusTip(self.tr("Insert a double prime symbol"))
        self.aInsDPrime.setShortcut("Ctrl+K, Ctrl+\"")
        self.aInsDPrime.triggered.connect(lambda: self._docInsert(nwUnicode.U_DPRIME))
        self.mInsPunct.addAction(self.aInsDPrime)

        # Insert > White Spaces
        self.mInsBreaks = self.insertMenu.addMenu(self.tr("White Spaces"))

        # Insert > Non-Breaking Space
        self.aInsNBSpace = QAction(self.tr("Non-Breaking Space"), self)
        self.aInsNBSpace.setStatusTip(self.tr("Insert a non-breaking space"))
        self.aInsNBSpace.setShortcut("Ctrl+K, Space")
        self.aInsNBSpace.triggered.connect(lambda: self._docInsert(nwUnicode.U_NBSP))
        self.mInsBreaks.addAction(self.aInsNBSpace)

        # Insert > Thin Space
        self.aInsThinSpace = QAction(self.tr("Thin Space"), self)
        self.aInsThinSpace.setStatusTip(self.tr("Insert a thin space"))
        self.aInsThinSpace.setShortcut("Ctrl+K, Shift+Space")
        self.aInsThinSpace.triggered.connect(lambda: self._docInsert(nwUnicode.U_THSP))
        self.mInsBreaks.addAction(self.aInsThinSpace)

        # Insert > Thin Non-Breaking Space
        self.aInsThinNBSpace = QAction(self.tr("Thin Non-Breaking Space"), self)
        self.aInsThinNBSpace.setStatusTip(self.tr("Insert a thin non-breaking space"))
        self.aInsThinNBSpace.setShortcut("Ctrl+K, Ctrl+Space")
        self.aInsThinNBSpace.triggered.connect(lambda: self._docInsert(nwUnicode.U_THNBSP))
        self.mInsBreaks.addAction(self.aInsThinNBSpace)

        # Insert > Symbols
        self.mInsSymbol = self.insertMenu.addMenu(self.tr("Other Symbols"))

        # Insert > List Bullet
        self.aInsBullet = QAction(self.tr("List Bullet"), self)
        self.aInsBullet.setStatusTip(self.tr("Insert a list bullet"))
        self.aInsBullet.setShortcut("Ctrl+K, *")
        self.aInsBullet.triggered.connect(lambda: self._docInsert(nwUnicode.U_BULL))
        self.mInsSymbol.addAction(self.aInsBullet)

        # Insert > Hyphen Bullet
        self.aInsHyBull = QAction(self.tr("Hyphen Bullet"), self)
        self.aInsHyBull.setStatusTip(self.tr("Insert a hyphen bullet (alternative bullet)"))
        self.aInsHyBull.setShortcut("Ctrl+K, Ctrl+-")
        self.aInsHyBull.triggered.connect(lambda: self._docInsert(nwUnicode.U_HYBULL))
        self.mInsSymbol.addAction(self.aInsHyBull)

        # Insert > Flower Mark
        self.aInsFlower = QAction(self.tr("Flower Mark"), self)
        self.aInsFlower.setStatusTip(self.tr("Insert a flower mark (alternative bullet)"))
        self.aInsFlower.setShortcut("Ctrl+K, Ctrl+*")
        self.aInsFlower.triggered.connect(lambda: self._docInsert(nwUnicode.U_FLOWER))
        self.mInsSymbol.addAction(self.aInsFlower)

        # Insert > Per Mille
        self.aInsPerMille = QAction(self.tr("Per Mille"), self)
        self.aInsPerMille.setStatusTip(self.tr("Insert a per mille symbol"))
        self.aInsPerMille.setShortcut("Ctrl+K, %")
        self.aInsPerMille.triggered.connect(lambda: self._docInsert(nwUnicode.U_PERMIL))
        self.mInsSymbol.addAction(self.aInsPerMille)

        # Insert > Degree Symbol
        self.aInsDegree = QAction(self.tr("Degree Symbol"), self)
        self.aInsDegree.setStatusTip(self.tr("Insert a degree symbol"))
        self.aInsDegree.setShortcut("Ctrl+K, Ctrl+O")
        self.aInsDegree.triggered.connect(lambda: self._docInsert(nwUnicode.U_DEGREE))
        self.mInsSymbol.addAction(self.aInsDegree)

        # Insert > Minus Sign
        self.aInsMinus = QAction(self.tr("Minus Sign"), self)
        self.aInsMinus.setStatusTip(self.tr("Insert a minus sign (not a hypen or dash)"))
        self.aInsMinus.setShortcut("Ctrl+K, Ctrl+M")
        self.aInsMinus.triggered.connect(lambda: self._docInsert(nwUnicode.U_MINUS))
        self.mInsSymbol.addAction(self.aInsMinus)

        # Insert > Times Sign
        self.aInsTimes = QAction(self.tr("Times Sign"), self)
        self.aInsTimes.setStatusTip(self.tr("Insert a times sign (multiplication cross)"))
        self.aInsTimes.setShortcut("Ctrl+K, Ctrl+X")
        self.aInsTimes.triggered.connect(lambda: self._docInsert(nwUnicode.U_TIMES))
        self.mInsSymbol.addAction(self.aInsTimes)

        # Insert > Division
        self.aInsDivide = QAction(self.tr("Division Sign"), self)
        self.aInsDivide.setStatusTip(self.tr("Insert a division sign"))
        self.aInsDivide.setShortcut("Ctrl+K, Ctrl+D")
        self.aInsDivide.triggered.connect(lambda: self._docInsert(nwUnicode.U_DIVIDE))
        self.mInsSymbol.addAction(self.aInsDivide)

        # Insert > Separator
        self.insertMenu.addSeparator()

        # Insert > Tags and References
        self.mInsKeywords = self.insertMenu.addMenu(self.tr("Tags and References"))
        self.mInsKWItems = {}
        self.mInsKWItems[nwKeyWords.TAG_KEY]    = (QAction(self.mInsKeywords), "Ctrl+K, G")
        self.mInsKWItems[nwKeyWords.POV_KEY]    = (QAction(self.mInsKeywords), "Ctrl+K, V")
        self.mInsKWItems[nwKeyWords.FOCUS_KEY]  = (QAction(self.mInsKeywords), "Ctrl+K, F")
        self.mInsKWItems[nwKeyWords.CHAR_KEY]   = (QAction(self.mInsKeywords), "Ctrl+K, C")
        self.mInsKWItems[nwKeyWords.PLOT_KEY]   = (QAction(self.mInsKeywords), "Ctrl+K, P")
        self.mInsKWItems[nwKeyWords.TIME_KEY]   = (QAction(self.mInsKeywords), "Ctrl+K, T")
        self.mInsKWItems[nwKeyWords.WORLD_KEY]  = (QAction(self.mInsKeywords), "Ctrl+K, L")
        self.mInsKWItems[nwKeyWords.OBJECT_KEY] = (QAction(self.mInsKeywords), "Ctrl+K, O")
        self.mInsKWItems[nwKeyWords.ENTITY_KEY] = (QAction(self.mInsKeywords), "Ctrl+K, E")
        self.mInsKWItems[nwKeyWords.CUSTOM_KEY] = (QAction(self.mInsKeywords), "Ctrl+K, X")
        for n, keyWord in enumerate(self.mInsKWItems):
            self.mInsKWItems[keyWord][0].setText(trConst(nwLabels.KEY_NAME[keyWord]))
            self.mInsKWItems[keyWord][0].setShortcut(self.mInsKWItems[keyWord][1])
            self.mInsKWItems[keyWord][0].triggered.connect(
                lambda n, keyWord=keyWord: self._insertKeyWord(keyWord)
            )
            self.mInsKeywords.addAction(self.mInsKWItems[keyWord][0])

        return

    def _buildFormatMenu(self):
        """Assemble the Format menu.
        """
        # Format
        self.fmtMenu = self.addMenu(self.tr("&Format"))

        # Format > Emphasis
        self.aFmtEmph = QAction(self.tr("Emphasis"), self)
        self.aFmtEmph.setStatusTip(self.tr("Add emphasis to selected text (italic)"))
        self.aFmtEmph.setShortcut("Ctrl+I")
        self.aFmtEmph.triggered.connect(lambda: self._docAction(nwDocAction.EMPH))
        self.fmtMenu.addAction(self.aFmtEmph)

        # Format > Strong Emphasis
        self.aFmtStrong = QAction(self.tr("Strong Emphasis"), self)
        self.aFmtStrong.setStatusTip(self.tr("Add strong emphasis to selected text (bold)"))
        self.aFmtStrong.setShortcut("Ctrl+B")
        self.aFmtStrong.triggered.connect(lambda: self._docAction(nwDocAction.STRONG))
        self.fmtMenu.addAction(self.aFmtStrong)

        # Format > Strikethrough
        self.aFmtStrike = QAction(self.tr("Strikethrough"), self)
        self.aFmtStrike.setStatusTip(self.tr("Add strikethrough to selected text"))
        self.aFmtStrike.setShortcut("Ctrl+D")
        self.aFmtStrike.triggered.connect(lambda: self._docAction(nwDocAction.STRIKE))
        self.fmtMenu.addAction(self.aFmtStrike)

        # Edit > Separator
        self.fmtMenu.addSeparator()

        # Format > Double Quotes
        self.aFmtDQuote = QAction(self.tr("Wrap Double Quotes"), self)
        self.aFmtDQuote.setStatusTip(self.tr("Wrap selected text in double quotes"))
        self.aFmtDQuote.setShortcut("Ctrl+\"")
        self.aFmtDQuote.triggered.connect(lambda: self._docAction(nwDocAction.D_QUOTE))
        self.fmtMenu.addAction(self.aFmtDQuote)

        # Format > Single Quotes
        self.aFmtSQuote = QAction(self.tr("Wrap Single Quotes"), self)
        self.aFmtSQuote.setStatusTip(self.tr("Wrap selected text in single quotes"))
        self.aFmtSQuote.setShortcut("Ctrl+'")
        self.aFmtSQuote.triggered.connect(lambda: self._docAction(nwDocAction.S_QUOTE))
        self.fmtMenu.addAction(self.aFmtSQuote)

        # Format > Separator
        self.fmtMenu.addSeparator()

        # Format > Header 1
        self.aFmtHead1 = QAction(self.tr("Header 1"), self)
        self.aFmtHead1.setStatusTip(self.tr("Change the block format to Header 1"))
        self.aFmtHead1.setShortcut("Ctrl+1")
        self.aFmtHead1.triggered.connect(lambda: self._docAction(nwDocAction.BLOCK_H1))
        self.fmtMenu.addAction(self.aFmtHead1)

        # Format > Header 2
        self.aFmtHead2 = QAction(self.tr("Header 2"), self)
        self.aFmtHead2.setStatusTip(self.tr("Change the block format to Header 2"))
        self.aFmtHead2.setShortcut("Ctrl+2")
        self.aFmtHead2.triggered.connect(lambda: self._docAction(nwDocAction.BLOCK_H2))
        self.fmtMenu.addAction(self.aFmtHead2)

        # Format > Header 3
        self.aFmtHead3 = QAction(self.tr("Header 3"), self)
        self.aFmtHead3.setStatusTip(self.tr("Change the block format to Header 3"))
        self.aFmtHead3.setShortcut("Ctrl+3")
        self.aFmtHead3.triggered.connect(lambda: self._docAction(nwDocAction.BLOCK_H3))
        self.fmtMenu.addAction(self.aFmtHead3)

        # Format > Header 4
        self.aFmtHead4 = QAction(self.tr("Header 4"), self)
        self.aFmtHead4.setStatusTip(self.tr("Change the block format to Header 4"))
        self.aFmtHead4.setShortcut("Ctrl+4")
        self.aFmtHead4.triggered.connect(lambda: self._docAction(nwDocAction.BLOCK_H4))
        self.fmtMenu.addAction(self.aFmtHead4)

        # Format > Separator
        self.fmtMenu.addSeparator()

        # Format > Align Left
        self.aFmtAlignLeft = QAction(self.tr("Align Left"), self)
        self.aFmtAlignLeft.setStatusTip(self.tr("Change the block alignment to left"))
        self.aFmtAlignLeft.setShortcut("Ctrl+5")
        self.aFmtAlignLeft.triggered.connect(lambda: self._docAction(nwDocAction.ALIGN_L))
        self.fmtMenu.addAction(self.aFmtAlignLeft)

        # Format > Align Centre
        self.aFmtAlignCentre = QAction(self.tr("Align Centre"), self)
        self.aFmtAlignCentre.setStatusTip(self.tr("Change the block alignment to centre"))
        self.aFmtAlignCentre.setShortcut("Ctrl+6")
        self.aFmtAlignCentre.triggered.connect(lambda: self._docAction(nwDocAction.ALIGN_C))
        self.fmtMenu.addAction(self.aFmtAlignCentre)

        # Format > Align Right
        self.aFmtAlignRight = QAction(self.tr("Align Right"), self)
        self.aFmtAlignRight.setStatusTip(self.tr("Change the block alignment to right"))
        self.aFmtAlignRight.setShortcut("Ctrl+7")
        self.aFmtAlignRight.triggered.connect(lambda: self._docAction(nwDocAction.ALIGN_R))
        self.fmtMenu.addAction(self.aFmtAlignRight)

        # Format > Separator
        self.fmtMenu.addSeparator()

        # Format > Indent Left
        self.aFmtIndentLeft = QAction(self.tr("Indent Left"), self)
        self.aFmtIndentLeft.setStatusTip(self.tr("Increase the block's left margin"))
        self.aFmtIndentLeft.setShortcut("Ctrl+8")
        self.aFmtIndentLeft.triggered.connect(lambda: self._docAction(nwDocAction.INDENT_L))
        self.fmtMenu.addAction(self.aFmtIndentLeft)

        # Format > Indent Right
        self.aFmtIndentRight = QAction(self.tr("Indent Right"), self)
        self.aFmtIndentRight.setStatusTip(self.tr("Increase the block's right margin"))
        self.aFmtIndentRight.setShortcut("Ctrl+9")
        self.aFmtIndentRight.triggered.connect(lambda: self._docAction(nwDocAction.INDENT_R))
        self.fmtMenu.addAction(self.aFmtIndentRight)

        # Format > Separator
        self.fmtMenu.addSeparator()

        # Format > Comment
        self.aFmtComment = QAction(self.tr("Comment"), self)
        self.aFmtComment.setStatusTip(self.tr("Change the block format to comment"))
        self.aFmtComment.setShortcut("Ctrl+/")
        self.aFmtComment.triggered.connect(lambda: self._docAction(nwDocAction.BLOCK_COM))
        self.fmtMenu.addAction(self.aFmtComment)

        # Format > Remove Block Format
        self.aFmtNoFormat = QAction(self.tr("Remove Block Format"), self)
        self.aFmtNoFormat.setStatusTip(self.tr("Strips block format"))
        self.aFmtNoFormat.setShortcuts(["Ctrl+0", "Ctrl+Shift+/"])
        self.aFmtNoFormat.triggered.connect(lambda: self._docAction(nwDocAction.BLOCK_TXT))
        self.fmtMenu.addAction(self.aFmtNoFormat)

        # Format > Separator
        self.fmtMenu.addSeparator()

        # Format > Replace Single Quotes
        self.aFmtReplSng = QAction(self.tr("Replace Single Quotes"), self)
        self.aFmtReplSng.setStatusTip(
            self.tr("Replace all straight single quotes in selected text")
        )
        self.aFmtReplSng.triggered.connect(lambda: self._docAction(nwDocAction.REPL_SNG))
        self.fmtMenu.addAction(self.aFmtReplSng)

        # Format > Replace Double Quotes
        self.aFmtReplDbl = QAction(self.tr("Replace Double Quotes"), self)
        self.aFmtReplDbl.setStatusTip(
            self.tr("Replace all straight double quotes in selected text")
        )
        self.aFmtReplDbl.triggered.connect(lambda: self._docAction(nwDocAction.REPL_DBL))
        self.fmtMenu.addAction(self.aFmtReplDbl)

        # Format > Remove In-Paragraph Breaks
        self.aFmtRmBreaks = QAction(self.tr("Remove In-Paragraph Breaks"), self)
        self.aFmtRmBreaks.setStatusTip(
            self.tr("Removes all line breaks within paragraphs in the selected text")
        )
        self.aFmtRmBreaks.triggered.connect(lambda: self._docAction(nwDocAction.RM_BREAKS))
        self.fmtMenu.addAction(self.aFmtRmBreaks)

        return

    def _buildSearchMenu(self):
        """Assemble the Search menu.
        """
        # Search
        self.srcMenu = self.addMenu(self.tr("&Search"))

        # Search > Find
        self.aFind = QAction(self.tr("Find"), self)
        self.aFind.setStatusTip(self.tr("Find text in document"))
        self.aFind.setShortcut("Ctrl+F")
        self.aFind.triggered.connect(lambda: self.theParent.docEditor.beginSearch())
        self.srcMenu.addAction(self.aFind)

        # Search > Replace
        self.aReplace = QAction(self.tr("Replace"), self)
        self.aReplace.setStatusTip(self.tr("Replace text in document"))
        if self.mainConf.osDarwin:
            self.aReplace.setShortcut("Ctrl+=")
        else:
            self.aReplace.setShortcut("Ctrl+H")
        self.aReplace.triggered.connect(lambda: self.theParent.docEditor.beginReplace())
        self.srcMenu.addAction(self.aReplace)

        # Search > Find Next
        self.aFindNext = QAction(self.tr("Find Next"), self)
        self.aFindNext.setStatusTip(self.tr("Find next occurrence of text in document"))
        if self.mainConf.osDarwin:
            self.aFindNext.setShortcuts(["Ctrl+G", "F3"])
        else:
            self.aFindNext.setShortcuts(["F3", "Ctrl+G"])
        self.aFindNext.triggered.connect(lambda: self.theParent.docEditor.findNext())
        self.srcMenu.addAction(self.aFindNext)

        # Search > Find Prev
        self.aFindPrev = QAction(self.tr("Find Previous"), self)
        self.aFindPrev.setStatusTip(self.tr("Find previous occurrence of text in document"))
        if self.mainConf.osDarwin:
            self.aFindPrev.setShortcuts(["Ctrl+Shift+G", "Shift+F3"])
        else:
            self.aFindPrev.setShortcuts(["Shift+F3", "Ctrl+Shift+G"])
        self.aFindPrev.triggered.connect(lambda: self.theParent.docEditor.findNext(goBack=True))
        self.srcMenu.addAction(self.aFindPrev)

        # Search > Replace Next
        self.aReplaceNext = QAction(self.tr("Replace Next"), self)
        self.aReplaceNext.setStatusTip(
            self.tr("Find and replace next occurrence of text in document")
        )
        self.aReplaceNext.setShortcut("Ctrl+Shift+1")
        self.aReplaceNext.triggered.connect(lambda: self.theParent.docEditor.replaceNext())
        self.srcMenu.addAction(self.aReplaceNext)

        return

    def _buildToolsMenu(self):
        """Assemble the Tools menu.
        """
        # Tools
        self.toolsMenu = self.addMenu(self.tr("&Tools"))

        # Tools > Check Spelling
        self.aSpellCheck = QAction(self.tr("Check Spelling"), self)
        self.aSpellCheck.setStatusTip(self.tr("Toggle check spelling"))
        self.aSpellCheck.setCheckable(True)
        self.aSpellCheck.setChecked(self.theProject.spellCheck)
        self.aSpellCheck.triggered.connect(self._toggleSpellCheck) # triggered, not toggled!
        self.aSpellCheck.setShortcut("Ctrl+F7")
        self.toolsMenu.addAction(self.aSpellCheck)

        # Tools > Re-Run Spell Check
        self.aReRunSpell = QAction(self.tr("Re-Run Spell Check"), self)
        self.aReRunSpell.setStatusTip(self.tr("Run the spell checker on current document"))
        self.aReRunSpell.setShortcut("F7")
        self.aReRunSpell.triggered.connect(lambda: self.theParent.docEditor.spellCheckDocument())
        self.toolsMenu.addAction(self.aReRunSpell)

        # Tools > Project Word List
        self.aEditWordList = QAction(self.tr("Project Word List"), self)
        self.aEditWordList.setStatusTip(self.tr("Edit the project's word list"))
        self.aEditWordList.triggered.connect(lambda: self.theParent.showProjectWordListDialog())
        self.toolsMenu.addAction(self.aEditWordList)

        # Tools > Separator
        self.toolsMenu.addSeparator()

        # Tools > Rebuild Indices
        self.aRebuildIndex = QAction(self.tr("Rebuild Index"), self)
        self.aRebuildIndex.setStatusTip(self.tr("Rebuild the tag indices and word counts"))
        self.aRebuildIndex.setShortcut("F9")
        self.aRebuildIndex.triggered.connect(lambda: self.theParent.rebuildIndex())
        self.toolsMenu.addAction(self.aRebuildIndex)

        # Tools > Rebuild Outline
        self.aRebuildOutline = QAction(self.tr("Rebuild Outline"), self)
        self.aRebuildOutline.setStatusTip(self.tr("Rebuild the novel outline tree"))
        self.aRebuildOutline.setShortcut("F10")
        self.aRebuildOutline.triggered.connect(lambda: self.theParent.rebuildOutline())
        self.toolsMenu.addAction(self.aRebuildOutline)

        # Tools > Toggle Auto Build Outline
        self.aAutoOutline = QAction(self.tr("Auto-Update Outline"), self)
        self.aAutoOutline.setStatusTip(
            self.tr("Update project outline when a novel file is changed")
        )
        self.aAutoOutline.setCheckable(True)
        self.aAutoOutline.toggled.connect(self._toggleAutoOutline)
        self.aAutoOutline.setShortcut("Ctrl+F10")
        self.toolsMenu.addAction(self.aAutoOutline)

        # Tools > Separator
        self.toolsMenu.addSeparator()

        # Tools > Backup
        self.aBackupProject = QAction(self.tr("Backup Project Folder"), self)
        self.aBackupProject.setStatusTip(self.tr("Backup Project"))
        self.aBackupProject.triggered.connect(lambda: self.theProject.zipIt(True))
        self.toolsMenu.addAction(self.aBackupProject)

        # Tools > Export Project
        self.aBuildProject = QAction(self.tr("Build Novel Project"), self)
        self.aBuildProject.setStatusTip(self.tr("Launch the Build novel project tool"))
        self.aBuildProject.setShortcut("F5")
        self.aBuildProject.triggered.connect(lambda: self.theParent.showBuildProjectDialog())
        self.toolsMenu.addAction(self.aBuildProject)

        # Tools > Writing Stats
        self.aWritingStats = QAction(self.tr("Writing Statistics"), self)
        self.aWritingStats.setStatusTip(self.tr("Show the writing statistics dialogue"))
        self.aWritingStats.setShortcut("F6")
        self.aWritingStats.triggered.connect(lambda: self.theParent.showWritingStatsDialog())
        self.toolsMenu.addAction(self.aWritingStats)

        # Tools > Settings
        self.aPreferences = QAction(self.tr("Preferences"), self)
        self.aPreferences.setStatusTip(self.tr("Preferences"))
        self.aPreferences.setShortcut("Ctrl+,")
        self.aPreferences.setMenuRole(QAction.PreferencesRole)
        self.aPreferences.triggered.connect(lambda: self.theParent.showPreferencesDialog())
        self.toolsMenu.addAction(self.aPreferences)

        return

    def _buildHelpMenu(self):
        """Assemble the Help menu.
        """
        # Help
        self.helpMenu = self.addMenu(self.tr("&Help"))

        # Help > About
        self.aAboutNW = QAction(self.tr("About novelWriter"), self)
        self.aAboutNW.setStatusTip(self.tr("About novelWriter"))
        self.aAboutNW.setMenuRole(QAction.AboutRole)
        self.aAboutNW.triggered.connect(lambda: self.theParent.showAboutNWDialog())
        self.helpMenu.addAction(self.aAboutNW)

        # Help > About Qt5
        self.aAboutQt = QAction(self.tr("About Qt5"), self)
        self.aAboutQt.setStatusTip(self.tr("About Qt5"))
        self.aAboutQt.setMenuRole(QAction.AboutQtRole)
        self.aAboutQt.triggered.connect(lambda: self.theParent.showAboutQtDialog())
        self.helpMenu.addAction(self.aAboutQt)

        # Help > Separator
        self.helpMenu.addSeparator()

        # Document > Documentation
        if self.mainConf.hasHelp and self.mainConf.hasAssistant:
            self.aHelpLoc = QAction(self.tr("Documentation (Local)"), self)
            self.aHelpLoc.setStatusTip(self.tr("View local documentation with Qt Assistant"))
            self.aHelpLoc.triggered.connect(self._openAssistant)
            self.aHelpLoc.setShortcut("F1")
            self.helpMenu.addAction(self.aHelpLoc)

        self.aHelpWeb = QAction(self.tr("Documentation (Online)"), self)
        self.aHelpWeb.setStatusTip(
            self.tr("View online documentation at {0}").format(nw.__docurl__)
        )
        self.aHelpWeb.triggered.connect(lambda: self._openWebsite(nw.__docurl__))
        if self.mainConf.hasHelp and self.mainConf.hasAssistant:
            self.aHelpWeb.setShortcut("Shift+F1")
        else:
            self.aHelpWeb.setShortcuts(["F1", "Shift+F1"])
        self.helpMenu.addAction(self.aHelpWeb)

        # Help > Separator
        self.helpMenu.addSeparator()

        # Document > Report an Issue
        self.aIssue = QAction(self.tr("Report an Issue (GitHub)"), self)
        self.aIssue.setStatusTip(
            self.tr("Report a bug or issue on GitHub at {0}").format(nw.__issuesurl__)
        )
        self.aIssue.triggered.connect(lambda: self._openWebsite(nw.__issuesurl__))
        self.helpMenu.addAction(self.aIssue)

        # Document > Ask a Question
        self.aQuestion = QAction(self.tr("Ask a Question (GitHub)"), self)
        self.aQuestion.setStatusTip(
            self.tr("Ask a question on GitHub at {0}").format(nw.__helpurl__)
        )
        self.aQuestion.triggered.connect(lambda: self._openWebsite(nw.__helpurl__))
        self.helpMenu.addAction(self.aQuestion)

        # Document > Latest Release
        self.aRelease = QAction(self.tr("Latest Release (GitHub)"), self)
        self.aRelease.setStatusTip(
            self.tr("Open the Releases page on GitHub at {0}").format(nw.__releaseurl__)
        )
        self.aRelease.triggered.connect(lambda: self._openWebsite(nw.__releaseurl__))
        self.helpMenu.addAction(self.aRelease)

        # Document > Main Website
        self.aWebsite = QAction(self.tr("The novelWriter Website"), self)
        self.aWebsite.setStatusTip(
            self.tr("Open the novelWriter website at {0}").format(nw.__url__)
        )
        self.aWebsite.triggered.connect(lambda: self._openWebsite(nw.__url__))
        self.helpMenu.addAction(self.aWebsite)

        return

# END Class GuiMainMenu
