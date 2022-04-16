"""
novelWriter – GUI Project Settings
==================================
GUI classes for the project settings dialog

File History:
Created: 2018-09-29 [0.0.1]

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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

import logging
import novelwriter

from PyQt5.QtGui import QIcon, QPixmap, QColor, QBrush
from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QLineEdit, QPlainTextEdit, QLabel, QWidget,
    QDialogButtonBox, QPushButton, QColorDialog, QTreeWidget, QTreeWidgetItem,
    QComboBox
)

from novelwriter.enum import nwAlert
from novelwriter.common import simplified
from novelwriter.gui.custom import QSwitch, PagedDialog, QConfigLayout

logger = logging.getLogger(__name__)


class GuiProjectSettings(PagedDialog):

    def __init__(self, theParent):
        PagedDialog.__init__(self, theParent)

        logger.debug("Initialising GuiProjectSettings ...")
        self.setObjectName("GuiProjectSettings")

        self.mainConf   = novelwriter.CONFIG
        self.theParent  = theParent
        self.theProject = theParent.theProject
        self.optState   = theParent.theProject.optState

        self.theProject.countStatus()
        self.setWindowTitle(self.tr("Project Settings"))

        wW = self.mainConf.pxInt(570)
        wH = self.mainConf.pxInt(375)

        self.setMinimumWidth(wW)
        self.setMinimumHeight(wH)
        self.resize(
            self.mainConf.pxInt(self.optState.getInt("GuiProjectSettings", "winWidth",  wW)),
            self.mainConf.pxInt(self.optState.getInt("GuiProjectSettings", "winHeight", wH))
        )

        self.tabMain    = GuiProjectEditMain(self.theParent, self.theProject)
        self.tabStatus  = GuiProjectEditStatus(self.theParent, self.theProject, True)
        self.tabImport  = GuiProjectEditStatus(self.theParent, self.theProject, False)
        self.tabReplace = GuiProjectEditReplace(self.theParent, self.theProject)

        self.addTab(self.tabMain,    self.tr("Settings"))
        self.addTab(self.tabStatus,  self.tr("Status"))
        self.addTab(self.tabImport,  self.tr("Importance"))
        self.addTab(self.tabReplace, self.tr("Auto-Replace"))

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._doSave)
        self.buttonBox.rejected.connect(self._doClose)
        self.addControls(self.buttonBox)

        # Flags
        self.spellChanged = False

        logger.debug("GuiProjectSettings initialisation complete")

        return

    ##
    #  Slots
    ##

    def _doSave(self):
        """Save settings and close dialog.
        """
        logger.verbose("GuiProjectSettings save button clicked")

        projName    = self.tabMain.editName.text()
        bookTitle   = self.tabMain.editTitle.text()
        bookAuthors = self.tabMain.editAuthors.toPlainText()
        spellLang   = self.tabMain.spellLang.currentData()
        doBackup    = not self.tabMain.doBackup.isChecked()

        self.theProject.setProjectName(projName)
        self.theProject.setBookTitle(bookTitle)
        self.theProject.setBookAuthors(bookAuthors)
        self.theProject.setProjBackup(doBackup)

        # Remember this as updating spell dictionary can be expensive
        self.spellChanged = self.theProject.setSpellLang(spellLang)

        if self.tabStatus.colChanged:
            newList, delList = self.tabStatus.getNewList()
            self.theProject.setStatusColours(newList, delList)

        if self.tabImport.colChanged:
            newList, delList = self.tabImport.getNewList()
            self.theProject.setImportColours(newList, delList)

        if self.tabStatus.colChanged or self.tabImport.colChanged:
            self.theParent.rebuildTrees()

        if self.tabReplace.arChanged:
            newList = self.tabReplace.getNewList()
            self.theProject.setAutoReplace(newList)

        self._saveGuiSettings()
        self.accept()

        return

    def _doClose(self):
        """Save settings and close the dialog.
        """
        self._saveGuiSettings()
        self.reject()
        return

    ##
    #  Internal Functions
    ##

    def _saveGuiSettings(self):
        """Save GUI settings.
        """
        winWidth    = self.mainConf.rpxInt(self.width())
        winHeight   = self.mainConf.rpxInt(self.height())
        replaceColW = self.mainConf.rpxInt(self.tabReplace.listBox.columnWidth(0))
        statusColW  = self.mainConf.rpxInt(self.tabStatus.listBox.columnWidth(0))
        importColW  = self.mainConf.rpxInt(self.tabImport.listBox.columnWidth(0))

        self.optState.setValue("GuiProjectSettings", "winWidth",    winWidth)
        self.optState.setValue("GuiProjectSettings", "winHeight",   winHeight)
        self.optState.setValue("GuiProjectSettings", "replaceColW", replaceColW)
        self.optState.setValue("GuiProjectSettings", "statusColW",  statusColW)
        self.optState.setValue("GuiProjectSettings", "importColW",  importColW)

        return

# END Class GuiProjectSettings


class GuiProjectEditMain(QWidget):

    def __init__(self, theParent, theProject):
        QWidget.__init__(self, theParent)

        self.mainConf   = novelwriter.CONFIG
        self.theParent  = theParent
        self.theProject = theProject

        # The Form
        self.mainForm = QConfigLayout()
        self.mainForm.setHelpTextStyle(self.theParent.theTheme.helpText)
        self.setLayout(self.mainForm)

        self.mainForm.addGroupLabel(self.tr("Project Settings"))

        xW = self.mainConf.pxInt(250)
        xH = round(4.8*self.theParent.theTheme.fontPixelSize)

        self.editName = QLineEdit()
        self.editName.setMaxLength(200)
        self.editName.setMaximumWidth(xW)
        self.editName.setText(self.theProject.projName)
        self.mainForm.addRow(
            self.tr("Working title"),
            self.editName,
            self.tr("Should be set only once.")
        )

        self.editTitle = QLineEdit()
        self.editTitle.setMaxLength(200)
        self.editTitle.setMaximumWidth(xW)
        self.editTitle.setText(self.theProject.bookTitle)
        self.mainForm.addRow(
            self.tr("Novel title"),
            self.editTitle,
            self.tr("Change whenever you want!")
        )

        self.editAuthors = QPlainTextEdit()
        self.editAuthors.setMaximumHeight(xH)
        self.editAuthors.setMaximumWidth(xW)
        self.editAuthors.setPlainText("\n".join(self.theProject.bookAuthors))
        self.mainForm.addRow(
            self.tr("Author(s)"),
            self.editAuthors,
            self.tr("One name per line.")
        )

        self.spellLang = QComboBox(self)
        self.spellLang.setMaximumWidth(xW)
        self.spellLang.addItem(self.tr("Default"), "None")
        langAvail = self.theParent.docEditor.spEnchant.listDictionaries()
        for spTag, spProv in langAvail:
            qLocal = QLocale(spTag)
            spLang = qLocal.nativeLanguageName().title()
            self.spellLang.addItem("%s [%s]" % (spLang, spProv), spTag)

        self.mainForm.addRow(
            self.tr("Spell check language"),
            self.spellLang,
            self.tr("Overrides main preferences.")
        )

        spellIdx = 0
        if self.theProject.projSpell is not None:
            spellIdx = self.spellLang.findData(self.theProject.projSpell)
        if spellIdx != -1:
            self.spellLang.setCurrentIndex(spellIdx)

        self.doBackup = QSwitch(self)
        self.doBackup.setChecked(not self.theProject.doBackup)
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

    KEY_ROLE = Qt.UserRole
    COL_ROLE = Qt.UserRole + 1
    NUM_ROLE = Qt.UserRole + 2

    def __init__(self, theParent, theProject, isStatus):
        QWidget.__init__(self, theParent)

        self.mainConf   = novelwriter.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.optState   = theProject.optState
        self.theTheme   = theParent.theTheme

        if isStatus:
            self.theStatus = self.theProject.statusItems
            pageLabel = self.tr("Novel File Status Levels")
            colSetting = "statusColW"
        else:
            self.theStatus = self.theProject.importItems
            pageLabel = self.tr("Note File Importance Levels")
            colSetting = "importColW"

        wCol0 = self.mainConf.pxInt(
            self.optState.getInt("GuiProjectSettings", colSetting, 130)
        )

        self.colDeleted = []
        self.colChanged = False
        self.selColour  = QColor(100, 100, 100)

        self.iPx = self.theTheme.baseIconSize

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

        self.addButton = QPushButton(self.theTheme.getIcon("add"), "")
        self.addButton.clicked.connect(self._newItem)

        self.delButton = QPushButton(self.theTheme.getIcon("remove"), "")
        self.delButton.clicked.connect(self._delItem)

        self.upButton = QPushButton(self.theTheme.getIcon("up"), "")
        self.upButton.clicked.connect(lambda: self._moveItem(-1))

        self.dnButton = QPushButton(self.theTheme.getIcon("down"), "")
        self.dnButton.clicked.connect(lambda: self._moveItem(1))

        # Edit Form
        # =========

        self.editName = QLineEdit()
        self.editName.setMaxLength(40)
        self.editName.setEnabled(False)
        self.editName.setPlaceholderText(self.tr("Select item to edit"))

        self.colPixmap = QPixmap(self.iPx, self.iPx)
        self.colPixmap.fill(QColor(100, 100, 100))
        self.colButton = QPushButton(QIcon(self.colPixmap), self.tr("Colour"))
        self.colButton.setIconSize(self.colPixmap.rect().size())
        self.colButton.clicked.connect(self._selectColour)

        self.saveButton = QPushButton(self.tr("Save"))
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

    def getNewList(self):
        """Return list of entries.
        """
        if self.colChanged:
            newList = []
            for n in range(self.listBox.topLevelItemCount()):
                item = self.listBox.topLevelItem(n)
                newList.append({
                    "key":  item.data(self.COL_LABEL, self.KEY_ROLE),
                    "name": item.text(self.COL_LABEL),
                    "cols": item.data(self.COL_LABEL, self.COL_ROLE),
                })
            return newList, self.colDeleted

        return [], []

    ##
    #  User Actions
    ##

    def _selectColour(self):
        """Open a dialog to select the status icon colour.
        """
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

    def _newItem(self):
        """Create a new status item.
        """
        newItem = self._addItem(None, self.tr("New Item"), (100, 100, 100), 0)
        newItem.setBackground(self.COL_LABEL, QBrush(QColor(0, 255, 0, 70)))
        newItem.setBackground(self.COL_USAGE, QBrush(QColor(0, 255, 0, 70)))
        self.colChanged = True
        return

    def _delItem(self):
        """Delete a status item.
        """
        selItem = self._getSelectedItem()
        if selItem is not None:
            iRow = self.listBox.indexOfTopLevelItem(selItem)
            if selItem.data(self.COL_LABEL, self.NUM_ROLE) > 0:
                self.theParent.makeAlert(self.tr(
                    "Cannot delete a status item that is in use."
                ), nwAlert.ERROR)
            else:
                self.listBox.takeTopLevelItem(iRow)
                self.colDeleted.append(selItem.data(self.COL_LABEL, self.KEY_ROLE))
                self.colChanged = True
        return

    def _saveItem(self):
        """Save changes made to a status item.
        """
        selItem = self._getSelectedItem()
        if selItem is not None:
            selItem.setText(self.COL_LABEL, simplified(self.editName.text()))
            selItem.setIcon(self.COL_LABEL, self.colButton.icon())
            selItem.setData(self.COL_LABEL, self.COL_ROLE, (
                self.selColour.red(), self.selColour.green(), self.selColour.blue()
            ))
            self.editName.setEnabled(False)
            self.colChanged = True

        return

    def _addItem(self, key, name, cols, count):
        """Add a status item to the list.
        """
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

        return item

    def _moveItem(self, step):
        """Move and item up or down step.
        """
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

        cItem.setSelected(True)
        self.colChanged = True

        return

    def _selectedItem(self):
        """Extract the info of a selected item and populate the settings
        boxes and button.
        """
        selItem = self._getSelectedItem()
        if selItem is None:
            return

        cols = selItem.data(self.COL_LABEL, self.COL_ROLE)
        name = selItem.text(self.COL_LABEL)

        pixmap = QPixmap(self.iPx, self.iPx)
        pixmap.fill(QColor(*cols))
        self.selColour = QColor(*cols)
        self.editName.setText(name)
        self.colButton.setIcon(QIcon(pixmap))
        self.editName.setEnabled(True)
        self.editName.selectAll()
        self.editName.setFocus()

        return

    ##
    #  Internal Functions
    ##

    def _getSelectedItem(self):
        """Get the currently selected item.
        """
        selItem = self.listBox.selectedItems()
        if len(selItem) > 0:
            return selItem[0]
        return None

    def _usageString(self, nUse):
        """Generate usage string.
        """
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

    def __init__(self, theParent, theProject):
        QWidget.__init__(self, theParent)

        self.mainConf   = novelwriter.CONFIG
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
        self.theProject = theProject
        self.optState   = theProject.optState
        self.arChanged  = False

        wCol0 = self.mainConf.pxInt(
            self.optState.getInt("GuiProjectSettings", "replaceColW", 130)
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

        for aKey, aVal in self.theProject.autoReplace.items():
            newItem = QTreeWidgetItem(["<%s>" % aKey, aVal])
            self.listBox.addTopLevelItem(newItem)

        self.listBox.sortByColumn(self.COL_KEY, Qt.AscendingOrder)
        self.listBox.setSortingEnabled(True)

        # List Controls
        # =============

        self.addButton = QPushButton(self.theTheme.getIcon("add"), "")
        self.addButton.clicked.connect(self._addEntry)

        self.delButton = QPushButton(self.theTheme.getIcon("remove"), "")
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

    def getNewList(self):
        """Extract the list from the widget.
        """
        newList = {}
        for n in range(self.listBox.topLevelItemCount()):
            tItem = self.listBox.topLevelItem(n)
            aKey = self._stripNotAllowed(tItem.text(0))
            aVal = tItem.text(1)
            if len(aKey) > 0:
                newList[aKey] = aVal

        return newList

    ##
    #  Internal Functions
    ##

    def _selectedItem(self):
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

    def _saveEntry(self):
        """Save the form data into the list widget.
        """
        selItem = self._getSelectedItem()
        if selItem is None:
            return False

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

    def _addEntry(self):
        """Add a new list entry.
        """
        saveKey = "<keyword%d>" % (self.listBox.topLevelItemCount() + 1)
        newVal  = ""
        newItem = QTreeWidgetItem([saveKey, newVal])
        self.listBox.addTopLevelItem(newItem)
        return True

    def _delEntry(self):
        """Delete the selected entry.
        """
        selItem = self._getSelectedItem()
        if selItem is None:
            return False
        self.listBox.takeTopLevelItem(self.listBox.indexOfTopLevelItem(selItem))
        self.arChanged = True
        return True

    def _getSelectedItem(self):
        """Extract the currently selected item.
        """
        selItem = self.listBox.selectedItems()
        if len(selItem) == 0:
            return None
        return selItem[0]

    def _stripNotAllowed(self, theKey):
        """Clean up the replace key string.
        """
        retKey = ""
        for c in theKey:
            if c.isalnum():
                retKey += c
        return retKey

# END Class GuiProjectEditReplace
