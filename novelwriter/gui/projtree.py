"""
novelWriter – GUI Project Tree
==============================

File History:
Created:   2018-09-29 [0.0.1]  GuiProjectTree
Created:   2022-06-06 [2.0rc1] GuiProjectView
Created:   2022-06-06 [2.0rc1] GuiProjectToolBar
Created:   2023-11-22 [2.2rc1] _TreeContextMenu
Rewritten: 2024-11-17 [2.7b1]  GuiProjectTree

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

from PyQt5.QtCore import QModelIndex, QPoint, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QMouseEvent, QPalette
from PyQt5.QtWidgets import (
    QAbstractItemView, QAction, QFrame, QHBoxLayout, QLabel, QMenu, QShortcut,
    QTreeView, QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import qtLambda
from novelwriter.constants import nwLabels, nwStyles, trConst
from novelwriter.core.item import NWItem
from novelwriter.core.itemmodel import ProjectModel, ProjectNode
from novelwriter.dialogs.editlabel import GuiEditLabel
from novelwriter.enum import nwDocMode, nwItemClass, nwItemType
from novelwriter.extensions.modified import NIconToolButton
from novelwriter.gui.theme import STYLES_MIN_TOOLBUTTON
from novelwriter.types import (
    QtHeaderFixed, QtHeaderStretch, QtHeaderToContents, QtMouseLeft,
    QtMouseMiddle, QtScrollAlwaysOff, QtScrollAsNeeded, QtSizeExpanding
)

logger = logging.getLogger(__name__)


class GuiProjectView(QWidget):
    """This is a wrapper class holding all the elements of the project
    tree. The core object is the project tree itself. Most methods
    available are mapped through to the project tree class.
    """

    # Signals triggered when the meta data values of items change
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
        self.keyMoveUp.activated.connect(self.projTree.moveItemUp)

        self.keyMoveDn = QShortcut(self.projTree)
        self.keyMoveDn.setKey("Ctrl+Down")
        self.keyMoveDn.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.keyMoveDn.activated.connect(self.projTree.moveItemDown)

        self.keyGoPrev = QShortcut(self.projTree)
        self.keyGoPrev.setKey("Alt+Up")
        self.keyGoPrev.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.keyGoPrev.activated.connect(self.projTree.moveSiblingUp)

        self.keyGoNext = QShortcut(self.projTree)
        self.keyGoNext.setKey("Alt+Down")
        self.keyGoNext.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.keyGoNext.activated.connect(self.projTree.moveSiblingDown)

        self.keyGoUp = QShortcut(self.projTree)
        self.keyGoUp.setKey("Alt+Left")
        self.keyGoUp.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.keyGoUp.activated.connect(self.projTree.moveToParent)

        self.keyGoDown = QShortcut(self.projTree)
        self.keyGoDown.setKey("Alt+Right")
        self.keyGoDown.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.keyGoDown.activated.connect(self.projTree.moveToFirstChild)

        self.keyContext = QShortcut(self.projTree)
        self.keyContext.setKey("Ctrl+.")
        self.keyContext.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.keyContext.activated.connect(self.projTree.openContextMenu)

        # Signals
        self.selectedItemChanged.connect(self.projBar.treeSelectionChanged)
        self.projTree.itemRefreshed.connect(self.projBar.treeItemRefreshed)
        self.projBar.newDocumentFromTemplate.connect(self.createFileFromTemplate)

        # Function Mappings
        self.getSelectedHandle = self.projTree.getSelectedHandle

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
        # self.projTree.saveTreeOrder()
        return

    def populateTree(self) -> None:
        """Build the tree structure from project data."""
        self.projTree.loadModel()
        return

    def setTreeFocus(self) -> None:
        """Forward the set focus call to the tree widget."""
        self.projTree.setFocus()
        return

    def treeHasFocus(self) -> bool:
        """Check if the project tree has focus."""
        return self.projTree.hasFocus()

    def connectMenuActions(self, rename: QAction, delete: QAction, trash: QAction) -> None:
        """Main menu actions passed to the project tree."""
        self.projTree.addAction(rename)
        self.projTree.addAction(delete)
        self.projTree.addAction(trash)
        rename.triggered.connect(self.renameTreeItem)
        delete.triggered.connect(self.projTree.processDeleteRequest)
        return

    ##
    #  Public Slots
    ##

    @pyqtSlot()
    @pyqtSlot(str, str)
    def renameTreeItem(self, tHandle: str | None = None, name: str = "") -> None:
        """External request to rename an item or the currently selected
        item. This is triggered by the global menu or keyboard shortcut.
        """
        if tHandle is None:
            tHandle = self.projTree.getSelectedHandle()
        if nwItem := SHARED.project.tree[tHandle]:
            newLabel, dlgOk = GuiEditLabel.getLabel(self, text=name or nwItem.itemName)
            if dlgOk:
                nwItem.setName(newLabel)
                nwItem.notifyToRefresh()
        return

    @pyqtSlot(str, bool)
    def setSelectedHandle(self, tHandle: str, doScroll: bool = False) -> None:
        """Select an item and optionally scroll it into view."""
        self.projTree.setSelectedHandle(tHandle, doScroll=doScroll)
        return

    @pyqtSlot(str)
    def setActiveHandle(self, tHandle: str | None) -> None:
        """Highlight the active handle."""
        self.projTree.setActiveHandle(tHandle)
        return

    @pyqtSlot(str)
    def updateItemValues(self, tHandle: str) -> None:
        """Update tree item."""
        # if nwItem := SHARED.project.tree[tHandle]:
        #     self.projTree.setTreeItemValues(nwItem)
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
        self.tbMoveU.clicked.connect(self.projTree.moveItemUp)

        self.tbMoveD = NIconToolButton(self, iSz)
        self.tbMoveD.setToolTip("%s [Ctrl+Down]" % self.tr("Move Down"))
        self.tbMoveD.clicked.connect(self.projTree.moveItemDown)

        # Add Item Menu
        self.mAdd = QMenu(self)

        self.aAddEmpty = self.mAdd.addAction(trConst(nwLabels.ITEM_DESCRIPTION["document"]))
        self.aAddEmpty.triggered.connect(
            qtLambda(self.projTree.newTreeItem, nwItemType.FILE, hLevel=0, isNote=False)
        )

        self.aAddChap = self.mAdd.addAction(trConst(nwLabels.ITEM_DESCRIPTION["doc_h2"]))
        self.aAddChap.triggered.connect(
            qtLambda(self.projTree.newTreeItem, nwItemType.FILE, hLevel=2, isNote=False)
        )

        self.aAddScene = self.mAdd.addAction(trConst(nwLabels.ITEM_DESCRIPTION["doc_h3"]))
        self.aAddScene.triggered.connect(
            qtLambda(self.projTree.newTreeItem, nwItemType.FILE, hLevel=3, isNote=False)
        )

        self.aAddNote = self.mAdd.addAction(trConst(nwLabels.ITEM_DESCRIPTION["note"]))
        self.aAddNote.triggered.connect(
            qtLambda(self.projTree.newTreeItem, nwItemType.FILE, hLevel=1, isNote=True)
        )

        self.aAddFolder = self.mAdd.addAction(trConst(nwLabels.ITEM_DESCRIPTION["folder"]))
        self.aAddFolder.triggered.connect(
            qtLambda(self.projTree.newTreeItem, nwItemType.FOLDER)
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
        self.aExpand.triggered.connect(
            qtLambda(self.projTree.setExpandedFromHandle, None, True)
        )

        self.aCollapse = self.mMore.addAction(self.tr("Collapse All"))
        self.aCollapse.triggered.connect(
            qtLambda(self.projTree.setExpandedFromHandle, None, False)
        )

        self.aEmptyTrash = self.mMore.addAction(self.tr("Empty Trash"))
        self.aEmptyTrash.triggered.connect(qtLambda(self.projTree.emptyTrash))

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
                qtLambda(self.projView.setSelectedHandle, tHandle, doScroll=True)
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
            aNew.triggered.connect(
                qtLambda(self.projTree.newTreeItem, nwItemType.ROOT, itemClass)
            )
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


class GuiProjectTree(QTreeView):

    itemRefreshed = pyqtSignal(str, NWItem, QIcon)

    def __init__(self, projView: GuiProjectView) -> None:
        super().__init__(parent=projView)

        logger.debug("Create: GuiProjectTree")

        self.projView = projView

        # Internal Variables
        # self._actHandle = None

        # Tree Settings
        iPx = SHARED.theme.baseIconHeight

        self.setIconSize(SHARED.theme.baseIconSize)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setUniformRowHeights(True)
        self.setAllColumnsShowFocus(True)
        self.setExpandsOnDoubleClick(False)
        self.setAutoExpandDelay(1000)
        self.setHeaderHidden(True)
        self.setIndentation(iPx)

        # Allow Move by Drag & Drop
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

        # Disable built-in auto scroll as it isn't working in some Qt
        # releases (see #1561) and instead use our own implementation
        # self.setAutoScroll(False)

        # Set selection options
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        # Context Menu
        # self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.openContextMenu)

        # Connect signals
        self.clicked.connect(self._onSingleClick)
        self.doubleClicked.connect(self._onDoubleClick)
        self.collapsed.connect(self._onNodeCollapsed)
        self.expanded.connect(self._onNodeExpanded)

        # Auto Scroll
        # self._scrollMargin = SHARED.theme.baseIconHeight
        # self._scrollDirection = 0
        # self._scrollTimer = QTimer(self)
        # self._scrollTimer.timeout.connect(self._doAutoScroll)
        # self._scrollTimer.setInterval(250)

        # Set custom settings
        self.initSettings()

        logger.debug("Ready: GuiProjectTree")

        return

    def initSettings(self) -> None:
        """Set or update tree widget settings."""
        # Scroll bars
        if CONFIG.hideVScroll:
            self.setVerticalScrollBarPolicy(QtScrollAlwaysOff)
        else:
            self.setVerticalScrollBarPolicy(QtScrollAsNeeded)
        if CONFIG.hideHScroll:
            self.setHorizontalScrollBarPolicy(QtScrollAlwaysOff)
        else:
            self.setHorizontalScrollBarPolicy(QtScrollAsNeeded)
        return

    ##
    #  External Methods
    ##

    def getSelectedHandle(self) -> str | None:
        """Get the currently selected handle."""
        if (indexes := self.selectedIndexes()) and (node := self._getNode(indexes[0])):
            return node.item.itemHandle
        return None

    ##
    #  Module Internal Methods
    ##

    def clearTree(self) -> None:
        """Clear the tree view."""
        self.setModel(None)
        return

    def loadModel(self) -> None:
        """Load and prepare a new project model."""
        selModel = self.selectionModel()
        self.setModel(SHARED.project.tree.model)
        if selModel:
            selModel.deleteLater()
            del selModel

        # Lock the column sizes
        iPx = SHARED.theme.baseIconHeight
        cMg = CONFIG.pxInt(6)

        treeHeader = self.header()
        treeHeader.setStretchLastSection(False)
        treeHeader.setMinimumSectionSize(iPx + cMg)
        treeHeader.setSectionResizeMode(ProjectNode.C_NAME, QtHeaderStretch)
        treeHeader.setSectionResizeMode(ProjectNode.C_COUNT, QtHeaderToContents)
        treeHeader.setSectionResizeMode(ProjectNode.C_ACTIVE, QtHeaderFixed)
        treeHeader.setSectionResizeMode(ProjectNode.C_STATUS, QtHeaderFixed)
        treeHeader.resizeSection(ProjectNode.C_ACTIVE, iPx + cMg)
        treeHeader.resizeSection(ProjectNode.C_STATUS, iPx + cMg)

        self.restoreExpandedState()

        return

    def restoreExpandedState(self) -> None:
        """Expand all nodes that were previously expanded."""
        if model := self._getModel():
            self.blockSignals(True)
            for index in model.allExpanded():
                self.setExpanded(index, True)
            self.blockSignals(False)
        return

    def setSelectedHandle(self, tHandle: str | None, doScroll: bool = False) -> None:
        """Set a specific handle as the selected item."""
        if (model := self._getModel()) and (index := model.indexFromHandle(tHandle)).isValid():
            self.setCurrentIndex(index)
            if doScroll:
                self.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtCenter)
            self.projView.selectedItemChanged.emit(tHandle)
        return

    def newTreeItem(
        self, itemType: nwItemType, itemClass: nwItemClass | None = None,
        hLevel: int = 1, isNote: bool = False, copyDoc: str | None = None,
    ) -> None:
        """Add new item to the tree, with a given itemType (and
        itemClass if Root), and attach it to the selected handle. Also
        make sure the item is added in a place it can be added, and that
        other meta data is set correctly to ensure a valid project tree.
        """
        if not SHARED.hasProject:
            logger.error("No project open")
            return

        tHandle = None
        if itemType == nwItemType.ROOT and isinstance(itemClass, nwItemClass):

            pos = -1
            if (node := self._getNode(self.currentIndex())) and (itemRoot := node.item.itemRoot):
                if root := SHARED.project.tree.nodes.get(itemRoot):
                    pos = root.row() + 1

            SHARED.project.newRoot(itemClass, pos)
            self.restoreExpandedState()

        elif itemType in (nwItemType.FILE, nwItemType.FOLDER):

            if not ((model := self._getModel()) and (node := model.node(self.currentIndex()))):
                SHARED.error(self.tr("Did not find anywhere to add the file or folder!"))
                return

            if node.item.itemClass == nwItemClass.TRASH:
                SHARED.error(self.tr("Cannot add new files or folders to the Trash folder."))
                return

            # Collect some information about the selected item
            sLevel = nwStyles.H_LEVEL.get(node.item.mainHeading, 0)
            sIsParent = node.childCount() > 0

            # Set default label and determine if new item is to be added
            # as child or sibling to the selected item
            if itemType == nwItemType.FILE:
                if copyDoc and (cItem := SHARED.project.tree[copyDoc]):
                    newLabel = cItem.itemName
                    asChild = sIsParent and node.item.isDocumentLayout()
                elif isNote:
                    newLabel = self.tr("New Note")
                    asChild = sIsParent
                elif hLevel == 2:
                    newLabel = self.tr("New Chapter")
                    asChild = sIsParent and node.item.isDocumentLayout() and sLevel < 2
                elif hLevel == 3:
                    newLabel = self.tr("New Scene")
                    asChild = sIsParent and node.item.isDocumentLayout() and sLevel < 3
                else:
                    newLabel = self.tr("New Document")
                    asChild = sIsParent and node.item.isDocumentLayout()
            else:
                newLabel = self.tr("New Folder")
                asChild = False

            pos = -1
            sHandle = None
            if not (asChild or node.item.isFolderType() or node.item.isRootType()):
                pos = node.row() + 1
                sHandle = node.item.itemParent

            sHandle = sHandle or node.item.itemHandle
            newLabel, dlgOk = GuiEditLabel.getLabel(self, text=newLabel)
            if dlgOk:
                # Add the file or folder
                if itemType == nwItemType.FILE:
                    if tHandle := SHARED.project.newFile(newLabel, sHandle, pos):
                        if copyDoc:
                            SHARED.project.copyFileContent(tHandle, copyDoc)
                        elif hLevel > 0:
                            SHARED.project.writeNewFile(tHandle, hLevel, not isNote)
                        SHARED.project.index.reIndexHandle(tHandle)
                        SHARED.project.tree.refreshItems([tHandle])
                else:
                    SHARED.project.newFolder(newLabel, sHandle, pos)

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
            if not self.indexAt(event.pos()).isValid():
                self.selectionModel().clearCurrentIndex()
        elif event.button() == QtMouseMiddle:
            if (node := self._getNode(self.indexAt(event.pos()))) and node.item.isFileType():
                self.projView.openDocumentRequest.emit(
                    node.item.itemHandle, nwDocMode.VIEW, "", False
                )
        return

    ##
    #  Public Slots
    ##

    @pyqtSlot()
    def moveItemUp(self) -> None:
        """Move an item up in the tree."""
        if model := self._getModel():
            model.internalMove(self.currentIndex(), -1)
        return

    @pyqtSlot()
    def moveItemDown(self) -> None:
        """Move an item down in the tree."""
        if model := self._getModel():
            model.internalMove(self.currentIndex(), 1)
        return

    @pyqtSlot()
    def moveSiblingUp(self) -> None:
        """Skip to the previous sibling."""
        if (node := self._getNode(self.currentIndex())) and (parent := node.parent()):
            if (move := parent.child(node.row() - 1)) and (model := self._getModel()):
                self.setCurrentIndex(model.indexFromNode(move))
        return

    @pyqtSlot()
    def moveSiblingDown(self) -> None:
        """Skip to the next sibling."""
        if (node := self._getNode(self.currentIndex())) and (parent := node.parent()):
            if (move := parent.child(node.row() + 1)) and (model := self._getModel()):
                self.setCurrentIndex(model.indexFromNode(move))
        return

    @pyqtSlot()
    def moveToParent(self) -> None:
        """Move to parent item."""
        if (
            (model := self._getModel())
            and (node := model.node(self.currentIndex()))
            and (parent := node.parent())
        ):
            self.setCurrentIndex(model.indexFromNode(parent))
        return

    @pyqtSlot()
    def moveToFirstChild(self) -> None:
        """Move to first child item."""
        if (
            (model := self._getModel())
            and (node := model.node(self.currentIndex()))
            and (child := node.child(0))
        ):
            self.setCurrentIndex(model.indexFromNode(child))
        return

    @pyqtSlot()
    def processDeleteRequest(self, askFirst: bool = True) -> None:
        """Move selected items to Trash."""
        if (items := self._selectedRows()) and (model := self._getModel()):
            if len(items) == 1 and (node := model.node(items[0])) and node.item.isRootType():
                if node.childCount() == 0:
                    SHARED.project.removeItem(node.item.itemHandle)
                else:
                    SHARED.error(self.tr("Root folders can only be deleted when they are empty."))
                return

            if model.trashSelection(items):
                if askFirst:
                    if not SHARED.question(self.tr("Permanently delete selected item(s)?")):
                        logger.info("Action cancelled by user")
                        return
                for node in model.nodes(items):
                    SHARED.project.removeItem(node.item.itemHandle)

            elif trashNode := SHARED.project.tree.trash:
                if askFirst and not SHARED.question(self.tr("Move selected item(s) to Trash?")):
                    logger.info("Action cancelled by user")
                    return
                model.multiMove(items, model.indexFromNode(trashNode))
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(QModelIndex)
    def _onSingleClick(self, index: QModelIndex) -> None:
        """The user changed which item is selected."""
        if node := self._getNode(index):
            self.projView.selectedItemChanged.emit(node.item.itemHandle)
        return

    @pyqtSlot(QModelIndex)
    def _onDoubleClick(self, index: QModelIndex) -> None:
        """Capture a double-click event and either request the document
        for editing if it is a file, or expand/close the node if not.
        """
        if node := self._getNode(index):
            if node.item.isFileType():
                self.projView.openDocumentRequest.emit(
                    node.item.itemHandle, nwDocMode.EDIT, "", True
                )
            else:
                self.setExpanded(index, not self.isExpanded(index))
        return

    @pyqtSlot(QModelIndex)
    def _onNodeCollapsed(self, index: QModelIndex) -> None:
        """Capture a node collapse, and pass it to the model."""
        if node := self._getNode(index):
            node.item.setExpanded(False)
        return

    @pyqtSlot(QModelIndex)
    def _onNodeExpanded(self, index: QModelIndex) -> None:
        """Capture a node expand, and pass it to the model."""
        if node := self._getNode(index):
            node.item.setExpanded(True)
        return

    ##
    #  Internal Functions
    ##

    def _selectedRows(self) -> list[QModelIndex]:
        """Return all column 0 indexes."""
        return [i for i in self.selectedIndexes() if i.column() == 0]

    def _getModel(self) -> ProjectModel | None:
        """Return a project node corresponding to a model index."""
        if isinstance(model := self.model(), ProjectModel):
            return model
        return None

    def _getNode(self, index: QModelIndex) -> ProjectNode | None:
        """Return a project node corresponding to a model index."""
        if isinstance(model := self.model(), ProjectModel) and (node := model.node(index)):
            return node
        return None

    # =========================================================================================== #
    #  Old Code
    # =========================================================================================== #

    def createNewNote(self, tag: str, itemClass: nwItemClass) -> None:
        """Create a new note. This function is used by the document
        editor to create note files for unknown tags.
        """
        # if itemClass != nwItemClass.NO_CLASS:
        #     if not (rHandle := SHARED.project.tree.findRoot(itemClass)):
        #         self.newTreeItem(nwItemType.ROOT, itemClass)
        #         rHandle = SHARED.project.tree.findRoot(itemClass)
        #     if rHandle and (tHandle := SHARED.project.newFile(tag, rHandle)):
        #         SHARED.project.writeNewFile(tHandle, 1, False, f"@tag: {tag}\n\n")
        #         self.revealNewTreeItem(tHandle, wordCount=True)
        return

    @pyqtSlot()
    def emptyTrash(self) -> bool:
        """Permanently delete all documents in the Trash folder. This
        function only asks for confirmation once, and calls the regular
        deleteItem function for each document in the Trash folder.
        """
        # if not SHARED.hasProject:
        #     logger.error("No project open")
        #     return False

        # trashHandle = SHARED.project.tree.trashRoot

        # logger.debug("Emptying Trash folder")
        # if trashHandle is None:
        #     SHARED.info(self.tr("There is currently no Trash folder in this project."))
        #     return False

        # trashItems = self.getTreeFromHandle(trashHandle)
        # if trashHandle in trashItems:
        #     trashItems.remove(trashHandle)

        # nTrash = len(trashItems)
        # if nTrash == 0:
        #     SHARED.info(self.tr("The Trash folder is already empty."))
        #     return False

        # if not SHARED.question(self.trPermDelete.format(nTrash)):
        #     logger.info("Action cancelled by user")
        #     return False

        # logger.debug("Deleting %d file(s) from Trash", nTrash)
        # for tHandle in reversed(self.getTreeFromHandle(trashHandle)):
        #     if tHandle == trashHandle:
        #         continue
        #     self.permDeleteItem(tHandle, askFirst=False, flush=False)

        # if nTrash > 0:
        #     self._alertTreeChange(trashHandle, flush=True)

        return True

    def refreshUserLabels(self, kind: str) -> None:
        """Refresh status or importance labels."""
        # if kind == "s":
        #     for nwItem in SHARED.project.tree:
        #         if nwItem.isNovelLike():
        #             self.setTreeItemValues(nwItem)
        # elif kind == "i":
        #     for nwItem in SHARED.project.tree:
        #         if not nwItem.isNovelLike():
        #             self.setTreeItemValues(nwItem)
        return

    def propagateCount(self, tHandle: str, newCount: int, countChildren: bool = False) -> None:
        """Recursive function setting the word count for a given item,
        and propagating that count upwards in the tree until reaching a
        root item. This function is more efficient than recalculating
        everything each time the word count is updated, but is also
        prone to diverging from the true values if the counts are not
        properly reported to the function.
        """
        # tItem = self._getTreeItem(tHandle)
        # if tItem is None:
        #     return

        # if countChildren:
        #     for i in range(tItem.childCount()):
        #         newCount += int(tItem.child(i).data(self.C_DATA, self.D_WORDS))

        # tItem.setText(self.C_COUNT, f"{newCount:n}")
        # tItem.setData(self.C_DATA, self.D_WORDS, int(newCount))

        # pItem = tItem.parent()
        # if pItem is None:
        #     return

        # pCount = 0
        # pHandle = None
        # for i in range(pItem.childCount()):
        #     pCount += int(pItem.child(i).data(self.C_DATA, self.D_WORDS))
        #     pHandle = pItem.data(self.C_DATA, self.D_HANDLE)

        # if pHandle:
        #     if SHARED.project.tree.checkType(pHandle, nwItemType.FILE):
        #         # A file has an internal word count we need to account
        #         # for, but a folder always has 0 words on its own.
        #         pCount += SHARED.project.index.getCounts(pHandle)[1]

        #     self.propagateCount(pHandle, pCount, countChildren=False)

        return

    def setActiveHandle(self, tHandle: str | None) -> None:
        """Highlight the rows associated with a given handle."""
        # brushOn = self.palette().alternateBase()
        # brushOff = self.palette().base()
        # if (pHandle := self._actHandle) and (item := self._treeMap.get(pHandle)):
        #     for i in range(self.columnCount()):
        #         item.setBackground(i, brushOff)
        # if tHandle and (item := self._treeMap.get(tHandle)):
        #     for i in range(self.columnCount()):
        #         item.setBackground(i, brushOn)
        # self._actHandle = tHandle or None
        return

    def setExpandedFromHandle(self, tHandle: str | None, isExpanded: bool) -> None:
        """Iterate through items below tHandle and change expanded
        status for all child items. If tHandle is None, it affects the
        entire tree.
        """
        # item = self._getTreeItem(tHandle) or self.invisibleRootItem()
        # self._recursiveSetExpanded(item, isExpanded)
        return

    ##
    #  Public Slots
    ##

    @pyqtSlot()
    @pyqtSlot("QPoint")
    def openContextMenu(self, clickPos: QPoint | None = None) -> None:
        """The user right clicked an element in the project tree, so we
        open a context menu in-place.
        """
        # if clickPos is None and (items := self.selectedItems()):
        #     clickPos = self.visualItemRect(items[0]).center()

        # if clickPos is not None:
        #     tItem = None
        #     tHandle = None
        #     hasChild = False
        #     sItem = self.itemAt(clickPos)
        #     sItems = self.selectedItems()
        #     if isinstance(sItem, QTreeWidgetItem):
        #         tHandle = sItem.data(self.C_DATA, self.D_HANDLE)
        #         tItem = SHARED.project.tree[tHandle]
        #         hasChild = sItem.childCount() > 0

        #     if tItem is None or tHandle is None:
        #         logger.debug("No item found")
        #         return

        #     ctxMenu = _TreeContextMenu(self, tItem)
        #     trashHandle = SHARED.project.tree.trashRoot
        #     if trashHandle and tHandle == trashHandle:
        #         ctxMenu.buildTrashMenu()
        #     elif len(sItems) > 1:
        #         handles = [str(x.data(self.C_DATA, self.D_HANDLE)) for x in sItems]
        #         ctxMenu.buildMultiSelectMenu(handles)
        #     else:
        #         ctxMenu.buildSingleSelectMenu(hasChild)

        #     ctxMenu.exec(self.viewport().mapToGlobal(clickPos))
        #     ctxMenu.deleteLater()

        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _doAutoScroll(self) -> None:
        """Scroll one item up or down based on direction value."""
        # if self._scrollDirection == -1:
        #     self.scrollToItem(self.itemAbove(self.itemAt(1, 1)))
        # elif self._scrollDirection == 1:
        #     self.scrollToItem(self.itemBelow(self.itemAt(1, self.height() - 1)))
        # self._scrollDirection = 0
        # self._scrollTimer.stop()
        return

    ##
    #  Internal Functions
    ##

    def _mergeDocuments(self, tHandle: str, newFile: bool) -> bool:
        """Merge an item's child documents into a single document."""
        # logger.info("Request to merge items under handle '%s'", tHandle)
        # itemList = self.getTreeFromHandle(tHandle)

        # tItem = SHARED.project.tree[tHandle]
        # if tItem is None:
        #     return False

        # if tItem.isRootType():
        #     logger.error("Cannot merge root item")
        #     return False

        # if not newFile:
        #     itemList.remove(tHandle)

        # data, status = GuiDocMerge.getData(SHARED.mainGui, tHandle, itemList)
        # if status:
        #     items = data.get("finalItems", [])
        #     if not items:
        #         SHARED.info(self.tr("No documents selected for merging."))
        #         return False

        #     # Save the open document first, in case it's part of merge
        #     SHARED.saveEditor()

        #     # Create merge object, and append docs
        #     docMerger = DocMerger(SHARED.project)
        #     mLabel = self.tr("Merged")

        #     if newFile:
        #         docLabel = f"[{mLabel}] {tItem.itemName}"
        #         mHandle = docMerger.newTargetDoc(tHandle, docLabel)
        #     elif tItem.isFileType():
        #         docMerger.setTargetDoc(tHandle)
        #         mHandle = tHandle
        #     else:
        #         return False

        #     for sHandle in items:
        #         docMerger.appendText(sHandle, True, mLabel)

        #     if not docMerger.writeTargetDoc():
        #         SHARED.error(
        #             self.tr("Could not write document content."),
        #             info=docMerger.getError()
        #         )
        #         return False

        #     SHARED.project.index.reIndexHandle(mHandle)
        #     if newFile:
        #         self.revealNewTreeItem(mHandle, nHandle=tHandle, wordCount=True)

        #     self.projView.openDocumentRequest.emit(mHandle, nwDocMode.EDIT, "", False)
        #     self.projView.setSelectedHandle(mHandle, doScroll=True)

        #     if data.get("moveToTrash", False):
        #         for sHandle in reversed(data.get("finalItems", [])):
        #             trItem = self._getTreeItem(sHandle)
        #             if isinstance(trItem, QTreeWidgetItem) and trItem.childCount() == 0:
        #                 self.moveItemToTrash(sHandle, askFirst=False, flush=False)

        #     self._alertTreeChange(mHandle, flush=True)
        #     self.projView.wordCountsChanged.emit()

        # else:
        #     logger.info("Action cancelled by user")
        #     return False

        return True

    def _splitDocument(self, tHandle: str) -> bool:
        """Split a document into multiple documents."""
        # logger.info("Request to split items with handle '%s'", tHandle)

        # tItem = SHARED.project.tree[tHandle]
        # if tItem is None:
        #     return False

        # if not tItem.isFileType() or tItem.itemParent is None:
        #     logger.error("Only valid document items can be split")
        #     return False

        # data, text, status = GuiDocSplit.getData(SHARED.mainGui, tHandle)
        # if status:
        #     headerList = data.get("headerList", [])
        #     intoFolder = data.get("intoFolder", False)
        #     docHierarchy = data.get("docHierarchy", False)

        #     docSplit = DocSplitter(SHARED.project, tHandle)
        #     if intoFolder:
        #         fHandle = docSplit.newParentFolder(tItem.itemParent, tItem.itemName)
        #         self.revealNewTreeItem(fHandle, nHandle=tHandle)
        #         self._alertTreeChange(fHandle, flush=False)
        #     else:
        #         docSplit.setParentItem(tItem.itemParent)

        #     docSplit.splitDocument(headerList, text)
        #     for writeOk, dHandle, nHandle in docSplit.writeDocuments(docHierarchy):
        #         SHARED.project.index.reIndexHandle(dHandle)
        #         self.revealNewTreeItem(dHandle, nHandle=nHandle, wordCount=True)
        #         self._alertTreeChange(dHandle, flush=False)
        #         if not writeOk:
        #             SHARED.error(
        #                 self.tr("Could not write document content."),
        #                 info=docSplit.getError()
        #             )

        #     if data.get("moveToTrash", False):
        #         self.moveItemToTrash(tHandle, askFirst=False, flush=True)

        #     self.saveTreeOrder()

        # else:
        #     logger.info("Action cancelled by user")
        #     return False

        return True

    def _duplicateFromHandle(self, tHandle: str) -> bool:
        """Duplicate the item hierarchy from a given item."""
        # itemTree = self.getTreeFromHandle(tHandle)
        # nItems = len(itemTree)
        # if nItems == 0:
        #     return False
        # elif nItems == 1:
        #     question = self.tr("Do you want to duplicate this document?")
        # else:
        #     question = self.tr("Do you want to duplicate this item and all child items?")

        # if not SHARED.question(question):
        #     return False

        # docDup = DocDuplicator(SHARED.project)
        # dupCount = 0
        # for dHandle, nHandle in docDup.duplicate(itemTree):
        #     SHARED.project.index.reIndexHandle(dHandle)
        #     self.revealNewTreeItem(dHandle, nHandle=nHandle, wordCount=True)
        #     self._alertTreeChange(dHandle, flush=False)
        #     dupCount += 1

        # if dupCount != nItems:
        #     SHARED.warn(self.tr("Could not duplicate all items."))

        # self.saveTreeOrder()

        return True


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


