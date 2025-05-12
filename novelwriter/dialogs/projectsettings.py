"""
novelWriter – GUI Project Settings
==================================

File History:
Created:   2018-09-29 [0.0.1] GuiProjectSettings
Rewritten: 2024-01-26 [2.3b1] GuiProjectSettings

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

import csv
import logging

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QCloseEvent, QColor
from PyQt6.QtWidgets import (
    QAbstractItemView, QApplication, QColorDialog, QDialogButtonBox,
    QFileDialog, QGridLayout, QHBoxLayout, QLineEdit, QMenu, QStackedWidget,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import formatFileFilter, qtAddAction, qtLambda, simplified
from novelwriter.constants import nwLabels, trConst
from novelwriter.core.status import NWStatus, StatusEntry
from novelwriter.enum import nwStatusShape
from novelwriter.extensions.configlayout import NColorLabel, NFixedPage, NScrollableForm
from novelwriter.extensions.modified import NComboBox, NDialog, NIconToolButton
from novelwriter.extensions.pagedsidebar import NPagedSideBar
from novelwriter.extensions.switch import NSwitch
from novelwriter.types import (
    QtDialogCancel, QtDialogSave, QtSizeMinimum, QtSizeMinimumExpanding,
    QtUserRole
)

logger = logging.getLogger(__name__)


class GuiProjectSettings(NDialog):

    PAGE_SETTINGS = 0
    PAGE_STATUS   = 1
    PAGE_IMPORT   = 2
    PAGE_REPLACE  = 3

    newProjectSettingsReady = pyqtSignal()

    def __init__(self, parent: QWidget, gotoPage: int = PAGE_SETTINGS) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiProjectSettings")
        self.setObjectName("GuiProjectSettings")
        self.setWindowTitle(self.tr("Project Settings"))

        options = SHARED.project.options
        self.setMinimumSize(500, 400)
        self.resize(
            options.getInt("GuiProjectSettings", "winWidth", 650),
            options.getInt("GuiProjectSettings", "winHeight", 500),
        )

        # Title
        self.titleLabel = NColorLabel(
            self.tr("Project Settings"), self, color=SHARED.theme.helpText,
            scale=NColorLabel.HEADER_SCALE, indent=4,
        )

        # SideBar
        self.sidebar = NPagedSideBar(self)
        self.sidebar.setLabelColor(SHARED.theme.helpText)
        self.sidebar.setAccessibleName(self.titleLabel.text())
        self.sidebar.addButton(self.tr("Settings"), self.PAGE_SETTINGS)
        self.sidebar.addButton(self.tr("Status"), self.PAGE_STATUS)
        self.sidebar.addButton(self.tr("Importance"), self.PAGE_IMPORT)
        self.sidebar.addButton(self.tr("Auto-Replace"), self.PAGE_REPLACE)
        self.sidebar.buttonClicked.connect(self._sidebarClicked)

        # Buttons
        self.buttonBox = QDialogButtonBox(QtDialogSave | QtDialogCancel, self)
        self.buttonBox.accepted.connect(self._doSave)
        self.buttonBox.rejected.connect(self.reject)

        # Content
        SHARED.project.countStatus()

        self.settingsPage = _SettingsPage(self)
        self.statusPage = _StatusPage(self, True)
        self.importPage = _StatusPage(self, False)
        self.replacePage = _ReplacePage(self)

        self.mainStack = QStackedWidget(self)
        self.mainStack.addWidget(self.settingsPage)
        self.mainStack.addWidget(self.statusPage)
        self.mainStack.addWidget(self.importPage)
        self.mainStack.addWidget(self.replacePage)

        # Assemble
        self.topBox = QHBoxLayout()
        self.topBox.addWidget(self.titleLabel)
        self.topBox.addStretch(1)

        self.mainBox = QHBoxLayout()
        self.mainBox.addWidget(self.sidebar)
        self.mainBox.addWidget(self.mainStack)
        self.mainBox.setContentsMargins(0, 0, 0, 0)

        self.outerBox = QVBoxLayout()
        self.outerBox.addLayout(self.topBox)
        self.outerBox.addLayout(self.mainBox)
        self.outerBox.addWidget(self.buttonBox)
        self.outerBox.setSpacing(8)

        self.setLayout(self.outerBox)
        self.setSizeGripEnabled(True)

        # Jump to Specified Page
        self.sidebar.setSelected(gotoPage)
        self._sidebarClicked(gotoPage)

        logger.debug("Ready: GuiProjectSettings")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiProjectSettings")
        return

    ##
    #  Events
    ##

    def closeEvent(self, event: QCloseEvent) -> None:
        """Capture the user closing the window and save settings."""
        self._saveSettings()
        event.accept()
        self.softDelete()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(int)
    def _sidebarClicked(self, pageId: int) -> None:
        """Process a user request to switch page."""
        if pageId == self.PAGE_SETTINGS:
            self.mainStack.setCurrentWidget(self.settingsPage)
        elif pageId == self.PAGE_STATUS:
            self.mainStack.setCurrentWidget(self.statusPage)
        elif pageId == self.PAGE_IMPORT:
            self.mainStack.setCurrentWidget(self.importPage)
        elif pageId == self.PAGE_REPLACE:
            self.mainStack.setCurrentWidget(self.replacePage)
        return

    @pyqtSlot()
    def _doSave(self) -> None:
        """Save settings and close dialog."""
        project    = SHARED.project
        projName   = self.settingsPage.projName.text()
        projAuthor = self.settingsPage.projAuthor.text()
        projLang   = self.settingsPage.projLang.currentData()
        spellLang  = self.settingsPage.spellLang.currentData()
        doBackup   = not self.settingsPage.noBackup.isChecked()

        project.data.setName(projName)
        project.data.setAuthor(projAuthor)
        project.data.setDoBackup(doBackup)
        project.data.setSpellLang(spellLang)
        project.setProjectLang(projLang)

        if self.statusPage.changed:
            logger.debug("Updating status labels")
            project.updateStatus("s", self.statusPage.getNewList())

        if self.importPage.changed:
            logger.debug("Updating importance labels")
            project.updateStatus("i", self.importPage.getNewList())

        if self.replacePage.changed:
            logger.debug("Updating auto-replace settings")
            project.data.setAutoReplace(self.replacePage.getNewList())

        self.newProjectSettingsReady.emit()
        QApplication.processEvents()
        self.close()

        return

    ##
    #  Internal Functions
    ##

    def _saveSettings(self) -> None:
        """Save GUI settings."""
        statusColW  = self.statusPage.columnWidth()
        importColW  = self.importPage.columnWidth()
        replaceColW = self.replacePage.columnWidth()

        logger.debug("Saving State: GuiProjectSettings")
        options = SHARED.project.options
        options.setValue("GuiProjectSettings", "winWidth", self.width())
        options.setValue("GuiProjectSettings", "winHeight", self.height())
        options.setValue("GuiProjectSettings", "statusColW", statusColW)
        options.setValue("GuiProjectSettings", "importColW", importColW)
        options.setValue("GuiProjectSettings", "replaceColW", replaceColW)

        return


class _SettingsPage(NScrollableForm):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        data = SHARED.project.data
        self.setHelpTextStyle(SHARED.theme.helpText)
        self.setRowIndent(0)

        # Project Name
        self.projName = QLineEdit(self)
        self.projName.setMaxLength(200)
        self.projName.setMinimumWidth(200)
        self.projName.setText(data.name)
        self.addRow(
            self.tr("Project name"), self.projName,
            self.tr("Changing this will affect the backup path."),
            stretch=(3, 2)
        )

        # Project Author
        self.projAuthor = QLineEdit(self)
        self.projAuthor.setMaxLength(200)
        self.projAuthor.setMinimumWidth(200)
        self.projAuthor.setText(data.author)
        self.addRow(
            self.tr("Author(s)"), self.projAuthor,
            self.tr("Only used when building the manuscript."),
            stretch=(3, 2)
        )

        # Project Language
        projLang = data.language or CONFIG.guiLocale
        self.projLang = NComboBox(self)
        self.projLang.setMinimumWidth(200)
        for tag, language in CONFIG.listLanguages(CONFIG.LANG_PROJ):
            self.projLang.addItem(language, tag)
        self.projLang.setCurrentData(projLang, projLang)
        self.addRow(
            self.tr("Project language"), self.projLang,
            self.tr("Only used when building the manuscript."),
            stretch=(3, 2)
        )

        # Spell Check Language
        self.spellLang = NComboBox(self)
        self.spellLang.setMinimumWidth(200)
        self.spellLang.addItem(self.tr("Default"), "None")
        if CONFIG.hasEnchant:
            for tag, language in SHARED.spelling.listDictionaries():
                self.spellLang.addItem(language, tag)
        self.addRow(
            self.tr("Spell check language"), self.spellLang,
            self.tr("Overrides main preferences."),
            stretch=(3, 2)
        )
        if (idx := self.spellLang.findData(data.spellLang)) != -1:
            self.spellLang.setCurrentIndex(idx)

        # Backup on Close
        self.noBackup = NSwitch(self)
        self.noBackup.setChecked(not data.doBackup)
        self.addRow(
            self.tr("Disable backup on close"), self.noBackup,
            self.tr("Overrides main preferences.")
        )

        self.finalise()

        return


class _StatusPage(NFixedPage):

    C_DATA  = 0
    C_LABEL = 0
    C_USAGE = 1

    D_KEY   = QtUserRole
    D_ENTRY = QtUserRole + 1

    def __init__(self, parent: QWidget, isStatus: bool) -> None:
        super().__init__(parent=parent)

        if isStatus:
            self._kind = self.tr("Status")
            self._store = SHARED.project.data.itemStatus
            pageLabel = self.tr("Novel Document Status Levels")
            colSetting = "statusColW"
        else:
            self._kind = self.tr("Importance")
            self._store = SHARED.project.data.itemImport
            pageLabel = self.tr("Project Note Importance Levels")
            colSetting = "importColW"

        wCol0 = SHARED.project.options.getInt("GuiProjectSettings", colSetting, 130)

        self._changed = False
        self._color = QColor(100, 100, 100)
        self._shape = nwStatusShape.SQUARE
        self._icons = {}

        self._iPx = SHARED.theme.baseIconHeight
        iSz = SHARED.theme.baseIconSize

        iColor = self.palette().text().color()

        # Labels
        self.trCountNone = self.tr("Not in use")
        self.trCountOne  = self.tr("Used once")
        self.trCountMore = self.tr("Used by {0} items")
        self.trSelColor  = self.tr("Select Colour")

        # Title
        self.pageTitle = NColorLabel(
            pageLabel, self, color=SHARED.theme.helpText,
            scale=NColorLabel.HEADER_SCALE
        )

        # List Box
        self.listBox = QTreeWidget(self)
        self.listBox.setHeaderLabels([self.tr("Label"), self.tr("Usage")])
        self.listBox.setColumnWidth(self.C_LABEL, wCol0)
        self.listBox.setIndentation(0)
        self.listBox.setAccessibleName(pageLabel)
        self.listBox.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.listBox.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.listBox.itemSelectionChanged.connect(self._onSelectionChanged)

        for key, entry in self._store.iterItems():
            self._addItem(key, StatusEntry.duplicate(entry))

        # List Controls
        self.addButton = NIconToolButton(self, iSz, "add", "green")
        self.addButton.setToolTip(self.tr("Add Label"))
        self.addButton.clicked.connect(self._onItemCreate)

        self.delButton = NIconToolButton(self, iSz, "remove", "red")
        self.delButton.setToolTip(self.tr("Delete Label"))
        self.delButton.clicked.connect(self._onItemDelete)

        self.upButton = NIconToolButton(self, iSz, "chevron_up", "blue")
        self.upButton.setToolTip(self.tr("Move Up"))
        self.upButton.clicked.connect(qtLambda(self._moveItem, -1))

        self.downButton = NIconToolButton(self, iSz, "chevron_down", "blue")
        self.downButton.setToolTip(self.tr("Move Down"))
        self.downButton.clicked.connect(qtLambda(self._moveItem, 1))

        self.importButton = NIconToolButton(self, iSz, "import", "green")
        self.importButton.setToolTip(self.tr("Import Labels"))
        self.importButton.clicked.connect(self._importLabels)

        self.exportButton = NIconToolButton(self, iSz, "export", "blue")
        self.exportButton.setToolTip(self.tr("Export Labels"))
        self.exportButton.clicked.connect(self._exportLabels)

        # Edit Form
        self.labelText = QLineEdit(self)
        self.labelText.setMaxLength(40)
        self.labelText.setPlaceholderText(self.tr("Select item to edit"))
        self.labelText.setEnabled(False)
        self.labelText.textEdited.connect(self._onNameEdit)

        buttonStyle = (
            "QToolButton {padding: 0 4px;} "
            "QToolButton::menu-indicator {image: none;}"
        )

        self.colorButton = NIconToolButton(self, iSz)
        self.colorButton.setToolTip(self.tr("Colour"))
        self.colorButton.setSizePolicy(QtSizeMinimum, QtSizeMinimumExpanding)
        self.colorButton.setStyleSheet(buttonStyle)
        self.colorButton.setEnabled(False)
        self.colorButton.clicked.connect(self._onColorSelect)

        def buildMenu(menu: QMenu | None, items: dict[nwStatusShape, str]) -> None:
            if menu is not None:
                for shape, label in items.items():
                    icon = NWStatus.createIcon(self._iPx, iColor, shape)
                    action = qtAddAction(menu, trConst(label))
                    action.setIcon(icon)
                    action.triggered.connect(qtLambda(self._selectShape, shape))
                    menu.addAction(action)
                    self._icons[shape] = icon

        self.shapeMenu = QMenu(self)
        buildMenu(self.shapeMenu, nwLabels.SHAPES_PLAIN)
        buildMenu(self.shapeMenu.addMenu(self.tr("Circles ...")), nwLabels.SHAPES_CIRCLE)
        buildMenu(self.shapeMenu.addMenu(self.tr("Bars ...")), nwLabels.SHAPES_BARS)
        buildMenu(self.shapeMenu.addMenu(self.tr("Blocks ...")), nwLabels.SHAPES_BLOCKS)

        self.shapeButton = NIconToolButton(self, iSz)
        self.shapeButton.setMenu(self.shapeMenu)
        self.shapeButton.setToolTip(self.tr("Shape"))
        self.shapeButton.setSizePolicy(QtSizeMinimum, QtSizeMinimumExpanding)
        self.shapeButton.setStyleSheet(buttonStyle)
        self.shapeButton.setEnabled(False)

        # Assemble
        self.listControls = QVBoxLayout()
        self.listControls.addWidget(self.addButton)
        self.listControls.addWidget(self.delButton)
        self.listControls.addWidget(self.upButton)
        self.listControls.addWidget(self.downButton)
        self.listControls.addStretch(1)
        self.listControls.addWidget(self.importButton)
        self.listControls.addWidget(self.exportButton)

        self.editBox = QHBoxLayout()
        self.editBox.addWidget(self.labelText, 1)
        self.editBox.addWidget(self.colorButton, 0)
        self.editBox.addWidget(self.shapeButton, 0)

        self.innerBox = QGridLayout()
        self.innerBox.addWidget(self.listBox, 0, 0)
        self.innerBox.addLayout(self.listControls, 0, 1)
        self.innerBox.addLayout(self.editBox, 1, 0)
        self.innerBox.setRowStretch(0, 1)
        self.innerBox.setColumnStretch(0, 1)

        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.pageTitle, 0)
        self.outerBox.addLayout(self.innerBox, 1)

        self.setCentralLayout(self.outerBox)
        self._setButtonIcons()

        return

    @property
    def changed(self) -> bool:
        """The user changed these settings."""
        return self._changed

    ##
    #  Methods
    ##

    def getNewList(self) -> list[tuple[str | None, StatusEntry]]:
        """Return list of entries."""
        if self._changed:
            update = []
            for n in range(self.listBox.topLevelItemCount()):
                if item := self.listBox.topLevelItem(n):
                    key = item.data(self.C_DATA, self.D_KEY)
                    entry = item.data(self.C_DATA, self.D_ENTRY)
                    update.append((key, entry))
            return update
        return []

    def columnWidth(self) -> int:
        """Return the size of the header column."""
        return self.listBox.columnWidth(0)

    ##
    #  Private Slots
    ##

    @pyqtSlot(str)
    def _onNameEdit(self, text: str) -> None:
        """Update the status label text."""
        if item := self._getSelectedItem():
            name = simplified(text)
            entry: StatusEntry = item.data(self.C_DATA, self.D_ENTRY)
            entry.name = name
            item.setText(self.C_LABEL, name)
            self._changed = True
        return

    @pyqtSlot()
    def _onColorSelect(self) -> None:
        """Open a dialog to select the status icon colour."""
        if (color := QColorDialog.getColor(self._color, self, self.trSelColor)).isValid():
            self._color = color
            self._setButtonIcons()
            self._updateIcon()
        return

    @pyqtSlot()
    def _onItemCreate(self) -> None:
        """Create a new status item."""
        color = QColor(100, 100, 100)
        shape = nwStatusShape.SQUARE
        icon = NWStatus.createIcon(self._iPx, color, shape)
        self._addItem(None, StatusEntry(self.tr("New Item"), color, shape, icon, 0))
        self._changed = True
        return

    @pyqtSlot()
    def _onItemDelete(self) -> None:
        """Delete a status item."""
        if item := self._getSelectedItem():
            iRow = self.listBox.indexOfTopLevelItem(item)
            entry: StatusEntry = item.data(self.C_DATA, self.D_ENTRY)
            if entry.count > 0:
                SHARED.error(self.tr("Cannot delete a status item that is in use."))
            else:
                self.listBox.takeTopLevelItem(iRow)
                self._changed = True
        return

    @pyqtSlot()
    def _onSelectionChanged(self) -> None:
        """Extract the info of a selected item and populate the settings
        boxes and button. If no item is selected, clear the form.
        """
        if item := self._getSelectedItem():
            entry: StatusEntry = item.data(self.C_DATA, self.D_ENTRY)
            self._color = entry.color
            self._shape = entry.shape
            self._setButtonIcons()

            self.labelText.setText(entry.name)
            self.labelText.selectAll()
            self.labelText.setFocus()

            self.labelText.setEnabled(True)
            self.colorButton.setEnabled(True)
            self.shapeButton.setEnabled(True)
        else:
            self._color = QColor(100, 100, 100)
            self._shape = nwStatusShape.SQUARE
            self._setButtonIcons()
            self.labelText.setText("")

            self.labelText.setEnabled(False)
            self.colorButton.setEnabled(False)
            self.shapeButton.setEnabled(False)
        return

    @pyqtSlot()
    def _importLabels(self) -> None:
        """Import labels from file."""
        if path := QFileDialog.getOpenFileName(
            self, self.tr("Import File"),
            str(CONFIG.homePath()), filter=formatFileFilter(["*.csv", "*"]),
        )[0]:
            try:
                with open(path, mode="r", encoding="utf-8") as fo:
                    for row in csv.reader(fo):
                        if entry := self._store.fromRaw(row):
                            self._addItem(None, entry)
                            self._changed = True
            except Exception as exc:
                SHARED.error("Could not read file.", exc=exc)
                return
        return

    @pyqtSlot()
    def _exportLabels(self) -> None:
        """Export labels to file."""
        name = f"{SHARED.project.data.fileSafeName} - {self._kind}.csv"
        if path := QFileDialog.getSaveFileName(
            self, self.tr("Export File"), str(CONFIG.homePath() / name),
        )[0]:
            try:
                path = Path(path).with_suffix(".csv")
                with open(path, mode="w", encoding="utf-8") as fo:
                    writer = csv.writer(fo)
                    for n in range(self.listBox.topLevelItemCount()):
                        if item := self.listBox.topLevelItem(n):
                            entry: StatusEntry = item.data(self.C_DATA, self.D_ENTRY)
                            writer.writerow([entry.shape.name, entry.color.name(), entry.name])
            except Exception as exc:
                SHARED.error("Could not write file.", exc=exc)
        return

    ##
    #  Internal Functions
    ##

    def _selectShape(self, shape: nwStatusShape) -> None:
        """Set the current shape."""
        self._shape = shape
        self._setButtonIcons()
        self._updateIcon()
        return

    def _updateIcon(self) -> None:
        """Apply changes made to a status icon."""
        if item := self._getSelectedItem():
            icon = NWStatus.createIcon(self._iPx, self._color, self._shape)
            entry: StatusEntry = item.data(self.C_DATA, self.D_ENTRY)
            entry.color = self._color
            entry.shape = self._shape
            entry.icon = icon
            item.setIcon(self.C_LABEL, icon)
            self._changed = True
        return

    def _addItem(self, key: str | None, entry: StatusEntry) -> None:
        """Add a status item to the list."""
        item = QTreeWidgetItem()
        item.setText(self.C_LABEL, entry.name)
        item.setIcon(self.C_LABEL, entry.icon)
        item.setText(self.C_USAGE, self._usageString(entry.count))
        item.setData(self.C_DATA, self.D_KEY, key)
        item.setData(self.C_DATA, self.D_ENTRY, entry)
        self.listBox.addTopLevelItem(item)
        return

    def _moveItem(self, step: int) -> None:
        """Move and item up or down step."""
        if item := self._getSelectedItem():
            tIdx = self.listBox.indexOfTopLevelItem(item)
            nItm = self.listBox.topLevelItemCount()
            nIdx = tIdx + step
            if (0 <= nIdx < nItm) and (cItem := self.listBox.takeTopLevelItem(tIdx)):
                self.listBox.insertTopLevelItem(nIdx, cItem)
                self.listBox.clearSelection()
                cItem.setSelected(True)
                self._changed = True
        return

    def _getSelectedItem(self) -> QTreeWidgetItem | None:
        """Get the currently selected item."""
        if items := self.listBox.selectedItems():
            return items[0]
        return None

    def _usageString(self, count: int) -> str:
        """Generate usage string."""
        if count == 0:
            return self.trCountNone
        elif count == 1:
            return self.trCountOne
        else:
            return self.trCountMore.format(count)

    def _setButtonIcons(self) -> None:
        """Set the colour of the colour button."""
        icon = NWStatus.createIcon(self._iPx, self._color, nwStatusShape.SQUARE)
        self.colorButton.setIcon(icon)
        self.shapeButton.setIcon(self._icons[self._shape])
        return


class _ReplacePage(NFixedPage):

    C_KEY  = 0
    C_REPL = 1

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        self._changed = False

        iSz = SHARED.theme.baseIconSize
        wCol0 = SHARED.project.options.getInt("GuiProjectSettings", "replaceColW", 130)

        # Title
        self.pageTitle = NColorLabel(
            self.tr("Text Auto-Replace for Preview and Build"), self,
            color=SHARED.theme.helpText, scale=NColorLabel.HEADER_SCALE
        )

        # List Box
        self.listBox = QTreeWidget(self)
        self.listBox.setHeaderLabels([self.tr("Keyword"), self.tr("Replace With")])
        self.listBox.setColumnWidth(self.C_KEY, wCol0)
        self.listBox.setIndentation(0)
        self.listBox.setAccessibleName(self.pageTitle.text())
        self.listBox.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.listBox.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.listBox.itemSelectionChanged.connect(self._onSelectionChanged)

        for aKey, aVal in SHARED.project.data.autoReplace.items():
            newItem = QTreeWidgetItem([f"<{aKey}>", aVal])
            self.listBox.addTopLevelItem(newItem)

        self.listBox.sortByColumn(self.C_KEY, Qt.SortOrder.AscendingOrder)
        self.listBox.setSortingEnabled(True)

        # List Controls
        self.addButton = NIconToolButton(self, iSz, "add", "green")
        self.addButton.clicked.connect(self._onEntryCreated)

        self.delButton = NIconToolButton(self, iSz, "remove", "red")
        self.delButton.clicked.connect(self._onEntryDeleted)

        # Edit Form
        self.editKey = QLineEdit(self)
        self.editKey.setPlaceholderText(self.tr("Select item to edit"))
        self.editKey.setEnabled(False)
        self.editKey.setMaxLength(40)
        self.editKey.textEdited.connect(self._onKeyEdit)

        self.editValue = QLineEdit(self)
        self.editValue.setEnabled(False)
        self.editValue.setMaxLength(250)
        self.editValue.textEdited.connect(self._onValueEdit)

        # Assemble
        self.listControls = QVBoxLayout()
        self.listControls.addWidget(self.addButton)
        self.listControls.addWidget(self.delButton)
        self.listControls.addStretch(1)

        self.editBox = QHBoxLayout()
        self.editBox.addWidget(self.editKey, 4)
        self.editBox.addWidget(self.editValue, 5)

        self.mainBox = QVBoxLayout()
        self.mainBox.addWidget(self.listBox, 1)
        self.mainBox.addLayout(self.editBox, 0)

        self.innerBox = QHBoxLayout()
        self.innerBox.addLayout(self.mainBox)
        self.innerBox.addLayout(self.listControls)

        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.pageTitle)
        self.outerBox.addLayout(self.innerBox)

        self.setCentralLayout(self.outerBox)

        return

    @property
    def changed(self) -> bool:
        """The user changed these settings."""
        return self._changed

    ##
    #  Methods
    ##

    def getNewList(self) -> dict[str, str]:
        """Extract the list from the widget."""
        new = {}
        for n in range(self.listBox.topLevelItemCount()):
            if item := self.listBox.topLevelItem(n):
                if key := self._stripKey(item.text(self.C_KEY)):
                    new[key] = item.text(self.C_REPL)
        return new

    def columnWidth(self) -> int:
        """Return the size of the header column."""
        return self.listBox.columnWidth(0)

    ##
    #  Private Slots
    ##

    @pyqtSlot(str)
    def _onKeyEdit(self, text: str) -> None:
        """Update the key text."""
        if (item := self._getSelectedItem()) and (key := self._stripKey(text)):
            item.setText(self.C_KEY, f"<{key}>")
            self._changed = True
        return

    @pyqtSlot(str)
    def _onValueEdit(self, text: str) -> None:
        """Update the value text."""
        if item := self._getSelectedItem():
            item.setText(self.C_REPL, text)
            self._changed = True
        return

    @pyqtSlot()
    def _onSelectionChanged(self) -> None:
        """Extract the details from the selected item and populate the
        edit form.
        """
        if item := self._getSelectedItem():
            self.editKey.setText(self._stripKey(item.text(self.C_KEY)))
            self.editValue.setText(item.text(self.C_REPL))
            self.editKey.setEnabled(True)
            self.editValue.setEnabled(True)
            self.editKey.selectAll()
            self.editKey.setFocus()
        else:
            self.editKey.setText("")
            self.editValue.setText("")
            self.editKey.setEnabled(False)
            self.editValue.setEnabled(False)
        return

    @pyqtSlot()
    def _onEntryCreated(self) -> None:
        """Add a new list entry."""
        key = f"<keyword{self.listBox.topLevelItemCount() + 1:d}>"
        self.listBox.addTopLevelItem(QTreeWidgetItem([key, ""]))
        return

    @pyqtSlot()
    def _onEntryDeleted(self) -> None:
        """Delete the selected entry."""
        if item := self._getSelectedItem():
            self.listBox.takeTopLevelItem(self.listBox.indexOfTopLevelItem(item))
            self._changed = True
        return

    ##
    #  Internal Functions
    ##

    def _getSelectedItem(self) -> QTreeWidgetItem | None:
        """Extract the currently selected item."""
        if items := self.listBox.selectedItems():
            return items[0]
        return None

    def _stripKey(self, key: str) -> str:
        """Clean up the replace key string."""
        return "".join(c for c in key if c.isalnum())
