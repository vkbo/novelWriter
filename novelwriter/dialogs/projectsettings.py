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

from PyQt5.QtGui import QCloseEvent, QColor, QIcon, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QColorDialog, QDialog, QDialogButtonBox, QHBoxLayout, QLineEdit,
    QPushButton, QStackedWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget, qApp
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import simplified
from novelwriter.extensions.switch import NSwitch
from novelwriter.extensions.modified import NComboBox
from novelwriter.extensions.configlayout import NColourLabel, NFixedPage, NScrollableForm
from novelwriter.extensions.pagedsidebar import NPagedSideBar

logger = logging.getLogger(__name__)


class GuiProjectSettings(QDialog):

    PAGE_SETTINGS = 0
    PAGE_STATUS   = 1
    PAGE_IMPORT   = 2
    PAGE_REPLACE  = 3

    newProjectSettingsReady = pyqtSignal(bool)

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
            self.tr("Project Settings"), SHARED.theme.helpText,
            parent=self, scale=NColourLabel.HEADER_SCALE, indent=CONFIG.pxInt(4)
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
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttonBox.accepted.connect(self._doSave)
        self.buttonBox.rejected.connect(self.close)

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
        self.deleteLater()
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
        doBackup   = not self.settingsPage.doBackup.isChecked()

        project.data.setName(projName)
        project.data.setAuthor(projAuthor)
        project.data.setDoBackup(doBackup)
        project.data.setSpellLang(spellLang)
        project.setProjectLang(projLang)

        rebuildTrees = False

        if self.statusPage.wasChanged:
            newList, delList = self.statusPage.getNewList()
            project.setStatusColours(newList, delList)
            rebuildTrees = True

        if self.importPage.wasChanged:
            newList, delList = self.importPage.getNewList()
            project.setImportColours(newList, delList)
            rebuildTrees = True

        if self.replacePage.wasChanged:
            newList = self.replacePage.getNewList()
            project.data.setAutoReplace(newList)

        self.newProjectSettingsReady.emit(rebuildTrees)
        qApp.processEvents()
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

# END Class GuiProjectSettings


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
        self.projLang = NComboBox(self)
        self.projLang.setMinimumWidth(xW)
        for tag, language in CONFIG.listLanguages(CONFIG.LANG_PROJ):
            self.projLang.addItem(language, tag)
        self.addRow(
            self.tr("Project language"), self.projLang,
            self.tr("Only used when building the manuscript."),
            stretch=(3, 2)
        )
        if (idx := self.projLang.findData(data.language)) != -1:
            self.projLang.setCurrentIndex(idx)

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
        self.doBackup = NSwitch(self)
        self.doBackup.setChecked(not data.doBackup)
        self.addRow(
            self.tr("Disable backup on close"), self.doBackup,
            self.tr("Overrides main preferences.")
        )

        self.finalise()

        return

# END Class _SettingsPage


