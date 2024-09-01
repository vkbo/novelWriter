"""
novelWriter – GUI Manuscript Tool
=================================

File History:
Created: 2023-05-13 [2.1b1] GuiManuscript

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

from time import time
from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt, QTimer, QUrl, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QCloseEvent, QColor, QCursor, QFont, QPalette, QResizeEvent, QTextDocument
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PyQt5.QtWidgets import (
    QAbstractItemView, QApplication, QFormLayout, QGridLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QPushButton, QSplitter,
    QStackedWidget, QTabWidget, QTextBrowser, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import fuzzyTime
from novelwriter.core.buildsettings import BuildCollection, BuildSettings
from novelwriter.core.docbuild import NWBuildDocument
from novelwriter.core.tokenizer import HeadingFormatter
from novelwriter.core.toqdoc import TextDocumentTheme, ToQTextDocument
from novelwriter.extensions.modified import NIconToggleButton, NIconToolButton, NToolDialog
from novelwriter.extensions.progressbars import NProgressCircle
from novelwriter.gui.theme import STYLES_FLAT_TABS, STYLES_MIN_TOOLBUTTON
from novelwriter.tools.manusbuild import GuiManuscriptBuild
from novelwriter.tools.manussettings import GuiBuildSettings
from novelwriter.types import (
    QtAlignCenter, QtAlignRight, QtAlignTop, QtSizeExpanding, QtSizeIgnored,
    QtUserRole
)

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


class GuiManuscript(NToolDialog):
    """GUI Tools: Manuscript Tool

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
        self.setMinimumWidth(CONFIG.pxInt(600))
        self.setMinimumHeight(CONFIG.pxInt(500))

        iSz = SHARED.theme.baseIconSize
        wWin = CONFIG.pxInt(900)
        hWin = CONFIG.pxInt(600)

        pOptions = SHARED.project.options
        self.resize(
            CONFIG.pxInt(pOptions.getInt("GuiManuscript", "winWidth", wWin)),
            CONFIG.pxInt(pOptions.getInt("GuiManuscript", "winHeight", hWin))
        )

        # Build Controls
        # ==============

        qPalette = self.palette()
        qPalette.setBrush(QPalette.ColorRole.Window, qPalette.base())
        self.setPalette(qPalette)

        buttonStyle = SHARED.theme.getStyleSheet(STYLES_MIN_TOOLBUTTON)

        self.tbAdd = NIconToolButton(self, iSz, "add")
        self.tbAdd.setToolTip(self.tr("Add New Build"))
        self.tbAdd.setStyleSheet(buttonStyle)
        self.tbAdd.clicked.connect(self._createNewBuild)

        self.tbDel = NIconToolButton(self, iSz, "remove")
        self.tbDel.setToolTip(self.tr("Delete Selected Build"))
        self.tbDel.setStyleSheet(buttonStyle)
        self.tbDel.clicked.connect(self._deleteSelectedBuild)

        self.tbEdit = NIconToolButton(self, iSz, "edit")
        self.tbEdit.setToolTip(self.tr("Edit Selected Build"))
        self.tbEdit.setStyleSheet(buttonStyle)
        self.tbEdit.clicked.connect(self._editSelectedBuild)

        self.lblBuilds = QLabel("<b>{0}</b>".format(self.tr("Builds")), self)

        self.listToolBox = QHBoxLayout()
        self.listToolBox.addWidget(self.lblBuilds)
        self.listToolBox.addStretch(1)
        self.listToolBox.addWidget(self.tbAdd)
        self.listToolBox.addWidget(self.tbDel)
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
        self.buildDetails.setColumnWidth(
            CONFIG.pxInt(pOptions.getInt("GuiManuscript", "detailsWidth", 100)),
        )

        self.buildOutline = _OutlineWidget(self)

        self.detailsTabs = QTabWidget(self)
        self.detailsTabs.addTab(self.buildDetails, self.tr("Details"))
        self.detailsTabs.addTab(self.buildOutline, self.tr("Outline"))
        self.detailsTabs.setStyleSheet(SHARED.theme.getStyleSheet(STYLES_FLAT_TABS))

        self.buildSplit = QSplitter(Qt.Orientation.Vertical, self)
        self.buildSplit.addWidget(self.buildList)
        self.buildSplit.addWidget(self.detailsTabs)
        self.buildSplit.setSizes([
            CONFIG.pxInt(pOptions.getInt("GuiManuscript", "listHeight", 50)),
            CONFIG.pxInt(pOptions.getInt("GuiManuscript", "detailsHeight", 50)),
        ])

        # Process Controls
        # ================

        self.btnPreview = QPushButton(self.tr("Preview"), self)
        self.btnPreview.clicked.connect(self._generatePreview)

        self.btnPrint = QPushButton(self.tr("Print"), self)
        self.btnPrint.clicked.connect(self._printDocument)

        self.btnBuild = QPushButton(self.tr("Build"), self)
        self.btnBuild.clicked.connect(self._buildManuscript)

        self.btnClose = QPushButton(self.tr("Close"), self)
        self.btnClose.clicked.connect(self.close)

        self.processBox = QGridLayout()
        self.processBox.addWidget(self.btnPreview, 0, 0)
        self.processBox.addWidget(self.btnPrint,   0, 1)
        self.processBox.addWidget(self.btnBuild,   1, 0)
        self.processBox.addWidget(self.btnClose,   1, 1)

        # Assemble GUI
        # ============

        self.docPreview = _PreviewWidget(self)
        self.docStats = _StatsWidget(self)

        self.docBox = QVBoxLayout()
        self.docBox.addWidget(self.docPreview, 1)
        self.docBox.addWidget(self.docStats, 0)
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
            CONFIG.pxInt(pOptions.getInt("GuiManuscript", "optsWidth", wWin//4)),
            CONFIG.pxInt(pOptions.getInt("GuiManuscript", "viewWidth", 3*wWin//4)),
        ])

        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.mainSplit)

        self.setLayout(self.outerBox)
        self.setSizeGripEnabled(True)

        # Signals
        self.buildOutline.outlineEntryClicked.connect(self.docPreview.navigateTo)

        logger.debug("Ready: GuiManuscript")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiManuscript")
        return

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

        return

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
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _createNewBuild(self) -> None:
        """Open the build settings dialog for a new build."""
        build = BuildSettings()
        build.setName(self.tr("My Manuscript"))
        self._openSettingsDialog(build)
        return

    @pyqtSlot()
    def _editSelectedBuild(self) -> None:
        """Edit the currently selected build settings entry."""
        if build := self._getSelectedBuild():
            self._openSettingsDialog(build)
        return

    @pyqtSlot("QListWidgetItem*", "QListWidgetItem*")
    def _updateBuildDetails(self, current: QListWidgetItem, previous: QListWidgetItem) -> None:
        """Process change of build selection to update the details."""
        if current and (build := self._builds.getBuild(current.data(self.D_KEY))):
            self.buildDetails.updateInfo(build)
        return

    @pyqtSlot()
    def _deleteSelectedBuild(self) -> None:
        """Delete the currently selected build settings entry."""
        if build := self._getSelectedBuild():
            if SHARED.question(self.tr("Delete build '{0}'?".format(build.name))):
                if dialog := self._findSettingsDialog(build.buildID):
                    dialog.close()
                self._builds.removeBuild(build.buildID)
                self._updateBuildsList()
        return

    @pyqtSlot(BuildSettings)
    def _processNewSettings(self, build: BuildSettings) -> None:
        """Process new build settings from the settings dialog."""
        self._builds.setBuild(build)
        self._updateBuildItem(build)
        if (current := self.buildList.currentItem()) and current.data(self.D_KEY) == build.buildID:
            self._updateBuildDetails(current, current)
        return

    @pyqtSlot()
    def _generatePreview(self) -> None:
        """Run the document builder on the current build settings for
        the preview widget.
        """
        if not (build := self._getSelectedBuild()):
            return

        start = time()

        # Make sure editor content is saved before we start
        SHARED.saveEditor()

        docBuild = NWBuildDocument(SHARED.project, build)
        docBuild.queueAll()

        theme = TextDocumentTheme()
        theme.text      = QColor(0, 0, 0)
        theme.highlight = QColor(255, 255, 166)
        theme.head      = QColor(66, 113, 174)
        theme.comment   = QColor(100, 100, 100)
        theme.note      = QColor(129, 55, 9)
        theme.code      = QColor(66, 113, 174)
        theme.modifier  = QColor(129, 55, 9)
        theme.keyword   = QColor(245, 135, 31)
        theme.tag       = QColor(66, 113, 174)
        theme.optional  = QColor(66, 113, 174)
        theme.dialog    = QColor(66, 113, 174)
        theme.altdialog = QColor(129, 55, 9)

        self.docPreview.beginNewBuild(len(docBuild))
        for step, _ in docBuild.iterBuildPreview(theme):
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

        return

    @pyqtSlot()
    def _printDocument(self) -> None:
        """Open the print preview dialog."""
        preview = QPrintPreviewDialog(self)
        preview.paintRequested.connect(self.docPreview.printPreview)
        preview.exec()
        return

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
        buildOrder = []
        for i in range(self.buildList.count()):
            if item := self.buildList.item(i):
                buildOrder.append(item.data(self.D_KEY))

        current = self.buildList.currentItem()
        lastBuild = current.data(self.D_KEY) if isinstance(current, QListWidgetItem) else ""

        self._builds.setBuildsState(lastBuild, buildOrder)

        winWidth  = CONFIG.rpxInt(self.width())
        winHeight = CONFIG.rpxInt(self.height())

        mainSplit = self.mainSplit.sizes()
        optsWidth = CONFIG.rpxInt(mainSplit[0])
        viewWidth = CONFIG.rpxInt(mainSplit[1])

        buildSplit = self.buildSplit.sizes()
        listHeight = CONFIG.rpxInt(buildSplit[0])
        detailsHeight = CONFIG.rpxInt(buildSplit[1])
        detailsWidth = CONFIG.rpxInt(self.buildDetails.getColumnWidth())
        detailsExpanded = self.buildDetails.getExpandedState()

        logger.debug("Saving State: GuiManuscript")
        pOptions = SHARED.project.options
        pOptions.setValue("GuiManuscript", "winWidth", winWidth)
        pOptions.setValue("GuiManuscript", "winHeight", winHeight)
        pOptions.setValue("GuiManuscript", "optsWidth", optsWidth)
        pOptions.setValue("GuiManuscript", "viewWidth", viewWidth)
        pOptions.setValue("GuiManuscript", "listHeight", listHeight)
        pOptions.setValue("GuiManuscript", "detailsHeight", detailsHeight)
        pOptions.setValue("GuiManuscript", "detailsWidth", detailsWidth)
        pOptions.setValue("GuiManuscript", "detailsExpanded", detailsExpanded)
        pOptions.saveSettings()

        return

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
            bItem.setIcon(SHARED.theme.getIcon("export"))
            bItem.setData(self.D_KEY, key)
            self.buildList.addItem(bItem)
            self._buildMap[key] = bItem
        return

    def _updateBuildItem(self, build: BuildSettings) -> None:
        """Update the entry of a specific build item."""
        bItem = self._buildMap.get(build.buildID, None)
        if isinstance(bItem, QListWidgetItem):
            bItem.setText(build.name)
        else:  # Probably a new item
            self._updateBuildsList()
        return

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

        return

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
        return

    def setExpandedState(self, state: list[bool]) -> None:
        """Set the expanded state of each top level item."""
        count = len(state)
        for i in range(self.listView.topLevelItemCount()):
            item = self.listView.topLevelItem(i)
            if isinstance(item, QTreeWidgetItem):
                item.setExpanded((state[i] if i < count else True) and item.childCount() > 0)
        return

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

        on = SHARED.theme.getIcon("bullet-on")
        off = SHARED.theme.getIcon("bullet-off")

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
        hFmt = HeadingFormatter(SHARED.project)
        hFmt.incChapter()
        hFmt.incScene()
        hFmt.resetScene()
        hFmt.incScene()
        title = self.tr("Title")
        hidden = self.tr("Hidden")

        item = QTreeWidgetItem()
        item.setText(0, build.getLabel("headings"))
        item.setText(1, "")
        self.listView.addTopLevelItem(item)
        for hFormat, hHide in [
            ("headings.fmtTitle", "headings.hideTitle"),
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
                sub.setText(1, hFmt.apply(build.getStr(hFormat), title, 0))
            item.addChild(sub)

        # Text Content
        item = QTreeWidgetItem()
        item.setText(0, build.getLabel("text.grpContent"))
        item.setText(1, "")
        self.listView.addTopLevelItem(item)
        for key in [
            "text.includeSynopsis", "text.includeComments",
            "text.includeKeywords", "text.includeBodyText",
        ]:
            sub = QTreeWidgetItem()
            sub.setText(0, build.getLabel(key))
            sub.setIcon(1, on if build.getBool(key) else off)
            item.addChild(sub)

        # Restore expanded state
        self.setExpandedState(expanded)

        return


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

        return

    def updateOutline(self, data: dict[str, str]) -> None:
        """Update the outline."""
        if isinstance(data, dict) and data != self._outline:
            self.listView.clear()

            tFont = self.font()
            tFont.setBold(True)
            tBrush = self.palette().highlight()

            hFont = self.font()
            hFont.setBold(True)
            hFont.setUnderline(True)

            root = self.listView.invisibleRootItem()
            parent = root
            indent = False
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

            self.listView.setIndentation(
                SHARED.theme.baseIconHeight if indent else CONFIG.pxInt(4)
            )
            self._outline = data

        return

    ##
    #  Private Slots
    ##

    def _onItemClick(self, item: QTreeWidgetItem) -> None:
        """Process tree item click."""
        self.outlineEntryClicked.emit(str(item.data(0, self.D_LINE)))
        return


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
        self.setTabStopDistance(CONFIG.getTabWidth())
        self.setOpenExternalLinks(False)

        self.document().setDocumentMargin(CONFIG.getTextMargin())
        self.setPlaceholderText(self.tr(
            "Press the \"Preview\" button to generate ..."
        ))

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        # Document Age
        aPalette = self.palette()
        aPalette.setColor(QPalette.ColorRole.Window, aPalette.toolTipBase().color())
        aPalette.setColor(QPalette.ColorRole.WindowText, aPalette.toolTipText().color())

        aFont = self.font()
        aFont.setPointSizeF(0.9*SHARED.theme.fontPointSize)

        self.ageLabel = QLabel("", self)
        self.ageLabel.setIndent(0)
        self.ageLabel.setFont(aFont)
        self.ageLabel.setPalette(aPalette)
        self.ageLabel.setAutoFillBackground(True)
        self.ageLabel.setAlignment(QtAlignCenter)
        self.ageLabel.setFixedHeight(int(2.1*SHARED.theme.fontPixelSize))

        # Progress
        self.buildProgress = NProgressCircle(self, CONFIG.pxInt(160), CONFIG.pxInt(16))
        self.buildProgress.setVisible(False)
        self.buildProgress.setMaximum(1)
        self.buildProgress.setValue(0)
        self.buildProgress.setColours(
            back=QColor(255, 255, 255, 224),
            track=QColor(196, 196, 196, 128),
            text=QColor(0, 0, 0)
        )

        self._updateDocMargins()
        self._updateBuildAge()

        self.setTextFont(CONFIG.textFont)

        # Age Timer
        self.ageTimer = QTimer(self)
        self.ageTimer.setInterval(10000)
        self.ageTimer.timeout.connect(self._updateBuildAge)
        self.ageTimer.start()

        return

    ##
    #  Setters
    ##

    def setBuildName(self, name: str) -> None:
        """Set the build name for the document label."""
        self._buildName = name
        self._updateBuildAge()
        return

    def setTextFont(self, font: QFont) -> None:
        """Set the text font properties and then reset for sub-widgets.
        This needs special attention since there appears to be a bug in
        Qt 5.15.3. See issues #1862 and #1875.
        """
        self.setFont(font)
        self.buildProgress.setFont(SHARED.theme.guiFont)
        self.ageLabel.setFont(SHARED.theme.guiFontSmall)
        return

    ##
    #  Methods
    ##

    def beginNewBuild(self, length: int) -> None:
        """Clear the document and show the progress bar."""
        self.buildProgress.setMaximum(length)
        self.buildProgress.setValue(0)
        self.buildProgress.setCentreText(None)
        self.buildProgress.setVisible(True)
        self._scrollPos = self.verticalScrollBar().value()
        self.setPlaceholderText("")
        self.clear()
        return

    def buildStep(self, value: int) -> None:
        """Update the progress bar value."""
        self.buildProgress.setValue(value)
        QApplication.processEvents()
        return

    def setContent(self, document: QTextDocument) -> None:
        """Set the content of the preview widget."""
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))

        self.buildProgress.setCentreText(self.tr("Processing ..."))
        QApplication.processEvents()

        document.setDocumentMargin(CONFIG.getTextMargin())
        self.setDocument(document)
        self.setTabStopDistance(CONFIG.getTabWidth())

        self._docTime = int(time())
        self._updateBuildAge()

        self.buildProgress.setCentreText(self.tr("Done"))
        QApplication.restoreOverrideCursor()
        QApplication.processEvents()
        QTimer.singleShot(300, self._postUpdate)

        return

    ##
    #  Events
    ##

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Capture resize and update the document margins."""
        super().resizeEvent(event)
        self._updateDocMargins()
        return

    ##
    #  Public Slots
    ##

    @pyqtSlot("QPrinter*")
    def printPreview(self, printer: QPrinter) -> None:
        """Connect the print preview painter to the document viewer."""
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        printer.setOrientation(QPrinter.Orientation.Portrait)
        self.document().print(printer)
        QApplication.restoreOverrideCursor()
        return

    @pyqtSlot(str)
    def navigateTo(self, anchor: str) -> None:
        """Go to a specific #link in the document."""
        logger.debug("Moving to anchor '#%s'", anchor)
        self.setSource(QUrl(f"#{anchor}"))
        return

    ##
    #  Private Slots
    ##

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
        return

    @pyqtSlot()
    def _postUpdate(self) -> None:
        """Run tasks after content update."""
        self.buildProgress.setVisible(False)
        self.verticalScrollBar().setValue(self._scrollPos)
        return

    ##
    #  Internal Functions
    ##

    def _updateDocMargins(self) -> None:
        """Automatically adjust the header to fill the top of the
        document within the viewport.
        """
        vBar = self.verticalScrollBar()
        tB = self.frameWidth()
        vW = self.width() - 2*tB - vBar.width()
        vH = self.height() - 2*tB
        tH = self.ageLabel.height()
        pS = self.buildProgress.width()
        self.ageLabel.setGeometry(tB, tB, vW, tH)
        self.setViewportMargins(0, tH, 0, 0)
        self.buildProgress.move((vW-pS)//2, (vH-pS)//2)
        return


class _StatsWidget(QWidget):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        font = self.font()
        font.setPointSizeF(0.9*SHARED.theme.fontPointSize)
        self.setFont(font)

        self.minWidget = QWidget(self)
        self.maxWidget = QWidget(self)

        self.toggleButton = NIconToggleButton(self, SHARED.theme.baseIconSize, "unfold")
        self.toggleButton.toggled.connect(self._toggleView)

        self._buildMinimal()
        self._buildMaximal()

        self.mainStack = QStackedWidget(self)
        self.mainStack.addWidget(self.minWidget)
        self.mainStack.addWidget(self.maxWidget)

        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.toggleButton, 0, QtAlignTop)
        self.outerBox.addWidget(self.mainStack, 1, QtAlignTop)
        self.outerBox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.outerBox)

        self._toggleView(False)

        return

    def updateStats(self, data: dict[str, int]) -> None:
        """Update the stats values from a Tokenizer stats dict."""
        # Minimal
        self.minWordCount.setText("{0:n}".format(data.get("allWords", 0)))
        self.minCharCount.setText("{0:n}".format(data.get("allChars", 0)))

        # Maximal
        self.maxTotalWords.setText("{0:n}".format(data.get("allWords", 0)))
        self.maxHeadWords.setText("{0:n}".format(data.get("titleWords", 0)))
        self.maxTextWords.setText("{0:n}".format(data.get("textWords", 0)))
        self.maxTitleCount.setText("{0:n}".format(data.get("titleCount", 0)))
        self.maxParCount.setText("{0:n}".format(data.get("paragraphCount", 0)))

        self.maxTotalChars.setText("{0:n}".format(data.get("allChars", 0)))
        self.maxHeaderChars.setText("{0:n}".format(data.get("titleChars", 0)))
        self.maxTextChars.setText("{0:n}".format(data.get("textChars", 0)))

        self.maxTotalWordChars.setText("{0:n}".format(data.get("allWordChars", 0)))
        self.maxHeadWordChars.setText("{0:n}".format(data.get("titleWordChars", 0)))
        self.maxTextWordChars.setText("{0:n}".format(data.get("textWordChars", 0)))

        return

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
        return

    ##
    #  Internal Functions
    ##

    def _buildMinimal(self) -> None:
        """Build the minimal stats page."""
        mPx = CONFIG.pxInt(8)

        self.lblWordCount = QLabel(self.tr("Words"), self)
        self.minWordCount = QLabel(self)

        self.lblCharCount = QLabel(self.tr("Characters"), self)
        self.minCharCount = QLabel(self)

        # Assemble
        self.minLayout = QHBoxLayout()
        self.minLayout.addWidget(self.lblWordCount)
        self.minLayout.addWidget(self.minWordCount)
        self.minLayout.addSpacing(mPx)
        self.minLayout.addWidget(self.lblCharCount)
        self.minLayout.addWidget(self.minCharCount)
        self.minLayout.addStretch(1)
        self.minLayout.setSpacing(mPx)
        self.minLayout.setContentsMargins(0, 0, 0, 0)

        self.minWidget.setLayout(self.minLayout)

        return

    def _buildMaximal(self) -> None:
        """Build the maximal stats page."""
        hPx = CONFIG.pxInt(12)
        vPx = CONFIG.pxInt(4)

        # Left Column
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
        self.leftForm.addRow(self.tr("Words"), self.maxTotalWords)
        self.leftForm.addRow(self.tr("Words in Headings"), self.maxHeadWords)
        self.leftForm.addRow(self.tr("Words in Text"), self.maxTextWords)
        self.leftForm.addRow("", QLabel(self))
        self.leftForm.addRow(self.tr("Headings"), self.maxTitleCount)
        self.leftForm.addRow(self.tr("Paragraphs"), self.maxParCount)
        self.leftForm.setHorizontalSpacing(hPx)
        self.leftForm.setVerticalSpacing(vPx)

        # Right Column
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
        self.rightForm.addRow(self.tr("Characters"), self.maxTotalChars)
        self.rightForm.addRow(self.tr("Characters in Headings"), self.maxHeaderChars)
        self.rightForm.addRow(self.tr("Characters in Text"), self.maxTextChars)
        self.rightForm.addRow(self.tr("Characters, No Spaces"), self.maxTotalWordChars)
        self.rightForm.addRow(self.tr("Characters in Headings, No Spaces"), self.maxHeadWordChars)
        self.rightForm.addRow(self.tr("Characters in Text, No Spaces"), self.maxTextWordChars)
        self.rightForm.setHorizontalSpacing(hPx)
        self.rightForm.setVerticalSpacing(vPx)

        # Assemble
        self.maxLayout = QHBoxLayout()
        self.maxLayout.addLayout(self.leftForm)
        self.maxLayout.addLayout(self.rightForm)
        self.maxLayout.addStretch(1)
        self.maxLayout.setSpacing(CONFIG.pxInt(32))
        self.maxLayout.setContentsMargins(0, 0, 0, 0)

        self.maxWidget.setLayout(self.maxLayout)

        return
