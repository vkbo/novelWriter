# -*- coding: utf-8 -*-
"""novelWriter GUI Project Settings

 novelWriter – GUI Project Settings
====================================
 Class holding the project settings dialog

 File History:
 Created: 2018-09-29 [0.0.1]

 This file is a part of novelWriter
 Copyright 2018–2021, Veronica Berglyd Olsen

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

import nw
import logging

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QColor, QBrush
from PyQt5.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QGridLayout, QLineEdit, QPlainTextEdit, QLabel,
    QWidget, QDialogButtonBox, QListWidget, QPushButton, QListWidgetItem,
    QColorDialog, QAbstractItemView, QTreeWidget, QTreeWidgetItem, QComboBox
)

from nw.constants import nwAlert
from nw.gui.custom import QSwitch, PagedDialog, QConfigLayout

logger = logging.getLogger(__name__)

class GuiProjectSettings(PagedDialog):

    def __init__(self, theParent, theProject):
        PagedDialog.__init__(self, theParent)

        logger.debug("Initialising GuiProjectSettings ...")
        self.setObjectName("GuiProjectSettings")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.optState   = theProject.optState

        self.theProject.countStatus()
        self.setWindowTitle("Project Settings")

        wW = self.mainConf.pxInt(570)
        wH = self.mainConf.pxInt(375)

        self.setMinimumWidth(wW)
        self.setMinimumHeight(wH)
        self.resize(
            self.mainConf.pxInt(self.optState.getInt("GuiProjectSettings", "winWidth",  wW)),
            self.mainConf.pxInt(self.optState.getInt("GuiProjectSettings", "winHeight", wH))
        )

        self.tabMain    = GuiProjectEditMain(self.theParent, self.theProject)
        self.tabMeta    = GuiProjectEditMeta(self.theParent, self.theProject)
        self.tabStatus  = GuiProjectEditStatus(self.theParent, self.theProject, True)
        self.tabImport  = GuiProjectEditStatus(self.theParent, self.theProject, False)
        self.tabReplace = GuiProjectEditReplace(self.theParent, self.theProject)

        self.addTab(self.tabMain,    "Settings")
        self.addTab(self.tabMeta,    "Details")
        self.addTab(self.tabStatus,  "Status")
        self.addTab(self.tabImport,  "Importance")
        self.addTab(self.tabReplace, "Auto-Replace")

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._doSave)
        self.buttonBox.rejected.connect(self._doClose)
        self.addControls(self.buttonBox)

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
        self.theProject.setSpellLang(spellLang)
        self.theProject.setProjBackup(doBackup)

        if self.tabStatus.colChanged:
            statusCol = self.tabStatus.getNewList()
            self.theProject.setStatusColours(statusCol)

        if self.tabImport.colChanged:
            importCol = self.tabImport.getNewList()
            self.theProject.setImportColours(importCol)

        if self.tabStatus.colChanged or self.tabImport.colChanged:
            self.theParent.rebuildTree()

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

        self.optState.setValue("GuiProjectSettings", "winWidth",    winWidth)
        self.optState.setValue("GuiProjectSettings", "winHeight",   winHeight)
        self.optState.setValue("GuiProjectSettings", "replaceColW", replaceColW)

        return

# END Class GuiProjectSettings

class GuiProjectEditMain(QWidget):

    def __init__(self, theParent, theProject):
        QWidget.__init__(self, theParent)

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject

        # The Form
        self.mainForm = QConfigLayout()
        self.mainForm.setHelpTextStyle(self.theParent.theTheme.helpText)
        self.setLayout(self.mainForm)

        self.mainForm.addGroupLabel("Project Settings")

        xW = self.mainConf.pxInt(250)
        xH = self.mainConf.pxInt(100)

        self.editName = QLineEdit()
        self.editName.setMaxLength(200)
        self.editName.setFixedWidth(xW)
        self.editName.setText(self.theProject.projName)
        self.mainForm.addRow(
            "Working title",
            self.editName,
            "Should be set only once."
        )

        self.editTitle = QLineEdit()
        self.editTitle.setMaxLength(200)
        self.editTitle.setFixedWidth(xW)
        self.editTitle.setText(self.theProject.bookTitle)
        self.mainForm.addRow(
            "Novel title",
            self.editTitle,
            "Change whenever you want!"
        )

        self.editAuthors = QPlainTextEdit()
        bookAuthors = ""
        for bookAuthor in self.theProject.bookAuthors:
            bookAuthors += bookAuthor+"\n"
        self.editAuthors.setPlainText(bookAuthors)
        self.editAuthors.setFixedHeight(xH)
        self.editAuthors.setFixedWidth(xW)
        self.mainForm.addRow(
            "Author(s)",
            self.editAuthors,
            "One name per line."
        )

        self.spellLang = QComboBox(self)
        theDict = self.theParent.docEditor.theDict
        self.spellLang.addItem("Default", "None")
        if theDict is not None:
            for spTag, spName in theDict.listDictionaries():
                self.spellLang.addItem(spName, spTag)

        self.mainForm.addRow(
            "Spell check language",
            self.spellLang,
            "Overrides main preferences."
        )

        spellIdx = 0
        if self.theProject.projLang is not None:
            spellIdx = self.spellLang.findData(self.theProject.projLang)
        if spellIdx != -1:
            self.spellLang.setCurrentIndex(spellIdx)

        self.doBackup = QSwitch(self)
        self.doBackup.setChecked(not self.theProject.doBackup)
        self.mainForm.addRow(
            "No backup on close",
            self.doBackup,
            "Overrides main preferences."
        )

        return

# END Class GuiProjectEditMain

class GuiProjectEditMeta(QWidget):

    def __init__(self, theParent, theProject):
        QWidget.__init__(self, theParent)

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject

        xInd = self.mainConf.pxInt(8)

        # The Form
        self.mainForm = QGridLayout()
        self.setLayout(self.mainForm)

        self.headLabel = QLabel("<b>Project Details</b>")

        self.nameLabel = QLabel("Working title:")
        self.nameLabel.setIndent(xInd)
        self.nameValue = QLabel(self.theProject.projName)
        self.nameValue.setWordWrap(True)

        self.pathLabel = QLabel("Project path:")
        self.pathLabel.setIndent(xInd)
        self.pathValue = QLabel(self.theProject.projPath)
        self.pathValue.setWordWrap(True)
        self.pathValue.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.pathValue.setCursor(Qt.IBeamCursor)

        self.revLabel = QLabel("Revision count:")
        self.revLabel.setIndent(xInd)
        self.revValue = QLabel(f"{self.theProject.saveCount:n}")

        editHours = self.theProject.editTime/3600
        self.editLabel = QLabel("Edit time:")
        self.editLabel.setIndent(xInd)
        self.editValue = QLabel(f"{editHours:.2f} hours")

        self.statsLabel = QLabel("<b>Project Stats</b>")

        nR, nD, nF = self.theProject.projTree.countTypes()

        self.nRootLabel = QLabel("Root folders:")
        self.nRootLabel.setIndent(xInd)
        self.nRootValue = QLabel(f"{nR:n}")

        self.nDirLabel = QLabel("Folders:")
        self.nDirLabel.setIndent(xInd)
        self.nDirValue = QLabel(f"{nD:n}")

        self.nFileLabel = QLabel("Documents:")
        self.nFileLabel.setIndent(xInd)
        self.nFileValue = QLabel(f"{nF:n}")

        self.wordsLabel = QLabel("Word count:")
        self.wordsLabel.setIndent(xInd)
        self.wordsValue = QLabel(f"{self.theProject.currWCount:n}")

        self.mainForm.addWidget(self.headLabel,  0, 0, 1, 2, Qt.AlignTop)
        self.mainForm.addWidget(self.nameLabel,  1, 0, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.nameValue,  1, 1, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.pathLabel,  2, 0, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.pathValue,  2, 1, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.revLabel,   3, 0, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.revValue,   3, 1, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.editLabel,  4, 0, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.editValue,  4, 1, 1, 1, Qt.AlignTop)

        self.mainForm.addWidget(self.statsLabel, 5, 0, 1, 2, Qt.AlignTop)
        self.mainForm.addWidget(self.nRootLabel, 6, 0, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.nRootValue, 6, 1, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.nDirLabel,  7, 0, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.nDirValue,  7, 1, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.nFileLabel, 8, 0, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.nFileValue, 8, 1, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.wordsLabel, 9, 0, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.wordsValue, 9, 1, 1, 1, Qt.AlignTop)

        self.mainForm.setVerticalSpacing(self.mainConf.pxInt(6))
        self.mainForm.setHorizontalSpacing(self.mainConf.pxInt(12))
        self.mainForm.setColumnStretch(0, 0)
        self.mainForm.setColumnStretch(1, 1)
        self.mainForm.setRowStretch(10, 1)

        return

# END Class GuiProjectEditMeta

class GuiProjectEditStatus(QWidget):

    def __init__(self, theParent, theProject, isStatus):
        QWidget.__init__(self, theParent)

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.theTheme   = theParent.theTheme
        if isStatus:
            self.theStatus = self.theProject.statusItems
        else:
            self.theStatus = self.theProject.importItems

        self.colData    = []
        self.colCounts  = []
        self.colChanged = False
        self.selColour  = None

        self.iPx = self.theTheme.baseIconSize

        self.outerBox = QVBoxLayout()
        self.mainBox  = QHBoxLayout()
        self.mainForm = QVBoxLayout()

        self.listBox = QListWidget()
        self.listBox.setDragDropMode(QAbstractItemView.InternalMove)
        self.listBox.itemSelectionChanged.connect(self._selectedItem)
        self.listBox.model().rowsMoved.connect(self._rowsMoved)

        for iName, iCol, nUse in self.theStatus:
            self._addItem(iName, iCol, iName, nUse)

        self.editName = QLineEdit()
        self.editName.setMaxLength(40)
        self.editName.setEnabled(False)
        self.newButton  = QPushButton("New")
        self.delButton  = QPushButton("Delete")
        self.saveButton = QPushButton("Save")
        self.colPixmap  = QPixmap(self.iPx, self.iPx)
        self.colPixmap.fill(QColor(120, 120, 120))
        self.colButton  = QPushButton(QIcon(self.colPixmap), "Colour")
        self.colButton.setIconSize(self.colPixmap.rect().size())

        self.newButton.clicked.connect(self._newItem)
        self.delButton.clicked.connect(self._delItem)
        self.saveButton.clicked.connect(self._saveItem)
        self.colButton.clicked.connect(self._selectColour)

        self.mainForm.addWidget(self.newButton)
        self.mainForm.addWidget(self.delButton)
        self.mainForm.addStretch(1)
        self.mainForm.addWidget(QLabel("<b>Name</b>"))
        self.mainForm.addWidget(self.editName)
        self.mainForm.addWidget(self.colButton)
        self.mainForm.addStretch(1)
        self.mainForm.addWidget(self.saveButton)

        self.mainBox.addWidget(self.listBox)
        self.mainBox.addLayout(self.mainForm)

        if isStatus:
            self.outerBox.addWidget(QLabel("<b>Novel File Status Levels</b>"))
        else:
            self.outerBox.addWidget(QLabel("<b>Note File Importance Levels</b>"))
        self.outerBox.addLayout(self.mainBox)

        self.setLayout(self.outerBox)

        return

    def getNewList(self):
        if self.colChanged:
            newList = []
            for n in range(self.listBox.count()):
                nItem = self.listBox.item(n)
                nIdx  = nItem.data(Qt.UserRole)
                newList.append(self.colData[nIdx])
            return newList
        return None

    ##
    #  User Actions
    ##

    def _selectColour(self):
        """Open a dialog to select the status icon colour.
        """
        logger.verbose("Item colour button clicked")
        if self.selColour is not None:
            newCol = QColorDialog.getColor(
                self.selColour, self, "Select Colour", QColorDialog.DontUseNativeDialog
            )
            if newCol.isValid():
                self.selColour = newCol
                colPixmap = QPixmap(self.iPx, self.iPx)
                colPixmap.fill(newCol)
                self.colButton.setIcon(QIcon(colPixmap))
                self.colButton.setIconSize(colPixmap.rect().size())
        return

    def _newItem(self):
        """Create a new status item.
        """
        logger.verbose("New item button clicked")
        newItem = self._addItem("New Item", (0, 0, 0), None, 0)
        newItem.setBackground(QBrush(QColor(0, 255, 0, 80)))
        self.colChanged = True
        return

    def _delItem(self):
        """Delete a status item.
        """
        logger.verbose("Delete item button clicked")
        selItem = self._getSelectedItem()
        if selItem is not None:
            iRow   = self.listBox.row(selItem)
            selIdx = selItem.data(Qt.UserRole)
            if self.colCounts[selIdx] == 0:
                self.listBox.takeItem(iRow)
                self.colChanged = True
            else:
                self.theParent.makeAlert(
                    "Cannot delete status item that is in use.", nwAlert.ERROR
                )
        return

    def _saveItem(self):
        """Save changes made to a status item.
        """
        logger.verbose("Save item button clicked")
        selItem = self._getSelectedItem()
        if selItem is not None:
            selIdx = selItem.data(Qt.UserRole)
            self.colData[selIdx] = (
                self.editName.text().strip(),
                self.selColour.red(),
                self.selColour.green(),
                self.selColour.blue(),
                self.colData[selIdx][4]
            )
            selItem.setText("%s [%d]" % (self.colData[selIdx][0], self.colCounts[selIdx]))
            selItem.setIcon(self.colButton.icon())
            self.editName.setEnabled(False)
            self.colChanged = True
        return

    def _addItem(self, iName, iCol, oName, nUse):
        """Add a status item to the list.
        """
        newIcon = QPixmap(self.iPx, self.iPx)
        newIcon.fill(QColor(*iCol))
        newItem = QListWidgetItem()
        newItem.setText("%s [%d]" % (iName, nUse))
        newItem.setIcon(QIcon(newIcon))
        newItem.setData(Qt.UserRole, len(self.colData))
        self.listBox.addItem(newItem)
        self.colData.append((iName, iCol[0], iCol[1], iCol[2], oName))
        self.colCounts.append(nUse)
        return newItem

    def _selectedItem(self):
        """Extract the info of a selected item and populate the settings
        boxes and button.
        """
        logger.verbose("Item selected")
        selItem = self._getSelectedItem()
        if selItem is not None:
            selIdx = selItem.data(Qt.UserRole)
            selVal = self.colData[selIdx]
            self.selColour = QColor(selVal[1], selVal[2], selVal[3])
            newIcon = QPixmap(self.iPx, self.iPx)
            newIcon.fill(self.selColour)
            self.editName.setText(selVal[0])
            self.colButton.setIcon(QIcon(newIcon))
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

    def _rowsMoved(self):
        """A row has been moved, so sett the changed flag.
        """
        logger.verbose("A drag move event occurred")
        self.colChanged = True
        return

# END Class GuiProjectEditStatus

class GuiProjectEditReplace(QWidget):

    def __init__(self, theParent, theProject):
        QWidget.__init__(self, theParent)

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
        self.theProject = theProject
        self.optState   = theProject.optState
        self.arChanged  = False

        self.outerBox  = QVBoxLayout()
        self.bottomBox = QHBoxLayout()

        wCol0 = self.mainConf.pxInt(
            self.optState.getInt("GuiProjectSettings", "replaceColW", 100)
        )
        self.listBox = QTreeWidget()
        self.listBox.setHeaderLabels(["Keyword", "Replace With"])
        self.listBox.itemSelectionChanged.connect(self._selectedItem)
        self.listBox.setColumnWidth(0, wCol0)
        self.listBox.setIndentation(0)

        for aKey, aVal in self.theProject.autoReplace.items():
            newItem = QTreeWidgetItem(["<%s>" % aKey, aVal])
            self.listBox.addTopLevelItem(newItem)

        self.listBox.sortByColumn(0, Qt.AscendingOrder)
        self.listBox.setSortingEnabled(True)

        self.editKey    = QLineEdit()
        self.editValue  = QLineEdit()
        self.saveButton = QPushButton(self.theTheme.getIcon("done"), "")
        self.addButton  = QPushButton(self.theTheme.getIcon("add"), "")
        self.delButton  = QPushButton(self.theTheme.getIcon("remove"), "")
        self.saveButton.setToolTip("Save entry")
        self.addButton.setToolTip("Add new entry")
        self.delButton.setToolTip("Delete selected entry")

        self.editKey.setEnabled(False)
        self.editKey.setMaxLength(40)
        self.editValue.setEnabled(False)
        self.editValue.setMaxLength(80)

        self.saveButton.clicked.connect(self._saveEntry)
        self.addButton.clicked.connect(self._addEntry)
        self.delButton.clicked.connect(self._delEntry)

        self.bottomBox.addWidget(self.editKey, 2)
        self.bottomBox.addWidget(self.editValue, 3)
        self.bottomBox.addWidget(self.saveButton)
        self.bottomBox.addWidget(self.addButton)
        self.bottomBox.addWidget(self.delButton)

        self.outerBox.addWidget(QLabel("<b>Text Replace List for Preview and Export</b>"))
        self.outerBox.addWidget(self.listBox)
        self.outerBox.addLayout(self.bottomBox)
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

        newKey  = self.editKey.text()
        newVal  = self.editValue.text()
        saveKey = self._stripNotAllowed(newKey)

        if len(saveKey) > 0 and len(newVal) > 0:
            selItem.setText(0, "<%s>" % saveKey)
            selItem.setText(1, newVal)
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