class _StatusPage(NFixedPage):

    COL_LABEL = 0
    COL_USAGE = 1

    KEY_ROLE = Qt.ItemDataRole.UserRole
    COL_ROLE = Qt.ItemDataRole.UserRole + 1
    NUM_ROLE = Qt.ItemDataRole.UserRole + 2

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
        self._colDeleted = []
        self._selColour = QColor(100, 100, 100)

        self.iPx = SHARED.theme.baseIconSize

        # Title
        self.pageTitle = NColourLabel(
            pageLabel, SHARED.theme.helpText, parent=self,
            scale=NColourLabel.HEADER_SCALE
        )

        # List Box
        self.listBox = QTreeWidget(self)
        self.listBox.setHeaderLabels([self.tr("Label"), self.tr("Usage")])
        self.listBox.itemSelectionChanged.connect(self._selectedItem)
        self.listBox.setColumnWidth(self.COL_LABEL, wCol0)
        self.listBox.setIndentation(0)

        for key, entry in status.items():
            self._addItem(key, entry["name"], entry["cols"], entry["count"])

        # List Controls
        self.addButton = QPushButton(SHARED.theme.getIcon("add"), "", self)
        self.addButton.clicked.connect(self._newItem)

        self.delButton = QPushButton(SHARED.theme.getIcon("remove"), "", self)
        self.delButton.clicked.connect(self._delItem)

        self.upButton = QPushButton(SHARED.theme.getIcon("up"), "", self)
        self.upButton.clicked.connect(lambda: self._moveItem(-1))

        self.dnButton = QPushButton(SHARED.theme.getIcon("down"), "", self)
        self.dnButton.clicked.connect(lambda: self._moveItem(1))

        # Edit Form
        self.editName = QLineEdit(self)
        self.editName.setMaxLength(40)
        self.editName.setPlaceholderText(self.tr("Select item to edit"))
        self.editName.setEnabled(False)

        self.colPixmap = QPixmap(self.iPx, self.iPx)
        self.colPixmap.fill(QColor(100, 100, 100))
        self.colButton = QPushButton(QIcon(self.colPixmap), self.tr("Colour"))
        self.colButton.setIconSize(self.colPixmap.rect().size())
        self.colButton.setEnabled(False)
        self.colButton.clicked.connect(self._selectColour)

        self.saveButton = QPushButton(self.tr("Save"))
        self.saveButton.setEnabled(False)
        self.saveButton.clicked.connect(self._saveItem)

        # Assemble
        self.listControls = QVBoxLayout()
        self.listControls.addWidget(self.addButton)
        self.listControls.addWidget(self.delButton)
        self.listControls.addWidget(self.upButton)
        self.listControls.addWidget(self.dnButton)
        self.listControls.addStretch(1)

        self.editBox = QHBoxLayout()
        self.editBox.addWidget(self.editName)
        self.editBox.addWidget(self.colButton)
        self.editBox.addWidget(self.saveButton)

        self.mainBox = QVBoxLayout()
        self.mainBox.addWidget(self.listBox)
        self.mainBox.addLayout(self.editBox)

        self.innerBox = QHBoxLayout()
        self.innerBox.addLayout(self.mainBox)
        self.innerBox.addLayout(self.listControls)

        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.pageTitle)
        self.outerBox.addLayout(self.innerBox)

        self.setCentralLayout(self.outerBox)

        return

    @property
    def wasChanged(self) -> bool:
        """The user changed these settings."""
        return self._changed

    ##
    #  Methods
    ##

    def getNewList(self) -> tuple[list, list]:
        """Return list of entries."""
        if self._changed:
            newList = []
            for n in range(self.listBox.topLevelItemCount()):
                item = self.listBox.topLevelItem(n)
                if item is not None:
                    newList.append({
                        "key":  item.data(self.COL_LABEL, self.KEY_ROLE),
                        "name": item.text(self.COL_LABEL),
                        "cols": item.data(self.COL_LABEL, self.COL_ROLE),
                    })
            return newList, self._colDeleted
        return [], []

    def columnWidth(self) -> int:
        """Return the size of the header column."""
        return self.listBox.columnWidth(0)

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _selectColour(self) -> None:
        """Open a dialog to select the status icon colour."""
        if self._selColour is not None:
            newCol = QColorDialog.getColor(
                self._selColour, self, self.tr("Select Colour")
            )
            if newCol.isValid():
                self._selColour = newCol
                pixmap = QPixmap(self.iPx, self.iPx)
                pixmap.fill(newCol)
                self.colButton.setIcon(QIcon(pixmap))
                self.colButton.setIconSize(pixmap.rect().size())
        return

    @pyqtSlot()
    def _newItem(self) -> None:
        """Create a new status item."""
        self._addItem(None, self.tr("New Item"), (100, 100, 100), 0)
        self._changed = True
        return

    @pyqtSlot()
    def _delItem(self) -> None:
        """Delete a status item."""
        selItem = self._getSelectedItem()
        if isinstance(selItem, QTreeWidgetItem):
            iRow = self.listBox.indexOfTopLevelItem(selItem)
            if selItem.data(self.COL_LABEL, self.NUM_ROLE) > 0:
                SHARED.error(self.tr("Cannot delete a status item that is in use."))
            else:
                self.listBox.takeTopLevelItem(iRow)
                self._colDeleted.append(selItem.data(self.COL_LABEL, self.KEY_ROLE))
                self._changed = True
        return

    @pyqtSlot()
    def _saveItem(self) -> None:
        """Save changes made to a status item."""
        selItem = self._getSelectedItem()
        if isinstance(selItem, QTreeWidgetItem):
            selItem.setText(self.COL_LABEL, simplified(self.editName.text()))
            selItem.setIcon(self.COL_LABEL, self.colButton.icon())
            selItem.setData(self.COL_LABEL, self.COL_ROLE, (
                self._selColour.red(), self._selColour.green(), self._selColour.blue()
            ))
            self._changed = True
        return

    @pyqtSlot()
    def _selectedItem(self) -> None:
        """Extract the info of a selected item and populate the settings
        boxes and button. If no item is selected, clear the form.
        """
        selItem = self._getSelectedItem()
        if isinstance(selItem, QTreeWidgetItem):
            cols = selItem.data(self.COL_LABEL, self.COL_ROLE)
            name = selItem.text(self.COL_LABEL)
            pixmap = QPixmap(self.iPx, self.iPx)
            pixmap.fill(QColor(*cols))
            self._selColour = QColor(*cols)
            self.editName.setText(name)
            self.colButton.setIcon(QIcon(pixmap))
            self.editName.selectAll()
            self.editName.setFocus()
            self.editName.setEnabled(True)
            self.colButton.setEnabled(True)
            self.saveButton.setEnabled(True)
        else:
            pixmap = QPixmap(self.iPx, self.iPx)
            pixmap.fill(QColor(100, 100, 100))
            self._selColour = QColor(100, 100, 100)
            self.editName.setText("")
            self.colButton.setIcon(QIcon(pixmap))
            self.editName.setEnabled(False)
            self.colButton.setEnabled(False)
            self.saveButton.setEnabled(False)
        return

    ##
    #  Internal Functions
    ##

    def _addItem(self, key: str | None, name: str,
                 colour: tuple[int, int, int], count: int) -> None:
        """Add a status item to the list."""
        pixmap = QPixmap(self.iPx, self.iPx)
        pixmap.fill(QColor(*colour))

        item = QTreeWidgetItem()
        item.setText(self.COL_LABEL, name)
        item.setIcon(self.COL_LABEL, QIcon(pixmap))
        item.setData(self.COL_LABEL, self.KEY_ROLE, key)
        item.setData(self.COL_LABEL, self.COL_ROLE, colour)
        item.setData(self.COL_LABEL, self.NUM_ROLE, count)
        item.setText(self.COL_USAGE, self._usageString(count))

        self.listBox.addTopLevelItem(item)

        return

    def _moveItem(self, step: int) -> None:
        """Move and item up or down step."""
        selItem = self._getSelectedItem()
        if selItem is None:
            return

        tIndex = self.listBox.indexOfTopLevelItem(selItem)
        nChild = self.listBox.topLevelItemCount()
        nIndex = tIndex + step
        if nIndex < 0 or nIndex >= nChild:
            return

        cItem = self.listBox.takeTopLevelItem(tIndex)
        self.listBox.insertTopLevelItem(nIndex, cItem)
        self.listBox.clearSelection()

        if cItem is not None:
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
            return self.tr("Not in use")
        elif count == 1:
            return self.tr("Used once")
        else:
            return self.tr("Used by {0} items").format(count)

