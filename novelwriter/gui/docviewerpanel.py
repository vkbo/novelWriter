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

from PyQt5.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from novelwriter import CONFIG
from novelwriter.constants import nwLabels, nwLists, trConst

logger = logging.getLogger(__name__)


class GuiDocViewerPanel(QWidget):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiDocViewerPanel")

        self.tabBackRefs = _ViewPanelBackRefs(self)

        self.mainTabs = QTabWidget(self)
        self.mainTabs.addTab(self.tabBackRefs, self.tr("Back References"))

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
            "QTabWidget QTabBar::tab {"
            f"border: 0; padding: {vPx}px {rPx}px {vPx}px {lPx}px;"
            "} "
            "QTabWidget QTabBar::tab:selected {"
            f"color: rgb({hCol.red()}, {hCol.green()}, {hCol.blue()});"
            "} "
        )
        self.mainTabs.setStyleSheet(styleSheet)

        return

# END Class GuiDocViewerPanel


class _ViewPanelBackRefs(QWidget):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        return

    def refreshContent(self):
        """"""
        # theRefs = SHARED.project.index.getBackReferenceList(tHandle)
        # theList = []
        # for tHandle in theRefs:
        #     tItem = SHARED.project.tree[tHandle]
        #     if tItem is not None:
        #         theList.append("<a href='%s#%s' %s>%s</a>" % (
        #             tHandle, theRefs[tHandle], self.linkStyle, tItem.itemName
        #         ))
        return

# END Class _ViewPanelBackRefs


class _ViewPanelKeyWords(QWidget):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        return

# END Class _ViewPanelRefs
