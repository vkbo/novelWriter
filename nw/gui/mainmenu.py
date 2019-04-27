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

from PyQt5.QtWidgets      import QMenu
# from os                   import path
# from PyQt5.QtWidgets      import qApp, QWidget, QMainWindow, QVBoxLayout, QFrame, QSplitter, QAction, QToolBar, QFileDialog, QStackedWidget
# from PyQt5.QtCore         import Qt, QSize, pyqtSlot
# from PyQt5.QtGui          import QIcon

# from nw.gui.doctree       import GuiDocTree
# from nw.gui.doctreectx    import GuiDocTreeCtx
# from nw.gui.doceditor     import GuiDocEditor
# from nw.gui.docdetails    import GuiDocDetails
# from nw.gui.projecteditor import GuiProjectEditor
# from nw.gui.statusbar     import GuiMainStatus
# from nw.project.project   import NWProject
# from nw.project.document  import NWDoc
# from nw.project.item      import NWItem
# from nw.enum              import nwItemType, nwItemClass, nwDocAction, nwItemAction

logger = logging.getLogger(__name__)

class GuiMainMenu(QMenu):

    def __init__(self, theParent, theProject):
        QMenu.__init__(self, theParent)

        logger.debug("Initialising Main Menu ...")
        self.mainConf    = nw.CONFIG
        self.theProject  = NWProject()
        self.theDocument = NWDoc(self.theProject, self)

        self._buildMenu()

        logger.debug("Main Menu initialisation complete")

        return

    def openRecentProject(self, menuItem, recentItem):
        logger.verbose("User requested opening recent project #%d" % recentItem)
        self.theProject.openProject(self.mainConf.recentList[recentItem])
        self.treeView.buildTree()
        self._setWindowTitle(self.theProject.projName)
        return True

    ##
    #  GUI Builders
    ##

    def _buildMenu(self):

        # Project
        projMenu = self.addMenu("&Project")

        # Project > New Project
        menuItem = QAction(QIcon.fromTheme("folder-new"), "New Project", self)
        menuItem.setStatusTip("Create New Project")
        menuItem.triggered.connect(self.newProject)
        projMenu.addAction(menuItem)

        # Project > Open Project
        menuItem = QAction(QIcon.fromTheme("folder-open"), "Open Project", self)
        menuItem.setStatusTip("Open Project")
        menuItem.setShortcut("Ctrl+Shift+O")
        menuItem.triggered.connect(self.openProject)
        projMenu.addAction(menuItem)

        # Project > Save Project
        menuItem = QAction(QIcon.fromTheme("document-save"), "Save Project", self)
        menuItem.setStatusTip("Save Project")
        menuItem.setShortcut("Ctrl+Shift+S")
        menuItem.triggered.connect(self.saveProject)
        projMenu.addAction(menuItem)

        # Project > Recent Projects
        recentMenu = projMenu.addMenu(QIcon.fromTheme("document-open-recent"),"Recent Projects")
        for n in range(len(self.mainConf.recentList)):
            recentProject = self.mainConf.recentList[n]
            if recentProject == "": continue
            menuItem = QAction(QIcon.fromTheme("folder-open"), "%d: %s" % (n,recentProject), projMenu)
            menuItem.triggered.connect(lambda menuItem, n=n : self.openRecentProject(menuItem, n))
            recentMenu.addAction(menuItem)

        # Project > Separator
        projMenu.addSeparator()

        # Project > Project Settings
        menuItem = QAction(QIcon.fromTheme("document-properties"), "Project Settings", self)
        menuItem.setStatusTip("Project Settings")
        menuItem.triggered.connect(self.editProject)
        projMenu.addAction(menuItem)

        # Project > Separator
        projMenu.addSeparator()

        # Project > Exit
        menuItem = QAction(QIcon.fromTheme("application-exit"), "Exit", self)
        menuItem.setStatusTip("Exit %s" % nw.__package__)
        menuItem.setShortcut("Ctrl+Q")
        menuItem.triggered.connect(self._menuExit)
        projMenu.addAction(menuItem)

        ############################################################################################

        # Item
        itemMenu = self.addMenu("&Item")

        # Item > New
        menuItem = QAction(QIcon.fromTheme("document-new"), "&New Document", self)
        menuItem.setStatusTip("Create New Document")
        menuItem.setShortcut("Ctrl+N")
        itemMenu.addAction(menuItem)

        # Item > Open
        menuItem = QAction(QIcon.fromTheme("document-open"), "&Open Document", self)
        menuItem.setStatusTip("Open Selected Document")
        menuItem.setShortcut("Ctrl+O")
        itemMenu.addAction(menuItem)

        # Item > Save
        menuItem = QAction(QIcon.fromTheme("document-save"), "&Save Document", self)
        menuItem.setStatusTip("Save Current Document")
        menuItem.setShortcut("Ctrl+S")
        menuItem.triggered.connect(self.saveDocument)
        itemMenu.addAction(menuItem)

        # Item > Separator
        itemMenu.addSeparator()

        # Item > New Folder
        menuItem = QAction(QIcon.fromTheme("folder-new"), "New Folder", self)
        menuItem.setStatusTip("New Folder")
        menuItem.setShortcut("Ctrl+Shift+N")
        itemMenu.addAction(menuItem)

        # Item > New Root
        rootMenu = itemMenu.addMenu(QIcon.fromTheme("folder-new"), "Create Root Group")
        self.rootItems = {}
        self.rootItems[nwItemClass.NOVEL]      = QAction(QIcon.fromTheme("folder-new"), "Novel Root",     rootMenu)
        self.rootItems[nwItemClass.PLOT]       = QAction(QIcon.fromTheme("folder-new"), "Plot Root",      rootMenu)
        self.rootItems[nwItemClass.CHARACTER]  = QAction(QIcon.fromTheme("folder-new"), "Character Root", rootMenu)
        self.rootItems[nwItemClass.WORLD]      = QAction(QIcon.fromTheme("folder-new"), "Location Root",  rootMenu)
        self.rootItems[nwItemClass.TIMELINE]   = QAction(QIcon.fromTheme("folder-new"), "Timeline Root",  rootMenu)
        self.rootItems[nwItemClass.OBJECT]     = QAction(QIcon.fromTheme("folder-new"), "Object Root",    rootMenu)
        self.rootItems[nwItemClass.CUSTOM]     = QAction(QIcon.fromTheme("folder-new"), "Custom Root",    rootMenu)
        rootMenu.addActions(self.rootItems.values())

        # Item > Separator
        itemMenu.addSeparator()

        # Item > Delete Item
        menuItem = QAction(QIcon.fromTheme("folder-delete"), "Delete Item", self)
        menuItem.setStatusTip("Delete Selected Item")
        menuItem.setShortcut("Del")
        itemMenu.addAction(menuItem)

        ############################################################################################

        # Edit
        editMenu = self.addMenu("&Edit")

        # Edit > Undo
        menuItem = QAction(QIcon.fromTheme("edit-undo"), "Undo", self)
        menuItem.setStatusTip("Undo Last Change")
        menuItem.setShortcut("Ctrl+Z")
        menuItem.triggered.connect(lambda: self.docEditor.docAction(nwDocAction.UNDO))
        editMenu.addAction(menuItem)

        # Edit > Redo
        menuItem = QAction(QIcon.fromTheme("edit-redo"), "Redo", self)
        menuItem.setStatusTip("Redo Last Change")
        menuItem.setShortcut("Ctrl+Y")
        menuItem.triggered.connect(lambda: self.docEditor.docAction(nwDocAction.REDO))
        editMenu.addAction(menuItem)

        # Edit > Separator
        editMenu.addSeparator()

        # Edit > Cut
        menuItem = QAction(QIcon.fromTheme("edit-cut"), "Cut", self)
        menuItem.setStatusTip("Cut Selected Text")
        menuItem.setShortcut("Ctrl+X")
        menuItem.triggered.connect(lambda: self.docEditor.docAction(nwDocAction.CUT))
        editMenu.addAction(menuItem)

        # Edit > Copy
        menuItem = QAction(QIcon.fromTheme("edit-copy"), "Copy", self)
        menuItem.setStatusTip("Copy Selected Text")
        menuItem.setShortcut("Ctrl+C")
        menuItem.triggered.connect(lambda: self.docEditor.docAction(nwDocAction.COPY))
        editMenu.addAction(menuItem)

        # Edit > Paste
        menuItem = QAction(QIcon.fromTheme("edit-paste"), "Paste", self)
        menuItem.setStatusTip("Paste Text from Clipboard")
        menuItem.setShortcut("Ctrl+V")
        menuItem.triggered.connect(lambda: self.docEditor.docAction(nwDocAction.PASTE))
        editMenu.addAction(menuItem)

        # Edit > Separator
        editMenu.addSeparator()

        # Edit > Select All
        menuItem = QAction(QIcon.fromTheme("edit-select-all"), "Select All", self)
        menuItem.setStatusTip("Select All Text in Document")
        menuItem.setShortcut("Ctrl+A")
        menuItem.triggered.connect(lambda: self.docEditor.docAction(nwDocAction.SEL_ALL))
        editMenu.addAction(menuItem)

        # Edit > Select Paragraph
        menuItem = QAction(QIcon.fromTheme("edit-select-all"), "Select Paragraph", self)
        menuItem.setStatusTip("Select All Text in Paragraph")
        menuItem.setShortcut("Ctrl+Shift+A")
        menuItem.triggered.connect(lambda: self.docEditor.docAction(nwDocAction.SEL_PARA))
        editMenu.addAction(menuItem)

        # Edit > Separator
        editMenu.addSeparator()

        # Edit > Settings
        menuItem = QAction(QIcon.fromTheme("applications-system"), "Program Setting", self)
        menuItem.setStatusTip("Change %s Settings" % nw.__package__)
        editMenu.addAction(menuItem)

        ############################################################################################

        # Format
        fmtMenu = self.addMenu("&Format")

        # Format > Bold Text
        menuItem = QAction(QIcon.fromTheme("format-text-bold"), "Bold Text", self)
        menuItem.setStatusTip("Make Selected Text Bold")
        menuItem.setShortcut("Ctrl+B")
        menuItem.triggered.connect(lambda: self.docEditor.docAction(nwDocAction.BOLD))
        fmtMenu.addAction(menuItem)

        # Format > Italic Text
        menuItem = QAction(QIcon.fromTheme("format-text-italic"), "Italic Text", self)
        menuItem.setStatusTip("Make Selected Text Italic")
        menuItem.setShortcut("Ctrl+I")
        menuItem.triggered.connect(lambda: self.docEditor.docAction(nwDocAction.ITALIC))
        fmtMenu.addAction(menuItem)

        # Format > Underline Text
        menuItem = QAction(QIcon.fromTheme("format-text-underline"), "Underline Text", self)
        menuItem.setStatusTip("Underline Selected Text")
        menuItem.setShortcut("Ctrl+U")
        menuItem.triggered.connect(lambda: self.docEditor.docAction(nwDocAction.U_LINE))
        fmtMenu.addAction(menuItem)

        # Edit > Separator
        fmtMenu.addSeparator()

        # Format > Double Quotes
        menuItem = QAction(QIcon.fromTheme("insert-text"), "Wrap Double Quotes", self)
        menuItem.setStatusTip("Wrap Selected Text in Double Quotes")
        menuItem.setShortcut("Ctrl+D")
        menuItem.triggered.connect(lambda: self.docEditor.docAction(nwDocAction.D_QUOTE))
        fmtMenu.addAction(menuItem)

        # Format > Single Quotes
        menuItem = QAction(QIcon.fromTheme("insert-text"), "Wrap Single Quotes", self)
        menuItem.setStatusTip("Wrap Selected Text in Single Quotes")
        menuItem.setShortcut("Ctrl+Shift+D")
        menuItem.triggered.connect(lambda: self.docEditor.docAction(nwDocAction.S_QUOTE))
        fmtMenu.addAction(menuItem)

        ############################################################################################

        # Help
        helpMenu = self.addMenu("&Help")

        # Help > About
        menuItem = QAction(QIcon.fromTheme("help-about"), "About %s" % nw.__package__, self)
        menuItem.setStatusTip("About %s" % nw.__package__)
        menuItem.triggered.connect(self._showAbout)
        helpMenu.addAction(menuItem)

        # Help > About Qt5
        menuItem = QAction(QIcon.fromTheme("help-about"), "About Qt5", self)
        menuItem.setStatusTip("About Qt5")
        helpMenu.addAction(menuItem)

        if not self.mainConf.debugGUI:
            return

        ############################################################################################

        # Debug GUI
        debugMenu = self.addMenu("&Debug")

        return

# END Class GuiMainMenu
