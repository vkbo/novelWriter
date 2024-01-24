"""
novelWriter – GUI Novel Info
============================

File History:
Created: 2024-01-18 [2.3b1] GuiNovelDetails

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
from PyQt5.QtCore import pyqtSlot

from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import (
    QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout, QLabel, QStackedWidget, QVBoxLayout,
    QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import formatTime
from novelwriter.extensions.configlayout import NColourLabel
from novelwriter.extensions.novelselector import NovelSelector
from novelwriter.extensions.pagedsidebar import NPagedSideBar

logger = logging.getLogger(__name__)


class GuiNovelDetails(QDialog):

    PAGE_OVERVIEW = 1
    PAGE_CONTENTS = 2

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiNovelDetails")
        self.setObjectName("GuiNovelDetails")
        self.setWindowTitle(self.tr("Novel Details"))

        wW = CONFIG.pxInt(500)
        wH = CONFIG.pxInt(400)
        options = SHARED.project.options

        self.setMinimumSize(wW, wH)
        self.resize(
            CONFIG.pxInt(options.getInt("GuiNovelDetails", "winWidth", wW)),
            CONFIG.pxInt(options.getInt("GuiNovelDetails", "winHeight", wH))
        )

        # Title
        self.titleLabel = NColourLabel(
            self.tr("Novel Details"), SHARED.theme.helpText, parent=self, scale=1.25
        )
        self.titleLabel.setIndent(CONFIG.pxInt(4))

        # Novel Selector
        self.novelSelector = NovelSelector(self)
        self.novelSelector.refreshNovelList()

        # SideBar
        self.sidebar = NPagedSideBar(self)
        self.sidebar.setLabelColor(SHARED.theme.helpText)
        self.sidebar.addButton(self.tr("Overview"), self.PAGE_OVERVIEW)
        self.sidebar.addButton(self.tr("Contents"), self.PAGE_CONTENTS)
        self.sidebar.setSelected(self.PAGE_OVERVIEW)
        self.sidebar.buttonClicked.connect(self._sidebarClicked)

        # Content
        self.overviewPage = _OverviewPage(self)

        self.mainStack = QStackedWidget(self)
        self.mainStack.addWidget(self.overviewPage)

        # Buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        self.buttonBox.rejected.connect(self.close)

        # Assemble
        self.topBox = QHBoxLayout()
        self.topBox.addWidget(self.titleLabel)
        self.topBox.addStretch(1)
        self.topBox.addWidget(self.novelSelector, 1)

        self.mainBox = QHBoxLayout()
        self.mainBox.addWidget(self.sidebar)
        self.mainBox.addWidget(self.mainStack)
        self.mainBox.setContentsMargins(0, 0, 0, 0)

        self.outerBox = QVBoxLayout()
        self.outerBox.addLayout(self.topBox)
        self.outerBox.addLayout(self.mainBox)
        self.outerBox.addWidget(self.buttonBox)
        self.outerBox.setSpacing(CONFIG.pxInt(8))

        self.setLayout(self.outerBox)
        self.setSizeGripEnabled(True)

        logger.debug("Ready: GuiNovelDetails")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiNovelDetails")
        return

    ##
    #  Methods
    ##

    def updateValues(self) -> None:
        """Load the dialogs initial values."""
        self.overviewPage.updateProjectData()
        return

    ##
    #  Events
    ##

    def closeEvent(self, event: QCloseEvent) -> None:
        """Capture the user closing the window and save settings."""
        self._saveSettings()
        event.accept()
        self.deleteLater()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(int)
    def _sidebarClicked(self, pageId: int) -> None:
        """Process a user request to switch page."""
        if pageId == self.PAGE_OVERVIEW:
            self.mainStack.setCurrentWidget(self.overviewPage)
        return

    ##
    #  Internal Functions
    ##

    def _saveSettings(self) -> None:
        """Save the user GUI settings."""
        winWidth  = CONFIG.rpxInt(self.width())
        winHeight = CONFIG.rpxInt(self.height())

        logger.debug("Saving State: GuiNovelDetails")
        options = SHARED.project.options
        options.setValue("GuiNovelDetails", "winWidth", winWidth)
        options.setValue("GuiNovelDetails", "winHeight", winHeight)
        return

# END Class GuiNovelDetails


class _OverviewPage(QWidget):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        mPx = CONFIG.pxInt(8)
        sPx = CONFIG.pxInt(16)
        hPx = CONFIG.pxInt(24)
        vPx = CONFIG.pxInt(4)

        # Project Info
        self.projLabel = NColourLabel(self.tr("Project"), SHARED.theme.helpText, self, 1.5)

        self.projName = QLabel("", self)
        self.projWords = QLabel("", self)
        self.projRevisions = QLabel("", self)
        self.projEditTime = QLabel("", self)

        self.projForm = QFormLayout()
        self.projForm.addRow("<b>%s</b>" % self.tr("Name"), self.projName)
        self.projForm.addRow("<b>%s</b>" % self.tr("Word Count"), self.projWords)
        self.projForm.addRow("<b>%s</b>" % self.tr("Revisions"), self.projRevisions)
        self.projForm.addRow("<b>%s</b>" % self.tr("Editing Time"), self.projEditTime)
        self.projForm.setContentsMargins(mPx, 0, 0, 0)
        self.projForm.setHorizontalSpacing(hPx)
        self.projForm.setVerticalSpacing(vPx)

        # Novel Info
        self.novelLabel = NColourLabel(self.tr("Novel"), SHARED.theme.helpText, self, 1.5)

        self.novelName = QLabel("", self)
        self.novelWords = QLabel("", self)
        self.novelChapters = QLabel("", self)
        self.novelScenes = QLabel("", self)

        self.novelForm = QFormLayout()
        self.novelForm.addRow("<b>%s</b>" % self.tr("Name"), self.novelName)
        self.novelForm.addRow("<b>%s</b>" % self.tr("Word Count"), self.novelWords)
        self.novelForm.addRow("<b>%s</b>" % self.tr("Chapters"), self.novelChapters)
        self.novelForm.addRow("<b>%s</b>" % self.tr("Scenes"), self.novelScenes)
        self.novelForm.setContentsMargins(mPx, 0, 0, 0)
        self.novelForm.setHorizontalSpacing(hPx)
        self.novelForm.setVerticalSpacing(vPx)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.projLabel)
        self.outerBox.addLayout(self.projForm)
        self.outerBox.addWidget(self.novelLabel)
        self.outerBox.addLayout(self.novelForm)
        self.outerBox.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setSpacing(sPx)
        self.outerBox.addStretch(1)

        self.setLayout(self.outerBox)

        return

    ##
    #  Methods
    ##

    def updateProjectData(self) -> None:
        """Load information about the project."""
        project = SHARED.project
        self.projName.setText(project.data.name)
        self.projWords.setText(f"{project.index.getNovelWordCount():n}")
        self.projRevisions.setText(f"{project.data.saveCount:n}")
        self.projEditTime.setText(formatTime(project.currentEditTime))
        return

# END Class _OverviewPage