# class _TreeContextMenu(QMenu):

#     def __init__(self, projTree: GuiProjectTree, nwItem: NWItem) -> None:
#         super().__init__(parent=projTree)

#         self.projTree = projTree
#         self.projView = projTree.projView

#         self._item = nwItem
#         self._handle = nwItem.itemHandle
#         self._items: list[NWItem] = []

#         logger.debug("Ready: _TreeContextMenu")

#         return

#     def __del__(self) -> None:  # pragma: no cover
#         logger.debug("Delete: _TreeContextMenu")
#         return

#     ##
#     #  Methods
#     ##

#     def buildTrashMenu(self) -> None:
#         """Build the special menu for the Trash folder."""
#         action = self.addAction(self.tr("Empty Trash"))
#         action.triggered.connect(self.projTree.emptyTrash)
#         return

#     def buildSingleSelectMenu(self, hasChild: bool) -> None:
#         """Build the single-select menu."""
#         isFile = self._item.isFileType()
#         isFolder = self._item.isFolderType()
#         isRoot = self._item.isRootType()

#         # Document Actions
#         if isFile:
#             self._docActions()
#             self.addSeparator()

#         # Create New Items
#         self._itemCreation()
#         self.addSeparator()

#         # Edit Item Settings
#         action = self.addAction(self.tr("Rename"))
#         action.triggered.connect(qtLambda(self.projView.renameTreeItem, self._handle))
#         if isFile:
#             self._itemHeader()
#             self._itemActive(False)
#         self._itemStatusImport(False)

