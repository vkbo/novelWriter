"""
novelWriter – GUI Manuscript Tool
=================================

File History:
Created: 2023-05-13 [2.1b1] GuiManuscript

This file is a part of novelWriter
Copyright (C) 2023 Veronica Berglyd Olsen and novelWriter contributors

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
"""  # noqa
from __future__ import annotations

import logging

from time import time
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, QTimer, QUrl, pyqtSignal, pyqtSlot
from PyQt6.QtGui import (
    QCloseEvent, QColor, QCursor, QDesktopServices, QFont, QPageLayout,
    QPalette, QResizeEvent, QTextDocument
)
from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PyQt6.QtWidgets import (
    QAbstractItemView, QApplication, QFormLayout, QGridLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QSplitter, QStackedWidget,
    QTabWidget, QTextBrowser, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import fuzzyTime, qtLambda
from novelwriter.constants import nwHeadFmt, nwLabels, nwStats, nwUnicode, trStats
from novelwriter.core.buildsettings import BuildCollection, BuildSettings
from novelwriter.core.docbuild import NWBuildDocument
from novelwriter.enum import nwStandardButton
from novelwriter.extensions.modified import NIconToggleButton, NIconToolButton, NToolDialog
from novelwriter.extensions.progressbars import NProgressCircle
from novelwriter.extensions.switch import NSwitch
from novelwriter.formats.tokenizer import HeadingFormatter
from novelwriter.formats.toqdoc import ToQTextDocument
from novelwriter.gui.theme import STYLES_FLAT_TABS, STYLES_MIN_TOOLBUTTON
from novelwriter.tools.manusbuild import GuiManuscriptBuild
from novelwriter.tools.manussettings import GuiBuildSettings
from novelwriter.types import (
    QtAlignCenter, QtAlignRight, QtAlignTop, QtSizeExpanding, QtSizeIgnored,
    QtUserRole
)

if TYPE_CHECKING:
    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


class GuiManuscript(NToolDialog):
    """GUI Tools: Manuscript Tool.

    The dialog displays all the users build definitions, a preview panel
    for the manuscript, and can trigger the actual build dialog to build
    a document directly to disk.
    """

    D_KEY = QtUserRole

    def __init__(self, parent: GuiMain) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiManuscript")
        self.setObjectName("GuiManuscript")

        self._builds = BuildCollection(SHARED.project)
        self._buildMap: dict[str, QListWidgetItem] = {}

        self.setWindowTitle(self.tr("Build Manuscript"))
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        iPx = SHARED.theme.baseIconHeight
        iSz = SHARED.theme.baseIconSize

        options = SHARED.project.options
        self.resize(
            options.getInt("GuiManuscript", "winWidth", 900),
            options.getInt("GuiManuscript", "winHeight", 600),
        )

        # Build Controls
        # ==============

        self.tbAdd = NIconToolButton(self, iSz)
        self.tbAdd.setToolTip(self.tr("Add New Build"))
        self.tbAdd.clicked.connect(self._createNewBuild)

        self.tbDel = NIconToolButton(self, iSz)
        self.tbDel.setToolTip(self.tr("Delete Selected Build"))
        self.tbDel.clicked.connect(self._deleteSelectedBuild)

        self.tbCopy = NIconToolButton(self, iSz)
        self.tbCopy.setToolTip(self.tr("Duplicate Selected Build"))
        self.tbCopy.clicked.connect(self._copySelectedBuild)

        self.tbEdit = NIconToolButton(self, iSz)
        self.tbEdit.setToolTip(self.tr("Edit Selected Build"))
        self.tbEdit.clicked.connect(self._editSelectedBuild)

        self.lblBuilds = QLabel("<b>{0}</b>".format(self.tr("Builds")), self)

        self.listToolBox = QHBoxLayout()
        self.listToolBox.addWidget(self.lblBuilds)
        self.listToolBox.addStretch(1)
        self.listToolBox.addWidget(self.tbAdd)
        self.listToolBox.addWidget(self.tbDel)
        self.listToolBox.addWidget(self.tbCopy)
        self.listToolBox.addWidget(self.tbEdit)
        self.listToolBox.setSpacing(0)

        # Builds
        # ======

        self.buildList = QListWidget(self)
        self.buildList.setIconSize(iSz)
        self.buildList.doubleClicked.connect(self._editSelectedBuild)
        self.buildList.currentItemChanged.connect(self._updateBuildDetails)
        self.buildList.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.buildList.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

        # Details Tabs
        # ============

        self.buildDetails = _DetailsWidget(self)
        self.buildDetails.setColumnWidth(options.getInt("GuiManuscript", "detailsWidth", 100))

        self.buildOutline = _OutlineWidget(self)

        self.detailsTabs = QTabWidget(self)
        self.detailsTabs.addTab(self.buildDetails, self.tr("Details"))
        self.detailsTabs.addTab(self.buildOutline, self.tr("Outline"))

        self.buildSplit = QSplitter(Qt.Orientation.Vertical, self)
        self.buildSplit.addWidget(self.buildList)
        self.buildSplit.addWidget(self.detailsTabs)
        self.buildSplit.setSizes([
            options.getInt("GuiManuscript", "listHeight", 50),
            options.getInt("GuiManuscript", "detailsHeight", 50),
        ])

        # Process Controls
        # ================

        self.btnPreview = SHARED.theme.getStandardButton(nwStandardButton.PREVIEW, self)
        self.btnPreview.clicked.connect(self._generatePreview)

        self.btnPrint = SHARED.theme.getStandardButton(nwStandardButton.PRINT, self)
        self.btnPrint.clicked.connect(self._printDocument)

        self.btnBuild = SHARED.theme.getStandardButton(nwStandardButton.BUILD, self)
        self.btnBuild.clicked.connect(self._buildManuscript)

        self.btnClose = SHARED.theme.getStandardButton(nwStandardButton.CLOSE, self)
        self.btnClose.clicked.connect(qtLambda(self.close))

        self.processBox = QGridLayout()
        self.processBox.addWidget(self.btnPreview, 0, 0)
        self.processBox.addWidget(self.btnPrint,   0, 1)
        self.processBox.addWidget(self.btnBuild,   1, 0)
        self.processBox.addWidget(self.btnClose,   1, 1)

        # Preview Options
        # ===============

        self.swtNewPage = NSwitch(self, height=iPx)
        self.swtNewPage.setChecked(options.getBool("GuiManuscript", "showNewPage", True))
        self.swtNewPage.clicked.connect(self._generatePreview)

        self.lblNewPage = QLabel(self.tr("Show Page Breaks"), self)
        self.lblNewPage.setBuddy(self.swtNewPage)

        # Assemble GUI
        # ============

        self.docPreview = _PreviewWidget(self)
        self.docStats = _StatsWidget(self)

        self.docBar = QHBoxLayout()
        self.docBar.addWidget(self.docStats, 1, QtAlignTop)
        self.docBar.addWidget(self.lblNewPage, 0, QtAlignTop)
        self.docBar.addWidget(self.swtNewPage, 0, QtAlignTop)
        self.docBar.setContentsMargins(0, 0, 0, 0)

        self.docBox = QVBoxLayout()
        self.docBox.addWidget(self.docPreview, 1)
        self.docBox.addLayout(self.docBar, 0)
        self.docBox.setContentsMargins(0, 0, 0, 0)

        self.docWdiget = QWidget(self)
        self.docWdiget.setLayout(self.docBox)

        self.controlBox = QVBoxLayout()
        self.controlBox.addLayout(self.listToolBox, 0)
        self.controlBox.addWidget(self.buildSplit, 1)
        self.controlBox.addLayout(self.processBox, 0)
        self.controlBox.setContentsMargins(0, 0, 0, 0)

        self.optsWidget = QWidget(self)
        self.optsWidget.setLayout(self.controlBox)

        self.mainSplit = QSplitter(self)
        self.mainSplit.addWidget(self.optsWidget)
        self.mainSplit.addWidget(self.docWdiget)
        self.mainSplit.setCollapsible(0, False)
        self.mainSplit.setCollapsible(1, False)
        self.mainSplit.setStretchFactor(0, 0)
        self.mainSplit.setStretchFactor(1, 1)
        self.mainSplit.setSizes([
            options.getInt("GuiManuscript", "optsWidth", 225),
            options.getInt("GuiManuscript", "viewWidth", 675),
        ])

        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.mainSplit)

        self.setLayout(self.outerBox)
        self.setSizeGripEnabled(True)

        self.updateTheme(init=True)

        # Signals
        self.buildOutline.outlineEntryClicked.connect(self.docPreview.navigateTo)

        logger.debug("Ready: GuiManuscript")

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiManuscript")

    def loadContent(self) -> None:
        """Load dialog content from project data."""
        if len(self._builds) == 0:
            build = BuildSettings()
            build.setName(self.tr("My Manuscript"))
            self._builds.setBuild(build)
            selected = build.buildID
        else:
            selected = self._builds.lastBuild

        self._updateBuildsList()
        if selected in self._buildMap:
            self.buildList.setCurrentItem(self._buildMap[selected])
            QTimer.singleShot(200, self._generatePreview)

    def updateTheme(self, *, init: bool = False) -> None:
        """Update theme elements."""
        logger.debug("Theme Update: GuiManuscript, init=%s", init)

        if not init:
            self.btnPreview.updateIcon()
            self.btnPrint.updateIcon()
            self.btnBuild.updateIcon()
            self.btnClose.updateIcon()

        self.tbAdd.setThemeIcon("add", "add")
        self.tbDel.setThemeIcon("remove", "remove")
        self.tbCopy.setThemeIcon("copy", "action")
        self.tbEdit.setThemeIcon("edit", "change")

        buttonStyle = SHARED.theme.getStyleSheet(STYLES_MIN_TOOLBUTTON)
        self.tbAdd.setStyleSheet(buttonStyle)
        self.tbDel.setStyleSheet(buttonStyle)
        self.tbCopy.setStyleSheet(buttonStyle)
        self.tbEdit.setStyleSheet(buttonStyle)

        self.detailsTabs.setStyleSheet(SHARED.theme.getStyleSheet(STYLES_FLAT_TABS))

        self.buildDetails.updateTheme()
        self.buildOutline.updateTheme()
        self.docPreview.updateTheme()

        for obj in SHARED.mainGui.children():
            if isinstance(obj, GuiBuildSettings):
                obj.updateTheme()

    ##
    #  Events
    ##

    def closeEvent(self, event: QCloseEvent) -> None:
        """Capture the user closing the window so we can save GUI
        settings. We also check that we don't have a build settings
        dialog open.
        """
        self._saveSettings()
        for obj in SHARED.mainGui.children():
            # Make sure we don't have any settings windows open
            if isinstance(obj, GuiBuildSettings) and obj.isVisible():
                obj.close()
        event.accept()
        self.softDelete()

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _createNewBuild(self) -> None:
        """Open the build settings dialog for a new build."""
        build = BuildSettings()
        build.setName(self.tr("My Manuscript"))
        self._openSettingsDialog(build)

    @pyqtSlot()
    def _editSelectedBuild(self) -> None:
        """Edit the currently selected build settings entry."""
        if build := self._getSelectedBuild():
            self._openSettingsDialog(build)

    @pyqtSlot()
    def _copySelectedBuild(self) -> None:
        """Copy the currently selected build settings entry."""
        if build := self._getSelectedBuild():
            new = BuildSettings.duplicate(build)
            self._builds.setBuild(new)
            self._updateBuildsList()
            if item := self._buildMap.get(new.buildID):
                item.setSelected(True)

    @pyqtSlot("QListWidgetItem*", "QListWidgetItem*")
    def _updateBuildDetails(self, current: QListWidgetItem, previous: QListWidgetItem) -> None:
        """Process change of build selection to update the details."""
        if current and (build := self._builds.getBuild(current.data(self.D_KEY))):
            self.buildDetails.updateInfo(build)

    @pyqtSlot()
    def _deleteSelectedBuild(self) -> None:
        """Delete the currently selected build settings entry."""
        if build := self._getSelectedBuild():
            if SHARED.question(self.tr("Delete build '{0}'?").format(build.name)):
                if dialog := self._findSettingsDialog(build.buildID):
                    dialog.close()
                self._builds.removeBuild(build.buildID)
                self._updateBuildsList()

    @pyqtSlot(BuildSettings, bool)
    def _processNewSettings(self, build: BuildSettings, refreshPreview: bool) -> None:
        """Process new build settings from the settings dialog."""
        self._builds.setBuild(build)
        self._updateBuildItem(build)
        if refreshPreview:
            self.buildList.setCurrentItem(self._buildMap[build.buildID])
            self._generatePreview()
        elif (item := self.buildList.currentItem()) and item.data(self.D_KEY) == build.buildID:
            self._updateBuildDetails(item, item)

    @pyqtSlot()
    def _generatePreview(self) -> None:
        """Run the document builder on the current build settings for
        the preview widget.
        """
        if not (build := self._getSelectedBuild()):
            return

        start = time()
        showNewPage = self.swtNewPage.isChecked()

        # Make sure editor content is saved before we start
        SHARED.saveEditor()

        docBuild = NWBuildDocument(SHARED.project, build)
        docBuild.queueAll()

        self.docPreview.beginNewBuild(len(docBuild))
        for step, _ in docBuild.iterBuildPreview(showNewPage):
            self.docPreview.buildStep(step + 1)
            QApplication.processEvents()

        buildObj = docBuild.lastBuild
        assert isinstance(buildObj, ToQTextDocument)

        font = QFont()
        font.fromString(build.getStr("format.textFont"))

        self.docPreview.setTextFont(font)
        self.docPreview.setContent(buildObj.document)
        self.docPreview.setBuildName(build.name)

        self.docStats.updateStats(buildObj.textStats)
        self.buildOutline.updateOutline(buildObj.textOutline)

        logger.debug("Build completed in %.3f ms", 1000*(time()-start))

        return

    @pyqtSlot()
    def _buildManuscript(self) -> None:
        """Open the build dialog and build the manuscript."""
        if build := self._getSelectedBuild():
            dialog = GuiManuscriptBuild(self, build)
            dialog.exec()

            # After the build is done, save build settings changes
            if build.changed:
                self._builds.setBuild(build)

    @pyqtSlot()
    def _printDocument(self) -> None:
        """Open the print preview dialog."""
        preview = QPrintPreviewDialog(self)
        preview.paintRequested.connect(self.docPreview.printPreview)
        preview.exec()

    ##
    #  Internal Functions
    ##

    def _getSelectedBuild(self) -> BuildSettings | None:
        """Get the currently selected build. If none are selected,
        automatically select the first one.
        """
        items = self.buildList.selectedItems()
        item = items[0] if items else self.buildList.item(0)
        if item:
            build = self._builds.getBuild(item.data(self.D_KEY))
            if isinstance(build, BuildSettings):
                return build
        return None

    def _saveSettings(self) -> None:
        """Save the user GUI settings."""
        buildOrder = [
            item.data(self.D_KEY) for i in range(self.buildList.count())
            if (item := self.buildList.item(i))
        ]

        current = self.buildList.currentItem()
        lastBuild = current.data(self.D_KEY) if isinstance(current, QListWidgetItem) else ""

        self._builds.setBuildsState(lastBuild, buildOrder)

        mainSplit = self.mainSplit.sizes()
        buildSplit = self.buildSplit.sizes()
        detailsWidth = self.buildDetails.getColumnWidth()
        detailsExpanded = self.buildDetails.getExpandedState()
        showNewPage = self.swtNewPage.isChecked()

        logger.debug("Saving State: GuiManuscript")
        pOptions = SHARED.project.options
        pOptions.setValue("GuiManuscript", "winWidth", self.width())
        pOptions.setValue("GuiManuscript", "winHeight", self.height())
        pOptions.setValue("GuiManuscript", "optsWidth", mainSplit[0])
        pOptions.setValue("GuiManuscript", "viewWidth", mainSplit[1])
        pOptions.setValue("GuiManuscript", "listHeight", buildSplit[0])
        pOptions.setValue("GuiManuscript", "detailsHeight", buildSplit[1])
        pOptions.setValue("GuiManuscript", "detailsWidth", detailsWidth)
        pOptions.setValue("GuiManuscript", "detailsExpanded", detailsExpanded)
        pOptions.setValue("GuiManuscript", "showNewPage", showNewPage)
        pOptions.saveSettings()

    def _openSettingsDialog(self, build: BuildSettings) -> None:
        """Open the build settings dialog."""
        if dialog := self._findSettingsDialog(build.buildID):
            dialog.activateDialog()
            return

        dialog = GuiBuildSettings(SHARED.mainGui, build)
        dialog.activateDialog()
        dialog.loadContent()
        dialog.newSettingsReady.connect(self._processNewSettings)

        return

    def _updateBuildsList(self) -> None:
        """Update the list of available builds."""
        self.buildList.clear()
        self._buildMap.clear()
        for key, name in self._builds.builds():
            bItem = QListWidgetItem()
            bItem.setText(name)
            bItem.setIcon(SHARED.theme.getIcon("build_settings", "action"))
            bItem.setData(self.D_KEY, key)
            self.buildList.addItem(bItem)
            self._buildMap[key] = bItem

    def _updateBuildItem(self, build: BuildSettings) -> None:
        """Update the entry of a specific build item."""
        if item := self._buildMap.get(build.buildID):
            item.setText(build.name)
        else:  # Probably a new item
            self._updateBuildsList()

    def _findSettingsDialog(self, buildID: str) -> GuiBuildSettings | None:
        """Return an open build settings dialog for a given build, if
        one exists.
        """
        for obj in SHARED.mainGui.children():
            if isinstance(obj, GuiBuildSettings) and obj.buildID == buildID:
                return obj
        return None


