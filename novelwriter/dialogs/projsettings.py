"""
novelWriter – GUI Project Settings
==================================

File History:
Created: 2018-09-29 [0.0.1]

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

from typing import TYPE_CHECKING

from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import (
    QColorDialog, QComboBox, QDialogButtonBox, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import simplified
from novelwriter.extensions.switch import NSwitch
from novelwriter.extensions.pageddialog import NPagedDialog
from novelwriter.extensions.configlayout import NConfigLayout

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


class GuiProjectSettings(NPagedDialog):

    TAB_MAIN    = 0
    TAB_STATUS  = 1
    TAB_IMPORT  = 2
    TAB_REPLACE = 3

    def __init__(self, mainGui: GuiMain, focusTab: int = TAB_MAIN) -> None:
        super().__init__(parent=mainGui)

        logger.debug("Create: GuiProjectSettings")
        self.setObjectName("GuiProjectSettings")

        self.mainGui = mainGui
        SHARED.project.countStatus()
        self.setWindowTitle(self.tr("Project Settings"))

        wW = CONFIG.pxInt(570)
        wH = CONFIG.pxInt(375)
        pOptions = SHARED.project.options

        self.setMinimumWidth(wW)
        self.setMinimumHeight(wH)
        self.resize(
            CONFIG.pxInt(pOptions.getInt("GuiProjectSettings", "winWidth",  wW)),
            CONFIG.pxInt(pOptions.getInt("GuiProjectSettings", "winHeight", wH))
        )

        self.tabMain    = GuiProjectEditMain(self)
        self.tabStatus  = GuiProjectEditStatus(self, True)
        self.tabImport  = GuiProjectEditStatus(self, False)
        self.tabReplace = GuiProjectEditReplace(self)

        self.addTab(self.tabMain,    self.tr("Settings"))
        self.addTab(self.tabStatus,  self.tr("Status"))
        self.addTab(self.tabImport,  self.tr("Importance"))
        self.addTab(self.tabReplace, self.tr("Auto-Replace"))

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._doSave)
        self.buttonBox.rejected.connect(self._doClose)
        self.addControls(self.buttonBox)

        # Focus Tab
        self._focusTab(focusTab)

        logger.debug("Ready: GuiProjectSettings")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiProjectSettings")
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _doSave(self) -> None:
        """Save settings and close dialog."""
        project    = SHARED.project
        projName   = self.tabMain.editName.text()
        bookTitle  = self.tabMain.editTitle.text()
        bookAuthor = self.tabMain.editAuthor.text()
        projLang   = self.tabMain.projLang.currentData()
        spellLang  = self.tabMain.spellLang.currentData()
        doBackup   = not self.tabMain.doBackup.isChecked()

        project.data.setName(projName)
        project.data.setTitle(bookTitle)
        project.data.setAuthor(bookAuthor)
        project.data.setDoBackup(doBackup)
        project.data.setSpellLang(spellLang)
        project.setProjectLang(projLang)

        if self.tabStatus.colChanged:
            newList, delList = self.tabStatus.getNewList()
            project.setStatusColours(newList, delList)

        if self.tabImport.colChanged:
            newList, delList = self.tabImport.getNewList()
            project.setImportColours(newList, delList)

        if self.tabStatus.colChanged or self.tabImport.colChanged:
            self.mainGui.rebuildTrees()

        if self.tabReplace.arChanged:
            newList = self.tabReplace.getNewList()
            project.data.setAutoReplace(newList)

        self._saveGuiSettings()
        self.accept()

        return

    @pyqtSlot()
    def _doClose(self) -> None:
        """Save settings and close the dialog."""
        self._saveGuiSettings()
        self.reject()
        return

    ##
    #  Internal Functions
    ##

    def _focusTab(self, tab: int) -> None:
        """Change which is the focused tab."""
        if tab == self.TAB_MAIN:
            self.setCurrentWidget(self.tabMain)
        elif tab == self.TAB_STATUS:
            self.setCurrentWidget(self.tabStatus)
        elif tab == self.TAB_IMPORT:
            self.setCurrentWidget(self.tabImport)
        elif tab == self.TAB_REPLACE:
            self.setCurrentWidget(self.tabReplace)
        return

    def _saveGuiSettings(self) -> None:
        """Save GUI settings."""
        winWidth    = CONFIG.rpxInt(self.width())
        winHeight   = CONFIG.rpxInt(self.height())
        replaceColW = CONFIG.rpxInt(self.tabReplace.listBox.columnWidth(0))
        statusColW  = CONFIG.rpxInt(self.tabStatus.listBox.columnWidth(0))
        importColW  = CONFIG.rpxInt(self.tabImport.listBox.columnWidth(0))

        pOptions = SHARED.project.options
        pOptions.setValue("GuiProjectSettings", "winWidth",    winWidth)
        pOptions.setValue("GuiProjectSettings", "winHeight",   winHeight)
        pOptions.setValue("GuiProjectSettings", "replaceColW", replaceColW)
        pOptions.setValue("GuiProjectSettings", "statusColW",  statusColW)
        pOptions.setValue("GuiProjectSettings", "importColW",  importColW)

        return

# END Class GuiProjectSettings


class GuiProjectEditMain(QWidget):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        # The Form
        self.mainForm = NConfigLayout()
        self.mainForm.setHelpTextStyle(SHARED.theme.helpText)
        self.setLayout(self.mainForm)

        self.mainForm.addGroupLabel(self.tr("Project Settings"))

        xW = CONFIG.pxInt(250)
        pData = SHARED.project.data

        self.editName = QLineEdit()
        self.editName.setMaxLength(200)
        self.editName.setMaximumWidth(xW)
        self.editName.setText(pData.name)
        self.mainForm.addRow(
            self.tr("Project name"),
            self.editName,
            self.tr("Should be set only once.")
        )

        self.editTitle = QLineEdit()
        self.editTitle.setMaxLength(200)
        self.editTitle.setMaximumWidth(xW)
        self.editTitle.setText(pData.title)
        self.mainForm.addRow(
            self.tr("Novel title"),
            self.editTitle,
            self.tr("Change whenever you want!")
        )

        self.editAuthor = QLineEdit()
        self.editAuthor.setMaxLength(200)
        self.editAuthor.setMaximumWidth(xW)
        self.editAuthor.setText(pData.author)
        self.mainForm.addRow(
            self.tr("Author(s)"),
            self.editAuthor,
            self.tr("Change whenever you want!")
        )

        self.projLang = QComboBox(self)
        self.projLang.setMaximumWidth(xW)
        for tag, language in CONFIG.listLanguages(CONFIG.LANG_PROJ):
            self.projLang.addItem(language, tag)
        self.mainForm.addRow(
            self.tr("Project language"),
            self.projLang,
            self.tr("Used when building the manuscript.")
        )

        langIdx = 0
        if pData.language is not None:
            langIdx = self.projLang.findData(pData.language)
        if langIdx == -1:
            langIdx = self.projLang.findData("en_GB")
        if langIdx != -1:
            self.projLang.setCurrentIndex(langIdx)

        self.spellLang = QComboBox(self)
        self.spellLang.setMaximumWidth(xW)
        self.spellLang.addItem(self.tr("Default"), "None")
        if CONFIG.hasEnchant:
            for tag, language in SHARED.spelling.listDictionaries():
                self.spellLang.addItem(language, tag)
        self.mainForm.addRow(
            self.tr("Spell check language"),
            self.spellLang,
            self.tr("Overrides main preferences.")
        )

        langIdx = 0
        if pData.spellLang is not None:
            langIdx = self.spellLang.findData(pData.spellLang)
        if langIdx != -1:
            self.spellLang.setCurrentIndex(langIdx)

        self.doBackup = NSwitch(self)
        self.doBackup.setChecked(not pData.doBackup)
        self.mainForm.addRow(
            self.tr("No backup on close"),
            self.doBackup,
            self.tr("Overrides main preferences.")
        )

        return

# END Class GuiProjectEditMain


class GuiProjectEditStatus(QWidget):

    COL_LABEL = 0
    COL_USAGE = 1

    KEY_ROLE = Qt.ItemDataRole.UserRole
    COL_ROLE = Qt.ItemDataRole.UserRole + 1
    NUM_ROLE = Qt.ItemDataRole.UserRole + 2

    def __init__(self, parent: QWidget, isStatus: bool) -> None:
        super().__init__(parent=parent)

        if isStatus:
            self.theStatus = SHARED.project.data.itemStatus
            pageLabel = self.tr("Novel File Status Levels")
            colSetting = "statusColW"
        else:
            self.theStatus = SHARED.project.data.itemImport
            pageLabel = self.tr("Note File Importance Levels")
            colSetting = "importColW"

        wCol0 = CONFIG.pxInt(
            SHARED.project.options.getInt("GuiProjectSettings", colSetting, 130)
        )

        self.colDeleted = []
        self.colChanged = False
        self.selColour = QColor(100, 100, 100)

        self.iPx = SHARED.theme.baseIconSize

        # The List
        # ========

        self.listBox = QTreeWidget()
        self.listBox.setHeaderLabels([
            self.tr("Label"), self.tr("Usage"),
        ])
        self.listBox.itemSelectionChanged.connect(self._selectedItem)
        self.listBox.setColumnWidth(self.COL_LABEL, wCol0)
        self.listBox.setIndentation(0)

        for key, entry in self.theStatus.items():
            self._addItem(key, entry["name"], entry["cols"], entry["count"])

        # List Controls
        # =============

        self.addButton = QPushButton(SHARED.theme.getIcon("add"), "")
        self.addButton.clicked.connect(self._newItem)

        self.delButton = QPushButton(SHARED.theme.getIcon("remove"), "")
        self.delButton.clicked.connect(self._delItem)

        self.upButton = QPushButton(SHARED.theme.getIcon("up"), "")
        self.upButton.clicked.connect(lambda: self._moveItem(-1))

        self.dnButton = QPushButton(SHARED.theme.getIcon("down"), "")
        self.dnButton.clicked.connect(lambda: self._moveItem(1))

        # Edit Form
        # =========

        self.editName = QLineEdit()
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
        # ========

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
        self.outerBox.addWidget(QLabel("<b>%s</b>" % pageLabel))
        self.outerBox.addLayout(self.innerBox)

        self.setLayout(self.outerBox)

        return

    def getNewList(self) -> tuple[list, list]:
        """Return list of entries."""
        if self.colChanged:
            newList = []
            for n in range(self.listBox.topLevelItemCount()):
                item = self.listBox.topLevelItem(n)
                if item is not None:
                    newList.append({
                        "key":  item.data(self.COL_LABEL, self.KEY_ROLE),
                        "name": item.text(self.COL_LABEL),
                        "cols": item.data(self.COL_LABEL, self.COL_ROLE),
                    })
            return newList, self.colDeleted

        return [], []

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _selectColour(self) -> None:
        """Open a dialog to select the status icon colour."""
        if self.selColour is not None:
            newCol = QColorDialog.getColor(
                self.selColour, self, self.tr("Select Colour")
            )
            if newCol.isValid():
                self.selColour = newCol
                pixmap = QPixmap(self.iPx, self.iPx)
                pixmap.fill(newCol)
                self.colButton.setIcon(QIcon(pixmap))
                self.colButton.setIconSize(pixmap.rect().size())
        return

    @pyqtSlot()
    def _newItem(self) -> None:
        """Create a new status item."""
        self._addItem(None, self.tr("New Item"), (100, 100, 100), 0)
        self.colChanged = True
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
                self.colDeleted.append(selItem.data(self.COL_LABEL, self.KEY_ROLE))
                self.colChanged = True
        return

    @pyqtSlot()
    def _saveItem(self) -> None:
        """Save changes made to a status item."""
        selItem = self._getSelectedItem()
        if isinstance(selItem, QTreeWidgetItem):
            selItem.setText(self.COL_LABEL, simplified(self.editName.text()))
            selItem.setIcon(self.COL_LABEL, self.colButton.icon())
            selItem.setData(self.COL_LABEL, self.COL_ROLE, (
                self.selColour.red(), self.selColour.green(), self.selColour.blue()
            ))
            self.colChanged = True
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
            self.selColour = QColor(*cols)
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
            self.selColour = QColor(100, 100, 100)
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
                 cols: tuple[int, int, int], count: int) -> None:
        """Add a status item to the list."""
        pixmap = QPixmap(self.iPx, self.iPx)
        pixmap.fill(QColor(*cols))

        item = QTreeWidgetItem()
        item.setText(self.COL_LABEL, name)
        item.setIcon(self.COL_LABEL, QIcon(pixmap))
        item.setData(self.COL_LABEL, self.KEY_ROLE, key)
        item.setData(self.COL_LABEL, self.COL_ROLE, cols)
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
        self.colChanged = True

        return

    def _getSelectedItem(self) -> QTreeWidgetItem | None:
        """Get the currently selected item."""
        selItem = self.listBox.selectedItems()
        if len(selItem) > 0:
            return selItem[0]
        return None

    def _usageString(self, nUse: int) -> str:
        """Generate usage string."""
        if nUse == 0:
            return self.tr("Not in use")
        elif nUse == 1:
            return self.tr("Used once")
        else:
            return self.tr("Used by {0} items").format(nUse)

# END Class GuiProjectEditStatus


class GuiProjectEditReplace(QWidget):

    COL_KEY  = 0
    COL_REPL = 1

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        self.arChanged = False

        wCol0 = CONFIG.pxInt(
            SHARED.project.options.getInt("GuiProjectSettings", "replaceColW", 130)
        )
        pageLabel = self.tr("Text Replace List for Preview and Export")

        # List Box
        # ========

        self.listBox = QTreeWidget()
        self.listBox.setHeaderLabels([
            self.tr("Keyword"),
            self.tr("Replace With"),
        ])
        self.listBox.itemSelectionChanged.connect(self._selectedItem)
        self.listBox.setColumnWidth(self.COL_KEY, wCol0)
        self.listBox.setIndentation(0)

        for aKey, aVal in SHARED.project.data.autoReplace.items():
            newItem = QTreeWidgetItem(["<%s>" % aKey, aVal])
            self.listBox.addTopLevelItem(newItem)

        self.listBox.sortByColumn(self.COL_KEY, Qt.AscendingOrder)
        self.listBox.setSortingEnabled(True)

        # List Controls
        # =============

        self.addButton = QPushButton(SHARED.theme.getIcon("add"), "")
        self.addButton.clicked.connect(self._addEntry)

        self.delButton = QPushButton(SHARED.theme.getIcon("remove"), "")
        self.delButton.clicked.connect(self._delEntry)

        # Edit Form
        # =========

        self.editKey = QLineEdit()
        self.editKey.setPlaceholderText(self.tr("Select item to edit"))
        self.editKey.setEnabled(False)
        self.editKey.setMaxLength(40)

        self.editValue = QLineEdit()
        self.editValue.setEnabled(False)
        self.editValue.setMaxLength(80)

        self.saveButton = QPushButton(self.tr("Save"))
        self.saveButton.clicked.connect(self._saveEntry)

        # Assemble
        # ========

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
        self.outerBox.addWidget(QLabel("<b>%s</b>" % pageLabel))
        self.outerBox.addLayout(self.innerBox)

        self.setLayout(self.outerBox)

        return

    def getNewList(self) -> dict:
        """Extract the list from the widget."""
        new = {}
        for n in range(self.listBox.topLevelItemCount()):
            tItem = self.listBox.topLevelItem(n)
            if tItem is not None:
                aKey = self._stripNotAllowed(tItem.text(0))
                aVal = tItem.text(1)
                if len(aKey) > 0:
                    new[aKey] = aVal
        return new

    ##
    #  Internal Functions
    ##

    def _selectedItem(self) -> bool:
        """Extract the details from the selected item and populate the
        edit form.
        """
        selItem = self._getSelectedItem()
        if selItem is None:
            return False
        editKey = self._stripNotAllowed(selItem.text(0))
        editVal = selItem.text(1)
        self.editKey.setText(editKey)
        self.editValue.setText(editVal)
        self.editKey.setEnabled(True)
        self.editValue.setEnabled(True)
        self.editKey.selectAll()
        self.editKey.setFocus()
        return True

    def _saveEntry(self) -> None:
        """Save the form data into the list widget."""
        selItem = self._getSelectedItem()
        if selItem:
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
                self.arChanged = True
        return

    def _addEntry(self) -> None:
        """Add a new list entry."""
        saveKey = "<keyword%d>" % (self.listBox.topLevelItemCount() + 1)
        newVal  = ""
        newItem = QTreeWidgetItem([saveKey, newVal])
        self.listBox.addTopLevelItem(newItem)
        return

    def _delEntry(self) -> None:
        """Delete the selected entry."""
        selItem = self._getSelectedItem()
        if selItem:
            self.listBox.takeTopLevelItem(self.listBox.indexOfTopLevelItem(selItem))
            self.arChanged = True
        return

    def _getSelectedItem(self) -> QTreeWidgetItem | None:
        """Extract the currently selected item."""
        selItem = self.listBox.selectedItems()
        if len(selItem) == 0:
            return None
        return selItem[0]

    def _stripNotAllowed(self, key: str) -> str:
        """Clean up the replace key string."""
        result = ""
        for c in key:
            if c.isalnum():
                result += c
        return result

# END Class GuiProjectEditReplace