#         # Transform Item
#         if isFile or isFolder:
#             self._itemTransform(isFile, isFolder, hasChild)
#         self.addSeparator()

#         # Process Item
#         self._itemProcess(isFile, isFolder, isRoot, hasChild)

#         return

#     def buildMultiSelectMenu(self, handles: list[str]) -> None:
#         """Build the multi-select menu."""
#         self._items = []
#         for tHandle in handles:
#             if (tItem := SHARED.project.tree[tHandle]):
#                 self._items.append(tItem)

#         self._itemActive(True)
#         self._itemStatusImport(True)
#         self.addSeparator()
#         self._multiMoveToTrash()
#         return

#     ##
#     #  Menu Builders
#     ##

#     def _docActions(self) -> None:
#         """Add document actions."""
#         action = self.addAction(self.tr("Open Document"))
#         action.triggered.connect(qtLambda(
#             self.projView.openDocumentRequest.emit,
#             self._handle, nwDocMode.EDIT, "", True
#         ))
#         action = self.addAction(self.tr("View Document"))
#         action.triggered.connect(qtLambda(
#             self.projView.openDocumentRequest.emit,
#             self._handle, nwDocMode.VIEW, "", False
#         ))
#         return

#     def _itemCreation(self) -> None:
#         """Add create item actions."""
#         menu = self.addMenu(self.tr("Create New ..."))
#         menu.addAction(self.projView.projBar.aAddEmpty)
#         menu.addAction(self.projView.projBar.aAddChap)
#         menu.addAction(self.projView.projBar.aAddScene)
#         menu.addAction(self.projView.projBar.aAddNote)
#         menu.addAction(self.projView.projBar.aAddFolder)
#         return

