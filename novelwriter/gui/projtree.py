"""
novelWriter – GUI Project Tree
==============================

File History:
Created:   2018-09-29 [0.0.1]  GuiProjectTree
Created:   2022-06-06 [2.0rc1] GuiProjectView
Created:   2022-06-06 [2.0rc1] GuiProjectToolBar
Created:   2023-11-22 [2.2rc1] _TreeContextMenu
Rewritten: 2024-11-17 [2.6b2]  GuiProjectTree
Rewritten: 2024-11-20 [2.6b2]  _TreeContextMenu

This file is a part of novelWriter
Copyright (C) 2018 Veronica Berglyd Olsen and novelWriter contributors

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
from PyQt5.QtGui import QIcon, QMouseEvent, QPainter, QPalette
from PyQt5.QtWidgets import (
    QAbstractItemView, QAction, QFrame, QHBoxLayout, QLabel, QMenu, QShortcut,
    QStyleOptionViewItem, QTreeView, QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import qtLambda
from novelwriter.constants import nwLabels, nwStyles, nwUnicode, trConst
from novelwriter.core.coretools import DocDuplicator, DocMerger, DocSplitter
from novelwriter.core.item import NWItem
from novelwriter.core.itemmodel import ProjectModel, ProjectNode
from novelwriter.dialogs.docmerge import GuiDocMerge
from novelwriter.dialogs.docsplit import GuiDocSplit
from novelwriter.dialogs.editlabel import GuiEditLabel
from novelwriter.dialogs.projectsettings import GuiProjectSettings
from novelwriter.enum import nwChange, nwDocMode, nwItemClass, nwItemLayout, nwItemType
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

    openDocumentRequest = pyqtSignal(str, Enum, str, bool)
    projectSettingsRequest = pyqtSignal(int)
    selectedItemChanged = pyqtSignal(str)

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
        self.keyGoPrev.activated.connect(self.projTree.goToSiblingUp)

        self.keyGoNext = QShortcut(self.projTree)
        self.keyGoNext.setKey("Alt+Down")
        self.keyGoNext.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.keyGoNext.activated.connect(self.projTree.goToSiblingDown)

        self.keyGoUp = QShortcut(self.projTree)
        self.keyGoUp.setKey("Alt+Left")
        self.keyGoUp.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.keyGoUp.activated.connect(self.projTree.goToParent)

        self.keyGoDown = QShortcut(self.projTree)
        self.keyGoDown.setKey("Alt+Right")
        self.keyGoDown.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.keyGoDown.activated.connect(self.projTree.goToFirstChild)

        self.keyContext = QShortcut(self.projTree)
        self.keyContext.setKey("Ctrl+.")
        self.keyContext.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.keyContext.activated.connect(self.projTree.openContextMenu)

        # Signals
        self.selectedItemChanged.connect(self.projBar.treeSelectionChanged)
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
        self.projTree.loadModel()
        self.projBar.buildTemplatesMenu()
        self.projBar.buildQuickLinksMenu()
        self.projBar.setEnabled(True)
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

    @pyqtSlot(str, Enum)
    def onProjectItemChanged(self, tHandle: str, change: nwChange) -> None:
        """Refresh other content when project item changed."""
        self.projBar.processTemplateDocuments(tHandle)
        return

    @pyqtSlot(str)
    def createFileFromTemplate(self, tHandle: str) -> None:
        """Create a new document from a template."""
        logger.debug("Template selected: '%s'", tHandle)
        self.projTree.newTreeItem(nwItemType.FILE, copyDoc=tHandle)
        return

    @pyqtSlot(str, Enum)
    def updateRootItem(self, tHandle: str, change: nwChange) -> None:
        """Process root item changes."""
        self.projBar.buildQuickLinksMenu()
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
        self.aExpand.triggered.connect(self.projTree.expandAll)

        self.aCollapse = self.mMore.addAction(self.tr("Collapse All"))
        self.aCollapse.triggered.connect(self.projTree.collapseAll)

        self.aEmptyTrash = self.mMore.addAction(self.tr("Empty Trash"))
        self.aEmptyTrash.triggered.connect(self.projTree.emptyTrash)

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

        self.buildTemplatesMenu()
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

    def buildTemplatesMenu(self) -> None:
        """Build the templates menu."""
        for tHandle, _ in SHARED.project.tree.iterRoots(nwItemClass.TEMPLATE):
            for dHandle in SHARED.project.tree.subTree(tHandle):
                self.processTemplateDocuments(dHandle)
        return

    def processTemplateDocuments(self, tHandle: str) -> None:
        """Process change in tree items to update menu content."""
        if item := SHARED.project.tree[tHandle]:
            if item.isTemplateFile() and item.isActive:
                self.mTemplates.addUpdate(tHandle, item.itemName, item.getMainIcon())
            elif tHandle in self.mTemplates:
                self.mTemplates.remove(tHandle)
        return

    ##
    #  Public Slots
    ##

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

    def __init__(self, projView: GuiProjectView) -> None:
        super().__init__(parent=projView)

        logger.debug("Create: GuiProjectTree")

        self.projView = projView

        # Internal Variables
        self._actHandle = None

        # Cached Translations
        self.trActive = trConst(nwLabels.ACTIVE_NAME["checked"])
        self.trInactive = trConst(nwLabels.ACTIVE_NAME["unchecked"])

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

        # Set selection options
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        # Context Menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openContextMenu)

        # Connect signals
        self.clicked.connect(self._onSingleClick)
        self.doubleClicked.connect(self._onDoubleClick)
        self.collapsed.connect(self._onNodeCollapsed)
        self.expanded.connect(self._onNodeExpanded)

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

    def setActiveHandle(self, tHandle: str | None) -> None:
        """Set the handle to be highlighted."""
        self._actHandle = tHandle
        return

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
        self.setModel(SHARED.project.tree.model)

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

            tHandle = SHARED.project.newRoot(itemClass, pos)
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
                    tHandle = SHARED.project.newFolder(newLabel, sHandle, pos)

        # Select the new item automatically
        if tHandle:
            self.setSelectedHandle(tHandle)

        return

    def mergeDocuments(self, tHandle: str, newFile: bool) -> bool:
        """Merge an item's child documents into a single document."""
        logger.info("Request to merge items under handle '%s'", tHandle)

        if not (tItem := SHARED.project.tree[tHandle]):
            return False

        if tItem.isRootType():
            logger.error("Cannot merge root item")
            return False

        itemList = SHARED.project.tree.subTree(tHandle)
        if newFile:
            itemList.insert(0, tHandle)

        data, status = GuiDocMerge.getData(SHARED.mainGui, tHandle, itemList)
        if not status:
            logger.info("Action cancelled by user")
            return False
        if not (items := data.get("finalItems", [])):
            SHARED.info(self.tr("No documents selected for merging."))
            return False

        # Save the open document first, in case it's part of merge
        SHARED.saveEditor()

        # Create merge object, and append docs
        docMerger = DocMerger(SHARED.project)
        mLabel = self.tr("Merged")

        if newFile:
            docMerger.newTargetDoc(tHandle, f"[{mLabel}] {tItem.itemName}")
        elif tItem.isFileType():
            docMerger.setTargetDoc(tHandle)
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

        if data.get("moveToTrash", False):
            self.processDeleteRequest(data.get("finalItems", []), False)

        if mHandle := docMerger.targetHandle:
            self.projView.openDocumentRequest.emit(mHandle, nwDocMode.EDIT, "", False)
            self.projView.setSelectedHandle(mHandle, doScroll=True)

        return True

    def splitDocument(self, tHandle: str) -> bool:
        """Split a document into multiple documents."""
        logger.info("Request to split items with handle '%s'", tHandle)

        if not (tItem := SHARED.project.tree[tHandle]):
            return False

        if not tItem.isFileType() or tItem.itemParent is None:
            logger.error("Only valid document items can be split")
            return False

        data, text, status = GuiDocSplit.getData(SHARED.mainGui, tHandle)
        if not status:
            logger.info("Action cancelled by user")
            return False

        headerList = data.get("headerList", [])
        intoFolder = data.get("intoFolder", False)
        docHierarchy = data.get("docHierarchy", False)

        docSplit = DocSplitter(SHARED.project, tHandle)
        if intoFolder:
            docSplit.newParentFolder(tItem.itemParent, tItem.itemName)
        else:
            docSplit.setParentItem(tItem.itemParent)

        docSplit.splitDocument(headerList, text)
        for writeOk in docSplit.writeDocuments(docHierarchy):
            if not writeOk:
                SHARED.error(
                    self.tr("Could not write document content."),
                    info=docSplit.getError()
                )

        if data.get("moveToTrash", False):
            self.processDeleteRequest([tHandle], False)

        return True

    def duplicateFromHandle(self, tHandle: str) -> None:
        """Duplicate the item hierarchy from a given item."""
        itemTree = [tHandle]
        itemTree.extend(SHARED.project.tree.subTree(tHandle))
        if itemTree:
            if len(itemTree) == 1:
                question = self.tr("Do you want to duplicate this document?")
            else:
                question = self.tr("Do you want to duplicate this item and all child items?")
            if SHARED.question(question):
                docDup = DocDuplicator(SHARED.project)
                dHandles = docDup.duplicate(itemTree)
                if len(dHandles) != len(itemTree):
                    SHARED.warn(self.tr("Could not duplicate all items."))
        self.restoreExpandedState()
        return

    ##
    #  Events and Overloads
    ##

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Overload mousePressEvent to clear selection if clicking the
        mouse in a blank area of the tree view, and to load a document
        for viewing if the user middle-clicked.
        """
        super().mousePressEvent(event)
        if event.button() == QtMouseLeft:
            if not self.indexAt(event.pos()).isValid():
                self._clearSelection()
        elif event.button() == QtMouseMiddle:
            if (node := self._getNode(self.indexAt(event.pos()))) and node.item.isFileType():
                self.projView.openDocumentRequest.emit(
                    node.item.itemHandle, nwDocMode.VIEW, "", False
                )
        return

    def drawRow(self, painter: QPainter, opt: QStyleOptionViewItem, index: QModelIndex) -> None:
        """Draw a box on the active row."""
        if (node := self._getNode(index)) and node.item.itemHandle == self._actHandle:
            painter.fillRect(opt.rect, self.palette().alternateBase())
        super().drawRow(painter, opt, index)
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
    def goToSiblingUp(self) -> None:
        """Skip to the previous sibling."""
        if (node := self._getNode(self.currentIndex())) and (parent := node.parent()):
            if (move := parent.child(node.row() - 1)) and (model := self._getModel()):
                self.setCurrentIndex(model.indexFromNode(move))
        return

    @pyqtSlot()
    def goToSiblingDown(self) -> None:
        """Skip to the next sibling."""
        if (node := self._getNode(self.currentIndex())) and (parent := node.parent()):
            if (move := parent.child(node.row() + 1)) and (model := self._getModel()):
                self.setCurrentIndex(model.indexFromNode(move))
        return

    @pyqtSlot()
    def goToParent(self) -> None:
        """Move to parent item."""
        if (
            (model := self._getModel())
            and (node := model.node(self.currentIndex()))
            and (parent := node.parent())
        ):
            self.setCurrentIndex(model.indexFromNode(parent))
        return

    @pyqtSlot()
    def goToFirstChild(self) -> None:
        """Move to first child item."""
        if (
            (model := self._getModel())
            and (node := model.node(self.currentIndex()))
            and (child := node.child(0))
        ):
            self.setCurrentIndex(model.indexFromNode(child))
        return

    @pyqtSlot(QModelIndex)
    def expandFromIndex(self, index: QModelIndex) -> None:
        """Expand all nodes from index."""
        self.expandRecursively(index)
        return

    @pyqtSlot(QModelIndex)
    def collapseFromIndex(self, index: QModelIndex) -> None:
        """Collapse all nodes from index."""
        if (model := self._getModel()) and (node := model.node(index)):
            for child in node.allChildren():
                self.setExpanded(model.indexFromNode(child), False)
        return

    @pyqtSlot()
    def processDeleteRequest(
        self, handles: list[str] | None = None, askFirst: bool = True
    ) -> None:
        """Move selected items to Trash."""
        if handles and (model := self._getModel()):
            indices = [model.indexFromHandle(handle) for handle in handles]
        else:
            indices = self._selectedRows()

        if indices and (model := self._getModel()):
            if len(indices) == 1 and (node := model.node(indices[0])) and node.item.isRootType():
                if node.childCount() == 0:
                    SHARED.project.removeItem(node.item.itemHandle)
                else:
                    SHARED.error(self.tr("Root folders can only be deleted when they are empty."))
                return

            if model.trashSelection(indices):
                if not SHARED.question(self.tr("Permanently delete selected item(s)?")):
                    logger.info("Action cancelled by user")
                    return
                for index in indices:
                    if node := model.node(index):
                        for child in reversed(node.allChildren()):
                            SHARED.project.removeItem(child.item.itemHandle)
                        SHARED.project.removeItem(node.item.itemHandle)

            elif trashNode := SHARED.project.tree.trash:
                if askFirst and not SHARED.question(self.tr("Move selected item(s) to Trash?")):
                    logger.info("Action cancelled by user")
                    return
                model.multiMove(indices, model.indexFromNode(trashNode))

        return

    @pyqtSlot()
    def emptyTrash(self) -> None:
        """Permanently delete all documents in the Trash folder. This
        function only asks for confirmation once, and calls the regular
        deleteItem function for each document in the Trash folder.
        """
        if trash := SHARED.project.tree.trash:
            if not (nodes := trash.allChildren()):
                SHARED.info(self.tr("The Trash folder is already empty."))
                return
            if not SHARED.question(
                self.tr("Permanently delete {0} file(s) from Trash?").format(len(nodes))
            ):
                logger.info("Action cancelled by user")
                return
            for node in reversed(nodes):
                SHARED.project.removeItem(node.item.itemHandle)
        return

    @pyqtSlot()
    @pyqtSlot("QPoint")
    def openContextMenu(self, point: QPoint | None = None) -> None:
        """The user right clicked an element in the project tree, so we
        open a context menu in-place.
        """
        if model := self._getModel():
            if point is None:
                point = self.visualRect(self.currentIndex()).center()

            if (
                point is not None
                and (node := self._getNode(self.currentIndex()))
                and (indices := self._selectedRows())
            ):
                ctxMenu = _TreeContextMenu(self, model, node, indices)
                if node is SHARED.project.tree.trash:
                    ctxMenu.buildTrashMenu()
                elif len(indices) > 1:
                    ctxMenu.buildMultiSelectMenu()
                else:
                    ctxMenu.buildSingleSelectMenu()

                ctxMenu.exec(self.viewport().mapToGlobal(point))
                ctxMenu.deleteLater()

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
            node.setExpanded(False)
        return

    @pyqtSlot(QModelIndex)
    def _onNodeExpanded(self, index: QModelIndex) -> None:
        """Capture a node expand, and pass it to the model."""
        if node := self._getNode(index):
            node.setExpanded(True)
        return

    ##
    #  Internal Functions
    ##

    def _clearSelection(self) -> None:
        """Clear the currently selected items."""
        self.clearSelection()
        self.selectionModel().clearCurrentIndex()
        return

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

    __slots__ = ("_tree", "_view", "_node", "_item", "_model", "_handle", "_indices", "_children")

    def __init__(
        self, projTree: GuiProjectTree, model: ProjectModel,
        node: ProjectNode, indices: list[QModelIndex]
    ) -> None:
        super().__init__(parent=projTree)
        self._tree = projTree
        self._view = projTree.projView
        self._node = node
        self._item = node.item
        self._model = model
        self._handle = node.item.itemHandle
        self._indices = indices
        self._children = node.childCount() > 0
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
        action.triggered.connect(self._tree.emptyTrash)
        if self._children:
            self._expandCollapse()
        return

    def buildSingleSelectMenu(self) -> None:
        """Build the single-select menu."""
        isFile = self._item.isFileType()
        isFolder = self._item.isFolderType()

        # Document Actions
        if isFile:
            self._docActions()
            self.addSeparator()

        # Create New Items
        self._itemCreation()
        self.addSeparator()

        # Edit Item Settings
        action = self.addAction(self.tr("Rename"))
        action.triggered.connect(qtLambda(self._view.renameTreeItem, self._handle))
        if isFile:
            self._itemHeader()
            self._itemActive()
        self._itemStatusImport(False)

        # Transform Item
        if isFile or isFolder:
            self._itemTransform(isFile, isFolder)
        self.addSeparator()

        # Process Item
        if self._children:
            self._expandCollapse()
        action = self.addAction(self.tr("Duplicate"))
        action.triggered.connect(qtLambda(self._tree.duplicateFromHandle, self._handle))
        self._deleteOrTrash()

        return

    def buildMultiSelectMenu(self) -> None:
        """Build the multi-select menu."""
        self._itemActive()
        self._itemStatusImport(True)
        self.addSeparator()
        self._deleteOrTrash()
        return

    ##
    #  Menu Builders
    ##

    def _docActions(self) -> None:
        """Add document actions."""
        action = self.addAction(self.tr("Open Document"))
        action.triggered.connect(qtLambda(
            self._view.openDocumentRequest.emit,
            self._handle, nwDocMode.EDIT, "", True
        ))
        action = self.addAction(self.tr("View Document"))
        action.triggered.connect(qtLambda(
            self._view.openDocumentRequest.emit,
            self._handle, nwDocMode.VIEW, "", False
        ))
        return

    def _itemCreation(self) -> None:
        """Add create item actions."""
        menu = self.addMenu(self.tr("Create New ..."))
        menu.addAction(self._view.projBar.aAddEmpty)
        menu.addAction(self._view.projBar.aAddChap)
        menu.addAction(self._view.projBar.aAddScene)
        menu.addAction(self._view.projBar.aAddNote)
        menu.addAction(self._view.projBar.aAddFolder)
        return

    def _itemHeader(self) -> None:
        """Check if there is a header that can be used for rename."""
        SHARED.saveEditor()
        if hItem := SHARED.project.index.getItemHeading(self._handle, "T0001"):
            action = self.addAction(self.tr("Rename to Heading"))
            action.triggered.connect(
                qtLambda(self._view.renameTreeItem, self._handle, hItem.title)
            )
        return

    def _itemActive(self) -> None:
        """Add Active/Inactive actions."""
        if len(self._indices) > 1:
            mSub = self.addMenu(self.tr("Set Active to ..."))
            aOne = mSub.addAction(SHARED.theme.getIcon("checked"), self._tree.trActive)
            aOne.triggered.connect(qtLambda(self._iterItemActive, True))
            aTwo = mSub.addAction(SHARED.theme.getIcon("unchecked"), self._tree.trInactive)
            aTwo.triggered.connect(qtLambda(self._iterItemActive, False))
        else:
            action = self.addAction(self.tr("Toggle Active"))
            action.triggered.connect(self._toggleItemActive)
        return

    def _itemStatusImport(self, multi: bool) -> None:
        """Add actions for changing status or importance."""
        if self._item.isNovelLike():
            menu = self.addMenu(self.tr("Set Status to ..."))
            current = self._item.itemStatus
            for key, entry in SHARED.project.data.itemStatus.iterItems():
                name = entry.name
                if not multi and current == key:
                    name += f" ({nwUnicode.U_CHECK})"
                action = menu.addAction(entry.icon, name)
                if multi:
                    action.triggered.connect(qtLambda(self._iterSetItemStatus, key))
                else:
                    action.triggered.connect(qtLambda(self._changeItemStatus, key))
            menu.addSeparator()
            action = menu.addAction(self.tr("Manage Labels ..."))
            action.triggered.connect(qtLambda(
                self._view.projectSettingsRequest.emit,
                GuiProjectSettings.PAGE_STATUS
            ))
        else:
            menu = self.addMenu(self.tr("Set Importance to ..."))
            current = self._item.itemImport
            for key, entry in SHARED.project.data.itemImport.iterItems():
                name = entry.name
                if not multi and current == key:
                    name += f" ({nwUnicode.U_CHECK})"
                action = menu.addAction(entry.icon, name)
                if multi:
                    action.triggered.connect(qtLambda(self._iterSetItemImport, key))
                else:
                    action.triggered.connect(qtLambda(self._changeItemImport, key))
            menu.addSeparator()
            action = menu.addAction(self.tr("Manage Labels ..."))
            action.triggered.connect(qtLambda(
                self._view.projectSettingsRequest.emit,
                GuiProjectSettings.PAGE_IMPORT
            ))
        return

    def _itemTransform(self, isFile: bool, isFolder: bool) -> None:
        """Add actions for the Transform menu."""
        menu = self.addMenu(self.tr("Transform ..."))

        trDoc = trConst(nwLabels.LAYOUT_NAME[nwItemLayout.DOCUMENT])
        trNote = trConst(nwLabels.LAYOUT_NAME[nwItemLayout.NOTE])
        loDoc = nwItemLayout.DOCUMENT
        loNote = nwItemLayout.NOTE
        isDocFile = isFile and self._item.isDocumentLayout()
        isNoteFile = isFile and self._item.isNoteLayout()

        if isNoteFile and self._item.documentAllowed():
            action = menu.addAction(self.tr("Convert to {0}").format(trDoc))
            action.triggered.connect(qtLambda(self._changeItemLayout, loDoc))

        if isDocFile:
            action = menu.addAction(self.tr("Convert to {0}").format(trNote))
            action.triggered.connect(qtLambda(self._changeItemLayout, loNote))

        if isFolder and self._item.documentAllowed():
            action = menu.addAction(self.tr("Convert to {0}").format(trDoc))
            action.triggered.connect(qtLambda(self._convertFolderToFile, loDoc))

        if isFolder:
            action = menu.addAction(self.tr("Convert to {0}").format(trNote))
            action.triggered.connect(qtLambda(self._convertFolderToFile, loNote))

        if self._children and isFile:
            action = menu.addAction(self.tr("Merge Child Items into Self"))
            action.triggered.connect(qtLambda(self._tree.mergeDocuments, self._handle, False))
            action = menu.addAction(self.tr("Merge Child Items into New"))
            action.triggered.connect(qtLambda(self._tree.mergeDocuments, self._handle, True))

        if self._children and isFolder:
            action = menu.addAction(self.tr("Merge Documents in Folder"))
            action.triggered.connect(qtLambda(self._tree.mergeDocuments, self._handle, True))

        if isFile:
            action = menu.addAction(self.tr("Split Document by Headings"))
            action.triggered.connect(qtLambda(self._tree.splitDocument, self._handle))

        return

    def _expandCollapse(self) -> None:
        """Add actions for expand and collapse."""
        action = self.addAction(self.tr("Expand All"))
        action.triggered.connect(qtLambda(self._tree.expandFromIndex, self._indices[0]))
        action = self.addAction(self.tr("Collapse All"))
        action.triggered.connect(qtLambda(self._tree.collapseFromIndex, self._indices[0]))
        return

    def _deleteOrTrash(self) -> None:
        """Add move to Trash action."""
        if (
            self._model.trashSelection(self._indices)
            or len(self._indices) == 1 and self._item.isRootType()
        ):
            text = self.tr("Delete Permanently")
        else:
            text = self.tr("Move to Trash")
        action = self.addAction(text)
        action.triggered.connect(self._tree.processDeleteRequest)
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _toggleItemActive(self) -> None:
        """Toggle the active status of an item."""
        if self._item.isFileType():
            self._item.setActive(not self._item.isActive)
            self._item.notifyToRefresh()
        return

    ##
    #  Internal Functions
    ##

    def _iterItemActive(self, state: bool) -> None:
        """Set the active status of multiple items."""
        refresh = []
        for node in self._model.nodes(self._indices):
            if node.item.isFileType():
                node.item.setActive(state)
                refresh.append(node.item.itemHandle)
        SHARED.project.tree.refreshItems(refresh)
        return

    def _changeItemStatus(self, key: str) -> None:
        """Set a new status value of an item."""
        self._item.setStatus(key)
        self._item.notifyToRefresh()
        return

    def _iterSetItemStatus(self, key: str) -> None:
        """Change the status value for multiple items."""
        refresh = []
        for node in self._model.nodes(self._indices):
            if node.item.isNovelLike():
                node.item.setStatus(key)
                refresh.append(node.item.itemHandle)
        SHARED.project.tree.refreshItems(refresh)
        return

    def _changeItemImport(self, key: str) -> None:
        """Set a new importance value of an item."""
        self._item.setImport(key)
        self._item.notifyToRefresh()
        return

    def _iterSetItemImport(self, key: str) -> None:
        """Change the status value for multiple items."""
        refresh = []
        for node in self._model.nodes(self._indices):
            if not node.item.isNovelLike():
                node.item.setImport(key)
                refresh.append(node.item.itemHandle)
        SHARED.project.tree.refreshItems(refresh)
        return

    def _changeItemLayout(self, itemLayout: nwItemLayout) -> None:
        """Set a new item layout value of an item."""
        if itemLayout == nwItemLayout.DOCUMENT and self._item.documentAllowed():
            self._item.setLayout(nwItemLayout.DOCUMENT)
            self._item.notifyToRefresh()
        elif itemLayout == nwItemLayout.NOTE:
            self._item.setLayout(nwItemLayout.NOTE)
            self._item.notifyToRefresh()
        return

    def _convertFolderToFile(self, itemLayout: nwItemLayout) -> None:
        """Convert a folder to a note or document."""
        if self._item.isFolderType():
            msgYes = SHARED.question(self.tr(
                "Do you want to convert the folder to a {0}? "
                "This action cannot be reversed."
            ).format(trConst(nwLabels.LAYOUT_NAME[itemLayout])))
            if msgYes and itemLayout == nwItemLayout.DOCUMENT and self._item.documentAllowed():
                self._item.setType(nwItemType.FILE)
                self._item.setLayout(nwItemLayout.DOCUMENT)
                self._item.notifyToRefresh()
            elif msgYes and itemLayout == nwItemLayout.NOTE:
                self._item.setType(nwItemType.FILE)
                self._item.setLayout(nwItemLayout.NOTE)
                self._item.notifyToRefresh()
            else:
                logger.info("Folder conversion cancelled")
        return