class _DetailsWidget(QWidget):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        self._initExpanded = True
        self._build = None

        # Tree Widget
        self.listView = QTreeWidget(self)
        self.listView.setHeaderLabels([self.tr("Setting"), self.tr("Value")])
        self.listView.setIndentation(SHARED.theme.baseIconHeight)
        self.listView.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.listView)
        self.outerBox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.outerBox)

    ##
    #  Getters
    ##

    def getColumnWidth(self) -> int:
        """Get the width of the first column."""
        return self.listView.columnWidth(0)

    def getExpandedState(self) -> list[bool]:
        """Get the expanded state of each top level item."""
        state = []
        for i in range(self.listView.topLevelItemCount()):
            item = self.listView.topLevelItem(i)
            if isinstance(item, QTreeWidgetItem):
                state.append(item.isExpanded())
        return state

    ##
    #  Setters
    ##

    def setColumnWidth(self, value: int) -> None:
        """Set the width of the first column."""
        self.listView.setColumnWidth(0, value)

    def setExpandedState(self, state: list[bool]) -> None:
        """Set the expanded state of each top level item."""
        count = len(state)
        for i in range(self.listView.topLevelItemCount()):
            item = self.listView.topLevelItem(i)
            if isinstance(item, QTreeWidgetItem):
                item.setExpanded((state[i] if i < count else True) and item.childCount() > 0)

    ##
    #  Methods
    ##

    def updateInfo(self, build: BuildSettings) -> None:
        """Load the build settings info into the table."""
        if self._initExpanded:
            previous = SHARED.project.options.getValue("GuiManuscript", "detailsExpanded", [])
            expanded = [bool(s) for s in previous]
            self._initExpanded = False
        else:
            expanded = self.getExpandedState()

        self.listView.clear()

        on = SHARED.theme.getIcon("bullet-on", "action")
        off = SHARED.theme.getIcon("bullet-off", "action")

        # Name
        item = QTreeWidgetItem()
        item.setText(0, self.tr("Name"))
        item.setText(1, build.name)
        self.listView.addTopLevelItem(item)

        # Selection
        item = QTreeWidgetItem()
        item.setText(0, self.tr("Selection"))
        item.setText(1, "")
        self.listView.addTopLevelItem(item)
        for tHandle, nwItem in SHARED.project.tree.iterRoots(None):
            if not nwItem.isInactiveClass():
                sub = QTreeWidgetItem()
                sub.setText(0, nwItem.itemName)
                sub.setIcon(1, on if build.isRootAllowed(tHandle) else off)
                item.addChild(sub)

        # Headings
        hFmt = HeadingFormatter(SHARED.project, 7, 5, 23)
        title = self.tr("Title")
        hidden = self.tr("Hidden")

        item = QTreeWidgetItem()
        item.setText(0, build.getLabel("headings"))
        item.setText(1, "")
        self.listView.addTopLevelItem(item)
        for hFormat, hHide in [
            ("headings.fmtPart", "headings.hidePart"),
            ("headings.fmtChapter", "headings.hideChapter"),
            ("headings.fmtUnnumbered", "headings.hideUnnumbered"),
            ("headings.fmtScene", "headings.hideScene"),
            ("headings.fmtAltScene", "headings.hideAltScene"),
            ("headings.fmtSection", "headings.hideSection"),
        ]:
            sub = QTreeWidgetItem()
            sub.setText(0, build.getLabel(hFormat))
            if build.getBool(hHide):
                sub.setText(1, f"[{hidden}]")
            else:
                preview = build.getStr(hFormat).replace(nwHeadFmt.BR, nwUnicode.U_LBREAK)
                sub.setText(1, hFmt.apply(preview, title, 0))
            item.addChild(sub)

        # Text Content
        item = QTreeWidgetItem()
        item.setText(0, build.getLabel("text.grpContent"))
        item.setText(1, "")
        self.listView.addTopLevelItem(item)
        for key in [
            "text.includeSynopsis", "text.includeComments", "text.includeStory",
            "text.includeNotes", "text.includeKeywords", "text.includeBodyText",
        ]:
            sub = QTreeWidgetItem()
            sub.setText(0, build.getLabel(key))
            sub.setIcon(1, on if build.getBool(key) else off)
            item.addChild(sub)

        self._build = build

        # Restore expanded state
        self.setExpandedState(expanded)

    def updateTheme(self) -> None:
        """Update theme elements."""
        if self._build:
            logger.debug("Theme Update: _DetailsWidget")
            self.updateInfo(self._build)