#     def _itemHeader(self) -> None:
#         """Check if there is a header that can be used for rename."""
#         SHARED.saveEditor()
#         if hItem := SHARED.project.index.getItemHeading(self._handle, "T0001"):
#             action = self.addAction(self.tr("Rename to Heading"))
#             action.triggered.connect(
#                 qtLambda(self.projView.renameTreeItem, self._handle, hItem.title)
#             )
#         return

#     def _itemActive(self, multi: bool) -> None:
#         """Add Active/Inactive actions."""
#         if multi:
#             mSub = self.addMenu(self.tr("Set Active to ..."))
#             aOne = mSub.addAction(SHARED.theme.getIcon("checked"), self.projTree.trActive)
#             aOne.triggered.connect(qtLambda(self._iterItemActive, True))
#             aTwo = mSub.addAction(SHARED.theme.getIcon("unchecked"), self.projTree.trInactive)
#             aTwo.triggered.connect(qtLambda(self._iterItemActive, False))
#         else:
#             action = self.addAction(self.tr("Toggle Active"))
#             action.triggered.connect(self._toggleItemActive)
#         return

#     def _itemStatusImport(self, multi: bool) -> None:
#         """Add actions for changing status or importance."""
#         if self._item.isNovelLike():
#             menu = self.addMenu(self.tr("Set Status to ..."))
#             current = self._item.itemStatus
#             for key, entry in SHARED.project.data.itemStatus.iterItems():
#                 name = entry.name
#                 if not multi and current == key:
#                     name += f" ({nwUnicode.U_CHECK})"
#                 action = menu.addAction(entry.icon, name)
#                 if multi:
#                     action.triggered.connect(qtLambda(self._iterSetItemStatus, key))
#                 else:
#                     action.triggered.connect(qtLambda(self._changeItemStatus, key))
#             menu.addSeparator()
#             action = menu.addAction(self.tr("Manage Labels ..."))
#             action.triggered.connect(qtLambda(
#                 self.projView.projectSettingsRequest.emit,
#                 GuiProjectSettings.PAGE_STATUS
#             ))
#         else:
#             menu = self.addMenu(self.tr("Set Importance to ..."))
#             current = self._item.itemImport
#             for key, entry in SHARED.project.data.itemImport.iterItems():
#                 name = entry.name
#                 if not multi and current == key:
#                     name += f" ({nwUnicode.U_CHECK})"
#                 action = menu.addAction(entry.icon, name)
#                 if multi:
#                     action.triggered.connect(qtLambda(self._iterSetItemImport, key))
#                 else:
#                     action.triggered.connect(qtLambda(self._changeItemImport, key))
#             menu.addSeparator()
#             action = menu.addAction(self.tr("Manage Labels ..."))
#             action.triggered.connect(qtLambda(
#                 self.projView.projectSettingsRequest.emit,
#                 GuiProjectSettings.PAGE_IMPORT
#             ))
#         return