# END Class _StatusPage


class _ReplacePage(NFixedPage):

    COL_KEY  = 0
    COL_REPL = 1

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        self._changed = False

        wCol0 = CONFIG.pxInt(
            SHARED.project.options.getInt("GuiProjectSettings", "replaceColW", 130)
        )

        # Title
        self.pageTitle = NColourLabel(
            self.tr("Text Auto-Replace for Preview and Build"),
            SHARED.theme.helpText, parent=self, scale=NColourLabel.HEADER_SCALE
        )

        # List Box
        self.listBox = QTreeWidget()
        self.listBox.setHeaderLabels([self.tr("Keyword"), self.tr("Replace With")])
        self.listBox.setColumnWidth(self.COL_KEY, wCol0)
        self.listBox.setIndentation(0)
        self.listBox.itemSelectionChanged.connect(self._selectedItem)

        for aKey, aVal in SHARED.project.data.autoReplace.items():
            newItem = QTreeWidgetItem(["<%s>" % aKey, aVal])
            self.listBox.addTopLevelItem(newItem)

        self.listBox.sortByColumn(self.COL_KEY, Qt.AscendingOrder)
        self.listBox.setSortingEnabled(True)

        # List Controls
        self.addButton = QPushButton(SHARED.theme.getIcon("add"), "")
        self.addButton.clicked.connect(self._addEntry)

        self.delButton = QPushButton(SHARED.theme.getIcon("remove"), "")
        self.delButton.clicked.connect(self._delEntry)

        # Edit Form
        self.editKey = QLineEdit(self)
        self.editKey.setPlaceholderText(self.tr("Select item to edit"))
        self.editKey.setEnabled(False)
        self.editKey.setMaxLength(40)

        self.editValue = QLineEdit(self)
        self.editValue.setEnabled(False)
        self.editValue.setMaxLength(80)

        self.saveButton = QPushButton(self.tr("Save"))
        self.saveButton.clicked.connect(self._saveEntry)

        # Assemble
        self.listControls = QVBoxLayout()
        self.listControls.addWidget(self.addButton)
        self.listControls.addWidget(self.delButton)
        self.listControls.addStretch(1)

        self.editBox = QHBoxLayout()
        self.editBox.addWidget(self.editKey, 4)
        self.editBox.addWidget(self.editValue, 5)
        self.editBox.addWidget(self.saveButton, 0)

        self.mainBox = QVBoxLayout()
        self.mainBox.addWidget(self.listBox)
        self.mainBox.addLayout(self.editBox)

        self.innerBox = QHBoxLayout()
        self.innerBox.addLayout(self.mainBox)
        self.innerBox.addLayout(self.listControls)

        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.pageTitle)
        self.outerBox.addLayout(self.innerBox)

        self.setCentralLayout(self.outerBox)

        return

    @property
    def wasChanged(self) -> bool:
        """The user changed these settings."""
        return self._changed

    ##
    #  Methods
    ##

    def getNewList(self) -> dict:
        """Extract the list from the widget."""
        new = {}
        for n in range(self.listBox.topLevelItemCount()):
            if tItem := self.listBox.topLevelItem(n):
                aKey = self._stripNotAllowed(tItem.text(0))
                aVal = tItem.text(1)
                if len(aKey) > 0:
                    new[aKey] = aVal
        return new

    def columnWidth(self) -> int:
        """Return the size of the header column."""
        return self.listBox.columnWidth(0)

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _selectedItem(self) -> None:
        """Extract the details from the selected item and populate the
        edit form.
        """
        if selItem := self._getSelectedItem():
            editKey = self._stripNotAllowed(selItem.text(0))
            editVal = selItem.text(1)
            self.editKey.setText(editKey)
            self.editValue.setText(editVal)
            self.editKey.setEnabled(True)
            self.editValue.setEnabled(True)
            self.editKey.selectAll()
            self.editKey.setFocus()
        return

    @pyqtSlot()
    def _saveEntry(self) -> None:
        """Save the form data into the list widget."""
        if selItem := self._getSelectedItem():
            newKey = self.editKey.text()
            newVal = self.editValue.text()
            saveKey = self._stripNotAllowed(newKey)
            if len(saveKey) > 0 and len(newVal) > 0:
                selItem.setText(self.COL_KEY,  "<%s>" % saveKey)
                selItem.setText(self.COL_REPL, newVal)
                self.editKey.clear()
                self.editValue.clear()
                self.editKey.setEnabled(False)
                self.editValue.setEnabled(False)
                self.listBox.clearSelection()
                self._changed = True
        return

    @pyqtSlot()
    def _addEntry(self) -> None:
        """Add a new list entry."""
        saveKey = "<keyword%d>" % (self.listBox.topLevelItemCount() + 1)
        self.listBox.addTopLevelItem(QTreeWidgetItem([saveKey, ""]))
        return

    @pyqtSlot()
    def _delEntry(self) -> None:
        """Delete the selected entry."""
        if selItem := self._getSelectedItem():
            self.listBox.takeTopLevelItem(self.listBox.indexOfTopLevelItem(selItem))
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

# END Class _ReplacePage
