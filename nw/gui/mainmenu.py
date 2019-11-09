# -*- coding: utf-8 -*-
"""novelWriter GUI Main Menu

 novelWriter – GUI Main Menu
=============================
 Class holding the main window

 File History:
 Created: 2019-04-27 [0.0.1] (Split from winmain)

"""

import logging
import nw

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QMenuBar, QAction, QMessageBox

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
        self._docAction    = self.theParent.docEditor.docAction
        self._moveTreeItem = self.theParent.treeView.moveTreeItem
        self._newTreeItem  = self.theParent.treeView.newTreeItem

        logger.debug("Main Menu initialisation complete")

        return

    def openRecentProject(self, menuItem, recentItem):
        logger.verbose("User requested opening recent project #%d" % recentItem)
        self.theParent.openProject(self.mainConf.recentList[recentItem])
        return True

    def setAvailableRoot(self):
        for itemClass in nwItemClass:
            if itemClass == nwItemClass.NO_CLASS: continue
            if itemClass == nwItemClass.TRASH:    continue
            self.rootItems[itemClass].setEnabled(
                self.theProject.checkRootUnique(itemClass)
            )
        return

    ##
    #  Update Menu on Settings Changed
    ##

    def updateMenu(self):
        self.updateRecentProjects()
        self.updateSpellCheck()
        return

    def updateRecentProjects(self):

        self.recentMenu.clear()
        for n in range(len(self.mainConf.recentList)):
            recentProject = self.mainConf.recentList[n]
            if recentProject == "": continue
            menuItem = QAction("%s" % recentProject, self.projMenu)
            menuItem.triggered.connect(
                lambda menuItem, n=n : self.openRecentProject(menuItem, n)
            )
            self.recentMenu.addAction(menuItem)

        self.recentMenu.addSeparator()
        menuItem = QAction("Clear Recent Projects", self)
        menuItem.setStatusTip("Clear the list of recent projects")
        menuItem.triggered.connect(self._clearRecentProjects)
        self.recentMenu.addAction(menuItem)

        return

    def updateSpellCheck(self):
        if self.theParent.hasProject:
            self.toolsSpellCheck.setChecked(self.theProject.spellCheck)
            logger.verbose("Spell check is set to %s" % str(self.theProject.spellCheck))
        return

    ##
    #  Menu Action
    ##

    def _menuExit(self):
        self.theParent.closeMain()
        return

    def _toggleSpellCheck(self):
        if self.theParent.hasProject:
            self.theProject.setSpellCheck(self.toolsSpellCheck.isChecked())
            self.theParent.docEditor.setSpellCheck(self.toolsSpellCheck.isChecked())
            logger.verbose("Spell check is set to %s" % str(self.theProject.spellCheck))
        else:
            self.toolsSpellCheck.setChecked(False)
        return True

    def _toggleViewComments(self):
        self.mainConf.setViewComments(self.docViewComments.isChecked())
        self.theParent.docViewer.reloadText()
        return True

    def _showAbout(self):
        listPrefix = "&nbsp;&nbsp;&bull;&nbsp;&nbsp;"
        aboutMsg   = (
            "<h3>About {name:s}</h3>"
            "<p>Version: {version:s}<br>Release Date: {date:s}</p>"
            "<p>{name:s} is a markdown-like text editor designed for organising "
            "and writing novels. It is written in Python 3 with a Qt5 GUI, "
            "using PyQt5</p>"
            "<p>{name:s} is licensed under GPL v3.0</p>"
            "<p>{copyright:s}</p>"
            "<p>Website: <a href='{website:s}'>{website:s}</a></p>"
            "<h4>Credits</h4>"
            "<p>{credits:s}</p>"
        ).format(
            name      = nw.__package__,
            version   = nw.__version__,
            date      = nw.__date__,
            copyright = nw.__copyright__,
            website   = nw.__url__,
            credits   = "<br/>".join(["%s%s" % (listPrefix, x) for x in nw.__credits__]),
        )
        theTheme = self.theParent.theTheme
        if theTheme.themeCredit != "" or theTheme.syntaxCredit != "":
            aboutMsg += "<h4>GUI Theme and Syntax Highlighting</h4>"
            aboutMsg += "<p>"
            if theTheme.themeCredit != "":
                aboutMsg += "%s\"%s\" by %s<br/>" % (
                    listPrefix, theTheme.themeName, theTheme.themeCredit
                )
            if theTheme.syntaxCredit != "":
                aboutMsg += "%s\"%s\" by %s<br/>" % (
                    listPrefix, theTheme.syntaxName, theTheme.syntaxCredit
                )
            aboutMsg += "</p>"
        msgBox = QMessageBox()
        msgBox.about(self.theParent, "About %s" % nw.__package__, aboutMsg)
        return True

    def _showAboutQt(self):
        msgBox = QMessageBox()
        msgBox.aboutQt(self.theParent,"About Qt")
        return True

    def _openHelp(self):
        QDesktopServices.openUrl(QUrl(nw.__docurl__))
        return True

    def _clearRecentProjects(self):
        self.mainConf.clearRecent()
        self.updateRecentProjects()
        return True

    def _showDocumentLocation(self):
        self.theParent.docEditor.revealLocation()
        return True

    ##
    #  Menu Builders
    ##

    def _buildProjectMenu(self):

        # Project
        self.projMenu = self.addMenu("&Project")

        # Project > New Project
        menuItem = QAction("New Project", self)
        menuItem.setStatusTip("Create new project")
        menuItem.triggered.connect(lambda : self.theParent.newProject(None))
        self.projMenu.addAction(menuItem)

        # Project > Open Project
        menuItem = QAction("Open Project", self)
        menuItem.setStatusTip("Open project")
        menuItem.setShortcut("Ctrl+Shift+O")
        menuItem.triggered.connect(lambda : self.theParent.openProject(None))
        self.projMenu.addAction(menuItem)

        # Project > Save Project
        menuItem = QAction("Save Project", self)
        menuItem.setStatusTip("Save project")
        menuItem.setShortcut("Ctrl+Shift+S")
        menuItem.triggered.connect(self.theParent.saveProject)
        self.projMenu.addAction(menuItem)

        # Project > Close Project
        menuItem = QAction("Close Project", self)
        menuItem.setStatusTip("Close project")
        menuItem.setShortcut("Ctrl+Shift+W")
        menuItem.triggered.connect(lambda : self.theParent.closeProject(False))
        self.projMenu.addAction(menuItem)

        # Project > Recent Projects
        self.recentMenu = self.projMenu.addMenu("Recent Projects")
        self.updateRecentProjects()

        # Project > Project Settings
        menuItem = QAction("Project Settings", self)
        menuItem.setStatusTip("Project settings")
        menuItem.setShortcut("Ctrl+Shift+,")
        menuItem.triggered.connect(self.theParent.editProjectDialog)
        self.projMenu.addAction(menuItem)

        # Project > Export Project
        menuItem = QAction("Export Project", self)
        menuItem.setStatusTip("Export project")
        menuItem.setShortcut("F5")
        menuItem.triggered.connect(self.theParent.exportProjectDialog)
        self.projMenu.addAction(menuItem)

        # Project > Session Log
        menuItem = QAction("Session Log", self)
        menuItem.setStatusTip("Show the session log")
        menuItem.triggered.connect(self.theParent.showSessionLogDialog)
        self.projMenu.addAction(menuItem)

        # Project > Separator
        self.projMenu.addSeparator()

        # Project > New Root
        rootMenu = self.projMenu.addMenu("Create Root Folder")
        self.rootItems = {}
        self.rootItems[nwItemClass.NOVEL]     = QAction("Novel Root",     rootMenu)
        self.rootItems[nwItemClass.PLOT]      = QAction("Plot Root",      rootMenu)
        self.rootItems[nwItemClass.CHARACTER] = QAction("Character Root", rootMenu)
        self.rootItems[nwItemClass.WORLD]     = QAction("Location Root",  rootMenu)
        self.rootItems[nwItemClass.TIMELINE]  = QAction("Timeline Root",  rootMenu)
        self.rootItems[nwItemClass.OBJECT]    = QAction("Object Root",    rootMenu)
        self.rootItems[nwItemClass.ENTITY]    = QAction("Entity Root",    rootMenu)
        self.rootItems[nwItemClass.CUSTOM]    = QAction("Custom Root",    rootMenu)
        nCount = 0
        for itemClass in self.rootItems.keys():
            nCount += 1 # This forces the lambdas to be unique
            self.rootItems[itemClass].triggered.connect(
                lambda nCount, itemClass=itemClass : self._newTreeItem(nwItemType.ROOT, itemClass)
            )
        rootMenu.addActions(self.rootItems.values())

        # Project > New Folder
        menuItem = QAction("Create Folder", self)
        menuItem.setStatusTip("Create folder")
        menuItem.setShortcut("Ctrl+Shift+N")
        menuItem.triggered.connect(lambda : self._newTreeItem(nwItemType.FOLDER, None))
        self.projMenu.addAction(menuItem)

        # Project > Separator
        self.projMenu.addSeparator()

        # Project > Edit
        menuItem = QAction("&Edit Item", self)
        menuItem.setStatusTip("Change item settings")
        menuItem.setShortcuts(["Ctrl+E", "F2"])
        menuItem.triggered.connect(self.theParent.editItem)
        self.projMenu.addAction(menuItem)

        # Project > Delete
        menuItem = QAction("&Delete Item", self)
        menuItem.setStatusTip("Delete selected item")
        menuItem.setShortcut("Ctrl+Del")
        menuItem.triggered.connect(lambda : self.theParent.treeView.deleteItem(None))
        self.projMenu.addAction(menuItem)

        # Project > Separator
        self.projMenu.addSeparator()

        # Project > Exit
        menuItem = QAction("Exit", self)
        menuItem.setStatusTip("Exit %s" % nw.__package__)
        menuItem.setShortcut("Ctrl+Q")
        menuItem.triggered.connect(self._menuExit)
        self.projMenu.addAction(menuItem)

        return

    def _buildDocumentMenu(self):

        # Document
        self.docuMenu = self.addMenu("&Document")

        # Document > New
        menuItem = QAction("&New Document", self)
        menuItem.setStatusTip("Create new document")
        menuItem.setShortcut("Ctrl+N")
        menuItem.triggered.connect(lambda : self._newTreeItem(nwItemType.FILE, None))
        self.docuMenu.addAction(menuItem)

        # Document > Open
        menuItem = QAction("&Open Document", self)
        menuItem.setStatusTip("Open selected document")
        menuItem.setShortcut("Ctrl+O")
        menuItem.triggered.connect(self.theParent.openSelectedItem)
        self.docuMenu.addAction(menuItem)

        # Document > Save
        menuItem = QAction("&Save Document", self)
        menuItem.setStatusTip("Save current document")
        menuItem.setShortcut("Ctrl+S")
        menuItem.triggered.connect(self.theParent.saveDocument)
        self.docuMenu.addAction(menuItem)

        # Document > Close
        menuItem = QAction("Close Document", self)
        menuItem.setStatusTip("Close current document")
        menuItem.setShortcut("Ctrl+W")
        menuItem.triggered.connect(self.theParent.closeDocEditor)
        self.docuMenu.addAction(menuItem)

        # Document > Separator
        self.docuMenu.addSeparator()

        # Document > Preview
        menuItem = QAction("View Document", self)
        menuItem.setStatusTip("View document as HTML")
        menuItem.setShortcut("Ctrl+R")
        menuItem.triggered.connect(lambda : self.theParent.viewDocument(None))
        self.docuMenu.addAction(menuItem)

        # Document > Close Preview
        menuItem = QAction("Close Document View", self)
        menuItem.setStatusTip("Close document view pane")
        menuItem.setShortcut("Ctrl+Shift+R")
        menuItem.triggered.connect(self.theParent.closeDocViewer)
        self.docuMenu.addAction(menuItem)

        # Document > Toggle View Comments
        self.docViewComments = QAction("View Comments", self)
        self.docViewComments.setStatusTip("Show comments in view panel")
        self.docViewComments.setCheckable(True)
        self.docViewComments.setChecked(self.mainConf.viewComments)
        self.docViewComments.toggled.connect(self._toggleViewComments)
        self.docuMenu.addAction(self.docViewComments)

        # Document > Separator
        self.docuMenu.addSeparator()

        # Document > Show File Details
        menuItem = QAction("Show File Details", self)
        menuItem.setStatusTip(
            "Shows a message box with the document location in the project folder"
        )
        menuItem.triggered.connect(self._showDocumentLocation)
        self.docuMenu.addAction(menuItem)

        # Document > Import From File
        menuItem = QAction("Import from File", self)
        menuItem.setStatusTip("Import document from a text or markdown file")
        menuItem.setShortcut("Ctrl+Shift+I")
        menuItem.triggered.connect(self.theParent.importDocument)
        self.docuMenu.addAction(menuItem)

        # # Document > Split
        # menuItem = QAction("Split Document", self)
        # menuItem.setStatusTip("Split Selected Document")
        # self.docuMenu.addAction(menuItem)

        # # Document > Merge
        # menuItem = QAction("Merge Document", self)
        # menuItem.setStatusTip("Merge Selected Documents")
        # self.docuMenu.addAction(menuItem)

        return

    def _buildViewMenu(self):

        # View
        self.viewMenu = self.addMenu("&View")

        # View > TreeView
        menuItem = QAction("TreeView", self)
        menuItem.setStatusTip("Move focus to project tree")
        menuItem.setShortcut("Ctrl+1")
        menuItem.triggered.connect(lambda : self.theParent.setFocus(1))
        self.viewMenu.addAction(menuItem)

        # View > Document Pane 1
        menuItem = QAction("Left Document Pane", self)
        menuItem.setStatusTip("Move focus to left document pane")
        menuItem.setShortcut("Ctrl+2")
        menuItem.triggered.connect(lambda : self.theParent.setFocus(2))
        self.viewMenu.addAction(menuItem)

        # View > Document Pane 2
        menuItem = QAction("Right Document Pane", self)
        menuItem.setStatusTip("Move focus to right document pane")
        menuItem.setShortcut("Ctrl+3")
        menuItem.triggered.connect(lambda : self.theParent.setFocus(3))
        self.viewMenu.addAction(menuItem)

        # View > Separator
        self.viewMenu.addSeparator()

        # View > Toggle Distraction Free Mode
        menuItem = QAction("Zen Mode", self)
        menuItem.setStatusTip("Toggles distraction free mode, only showing text editor")
        menuItem.setShortcut("F8")
        menuItem.setCheckable(True)
        menuItem.setChecked(self.theParent.isZenMode)
        menuItem.toggled.connect(self.theParent.toggleZenMode)
        self.viewMenu.addAction(menuItem)

        # View > Toggle Full Screen
        menuItem = QAction("Full Screen Mode", self)
        menuItem.setStatusTip("Maximises the main window")
        menuItem.setShortcut("F11")
        menuItem.triggered.connect(self.theParent.toggleFullScreenMode)
        self.viewMenu.addAction(menuItem)

        # View > Separator
        self.viewMenu.addSeparator()

        # View > Project Timeline
        menuItem = QAction("Show Project Timeline", self)
        menuItem.setStatusTip("Open the project timeline window")
        menuItem.setShortcut("Ctrl+T")
        menuItem.triggered.connect(self.theParent.showTimeLineDialog)
        self.viewMenu.addAction(menuItem)

        return

    def _buildEditMenu(self):

        # Edit
        self.editMenu = self.addMenu("&Edit")

        # Edit > Undo
        menuItem = QAction("Undo", self)
        menuItem.setStatusTip("Undo last change")
        menuItem.setShortcut("Ctrl+Z")
        menuItem.triggered.connect(lambda: self._docAction(nwDocAction.UNDO))
        self.editMenu.addAction(menuItem)

        # Edit > Redo
        menuItem = QAction("Redo", self)
        menuItem.setStatusTip("Redo last change")
        menuItem.setShortcut("Ctrl+Y")
        menuItem.triggered.connect(lambda: self._docAction(nwDocAction.REDO))
        self.editMenu.addAction(menuItem)

        # Edit > Separator
        self.editMenu.addSeparator()

        # Edit > Cut
        menuItem = QAction("Cut", self)
        menuItem.setStatusTip("Cut selected text")
        menuItem.setShortcut("Ctrl+X")
        menuItem.triggered.connect(lambda: self._docAction(nwDocAction.CUT))
        self.editMenu.addAction(menuItem)

        # Edit > Copy
        menuItem = QAction("Copy", self)
        menuItem.setStatusTip("Copy selected text")
        menuItem.setShortcut("Ctrl+C")
        menuItem.triggered.connect(lambda: self._docAction(nwDocAction.COPY))
        self.editMenu.addAction(menuItem)

        # Edit > Paste
        menuItem = QAction("Paste", self)
        menuItem.setStatusTip("Paste text from clipboard")
        menuItem.setShortcut("Ctrl+V")
        menuItem.triggered.connect(lambda: self._docAction(nwDocAction.PASTE))
        self.editMenu.addAction(menuItem)

        # Edit > Separator
        self.editMenu.addSeparator()

        # Edit > Find
        menuItem = QAction("Find", self)
        menuItem.setStatusTip("Find text in document")
        menuItem.setShortcut("Ctrl+F")
        menuItem.triggered.connect(lambda: self._docAction(nwDocAction.FIND))
        self.editMenu.addAction(menuItem)

        # Edit > Replace
        menuItem = QAction("Replace", self)
        menuItem.setStatusTip("Replace text in document")
        if self.mainConf.osDarwin:
            menuItem.setShortcut("Ctrl+=")
        else:
            menuItem.setShortcut("Ctrl+H")
        menuItem.triggered.connect(lambda: self._docAction(nwDocAction.REPLACE))
        self.editMenu.addAction(menuItem)

        # Edit > Find Next
        menuItem = QAction("Find Next", self)
        menuItem.setStatusTip("Find next occurrence text in document")
        if self.mainConf.osDarwin:
            menuItem.setShortcuts(["Ctrl+G","F3"])
        else:
            menuItem.setShortcuts(["F3","Ctrl+G"])
        menuItem.triggered.connect(lambda: self._docAction(nwDocAction.GO_NEXT))
        self.editMenu.addAction(menuItem)

        # Edit > Find Prev
        menuItem = QAction("Find Previous", self)
        menuItem.setStatusTip("Find previous occurrence text in document")
        if self.mainConf.osDarwin:
            menuItem.setShortcuts(["Ctrl+Shift+G","Shift+F3"])
        else:
            menuItem.setShortcuts(["Shift+F3","Ctrl+Shift+G"])
        menuItem.triggered.connect(lambda: self._docAction(nwDocAction.GO_PREV))
        self.editMenu.addAction(menuItem)

        # Edit > Replace Next
        menuItem = QAction("Replace Next", self)
        menuItem.setStatusTip("Find and replace next occurrence text in document")
        menuItem.setShortcut("Ctrl+Shift+1")
        menuItem.triggered.connect(lambda: self._docAction(nwDocAction.REPL_NEXT))
        self.editMenu.addAction(menuItem)

        # Edit > Separator
        self.editMenu.addSeparator()

        # Edit > Select All
        menuItem = QAction("Select All", self)
        menuItem.setStatusTip("Select all text in document")
        menuItem.setShortcut("Ctrl+A")
        menuItem.triggered.connect(lambda: self._docAction(nwDocAction.SEL_ALL))
        self.editMenu.addAction(menuItem)

        # Edit > Select Paragraph
        menuItem = QAction("Select Paragraph", self)
        menuItem.setStatusTip("Select all text in paragraph")
        menuItem.setShortcut("Ctrl+Shift+A")
        menuItem.triggered.connect(lambda: self._docAction(nwDocAction.SEL_PARA))
        self.editMenu.addAction(menuItem)

        return

    def _buildFormatMenu(self):

        # Format
        self.fmtMenu = self.addMenu("&Format")

        # Format > Bold Text
        menuItem = QAction("Bold Text", self)
        menuItem.setStatusTip("Make selected text bold")
        menuItem.setShortcut("Ctrl+B")
        menuItem.triggered.connect(lambda: self._docAction(nwDocAction.BOLD))
        self.fmtMenu.addAction(menuItem)

        # Format > Italic Text
        menuItem = QAction("Italic Text", self)
        menuItem.setStatusTip("Make selected text italic")
        menuItem.setShortcut("Ctrl+I")
        menuItem.triggered.connect(lambda: self._docAction(nwDocAction.ITALIC))
        self.fmtMenu.addAction(menuItem)

        # Format > Underline Text
        menuItem = QAction("Underline Text", self)
        menuItem.setStatusTip("Underline selected text")
        menuItem.setShortcut("Ctrl+U")
        menuItem.triggered.connect(lambda: self._docAction(nwDocAction.U_LINE))
        self.fmtMenu.addAction(menuItem)

        # Edit > Separator
        self.fmtMenu.addSeparator()

        # Format > Double Quotes
        menuItem = QAction("Wrap Double Quotes", self)
        menuItem.setStatusTip("Wrap selected text in double quotes")
        menuItem.setShortcut("Ctrl+D")
        menuItem.triggered.connect(lambda: self._docAction(nwDocAction.D_QUOTE))
        self.fmtMenu.addAction(menuItem)

        # Format > Single Quotes
        menuItem = QAction("Wrap Single Quotes", self)
        menuItem.setStatusTip("Wrap selected text in single quotes")
        menuItem.setShortcut("Ctrl+Shift+D")
        menuItem.triggered.connect(lambda: self._docAction(nwDocAction.S_QUOTE))
        self.fmtMenu.addAction(menuItem)

        return

    def _buildToolsMenu(self):

        # Tools
        self.toolsMenu = self.addMenu("&Tools")

        # Tools > Move Up
        self.toolsMoveUp = QAction("Move Tree Item Up", self)
        self.toolsMoveUp.setStatusTip("Move item up")
        self.toolsMoveUp.setShortcut("Ctrl+Shift+Up")
        self.toolsMoveUp.triggered.connect(lambda : self._moveTreeItem(-1))
        self.toolsMenu.addAction(self.toolsMoveUp)

        # Tools > Move Down
        self.toolsMoveDown = QAction("Move Tree Item Down", self)
        self.toolsMoveDown.setStatusTip("Move item down")
        self.toolsMoveDown.setShortcut("Ctrl+Shift+Down")
        self.toolsMoveDown.triggered.connect(lambda : self._moveTreeItem(1))
        self.toolsMenu.addAction(self.toolsMoveDown)

        # Tools > Separator
        self.toolsMenu.addSeparator()

        # Tools > Toggle Spell Check
        self.toolsSpellCheck = QAction("Check Spelling", self)
        self.toolsSpellCheck.setStatusTip("Toggle check spelling")
        self.toolsSpellCheck.setCheckable(True)
        self.toolsSpellCheck.setChecked(self.theProject.spellCheck)
        self.toolsSpellCheck.toggled.connect(self._toggleSpellCheck)
        self.toolsSpellCheck.setShortcut("Ctrl+F7")
        self.toolsMenu.addAction(self.toolsSpellCheck)

        # Tools > Update Spell Check
        menuItem = QAction("Re-Run Spell Check", self)
        menuItem.setStatusTip("Run the spell checker on current document")
        menuItem.setShortcut("F7")
        menuItem.triggered.connect(self.theParent.docEditor.updateSpellCheck)
        self.toolsMenu.addAction(menuItem)

        # Tools > Separator
        self.toolsMenu.addSeparator()

        # Tools > Rebuild Indices
        menuItem = QAction("Rebuild Index", self)
        menuItem.setStatusTip("Rebuild the tag indices and word counts")
        menuItem.setShortcut("F9")
        menuItem.triggered.connect(self.theParent.rebuildIndex)
        self.toolsMenu.addAction(menuItem)

        # Tools > Backup
        menuItem = QAction("Backup Project", self)
        menuItem.setStatusTip("Backup Project")
        menuItem.triggered.connect(self.theParent.backupProject)
        self.toolsMenu.addAction(menuItem)

        # Tools > Settings
        menuItem = QAction("Preferences", self)
        menuItem.setStatusTip("Preferences")
        menuItem.setShortcut("Ctrl+,")
        menuItem.triggered.connect(self.theParent.editConfigDialog)
        self.toolsMenu.addAction(menuItem)

        return

    def _buildHelpMenu(self):

        # Help
        self.helpMenu = self.addMenu("&Help")

        # Help > About
        menuItem = QAction("About %s" % nw.__package__, self)
        menuItem.setStatusTip("About %s" % nw.__package__)
        menuItem.triggered.connect(self._showAbout)
        self.helpMenu.addAction(menuItem)

        # Help > About Qt5
        menuItem = QAction("About Qt5", self)
        menuItem.setStatusTip("About Qt5")
        menuItem.triggered.connect(self._showAboutQt)
        self.helpMenu.addAction(menuItem)

        # Help > Separator
        self.helpMenu.addSeparator()

        # Document > Preview
        menuItem = QAction("Documentation", self)
        menuItem.setStatusTip("View documentation")
        menuItem.setShortcut("F1")
        menuItem.triggered.connect(self._openHelp)
        self.helpMenu.addAction(menuItem)

        return

# END Class GuiMainMenu
