"""
novelWriter – GUI Project Tree
==============================

File History:
Created: 2018-09-29 [0.0.1]  GuiProjectTree
Created: 2022-06-06 [2.0rc1] GuiProjectView
Created: 2022-06-06 [2.0rc1] GuiProjectToolBar
Created: 2023-11-22 [2.2rc1] _TreeContextMenu

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

from enum import Enum
from time import time

from PyQt5.QtCore import QPoint, Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent, QIcon, QMouseEvent, QPalette
from PyQt5.QtWidgets import (
    QAbstractItemView, QAction, QFrame, QHBoxLayout, QHeaderView, QLabel,
    QMenu, QShortcut, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import minmax
from novelwriter.constants import nwHeaders, nwLabels, nwUnicode, trConst
from novelwriter.core.coretools import DocDuplicator, DocMerger, DocSplitter
from novelwriter.core.item import NWItem
from novelwriter.dialogs.docmerge import GuiDocMerge
from novelwriter.dialogs.docsplit import GuiDocSplit
from novelwriter.dialogs.editlabel import GuiEditLabel
from novelwriter.dialogs.projectsettings import GuiProjectSettings
from novelwriter.enum import nwDocMode, nwItemClass, nwItemLayout, nwItemType
from novelwriter.extensions.modified import NIconToolButton
from novelwriter.gui.theme import STYLES_MIN_TOOLBUTTON
from novelwriter.types import (
    QtAlignLeft, QtAlignRight, QtMouseLeft, QtMouseMiddle, QtSizeExpanding,
    QtUserRole
)

logger = logging.getLogger(__name__)


class GuiProjectView(QWidget):
    """This is a wrapper class holding all the elements of the project
    tree. The core object is the project tree itself. Most methods
    available are mapped through to the project tree class.
    """

    # Signals triggered when the meta data values of items change
    treeItemChanged = pyqtSignal(str)
    rootFolderChanged = pyqtSignal(str)
    wordCountsChanged = pyqtSignal()

    # Signals for user interaction with the project tree
    selectedItemChanged = pyqtSignal(str)
    openDocumentRequest = pyqtSignal(str, Enum, str, bool)

    # Requests for the main GUI
    projectSettingsRequest = pyqtSignal(int)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        # Build GUI
        self.projTree = GuiProjectTree(self)
        self.projBar = GuiProjectToolBar(self)
        self.projBar.setEnabled(False)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.projBar, 0)
        self.outerBox.addWidget(self.projTree, 1)
        self.outerBox.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setSpacing(0)

        self.setLayout(self.outerBox)

        # Keyboard Shortcuts
        self.keyMoveUp = QShortcut(self.projTree)
        self.keyMoveUp.setKey("Ctrl+Up")
        self.keyMoveUp.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.keyMoveUp.activated.connect(lambda: self.projTree.moveTreeItem(-1))

        self.keyMoveDn = QShortcut(self.projTree)
        self.keyMoveDn.setKey("Ctrl+Down")
        self.keyMoveDn.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.keyMoveDn.activated.connect(lambda: self.projTree.moveTreeItem(1))

        self.keyGoPrev = QShortcut(self.projTree)
        self.keyGoPrev.setKey("Alt+Up")
        self.keyGoPrev.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.keyGoPrev.activated.connect(lambda: self.projTree.moveToNextItem(-1))

        self.keyGoNext = QShortcut(self.projTree)
        self.keyGoNext.setKey("Alt+Down")
        self.keyGoNext.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.keyGoNext.activated.connect(lambda: self.projTree.moveToNextItem(1))

        self.keyGoUp = QShortcut(self.projTree)
        self.keyGoUp.setKey("Alt+Left")
        self.keyGoUp.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.keyGoUp.activated.connect(lambda: self.projTree.moveToLevel(-1))

        self.keyGoDown = QShortcut(self.projTree)
        self.keyGoDown.setKey("Alt+Right")
        self.keyGoDown.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.keyGoDown.activated.connect(lambda: self.projTree.moveToLevel(1))

        self.keyContext = QShortcut(self.projTree)
        self.keyContext.setKey("Ctrl+.")
        self.keyContext.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.keyContext.activated.connect(lambda: self.projTree.openContextOnSelected())

        # Signals
        self.selectedItemChanged.connect(self.projBar.treeSelectionChanged)
        self.projTree.itemRefreshed.connect(self.projBar.treeItemRefreshed)
        self.projBar.newDocumentFromTemplate.connect(self.createFileFromTemplate)

        # Function Mappings
        self.emptyTrash = self.projTree.emptyTrash
        self.requestDeleteItem = self.projTree.requestDeleteItem
        self.getSelectedHandle = self.projTree.getSelectedHandle
        self.changedSince = self.projTree.changedSince

        return

    ##
    #  Methods
    ##

    def updateTheme(self) -> None:
        """Update theme elements."""
        self.projBar.updateTheme()
        self.populateTree()
        return

    def initSettings(self) -> None:
        """Initialise GUI elements that depend on specific settings."""
        self.projTree.initSettings()
        return

    def closeProjectTasks(self) -> None:
        """Clear project-related GUI content."""
        self.projBar.clearContent()
        self.projBar.setEnabled(False)
        self.projTree.clearTree()
        return

    def openProjectTasks(self) -> None:
        """Run open project tasks."""
        self.populateTree()
        self.projBar.buildQuickLinksMenu()
        self.projBar.setEnabled(True)
        return

    def saveProjectTasks(self) -> None:
        """Run save project tasks."""
        self.projTree.saveTreeOrder()
        return

    def populateTree(self) -> None:
        """Build the tree structure from project data."""
        self.projTree.buildTree()
        return

    def setTreeFocus(self) -> None:
        """Forward the set focus call to the tree widget."""
        self.projTree.setFocus()
        return

    def treeHasFocus(self) -> bool:
        """Check if the project tree has focus."""
        return self.projTree.hasFocus()

    ##
    #  Public Slots
    ##

    @pyqtSlot(str, str)
    def renameTreeItem(self, tHandle: str | None = None, name: str = "") -> None:
        """External request to rename an item or the currently selected
        item. This is triggered by the global menu or keyboard shortcut.
        """
        if tHandle is None:
            tHandle = self.projTree.getSelectedHandle()
        if tHandle:
            self.projTree.renameTreeItem(tHandle, name=name)
        return

    @pyqtSlot(str, bool)
    def setSelectedHandle(self, tHandle: str, doScroll: bool = False) -> None:
        """Select an item and optionally scroll it into view."""
        self.projTree.setSelectedHandle(tHandle, doScroll=doScroll)
        return

    @pyqtSlot(str)
    def updateItemValues(self, tHandle: str) -> None:
        """Update tree item."""
        if nwItem := SHARED.project.tree[tHandle]:
            self.projTree.setTreeItemValues(nwItem)
        return

    @pyqtSlot(str)
    def createFileFromTemplate(self, tHandle: str) -> None:
        """Create a new document from a template."""
        logger.debug("Template selected: '%s'", tHandle)
        self.projTree.newTreeItem(nwItemType.FILE, copyDoc=tHandle)
        return

    @pyqtSlot(str, int, int, int)
    def updateCounts(self, tHandle: str, cCount: int, wCount: int, pCount: int) -> None:
        """Slot for updating the word count of a specific item."""
        self.projTree.propagateCount(tHandle, wCount, countChildren=True)
        self.wordCountsChanged.emit()
        return

    @pyqtSlot(str)
    def updateRootItem(self, tHandle: str) -> None:
        """Process root item changes."""
        self.projBar.buildQuickLinksMenu()
        return

    @pyqtSlot(str, nwItemClass)
    def createNewNote(self, tag: str, itemClass: nwItemClass) -> None:
        """Process new not request."""
        self.projTree.createNewNote(tag, itemClass)
        return

    @pyqtSlot(str)
    def refreshUserLabels(self, kind: str) -> None:
        """Refresh status or importance labels."""
        self.projTree.refreshUserLabels(kind)
        return


class GuiProjectToolBar(QWidget):

    newDocumentFromTemplate = pyqtSignal(str)

    def __init__(self, projView: GuiProjectView) -> None:
        super().__init__(parent=projView)

        logger.debug("Create: GuiProjectToolBar")

        self.projView = projView
        self.projTree = projView.projTree

        iSz = SHARED.theme.baseIconSize
        mPx = CONFIG.pxInt(2)

        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)

        # Widget Label
        self.viewLabel = QLabel(self.tr("Project Content"), self)
        self.viewLabel.setFont(SHARED.theme.guiFontB)
        self.viewLabel.setContentsMargins(0, 0, 0, 0)
        self.viewLabel.setSizePolicy(QtSizeExpanding, QtSizeExpanding)

        # Quick Links
        self.mQuick = QMenu(self)

        self.tbQuick = NIconToolButton(self, iSz)
        self.tbQuick.setToolTip("%s [Ctrl+L]" % self.tr("Quick Links"))
        self.tbQuick.setShortcut("Ctrl+L")
        self.tbQuick.setMenu(self.mQuick)

        # Move Buttons
        self.tbMoveU = NIconToolButton(self, iSz)
        self.tbMoveU.setToolTip("%s [Ctrl+Up]" % self.tr("Move Up"))
        self.tbMoveU.clicked.connect(lambda: self.projTree.moveTreeItem(-1))

        self.tbMoveD = NIconToolButton(self, iSz)
        self.tbMoveD.setToolTip("%s [Ctrl+Down]" % self.tr("Move Down"))
        self.tbMoveD.clicked.connect(lambda: self.projTree.moveTreeItem(1))

        # Add Item Menu
        self.mAdd = QMenu(self)

        self.aAddEmpty = self.mAdd.addAction(trConst(nwLabels.ITEM_DESCRIPTION["document"]))
        self.aAddEmpty.triggered.connect(
            lambda: self.projTree.newTreeItem(nwItemType.FILE, hLevel=0, isNote=False)
        )

        self.aAddChap = self.mAdd.addAction(trConst(nwLabels.ITEM_DESCRIPTION["doc_h2"]))
        self.aAddChap.triggered.connect(
            lambda: self.projTree.newTreeItem(nwItemType.FILE, hLevel=2, isNote=False)
        )

        self.aAddScene = self.mAdd.addAction(trConst(nwLabels.ITEM_DESCRIPTION["doc_h3"]))
        self.aAddScene.triggered.connect(
            lambda: self.projTree.newTreeItem(nwItemType.FILE, hLevel=3, isNote=False)
        )

        self.aAddNote = self.mAdd.addAction(trConst(nwLabels.ITEM_DESCRIPTION["note"]))
        self.aAddNote.triggered.connect(
            lambda: self.projTree.newTreeItem(nwItemType.FILE, hLevel=1, isNote=True)
        )

        self.aAddFolder = self.mAdd.addAction(trConst(nwLabels.ITEM_DESCRIPTION["folder"]))
        self.aAddFolder.triggered.connect(
            lambda: self.projTree.newTreeItem(nwItemType.FOLDER)
        )

        self.mTemplates = _UpdatableMenu(self.mAdd)
        self.mTemplates.setActionsVisible(False)
        self.mTemplates.menuItemTriggered.connect(lambda h: self.newDocumentFromTemplate.emit(h))
        self.mAdd.addMenu(self.mTemplates)

        self.mAddRoot = self.mAdd.addMenu(trConst(nwLabels.ITEM_DESCRIPTION["root"]))
        self._buildRootMenu()

        self.tbAdd = NIconToolButton(self, iSz)
        self.tbAdd.setToolTip("%s [Ctrl+N]" % self.tr("Add Item"))
        self.tbAdd.setShortcut("Ctrl+N")
        self.tbAdd.setMenu(self.mAdd)

        # More Options Menu
        self.mMore = QMenu(self)

        self.aExpand = self.mMore.addAction(self.tr("Expand All"))
        self.aExpand.triggered.connect(lambda: self.projTree.setExpandedFromHandle(None, True))

        self.aCollapse = self.mMore.addAction(self.tr("Collapse All"))
        self.aCollapse.triggered.connect(lambda: self.projTree.setExpandedFromHandle(None, False))

        self.aEmptyTrash = self.mMore.addAction(self.tr("Empty Trash"))
        self.aEmptyTrash.triggered.connect(lambda: self.projTree.emptyTrash())

        self.tbMore = NIconToolButton(self, iSz)
        self.tbMore.setToolTip(self.tr("More Options"))
        self.tbMore.setMenu(self.mMore)

        # Assemble
        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.viewLabel)
        self.outerBox.addWidget(self.tbQuick)
        self.outerBox.addWidget(self.tbMoveU)
        self.outerBox.addWidget(self.tbMoveD)
        self.outerBox.addWidget(self.tbAdd)
        self.outerBox.addWidget(self.tbMore)
        self.outerBox.setContentsMargins(mPx, mPx, 0, mPx)
        self.outerBox.setSpacing(0)

        self.setLayout(self.outerBox)
        self.updateTheme()

        logger.debug("Ready: GuiProjectToolBar")

        return

    ##
    #  Methods
    ##

    def updateTheme(self) -> None:
        """Update theme elements."""
        qPalette = self.palette()
        qPalette.setBrush(QPalette.ColorRole.Window, qPalette.base())
        self.setPalette(qPalette)

        buttonStyle = SHARED.theme.getStyleSheet(STYLES_MIN_TOOLBUTTON)
        self.tbQuick.setStyleSheet(buttonStyle)
        self.tbMoveU.setStyleSheet(buttonStyle)
        self.tbMoveD.setStyleSheet(buttonStyle)
        self.tbAdd.setStyleSheet(buttonStyle)
        self.tbMore.setStyleSheet(buttonStyle)

        self.tbQuick.setThemeIcon("bookmark")
        self.tbMoveU.setThemeIcon("up")
        self.tbMoveD.setThemeIcon("down")
        self.tbAdd.setThemeIcon("add")
        self.tbMore.setThemeIcon("menu")

        self.aAddEmpty.setIcon(SHARED.theme.getIcon("proj_document"))
        self.aAddChap.setIcon(SHARED.theme.getIcon("proj_chapter"))
        self.aAddScene.setIcon(SHARED.theme.getIcon("proj_scene"))
        self.aAddNote.setIcon(SHARED.theme.getIcon("proj_note"))
        self.aAddFolder.setIcon(SHARED.theme.getIcon("proj_folder"))

        self.buildQuickLinksMenu()
        self._buildRootMenu()

        return

    def clearContent(self) -> None:
        """Clear dynamic content on the tool bar."""
        self.mQuick.clear()
        self.mTemplates.clearMenu()
        return

    def buildQuickLinksMenu(self) -> None:
        """Build the quick link menu."""
        logger.debug("Rebuilding quick links menu")
        self.mQuick.clear()
        for tHandle, nwItem in SHARED.project.tree.iterRoots(None):
            action = self.mQuick.addAction(nwItem.itemName)
            action.setData(tHandle)
            action.setIcon(SHARED.theme.getIcon(nwLabels.CLASS_ICON[nwItem.itemClass]))
            action.triggered.connect(
                lambda _, tHandle=tHandle: self.projView.setSelectedHandle(tHandle, doScroll=True)
            )
        return

    ##
    #  Public Slots
    ##

    @pyqtSlot(str, NWItem, QIcon)
    def treeItemRefreshed(self, tHandle: str, nwItem: NWItem, icon: QIcon) -> None:
        """Process change in tree items to update menu content."""
        if nwItem.isTemplateFile() and nwItem.isActive:
            self.mTemplates.addUpdate(tHandle, nwItem.itemName, icon)
        elif tHandle in self.mTemplates:
            self.mTemplates.remove(tHandle)
        return

    @pyqtSlot(str)
    def treeSelectionChanged(self, tHandle: str) -> None:
        """Toggle the visibility of the new item entries for novel
        documents. They should only be visible if novel documents can
        actually be added.
        """
        nwItem = SHARED.project.tree[tHandle]
        allowDoc = isinstance(nwItem, NWItem) and nwItem.documentAllowed()
        self.aAddEmpty.setVisible(allowDoc)
        self.aAddChap.setVisible(allowDoc)
        self.aAddScene.setVisible(allowDoc)
        return

    ##
    #  Internal Functions
    ##

    def _buildRootMenu(self) -> None:
        """Build the rood folder menu."""
        def addClass(itemClass: nwItemClass) -> None:
            aNew = self.mAddRoot.addAction(trConst(nwLabels.CLASS_NAME[itemClass]))
            aNew.setIcon(SHARED.theme.getIcon(nwLabels.CLASS_ICON[itemClass]))
            aNew.triggered.connect(lambda: self.projTree.newTreeItem(nwItemType.ROOT, itemClass))
            self.mAddRoot.addAction(aNew)
            return

        self.mAddRoot.clear()
        addClass(nwItemClass.NOVEL)
        self.mAddRoot.addSeparator()
        addClass(nwItemClass.PLOT)
        addClass(nwItemClass.CHARACTER)
        addClass(nwItemClass.WORLD)
        addClass(nwItemClass.TIMELINE)
        addClass(nwItemClass.OBJECT)
        addClass(nwItemClass.ENTITY)
        addClass(nwItemClass.CUSTOM)
        self.mAddRoot.addSeparator()
        addClass(nwItemClass.ARCHIVE)
        addClass(nwItemClass.TEMPLATE)

        return


class GuiProjectTree(QTreeWidget):

    C_DATA   = 0
    C_NAME   = 0
    C_COUNT  = 1
    C_ACTIVE = 2
    C_STATUS = 3

    D_HANDLE = QtUserRole
    D_WORDS  = QtUserRole + 1

    itemRefreshed = pyqtSignal(str, NWItem, QIcon)

    def __init__(self, projView: GuiProjectView) -> None:
        super().__init__(parent=projView)

        logger.debug("Create: GuiProjectTree")

        self.projView = projView

        # Internal Variables
        self._treeMap: dict[str, QTreeWidgetItem] = {}
        self._timeChanged = 0.0
        self._popAlert = None

        # Cached Translations
        self.trActive = self.tr("Active")
        self.trInactive = self.tr("Inactive")
        self.trPermDelete = self.tr("Permanently delete {0} file(s) from Trash?")

        # Build GUI
        # =========

        # Context Menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._openContextMenu)

        # Tree Settings
        iPx = SHARED.theme.baseIconHeight
        cMg = CONFIG.pxInt(6)

        self.setIconSize(SHARED.theme.baseIconSize)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setUniformRowHeights(True)
        self.setAllColumnsShowFocus(True)
        self.setExpandsOnDoubleClick(False)
        self.setAutoExpandDelay(1000)
        self.setHeaderHidden(True)
        self.setIndentation(iPx)
        self.setColumnCount(4)

        # Lock the column sizes
        treeHeader = self.header()
        treeHeader.setStretchLastSection(False)
        treeHeader.setMinimumSectionSize(iPx + cMg)
        treeHeader.setSectionResizeMode(self.C_NAME, QHeaderView.ResizeMode.Stretch)
        treeHeader.setSectionResizeMode(self.C_COUNT, QHeaderView.ResizeMode.ResizeToContents)
        treeHeader.setSectionResizeMode(self.C_ACTIVE, QHeaderView.ResizeMode.Fixed)
        treeHeader.setSectionResizeMode(self.C_STATUS, QHeaderView.ResizeMode.Fixed)
        treeHeader.resizeSection(self.C_ACTIVE, iPx + cMg)
        treeHeader.resizeSection(self.C_STATUS, iPx + cMg)

        # Allow Move by Drag & Drop
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

        # Disable built-in auto scroll as it isn't working in some Qt
        # releases (see #1561) and instead use our own implementation
        self.setAutoScroll(False)

        # But don't allow drop on root level
        # Due to a bug, this stops working somewhere between Qt 5.15.3
        # and 5.15.8, so this is also blocked in dropEvent (see #1569)
        trRoot = self.invisibleRootItem()
        trRoot.setFlags(trRoot.flags() ^ Qt.ItemFlag.ItemIsDropEnabled)

        # Set selection options
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        # Connect signals
        self.itemDoubleClicked.connect(self._treeDoubleClick)
        self.itemSelectionChanged.connect(self._treeSelectionChange)

        # Auto Scroll
        self._scrollMargin = SHARED.theme.baseIconHeight
        self._scrollDirection = 0
        self._scrollTimer = QTimer(self)
        self._scrollTimer.timeout.connect(self._doAutoScroll)
        self._scrollTimer.setInterval(250)

        # Set custom settings
        self.initSettings()

        logger.debug("Ready: GuiProjectTree")

        return

    def initSettings(self) -> None:
        """Set or update tree widget settings."""
        # Scroll bars
        if CONFIG.hideVScroll:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        if CONFIG.hideHScroll:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        else:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        return

    ##
    #  Class Methods
    ##

    def clearTree(self) -> None:
        """Clear the GUI content and the related map."""
        self.clear()
        self._treeMap = {}
        self._timeChanged = 0.0
        return

    def createNewNote(self, tag: str, itemClass: nwItemClass) -> None:
        """Create a new note. This function is used by the document
        editor to create note files for unknown tags.
        """
        if itemClass != nwItemClass.NO_CLASS:
            if not (rHandle := SHARED.project.tree.findRoot(itemClass)):
                self.newTreeItem(nwItemType.ROOT, itemClass)
                rHandle = SHARED.project.tree.findRoot(itemClass)
            if rHandle and (tHandle := SHARED.project.newFile(tag, rHandle)):
                SHARED.project.writeNewFile(tHandle, 1, False, f"@tag: {tag}\n\n")
                self.revealNewTreeItem(tHandle, wordCount=True)
        return

    def newTreeItem(self, itemType: nwItemType, itemClass: nwItemClass | None = None,
                    hLevel: int = 1, isNote: bool = False, copyDoc: str | None = None) -> bool:
        """Add new item to the tree, with a given itemType (and
        itemClass if Root), and attach it to the selected handle. Also
        make sure the item is added in a place it can be added, and that
        other meta data is set correctly to ensure a valid project tree.
        """
        if not SHARED.hasProject:
            logger.error("No project open")
            return False

        nHandle = None
        tHandle = None

        if itemType == nwItemType.ROOT and isinstance(itemClass, nwItemClass):

            tHandle = SHARED.project.newRoot(itemClass)
            sHandle = self.getSelectedHandle()
            pItem = SHARED.project.tree[sHandle] if sHandle else None
            nHandle = pItem.itemRoot if pItem else None

        elif itemType in (nwItemType.FILE, nwItemType.FOLDER):

            sHandle = self.getSelectedHandle()
            pItem = SHARED.project.tree[sHandle] if sHandle else None
            if sHandle is None or pItem is None:
                SHARED.error(self.tr("Did not find anywhere to add the file or folder!"))
                return False

            # Collect some information about the selected item
            qItem = self._getTreeItem(sHandle)
            sLevel = nwHeaders.H_LEVEL.get(pItem.mainHeading, 0)
            sIsParent = False if qItem is None else qItem.childCount() > 0

            if SHARED.project.tree.isTrash(sHandle):
                SHARED.error(self.tr("Cannot add new files or folders to the Trash folder."))
                return False

            # Set default label and determine if new item is to be added
            # as child or sibling to the selected item
            if itemType == nwItemType.FILE:
                if copyDoc and (cItem := SHARED.project.tree[copyDoc]):
                    newLabel = cItem.itemName
                    asChild = sIsParent and pItem.isDocumentLayout()
                elif isNote:
                    newLabel = self.tr("New Note")
                    asChild = sIsParent
                elif hLevel == 2:
                    newLabel = self.tr("New Chapter")
                    asChild = sIsParent and pItem.isDocumentLayout() and sLevel < 2
                elif hLevel == 3:
                    newLabel = self.tr("New Scene")
                    asChild = sIsParent and pItem.isDocumentLayout() and sLevel < 3
                else:
                    newLabel = self.tr("New Document")
                    asChild = sIsParent and pItem.isDocumentLayout()
            else:
                newLabel = self.tr("New Folder")
                asChild = False

            if not (asChild or pItem.isFolderType() or pItem.isRootType()):
                # Move to the parent item so that the new item is added
                # as a sibling instead
                nHandle = sHandle
                sHandle = pItem.itemParent
                if sHandle is None:
                    # Bug: We have a condition that is unhandled
                    logger.error("Internal error")
                    return False

            # Ask for label
            newLabel, dlgOk = GuiEditLabel.getLabel(self, text=newLabel)
            if not dlgOk:
                logger.info("New item creation cancelled by user")
                return False

            # Add the file or folder
            if itemType == nwItemType.FILE:
                tHandle = SHARED.project.newFile(newLabel, sHandle)
            else:
                tHandle = SHARED.project.newFolder(newLabel, sHandle)

        else:
            logger.error("Failed to add new item")
            return False

        # If there is no handle set, return here. This is a bug.
        if tHandle is None:  # pragma: no cover
            logger.error("Internal error")
            return True

        # Handle new file creation
        if itemType == nwItemType.FILE and copyDoc:
            SHARED.project.copyFileContent(tHandle, copyDoc)
        elif itemType == nwItemType.FILE and hLevel > 0:
            SHARED.project.writeNewFile(tHandle, hLevel, not isNote)

        # Add the new item to the project tree
        self.revealNewTreeItem(tHandle, nHandle=nHandle, wordCount=True)
        self.projView.setTreeFocus()  # See issue #1376

        return True

    def revealNewTreeItem(self, tHandle: str | None, nHandle: str | None = None,
                          wordCount: bool = False) -> bool:
        """Reveal a newly added project item in the project tree."""
        nwItem = SHARED.project.tree[tHandle] if tHandle else None
        if tHandle is None or nwItem is None:
            return False

        trItem = self._addTreeItem(nwItem, nHandle)
        if trItem is None:
            return False

        if nwItem.isFileType() and wordCount:
            wC = SHARED.project.index.getCounts(tHandle)[1]
            self.propagateCount(tHandle, wC)
            self.projView.wordCountsChanged.emit()

        pHandle = nwItem.itemParent
        if pHandle is not None and pHandle in self._treeMap:
            self._treeMap[pHandle].setExpanded(True)

        self._alertTreeChange(tHandle, flush=True)
        self.setCurrentItem(trItem)

        return True

    def moveTreeItem(self, step: int) -> bool:
        """Move an item up or down in the tree."""
        tHandle = self.getSelectedHandle()
        tItem = self._getTreeItem(tHandle)
        if tItem is None:
            logger.debug("No item selected")
            return False

        pItem = tItem.parent()
        isExp = tItem.isExpanded()
        if pItem is None:
            tIndex = self.indexOfTopLevelItem(tItem)
            nChild = self.topLevelItemCount()

            nIndex = tIndex + step
            if nIndex < 0 or nIndex >= nChild:
                return False

            cItem = self.takeTopLevelItem(tIndex)
            self.insertTopLevelItem(nIndex, cItem)

        else:
            tIndex = pItem.indexOfChild(tItem)
            nChild = pItem.childCount()

            nIndex = tIndex + step
            if nIndex < 0 or nIndex >= nChild:
                return False

            cItem = pItem.takeChild(tIndex)
            pItem.insertChild(nIndex, cItem)

        self._alertTreeChange(tHandle, flush=True)
        self.setCurrentItem(tItem)
        tItem.setExpanded(isExp)

        return True

    def moveToNextItem(self, step: int) -> None:
        """Move to the next item of the same tree level."""
        tHandle = self.getSelectedHandle()
        tItem = self._getTreeItem(tHandle) if tHandle else None
        if tItem:
            pItem = tItem.parent() or self.invisibleRootItem()
            next = minmax(pItem.indexOfChild(tItem) + step, 0, pItem.childCount() - 1)
            self.setCurrentItem(pItem.child(next))
        return

    def moveToLevel(self, step: int) -> None:
        """Move to the next item in the parent/child chain."""
        tHandle = self.getSelectedHandle()
        tItem = self._getTreeItem(tHandle) if tHandle else None
        if tItem:
            if step < 0 and tItem.parent():
                self.setCurrentItem(tItem.parent())
            elif step > 0 and tItem.childCount() > 0:
                self.setCurrentItem(tItem.child(0))
        return

    def renameTreeItem(self, tHandle: str, name: str = "") -> None:
        """Open a dialog to edit the label of an item."""
        if nwItem := SHARED.project.tree[tHandle]:
            newLabel, dlgOk = GuiEditLabel.getLabel(self, text=name or nwItem.itemName)
            if dlgOk:
                nwItem.setName(newLabel)
                self.setTreeItemValues(nwItem)
                self._alertTreeChange(tHandle, flush=False)
        return

    def saveTreeOrder(self) -> None:
        """Build a list of the items in the project tree and send them
        to the project class. This syncs up the two versions of the
        project structure, and must be called before any code that
        depends on this order to be up to date.
        """
        items = []
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if isinstance(item, QTreeWidgetItem):
                items = self._scanChildren(items, item, i)
        logger.debug("Saving project tree item order")
        SHARED.project.setTreeOrder(items)
        return

    def getTreeFromHandle(self, tHandle: str) -> list[str]:
        """Recursively return all the child items starting from a given
        item handle.
        """
        result = []
        tIten = self._getTreeItem(tHandle)
        if tIten is not None:
            result = self._scanChildren(result, tIten, 0)
        return result

    def requestDeleteItem(self, tHandle: str | None = None) -> bool:
        """Request an item deleted from the project tree. This function
        can be called on any item, and will check whether to attempt a
        permanent deletion or moving the item to Trash.
        """
        if not SHARED.hasProject:
            logger.error("No project open")
            return False

        if not self.hasFocus():
            logger.info("Delete action blocked due to no widget focus")
            return False

        if tHandle is None:
            tHandle = self.getSelectedHandle()

        if tHandle is None:
            logger.error("There is no item to delete")
            return False

        trashHandle = SHARED.project.tree.trashRoot
        if tHandle == trashHandle:
            logger.error("Cannot delete the Trash folder")
            return False

        nwItem = SHARED.project.tree[tHandle]
        if nwItem is None:
            return False

        if SHARED.project.tree.isTrash(tHandle) or nwItem.isRootType():
            status = self.permDeleteItem(tHandle)
        else:
            status = self.moveItemToTrash(tHandle)

        return status

    @pyqtSlot()
    def emptyTrash(self) -> bool:
        """Permanently delete all documents in the Trash folder. This
        function only asks for confirmation once, and calls the regular
        deleteItem function for each document in the Trash folder.
        """
        if not SHARED.hasProject:
            logger.error("No project open")
            return False

        trashHandle = SHARED.project.tree.trashRoot

        logger.debug("Emptying Trash folder")
        if trashHandle is None:
            SHARED.info(self.tr("There is currently no Trash folder in this project."))
            return False

        trashItems = self.getTreeFromHandle(trashHandle)
        if trashHandle in trashItems:
            trashItems.remove(trashHandle)

        nTrash = len(trashItems)
        if nTrash == 0:
            SHARED.info(self.tr("The Trash folder is already empty."))
            return False

        if not SHARED.question(self.trPermDelete.format(nTrash)):
            logger.info("Action cancelled by user")
            return False

        logger.debug("Deleting %d file(s) from Trash", nTrash)
        for tHandle in reversed(self.getTreeFromHandle(trashHandle)):
            if tHandle == trashHandle:
                continue
            self.permDeleteItem(tHandle, askFirst=False, flush=False)

        if nTrash > 0:
            self._alertTreeChange(trashHandle, flush=True)

        return True

    def moveItemToTrash(self, tHandle: str, askFirst: bool = True, flush: bool = True) -> bool:
        """Move an item to Trash. Root folders cannot be moved to Trash,
        so such a request is cancelled.
        """
        trItemS = self._getTreeItem(tHandle)
        nwItemS = SHARED.project.tree[tHandle]

        if trItemS is None or nwItemS is None:
            logger.error("Could not find tree item for deletion")
            return False

        if SHARED.project.tree.isTrash(tHandle):
            logger.error("Item is already in the Trash folder")
            return False

        if nwItemS.isRootType():
            logger.error("Root folders cannot be moved to Trash")
            return False

        logger.debug("User requested file or folder '%s' move to Trash", tHandle)

        trItemP = trItemS.parent()
        trItemT = self._addTrashRoot()
        if trItemP is None or trItemT is None:
            logger.error("Could not delete item")
            return False

        if askFirst:
            msgYes = SHARED.question(
                self.tr("Move '{0}' to Trash?").format(nwItemS.itemName)
            )
            if not msgYes:
                logger.info("Action cancelled by user")
                return False

        self.propagateCount(tHandle, 0)

        tIndex = trItemP.indexOfChild(trItemS)
        trItemC = trItemP.takeChild(tIndex)
        trItemT.addChild(trItemC)

        self._postItemMove(tHandle)
        self._alertTreeChange(tHandle, flush=flush)

        logger.debug("Moved item '%s' to Trash", tHandle)

        return True

    def permDeleteItem(self, tHandle: str, askFirst: bool = True, flush: bool = True) -> bool:
        """Permanently delete a tree item from the project and the map.
        Root items are handled a little different than other items.
        """
        trItemS = self._getTreeItem(tHandle)
        nwItemS = SHARED.project.tree[tHandle]
        if trItemS is None or nwItemS is None:
            logger.error("Could not find tree item for deletion")
            return False

        if nwItemS.isRootType():
            # Only an empty ROOT folder can be deleted
            if trItemS.childCount() > 0:
                SHARED.error(self.tr("Root folders can only be deleted when they are empty."))
                return False

            logger.debug("Permanently deleting root folder '%s'", tHandle)

            tIndex = self.indexOfTopLevelItem(trItemS)
            self.takeTopLevelItem(tIndex)
            SHARED.project.removeItem(tHandle)
            self._treeMap.pop(tHandle, None)
            self._alertTreeChange(tHandle, flush=True)

            # These are not emitted by the alert function because the
            # item has already been deleted
            self.projView.rootFolderChanged.emit(tHandle)
            self.projView.treeItemChanged.emit(tHandle)

        else:
            if askFirst:
                msgYes = SHARED.question(
                    self.tr("Permanently delete '{0}'?").format(nwItemS.itemName)
                )
                if not msgYes:
                    logger.info("Action cancelled by user")
                    return False

            logger.debug("Permanently deleting item '%s'", tHandle)

            self.propagateCount(tHandle, 0)

            # If a non-root item ends up on root due to a bug, allow it
            # to still be deleted from invisible root (see #2108)
            trItemP = trItemS.parent() or self.invisibleRootItem()
            tIndex = trItemP.indexOfChild(trItemS)
            trItemP.takeChild(tIndex)

            for dHandle in reversed(self.getTreeFromHandle(tHandle)):
                SHARED.closeEditor(dHandle)
                SHARED.project.removeItem(dHandle)
                self._treeMap.pop(dHandle, None)

            self._alertTreeChange(tHandle, flush=flush)
            self.projView.wordCountsChanged.emit()

            # This is not emitted by the alert function because the item
            # has already been deleted
            self.projView.treeItemChanged.emit(tHandle)

        return True

    def refreshUserLabels(self, kind: str) -> None:
        """Refresh status or importance labels."""
        if kind == "s":
            for nwItem in SHARED.project.tree:
                if nwItem.isNovelLike():
                    self.setTreeItemValues(nwItem)
        elif kind == "i":
            for nwItem in SHARED.project.tree:
                if not nwItem.isNovelLike():
                    self.setTreeItemValues(nwItem)
        return

    def setTreeItemValues(self, nwItem: NWItem | None) -> None:
        """Set the name and flag values for a tree item in the project
        tree. Does not trigger a tree change as the data is already
        coming from project data.
        """
        if isinstance(nwItem, NWItem) and (trItem := self._getTreeItem(nwItem.itemHandle)):
            itemStatus, statusIcon = nwItem.getImportStatus()
            hLevel = nwItem.mainHeading
            itemIcon = SHARED.theme.getItemIcon(
                nwItem.itemType, nwItem.itemClass, nwItem.itemLayout, hLevel
            )

            trItem.setIcon(self.C_NAME, itemIcon)
            trItem.setText(self.C_NAME, nwItem.itemName)
            trItem.setIcon(self.C_STATUS, statusIcon)
            trItem.setToolTip(self.C_STATUS, itemStatus)

            if nwItem.isFileType():
                iconName = "checked" if nwItem.isActive else "unchecked"
                toolTip = self.trActive if nwItem.isActive else self.trInactive
                trItem.setToolTip(self.C_ACTIVE, toolTip)
            else:
                iconName = "noncheckable"

            trItem.setIcon(self.C_ACTIVE, SHARED.theme.getIcon(iconName))

            if CONFIG.emphLabels and nwItem.isDocumentLayout():
                trFont = trItem.font(self.C_NAME)
                trFont.setBold(hLevel == "H1" or hLevel == "H2")
                trFont.setUnderline(hLevel == "H1")
                trItem.setFont(self.C_NAME, trFont)

            # Emit Refresh Signal
            self.itemRefreshed.emit(nwItem.itemHandle, nwItem, itemIcon)

        return

    def propagateCount(self, tHandle: str, newCount: int, countChildren: bool = False) -> None:
        """Recursive function setting the word count for a given item,
        and propagating that count upwards in the tree until reaching a
        root item. This function is more efficient than recalculating
        everything each time the word count is updated, but is also
        prone to diverging from the true values if the counts are not
        properly reported to the function.
        """
        tItem = self._getTreeItem(tHandle)
        if tItem is None:
            return

        if countChildren:
            for i in range(tItem.childCount()):
                newCount += int(tItem.child(i).data(self.C_DATA, self.D_WORDS))

        tItem.setText(self.C_COUNT, f"{newCount:n}")
        tItem.setData(self.C_DATA, self.D_WORDS, int(newCount))

        pItem = tItem.parent()
        if pItem is None:
            return

        pCount = 0
        pHandle = None
        for i in range(pItem.childCount()):
            pCount += int(pItem.child(i).data(self.C_DATA, self.D_WORDS))
            pHandle = pItem.data(self.C_DATA, self.D_HANDLE)

        if pHandle:
            if SHARED.project.tree.checkType(pHandle, nwItemType.FILE):
                # A file has an internal word count we need to account
                # for, but a folder always has 0 words on its own.
                pCount += SHARED.project.index.getCounts(pHandle)[1]

            self.propagateCount(pHandle, pCount, countChildren=False)

        return

    def buildTree(self) -> None:
        """Build the entire project tree from scratch. This depends on
        the save project item iterator in the project class which will
        always make sure items with a parent have had their parent item
        sent first.
        """
        logger.debug("Building the project tree ...")
        self.clearTree()
        count = 0
        for nwItem in SHARED.project.iterProjectItems():
            count += 1
            self._addTreeItem(nwItem)
        if count > 0:
            logger.info("%d item(s) added to the project tree", count)
        return

    def getSelectedHandle(self) -> str | None:
        """Get the currently selected handle. If multiple items are
        selected, return the first.
        """
        if items := self.selectedItems():
            return items[0].data(self.C_DATA, self.D_HANDLE)
        return None

    def setSelectedHandle(self, tHandle: str | None, doScroll: bool = False) -> bool:
        """Set a specific handle as the selected item."""
        tItem = self._getTreeItem(tHandle)
        if tItem is None:
            return False

        if tHandle in self._treeMap:
            self.setCurrentItem(self._treeMap[tHandle])

        if (indexes := self.selectedIndexes()) and doScroll:
            self.scrollTo(indexes[0], QAbstractItemView.ScrollHint.PositionAtCenter)

        return True

    def setExpandedFromHandle(self, tHandle: str | None, isExpanded: bool) -> None:
        """Iterate through items below tHandle and change expanded
        status for all child items. If tHandle is None, it affects the
        entire tree.
        """
        trItem = self._getTreeItem(tHandle) or self.invisibleRootItem()
        self._recursiveSetExpanded(trItem, isExpanded)
        return

    def openContextOnSelected(self) -> bool:
        """Open the context menu on the current selected item."""
        if items := self.selectedItems():
            return self._openContextMenu(self.visualItemRect(items[0]).center())
        return False

    def changedSince(self, checkTime: float) -> bool:
        """Check if the tree has changed since a given time."""
        return self._timeChanged > checkTime

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _treeSelectionChange(self) -> None:
        """The user changed which item is selected."""
        tHandle = self.getSelectedHandle()
        if tHandle is not None:
            self.projView.selectedItemChanged.emit(tHandle)

        # When selecting multiple items, don't allow including root
        # items in the selection and instead deselect them
        items = self.selectedItems()
        if items and len(items) > 1:
            for item in items:
                if item.parent() is None:
                    item.setSelected(False)

        return

    @pyqtSlot("QTreeWidgetItem*", int)
    def _treeDoubleClick(self, trItem: QTreeWidgetItem, colNo: int) -> None:
        """Capture a double-click event and either request the document
        for editing if it is a file, or expand/close the node it is not.
        """
        tHandle = self.getSelectedHandle()
        if tHandle is None:
            return

        tItem = SHARED.project.tree[tHandle]
        if tItem is None:
            return

        if tItem.isFileType():
            self.projView.openDocumentRequest.emit(tHandle, nwDocMode.EDIT, "", True)
        else:
            trItem.setExpanded(not trItem.isExpanded())

        return

    @pyqtSlot("QPoint")
    def _openContextMenu(self, clickPos: QPoint) -> bool:
        """The user right clicked an element in the project tree, so we
        open a context menu in-place.
        """
        tItem = None
        tHandle = None
        hasChild = False
        sItem = self.itemAt(clickPos)
        sItems = self.selectedItems()
        if isinstance(sItem, QTreeWidgetItem):
            tHandle = sItem.data(self.C_DATA, self.D_HANDLE)
            tItem = SHARED.project.tree[tHandle]
            hasChild = sItem.childCount() > 0

        if tItem is None or tHandle is None:
            logger.debug("No item found")
            return False

        ctxMenu = _TreeContextMenu(self, tItem)
        trashHandle = SHARED.project.tree.trashRoot
        if trashHandle and tHandle == trashHandle:
            ctxMenu.buildTrashMenu()
        elif len(sItems) > 1:
            handles = [str(x.data(self.C_DATA, self.D_HANDLE)) for x in sItems]
            ctxMenu.buildMultiSelectMenu(handles)
        else:
            ctxMenu.buildSingleSelectMenu(hasChild)

        ctxMenu.exec(self.viewport().mapToGlobal(clickPos))
        ctxMenu.deleteLater()

        return True

    @pyqtSlot()
    def _doAutoScroll(self) -> None:
        """Scroll one item up or down based on direction value."""
        if self._scrollDirection == -1:
            self.scrollToItem(self.itemAbove(self.itemAt(1, 1)))
        elif self._scrollDirection == 1:
            self.scrollToItem(self.itemBelow(self.itemAt(1, self.height() - 1)))
        self._scrollDirection = 0
        self._scrollTimer.stop()
        return

    ##
    #  Events
    ##

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Overload mousePressEvent to clear selection if clicking the
        mouse in a blank area of the tree view, and to load a document
        for viewing if the user middle-clicked.
        """
        super().mousePressEvent(event)
        if event.button() == QtMouseLeft:
            selItem = self.indexAt(event.pos())
            if not selItem.isValid():
                self.clearSelection()
        elif event.button() == QtMouseMiddle:
            selItem = self.itemAt(event.pos())
            if selItem:
                tHandle = selItem.data(self.C_DATA, self.D_HANDLE)
                if (tItem := SHARED.project.tree[tHandle]) and tItem.isFileType():
                    self.projView.openDocumentRequest.emit(tHandle, nwDocMode.VIEW, "", False)
        return

    def startDrag(self, dropAction: Qt.DropAction) -> None:
        """Capture the drag and drop handling to pop alerts."""
        super().startDrag(dropAction)
        if self._popAlert:
            SHARED.error(self._popAlert)
            self._popAlert = None
        return

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Check that we're only dragging items that are siblings, and
        not a root level item.
        """
        items = self.selectedItems()
        if items and (parent := items[0].parent()) and all(x.parent() is parent for x in items):
            super().dragEnterEvent(event)
        else:
            logger.warning("Drag action is not allowed and has been cancelled")
            self._popAlert = self.tr(
                "Drag and drop is only allowed for single items, non-root "
                "items, or multiple items with the same parent."
            )
            event.mimeData().clear()
            event.ignore()
        return

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        """Capture the drag move event to enable edge auto scroll."""
        y = event.pos().y()
        if y < self._scrollMargin:
            if not self._scrollTimer.isActive():
                self._scrollDirection = -1
                self._scrollTimer.start()
        elif y > self.height() - self._scrollMargin:
            if not self._scrollTimer.isActive():
                self._scrollDirection = 1
                self._scrollTimer.start()
        super().dragMoveEvent(event)
        return

    def dropEvent(self, event: QDropEvent) -> None:
        """Overload the drop item event to ensure the drag and drop
        action is allowed, and update relevant data.
        """
        tItem = self.itemAt(event.pos())
        onItem = self.dropIndicatorPosition() == QAbstractItemView.DropIndicatorPosition.OnItem
        onView = self.dropIndicatorPosition() == QAbstractItemView.DropIndicatorPosition.OnViewport
        # Make sure nothing can be dropped on invisible root (see #1569)
        # Make sure nothing can be dropped on the viewport (see #2108)
        if tItem is None or (tItem.parent() is None and not onItem) or onView:
            logger.error("Invalid drop location")
            event.ignore()
            return

        mItems: dict[str, tuple[QTreeWidgetItem, bool]] = {}
        sItems = self.selectedItems()
        if sItems and (parent := sItems[0].parent()) and all(x.parent() is parent for x in sItems):
            for sItem in sItems:
                mHandle = str(sItem.data(self.C_DATA, self.D_HANDLE))
                mItems[mHandle] = (sItem, sItem.isExpanded())
                self.propagateCount(mHandle, 0)

            super().dropEvent(event)

            for mHandle, (sItem, isExpanded) in mItems.items():
                self._postItemMove(mHandle)
                sItem.setExpanded(isExpanded)
                self._alertTreeChange(mHandle, flush=False)

            self.saveTreeOrder()

        return

    ##
    #  Internal Functions
    ##

    def _postItemMove(self, tHandle: str) -> None:
        """Run various maintenance tasks for a moved item."""
        trItemS = self._getTreeItem(tHandle)
        nwItemS = SHARED.project.tree[tHandle]
        trItemP = trItemS.parent() if trItemS else None
        if trItemP is None or nwItemS is None:
            logger.error("Failed to find new parent item of '%s'", tHandle)
            return

        # Update item parent handle in the project
        pHandle = trItemP.data(self.C_DATA, self.D_HANDLE)
        nwItemS.setParent(pHandle)
        trItemP.setExpanded(True)
        logger.debug("The parent of item '%s' has been changed to '%s'", tHandle, pHandle)

        mHandles = self.getTreeFromHandle(tHandle)
        logger.debug("A total of %d item(s) were moved", len(mHandles))
        for mHandle in mHandles:
            logger.debug("Updating item '%s'", mHandle)
            SHARED.project.tree.updateItemData(mHandle)
            if nwItemS.isInactiveClass():
                SHARED.project.index.deleteHandle(mHandle)
            else:
                SHARED.project.index.reIndexHandle(mHandle)
            if mItem := SHARED.project.tree[mHandle]:
                self.setTreeItemValues(mItem)

        # Update word count
        self.propagateCount(tHandle, nwItemS.wordCount, countChildren=True)

        return

    def _getItemWordCount(self, tHandle: str) -> int:
        """Return the word count of a given item handle."""
        tItem = self._getTreeItem(tHandle)
        return int(tItem.data(self.C_DATA, self.D_WORDS)) if tItem else 0

    def _getTreeItem(self, tHandle: str | None) -> QTreeWidgetItem | None:
        """Return the QTreeWidgetItem of a given item handle."""
        return self._treeMap.get(tHandle, None) if tHandle else None

    def _recursiveSetExpanded(self, trItem: QTreeWidgetItem, isExpanded: bool) -> None:
        """Recursive function to set expanded status starting from (and
        not including) a given item.
        """
        if isinstance(trItem, QTreeWidgetItem):
            for i in range(trItem.childCount()):
                chItem = trItem.child(i)
                chItem.setExpanded(isExpanded)
                self._recursiveSetExpanded(chItem, isExpanded)
        return

    def _mergeDocuments(self, tHandle: str, newFile: bool) -> bool:
        """Merge an item's child documents into a single document."""
        logger.info("Request to merge items under handle '%s'", tHandle)
        itemList = self.getTreeFromHandle(tHandle)

        tItem = SHARED.project.tree[tHandle]
        if tItem is None:
            return False

        if tItem.isRootType():
            logger.error("Cannot merge root item")
            return False

        if not newFile:
            itemList.remove(tHandle)

        data, status = GuiDocMerge.getData(SHARED.mainGui, tHandle, itemList)
        if status:
            items = data.get("finalItems", [])
            if not items:
                SHARED.info(self.tr("No documents selected for merging."))
                return False

            # Save the open document first, in case it's part of merge
            SHARED.saveEditor()

            # Create merge object, and append docs
            docMerger = DocMerger(SHARED.project)
            mLabel = self.tr("Merged")

            if newFile:
                docLabel = f"[{mLabel}] {tItem.itemName}"
                mHandle = docMerger.newTargetDoc(tHandle, docLabel)
            elif tItem.isFileType():
                docMerger.setTargetDoc(tHandle)
                mHandle = tHandle
            else:
                return False

            for sHandle in items:
                docMerger.appendText(sHandle, True, mLabel)

            if not docMerger.writeTargetDoc():
                SHARED.error(
                    self.tr("Could not write document content."),
                    info=docMerger.getError()
                )
                return False

            SHARED.project.index.reIndexHandle(mHandle)
            if newFile:
                self.revealNewTreeItem(mHandle, nHandle=tHandle, wordCount=True)

            self.projView.openDocumentRequest.emit(mHandle, nwDocMode.EDIT, "", False)
            self.projView.setSelectedHandle(mHandle, doScroll=True)

            if data.get("moveToTrash", False):
                for sHandle in reversed(data.get("finalItems", [])):
                    trItem = self._getTreeItem(sHandle)
                    if isinstance(trItem, QTreeWidgetItem) and trItem.childCount() == 0:
                        self.moveItemToTrash(sHandle, askFirst=False, flush=False)

            self._alertTreeChange(mHandle, flush=True)
            self.projView.wordCountsChanged.emit()

        else:
            logger.info("Action cancelled by user")
            return False

        return True

    def _splitDocument(self, tHandle: str) -> bool:
        """Split a document into multiple documents."""
        logger.info("Request to split items with handle '%s'", tHandle)

        tItem = SHARED.project.tree[tHandle]
        if tItem is None:
            return False

        if not tItem.isFileType() or tItem.itemParent is None:
            logger.error("Only valid document items can be split")
            return False

        data, text, status = GuiDocSplit.getData(SHARED.mainGui, tHandle)
        if status:
            headerList = data.get("headerList", [])
            intoFolder = data.get("intoFolder", False)
            docHierarchy = data.get("docHierarchy", False)

            docSplit = DocSplitter(SHARED.project, tHandle)
            if intoFolder:
                fHandle = docSplit.newParentFolder(tItem.itemParent, tItem.itemName)
                self.revealNewTreeItem(fHandle, nHandle=tHandle)
                self._alertTreeChange(fHandle, flush=False)
            else:
                docSplit.setParentItem(tItem.itemParent)

            docSplit.splitDocument(headerList, text)
            for writeOk, dHandle, nHandle in docSplit.writeDocuments(docHierarchy):
                SHARED.project.index.reIndexHandle(dHandle)
                self.revealNewTreeItem(dHandle, nHandle=nHandle, wordCount=True)
                self._alertTreeChange(dHandle, flush=False)
                if not writeOk:
                    SHARED.error(
                        self.tr("Could not write document content."),
                        info=docSplit.getError()
                    )

            if data.get("moveToTrash", False):
                self.moveItemToTrash(tHandle, askFirst=False, flush=True)

            self.saveTreeOrder()

        else:
            logger.info("Action cancelled by user")
            return False

        return True

    def _duplicateFromHandle(self, tHandle: str) -> bool:
        """Duplicate the item hierarchy from a given item."""
        itemTree = self.getTreeFromHandle(tHandle)
        nItems = len(itemTree)
        if nItems == 0:
            return False
        elif nItems == 1:
            question = self.tr("Do you want to duplicate this document?")
        else:
            question = self.tr("Do you want to duplicate this item and all child items?")

        if not SHARED.question(question):
            return False

        docDup = DocDuplicator(SHARED.project)
        dupCount = 0
        for dHandle, nHandle in docDup.duplicate(itemTree):
            SHARED.project.index.reIndexHandle(dHandle)
            self.revealNewTreeItem(dHandle, nHandle=nHandle, wordCount=True)
            self._alertTreeChange(dHandle, flush=False)
            dupCount += 1

        if dupCount != nItems:
            SHARED.warn(self.tr("Could not duplicate all items."))

        self.saveTreeOrder()

        return True

    def _scanChildren(self, itemList: list, tItem: QTreeWidgetItem, tIndex: int) -> list[str]:
        """This is a recursive function returning all items in a tree
        starting at a given QTreeWidgetItem.
        """
        tHandle = tItem.data(self.C_DATA, self.D_HANDLE)
        cCount = tItem.childCount()

        # Update tree-related meta data
        nwItem = SHARED.project.tree[tHandle]
        if nwItem is not None:
            nwItem.setExpanded(tItem.isExpanded() and cCount > 0)
            nwItem.setOrder(tIndex)

        itemList.append(tHandle)
        for i in range(cCount):
            self._scanChildren(itemList, tItem.child(i), i)

        return itemList

    def _addTreeItem(self, nwItem: NWItem | None,
                     nHandle: str | None = None) -> QTreeWidgetItem | None:
        """Create a QTreeWidgetItem from an NWItem and add it to the
        project tree. Returns the widget if the item is valid, otherwise
        a None is returned.
        """
        if not nwItem:
            logger.error("Invalid item cannot be added to project tree")
            return None

        tHandle = nwItem.itemHandle
        pHandle = nwItem.itemParent
        newItem = QTreeWidgetItem()

        newItem.setText(self.C_NAME, "")
        newItem.setText(self.C_COUNT, "0")
        newItem.setText(self.C_ACTIVE, "")
        newItem.setText(self.C_STATUS, "")

        newItem.setTextAlignment(self.C_NAME, QtAlignLeft)
        newItem.setTextAlignment(self.C_COUNT, QtAlignRight)
        newItem.setTextAlignment(self.C_ACTIVE, QtAlignLeft)
        newItem.setTextAlignment(self.C_STATUS, QtAlignLeft)

        newItem.setData(self.C_DATA, self.D_HANDLE, tHandle)
        newItem.setData(self.C_DATA, self.D_WORDS, 0)

        if pHandle is None and nwItem.isRootType():
            pItem = self.invisibleRootItem()
        elif pHandle and pHandle in self._treeMap:
            pItem = self._treeMap[pHandle]
        else:
            SHARED.error(self.tr(
                "There is nowhere to add item with name '{0}'."
            ).format(nwItem.itemName))
            return None

        byIndex = -1
        if nHandle is not None and nHandle in self._treeMap:
            byIndex = pItem.indexOfChild(self._treeMap[nHandle])
        if byIndex >= 0:
            pItem.insertChild(byIndex + 1, newItem)
        else:
            pItem.addChild(newItem)

        self._treeMap[tHandle] = newItem
        self.propagateCount(tHandle, nwItem.wordCount, countChildren=True)
        self.setTreeItemValues(nwItem)
        newItem.setExpanded(nwItem.isExpanded)

        return newItem

    def _addTrashRoot(self) -> QTreeWidgetItem | None:
        """Adds the trash root folder if it doesn't already exist in the
        project tree.
        """
        trashHandle = SHARED.project.trashFolder()
        if trashHandle is None:
            return None

        trItem = self._getTreeItem(trashHandle)
        if trItem is None:
            trItem = self._addTreeItem(SHARED.project.tree[trashHandle])
            if trItem is not None:
                trItem.setExpanded(True)
                self._alertTreeChange(trashHandle, flush=True)

        return trItem

    def _alertTreeChange(self, tHandle: str | None, flush: bool = False) -> None:
        """Update information on tree change state, and emit necessary
        signals. A flush is only needed if an item is moved, created or
        deleted.
        """
        self._timeChanged = time()
        SHARED.project.setProjectChanged(True)
        if flush:
            self.saveTreeOrder()

        if tHandle is None or tHandle not in SHARED.project.tree:
            return

        tItem = SHARED.project.tree[tHandle]
        if tItem and tItem.isRootType():
            self.projView.rootFolderChanged.emit(tHandle)

        self.projView.treeItemChanged.emit(tHandle)

        return


