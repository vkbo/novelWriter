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

import json
import logging

from time import time
from typing import TYPE_CHECKING
from datetime import datetime

from PyQt5.QtGui import QCloseEvent, QColor, QCursor, QFont, QPalette, QResizeEvent
from PyQt5.QtCore import QSize, QTimer, Qt, pyqtSlot
from PyQt5.QtWidgets import (
    QAbstractItemView, QDialog, QFormLayout, QGridLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QSizePolicy, QSplitter,
    QStackedWidget, QTextBrowser, QToolButton, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget, qApp
)
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter

from novelwriter import CONFIG, SHARED
from novelwriter.error import logException
from novelwriter.common import checkInt, fuzzyTime
from novelwriter.core.tohtml import ToHtml
from novelwriter.core.docbuild import NWBuildDocument
from novelwriter.core.tokenizer import HeadingFormatter
from novelwriter.core.buildsettings import BuildCollection, BuildSettings
from novelwriter.tools.manusbuild import GuiManuscriptBuild
from novelwriter.tools.manussettings import GuiBuildSettings
from novelwriter.extensions.circularprogress import NProgressCircle

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


class GuiManuscript(QDialog):
    """GUI Tools: Manuscript Tool

    The dialog displays all the users build definitions, a preview panel
    for the manuscript, and can trigger the actual build dialog to build
    a document directly to disk.
    """

    D_KEY = Qt.ItemDataRole.UserRole

    def __init__(self, mainGui: GuiMain) -> None:
        super().__init__(parent=mainGui)

        logger.debug("Create: GuiManuscript")
        self.setObjectName("GuiManuscript")
        if CONFIG.osDarwin:
            self.setWindowFlag(Qt.WindowType.Tool)

        self.mainGui = mainGui

        self._builds = BuildCollection(SHARED.project)
        self._buildMap: dict[str, QListWidgetItem] = {}

        self.setWindowTitle(self.tr("Build Manuscript"))
        self.setMinimumWidth(CONFIG.pxInt(600))
        self.setMinimumHeight(CONFIG.pxInt(500))

        iPx = SHARED.theme.baseIconSize
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
        qPalette.setBrush(QPalette.Window, qPalette.base())
        self.setPalette(qPalette)

        fadeCol = qPalette.text().color()
        buttonStyle = (
            "QToolButton {{padding: {0}px; border: none; background: transparent;}} "
            "QToolButton:hover {{border: none; background: rgba({1},{2},{3},0.2);}}"
        ).format(CONFIG.pxInt(2), fadeCol.red(), fadeCol.green(), fadeCol.blue())

        self.tbAdd = QToolButton(self)
        self.tbAdd.setIcon(SHARED.theme.getIcon("add"))
        self.tbAdd.setIconSize(QSize(iPx, iPx))
        self.tbAdd.setToolTip(self.tr("Add New Build"))
        self.tbAdd.setStyleSheet(buttonStyle)
        self.tbAdd.clicked.connect(self._createNewBuild)

        self.tbDel = QToolButton(self)
        self.tbDel.setIcon(SHARED.theme.getIcon("remove"))
        self.tbDel.setIconSize(QSize(iPx, iPx))
        self.tbDel.setToolTip(self.tr("Delete Selected Build"))
        self.tbDel.setStyleSheet(buttonStyle)
        self.tbDel.clicked.connect(self._deleteSelectedBuild)

        self.tbEdit = QToolButton(self)
        self.tbEdit.setIcon(SHARED.theme.getIcon("edit"))
        self.tbEdit.setIconSize(QSize(iPx, iPx))
        self.tbEdit.setToolTip(self.tr("Edit Selected Build"))
        self.tbEdit.setStyleSheet(buttonStyle)
        self.tbEdit.clicked.connect(self._editSelectedBuild)

        self.lblBuilds = QLabel("<b>{0}</b>".format(self.tr("Builds")))

        self.listToolBox = QHBoxLayout()
        self.listToolBox.addWidget(self.lblBuilds)
        self.listToolBox.addStretch(1)
        self.listToolBox.addWidget(self.tbAdd)
        self.listToolBox.addWidget(self.tbDel)
        self.listToolBox.addWidget(self.tbEdit)
        self.listToolBox.setSpacing(0)

        # Builds
        # ======

        self.buildList = QListWidget()
        self.buildList.setIconSize(QSize(iPx, iPx))
        self.buildList.doubleClicked.connect(self._editSelectedBuild)
        self.buildList.currentItemChanged.connect(self._updateBuildDetails)
        self.buildList.setSelectionMode(QAbstractItemView.SingleSelection)
        self.buildList.setDragDropMode(QAbstractItemView.InternalMove)

        self.buildDetails = _DetailsWidget(self)
        self.buildDetails.setColumnWidth(
            CONFIG.pxInt(pOptions.getInt("GuiManuscript", "detailsWidth", 100)),
        )

        self.buildSplit = QSplitter(Qt.Orientation.Vertical, self)
        self.buildSplit.addWidget(self.buildList)
        self.buildSplit.addWidget(self.buildDetails)
        self.buildSplit.setSizes([
            CONFIG.pxInt(pOptions.getInt("GuiManuscript", "listHeight", 50)),
            CONFIG.pxInt(pOptions.getInt("GuiManuscript", "detailsHeight", 50)),
        ])

        # Process Controls
        # ================

        self.btnPreview = QPushButton(self.tr("Preview"))
        self.btnPreview.clicked.connect(self._generatePreview)

        self.btnPrint = QPushButton(self.tr("Print"))
        self.btnPrint.clicked.connect(self._printDocument)

        self.btnBuild = QPushButton(self.tr("Build"))
        self.btnBuild.clicked.connect(self._buildManuscript)

        self.btnClose = QPushButton(self.tr("Close"))
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

        self.mainSplit = QSplitter()
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

        logger.debug("Loading build cache")
        cache = CONFIG.dataPath("cache") / f"build_{SHARED.project.data.uuid}.json"
        if cache.is_file():
            try:
                with open(cache, mode="r", encoding="utf-8") as fObj:
                    data = json.load(fObj)
                build = self._builds.getBuild(data.get("uuid", ""))
                if isinstance(build, BuildSettings):
                    self._updatePreview(data, build)
            except Exception:
                logger.error("Failed to load build cache")
                logException()
                return

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
        for obj in self.mainGui.children():
            # Make sure we don't have any settings windows open
            if isinstance(obj, GuiBuildSettings) and obj.isVisible():
                obj.close()
        event.accept()
        self.deleteLater()
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
        build = self._getSelectedBuild()
        if build is not None:
            self._openSettingsDialog(build)
        return

    @pyqtSlot("QListWidgetItem*", "QListWidgetItem*")
    def _updateBuildDetails(self, current: QListWidgetItem, previous: QListWidgetItem) -> None:
        """Process change of build selection to update the details."""
        if isinstance(current, QListWidgetItem):
            build = self._builds.getBuild(current.data(self.D_KEY))
            if build is not None:
                self.buildDetails.updateInfo(build)
        return

    @pyqtSlot()
    def _deleteSelectedBuild(self) -> None:
        """Delete the currently selected build settings entry."""
        build = self._getSelectedBuild()
        if build is not None:
            if SHARED.question(self.tr("Delete build '{0}'?".format(build.name))):
                self._builds.removeBuild(build.buildID)
                self._updateBuildsList()
        return

    @pyqtSlot(BuildSettings)
    def _processNewSettings(self, build: BuildSettings) -> None:
        """Process new build settings from the settings dialog."""
        self._builds.setBuild(build)
        self._updateBuildItem(build)
        current = self.buildList.currentItem()
        if isinstance(current, QListWidgetItem) and current.data(self.D_KEY) == build.buildID:
            self._updateBuildDetails(current, current)
        return

    @pyqtSlot()
    def _generatePreview(self) -> None:
        """Run the document builder on the current build settings for
        the preview widget.
        """
        build = self._getSelectedBuild()
        if build is None:
            return

        docBuild = NWBuildDocument(SHARED.project, build)
        docBuild.setPreviewMode(True)
        docBuild.queueAll()

        self.docPreview.beginNewBuild(len(docBuild))
        for step, _ in docBuild.iterBuildHTML(None):
            self.docPreview.buildStep(step + 1)
            qApp.processEvents()

        buildObj = docBuild.lastBuild
        assert isinstance(buildObj, ToHtml)
        result = {
            "uuid": build.buildID,
            "time": int(time()),
            "stats": buildObj.textStats,
            "styles": buildObj.getStyleSheet(),
            "html": buildObj.fullHTML,
        }

        self._updatePreview(result, build)

        logger.debug("Saving build cache")
        cache = CONFIG.dataPath("cache") / f"build_{SHARED.project.data.uuid}.json"
        try:
            with open(cache, mode="w+", encoding="utf-8") as outFile:
                outFile.write(json.dumps(result, indent=2))
        except Exception:
            logger.error("Failed to save build cache")
            logException()
            return

        return

    @pyqtSlot()
    def _buildManuscript(self) -> None:
        """Open the build dialog and build the manuscript."""
        build = self._getSelectedBuild()
        if isinstance(build, BuildSettings):
            dlgBuild = GuiManuscriptBuild(self, build)
            dlgBuild.exec_()

            # After the build is done, save build settings changes
            if build.changed:
                self._builds.setBuild(build)

        return

    @pyqtSlot()
    def _printDocument(self) -> None:
        """Open the print preview dialog."""
        preview = QPrintPreviewDialog(self)
        preview.paintRequested.connect(self.docPreview.printPreview)
        preview.exec_()
        return

    ##
    #  Internal Functions
    ##

    def _updatePreview(self, data: dict, build: BuildSettings) -> None:
        """Update the preview widget and set relevant values."""
        self.docPreview.setContent(data)
        self.docPreview.setBuildName(build.name)
        self.docPreview.setTextFont(
            build.getStr("format.textFont"),
            build.getInt("format.textSize")
        )
        self.docPreview.setJustify(
            build.getBool("format.justifyText")
        )
        self.docStats.updateStats(data.get("stats", {}))
        return

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
        for obj in self.mainGui.children():
            # Don't open a second dialog if one exists
            if isinstance(obj, GuiBuildSettings):
                if obj.buildID == build.buildID:
                    logger.debug("Found instance of GuiBuildSettings")
                    obj.show()
                    obj.raise_()
                    return

        dlgSettings = GuiBuildSettings(self.mainGui, build)
        dlgSettings.setModal(False)
        dlgSettings.show()
        dlgSettings.raise_()
        qApp.processEvents()
        dlgSettings.loadContent()
        dlgSettings.newSettingsReady.connect(self._processNewSettings)

        return

    def _updateBuildsList(self) -> None:
        """Update the list of available builds."""
        self.buildList.clear()
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

