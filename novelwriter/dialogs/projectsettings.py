"""
novelWriter – GUI Project Settings
==================================

File History:
Created:   2018-09-29 [0.0.1] GuiProjectSettings
Rewritten: 2024-01-26 [2.3b1] GuiProjectSettings

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

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QCloseEvent, QColor
from PyQt5.QtWidgets import (
    QAbstractItemView, QApplication, QColorDialog, QDialogButtonBox,
    QHBoxLayout, QLineEdit, QMenu, QStackedWidget, QToolButton, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import simplified
from novelwriter.constants import nwLabels, trConst
from novelwriter.core.status import NWStatus, StatusEntry
from novelwriter.enum import nwStatusShape
from novelwriter.extensions.configlayout import NColourLabel, NFixedPage, NScrollableForm
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
        self.setMinimumSize(CONFIG.pxInt(500), CONFIG.pxInt(400))
        self.resize(
            CONFIG.pxInt(options.getInt("GuiProjectSettings", "winWidth", CONFIG.pxInt(650))),
            CONFIG.pxInt(options.getInt("GuiProjectSettings", "winHeight", CONFIG.pxInt(500)))
        )

        # Title
        self.titleLabel = NColourLabel(
            self.tr("Project Settings"), self, color=SHARED.theme.helpText,
            scale=NColourLabel.HEADER_SCALE, indent=CONFIG.pxInt(4)
        )

        # SideBar
        self.sidebar = NPagedSideBar(self)
        self.sidebar.setLabelColor(SHARED.theme.helpText)
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
        self.outerBox.setSpacing(CONFIG.pxInt(8))

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
            project.data.itemStatus.update(self.statusPage.getNewList())

        if self.importPage.changed:
            logger.debug("Updating importance labels")
            project.data.itemImport.update(self.importPage.getNewList())

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
        winWidth    = CONFIG.rpxInt(self.width())
        winHeight   = CONFIG.rpxInt(self.height())
        statusColW  = CONFIG.rpxInt(self.statusPage.columnWidth())
        importColW  = CONFIG.rpxInt(self.importPage.columnWidth())
        replaceColW = CONFIG.rpxInt(self.replacePage.columnWidth())

        logger.debug("Saving State: GuiProjectSettings")
        options = SHARED.project.options
        options.setValue("GuiProjectSettings", "winWidth", winWidth)
        options.setValue("GuiProjectSettings", "winHeight", winHeight)
        options.setValue("GuiProjectSettings", "statusColW", statusColW)
        options.setValue("GuiProjectSettings", "importColW", importColW)
        options.setValue("GuiProjectSettings", "replaceColW", replaceColW)

        return


class _SettingsPage(NScrollableForm):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        xW = CONFIG.pxInt(200)
        data = SHARED.project.data
        self.setHelpTextStyle(SHARED.theme.helpText)
        self.setRowIndent(0)

        # Project Name
        self.projName = QLineEdit(self)
        self.projName.setMaxLength(200)
        self.projName.setMinimumWidth(xW)
        self.projName.setText(data.name)
        self.addRow(
            self.tr("Project name"), self.projName,
            self.tr("Changing this will affect the backup path."),
            stretch=(3, 2)
        )

        # Project Author
        self.projAuthor = QLineEdit(self)
        self.projAuthor.setMaxLength(200)
        self.projAuthor.setMinimumWidth(xW)
        self.projAuthor.setText(data.author)
        self.addRow(
            self.tr("Author(s)"), self.projAuthor,
            self.tr("Only used when building the manuscript."),
            stretch=(3, 2)
        )

        # Project Language
        projLang = data.language or CONFIG.guiLocale
        self.projLang = NComboBox(self)
        self.projLang.setMinimumWidth(xW)
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
        self.spellLang.setMinimumWidth(xW)
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
            status = SHARED.project.data.itemStatus
            pageLabel = self.tr("Novel Document Status Levels")
            colSetting = "statusColW"
        else:
            status = SHARED.project.data.itemImport
            pageLabel = self.tr("Project Note Importance Levels")
            colSetting = "importColW"

        wCol0 = CONFIG.pxInt(
            SHARED.project.options.getInt("GuiProjectSettings", colSetting, 130)
        )

        self._changed = False
        self._color = QColor(100, 100, 100)
        self._shape = nwStatusShape.SQUARE
        self._icons = {}

        self._iPx = SHARED.theme.baseIconHeight
        iSz = SHARED.theme.baseIconSize
        bPd = CONFIG.pxInt(4)

        iColor = self.palette().text().color()

        # Labels
        self.trCountNone = self.tr("Not in use")
        self.trCountOne  = self.tr("Used once")
        self.trCountMore = self.tr("Used by {0} items")
        self.trSelColor  = self.tr("Select Colour")

        # Title
        self.pageTitle = NColourLabel(
            pageLabel, self, color=SHARED.theme.helpText,
            scale=NColourLabel.HEADER_SCALE
        )

        # List Box
        self.listBox = QTreeWidget(self)
        self.listBox.setHeaderLabels([self.tr("Label"), self.tr("Usage")])
        self.listBox.setColumnWidth(self.C_LABEL, wCol0)
        self.listBox.setIndentation(0)
        self.listBox.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.listBox.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.listBox.itemSelectionChanged.connect(self._selectionChanged)

        for key, entry in status.iterItems():
            self._addItem(key, StatusEntry.duplicate(entry))

        # List Controls
        self.addButton = NIconToolButton(self, iSz, "add")
        self.addButton.clicked.connect(self._newItem)

        self.delButton = NIconToolButton(self, iSz, "remove")
        self.delButton.clicked.connect(self._delItem)

        self.upButton = NIconToolButton(self, iSz, "up")
        self.upButton.clicked.connect(lambda: self._moveItem(-1))

        self.dnButton = NIconToolButton(self, iSz, "down")
        self.dnButton.clicked.connect(lambda: self._moveItem(1))

        # Edit Form
        self.editName = QLineEdit(self)
        self.editName.setMaxLength(40)
        self.editName.setPlaceholderText(self.tr("Select item to edit"))
        self.editName.setEnabled(False)

        buttonStyle = (
            f"QToolButton {{padding: 0 {bPd}px;}} "
            "QToolButton::menu-indicator {image: none;}"
        )

        self.colorButton = NIconToolButton(self, iSz)
        self.colorButton.setToolTip(self.tr("Colour"))
        self.colorButton.setSizePolicy(QtSizeMinimum, QtSizeMinimumExpanding)
        self.colorButton.setStyleSheet(buttonStyle)
        self.colorButton.setEnabled(False)
        self.colorButton.clicked.connect(self._selectColour)

        def buildMenu(menu: QMenu, items: dict[nwStatusShape, str]) -> None:
            for shape, label in items.items():
                icon = NWStatus.createIcon(self._iPx, iColor, shape)
                action = menu.addAction(icon, trConst(label))
                action.triggered.connect(lambda _, shape=shape: self._selectShape(shape))
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

        self.applyButton = QToolButton(self)
        self.applyButton.setText(self.tr("Apply"))
        self.applyButton.setSizePolicy(QtSizeMinimum, QtSizeMinimumExpanding)
        self.applyButton.setEnabled(False)
        self.applyButton.clicked.connect(self._applyChanges)

        # Assemble
        self.listControls = QVBoxLayout()
        self.listControls.addWidget(self.addButton)
        self.listControls.addWidget(self.delButton)
        self.listControls.addWidget(self.upButton)
        self.listControls.addWidget(self.dnButton)
        self.listControls.addStretch(1)

        self.editBox = QHBoxLayout()
        self.editBox.addWidget(self.editName, 1)
        self.editBox.addWidget(self.colorButton, 0)
        self.editBox.addWidget(self.shapeButton, 0)
        self.editBox.addWidget(self.applyButton, 0)

        self.mainBox = QVBoxLayout()
        self.mainBox.addWidget(self.listBox, 1)
        self.mainBox.addLayout(self.editBox, 0)

        self.innerBox = QHBoxLayout()
        self.innerBox.addLayout(self.mainBox, 1)
        self.innerBox.addLayout(self.listControls, 0)

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

    @pyqtSlot()
    def _selectColour(self) -> None:
        """Open a dialog to select the status icon colour."""
        if (color := QColorDialog.getColor(self._color, self, self.trSelColor)).isValid():
            self._color = color
            self._setButtonIcons()
        return

    @pyqtSlot()
    def _newItem(self) -> None:
        """Create a new status item."""
        color = QColor(100, 100, 100)
        shape = nwStatusShape.SQUARE
        icon = NWStatus.createIcon(self._iPx, color, shape)
        self._addItem(None, StatusEntry(self.tr("New Item"), color, shape, icon, 0))
        self._changed = True
        return

    @pyqtSlot()
    def _delItem(self) -> None:
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
    def _applyChanges(self) -> None:
        """Save changes made to a status item."""
        if item := self._getSelectedItem():
            entry: StatusEntry = item.data(self.C_DATA, self.D_ENTRY)

            name = simplified(self.editName.text())
            icon = NWStatus.createIcon(self._iPx, self._color, self._shape)

            entry.name = name
            entry.color = self._color
            entry.shape = self._shape
            entry.icon = icon

            item.setText(self.C_LABEL, name)
            item.setIcon(self.C_LABEL, icon)

            self._changed = True

        return

    @pyqtSlot()
    def _selectionChanged(self) -> None:
        """Extract the info of a selected item and populate the settings
        boxes and button. If no item is selected, clear the form.
        """
        if item := self._getSelectedItem():
            entry: StatusEntry = item.data(self.C_DATA, self.D_ENTRY)
            self._color = entry.color
            self._shape = entry.shape
            self._setButtonIcons()

            self.editName.setText(entry.name)
            self.editName.selectAll()
            self.editName.setFocus()

            self.editName.setEnabled(True)
            self.colorButton.setEnabled(True)
            self.shapeButton.setEnabled(True)
            self.applyButton.setEnabled(True)

        else:
            self._color = QColor(100, 100, 100)
            self._shape = nwStatusShape.SQUARE
            self._setButtonIcons()
            self.editName.setText("")

            self.editName.setEnabled(False)
            self.colorButton.setEnabled(False)
            self.shapeButton.setEnabled(False)
            self.applyButton.setEnabled(False)
        return

    ##
    #  Internal Functions
    ##

    def _selectShape(self, shape: nwStatusShape) -> None:
        """Set the current shape."""
        self._shape = shape
        self._setButtonIcons()
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

        wCol0 = CONFIG.pxInt(
            SHARED.project.options.getInt("GuiProjectSettings", "replaceColW", 130)
        )

        # Title
        self.pageTitle = NColourLabel(
            self.tr("Text Auto-Replace for Preview and Build"), self,
            color=SHARED.theme.helpText, scale=NColourLabel.HEADER_SCALE
        )

        # List Box
        self.listBox = QTreeWidget(self)
        self.listBox.setHeaderLabels([self.tr("Keyword"), self.tr("Replace With")])
        self.listBox.setColumnWidth(self.C_KEY, wCol0)
        self.listBox.setIndentation(0)
        self.listBox.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.listBox.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.listBox.itemSelectionChanged.connect(self._selectionChanged)

        for aKey, aVal in SHARED.project.data.autoReplace.items():
            newItem = QTreeWidgetItem(["<%s>" % aKey, aVal])
            self.listBox.addTopLevelItem(newItem)

        self.listBox.sortByColumn(self.C_KEY, Qt.SortOrder.AscendingOrder)
        self.listBox.setSortingEnabled(True)

        # List Controls
        self.addButton = NIconToolButton(self, iSz, "add")
        self.addButton.clicked.connect(self._addEntry)

        self.delButton = NIconToolButton(self, iSz, "remove")
        self.delButton.clicked.connect(self._delEntry)

        # Edit Form
        self.editKey = QLineEdit(self)
        self.editKey.setPlaceholderText(self.tr("Select item to edit"))
        self.editKey.setEnabled(False)
        self.editKey.setMaxLength(40)

        self.editValue = QLineEdit(self)
        self.editValue.setEnabled(False)
        self.editValue.setMaxLength(80)

        self.applyButton = QToolButton(self)
        self.applyButton.setText(self.tr("Apply"))
        self.applyButton.setSizePolicy(QtSizeMinimum, QtSizeMinimumExpanding)
        self.applyButton.clicked.connect(self._applyChanges)

        # Assemble
        self.listControls = QVBoxLayout()
        self.listControls.addWidget(self.addButton)
        self.listControls.addWidget(self.delButton)
        self.listControls.addStretch(1)

        self.editBox = QHBoxLayout()
        self.editBox.addWidget(self.editKey, 4)
        self.editBox.addWidget(self.editValue, 5)
        self.editBox.addWidget(self.applyButton, 0)

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
                if key := self._stripNotAllowed(item.text(self.C_KEY)):
                    new[key] = item.text(self.C_REPL)
        return new

    def columnWidth(self) -> int:
        """Return the size of the header column."""
        return self.listBox.columnWidth(0)

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _selectionChanged(self) -> None:
        """Extract the details from the selected item and populate the
        edit form.
        """
        if item := self._getSelectedItem():
            self.editKey.setText(self._stripNotAllowed(item.text(self.C_KEY)))
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
    def _applyChanges(self) -> None:
        """Save the form data into the list widget."""
        if item := self._getSelectedItem():
            key = self._stripNotAllowed(self.editKey.text())
            value = self.editValue.text()
            if key and value:
                item.setText(self.C_KEY, f"<{key}>")
                item.setText(self.C_REPL, value)
                self._changed = True
        return

    @pyqtSlot()
    def _addEntry(self) -> None:
        """Add a new list entry."""
        key = f"<keyword{self.listBox.topLevelItemCount() + 1:d}>"
        self.listBox.addTopLevelItem(QTreeWidgetItem([key, ""]))
        return

    @pyqtSlot()
    def _delEntry(self) -> None:
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

    def _stripNotAllowed(self, key: str) -> str:
        """Clean up the replace key string."""
        return "".join(c for c in key if c.isalnum())