class _UpdatableMenu(QMenu):

    menuItemTriggered = pyqtSignal(str)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self._map: dict[str, QAction] = {}
        self.setTitle(self.tr("From Template"))
        self.triggered.connect(self._actionTriggered)
        return

    def __contains__(self, tHandle: str) -> bool:
        """Look up a handle in the menu."""
        return tHandle in self._map

    ##
    #  Methods
    ##

    def addUpdate(self, tHandle: str, name: str, icon: QIcon) -> None:
        """Add or update a template item."""
        if tHandle in self._map:
            action = self._map[tHandle]
            action.setText(name)
            action.setIcon(icon)
        else:
            action = QAction(icon, name, self)
            action.setData(tHandle)
            self.addAction(action)
            self._map[tHandle] = action
        self.setActionsVisible(True)
        return

    def remove(self, tHandle: str) -> None:
        """Remove a template item."""
        if action := self._map.pop(tHandle, None):
            self.removeAction(action)
        if not self._map:
            self.setActionsVisible(False)
        return

    def clearMenu(self) -> None:
        """Clear all menu content."""
        self._map.clear()
        self.clear()
        return

    def setActionsVisible(self, value: bool) -> None:
        """Set the visibility of root action."""
        self.menuAction().setVisible(value)
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(QAction)
    def _actionTriggered(self, action: QAction) -> None:
        """Translate the menu trigger into an item trigger."""
        self.menuItemTriggered.emit(str(action.data()))
        return


