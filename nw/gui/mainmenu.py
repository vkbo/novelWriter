# -*- coding: utf-8 -*-
"""novelWriter GUI Main Menu

 novelWriter – GUI Main Menu
=============================
 Class holding the main window menu

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

from nw.constants import (
    nwItemType, nwItemClass, nwDocAction, nwDocInsert, nwKeyWords, nwLabels
)

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
        """Set the spell check check box to theMode. This is controlled
        by the document editor class, which holds the master spell check
        flag.
        """
        self.aSpellCheck.setChecked(theMode)
        return

    def setAutoOutline(self, theMode):
        """Set the auto outline check box to theMode. Used during
        initialisation.
        """
        self.aAutoOutline.setChecked(theMode)
        return

    ##
    #  Menu Action
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
        """Open an URL in the system's default browser.
        """
        QDesktopServices.openUrl(QUrl(theUrl))
        return True

    def _openIssue(self):
        """Open the issue tracker URL in the system's default browser.
        """
        QDesktopServices.openUrl(QUrl(nw.__issuesurl__))
        return True

    ##
    #  Menu Builders
    ##

    def _buildProjectMenu(self):
        """Assemble the Project menu.
        """
        # Project
        self.projMenu = self.addMenu("&Project")

        # Project > New Project
        self.aNewProject = QAction("New Project", self)
        self.aNewProject.setStatusTip("Create new project")
        self.aNewProject.triggered.connect(lambda: self.theParent.newProject(None))
        self.projMenu.addAction(self.aNewProject)

        # Project > Open Project
        self.aOpenProject = QAction("Open Project", self)
        self.aOpenProject.setStatusTip("Open project")
        self.aOpenProject.setShortcut("Ctrl+Shift+O")
        self.aOpenProject.triggered.connect(lambda: self.theParent.showProjectLoadDialog())
        self.projMenu.addAction(self.aOpenProject)

        # Project > Save Project
        self.aSaveProject = QAction("Save Project", self)
        self.aSaveProject.setStatusTip("Save project")
        self.aSaveProject.setShortcut("Ctrl+Shift+S")
        self.aSaveProject.triggered.connect(lambda: self.theParent.saveProject())
        self.projMenu.addAction(self.aSaveProject)

        # Project > Close Project
        self.aCloseProject = QAction("Close Project", self)
        self.aCloseProject.setStatusTip("Close project")
        self.aCloseProject.setShortcut("Ctrl+Shift+W")
        self.aCloseProject.triggered.connect(lambda: self.theParent.closeProject(False))
        self.projMenu.addAction(self.aCloseProject)

        # Project > Project Settings
        self.aProjectSettings = QAction("Project Settings", self)
        self.aProjectSettings.setStatusTip("Project settings")
        self.aProjectSettings.setShortcut("Ctrl+Shift+,")
        self.aProjectSettings.triggered.connect(lambda: self.theParent.showProjectSettingsDialog())
        self.projMenu.addAction(self.aProjectSettings)

        # Project > Separator
        self.projMenu.addSeparator()

        # Project > New Root
        self.rootMenu = self.projMenu.addMenu("Create Root Folder")
        self.rootItems = {}
        self.rootItems[nwItemClass.NOVEL]     = QAction("Novel Root",     self.rootMenu)
        self.rootItems[nwItemClass.PLOT]      = QAction("Plot Root",      self.rootMenu)
        self.rootItems[nwItemClass.CHARACTER] = QAction("Character Root", self.rootMenu)
        self.rootItems[nwItemClass.WORLD]     = QAction("Location Root",  self.rootMenu)
        self.rootItems[nwItemClass.TIMELINE]  = QAction("Timeline Root",  self.rootMenu)
        self.rootItems[nwItemClass.OBJECT]    = QAction("Object Root",    self.rootMenu)
        self.rootItems[nwItemClass.ENTITY]    = QAction("Entity Root",    self.rootMenu)
        self.rootItems[nwItemClass.CUSTOM]    = QAction("Custom Root",    self.rootMenu)
        self.rootItems[nwItemClass.ARCHIVE]   = QAction("Outtakes Root",  self.rootMenu)
        nCount = 0
        for itemClass in self.rootItems.keys():
            nCount += 1 # This forces the lambdas to be unique
            self.rootItems[itemClass].triggered.connect(
                lambda nCount, itemClass=itemClass: self._newTreeItem(nwItemType.ROOT, itemClass)
            )
            self.rootMenu.addAction(self.rootItems[itemClass])

        # Project > New Folder
        self.aCreateFolder = QAction("Create Folder", self)
        self.aCreateFolder.setStatusTip("Create folder")
        self.aCreateFolder.setShortcut("Ctrl+Shift+N")
        self.aCreateFolder.triggered.connect(lambda: self._newTreeItem(nwItemType.FOLDER, None))
        self.projMenu.addAction(self.aCreateFolder)

        # Project > Separator
        self.projMenu.addSeparator()

        # Project > Edit
        self.aEditItem = QAction("Edit Project Item", self)
        self.aEditItem.setStatusTip("Change item settings")
        self.aEditItem.setShortcuts(["Ctrl+E", "F2"])
        self.aEditItem.triggered.connect(lambda: self.theParent.editItem(None))
        self.projMenu.addAction(self.aEditItem)

        # Project > Delete
        self.aDeleteItem = QAction("Delete Project Item", self)
        self.aDeleteItem.setStatusTip("Delete selected item")
        self.aDeleteItem.setShortcut("Ctrl+Del")
        self.aDeleteItem.triggered.connect(lambda: self.theParent.treeView.deleteItem(None))
        self.projMenu.addAction(self.aDeleteItem)

        # Project > Empty Trash
        self.aEmptyTrash = QAction("Empty Trash", self)
        self.aEmptyTrash.setStatusTip("Permanently delete all files in the Trash folder")
        self.aEmptyTrash.triggered.connect(lambda: self.theParent.treeView.emptyTrash())
        self.projMenu.addAction(self.aEmptyTrash)

        # Project > Separator
        self.projMenu.addSeparator()

        # Project > Exit
        self.aExitNW = QAction("Exit", self)
        self.aExitNW.setStatusTip("Exit novelWriter")
        self.aExitNW.setShortcut("Ctrl+Q")
        self.aExitNW.setMenuRole(QAction.QuitRole)
        self.aExitNW.triggered.connect(lambda: self.theParent.closeMain())
        self.projMenu.addAction(self.aExitNW)

        return

    def _buildDocumentMenu(self):
        """Assemble the Document menu.
        """
        # Document
        self.docuMenu = self.addMenu("&Document")

        # Document > New
        self.aNewDoc = QAction("New Document", self)
        self.aNewDoc.setStatusTip("Create new document")
        self.aNewDoc.setShortcut("Ctrl+N")
        self.aNewDoc.triggered.connect(lambda: self._newTreeItem(nwItemType.FILE, None))
        self.docuMenu.addAction(self.aNewDoc)

        # Document > Open
        self.aOpenDoc = QAction("Open Document", self)
        self.aOpenDoc.setStatusTip("Open selected document")
        self.aOpenDoc.setShortcut("Ctrl+O")
        self.aOpenDoc.triggered.connect(lambda: self.theParent.openSelectedItem())
        self.docuMenu.addAction(self.aOpenDoc)

        # Document > Save
        self.aSaveDoc = QAction("Save Document", self)
        self.aSaveDoc.setStatusTip("Save current document")
        self.aSaveDoc.setShortcut("Ctrl+S")
        self.aSaveDoc.triggered.connect(lambda: self.theParent.saveDocument())
        self.docuMenu.addAction(self.aSaveDoc)

        # Document > Close
        self.aCloseDoc = QAction("Close Document", self)
        self.aCloseDoc.setStatusTip("Close current document")
        self.aCloseDoc.setShortcut("Ctrl+W")
        self.aCloseDoc.triggered.connect(lambda: self.theParent.closeDocEditor())
        self.docuMenu.addAction(self.aCloseDoc)

        # Document > Separator
        self.docuMenu.addSeparator()

        # Document > Preview
        self.aViewDoc = QAction("View Document", self)
        self.aViewDoc.setStatusTip("View document as HTML")
        self.aViewDoc.setShortcut("Ctrl+R")
        self.aViewDoc.triggered.connect(lambda: self.theParent.viewDocument(None))
        self.docuMenu.addAction(self.aViewDoc)

        # Document > Close Preview
        self.aCloseView = QAction("Close Document View", self)
        self.aCloseView.setStatusTip("Close document view pane")
        self.aCloseView.setShortcut("Ctrl+Shift+R")
        self.aCloseView.triggered.connect(lambda: self.theParent.closeDocViewer())
        self.docuMenu.addAction(self.aCloseView)

        # Document > Separator
        self.docuMenu.addSeparator()

        # Document > Show File Details
        self.aFileDetails = QAction("Show File Details", self)
        self.aFileDetails.setStatusTip(
            "Shows a message box with the document location in the project folder"
        )
        self.aFileDetails.triggered.connect(lambda: self.theParent.docEditor.revealLocation())
        self.docuMenu.addAction(self.aFileDetails)

        # Document > Import From File
        self.aImportFile = QAction("Import from File", self)
        self.aImportFile.setStatusTip("Import document from a text or markdown file")
        self.aImportFile.setShortcut("Ctrl+Shift+I")
        self.aImportFile.triggered.connect(lambda: self.theParent.importDocument())
        self.docuMenu.addAction(self.aImportFile)

        # Document > Merge Documents
        self.aMergeDocs = QAction("Merge Folder to Document", self)
        self.aMergeDocs.setStatusTip("Merge a folder of documents to a single document")
        self.aMergeDocs.triggered.connect(lambda: self.theParent.mergeDocuments())
        self.docuMenu.addAction(self.aMergeDocs)

        # Document > Split Document
        self.aSplitDoc = QAction("Split Document to Folder", self)
        self.aSplitDoc.setStatusTip("Split a document into a folder of multiple documents")
        self.aSplitDoc.triggered.connect(lambda: self.theParent.splitDocument())
        self.docuMenu.addAction(self.aSplitDoc)

        return

    def _buildEditMenu(self):
        """Assemble the Edit menu.
        """
        # Edit
        self.editMenu = self.addMenu("&Edit")

        # Edit > Undo
        self.aEditUndo = QAction("Undo", self)
        self.aEditUndo.setStatusTip("Undo last change")
        self.aEditUndo.setShortcut("Ctrl+Z")
        self.aEditUndo.triggered.connect(lambda: self._docAction(nwDocAction.UNDO))
        self.editMenu.addAction(self.aEditUndo)

        # Edit > Redo
        self.aEditRedo = QAction("Redo", self)
        self.aEditRedo.setStatusTip("Redo last change")
        self.aEditRedo.setShortcut("Ctrl+Y")
        self.aEditRedo.triggered.connect(lambda: self._docAction(nwDocAction.REDO))
        self.editMenu.addAction(self.aEditRedo)

        # Edit > Separator
        self.editMenu.addSeparator()

        # Edit > Cut
        self.aEditCut = QAction("Cut", self)
        self.aEditCut.setStatusTip("Cut selected text")
        self.aEditCut.setShortcut("Ctrl+X")
        self.aEditCut.triggered.connect(lambda: self._docAction(nwDocAction.CUT))
        self.editMenu.addAction(self.aEditCut)

        # Edit > Copy
        self.aEditCopy = QAction("Copy", self)
        self.aEditCopy.setStatusTip("Copy selected text")
        self.aEditCopy.setShortcut("Ctrl+C")
        self.aEditCopy.triggered.connect(lambda: self._docAction(nwDocAction.COPY))
        self.editMenu.addAction(self.aEditCopy)

        # Edit > Paste
        self.aEditPaste = QAction("Paste", self)
        self.aEditPaste.setStatusTip("Paste text from clipboard")
        self.aEditPaste.setShortcut("Ctrl+V")
        self.aEditPaste.triggered.connect(lambda: self._docAction(nwDocAction.PASTE))
        self.editMenu.addAction(self.aEditPaste)

        # Edit > Separator
        self.editMenu.addSeparator()

        # Edit > Select All
        self.aSelectAll = QAction("Select All", self)
        self.aSelectAll.setStatusTip("Select all text in document")
        self.aSelectAll.setShortcut("Ctrl+A")
        self.aSelectAll.triggered.connect(lambda: self._docAction(nwDocAction.SEL_ALL))
        self.editMenu.addAction(self.aSelectAll)

        # Edit > Select Paragraph
        self.aSelectPar = QAction("Select Paragraph", self)
        self.aSelectPar.setStatusTip("Select all text in paragraph")
        self.aSelectPar.setShortcut("Ctrl+Shift+A")
        self.aSelectPar.triggered.connect(lambda: self._docAction(nwDocAction.SEL_PARA))
        self.editMenu.addAction(self.aSelectPar)

        return

    def _buildViewMenu(self):
        """Assemble the View menu.
        """
        # View
        self.viewMenu = self.addMenu("&View")

        # View > TreeView
        self.aFocusTree = QAction("Focus Project Tree", self)
        self.aFocusTree.setStatusTip("Move focus to project tree")
        self.aFocusTree.setShortcut("Alt+1")
        self.aFocusTree.triggered.connect(lambda: self.theParent.setFocus(1))
        self.viewMenu.addAction(self.aFocusTree)

        # View > Document Pane 1
        self.aFocusEditor = QAction("Focus Document Editor", self)
        self.aFocusEditor.setStatusTip("Move focus to left document pane")
        self.aFocusEditor.setShortcut("Alt+2")
        self.aFocusEditor.triggered.connect(lambda: self.theParent.setFocus(2))
        self.viewMenu.addAction(self.aFocusEditor)

        # View > Document Pane 2
        self.aFocusView = QAction("Focus Document Viewer", self)
        self.aFocusView.setStatusTip("Move focus to right document pane")
        self.aFocusView.setShortcut("Alt+3")
        self.aFocusView.triggered.connect(lambda: self.theParent.setFocus(3))
        self.viewMenu.addAction(self.aFocusView)

        # View > Separator
        self.viewMenu.addSeparator()

        # View > Go Backward
        self.aViewPrev = QAction("Go Backward", self)
        self.aViewPrev.setStatusTip("Move backward in the view history of the right pane")
        self.aViewPrev.setShortcut("Alt+Left")
        self.aViewPrev.triggered.connect(lambda: self.theParent.docViewer.navBackward())
        self.viewMenu.addAction(self.aViewPrev)

        # View > Go Forward
        self.aViewNext = QAction("Go Forward", self)
        self.aViewNext.setStatusTip("Move forward in the view history of the right pane")
        self.aViewNext.setShortcut("Alt+Right")
        self.aViewNext.triggered.connect(lambda: self.theParent.docViewer.navForward())
        self.viewMenu.addAction(self.aViewNext)

        # View > Separator
        self.viewMenu.addSeparator()

        # View > Focus Mode
        self.aFocusMode = QAction("Focus Mode", self)
        self.aFocusMode.setStatusTip("Toggles a distraction free mode, only showing text editor")
        self.aFocusMode.setShortcut("F8")
        self.aFocusMode.setCheckable(True)
        self.aFocusMode.setChecked(self.theParent.isFocusMode)
        self.aFocusMode.triggered.connect(lambda: self.theParent.toggleFocusMode())
        self.viewMenu.addAction(self.aFocusMode)

        # View > Toggle Full Screen
        self.aFullScreen = QAction("Full Screen Mode", self)
        self.aFullScreen.setStatusTip("Maximises the main window")
        self.aFullScreen.setShortcut("F11")
        self.aFullScreen.triggered.connect(lambda: self.theParent.toggleFullScreenMode())
        self.viewMenu.addAction(self.aFullScreen)

        return

    def _buildInsertMenu(self):
        """Assemble the Insert menu.
        """
        # Insert
        self.insertMenu = self.addMenu("&Insert")

        # Insert > Dashes and Dots
        self.mInsDashes = self.insertMenu.addMenu("Dashes and Dots")

        # Insert > Short Dash
        self.aInsENDash = QAction("Short Dash", self)
        self.aInsENDash.setStatusTip("Insert short dash")
        self.aInsENDash.setShortcut("Ctrl+K, -")
        self.aInsENDash.triggered.connect(lambda: self._docInsert(nwDocInsert.SHORT_DASH))
        self.mInsDashes.addAction(self.aInsENDash)

        # Insert > Long Dash
        self.aInsEMDash = QAction("Long Dash", self)
        self.aInsEMDash.setStatusTip("Insert long dash")
        self.aInsEMDash.setShortcut("Ctrl+K, _")
        self.aInsEMDash.triggered.connect(lambda: self._docInsert(nwDocInsert.LONG_DASH))
        self.mInsDashes.addAction(self.aInsEMDash)

        # Insert > Ellipsis
        self.aInsEllipsis = QAction("Ellipsis", self)
        self.aInsEllipsis.setStatusTip("Insert ellipsis")
        self.aInsEllipsis.setShortcut("Ctrl+K, .")
        self.aInsEllipsis.triggered.connect(lambda: self._docInsert(nwDocInsert.ELLIPSIS))
        self.mInsDashes.addAction(self.aInsEllipsis)

        # Insert > Quote Marks
        self.mInsQuotes = self.insertMenu.addMenu("Quote Marks")

        # Insert > Left Single Quote
        self.aInsQuoteLS = QAction("Left Single Quote", self)
        self.aInsQuoteLS.setStatusTip("Insert left single quote")
        self.aInsQuoteLS.setShortcut("Ctrl+K, 1")
        self.aInsQuoteLS.triggered.connect(lambda: self._docInsert(nwDocInsert.QUOTE_LS))
        self.mInsQuotes.addAction(self.aInsQuoteLS)

        # Insert > Right Single Quote
        self.aInsQuoteRS = QAction("Right Single Quote", self)
        self.aInsQuoteRS.setStatusTip("Insert right single quote")
        self.aInsQuoteRS.setShortcut("Ctrl+K, 2")
        self.aInsQuoteRS.triggered.connect(lambda: self._docInsert(nwDocInsert.QUOTE_RS))
        self.mInsQuotes.addAction(self.aInsQuoteRS)

        # Insert > Left Double Quote
        self.aInsQuoteLD = QAction("Left Double Quote", self)
        self.aInsQuoteLD.setStatusTip("Insert left double quote")
        self.aInsQuoteLD.setShortcut("Ctrl+K, 3")
        self.aInsQuoteLD.triggered.connect(lambda: self._docInsert(nwDocInsert.QUOTE_LD))
        self.mInsQuotes.addAction(self.aInsQuoteLD)

        # Insert > Right Double Quote
        self.aInsQuoteRD = QAction("Right Double Quote", self)
        self.aInsQuoteRD.setStatusTip("Insert right double quote")
        self.aInsQuoteRD.setShortcut("Ctrl+K, 4")
        self.aInsQuoteRD.triggered.connect(lambda: self._docInsert(nwDocInsert.QUOTE_RD))
        self.mInsQuotes.addAction(self.aInsQuoteRD)

        # Insert > Alternative Apostrophe
        self.aInsMSApos = QAction("Alternative Apostrophe", self)
        self.aInsMSApos.setStatusTip("Insert unicode modifier letter single apostrophe")
        self.aInsMSApos.setShortcut("Ctrl+K, '")
        self.aInsMSApos.triggered.connect(lambda: self._docInsert(nwDocInsert.MODAPOS_S))
        self.mInsQuotes.addAction(self.aInsMSApos)

        # Insert > Breaks and Spaces
        self.mInsBreaks = self.insertMenu.addMenu("Breaks and Spaces")

        # Insert > Hard Line Break
        self.aInsHardBreak = QAction("Hard Line Break", self)
        self.aInsHardBreak.setStatusTip("Insert a hard line break")
        self.aInsHardBreak.setShortcut("Ctrl+K, Return")
        self.aInsHardBreak.triggered.connect(lambda: self._docInsert(nwDocInsert.HARD_BREAK))
        self.mInsBreaks.addAction(self.aInsHardBreak)

        # Insert > Non-Breaking Space
        self.aInsNBSpace = QAction("Non-Breaking Space", self)
        self.aInsNBSpace.setStatusTip("Insert a non-breaking space")
        self.aInsNBSpace.setShortcut("Ctrl+K, Space")
        self.aInsNBSpace.triggered.connect(lambda: self._docInsert(nwDocInsert.NB_SPACE))
        self.mInsBreaks.addAction(self.aInsNBSpace)

        # Insert > Thin Space
        self.aInsThinSpace = QAction("Thin Space", self)
        self.aInsThinSpace.setStatusTip("Insert a thin space")
        self.aInsThinSpace.setShortcut("Ctrl+K, Shift+Space")
        self.aInsThinSpace.triggered.connect(lambda: self._docInsert(nwDocInsert.THIN_SPACE))
        self.mInsBreaks.addAction(self.aInsThinSpace)

        # Insert > Thin Non-Breaking Space
        self.aInsThinNBSpace = QAction("Thin Non-Breaking Space", self)
        self.aInsThinNBSpace.setStatusTip("Insert a thin non-breaking space")
        self.aInsThinNBSpace.setShortcut("Ctrl+K, Ctrl+Space")
        self.aInsThinNBSpace.triggered.connect(lambda: self._docInsert(nwDocInsert.THIN_NB_SPACE))
        self.mInsBreaks.addAction(self.aInsThinNBSpace)

        # Insert > Separator
        self.insertMenu.addSeparator()

        # Insert > Tags and References
        self.mInsKeywords = self.insertMenu.addMenu("Tags and References")
        self.mInsKWItems = {}
        self.mInsKWItems[nwKeyWords.TAG_KEY]    = (QAction(self.mInsKeywords), "Ctrl+K, G")
        self.mInsKWItems[nwKeyWords.POV_KEY]    = (QAction(self.mInsKeywords), "Ctrl+K, V")
        self.mInsKWItems[nwKeyWords.CHAR_KEY]   = (QAction(self.mInsKeywords), "Ctrl+K, C")
        self.mInsKWItems[nwKeyWords.PLOT_KEY]   = (QAction(self.mInsKeywords), "Ctrl+K, P")
        self.mInsKWItems[nwKeyWords.TIME_KEY]   = (QAction(self.mInsKeywords), "Ctrl+K, T")
        self.mInsKWItems[nwKeyWords.WORLD_KEY]  = (QAction(self.mInsKeywords), "Ctrl+K, L")
        self.mInsKWItems[nwKeyWords.OBJECT_KEY] = (QAction(self.mInsKeywords), "Ctrl+K, O")
        self.mInsKWItems[nwKeyWords.ENTITY_KEY] = (QAction(self.mInsKeywords), "Ctrl+K, E")
        self.mInsKWItems[nwKeyWords.CUSTOM_KEY] = (QAction(self.mInsKeywords), "Ctrl+K, X")
        for n, keyWord in enumerate(self.mInsKWItems):
            self.mInsKWItems[keyWord][0].setText(nwLabels.KEY_NAME[keyWord])
            self.mInsKWItems[keyWord][0].setShortcut(self.mInsKWItems[keyWord][1])
            self.mInsKWItems[keyWord][0].triggered.connect(
                lambda n, keyWord=keyWord: self._insertKeyWord(keyWord)
            )
            self.mInsKeywords.addAction(self.mInsKWItems[keyWord][0])

        return

    def _buildSearchMenu(self):
        """Assemble the Search menu.
        """
        # Search
        self.srcMenu = self.addMenu("&Search")

        # Search > Find
        self.aFind = QAction("Find", self)
        self.aFind.setStatusTip("Find text in document")
        self.aFind.setShortcut("Ctrl+F")
        self.aFind.triggered.connect(lambda: self._docAction(nwDocAction.FIND))
        self.srcMenu.addAction(self.aFind)

        # Search > Replace
        self.aReplace = QAction("Replace", self)
        self.aReplace.setStatusTip("Replace text in document")
        if self.mainConf.osDarwin:
            self.aReplace.setShortcut("Ctrl+=")
        else:
            self.aReplace.setShortcut("Ctrl+H")
        self.aReplace.triggered.connect(lambda: self._docAction(nwDocAction.REPLACE))
        self.srcMenu.addAction(self.aReplace)

        # Search > Find Next
        self.aFindNext = QAction("Find Next", self)
        self.aFindNext.setStatusTip("Find next occurrence text in document")
        if self.mainConf.osDarwin:
            self.aFindNext.setShortcuts(["Ctrl+G", "F3"])
        else:
            self.aFindNext.setShortcuts(["F3", "Ctrl+G"])
        self.aFindNext.triggered.connect(lambda: self._docAction(nwDocAction.GO_NEXT))
        self.srcMenu.addAction(self.aFindNext)

        # Search > Find Prev
        self.aFindPrev = QAction("Find Previous", self)
        self.aFindPrev.setStatusTip("Find previous occurrence text in document")
        if self.mainConf.osDarwin:
            self.aFindPrev.setShortcuts(["Ctrl+Shift+G", "Shift+F3"])
        else:
            self.aFindPrev.setShortcuts(["Shift+F3", "Ctrl+Shift+G"])
        self.aFindPrev.triggered.connect(lambda: self._docAction(nwDocAction.GO_PREV))
        self.srcMenu.addAction(self.aFindPrev)

        # Search > Replace Next
        self.aReplaceNext = QAction("Replace Next", self)
        self.aReplaceNext.setStatusTip("Find and replace next occurrence text in document")
        self.aReplaceNext.setShortcut("Ctrl+Shift+1")
        self.aReplaceNext.triggered.connect(lambda: self._docAction(nwDocAction.REPL_NEXT))
        self.srcMenu.addAction(self.aReplaceNext)

        return

    def _buildFormatMenu(self):
        """Assemble the Format menu.
        """
        # Format
        self.fmtMenu = self.addMenu("&Format")

        # Format > Emphasis
        self.aFmtEmph = QAction("Emphasis", self)
        self.aFmtEmph.setStatusTip("Add emphasis to selected text (italic)")
        self.aFmtEmph.setShortcut("Ctrl+I")
        self.aFmtEmph.triggered.connect(lambda: self._docAction(nwDocAction.EMPH))
        self.fmtMenu.addAction(self.aFmtEmph)

        # Format > Strong Emphasis
        self.aFmtStrong = QAction("Strong Emphasis", self)
        self.aFmtStrong.setStatusTip("Add strong emphasis to selected text (bold)")
        self.aFmtStrong.setShortcut("Ctrl+B")
        self.aFmtStrong.triggered.connect(lambda: self._docAction(nwDocAction.STRONG))
        self.fmtMenu.addAction(self.aFmtStrong)

        # Format > Strikethrough
        self.aFmtStrike = QAction("Strikethrough", self)
        self.aFmtStrike.setStatusTip("Add strikethrough to selected text")
        self.aFmtStrike.setShortcut("Ctrl+-")
        self.aFmtStrike.triggered.connect(lambda: self._docAction(nwDocAction.STRIKE))
        self.fmtMenu.addAction(self.aFmtStrike)

        # Edit > Separator
        self.fmtMenu.addSeparator()

        # Format > Double Quotes
        self.aFmtDQuote = QAction("Wrap Double Quotes", self)
        self.aFmtDQuote.setStatusTip("Wrap selected text in double quotes")
        self.aFmtDQuote.setShortcut("Ctrl+D")
        self.aFmtDQuote.triggered.connect(lambda: self._docAction(nwDocAction.D_QUOTE))
        self.fmtMenu.addAction(self.aFmtDQuote)

        # Format > Single Quotes
        self.aFmtSQuote = QAction("Wrap Single Quotes", self)
        self.aFmtSQuote.setStatusTip("Wrap selected text in single quotes")
        self.aFmtSQuote.setShortcut("Ctrl+Shift+D")
        self.aFmtSQuote.triggered.connect(lambda: self._docAction(nwDocAction.S_QUOTE))
        self.fmtMenu.addAction(self.aFmtSQuote)

        # Format > Separator
        self.fmtMenu.addSeparator()

        # Format > Header 1
        self.aFmtHead1 = QAction("Header 1", self)
        self.aFmtHead1.setStatusTip("Change the block format to Header 1")
        self.aFmtHead1.setShortcut("Ctrl+1")
        self.aFmtHead1.triggered.connect(lambda: self._docAction(nwDocAction.BLOCK_H1))
        self.fmtMenu.addAction(self.aFmtHead1)

        # Format > Header 2
        self.aFmtHead2 = QAction("Header 2", self)
        self.aFmtHead2.setStatusTip("Change the block format to Header 2")
        self.aFmtHead2.setShortcut("Ctrl+2")
        self.aFmtHead2.triggered.connect(lambda: self._docAction(nwDocAction.BLOCK_H2))
        self.fmtMenu.addAction(self.aFmtHead2)

        # Format > Header 3
        self.aFmtHead3 = QAction("Header 3", self)
        self.aFmtHead3.setStatusTip("Change the block format to Header 3")
        self.aFmtHead3.setShortcut("Ctrl+3")
        self.aFmtHead3.triggered.connect(lambda: self._docAction(nwDocAction.BLOCK_H3))
        self.fmtMenu.addAction(self.aFmtHead3)

        # Format > Header 4
        self.aFmtHead4 = QAction("Header 4", self)
        self.aFmtHead4.setStatusTip("Change the block format to Header 4")
        self.aFmtHead4.setShortcut("Ctrl+4")
        self.aFmtHead4.triggered.connect(lambda: self._docAction(nwDocAction.BLOCK_H4))
        self.fmtMenu.addAction(self.aFmtHead4)

        # Format > Comment
        self.aFmtComment = QAction("Comment", self)
        self.aFmtComment.setStatusTip("Change the block format to comment")
        self.aFmtComment.setShortcut("Ctrl+/")
        self.aFmtComment.triggered.connect(lambda: self._docAction(nwDocAction.BLOCK_COM))
        self.fmtMenu.addAction(self.aFmtComment)

        # Format > Remove Block Format
        self.aFmtNoFormat = QAction("Remove Block Format", self)
        self.aFmtNoFormat.setStatusTip("Strips block format")
        self.aFmtNoFormat.setShortcuts(["Ctrl+0", "Ctrl+Shift+/"])
        self.aFmtNoFormat.triggered.connect(lambda: self._docAction(nwDocAction.BLOCK_TXT))
        self.fmtMenu.addAction(self.aFmtNoFormat)

        # Format > Separator
        self.fmtMenu.addSeparator()

        # Format > Replace Single Quotes
        self.aFmtReplSng = QAction("Replace Single Quotes", self)
        self.aFmtReplSng.setStatusTip("Replace all straight single quotes in selected text")
        self.aFmtReplSng.triggered.connect(lambda: self._docAction(nwDocAction.REPL_SNG))
        self.fmtMenu.addAction(self.aFmtReplSng)

        # Format > Replace Double Quotes
        self.aFmtReplDbl = QAction("Replace Double Quotes", self)
        self.aFmtReplDbl.setStatusTip("Replace all straight double quotes in selected text")
        self.aFmtReplDbl.triggered.connect(lambda: self._docAction(nwDocAction.REPL_DBL))
        self.fmtMenu.addAction(self.aFmtReplDbl)

        return

    def _buildToolsMenu(self):
        """Assemble the Tools menu.
        """
        # Tools
        self.toolsMenu = self.addMenu("&Tools")

        # Tools > Move Up
        self.aMoveUp = QAction("Move Tree Item Up", self)
        self.aMoveUp.setStatusTip("Move item up")
        self.aMoveUp.setShortcut("Ctrl+Shift+Up")
        self.aMoveUp.triggered.connect(lambda: self._moveTreeItem(-1))
        self.toolsMenu.addAction(self.aMoveUp)

        # Tools > Move Down
        self.aMoveDown = QAction("Move Tree Item Down", self)
        self.aMoveDown.setStatusTip("Move item down")
        self.aMoveDown.setShortcut("Ctrl+Shift+Down")
        self.aMoveDown.triggered.connect(lambda: self._moveTreeItem(1))
        self.toolsMenu.addAction(self.aMoveDown)

        # Tools > Separator
        self.toolsMenu.addSeparator()

        # Tools > Toggle Spell Check
        self.aSpellCheck = QAction("Check Spelling", self)
        self.aSpellCheck.setStatusTip("Toggle check spelling")
        self.aSpellCheck.setCheckable(True)
        self.aSpellCheck.setChecked(self.theProject.spellCheck)
        # Here we must used triggered, not toggled, to avoid recursion
        self.aSpellCheck.triggered.connect(self._toggleSpellCheck)
        self.aSpellCheck.setShortcut("Ctrl+F7")
        self.toolsMenu.addAction(self.aSpellCheck)

        # Tools > Update Spell Check
        self.aReRunSpell = QAction("Re-Run Spell Check", self)
        self.aReRunSpell.setStatusTip("Run the spell checker on current document")
        self.aReRunSpell.setShortcut("F7")
        self.aReRunSpell.triggered.connect(lambda: self.theParent.docEditor.spellCheckDocument())
        self.toolsMenu.addAction(self.aReRunSpell)

        # Tools > Separator
        self.toolsMenu.addSeparator()

        # Tools > Rebuild Indices
        self.aRebuildIndex = QAction("Rebuild Index", self)
        self.aRebuildIndex.setStatusTip("Rebuild the tag indices and word counts")
        self.aRebuildIndex.setShortcut("F9")
        self.aRebuildIndex.triggered.connect(lambda: self.theParent.rebuildIndex())
        self.toolsMenu.addAction(self.aRebuildIndex)

        # Tools > Rebuild Outline
        self.aRebuildOutline = QAction("Rebuild Outline", self)
        self.aRebuildOutline.setStatusTip("Rebuild the novel outline tree")
        self.aRebuildOutline.setShortcut("F10")
        self.aRebuildOutline.triggered.connect(lambda: self.theParent.rebuildOutline())
        self.toolsMenu.addAction(self.aRebuildOutline)

        # Tools > Toggle Auto Build Outline
        self.aAutoOutline = QAction("Auto-Update Outline", self)
        self.aAutoOutline.setStatusTip("Update project outline when a novel file is changed")
        self.aAutoOutline.setCheckable(True)
        self.aAutoOutline.toggled.connect(self._toggleAutoOutline)
        self.aAutoOutline.setShortcut("Ctrl+F10")
        self.toolsMenu.addAction(self.aAutoOutline)

        # Tools > Separator
        self.toolsMenu.addSeparator()

        # Tools > Backup
        self.aBackupProject = QAction("Backup Project Folder", self)
        self.aBackupProject.setStatusTip("Backup Project")
        self.aBackupProject.triggered.connect(lambda: self.theProject.zipIt(True))
        self.toolsMenu.addAction(self.aBackupProject)

        # Tools > Export Project
        self.aBuildProject = QAction("Build Novel Project", self)
        self.aBuildProject.setStatusTip("Launch the Build novel project tool")
        self.aBuildProject.setShortcut("F5")
        self.aBuildProject.triggered.connect(lambda: self.theParent.showBuildProjectDialog())
        self.toolsMenu.addAction(self.aBuildProject)

        # Tools > Writing Stats
        self.aWritingStats = QAction("Writing Statistics", self)
        self.aWritingStats.setStatusTip("Show the writing statistics dialog")
        self.aWritingStats.setShortcut("F6")
        self.aWritingStats.triggered.connect(lambda: self.theParent.showWritingStatsDialog())
        self.toolsMenu.addAction(self.aWritingStats)

        # Tools > Settings
        self.aPreferences = QAction("Preferences", self)
        self.aPreferences.setStatusTip("Preferences")
        self.aPreferences.setShortcut("Ctrl+,")
        self.aPreferences.setMenuRole(QAction.PreferencesRole)
        self.aPreferences.triggered.connect(lambda: self.theParent.showPreferencesDialog())
        self.toolsMenu.addAction(self.aPreferences)

        return

    def _buildHelpMenu(self):
        """Assemble the Help menu.
        """
        # Help
        self.helpMenu = self.addMenu("&Help")

        # Help > About
        self.aAboutNW = QAction("About novelWriter", self)
        self.aAboutNW.setStatusTip("About novelWriter")
        self.aAboutNW.setMenuRole(QAction.AboutRole)
        self.aAboutNW.triggered.connect(lambda: self.theParent.showAboutNWDialog())
        self.helpMenu.addAction(self.aAboutNW)

        # Help > About Qt5
        self.aAboutQt = QAction("About Qt5", self)
        self.aAboutQt.setStatusTip("About Qt5")
        self.aAboutQt.setMenuRole(QAction.AboutQtRole)
        self.aAboutQt.triggered.connect(lambda: self.theParent.showAboutQtDialog())
        self.helpMenu.addAction(self.aAboutQt)

        # Help > Separator
        self.helpMenu.addSeparator()

        # Document > Documentation
        if self.mainConf.hasHelp and self.mainConf.hasAssistant:
            self.aHelpLoc = QAction("Documentation (Local)", self)
            self.aHelpLoc.setStatusTip("View local documentation with Qt Assistant")
            self.aHelpLoc.triggered.connect(self._openAssistant)
            self.aHelpLoc.setShortcut("F1")
            self.helpMenu.addAction(self.aHelpLoc)

        self.aHelpWeb = QAction("Documentation (Online)", self)
        self.aHelpWeb.setStatusTip("View online documentation at %s" % nw.__docurl__)
        self.aHelpWeb.triggered.connect(lambda: self._openWebsite(nw.__docurl__))
        if self.mainConf.hasHelp and self.mainConf.hasAssistant:
            self.aHelpWeb.setShortcut("Shift+F1")
        else:
            self.aHelpWeb.setShortcuts(["F1", "Shift+F1"])
        self.helpMenu.addAction(self.aHelpWeb)

        # Help > Separator
        self.helpMenu.addSeparator()

        # Document > Report an Issue
        self.aIssue = QAction("Report an Issue (GitHub)", self)
        self.aIssue.setStatusTip("Report a bug or issue on GitHub at %s" % nw.__issuesurl__)
        self.aIssue.triggered.connect(lambda: self._openWebsite(nw.__issuesurl__))
        self.helpMenu.addAction(self.aIssue)

        # Document > Ask a Question
        self.aQuestion = QAction("Ask a Question (GitHub)", self)
        self.aQuestion.setStatusTip("Ask a question on GitHub at %s" % nw.__helpurl__)
        self.aQuestion.triggered.connect(lambda: self._openWebsite(nw.__helpurl__))
        self.helpMenu.addAction(self.aQuestion)

        # Document > Latest Release
        self.aRelease = QAction("Latest Release (GitHub)", self)
        self.aRelease.setStatusTip("Open the Releases page on GitHub at %s" % nw.__releaseurl__)
        self.aRelease.triggered.connect(lambda: self._openWebsite(nw.__releaseurl__))
        self.helpMenu.addAction(self.aRelease)

        # Document > Main Website
        self.aWebsite = QAction("The novelWriter Website", self)
        self.aWebsite.setStatusTip("Open the novelWriter website at %s" % nw.__url__)
        self.aWebsite.triggered.connect(lambda: self._openWebsite(nw.__url__))
        self.helpMenu.addAction(self.aWebsite)

        return

# END Class GuiMainMenu