#     def _itemTransform(self, isFile: bool, isFolder: bool, hasChild: bool) -> None:
#         """Add actions for the Transform menu."""
#         menu = self.addMenu(self.tr("Transform ..."))

#         tree = self.projTree
#         tHandle = self._handle

#         trDoc = trConst(nwLabels.LAYOUT_NAME[nwItemLayout.DOCUMENT])
#         trNote = trConst(nwLabels.LAYOUT_NAME[nwItemLayout.NOTE])
#         loDoc = nwItemLayout.DOCUMENT
#         loNote = nwItemLayout.NOTE
#         isDocFile = isFile and self._item.isDocumentLayout()
#         isNoteFile = isFile and self._item.isNoteLayout()

#         if isNoteFile and self._item.documentAllowed():
#             action = menu.addAction(self.tr("Convert to {0}").format(trDoc))
#             action.triggered.connect(qtLambda(self._changeItemLayout, loDoc))

#         if isDocFile:
#             action = menu.addAction(self.tr("Convert to {0}").format(trNote))
#             action.triggered.connect(qtLambda(self._changeItemLayout, loNote))

#         if isFolder and self._item.documentAllowed():
#             action = menu.addAction(self.tr("Convert to {0}").format(trDoc))
#             action.triggered.connect(qtLambda(self._covertFolderToFile, loDoc))