class _TreeContextMenu(QMenu):

    def __init__(self, projTree: GuiProjectTree, nwItem: NWItem) -> None:
        super().__init__(parent=projTree)

        self.projTree = projTree
        self.projView = projTree.projView

        self._item = nwItem
        self._handle = nwItem.itemHandle
        self._items: list[NWItem] = []

        logger.debug("Ready: _TreeContextMenu")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: _TreeContextMenu")
        return

    ##
    #  Methods
    ##

    def buildTrashMenu(self) -> None:
        """Build the special menu for the Trash folder."""
        action = self.addAction(self.tr("Empty Trash"))
        action.triggered.connect(self.projTree.emptyTrash)
        return

    def buildSingleSelectMenu(self, hasChild: bool) -> None:
        """Build the single-select menu."""
        isFile = self._item.isFileType()
        isFolder = self._item.isFolderType()
        isRoot = self._item.isRootType()

        # Document Actions
        if isFile:
            self._docActions()
            self.addSeparator()

        # Create New Items
        self._itemCreation()
        self.addSeparator()

        # Edit Item Settings
        action = self.addAction(self.tr("Rename"))
        action.triggered.connect(lambda: self.projTree.renameTreeItem(self._handle))
        if isFile:
            self._itemHeader()
            self._itemActive(False)
        self._itemStatusImport(False)

        # Transform Item
        if isFile or isFolder:
            self._itemTransform(isFile, isFolder, hasChild)
        self.addSeparator()

        # Process Item
        self._itemProcess(isFile, isFolder, isRoot, hasChild)

        return

    def buildMultiSelectMenu(self, handles: list[str]) -> None:
        """Build the multi-select menu."""
        self._items = []
        for tHandle in handles:
            if (tItem := SHARED.project.tree[tHandle]):
                self._items.append(tItem)

        self._itemActive(True)
        self._itemStatusImport(True)
        self.addSeparator()
        self._multiMoveToTrash()
        return

    ##
    #  Menu Builders
    ##

    def _docActions(self) -> None:
        """Add document actions."""
        action = self.addAction(self.tr("Open Document"))
        action.triggered.connect(
            lambda: self.projView.openDocumentRequest.emit(self._handle, nwDocMode.EDIT, "", True)
        )
        action = self.addAction(self.tr("View Document"))
        action.triggered.connect(
            lambda: self.projView.openDocumentRequest.emit(self._handle, nwDocMode.VIEW, "", False)
        )
        return

    def _itemCreation(self) -> None:
        """Add create item actions."""
        menu = self.addMenu(self.tr("Create New ..."))
        menu.addAction(self.projView.projBar.aAddEmpty)
        menu.addAction(self.projView.projBar.aAddChap)
        menu.addAction(self.projView.projBar.aAddScene)
        menu.addAction(self.projView.projBar.aAddNote)
        menu.addAction(self.projView.projBar.aAddFolder)
        return

    def _itemHeader(self) -> None:
        """Check if there is a header that can be used for rename."""
        SHARED.saveEditor()
        if hItem := SHARED.project.index.getItemHeading(self._handle, "T0001"):
            action = self.addAction(self.tr("Rename to Heading"))
            action.triggered.connect(
                lambda: self.projTree.renameTreeItem(self._handle, hItem.title)
            )
        return

    def _itemActive(self, multi: bool) -> None:
        """Add Active/Inactive actions."""
        if multi:
            mSub = self.addMenu(self.tr("Set Active to ..."))
            aOne = mSub.addAction(SHARED.theme.getIcon("checked"), self.projTree.trActive)
            aOne.triggered.connect(lambda: self._iterItemActive(True))
            aTwo = mSub.addAction(SHARED.theme.getIcon("unchecked"), self.projTree.trInactive)
            aTwo.triggered.connect(lambda: self._iterItemActive(False))
        else:
            action = self.addAction(self.tr("Toggle Active"))
            action.triggered.connect(self._toggleItemActive)
        return

    def _itemStatusImport(self, multi: bool) -> None:
        """Add actions for changing status or importance."""
        if self._item.isNovelLike():
            menu = self.addMenu(self.tr("Set Status to ..."))
            current = self._item.itemStatus
            for n, (key, entry) in enumerate(SHARED.project.data.itemStatus.iterItems()):
                name = entry.name
                if not multi and current == key:
                    name += f" ({nwUnicode.U_CHECK})"
                action = menu.addAction(entry.icon, name)
                if multi:
                    action.triggered.connect(lambda n, key=key: self._iterSetItemStatus(key))
                else:
                    action.triggered.connect(lambda n, key=key: self._changeItemStatus(key))
            menu.addSeparator()
            action = menu.addAction(self.tr("Manage Labels ..."))
            action.triggered.connect(
                lambda: self.projView.projectSettingsRequest.emit(GuiProjectSettings.PAGE_STATUS)
            )
        else:
            menu = self.addMenu(self.tr("Set Importance to ..."))
            current = self._item.itemImport
            for n, (key, entry) in enumerate(SHARED.project.data.itemImport.iterItems()):
                name = entry.name
                if not multi and current == key:
                    name += f" ({nwUnicode.U_CHECK})"
                action = menu.addAction(entry.icon, name)
                if multi:
                    action.triggered.connect(lambda n, key=key: self._iterSetItemImport(key))
                else:
                    action.triggered.connect(lambda n, key=key: self._changeItemImport(key))
            menu.addSeparator()
            action = menu.addAction(self.tr("Manage Labels ..."))
            action.triggered.connect(
                lambda: self.projView.projectSettingsRequest.emit(GuiProjectSettings.PAGE_IMPORT)
            )
        return

    def _itemTransform(self, isFile: bool, isFolder: bool, hasChild: bool) -> None:
        """Add actions for the Transform menu."""
        menu = self.addMenu(self.tr("Transform ..."))

        tree = self.projTree
        tHandle = self._handle

        trDoc = trConst(nwLabels.LAYOUT_NAME[nwItemLayout.DOCUMENT])
        trNote = trConst(nwLabels.LAYOUT_NAME[nwItemLayout.NOTE])
        loDoc = nwItemLayout.DOCUMENT
        loNote = nwItemLayout.NOTE
        isDocFile = isFile and self._item.isDocumentLayout()
        isNoteFile = isFile and self._item.isNoteLayout()

        if isNoteFile and self._item.documentAllowed():
            action = menu.addAction(self.tr("Convert to {0}").format(trDoc))
            action.triggered.connect(lambda: self._changeItemLayout(loDoc))

        if isDocFile:
            action = menu.addAction(self.tr("Convert to {0}").format(trNote))
            action.triggered.connect(lambda: self._changeItemLayout(loNote))

        if isFolder and self._item.documentAllowed():
            action = menu.addAction(self.tr("Convert to {0}").format(trDoc))
            action.triggered.connect(lambda: self._covertFolderToFile(loDoc))

        if isFolder:
            action = menu.addAction(self.tr("Convert to {0}").format(trNote))
            action.triggered.connect(lambda: self._covertFolderToFile(loNote))

        if hasChild and isFile:
            action = menu.addAction(self.tr("Merge Child Items into Self"))
            action.triggered.connect(lambda: tree._mergeDocuments(tHandle, False))
            action = menu.addAction(self.tr("Merge Child Items into New"))
            action.triggered.connect(lambda: tree._mergeDocuments(tHandle, True))

        if hasChild and isFolder:
            action = menu.addAction(self.tr("Merge Documents in Folder"))
            action.triggered.connect(lambda: tree._mergeDocuments(tHandle, True))

        if isFile:
            action = menu.addAction(self.tr("Split Document by Headings"))
            action.triggered.connect(lambda: tree._splitDocument(tHandle))

        return

    def _itemProcess(self, isFile: bool, isFolder: bool, isRoot: bool, hasChild: bool) -> None:
        """Add actions for item processing."""
        tree = self.projTree
        tHandle = self._handle
        if hasChild:
            action = self.addAction(self.tr("Expand All"))
            action.triggered.connect(lambda: tree.setExpandedFromHandle(tHandle, True))
            action = self.addAction(self.tr("Collapse All"))
            action.triggered.connect(lambda: tree.setExpandedFromHandle(tHandle, False))

        action = self.addAction(self.tr("Duplicate"))
        action.triggered.connect(lambda: tree._duplicateFromHandle(tHandle))

        if self._item.itemClass == nwItemClass.TRASH or isRoot or (isFolder and not hasChild):
            action = self.addAction(self.tr("Delete Permanently"))
            action.triggered.connect(lambda: tree.permDeleteItem(tHandle))
        else:
            action = self.addAction(self.tr("Move to Trash"))
            action.triggered.connect(lambda: tree.moveItemToTrash(tHandle))

        return

    def _multiMoveToTrash(self) -> None:
        """Add move to Trash action."""
        areTrash = [i.itemClass == nwItemClass.TRASH for i in self._items]
        if all(areTrash):
            action = self.addAction(self.tr("Delete Permanently"))
            action.triggered.connect(self._iterPermDelete)
        elif not any(areTrash):
            action = self.addAction(self.tr("Move to Trash"))
            action.triggered.connect(self._iterMoveToTrash)
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _iterMoveToTrash(self) -> None:
        """Iterate through files and move them to Trash."""
        if SHARED.question(self.tr("Move {0} items to Trash?").format(len(self._items))):
            for tItem in self._items:
                if tItem.isFileType() and tItem.itemClass != nwItemClass.TRASH:
                    self.projTree.moveItemToTrash(tItem.itemHandle, askFirst=False, flush=False)
                self.projTree.saveTreeOrder()
        return

    @pyqtSlot()
    def _iterPermDelete(self) -> None:
        """Iterate through files and delete them."""
        if SHARED.question(self.projTree.trPermDelete.format(len(self._items))):
            for tItem in self._items:
                if tItem.isFileType() and tItem.itemClass == nwItemClass.TRASH:
                    self.projTree.permDeleteItem(tItem.itemHandle, askFirst=False, flush=False)
                self.projTree.saveTreeOrder()
        return

    @pyqtSlot()
    def _toggleItemActive(self) -> None:
        """Toggle the active status of an item."""
        self._item.setActive(not self._item.isActive)
        self.projTree.setTreeItemValues(self._item)
        self.projTree._alertTreeChange(self._handle, flush=False)
        return

    ##
    #  Internal Functions
    ##

    def _iterItemActive(self, isActive: bool) -> None:
        """Set the active status of multiple items."""
        for tItem in self._items:
            if tItem and tItem.isFileType():
                tItem.setActive(isActive)
                self.projTree.setTreeItemValues(tItem)
                self.projTree._alertTreeChange(tItem.itemHandle, flush=False)
        return

    def _changeItemStatus(self, key: str) -> None:
        """Set a new status value of an item."""
        self._item.setStatus(key)
        self.projTree.setTreeItemValues(self._item)
        self.projTree._alertTreeChange(self._handle, flush=False)
        return

    def _iterSetItemStatus(self, key: str) -> None:
        """Change the status value for multiple items."""
        for tItem in self._items:
            if tItem and tItem.isNovelLike():
                tItem.setStatus(key)
                self.projTree.setTreeItemValues(tItem)
                self.projTree._alertTreeChange(tItem.itemHandle, flush=False)
        return

    def _changeItemImport(self, key: str) -> None:
        """Set a new importance value of an item."""
        self._item.setImport(key)
        self.projTree.setTreeItemValues(self._item)
        self.projTree._alertTreeChange(self._handle, flush=False)
        return

    def _iterSetItemImport(self, key: str) -> None:
        """Change the status value for multiple items."""
        for tItem in self._items:
            if tItem and not tItem.isNovelLike():
                tItem.setImport(key)
                self.projTree.setTreeItemValues(tItem)
                self.projTree._alertTreeChange(tItem.itemHandle, flush=False)
        return

    def _changeItemLayout(self, itemLayout: nwItemLayout) -> None:
        """Set a new item layout value of an item."""
        if itemLayout == nwItemLayout.DOCUMENT and self._item.documentAllowed():
            self._item.setLayout(nwItemLayout.DOCUMENT)
            self.projTree.setTreeItemValues(self._item)
            self.projTree._alertTreeChange(self._handle, flush=False)
        elif itemLayout == nwItemLayout.NOTE:
            self._item.setLayout(nwItemLayout.NOTE)
            self.projTree.setTreeItemValues(self._item)
            self.projTree._alertTreeChange(self._handle, flush=False)
        return

    def _covertFolderToFile(self, itemLayout: nwItemLayout) -> None:
        """Convert a folder to a note or document."""
        if self._item.isFolderType():
            msgYes = SHARED.question(self.tr(
                "Do you want to convert the folder to a {0}? "
                "This action cannot be reversed."
            ).format(trConst(nwLabels.LAYOUT_NAME[itemLayout])))
            if msgYes and itemLayout == nwItemLayout.DOCUMENT and self._item.documentAllowed():
                self._item.setType(nwItemType.FILE)
                self._item.setLayout(nwItemLayout.DOCUMENT)
                self.projTree.setTreeItemValues(self._item)
                self.projTree._alertTreeChange(self._handle, flush=False)
            elif msgYes and itemLayout == nwItemLayout.NOTE:
                self._item.setType(nwItemType.FILE)
                self._item.setLayout(nwItemLayout.NOTE)
                self.projTree.setTreeItemValues(self._item)
                self.projTree._alertTreeChange(self._handle, flush=False)
            else:
                logger.info("Folder conversion cancelled")
        return
