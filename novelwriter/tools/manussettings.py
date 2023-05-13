"""
novelWriter – GUI Build Settings
================================
GUI classes for editing Manuscript Build Settings

File History:
Created: 2023-02-13 [2.1b1]

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

import logging
import novelwriter

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt, pyqtSlot
from PyQt5.QtWidgets import (
    QAbstractItemView, QDialog, QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSplitter, QStackedWidget, QToolButton,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
)

from novelwriter.core.buildsettings import BuildSettings, FilterMode
from novelwriter.extensions.switch import NSwitch
from novelwriter.extensions.switchbox import NSwitchBox
from novelwriter.extensions.pagedsidebar import NPagedSideBar

logger = logging.getLogger(__name__)


class GuiBuildSettings(QDialog):

    OPT_FILTERS  = 1
    OPT_HEADINGS = 2
    OPT_FORMAT   = 3
    OPT_CONTENT  = 4
    BLD_HTML     = 5
    BLD_MARKDOWN = 6
    BLD_ODT      = 7

    def __init__(self, mainGui):
        super().__init__(parent=mainGui)

        self.mainConf   = novelwriter.CONFIG
        self.mainGui    = mainGui
        self.mainTheme  = mainGui.mainTheme
        self.theProject = mainGui.theProject

        self._build = None

        self.setWindowTitle(self.tr("Manuscript Build Settings"))
        self.setMinimumWidth(self.mainConf.pxInt(700))
        self.setMinimumHeight(self.mainConf.pxInt(400))

        mPx = self.mainConf.pxInt(150)
        wWin = self.mainConf.pxInt(900)
        hWin = self.mainConf.pxInt(600)

        pOptions = self.theProject.options
        self.resize(
            self.mainConf.pxInt(pOptions.getInt("GuiBuildSettings", "winWidth", wWin)),
            self.mainConf.pxInt(pOptions.getInt("GuiBuildSettings", "winHeight", hWin))
        )

        # Options SideBar
        # ===============

        self.optSideBar = NPagedSideBar(self)
        self.optSideBar.setMinimumWidth(mPx)
        self.optSideBar.setMaximumWidth(mPx)
        self.optSideBar.setLabelColor(self.mainTheme.helpText)

        self.optSideBar.addLabel(self.tr("Options"))
        self.optSideBar.addButton(self.tr("Filters"), self.OPT_FILTERS)
        self.optSideBar.addButton(self.tr("Headings"), self.OPT_HEADINGS)
        self.optSideBar.addButton(self.tr("Format"), self.OPT_FORMAT)
        self.optSideBar.addButton(self.tr("Content"), self.OPT_CONTENT)
        self.optSideBar.addSeparator()

        self.optSideBar.addLabel(self.tr("Build"))
        self.optSideBar.addButton(self.tr("HTML"), self.BLD_HTML)
        self.optSideBar.addButton(self.tr("Markdown"), self.BLD_MARKDOWN)
        self.optSideBar.addButton(self.tr("Open Document"), self.BLD_ODT)

        self.optSideBar.buttonClicked.connect(self._stackPageSelected)

        # Options Area
        # ============

        # Create Tabs
        self.optTabSelect = GuiBuildFilterTab(self)
        self.optTabHeadings = GuiBuildHeadingsTab(self)
        self.optTabFormat = GuiBuildFormatTab(self)
        self.optTabContent = GuiBuildContentTab(self)
        self.buildTabHTML = GuiBuildHTMLTab(self)
        self.buildTabMarkdown = GuiBuildMarkdownTab(self)
        self.buildTabODT = GuiBuildODTTab(self)

        # Add Tabs
        self.toolStack = QStackedWidget(self)
        self.toolStack.addWidget(self.optTabSelect)
        self.toolStack.addWidget(self.optTabHeadings)
        self.toolStack.addWidget(self.optTabFormat)
        self.toolStack.addWidget(self.optTabContent)
        self.toolStack.addWidget(self.buildTabHTML)
        self.toolStack.addWidget(self.buildTabMarkdown)
        self.toolStack.addWidget(self.buildTabODT)

        # Assemble
        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.optSideBar)
        self.outerBox.addWidget(self.toolStack)

        self.setLayout(self.outerBox)

        # Set Default Tab
        self.optSideBar.setSelected(self.OPT_FILTERS)

        return

    def loadContent(self, data):
        """Populate the child widgets.
        """
        if isinstance(self._build, BuildSettings) and self._build.changed:
            logger.error("There are unsaved changes in this GUI")
            return

        self._build = BuildSettings()
        self._build.unpack(data)
        self.optTabSelect.loadContent(self._build)

        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(int)
    def _stackPageSelected(self, pageId):
        """Process a user request to switch page.
        """
        if pageId == self.OPT_FILTERS:
            self.toolStack.setCurrentWidget(self.optTabSelect)
        elif pageId == self.OPT_HEADINGS:
            self.toolStack.setCurrentWidget(self.optTabHeadings)
        elif pageId == self.OPT_FORMAT:
            self.toolStack.setCurrentWidget(self.optTabFormat)
        elif pageId == self.OPT_CONTENT:
            self.toolStack.setCurrentWidget(self.optTabContent)
        elif pageId == self.BLD_HTML:
            self.toolStack.setCurrentWidget(self.buildTabHTML)
        elif pageId == self.BLD_MARKDOWN:
            self.toolStack.setCurrentWidget(self.buildTabMarkdown)
        elif pageId == self.BLD_ODT:
            self.toolStack.setCurrentWidget(self.buildTabODT)
        return

    ##
    #  Events
    ##

    def closeEvent(self, event):
        """Capture the user closing the window so we can save settings.
        """
        self._saveSettings()
        event.accept()
        return

    ##
    #  Internal Functions
    ##

    def _saveSettings(self):
        """Save the various user settings.
        """
        logger.debug("Saving GuiBuildSettings settings")

        winWidth  = self.mainConf.rpxInt(self.width())
        winHeight = self.mainConf.rpxInt(self.height())

        treeWidth, filterWidth = self.optTabSelect.mainSplitSizes()

        pOptions = self.theProject.options
        pOptions.setValue("GuiBuildSettings", "winWidth", winWidth)
        pOptions.setValue("GuiBuildSettings", "winHeight", winHeight)
        pOptions.setValue("GuiBuildSettings", "treeWidth", treeWidth)
        pOptions.setValue("GuiBuildSettings", "filterWidth", filterWidth)
        pOptions.saveSettings()

        return

# END Class GuiBuildSettings


class GuiBuildFilterTab(QWidget):

    C_DATA   = 0
    C_NAME   = 0
    C_ACTIVE = 1
    C_STATUS = 2

    D_HANDLE = Qt.UserRole
    D_FILE   = Qt.UserRole + 1

    F_NONE     = 0
    F_FILTERED = 1
    F_INCLUDED = 2
    F_EXCLUDED = 3

    def __init__(self, buildMain):
        super().__init__(parent=buildMain)

        self.mainConf   = novelwriter.CONFIG
        self.mainGui    = buildMain.mainGui
        self.mainTheme  = buildMain.mainGui.mainTheme
        self.theProject = buildMain.mainGui.theProject

        self._treeMap = {}
        self._build = None

        self._statusFlags = {
            self.F_NONE:     ("", QIcon()),
            self.F_FILTERED: (self.tr("Filtered"), self.mainTheme.getIcon("build_filtered")),
            self.F_INCLUDED: (self.tr("Included"), self.mainTheme.getIcon("build_included")),
            self.F_EXCLUDED: (self.tr("Excluded"), self.mainTheme.getIcon("build_excluded")),
        }

        # Project Tree
        # ============

        # Tree Settings
        iPx = self.mainTheme.baseIconSize
        cMg = self.mainConf.pxInt(6)

        # Tree Widget
        self.optTree = QTreeWidget(self)
        self.optTree.setIconSize(QSize(iPx, iPx))
        self.optTree.setUniformRowHeights(True)
        self.optTree.setAllColumnsShowFocus(True)
        self.optTree.setHeaderHidden(True)
        self.optTree.setIndentation(iPx)
        self.optTree.setColumnCount(3)

        treeHeader = self.optTree.header()
        treeHeader.setStretchLastSection(False)
        treeHeader.setSectionResizeMode(self.C_NAME, QHeaderView.Stretch)
        treeHeader.setSectionResizeMode(self.C_ACTIVE, QHeaderView.Fixed)
        treeHeader.setSectionResizeMode(self.C_STATUS, QHeaderView.Fixed)
        treeHeader.resizeSection(self.C_ACTIVE, iPx + cMg)
        treeHeader.resizeSection(self.C_STATUS, iPx + cMg)

        self.optTree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.optTree.setDragDropMode(QAbstractItemView.NoDragDrop)

        # Filters
        # =======

        self.filteredButton = QPushButton(self)
        self.filteredButton.setText(self._statusFlags[self.F_FILTERED][0])
        self.filteredButton.setIcon(self._statusFlags[self.F_FILTERED][1])
        self.filteredButton.clicked.connect(lambda: self._setSelectedMode(self.F_FILTERED))

        self.includedButton = QPushButton(self)
        self.includedButton.setText(self._statusFlags[self.F_INCLUDED][0])
        self.includedButton.setIcon(self._statusFlags[self.F_INCLUDED][1])
        self.includedButton.clicked.connect(lambda: self._setSelectedMode(self.F_INCLUDED))

        self.excludedButton = QPushButton(self)
        self.excludedButton.setText(self._statusFlags[self.F_EXCLUDED][0])
        self.excludedButton.setIcon(self._statusFlags[self.F_EXCLUDED][1])
        self.excludedButton.clicked.connect(lambda: self._setSelectedMode(self.F_EXCLUDED))

        self.modeBox = QHBoxLayout()
        self.modeBox.addWidget(self.filteredButton)
        self.modeBox.addWidget(self.includedButton)
        self.modeBox.addWidget(self.excludedButton)

        # Filer Options
        self.filterOpt = NSwitchBox(self, iPx)
        self.filterOpt.switchToggled.connect(self._applyFilterSwitch)

        # Assemble
        # ========

        pOptions = self.theProject.options
        wTree = self.mainConf.pxInt(pOptions.getInt("GuiBuildSettings", "treeWidth", 0))
        fTree = self.mainConf.pxInt(pOptions.getInt("GuiBuildSettings", "filterWidth", 0))

        self.selectionBox = QVBoxLayout()
        self.selectionBox.addLayout(self.modeBox)
        self.selectionBox.addWidget(self.filterOpt)
        self.selectionBox.setContentsMargins(0, 0, 0, 0)

        self.selectionWidget = QWidget()
        self.selectionWidget.setLayout(self.selectionBox)

        self.mainSplit = QSplitter()
        self.mainSplit.addWidget(self.optTree)
        self.mainSplit.addWidget(self.selectionWidget)
        if wTree > 0:
            self.mainSplit.setSizes([wTree, fTree])

        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.mainSplit)

        self.setLayout(self.outerBox)

        return

    def loadContent(self, build):
        """Populate the widgets.
        """
        self._build = build
        self._populateTree()
        self._populateFilters()
        return

    def mainSplitSizes(self):
        """Extract the sizes of the main splitter.
        """
        sizes = self.mainSplit.sizes()
        if len(sizes) < 2:
            return 0, 0
        return sizes[0], sizes[1]

    ##
    #  Slots
    ##

    @pyqtSlot(str, bool)
    def _applyFilterSwitch(self, key, state):
        """A filter switch has been toggled, so update the settings.
        """
        if not isinstance(self._build, BuildSettings):
            return
        if key.startswith("doc:"):
            self._build.setValue(key[4:], state)
            self._setTreeItemMode()
        elif key.startswith("root:"):
            self._build.setSkipRoot(key[5:], state)
            self._populateTree()
        return

    ##
    #  Internal Functions
    ##

    def _populateTree(self):
        """Build the tree of project items.
        """
        if not isinstance(self._build, BuildSettings):
            return

        logger.debug("Building project tree")
        self._treeMap = {}
        self.optTree.clear()
        for nwItem in self.theProject.getProjectItems():

            tHandle = nwItem.itemHandle
            pHandle = nwItem.itemParent
            rHandle = nwItem.itemRoot
            isFile = nwItem.isFileType()
            isActive = nwItem.isActive

            if nwItem.isInactiveClass() or not self._build.isRootAllowed(rHandle):
                continue

            hLevel = nwItem.mainHeading
            itemIcon = self.mainTheme.getItemIcon(
                nwItem.itemType, nwItem.itemClass, nwItem.itemLayout, hLevel
            )

            if isFile:
                iconName = "checked" if isActive else "unchecked"
            else:
                iconName = "noncheckable"

            trItem = QTreeWidgetItem()
            trItem.setIcon(self.C_NAME, itemIcon)
            trItem.setText(self.C_NAME, nwItem.itemName)
            trItem.setData(self.C_DATA, self.D_HANDLE, tHandle)
            trItem.setData(self.C_DATA, self.D_FILE, isFile)
            trItem.setIcon(self.C_ACTIVE, self.mainTheme.getIcon(iconName))

            trItem.setTextAlignment(self.C_NAME, Qt.AlignLeft)

            if pHandle is None:
                if nwItem.isRootType():
                    self.optTree.addTopLevelItem(trItem)
                else:
                    logger.debug("Skipping item '%s'", tHandle)
                    continue

            elif pHandle in self._treeMap:
                self._treeMap[pHandle].addChild(trItem)

            else:
                logger.debug("Skipping item '%s'", tHandle)
                continue

            self._treeMap[tHandle] = trItem
            trItem.setExpanded(True)

        self._setTreeItemMode()

        return

    def _populateFilters(self):
        """Populate the filter options switches.
        """
        self.filterOpt.clear()
        if not isinstance(self._build, BuildSettings):
            return

        self.filterOpt.addLabel(self._build.getLabel("filter"))
        self.filterOpt.addItem(
            self.mainTheme.getIcon("proj_scene"),
            self._build.getLabel("filter.includeNovel"),
            "doc:filter.includeNovel",
            default=self._build.getValue("filter.includeNovel") or False
        )
        self.filterOpt.addItem(
            self.mainTheme.getIcon("proj_note"),
            self._build.getLabel("filter.includeNotes"),
            "doc:filter.includeNotes",
            default=self._build.getValue("filter.includeNotes") or False
        )
        self.filterOpt.addItem(
            self.mainTheme.getIcon("unchecked"),
            self._build.getLabel("filter.includeInactive"),
            "doc:filter.includeInactive",
            default=self._build.getValue("filter.includeInactive") or False
        )

        self.filterOpt.addSeparator()

        # Root Classes
        self.filterOpt.addLabel(self.tr("Root Folders"))
        for tHandle, nwItem in self.theProject.tree.iterRoots(None):
            if not nwItem.isInactiveClass():
                itemIcon = self.mainTheme.getItemIcon(
                    nwItem.itemType, nwItem.itemClass, nwItem.itemLayout
                )
                self.filterOpt.addItem(itemIcon, nwItem.itemName, f"root:{tHandle}", default=True)

        return

    def _setSelectedMode(self, mode):
        """Set the mode for the selected items.
        """
        if not isinstance(self._build, BuildSettings):
            return

        for item in self.optTree.selectedItems():
            if not isinstance(item, QTreeWidgetItem):
                continue

            tHandle = item.data(self.C_DATA, self.D_HANDLE)
            isFile = item.data(self.C_DATA, self.D_FILE)
            if isFile:
                if mode == self.F_FILTERED:
                    self._build.setFiltered(tHandle)
                elif mode == self.F_INCLUDED:
                    self._build.setIncluded(tHandle)
                elif mode == self.F_EXCLUDED:
                    self._build.setExcluded(tHandle)

        self._setTreeItemMode()

        return

    def _setTreeItemMode(self):
        """Update the filtered mode icon on all items.
        """
        if not isinstance(self._build, BuildSettings):
            return

        filtered = self._build.buildItemFilter(self.theProject)
        for tHandle, item in self._treeMap.items():
            allow, mode = filtered.get(tHandle, (False, FilterMode.UNKNOWN))
            if mode == FilterMode.INCLUDED:
                item.setIcon(self.C_STATUS, self._statusFlags[self.F_INCLUDED][1])
            elif mode == FilterMode.EXCLUDED:
                item.setIcon(self.C_STATUS, self._statusFlags[self.F_EXCLUDED][1])
            elif mode == FilterMode.FILTERED and allow:
                item.setIcon(self.C_STATUS, self._statusFlags[self.F_FILTERED][1])
            else:
                item.setIcon(self.C_STATUS, self._statusFlags[self.F_NONE][1])
        return

# END Class GuiBuildFilterTab


class GuiBuildHeadingsTab(QWidget):

    def __init__(self, buildMain):
        super().__init__(parent=buildMain)

        self.mainConf   = novelwriter.CONFIG
        self.mainGui    = buildMain.mainGui
        self.mainTheme  = buildMain.mainGui.mainTheme
        self.theProject = buildMain.mainGui.theProject

        iPx = self.mainTheme.baseIconSize
        vSp = self.mainConf.pxInt(12)
        bSp = self.mainConf.pxInt(6)

        # Format Boxes
        # ============
        self.formatBox = QGridLayout()
        self.formatBox.setHorizontalSpacing(vSp)

        # Title Heading
        self.lblTitle = QLabel(BuildSettings.getLabel("headings.fmtTitle"))
        self.fmtTitle = QLineEdit("")
        self.fmtTitle.setEnabled(False)
        self.btnTitle = QToolButton()
        self.btnTitle.setIcon(self.mainTheme.getIcon("edit"))

        wrapTitle = QHBoxLayout()
        wrapTitle.addWidget(self.fmtTitle)
        wrapTitle.addWidget(self.btnTitle)
        wrapTitle.setSpacing(bSp)

        self.formatBox.addWidget(self.lblTitle, 0, 0, Qt.AlignLeft)
        self.formatBox.addLayout(wrapTitle,     0, 1, Qt.AlignLeft)

        # Chapter Heading
        self.lblChapter = QLabel(BuildSettings.getLabel("headings.fmtChapter"))
        self.fmtChapter = QLineEdit("")
        self.fmtChapter.setEnabled(False)
        self.btnChapter = QToolButton()
        self.btnChapter.setIcon(self.mainTheme.getIcon("edit"))

        wrapChapter = QHBoxLayout()
        wrapChapter.addWidget(self.fmtChapter)
        wrapChapter.addWidget(self.btnChapter)
        wrapChapter.setSpacing(bSp)

        self.formatBox.addWidget(self.lblChapter, 1, 0, Qt.AlignLeft)
        self.formatBox.addLayout(wrapChapter,     1, 1, Qt.AlignLeft)

        # Unnumbered Chapter Heading
        self.lblUnChapter = QLabel(BuildSettings.getLabel("headings.fmtUnnumbered"))
        self.fmtUnChapter = QLineEdit("")
        self.fmtUnChapter.setEnabled(False)
        self.btnUnChapter = QToolButton()
        self.btnUnChapter.setIcon(self.mainTheme.getIcon("edit"))

        wrapUnChapter = QHBoxLayout()
        wrapUnChapter.addWidget(self.fmtUnChapter)
        wrapUnChapter.addWidget(self.btnUnChapter)
        wrapUnChapter.setSpacing(bSp)

        self.formatBox.addWidget(self.lblUnChapter, 2, 0, Qt.AlignLeft)
        self.formatBox.addLayout(wrapUnChapter,     2, 1, Qt.AlignLeft)

        # Scene Heading
        self.lblScene = QLabel(BuildSettings.getLabel("headings.fmtScene"))
        self.fmtScene = QLineEdit("")
        self.fmtScene.setEnabled(False)
        self.btnScene = QToolButton()
        self.btnScene.setIcon(self.mainTheme.getIcon("edit"))
        self.swtScene = NSwitch(width=2*iPx, height=iPx)

        wrapScene = QHBoxLayout()
        wrapScene.addWidget(self.fmtScene)
        wrapScene.addWidget(self.btnScene)
        wrapScene.setSpacing(bSp)

        wrapSceneHide = QHBoxLayout()
        wrapSceneHide.addWidget(QLabel(self.tr("Hide")))
        wrapSceneHide.addWidget(self.swtScene)
        wrapSceneHide.setSpacing(bSp)

        self.formatBox.addWidget(self.lblScene, 3, 0, Qt.AlignLeft)
        self.formatBox.addLayout(wrapScene,     3, 1, Qt.AlignLeft)
        self.formatBox.addLayout(wrapSceneHide, 3, 2, Qt.AlignLeft)

        # Section Heading
        self.lblSection = QLabel(BuildSettings.getLabel("headings.fmtSection"))
        self.fmtSection = QLineEdit("")
        self.fmtSection.setEnabled(False)
        self.btnSection = QToolButton()
        self.btnSection.setIcon(self.mainTheme.getIcon("edit"))
        self.swtSection = NSwitch(width=2*iPx, height=iPx)

        wrapSection = QHBoxLayout()
        wrapSection.addWidget(self.fmtSection)
        wrapSection.addWidget(self.btnSection)
        wrapSection.setSpacing(bSp)

        wrapSectionHide = QHBoxLayout()
        wrapSectionHide.addWidget(QLabel(self.tr("Hide")))
        wrapSectionHide.addWidget(self.swtSection)
        wrapSectionHide.setSpacing(bSp)

        self.formatBox.addWidget(self.lblSection, 4, 0, Qt.AlignLeft)
        self.formatBox.addLayout(wrapSection,     4, 1, Qt.AlignLeft)
        self.formatBox.addLayout(wrapSectionHide, 4, 2, Qt.AlignLeft)

        # Assemble
        # ========

        self.outerBox = QVBoxLayout()
        self.outerBox.addLayout(self.formatBox)
        self.outerBox.addStretch(1)

        self.setLayout(self.outerBox)

        return

# END Class GuiBuildHeadingsTab


class GuiBuildFormatTab(QWidget):

    def __init__(self, buildMain):
        super().__init__(parent=buildMain)

        return

# END Class GuiBuildFormatTab


class GuiBuildContentTab(QWidget):

    def __init__(self, buildMain):
        super().__init__(parent=buildMain)

        return

# END Class GuiBuildContentTab


class GuiBuildHTMLTab(QWidget):

    def __init__(self, buildMain):
        super().__init__(parent=buildMain)

        return

# END Class GuiBuildHTMLTab


class GuiBuildMarkdownTab(QWidget):

    def __init__(self, buildMain):
        super().__init__(parent=buildMain)

        return

# END Class GuiBuildMarkdownTab


class GuiBuildODTTab(QWidget):

    def __init__(self, buildMain):
        super().__init__(parent=buildMain)

        return

# END Class GuiBuildODTTab