class _OutlineWidget(QWidget):

    D_LINE = QtUserRole

    outlineEntryClicked = pyqtSignal(str)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        self._outline = {}

        # Tree Widget
        self.listView = QTreeWidget(self)
        self.listView.setHeaderHidden(True)
        self.listView.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.listView.itemClicked.connect(self._onItemClick)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.listView)
        self.outerBox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.outerBox)

    def updateOutline(self, data: dict[str, str], *, force: bool = False) -> None:
        """Update the outline."""
        if isinstance(data, dict) and (data != self._outline or force):
            self.listView.clear()

            tFont = self.font()
            tFont.setBold(True)
            tBrush = self.palette().highlight()

            hFont = self.font()
            hFont.setBold(True)
            hFont.setUnderline(True)

            indent = False
            if root := self.listView.invisibleRootItem():
                parent = root
                for anchor, entry in data.items():
                    prefix, _, text = entry.partition("|")
                    if prefix in ("TT", "PT", "CH", "SC", "H1", "H2"):
                        item = QTreeWidgetItem([text])
                        item.setData(0, self.D_LINE, anchor)
                        if prefix == "TT":
                            item.setFont(0, tFont)
                            item.setForeground(0, tBrush)
                            root.addChild(item)
                            parent = root
                        elif prefix == "PT":
                            item.setFont(0, hFont)
                            root.addChild(item)
                            parent = root
                        elif prefix in ("CH", "H1"):
                            root.addChild(item)
                            parent = item
                        elif prefix in ("SC", "H2"):
                            parent.addChild(item)
                            indent = True

            self.listView.setIndentation(SHARED.theme.baseIconHeight if indent else 4)
            self._outline = data

    def updateTheme(self) -> None:
        """Update theme elements."""
        logger.debug("Theme Update: _OutlineWidget")
        self.updateOutline(self._outline, force=True)

    ##
    #  Private Slots
    ##

    def _onItemClick(self, item: QTreeWidgetItem) -> None:
        """Process tree item click."""
        self.outlineEntryClicked.emit(str(item.data(0, self.D_LINE)))


