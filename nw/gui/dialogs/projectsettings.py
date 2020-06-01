# -*- coding: utf-8 -*-
"""novelWriter GUI Project Settings

 novelWriter – GUI Project Settings
====================================
 Class holding the project settings dialog

 File History:
 Created: 2018-09-29 [0.0.1]

 This file is a part of novelWriter
 Copyright 2020, Veronica Berglyd Olsen

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
import nw

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QColor, QBrush
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QGridLayout, QLineEdit, QPlainTextEdit,
    QLabel, QWidget, QTabWidget, QDialogButtonBox, QListWidget, QPushButton,
    QListWidgetItem, QColorDialog, QAbstractItemView, QTreeWidget, QCheckBox,
    QTreeWidgetItem
)

from nw.constants import nwAlert
from nw.gui.additions import QSwitch, PagedDialog, QConfigLayout

logger = logging.getLogger(__name__)

class GuiProjectSettings(PagedDialog):

    def __init__(self, theParent, theProject):
        PagedDialog.__init__(self, theParent)

        logger.debug("Initialising GuiProjectSettings ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject

        self.theProject.countStatus()
        self.setWindowTitle("Project Settings")

        self.tabMain    = GuiProjectEditMain(self.theParent, self.theProject)
        self.tabMeta    = GuiProjectEditMeta(self.theParent, self.theProject)
        self.tabStatus  = GuiProjectEditStatus(self.theParent, self.theProject, True)
        self.tabImport  = GuiProjectEditStatus(self.theParent, self.theProject, False)
        self.tabReplace = GuiProjectEditReplace(self.theParent, self.theProject)

        self.addTab(self.tabMain,   "Settings")
        self.addTab(self.tabMeta,   "Details")
        self.addTab(self.tabStatus, "Status")
        self.addTab(self.tabImport, "Importance")
        self.addTab(self.tabReplace,"Auto-Replace")

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._doSave)
        self.buttonBox.rejected.connect(self._doClose)
        self.addControls(self.buttonBox)

        self.show()

        logger.debug("GuiProjectSettings initialisation complete")

        return

    def _doSave(self):
        logger.verbose("GuiProjectSettings save button clicked")

        projName    = self.tabMain.editName.text()
        bookTitle   = self.tabMain.editTitle.text()
        bookAuthors = self.tabMain.editAuthors.toPlainText()
        doBackup    = not self.tabMain.doBackup.isChecked()
        self.theProject.setProjectName(projName)
        self.theProject.setBookTitle(bookTitle)
        self.theProject.setBookAuthors(bookAuthors)
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

        self.close()

        return

    def _doClose(self):
        logger.verbose("GuiProjectSettings close button clicked")
        self.close()
        return

# END Class GuiProjectSettings

class GuiProjectEditMain(QWidget):

    def __init__(self, theParent, theProject):
        QWidget.__init__(self, theParent)

        self.theParent  = theParent
        self.theProject = theProject

        # The Form
        self.mainForm = QConfigLayout()
        self.mainForm.setHelpTextStyle(self.theParent.theTheme.helpText)
        self.setLayout(self.mainForm)

        self.mainForm.addGroupLabel("Project Settings")

        self.editName = QLineEdit()
        self.editName.setMaxLength(200)
        self.editName.setFixedWidth(250)
        self.editName.setText(self.theProject.projName)
        self.mainForm.addRow(
            "Working title",
            self.editName,
            "Should be set only once."
        )

        self.editTitle = QLineEdit()
        self.editTitle.setMaxLength(200)
        self.editTitle.setFixedWidth(250)
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
        self.editAuthors.setFixedHeight(100)
        self.editAuthors.setFixedWidth(250)
        self.mainForm.addRow(
            "Author(s)",
            self.editAuthors,
            "One name per line."
        )

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

        self.theParent  = theParent
        self.theProject = theProject

        # The Form
        self.mainForm = QGridLayout()
        self.setLayout(self.mainForm)

        self.headLabel = QLabel("<b>Project Details</b>")

        self.nameLabel = QLabel("Working title:")
        self.nameLabel.setIndent(8)
        self.nameValue = QLabel(self.theProject.projName)
        self.nameValue.setWordWrap(True)

        self.pathLabel = QLabel("Project path:")
        self.pathLabel.setIndent(8)
        self.pathValue = QLabel(self.theProject.projPath)
        self.pathValue.setWordWrap(True)

        self.revLabel = QLabel("Revision count:")
        self.revLabel.setIndent(8)
        self.revValue = QLabel("{:n}".format(self.theProject.saveCount))

        self.statsLabel = QLabel("<b>Project Stats</b>")

        nR, nD, nF = self.theProject.projTree.countTypes()

        self.nRootLabel = QLabel("Root folders:")
        self.nRootLabel.setIndent(8)
        self.nRootValue = QLabel("{:n}".format(nR))

        self.nDirLabel = QLabel("Folders:")
        self.nDirLabel.setIndent(8)
        self.nDirValue = QLabel("{:n}".format(nD))

        self.nFileLabel = QLabel("Documents:")
        self.nFileLabel.setIndent(8)
        self.nFileValue = QLabel("{:n}".format(nF))

        self.wordsLabel = QLabel("Word count:")
        self.wordsLabel.setIndent(8)
        self.wordsValue = QLabel("{:n}".format(self.theProject.currWCount))

        self.mainForm.addWidget(self.headLabel,  0, 0, 1, 2, Qt.AlignTop)
        self.mainForm.addWidget(self.nameLabel,  1, 0, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.nameValue,  1, 1, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.pathLabel,  2, 0, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.pathValue,  2, 1, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.revLabel,   3, 0, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.revValue,   3, 1, 1, 1, Qt.AlignTop)

        self.mainForm.addWidget(self.statsLabel, 4, 0, 1, 2, Qt.AlignTop)
        self.mainForm.addWidget(self.nRootLabel, 5, 0, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.nRootValue, 5, 1, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.nDirLabel,  6, 0, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.nDirValue,  6, 1, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.nFileLabel, 7, 0, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.nFileValue, 7, 1, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.wordsLabel, 8, 0, 1, 1, Qt.AlignTop)
        self.mainForm.addWidget(self.wordsValue, 8, 1, 1, 1, Qt.AlignTop)

        self.mainForm.setVerticalSpacing(6)
        self.mainForm.setHorizontalSpacing(12)
        self.mainForm.setColumnStretch(0, 0)
        self.mainForm.setColumnStretch(1, 1)
        self.mainForm.setRowStretch(10, 1)

        return

# END Class GuiProjectEditMeta

class GuiProjectEditStatus(QWidget):

    def __init__(self, theParent, theProject, isStatus):
        QWidget.__init__(self, theParent)

        self.theParent  = theParent
        self.theProject = theProject
        if isStatus:
            self.theStatus = self.theProject.statusItems
        else:
            self.theStatus = self.theProject.importItems

        self.colData    = []
        self.colCounts  = []
        self.colChanged = False
        self.selColour  = None

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
        self.colPixmap  = QPixmap(16,16)
        self.colPixmap.fill(QColor(120,120,120))
        self.colButton  = QPushButton(QIcon(self.colPixmap),"Colour")
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
        logger.verbose("Item colour button clicked")
        if self.selColour is not None:
            newCol = QColorDialog.getColor(
                self.selColour, self, "Select Colour", QColorDialog.DontUseNativeDialog
            )
            if newCol:
                self.selColour = newCol
                colPixmap = QPixmap(16,16)
                colPixmap.fill(newCol)
                self.colButton.setIcon(QIcon(colPixmap))
                self.colButton.setIconSize(colPixmap.rect().size())
        return

    def _newItem(self):
        logger.verbose("New item button clicked")
        newItem = self._addItem("New Item", (0, 0, 0), None, 0)
        newItem.setBackground(QBrush(QColor(0,255,0,80)))
        self.colChanged = True
        return

    def _delItem(self):
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
        logger.verbose("Save item button clicked")
        selItem = self._getSelectedItem()
        iRow    = self.listBox.row(selItem)
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
        newIcon = QPixmap(16,16)
        newIcon.fill(QColor(*iCol))
        newItem = QListWidgetItem()
        newItem.setText("%s [%d]" % (iName, nUse))
        newItem.setIcon(QIcon(newIcon))
        newItem.setData(Qt.UserRole, len(self.colData))
        self.listBox.addItem(newItem)
        self.colData.append((iName,iCol[0],iCol[1],iCol[2],oName))
        self.colCounts.append(nUse)
        return newItem

    def _selectedItem(self):
        logger.verbose("Item selected")
        selItem = self._getSelectedItem()
        if selItem is not None:
            selIdx  = selItem.data(Qt.UserRole)
            selVal  = self.colData[selIdx]
            self.selColour = QColor(selVal[1],selVal[2],selVal[3])
            newIcon = QPixmap(16,16)
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
        selItem = self.listBox.selectedItems()
        if len(selItem) == 0:
            return None
        if isinstance(selItem[0], QListWidgetItem):
            return selItem[0]
        return None

    def _rowsMoved(self):
        logger.verbose("A drag move event occurred")
        self.colChanged = True
        return

# END Class GuiProjectEditStatus

class GuiProjectEditReplace(QWidget):

    def __init__(self, theParent, theProject):
        QWidget.__init__(self, theParent)

        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
        self.theProject = theProject
        self.arChanged  = False

        self.outerBox   = QVBoxLayout()
        self.bottomBox  = QHBoxLayout()
        self.listBox    = QTreeWidget()
        self.listBox.setHeaderLabels(["Keyword","Replace With"])
        self.listBox.itemSelectionChanged.connect(self._selectedItem)
        self.listBox.setIndentation(0)

        treeHead = self.listBox.headerItem()
        treeHead.setFont(0, self.theTheme.guiFont)
        treeHead.setFont(1, self.theTheme.guiFont)

        for aKey, aVal in self.theProject.autoReplace.items():
            newItem = QTreeWidgetItem(["<%s>" % aKey, aVal])
            newItem.setFont(0, self.theTheme.guiFont)
            newItem.setFont(1, self.theTheme.guiFont)
            self.listBox.addTopLevelItem(newItem)

        self.listBox.sortByColumn(0, Qt.AscendingOrder)
        self.listBox.setSortingEnabled(True)

        self.editKey    = QLineEdit()
        self.editValue  = QLineEdit()
        self.saveButton = QPushButton(self.theTheme.getIcon("done"),"")
        self.addButton  = QPushButton(self.theTheme.getIcon("add"),"")
        self.delButton  = QPushButton(self.theTheme.getIcon("remove"),"")
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
        newList = {}
        for n in range(self.listBox.topLevelItemCount()):
            tItem = self.listBox.topLevelItem(n)
            aKey  = self._stripNotAllowed(tItem.text(0))
            aVal  = tItem.text(1)
            if len(aKey) > 0:
                newList[aKey] = aVal
        return newList

    ##
    #  Internal Functions
    ##

    def _selectedItem(self):
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

        selItem = self._getSelectedItem()
        if selItem is None:
            return False

        newKey  = self.editKey.text()
        newVal  = self.editValue.text()
        saveKey = self._stripNotAllowed(newKey)

        if len(saveKey) > 0 and len(newVal) > 0:
            selItem.setText(0,"<%s>" % saveKey)
            selItem.setText(1,newVal)
            self.editKey.clear()
            self.editValue.clear()
            self.editKey.setEnabled(False)
            self.editValue.setEnabled(False)
            self.listBox.clearSelection()
            self.arChanged = True

        return

    def _addEntry(self):
        saveKey = "<keyword%d>" % (self.listBox.topLevelItemCount() + 1)
        newVal  = ""
        newItem = QTreeWidgetItem([saveKey, newVal])
        newItem.setFont(0, self.theTheme.guiFont)
        newItem.setFont(1, self.theTheme.guiFont)
        self.listBox.addTopLevelItem(newItem)
        return True

    def _delEntry(self):
        selItem = self._getSelectedItem()
        if selItem is None:
            return False
        self.listBox.takeTopLevelItem(self.listBox.indexOfTopLevelItem(selItem))
        self.arChanged = True
        return True

    def _getSelectedItem(self):
        selItem = self.listBox.selectedItems()
        if len(selItem) == 0:
            return None
        return selItem[0]

    def _stripNotAllowed(self, theKey):
        retKey = ""
        for c in theKey:
            if c.isalnum():
                retKey += c
        return retKey

# END Class GuiProjectEditReplace