#         if isFolder:
#             action = menu.addAction(self.tr("Convert to {0}").format(trNote))
#             action.triggered.connect(qtLambda(self._covertFolderToFile, loNote))

#         if hasChild and isFile:
#             action = menu.addAction(self.tr("Merge Child Items into Self"))
#             action.triggered.connect(qtLambda(tree._mergeDocuments, tHandle, False))
#             action = menu.addAction(self.tr("Merge Child Items into New"))
#             action.triggered.connect(qtLambda(tree._mergeDocuments, tHandle, True))

#         if hasChild and isFolder:
#             action = menu.addAction(self.tr("Merge Documents in Folder"))
#             action.triggered.connect(qtLambda(tree._mergeDocuments, tHandle, True))

#         if isFile:
#             action = menu.addAction(self.tr("Split Document by Headings"))
#             action.triggered.connect(qtLambda(tree._splitDocument, tHandle))

#         return

#     def _itemProcess(self, isFile: bool, isFolder: bool, isRoot: bool, hasChild: bool) -> None:
#         """Add actions for item processing."""
#         tree = self.projTree
#         tHandle = self._handle
#         if hasChild:
#             action = self.addAction(self.tr("Expand All"))
#             action.triggered.connect(qtLambda(tree.setExpandedFromHandle, tHandle, True))
#             action = self.addAction(self.tr("Collapse All"))
#             action.triggered.connect(qtLambda(tree.setExpandedFromHandle, tHandle, False))