class _PreviewWidget(QTextBrowser):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        self._docTime = 0
        self._buildName = ""
        self._scrollPos = 0

        # Document Setup
        dPalette = self.palette()
        dPalette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        dPalette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        self.setPalette(dPalette)

        self.setMinimumWidth(40*SHARED.theme.textNWidth)
        self.setTabStopDistance(CONFIG.tabWidth)
        self.setOpenExternalLinks(False)
        self.setOpenLinks(False)

        if document := self.document():
            document.setDocumentMargin(CONFIG.textMargin)

        self.setPlaceholderText(self.tr(
            'Press the "Preview" button to generate ...'
        ))

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        # Signals
        self.anchorClicked.connect(self._linkClicked)

        # Document Age
        aFont = self.font()
        aFont.setPointSizeF(0.9*SHARED.theme.fontPointSize)

        self.ageLabel = QLabel("", self)
        self.ageLabel.setIndent(0)
        self.ageLabel.setFont(aFont)
        self.ageLabel.setAutoFillBackground(True)
        self.ageLabel.setAlignment(QtAlignCenter)
        self.ageLabel.setFixedHeight(int(2.1*SHARED.theme.fontPixelSize))

        # Progress
        self.buildProgress = NProgressCircle(self, 160, 16)
        self.buildProgress.setVisible(False)
        self.buildProgress.setMaximum(1)
        self.buildProgress.setValue(0)
        self.buildProgress.setColors(
            back=QColor(255, 255, 255, 224),
            track=QColor(196, 196, 196, 128),
            text=QColor(0, 0, 0)
        )

        self._updateDocMargins()
        self._updateBuildAge()

        self.updateTheme()
        self.setTextFont(CONFIG.textFont)

        # Age Timer
        self.ageTimer = QTimer(self)
        self.ageTimer.setInterval(10000)
        self.ageTimer.timeout.connect(self._updateBuildAge)
        self.ageTimer.start()

    ##
    #  Setters
    ##

    def setBuildName(self, name: str) -> None:
        """Set the build name for the document label."""
        self._buildName = name
        self._updateBuildAge()

    def setTextFont(self, font: QFont) -> None:
        """Set the text font properties and then reset for sub-widgets.
        This needs special attention since there appears to be a bug in
        Qt 5.15.3. See issues #1862 and #1875.
        """
        self.setFont(font)
        self.buildProgress.setFont(SHARED.theme.guiFont)
        self.ageLabel.setFont(SHARED.theme.guiFontSmall)

    ##
    #  Methods
    ##

    def beginNewBuild(self, length: int) -> None:
        """Clear the document and show the progress bar."""
        self.buildProgress.setMaximum(length)
        self.buildProgress.setValue(0)
        self.buildProgress.setCentreText(None)
        self.buildProgress.setVisible(True)
        if vBar := self.verticalScrollBar():
            self._scrollPos = vBar.value()
        self.setPlaceholderText("")
        self.clear()

    def buildStep(self, value: int) -> None:
        """Update the progress bar value."""
        self.buildProgress.setValue(value)
        QApplication.processEvents()

    def setContent(self, document: QTextDocument) -> None:
        """Set the content of the preview widget."""
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))

        self.buildProgress.setCentreText(self.tr("Processing ..."))
        QApplication.processEvents()

        document.setDocumentMargin(CONFIG.textMargin)
        self.setDocument(document)
        self.setTabStopDistance(CONFIG.tabWidth)

        self._docTime = int(time())
        self._updateBuildAge()

        self.buildProgress.setCentreText(self.tr("Done"))
        QApplication.restoreOverrideCursor()
        QApplication.processEvents()
        QTimer.singleShot(300, self._postUpdate)

    def updateTheme(self) -> None:
        """Update theme elements."""
        logger.debug("Theme Update: _PreviewWidget")

        palette = QApplication.palette()
        palette.setColor(QPalette.ColorRole.Window, palette.toolTipBase().color())
        palette.setColor(QPalette.ColorRole.WindowText, palette.toolTipText().color())
        self.ageLabel.setPalette(palette)

    ##
    #  Events
    ##

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Capture resize and update the document margins."""
        super().resizeEvent(event)
        self._updateDocMargins()

    ##
    #  Public Slots
    ##

    @pyqtSlot("QPrinter*")
    def printPreview(self, printer: QPrinter) -> None:
        """Connect the print preview painter to the document viewer."""
        if document := self.document():
            QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
            printer.setPageOrientation(QPageLayout.Orientation.Portrait)
            document.print(printer)
            QApplication.restoreOverrideCursor()

    @pyqtSlot(str)
    def navigateTo(self, anchor: str) -> None:
        """Go to a specific #link in the document."""
        logger.debug("Moving to anchor '#%s'", anchor)
        self.setSource(QUrl(f"#{anchor}"))

    ##
    #  Private Slots
    ##

    @pyqtSlot("QUrl")
    def _linkClicked(self, url: QUrl) -> None:
        """Process a clicked link in the document."""
        if link := url.url():
            logger.debug("Clicked link: '%s'", link)
            if link.startswith("#"):
                self.navigateTo(link.lstrip("#"))
            elif link.startswith("http"):
                QDesktopServices.openUrl(QUrl(url))

    @pyqtSlot()
    def _updateBuildAge(self) -> None:
        """Update the build time and the fuzzy age."""
        if self._buildName and self._docTime > 0:
            self.ageLabel.setText("<b>{0}</b><br>{1}: {2}".format(
                self._buildName,
                self.tr("Built"),
                fuzzyTime(int(time()) - self._docTime),
            ))
        else:
            self.ageLabel.setText("<b>{0}</b>".format(self.tr("No Preview")))

    @pyqtSlot()
    def _postUpdate(self) -> None:
        """Run tasks after content update."""
        self.buildProgress.setVisible(False)
        if vBar := self.verticalScrollBar():
            vBar.setValue(self._scrollPos)

    ##
    #  Internal Functions
    ##

    def _updateDocMargins(self) -> None:
        """Automatically adjust the header to fill the top of the
        document within the viewport.
        """
        vBar = self.verticalScrollBar()
        tB = self.frameWidth()
        vW = self.width() - 2*tB - (vBar.width() if vBar else 0)
        vH = self.height() - 2*tB
        tH = self.ageLabel.height()
        pS = self.buildProgress.width()
        self.ageLabel.setGeometry(tB, tB, vW, tH)
        self.setViewportMargins(0, tH, 0, 0)
        self.buildProgress.move((vW-pS)//2, (vH-pS)//2)


class _StatsWidget(QWidget):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        font = self.font()
        font.setPointSizeF(0.9*SHARED.theme.fontPointSize)
        self.setFont(font)

        self.minWidget = QWidget(self)
        self.maxWidget = QWidget(self)

        self.toggleButton = NIconToggleButton(self, SHARED.theme.baseIconSize)
        self.toggleButton.toggled.connect(self._toggleView)

        self._buildBottomPanel()

        self.mainStack = QStackedWidget(self)
        self.mainStack.addWidget(self.minWidget)
        self.mainStack.addWidget(self.maxWidget)

        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.toggleButton, 0, QtAlignTop)
        self.outerBox.addWidget(self.mainStack, 1, QtAlignTop)
        self.outerBox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.outerBox)
        self.updateTheme()

        self._toggleView(False)

    def updateStats(self, data: dict[str, int]) -> None:
        """Update the stats values from a Tokenizer stats dict."""
        # Minimal
        self.minWordCount.setText(f"{data.get(nwStats.WORDS, 0):n}")
        self.minCharCount.setText(f"{data.get(nwStats.CHARS, 0):n}")

        # Maximal
        self.maxTotalWords.setText(f"{data.get(nwStats.WORDS, 0):n}")
        self.maxHeadWords.setText(f"{data.get(nwStats.WORDS_TITLE, 0):n}")
        self.maxTextWords.setText(f"{data.get(nwStats.WORDS_TEXT, 0):n}")
        self.maxTitleCount.setText(f"{data.get(nwStats.TITLES, 0):n}")
        self.maxParCount.setText(f"{data.get(nwStats.PARAGRAPHS, 0):n}")

        self.maxTotalChars.setText(f"{data.get(nwStats.CHARS, 0):n}")
        self.maxHeaderChars.setText(f"{data.get(nwStats.CHARS_TITLE, 0):n}")
        self.maxTextChars.setText(f"{data.get(nwStats.CHARS_TEXT, 0):n}")

        self.maxTotalWordChars.setText(f"{data.get(nwStats.WCHARS_ALL, 0):n}")
        self.maxHeadWordChars.setText(f"{data.get(nwStats.WCHARS_TITLE, 0):n}")
        self.maxTextWordChars.setText(f"{data.get(nwStats.WCHARS_TEXT, 0):n}")

    def updateTheme(self) -> None:
        """Update theme elements."""
        logger.debug("Theme Update: _StatsWidget")
        self.toggleButton.setThemeIcon("unfold", "default")

    ##
    #  Private Slots
    ##

    @pyqtSlot(bool)
    def _toggleView(self, state: bool) -> None:
        """Toggle minimal or maximal view."""
        if state:
            self.mainStack.setCurrentWidget(self.maxWidget)
            self.maxWidget.setSizePolicy(QtSizeExpanding, QtSizeExpanding)
            self.minWidget.setSizePolicy(QtSizeIgnored, QtSizeIgnored)
        else:
            self.mainStack.setCurrentWidget(self.minWidget)
            self.maxWidget.setSizePolicy(QtSizeIgnored, QtSizeIgnored)
            self.minWidget.setSizePolicy(QtSizeExpanding, QtSizeExpanding)
        self.maxWidget.adjustSize()
        self.minWidget.adjustSize()
        self.mainStack.adjustSize()
        self.adjustSize()

    ##
    #  Internal Functions
    ##

    def _buildBottomPanel(self) -> None:
        """Build the bottom page."""
        trAllChars = trStats(nwLabels.STATS_NAME[nwStats.CHARS])
        trTextChars = trStats(nwLabels.STATS_NAME[nwStats.CHARS_TEXT])
        trTitleChars = trStats(nwLabels.STATS_NAME[nwStats.CHARS_TITLE])
        trParagraphCount = trStats(nwLabels.STATS_NAME[nwStats.PARAGRAPHS])
        trTitleCount = trStats(nwLabels.STATS_NAME[nwStats.TITLES])
        trAllWordChars = trStats(nwLabels.STATS_NAME[nwStats.WCHARS_ALL])
        trTextWordChars = trStats(nwLabels.STATS_NAME[nwStats.WCHARS_TEXT])
        trTitleWordChars = trStats(nwLabels.STATS_NAME[nwStats.WCHARS_TITLE])
        trAllWords = trStats(nwLabels.STATS_NAME[nwStats.WORDS])
        trTextWords = trStats(nwLabels.STATS_NAME[nwStats.WORDS_TEXT])
        trTitleWords = trStats(nwLabels.STATS_NAME[nwStats.WORDS_TITLE])

        # Minimal Form
        self.minWordCount = QLabel(self)
        self.minCharCount = QLabel(self)

        # Maximal Form, Left Column
        self.maxTotalWords = QLabel(self)
        self.maxHeadWords = QLabel(self)
        self.maxTextWords = QLabel(self)
        self.maxTitleCount = QLabel(self)
        self.maxParCount = QLabel(self)

        self.maxTotalWords.setAlignment(QtAlignRight)
        self.maxHeadWords.setAlignment(QtAlignRight)
        self.maxTextWords.setAlignment(QtAlignRight)
        self.maxTitleCount.setAlignment(QtAlignRight)
        self.maxParCount.setAlignment(QtAlignRight)

        self.leftForm = QFormLayout()
        self.leftForm.addRow(trAllWords, self.maxTotalWords)
        self.leftForm.addRow(trTitleWords, self.maxHeadWords)
        self.leftForm.addRow(trTextWords, self.maxTextWords)
        self.leftForm.addRow("", QLabel(self))
        self.leftForm.addRow(trTitleCount, self.maxTitleCount)
        self.leftForm.addRow(trParagraphCount, self.maxParCount)
        self.leftForm.setHorizontalSpacing(12)
        self.leftForm.setVerticalSpacing(4)

        # Maximal Form, Right Column
        self.maxTotalChars = QLabel(self)
        self.maxHeaderChars = QLabel(self)
        self.maxTextChars = QLabel(self)
        self.maxTotalWordChars = QLabel(self)
        self.maxHeadWordChars = QLabel(self)
        self.maxTextWordChars = QLabel(self)

        self.maxTotalChars.setAlignment(QtAlignRight)
        self.maxHeaderChars.setAlignment(QtAlignRight)
        self.maxTextChars.setAlignment(QtAlignRight)
        self.maxTotalWordChars.setAlignment(QtAlignRight)
        self.maxHeadWordChars.setAlignment(QtAlignRight)
        self.maxTextWordChars.setAlignment(QtAlignRight)

        self.rightForm = QFormLayout()
        self.rightForm.addRow(trAllChars, self.maxTotalChars)
        self.rightForm.addRow(trTitleChars, self.maxHeaderChars)
        self.rightForm.addRow(trTextChars, self.maxTextChars)
        self.rightForm.addRow(trAllWordChars, self.maxTotalWordChars)
        self.rightForm.addRow(trTitleWordChars, self.maxHeadWordChars)
        self.rightForm.addRow(trTextWordChars, self.maxTextWordChars)
        self.rightForm.setHorizontalSpacing(12)
        self.rightForm.setVerticalSpacing(4)

        # Assemble
        self.minLayout = QHBoxLayout()
        self.minLayout.addWidget(QLabel(trAllWords, self))
        self.minLayout.addWidget(self.minWordCount)
        self.minLayout.addSpacing(8)
        self.minLayout.addWidget(QLabel(trAllChars, self))
        self.minLayout.addWidget(self.minCharCount)
        self.minLayout.addStretch(1)
        self.minLayout.setSpacing(8)
        self.minLayout.setContentsMargins(0, 0, 0, 0)

        self.maxLayout = QHBoxLayout()
        self.maxLayout.addLayout(self.leftForm)
        self.maxLayout.addLayout(self.rightForm)
        self.maxLayout.addStretch(1)
        self.maxLayout.setSpacing(32)
        self.maxLayout.setContentsMargins(0, 0, 0, 0)

        self.minWidget.setLayout(self.minLayout)
        self.maxWidget.setLayout(self.maxLayout)