# END Class GuiManuscript


class _DetailsWidget(QWidget):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        self._initExpanded = True

        # Tree Widget
        self.listView = QTreeWidget(self)
        self.listView.setHeaderLabels([self.tr("Setting"), self.tr("Value")])
        self.listView.setIndentation(SHARED.theme.baseIconSize)
        self.listView.setSelectionMode(QAbstractItemView.NoSelection)

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

        item = QTreeWidgetItem()
        item.setText(0, build.getLabel("headings"))
        item.setText(1, "")
        self.listView.addTopLevelItem(item)
        entries = [
            "headings.fmtTitle", "headings.fmtChapter", "headings.fmtUnnumbered",
            "headings.fmtScene", "headings.fmtSection"
        ]
        for key in entries:
            sub = QTreeWidgetItem()
            sub.setText(0, build.getLabel(key))
            sub.setText(1, hFmt.apply(build.getStr(key), title, 0))
            item.addChild(sub)
        for key in ["headings.hideScene", "headings.hideSection"]:
            sub = QTreeWidgetItem()
            sub.setText(0, build.getLabel(key))
            sub.setIcon(1, on if build.getBool(key) else off)
            item.addChild(sub)

        # Text Content
        item = QTreeWidgetItem()
        item.setText(0, build.getLabel("text.grpContent"))
        item.setText(1, "")
        self.listView.addTopLevelItem(item)
        entries = [
            "text.includeSynopsis", "text.includeComments",
            "text.includeKeywords", "text.includeBodyText",
        ]
        for key in entries:
            sub = QTreeWidgetItem()
            sub.setText(0, build.getLabel(key))
            sub.setIcon(1, on if build.getBool(key) else off)
            item.addChild(sub)

        # Restore expanded state
        self.setExpandedState(expanded)

        return

