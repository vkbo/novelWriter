# -*- coding: utf-8 -*-
"""novelWriter GUI Main Menu

 novelWriter – GUI Main Menu
=============================
 Class holding the main window

 File History:
 Created: 2019-04-27 [0.0.1] (Split from winmain)

 This file is a part of novelWriter
 Copyright 2020, Veronica Berglyd Olsen

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
import nw

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QMenuBar, QAction, QMessageBox

from nw.gui.dialogs import GuiAbout
from nw.constants import nwItemType, nwItemClass, nwDocAction

logger = logging.getLogger(__name__)

class GuiMainMenu(QMenuBar):

    def __init__(self, theParent, theProject):
        QMenuBar.__init__(self, theParent)

        logger.debug("Initialising Main Menu ...")
        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject

        self._buildProjectMenu()
        self._buildDocumentMenu()
        self._buildEditMenu()
        self._buildViewMenu()
        self._buildFormatMenu()
        self._buildToolsMenu()
        self._buildHelpMenu()

        # Function Pointers
        self._docAction    = self.theParent.passDocumentAction
        self._moveTreeItem = self.theParent.treeView.moveTreeItem
        self._newTreeItem  = self.theParent.treeView.newTreeItem

        logger.debug("Main Menu initialisation complete")

        return

    def setAvailableRoot(self):
        for itemClass in nwItemClass:
            if itemClass == nwItemClass.NO_CLASS: continue
            if itemClass == nwItemClass.TRASH:    continue
            self.rootItems[itemClass].setEnabled(
                self.theProject.projTree.checkRootUnique(itemClass)
            )
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

    def _menuExit(self):
        self.theParent.closeMain()
        return

    def _toggleSpellCheck(self):
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

    def _toggleViewComments(self):
        self.mainConf.setViewComments(self.aViewDocComments.isChecked())
        self.theParent.docViewer.reloadText()
        return True

    def _showAbout(self):
        """Show the about dialog.
        """
        if self.mainConf.showGUI:
            msgAbout = GuiAbout(self.theParent)
            msgAbout.exec_()
        return True

    def _showAboutQt(self):
        msgBox = QMessageBox()
        msgBox.aboutQt(self.theParent,"About Qt")
        return True

    def _openHelp(self):
        QDesktopServices.openUrl(QUrl(nw.__docurl__))
        return True

    def _showDocumentLocation(self):
        self.theParent.docEditor.revealLocation()
        return True

    def _doBackup(self):
        self.theProject.zipIt(True)
        return True

    ##
    #  Menu Builders
    ##

    def _buildProjectMenu(self):

        # Project
        self.projMenu = self.addMenu("&Project")

        # Project > New Project
        self.aNewProject = QAction("New Project", self)
        self.aNewProject.setStatusTip("Create new project")
        self.aNewProject.triggered.connect(lambda : self.theParent.newProject(None))
        self.projMenu.addAction(self.aNewProject)

        # Project > Open Project
        self.aOpenProject = QAction("Open Project", self)
        self.aOpenProject.setStatusTip("Open project")
        self.aOpenProject.setShortcut("Ctrl+Shift+O")
        self.aOpenProject.triggered.connect(self.theParent.manageProjects)
        self.projMenu.addAction(self.aOpenProject)

        # Project > Save Project
        self.aSaveProject = QAction("Save Project", self)
        self.aSaveProject.setStatusTip("Save project")
        self.aSaveProject.setShortcut("Ctrl+Shift+S")
        self.aSaveProject.triggered.connect(self.theParent.saveProject)
        self.projMenu.addAction(self.aSaveProject)

        # Project > Close Project
        self.aCloseProject = QAction("Close Project", self)
        self.aCloseProject.setStatusTip("Close project")
        self.aCloseProject.setShortcut("Ctrl+Shift+W")
        self.aCloseProject.triggered.connect(lambda : self.theParent.closeProject(False))
        self.projMenu.addAction(self.aCloseProject)

        # Project > Project Settings
        self.aProjectSettings = QAction("Project Settings", self)
        self.aProjectSettings.setStatusTip("Project settings")
        self.aProjectSettings.setShortcut("Ctrl+Shift+,")
        self.aProjectSettings.triggered.connect(self.theParent.editProjectDialog)
        self.projMenu.addAction(self.aProjectSettings)

        # Project > Export Project
        self.aBuildProject = QAction("Build Project", self)
        self.aBuildProject.setStatusTip("Build project")
        self.aBuildProject.setShortcut("F5")
        self.aBuildProject.triggered.connect(self.theParent.buildProjectDialog)
        self.projMenu.addAction(self.aBuildProject)

        # Project > Session Log
        self.aSessionLog = QAction("Session Log", self)
        self.aSessionLog.setStatusTip("Show the session log")
        self.aSessionLog.triggered.connect(self.theParent.showSessionLogDialog)
        self.projMenu.addAction(self.aSessionLog)

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
        nCount = 0
        for itemClass in self.rootItems.keys():
            nCount += 1 # This forces the lambdas to be unique
            self.rootItems[itemClass].triggered.connect(
                lambda nCount, itemClass=itemClass : self._newTreeItem(nwItemType.ROOT, itemClass)
            )
            self.rootMenu.addAction(self.rootItems[itemClass])

        # Project > New Folder
        self.aCreateFolder = QAction("Create Folder", self)
        self.aCreateFolder.setStatusTip("Create folder")
        self.aCreateFolder.setShortcut("Ctrl+Shift+N")
        self.aCreateFolder.triggered.connect(lambda : self._newTreeItem(nwItemType.FOLDER, None))
        self.projMenu.addAction(self.aCreateFolder)

        # Project > Separator
        self.projMenu.addSeparator()

        # Project > Edit
        self.aEditItem = QAction("&Edit Item", self)
        self.aEditItem.setStatusTip("Change item settings")
        self.aEditItem.setShortcuts(["Ctrl+E", "F2"])
        self.aEditItem.triggered.connect(self.theParent.editItem)
        self.projMenu.addAction(self.aEditItem)

        # Project > Delete
        self.aDeleteItem = QAction("&Delete Item", self)
        self.aDeleteItem.setStatusTip("Delete selected item")
        self.aDeleteItem.setShortcut("Ctrl+Del")
        self.aDeleteItem.triggered.connect(lambda : self.theParent.treeView.deleteItem(None))
        self.projMenu.addAction(self.aDeleteItem)

        # Project > Empty Trash
        self.aEmptyTrash = QAction("Empty Trash", self)
        self.aEmptyTrash.setStatusTip("Permanently delete all files in the Trash folder")
        self.aEmptyTrash.triggered.connect(self.theParent.treeView.emptyTrash)
        self.projMenu.addAction(self.aEmptyTrash)

        # Project > Separator
        self.projMenu.addSeparator()

        # Project > Exit
        self.aExitNW = QAction("Exit", self)
        self.aExitNW.setStatusTip("Exit %s" % nw.__package__)
        self.aExitNW.setShortcut("Ctrl+Q")
        self.aExitNW.triggered.connect(self._menuExit)
        self.projMenu.addAction(self.aExitNW)

        return

    def _buildDocumentMenu(self):

        # Document
        self.docuMenu = self.addMenu("&Document")

        # Document > New
        self.aNewDoc = QAction("&New Document", self)
        self.aNewDoc.setStatusTip("Create new document")
        self.aNewDoc.setShortcut("Ctrl+N")
        self.aNewDoc.triggered.connect(lambda : self._newTreeItem(nwItemType.FILE, None))
        self.docuMenu.addAction(self.aNewDoc)

        # Document > Open
        self.aOpenDoc = QAction("&Open Document", self)
        self.aOpenDoc.setStatusTip("Open selected document")
        self.aOpenDoc.setShortcut("Ctrl+O")
        self.aOpenDoc.triggered.connect(self.theParent.openSelectedItem)
        self.docuMenu.addAction(self.aOpenDoc)

        # Document > Save
        self.aSaveDoc = QAction("&Save Document", self)
        self.aSaveDoc.setStatusTip("Save current document")
        self.aSaveDoc.setShortcut("Ctrl+S")
        self.aSaveDoc.triggered.connect(self.theParent.saveDocument)
        self.docuMenu.addAction(self.aSaveDoc)

        # Document > Close
        self.aCloseDoc = QAction("Close Document", self)
        self.aCloseDoc.setStatusTip("Close current document")
        self.aCloseDoc.setShortcut("Ctrl+W")
        self.aCloseDoc.triggered.connect(self.theParent.closeDocEditor)
        self.docuMenu.addAction(self.aCloseDoc)

        # Document > Separator
        self.docuMenu.addSeparator()

        # Document > Preview
        self.aViewDoc = QAction("View Document", self)
        self.aViewDoc.setStatusTip("View document as HTML")
        self.aViewDoc.setShortcut("Ctrl+R")
        self.aViewDoc.triggered.connect(lambda : self.theParent.viewDocument(None))
        self.docuMenu.addAction(self.aViewDoc)

        # Document > Close Preview
        self.aCloseView = QAction("Close Document View", self)
        self.aCloseView.setStatusTip("Close document view pane")
        self.aCloseView.setShortcut("Ctrl+Shift+R")
        self.aCloseView.triggered.connect(self.theParent.closeDocViewer)
        self.docuMenu.addAction(self.aCloseView)

        # Document > Toggle View Comments
        self.aViewDocComments = QAction("Show Comments", self)
        self.aViewDocComments.setStatusTip("Show comments in view panel")
        self.aViewDocComments.setCheckable(True)
        self.aViewDocComments.setChecked(self.mainConf.viewComments)
        self.aViewDocComments.toggled.connect(self._toggleViewComments)
        self.docuMenu.addAction(self.aViewDocComments)

        # Document > Separator
        self.docuMenu.addSeparator()

        # Document > Show File Details
        self.aFileDetails = QAction("Show File Details", self)
        self.aFileDetails.setStatusTip(
            "Shows a message box with the document location in the project folder"
        )
        self.aFileDetails.triggered.connect(self._showDocumentLocation)
        self.docuMenu.addAction(self.aFileDetails)

        # Document > Import From File
        self.aImportFile = QAction("Import from File", self)
        self.aImportFile.setStatusTip("Import document from a text or markdown file")
        self.aImportFile.setShortcut("Ctrl+Shift+I")
        self.aImportFile.triggered.connect(self.theParent.importDocument)
        self.docuMenu.addAction(self.aImportFile)

        # Document > Merge Documents
        self.aMergeDocs = QAction("Merge Folder to Document", self)
        self.aMergeDocs.setStatusTip("Merge a folder of documents to a single document")
        self.aMergeDocs.triggered.connect(self.theParent.mergeDocuments)
        self.docuMenu.addAction(self.aMergeDocs)

        # Document > Split Document
        self.aSplitDoc = QAction("Split Document to Folder", self)
        self.aSplitDoc.setStatusTip("Split a document into a folder of multiple documents")
        self.aSplitDoc.triggered.connect(self.theParent.splitDocument)
        self.docuMenu.addAction(self.aSplitDoc)

        return

    def _buildViewMenu(self):

        # View
        self.viewMenu = self.addMenu("&View")

        # View > TreeView
        self.aFocusTree = QAction("TreeView", self)
        self.aFocusTree.setStatusTip("Move focus to project tree")
        self.aFocusTree.setShortcut("Alt+1")
        self.aFocusTree.triggered.connect(lambda : self.theParent.setFocus(1))
        self.viewMenu.addAction(self.aFocusTree)

        # View > Document Pane 1
        self.aFocusEditor = QAction("Left Document Pane", self)
        self.aFocusEditor.setStatusTip("Move focus to left document pane")
        self.aFocusEditor.setShortcut("Alt+2")
        self.aFocusEditor.triggered.connect(lambda : self.theParent.setFocus(2))
        self.viewMenu.addAction(self.aFocusEditor)

        # View > Document Pane 2
        self.aFocusView = QAction("Right Document Pane", self)
        self.aFocusView.setStatusTip("Move focus to right document pane")
        self.aFocusView.setShortcut("Alt+3")
        self.aFocusView.triggered.connect(lambda : self.theParent.setFocus(3))
        self.viewMenu.addAction(self.aFocusView)

        # View > Separator
        self.viewMenu.addSeparator()

        # View > Toggle Distraction Free Mode
        self.aZenMode = QAction("Zen Mode", self)
        self.aZenMode.setStatusTip("Toggles distraction free mode, only showing text editor")
        self.aZenMode.setShortcut("F8")
        self.aZenMode.setCheckable(True)
        self.aZenMode.setChecked(self.theParent.isZenMode)
        self.aZenMode.toggled.connect(self.theParent.toggleZenMode)
        self.viewMenu.addAction(self.aZenMode)

        # View > Toggle Full Screen
        self.aFullScreen = QAction("Full Screen Mode", self)
        self.aFullScreen.setStatusTip("Maximises the main window")
        self.aFullScreen.setShortcut("F11")
        self.aFullScreen.triggered.connect(self.theParent.toggleFullScreenMode)
        self.viewMenu.addAction(self.aFullScreen)

        return

    def _buildEditMenu(self):

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

        # Edit > Find
        self.aEditFind = QAction("Find", self)
        self.aEditFind.setStatusTip("Find text in document")
        self.aEditFind.setShortcut("Ctrl+F")
        self.aEditFind.triggered.connect(lambda: self._docAction(nwDocAction.FIND))
        self.editMenu.addAction(self.aEditFind)

        # Edit > Replace
        self.aEditReplace = QAction("Replace", self)
        self.aEditReplace.setStatusTip("Replace text in document")
        if self.mainConf.osDarwin:
            self.aEditReplace.setShortcut("Ctrl+=")
        else:
            self.aEditReplace.setShortcut("Ctrl+H")
        self.aEditReplace.triggered.connect(lambda: self._docAction(nwDocAction.REPLACE))
        self.editMenu.addAction(self.aEditReplace)

        # Edit > Find Next
        self.aFindNext = QAction("Find Next", self)
        self.aFindNext.setStatusTip("Find next occurrence text in document")
        if self.mainConf.osDarwin:
            self.aFindNext.setShortcuts(["Ctrl+G","F3"])
        else:
            self.aFindNext.setShortcuts(["F3","Ctrl+G"])
        self.aFindNext.triggered.connect(lambda: self._docAction(nwDocAction.GO_NEXT))
        self.editMenu.addAction(self.aFindNext)

        # Edit > Find Prev
        self.aFindPrev = QAction("Find Previous", self)
        self.aFindPrev.setStatusTip("Find previous occurrence text in document")
        if self.mainConf.osDarwin:
            self.aFindPrev.setShortcuts(["Ctrl+Shift+G","Shift+F3"])
        else:
            self.aFindPrev.setShortcuts(["Shift+F3","Ctrl+Shift+G"])
        self.aFindPrev.triggered.connect(lambda: self._docAction(nwDocAction.GO_PREV))
        self.editMenu.addAction(self.aFindPrev)

        # Edit > Replace Next
        self.aReplaceNext = QAction("Replace Next", self)
        self.aReplaceNext.setStatusTip("Find and replace next occurrence text in document")
        self.aReplaceNext.setShortcut("Ctrl+Shift+1")
        self.aReplaceNext.triggered.connect(lambda: self._docAction(nwDocAction.REPL_NEXT))
        self.editMenu.addAction(self.aReplaceNext)

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

    def _buildFormatMenu(self):

        # Format
        self.fmtMenu = self.addMenu("&Format")

        # Format > Bold Text
        self.aFmtBold = QAction("Bold Text", self)
        self.aFmtBold.setStatusTip("Make selected text bold")
        self.aFmtBold.setShortcut("Ctrl+B")
        self.aFmtBold.triggered.connect(lambda: self._docAction(nwDocAction.BOLD))
        self.fmtMenu.addAction(self.aFmtBold)

        # Format > Italic Text
        self.aFmtItalic = QAction("Italic Text", self)
        self.aFmtItalic.setStatusTip("Make selected text italic")
        self.aFmtItalic.setShortcut("Ctrl+I")
        self.aFmtItalic.triggered.connect(lambda: self._docAction(nwDocAction.ITALIC))
        self.fmtMenu.addAction(self.aFmtItalic)

        # Format > Underline Text
        self.aFmtULine = QAction("Underline Text", self)
        self.aFmtULine.setStatusTip("Underline selected text")
        self.aFmtULine.setShortcut("Ctrl+U")
        self.aFmtULine.triggered.connect(lambda: self._docAction(nwDocAction.U_LINE))
        self.fmtMenu.addAction(self.aFmtULine)

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

        # Edit > Separator
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

        # Format > Remove Format
        self.aFmtNoFormat = QAction("Remove Format", self)
        self.aFmtNoFormat.setStatusTip("Strips block format")
        self.aFmtNoFormat.setShortcuts(["Ctrl+0","Ctrl+Shift+/"])
        self.aFmtNoFormat.triggered.connect(lambda: self._docAction(nwDocAction.BLOCK_TXT))
        self.fmtMenu.addAction(self.aFmtNoFormat)

        return

    def _buildToolsMenu(self):

        # Tools
        self.toolsMenu = self.addMenu("&Tools")

        # Tools > Move Up
        self.aMoveUp = QAction("Move Tree Item Up", self)
        self.aMoveUp.setStatusTip("Move item up")
        self.aMoveUp.setShortcut("Ctrl+Shift+Up")
        self.aMoveUp.triggered.connect(lambda : self._moveTreeItem(-1))
        self.toolsMenu.addAction(self.aMoveUp)

        # Tools > Move Down
        self.aMoveDown = QAction("Move Tree Item Down", self)
        self.aMoveDown.setStatusTip("Move item down")
        self.aMoveDown.setShortcut("Ctrl+Shift+Down")
        self.aMoveDown.triggered.connect(lambda : self._moveTreeItem(1))
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
        self.aReRunSpell.triggered.connect(self.theParent.docEditor.spellCheckDocument)
        self.toolsMenu.addAction(self.aReRunSpell)

        # Tools > Separator
        self.toolsMenu.addSeparator()

        # Tools > Rebuild Indices
        self.aRebuildIndex = QAction("Rebuild Index", self)
        self.aRebuildIndex.setStatusTip("Rebuild the tag indices and word counts")
        self.aRebuildIndex.setShortcut("F9")
        self.aRebuildIndex.triggered.connect(self.theParent.rebuildIndex)
        self.toolsMenu.addAction(self.aRebuildIndex)

        # Tools > Rebuild Outline
        self.aRebuildOutline = QAction("Rebuild Outline", self)
        self.aRebuildOutline.setStatusTip("Rebuild the novel outline tree")
        self.aRebuildOutline.setShortcut("F10")
        self.aRebuildOutline.triggered.connect(self.theParent.rebuildOutline)
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
        self.aBackupProject = QAction("Backup Project", self)
        self.aBackupProject.setStatusTip("Backup Project")
        self.aBackupProject.triggered.connect(self._doBackup)
        self.toolsMenu.addAction(self.aBackupProject)

        # Tools > Settings
        self.aPreferences = QAction("Preferences", self)
        self.aPreferences.setStatusTip("Preferences")
        self.aPreferences.setShortcut("Ctrl+,")
        self.aPreferences.triggered.connect(self.theParent.editConfigDialog)
        self.toolsMenu.addAction(self.aPreferences)

        return

    def _buildHelpMenu(self):

        # Help
        self.helpMenu = self.addMenu("&Help")

        # Help > About
        self.aAboutNW = QAction("About %s" % nw.__package__, self)
        self.aAboutNW.setStatusTip("About %s" % nw.__package__)
        self.aAboutNW.triggered.connect(self._showAbout)
        self.helpMenu.addAction(self.aAboutNW)

        # Help > About Qt5
        self.aAboutQt = QAction("About Qt5", self)
        self.aAboutQt.setStatusTip("About Qt5")
        self.aAboutQt.triggered.connect(self._showAboutQt)
        self.helpMenu.addAction(self.aAboutQt)

        # Help > Separator
        self.helpMenu.addSeparator()

        # Document > Preview
        self.aHelp = QAction("Online Documentation", self)
        self.aHelp.setStatusTip("View online documentation")
        self.aHelp.setShortcut("F1")
        self.aHelp.triggered.connect(self._openHelp)
        self.helpMenu.addAction(self.aHelp)

        return

# END Class GuiMainMenu
