"""
novelWriter – GUI Document Viewer Panel
=======================================

File History:
Created: 2023-11-14 [2.2rc1] GuiDocViewerPanel

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
from __future__ import annotations

import logging

from PyQt5.QtCore import QSize, Qt, pyqtSlot
from PyQt5.QtWidgets import (
    QAbstractItemView, QFrame, QHBoxLayout, QHeaderView, QTabWidget, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.constants import nwHeaders, nwLabels, nwLists, trConst

logger = logging.getLogger(__name__)


class GuiDocViewerPanel(QWidget):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiDocViewerPanel")

        self._lastHandle = None

        self.tabBackRefs = _ViewPanelBackRefs(self)

        self.mainTabs = QTabWidget(self)
        self.mainTabs.addTab(self.tabBackRefs, self.tr("Backreferences"))

        self.kwTabs = {}
        for itemClass in nwLists.USER_CLASSES:
            self.kwTabs[itemClass] = _ViewPanelKeyWords(self)
            self.mainTabs.addTab(self.kwTabs[itemClass], trConst(nwLabels.CLASS_NAME[itemClass]))

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.mainTabs)
        self.outerBox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.outerBox)
        self.updateTheme()

        logger.debug("Ready: GuiDocViewerPanel")

        return

    def updateTheme(self) -> None:
        """Update theme elements."""
        vPx = CONFIG.pxInt(4)
        lPx = CONFIG.pxInt(2)
        rPx = CONFIG.pxInt(14)
        hCol = self.palette().highlight().color()

        styleSheet = (
            "QTabWidget::pane {border: 0;} "
            "QTabWidget QTabBar::tab {"
            f"border: 0; padding: {vPx}px {rPx}px {vPx}px {lPx}px;"
            "} "
            "QTabWidget QTabBar::tab:selected {"
            f"color: rgb({hCol.red()}, {hCol.green()}, {hCol.blue()});"
            "} "
        )
        self.mainTabs.setStyleSheet(styleSheet)
        self.updateHandle(self._lastHandle)

        return

    ##
    #  Public Slots
    ##

    @pyqtSlot(str)
    def updateHandle(self, tHandle: str | None) -> None:
        """Update the document handle."""
        self._lastHandle = tHandle
        self.tabBackRefs.refreshContent(tHandle or None)
        return

# END Class GuiDocViewerPanel


class _ViewPanelBackRefs(QWidget):

    C_DATA  = 0
    C_TITLE = 0
    C_EDIT  = 1
    C_VIEW  = 2
    C_NAME  = 3

    D_HANDLE = Qt.ItemDataRole.UserRole
    D_TITLE  = Qt.ItemDataRole.UserRole + 1

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        iPx = SHARED.theme.baseIconSize
        cMg = CONFIG.pxInt(6)

        # Content
        self.listBox = QTreeWidget(self)
        # self.listBox.setHeaderHidden(True)
        # self.listBox.setColumnCount(4)
        self.listBox.setHeaderLabels([
            self.tr("Title"), "", "", self.tr("Document")
        ])
        self.listBox.setIndentation(0)
        self.listBox.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.listBox.setIconSize(QSize(iPx, iPx))
        self.listBox.setFrameStyle(QFrame.Shape.NoFrame)

        treeHeader = self.listBox.header()
        treeHeader.setStretchLastSection(True)
        treeHeader.setSectionResizeMode(self.C_EDIT, QHeaderView.ResizeMode.Fixed)
        treeHeader.setSectionResizeMode(self.C_VIEW, QHeaderView.ResizeMode.Fixed)
        treeHeader.setSectionResizeMode(self.C_NAME, QHeaderView.ResizeMode.ResizeToContents)
        treeHeader.setSectionResizeMode(self.C_TITLE, QHeaderView.ResizeMode.ResizeToContents)
        treeHeader.resizeSection(self.C_EDIT, iPx + cMg)
        treeHeader.resizeSection(self.C_VIEW, iPx + cMg)

        fH1 = self.font()
        fH1.setBold(True)
        fH1.setUnderline(True)

        fH2 = self.font()
        fH2.setBold(True)

        self._hFonts = [self.font(), fH1, fH2, self.font(), self.font(), self.font()]
        self._editIcon = SHARED.theme.getIcon("edit")
        self._viewIcon = SHARED.theme.getIcon("view")

        # Assemble
        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.listBox)
        self.outerBox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.outerBox)
        self.setContentsMargins(0, 0, 0, 0)

        return

    def refreshContent(self, dHandle: str | None) -> None:
        """Update the content."""
        self.listBox.clear()
        if dHandle:
            refs = SHARED.project.index.getBackReferenceList(dHandle)
            for tHandle, (sTitle, hItem) in refs.items():
                nwItem = SHARED.project.tree[tHandle]
                if nwItem is None:
                    continue

                docIcon = SHARED.theme.getItemIcon(
                    nwItem.itemType, nwItem.itemClass,
                    nwItem.itemLayout, nwItem.mainHeading
                )
                iLevel = nwHeaders.H_LEVEL.get(hItem.level, 0) if nwItem.isDocumentLayout() else 5
                hDec = SHARED.theme.getHeaderDecorationNarrow(iLevel)

                trItem = QTreeWidgetItem()
                trItem.setText(self.C_TITLE, hItem.title)
                trItem.setData(self.C_TITLE, Qt.ItemDataRole.DecorationRole, hDec)
                trItem.setFont(self.C_TITLE, self._hFonts[iLevel])
                trItem.setIcon(self.C_EDIT, self._editIcon)
                trItem.setIcon(self.C_VIEW, self._viewIcon)
                trItem.setIcon(self.C_NAME, docIcon)
                trItem.setText(self.C_NAME, nwItem.itemName)

                trItem.setData(self.C_DATA, self.D_HANDLE, tHandle)
                trItem.setData(self.C_DATA, self.D_TITLE, sTitle)

                self.listBox.addTopLevelItem(trItem)
        return

# END Class _ViewPanelBackRefs


class _ViewPanelKeyWords(QWidget):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        return

# END Class _ViewPanelRefs