# END Class _DetailsWidget


class _PreviewWidget(QTextBrowser):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        self._docTime = 0
        self._buildName = ""

        # Document Setup
        dPalette = self.palette()
        dPalette.setColor(QPalette.Base, QColor(255, 255, 255))
        dPalette.setColor(QPalette.Text, QColor(0, 0, 0))
        self.setPalette(dPalette)

        self.setMinimumWidth(40*SHARED.theme.textNWidth)
        self.setTextFont(CONFIG.textFont, CONFIG.textSize)
        self.setTabStopDistance(CONFIG.getTabWidth())
        self.setOpenExternalLinks(False)

        self.document().setDocumentMargin(CONFIG.getTextMargin())
        self.setPlaceholderText(self.tr(
            "Press the \"Preview\" button to generate ..."
        ))

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        # Document Age
        aPalette = self.palette()
        aPalette.setColor(QPalette.Background, aPalette.toolTipBase().color())
        aPalette.setColor(QPalette.Foreground, aPalette.toolTipText().color())

        aFont = self.font()
        aFont.setPointSizeF(0.9*SHARED.theme.fontPointSize)

        self.ageLabel = QLabel("", self)
        self.ageLabel.setIndent(0)
        self.ageLabel.setFont(aFont)
        self.ageLabel.setPalette(aPalette)
        self.ageLabel.setAutoFillBackground(True)
        self.ageLabel.setAlignment(Qt.AlignCenter)
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

        # Age Timer
        self.ageTimer = QTimer()
        self.ageTimer.setInterval(10)
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

    def setJustify(self, state: bool) -> None:
        """Enable/disable the justify text option."""
        pOptions = self.document().defaultTextOption()
        if state:
            pOptions.setAlignment(Qt.AlignJustify)
        else:
            pOptions.setAlignment(Qt.AlignAbsolute)
        self.document().setDefaultTextOption(pOptions)
        return

    def setTextFont(self, family: str, size: int) -> None:
        """Set the text font properties."""
        if family:
            font = QFont()
            font.setFamily(family)
            font.setPointSize(size)
            self.setFont(font)
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
        self.setPlaceholderText("")
        self.clear()
        return

    def buildStep(self, value: int) -> None:
        """Update the progress bar value."""
        self.buildProgress.setValue(value)
        qApp.processEvents()
        return

    def setContent(self, data: dict) -> None:
        """Set the content of the preview widget."""
        sPos = self.verticalScrollBar().value()
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))

        self.buildProgress.setCentreText(self.tr("Processing ..."))
        qApp.processEvents()

        styles = "\n".join(data.get("styles", []))
        self.document().setDefaultStyleSheet(styles)

        html = "".join(data.get("html", []))
        html = html.replace("\t", "!!tab!!")
        html = html.replace("<del>", "<span style='text-decoration: line-through;'>")
        html = html.replace("</del>", "</span>")
        self.setHtml(html)
        qApp.processEvents()
        while self.find("!!tab!!"):
            cursor = self.textCursor()
            cursor.insertText("\t")

        self.verticalScrollBar().setValue(sPos)
        self._docTime = checkInt(data.get("time"), 0)
        self._updateBuildAge()

        # Since we change the content while it may still be rendering, we mark
        # the document as dirty again to make sure it's re-rendered properly.
        self.document().markContentsDirty(0, self.document().characterCount())

        self.buildProgress.setCentreText(self.tr("Done"))
        qApp.restoreOverrideCursor()
        qApp.processEvents()
        QTimer.singleShot(300, self._hideProgress)

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
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        printer.setOrientation(QPrinter.Portrait)
        self.document().print(printer)
        qApp.restoreOverrideCursor()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _updateBuildAge(self) -> None:
        """Update the build time and the fuzzy age."""
        if self._docTime > 0:
            strBuildTime = "%s (%s)" % (
                CONFIG.localDateTime(datetime.fromtimestamp(self._docTime)),
                fuzzyTime(int(time()) - self._docTime)
            )
        else:
            strBuildTime = self.tr("Unknown")
        text = "{0}: {1}".format(self.tr("Built"), strBuildTime)
        if self._buildName:
            text = "<b>{0}</b><br>{1}".format(self._buildName, text)
        self.ageLabel.setText(text)
        return

    @pyqtSlot()
    def _hideProgress(self) -> None:
        """Clean up the build progress bar."""
        self.buildProgress.setVisible(False)
        return

    ##
    #  Internal Functions
    ##

    def _updateDocMargins(self) -> None:
        """Automatically adjust the header to fill the top of the
        document within the viewport.
        """
        vBar = self.verticalScrollBar()
        sW = vBar.width() if vBar.isVisible() else 0
        tB = self.frameWidth()
        vW = self.width() - 2*tB - sW
        vH = self.height() - 2*tB
        tH = self.ageLabel.height()
        pS = self.buildProgress.width()
        self.ageLabel.setGeometry(tB, tB, vW, tH)
        self.setViewportMargins(0, tH, 0, 0)
        self.buildProgress.move((vW-pS)//2, (vH-pS)//2)
        return

# END Class _PreviewWidget


class _StatsWidget(QWidget):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        font = self.font()
        font.setPointSizeF(0.9*SHARED.theme.fontPointSize)
        self.setFont(font)

        self.minWidget = QWidget(self)
        self.maxWidget = QWidget(self)

        fPx = int(0.6*SHARED.theme.fontPixelSize)
        toggleIcon = SHARED.theme.getToggleIcon("unfold", (fPx, fPx))

        fadeCol = self.palette().text().color()
        buttonStyle = (
            "QToolButton {{padding: 0; border: none; background: transparent;}} "
            "QToolButton:hover {{border: none; background: rgba({0},{1},{2},0.2);}}"
        ).format(fadeCol.red(), fadeCol.green(), fadeCol.blue())

        self.toggleButton = QToolButton(self)
        self.toggleButton.setCheckable(True)
        self.toggleButton.setIcon(toggleIcon)
        self.toggleButton.setStyleSheet(buttonStyle)
        self.toggleButton.toggled.connect(self._toggleView)

        self._buildMinimal()
        self._buildMaximal()

        self.mainStack = QStackedWidget(self)
        self.mainStack.addWidget(self.minWidget)
        self.mainStack.addWidget(self.maxWidget)

        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.toggleButton, 0, Qt.AlignmentFlag.AlignTop)
        self.outerBox.addWidget(self.mainStack, 1, Qt.AlignmentFlag.AlignTop)
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
        self.maxHeaderWords.setText("{0:n}".format(data.get("titleWords", 0)))
        self.maxTextWords.setText("{0:n}".format(data.get("textWords", 0)))
        self.maxTitleCount.setText("{0:n}".format(data.get("titleCount", 0)))
        self.maxParCount.setText("{0:n}".format(data.get("paragraphCount", 0)))

        self.maxTotalChars.setText("{0:n}".format(data.get("allChars", 0)))
        self.maxHeaderChars.setText("{0:n}".format(data.get("titleChars", 0)))
        self.maxTextChars.setText("{0:n}".format(data.get("textChars", 0)))

        self.maxTotalWordChars.setText("{0:n}".format(data.get("allWordChars", 0)))
        self.maxHeaderWordChars.setText("{0:n}".format(data.get("titleWordChars", 0)))
        self.maxTextWordChars.setText("{0:n}".format(data.get("textWordChars", 0)))

        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(bool)
    def _toggleView(self, state: bool) -> None:
        """Toggle minimal or maximal view."""
        ignored = QSizePolicy.Policy.Ignored
        expanded = QSizePolicy.Policy.Expanding
        if state:
            self.mainStack.setCurrentWidget(self.maxWidget)
            self.maxWidget.setSizePolicy(expanded, expanded)
            self.minWidget.setSizePolicy(ignored, ignored)
        else:
            self.mainStack.setCurrentWidget(self.minWidget)
            self.maxWidget.setSizePolicy(ignored, ignored)
            self.minWidget.setSizePolicy(expanded, expanded)
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

        self.lblWordCount = QLabel(self.tr("Words"))
        self.minWordCount = QLabel(self)

        self.lblCharCount = QLabel(self.tr("Characters"))
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

        alignRight = Qt.AlignmentFlag.AlignRight

        # Left Column
        self.maxTotalWords = QLabel(self)
        self.maxHeaderWords = QLabel(self)
        self.maxTextWords = QLabel(self)
        self.maxTitleCount = QLabel(self)
        self.maxParCount = QLabel(self)

        self.maxTotalWords.setAlignment(alignRight)
        self.maxHeaderWords.setAlignment(alignRight)
        self.maxTextWords.setAlignment(alignRight)
        self.maxTitleCount.setAlignment(alignRight)
        self.maxParCount.setAlignment(alignRight)

        self.leftForm = QFormLayout()
        self.leftForm.addRow(self.tr("Words"), self.maxTotalWords)
        self.leftForm.addRow(self.tr("Heading Words"), self.maxHeaderWords)
        self.leftForm.addRow(self.tr("Body Text Words"), self.maxTextWords)
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
        self.maxHeaderWordChars = QLabel(self)
        self.maxTextWordChars = QLabel(self)

        self.maxTotalChars.setAlignment(alignRight)
        self.maxHeaderChars.setAlignment(alignRight)
        self.maxTextChars.setAlignment(alignRight)

        self.maxTotalWordChars.setAlignment(alignRight)
        self.maxHeaderWordChars.setAlignment(alignRight)
        self.maxTextWordChars.setAlignment(alignRight)

        self.rightForm = QFormLayout()
        self.rightForm.addRow(self.tr("Characters"), self.maxTotalChars)
        self.rightForm.addRow(self.tr("Heading Characters"), self.maxHeaderChars)
        self.rightForm.addRow(self.tr("Body Text Characters"), self.maxTextChars)
        self.rightForm.addRow(self.tr("Characters, No Spaces"), self.maxTotalWordChars)
        self.rightForm.addRow(self.tr("Heading Characters, No Spaces"), self.maxHeaderWordChars)
        self.rightForm.addRow(self.tr("Body Text Characters, No Spaces"), self.maxTextWordChars)
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

# END Class _StatsWidget