#         action = self.addAction(self.tr("Duplicate"))
#         action.triggered.connect(qtLambda(tree._duplicateFromHandle, tHandle))

#         if self._item.itemClass == nwItemClass.TRASH or isRoot or (isFolder and not hasChild):
#             action = self.addAction(self.tr("Delete Permanently"))
#             action.triggered.connect(qtLambda(tree.permDeleteItem, tHandle))
#         else:
#             action = self.addAction(self.tr("Move to Trash"))
#             action.triggered.connect(qtLambda(tree.moveItemToTrash, tHandle))

#         return

#     def _multiMoveToTrash(self) -> None:
#         """Add move to Trash action."""
#         areTrash = [i.itemClass == nwItemClass.TRASH for i in self._items]
#         if all(areTrash):
#             action = self.addAction(self.tr("Delete Permanently"))
#             action.triggered.connect(self._iterPermDelete)
#         elif not any(areTrash):
#             action = self.addAction(self.tr("Move to Trash"))
#             action.triggered.connect(self._iterMoveToTrash)
#         return

#     ##
#     #  Private Slots
#     ##

#     @pyqtSlot()
#     def _iterMoveToTrash(self) -> None:
#         """Iterate through files and move them to Trash."""
#         if SHARED.question(self.tr("Move {0} items to Trash?").format(len(self._items))):
#             for tItem in self._items:
#                 if tItem.isFileType() and tItem.itemClass != nwItemClass.TRASH:
#                     self.projTree.moveItemToTrash(tItem.itemHandle, askFirst=False, flush=False)
#                 # self.projTree.saveTreeOrder()
#         return

#     @pyqtSlot()
#     def _iterPermDelete(self) -> None:
#         """Iterate through files and delete them."""
#         if SHARED.question(self.projTree.trPermDelete.format(len(self._items))):
#             for tItem in self._items:
#                 if tItem.isFileType() and tItem.itemClass == nwItemClass.TRASH:
#                     self.projTree.permDeleteItem(tItem.itemHandle, askFirst=False, flush=False)
#                 # self.projTree.saveTreeOrder()
#         return

#     @pyqtSlot()
#     def _toggleItemActive(self) -> None:
#         """Toggle the active status of an item."""
#         self._item.setActive(not self._item.isActive)
#         self.projTree.setTreeItemValues(self._item)
#         self.projTree._alertTreeChange(self._handle, flush=False)
#         return

#     ##
#     #  Internal Functions
#     ##

#     def _iterItemActive(self, isActive: bool) -> None:
#         """Set the active status of multiple items."""
#         for tItem in self._items:
#             if tItem and tItem.isFileType():
#                 tItem.setActive(isActive)
#                 self.projTree.setTreeItemValues(tItem)
#                 self.projTree._alertTreeChange(tItem.itemHandle, flush=False)
#         return

#     def _changeItemStatus(self, key: str) -> None:
#         """Set a new status value of an item."""
#         self._item.setStatus(key)
#         self.projTree.setTreeItemValues(self._item)
#         self.projTree._alertTreeChange(self._handle, flush=False)
#         return

#     def _iterSetItemStatus(self, key: str) -> None:
#         """Change the status value for multiple items."""
#         for tItem in self._items:
#             if tItem and tItem.isNovelLike():
#                 tItem.setStatus(key)
#                 self.projTree.setTreeItemValues(tItem)
#                 self.projTree._alertTreeChange(tItem.itemHandle, flush=False)
#         return

#     def _changeItemImport(self, key: str) -> None:
#         """Set a new importance value of an item."""
#         self._item.setImport(key)
#         self.projTree.setTreeItemValues(self._item)
#         self.projTree._alertTreeChange(self._handle, flush=False)
#         return

#     def _iterSetItemImport(self, key: str) -> None:
#         """Change the status value for multiple items."""
#         for tItem in self._items:
#             if tItem and not tItem.isNovelLike():
#                 tItem.setImport(key)
#                 self.projTree.setTreeItemValues(tItem)
#                 self.projTree._alertTreeChange(tItem.itemHandle, flush=False)
#         return

#     def _changeItemLayout(self, itemLayout: nwItemLayout) -> None:
#         """Set a new item layout value of an item."""
#         if itemLayout == nwItemLayout.DOCUMENT and self._item.documentAllowed():
#             self._item.setLayout(nwItemLayout.DOCUMENT)
#             self.projTree.setTreeItemValues(self._item)
#             self.projTree._alertTreeChange(self._handle, flush=False)
#         elif itemLayout == nwItemLayout.NOTE:
#             self._item.setLayout(nwItemLayout.NOTE)
#             self.projTree.setTreeItemValues(self._item)
#             self.projTree._alertTreeChange(self._handle, flush=False)
#         return

#     def _covertFolderToFile(self, itemLayout: nwItemLayout) -> None:
#         """Convert a folder to a note or document."""
#         if self._item.isFolderType():
#             msgYes = SHARED.question(self.tr(
#                 "Do you want to convert the folder to a {0}? "
#                 "This action cannot be reversed."
#             ).format(trConst(nwLabels.LAYOUT_NAME[itemLayout])))
#             if msgYes and itemLayout == nwItemLayout.DOCUMENT and self._item.documentAllowed():
#                 self._item.setType(nwItemType.FILE)
#                 self._item.setLayout(nwItemLayout.DOCUMENT)
#                 self.projTree.setTreeItemValues(self._item)
#                 self.projTree._alertTreeChange(self._handle, flush=False)
#             elif msgYes and itemLayout == nwItemLayout.NOTE:
#                 self._item.setType(nwItemType.FILE)
#                 self._item.setLayout(nwItemLayout.NOTE)
#                 self.projTree.setTreeItemValues(self._item)
#                 self.projTree._alertTreeChange(self._handle, flush=False)
#             else:
#                 logger.info("Folder conversion cancelled")
#         return
