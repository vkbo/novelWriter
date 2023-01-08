"""
novelWriter – Project Wrapper
=============================
The parent class for a novelWriter project

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

import json
import logging
import novelwriter

from time import time
from pathlib import Path
from functools import partial

from PyQt5.QtCore import QCoreApplication, QObject, pyqtSignal

from novelwriter.enum import nwItemType, nwItemClass, nwItemLayout, nwAlert
from novelwriter.error import logException
from novelwriter.constants import trConst, nwFiles, nwLabels
from novelwriter.core.tree import NWTree
from novelwriter.core.item import NWItem
from novelwriter.core.index import NWIndex
from novelwriter.core.options import OptionState
from novelwriter.core.storage import NWStorage
from novelwriter.core.projectxml import ProjectXMLReader, ProjectXMLWriter, XMLReadState
from novelwriter.core.projectdata import NWProjectData
from novelwriter.common import (
    checkStringNone, formatTimeStamp, hexToInt, isHandle, makeFileNameSafe, minmax
)

logger = logging.getLogger(__name__)


class NWProject(QObject):

    projectStatusChanged = pyqtSignal(bool)

    def __init__(self, mainGui):
        super().__init__(parent=mainGui)

        # Internal
        self.mainConf = novelwriter.CONFIG
        self.mainGui  = mainGui

        # Core Elements
        self._options = OptionState(self)    # Project-specific GUI options
        self._storage = NWStorage(self)      # The project storage handler
        self._data    = NWProjectData(self)  # The project settings
        self._tree    = NWTree(self)         # The project tree
        self._index   = NWIndex(self)        # The projecty index

        # Data Cache
        self._langData = {}  # Localisation data

        # Project Status
        self._projOpened  = 0      # The time stamp of when the project file was opened
        self._projChanged = False  # The project has unsaved changes
        self._lockedBy    = None   # Data on which computer has the project open
        self._projFiles   = []     # A list of all files in the content folder on load

        # Internal Mapping
        self.tr = partial(QCoreApplication.translate, "NWProject")

        # Set Defaults
        self.clearProject()

        return

    ##
    #  Properties
    ##

    @property
    def options(self):
        return self._options

    @property
    def storage(self):
        return self._storage

    @property
    def data(self):
        return self._data

    @property
    def tree(self):
        return self._tree

    @property
    def index(self):
        return self._index

    @property
    def projOpened(self):
        return self._projOpened

    @property
    def projChanged(self):
        return self._projChanged

    @property
    def projFiles(self):
        return self._projFiles

    ##
    #  Item Methods
    ##

    def newRoot(self, itemClass, label=None):
        """Add a new root item. If label is None, use the class label.
        """
        if label is None:
            label = trConst(nwLabels.CLASS_NAME[itemClass])
        newItem = NWItem(self)
        newItem.setName(label)
        newItem.setType(nwItemType.ROOT)
        newItem.setClass(itemClass)
        self._tree.append(None, None, newItem)
        self._tree.updateItemData(newItem.itemHandle)
        return newItem.itemHandle

    def newFolder(self, label, pHandle):
        """Add a new folder with a given label and parent item.
        """
        if pHandle not in self._tree:
            return None
        newItem = NWItem(self)
        newItem.setName(label)
        newItem.setType(nwItemType.FOLDER)
        self._tree.append(None, pHandle, newItem)
        self._tree.updateItemData(newItem.itemHandle)
        return newItem.itemHandle

    def newFile(self, label, pHandle):
        """Add a new file with a given label and parent item.
        """
        if pHandle not in self._tree:
            return None
        newItem = NWItem(self)
        newItem.setName(label)
        newItem.setType(nwItemType.FILE)
        self._tree.append(None, pHandle, newItem)
        self._tree.updateItemData(newItem.itemHandle)
        return newItem.itemHandle

    def writeNewFile(self, tHandle, hLevel, isDocument, addText=""):
        """Write content to a new document after it is created. This
        will not run if the file exists and is not empty.
        """
        tItem = self._tree[tHandle]
        if tItem is None:
            return False
        if not tItem.isFileType():
            return False

        newDoc = self._storage.getDocument(tHandle)
        if (newDoc.readDocument() or "").strip():
            return False

        hshText = "#"*minmax(hLevel, 1, 4)
        newText = f"{hshText} {tItem.itemName}\n\n{addText}"
        if tItem.isNovelLike() and isDocument:
            tItem.setLayout(nwItemLayout.DOCUMENT)
        else:
            tItem.setLayout(nwItemLayout.NOTE)

        newDoc.writeDocument(newText)
        self._index.scanText(tHandle, newText)

        return True

    def removeItem(self, tHandle):
        """Remove an item from the project. This will delete both the
        project entry and a document file if it exists.
        """
        if self._tree.checkType(tHandle, nwItemType.FILE):
            delDoc = self._storage.getDocument(tHandle)
            if not delDoc.deleteDocument():
                self.mainGui.makeAlert([
                    self.tr("Could not delete document file."), delDoc.getError()
                ], nwAlert.ERROR)
                return False

        self._index.deleteHandle(tHandle)
        del self._tree[tHandle]

        return True

    def trashFolder(self):
        """Add the special trash root folder to the project.
        """
        trashHandle = self._tree.trashRoot()
        if trashHandle is None:
            newItem = NWItem(self)
            newItem.setName(trConst(nwLabels.CLASS_NAME[nwItemClass.TRASH]))
            newItem.setType(nwItemType.ROOT)
            newItem.setClass(nwItemClass.TRASH)
            self._tree.append(None, None, newItem)
            self._tree.updateItemData(newItem.itemHandle)
            return newItem.itemHandle

        return trashHandle

    ##
    #  Project Methods
    ##

    def clearProject(self):
        """Clear the data for the current project, and set them to
        default values.
        """
        # Project Status
        self._projOpened  = 0
        self._projChanged = False

        # Project Tree
        self._storage.clear()
        self._tree.clear()
        self._index.clearIndex()
        self._data = NWProjectData(self)

        # Project Settings
        self._projFiles = []

        return

    def openProject(self, projPath, overrideLock=False):
        """Open the project file provided. If it doesn't exist, assume
        it is a folder and look for the file within it. If successful,
        parse the XML of the file and populate the project variables and
        build the tree of project items.
        """
        self.clearProject()
        if not self._storage.openProjectInPlace(projPath):
            self.mainGui.makeAlert(self.tr(
                "Could not open project with path: {0}"
            ).format(projPath), nwAlert.ERROR)
            return False

        logger.info("Opening project: %s", projPath)

        # Project Lock
        # ============

        if overrideLock:
            self._storage.clearLockFile()

        lockStatus = self._storage.readLockFile()
        if len(lockStatus) > 0:
            if lockStatus[0] == "ERROR":
                logger.warning("Failed to check lock file")
            else:
                logger.error("Project is locked, so not opening")
                self._lockedBy = lockStatus
                self.clearProject()
                return False
        else:
            logger.debug("Project is not locked")

        # Open The Project XML File
        # =========================

        xmlReader = self._storage.getXmlReader()
        if not isinstance(xmlReader, ProjectXMLReader):
            self.clearProject()
            return False

        self._data = NWProjectData(self)
        projContent = []
        xmlParsed = xmlReader.read(self._data, projContent)

        appVersion = xmlReader.appVersion or self.tr("Unknown")

        if not xmlParsed:
            if xmlReader.state == XMLReadState.NOT_NWX_FILE:
                self.mainGui.makeAlert(self.tr(
                    "Project file does not appear to be a novelWriterXML file."
                ), nwAlert.ERROR)
            elif xmlReader.state == XMLReadState.UNKNOWN_VERSION:
                self.mainGui.makeAlert(self.tr(
                    "Unknown or unsupported novelWriter project file format. "
                    "The project cannot be opened by this version of novelWriter. "
                    "The file was saved with novelWriter version {0}."
                ).format(appVersion), nwAlert.ERROR)
            else:
                self.mainGui.makeAlert(self.tr(
                    "Failed to parse project xml."
                ), nwAlert.ERROR)

            self.clearProject()
            return False

        # Check Legacy Upgrade
        # ====================

        if xmlReader.state == XMLReadState.WAS_LEGACY:
            msgYes = self.mainGui.askQuestion(
                self.tr("File Version"),
                self.tr(
                    "The file format of your project is about to be updated. "
                    "If you proceed, older versions of novelWriter will no "
                    "longer be able to open this project. Continue?"
                )
            )
            if not msgYes:
                self.clearProject()
                return False

        # Check novelWriter Version
        # =========================

        if xmlReader.hexVersion > hexToInt(novelwriter.__hexversion__):
            msgYes = self.mainGui.askQuestion(
                self.tr("Version Conflict"),
                self.tr(
                    "This project was saved by a newer version of "
                    "novelWriter, version {0}. This is version {1}. If you "
                    "continue to open the project, some attributes and "
                    "settings may not be preserved, but the overall project "
                    "should be fine. Continue opening the project?"
                ).format(appVersion, novelwriter.__version__)
            )
            if not msgYes:
                self.clearProject()
                return False

        # Extract Data
        # ============

        self._tree.unpack(projContent)
        self._options.loadSettings()
        self._loadProjectLocalisation()

        # Update recent projects
        self.mainConf.recentProjects.update(
            self._storage.storagePath, self._data.name, sum(self._data.initCounts), time()
        )

        # Check the project tree consistency
        for tItem in self._tree:
            if tItem:
                tHandle = tItem.itemHandle
                logger.debug("Checking item '%s'", tHandle)
                if not self._tree.updateItemData(tHandle):
                    logger.error("There was a problem the item, and it has been removed")
                    del self._tree[tHandle]  # The file will be re-added as orphaned

        self._scanProjectFolder()
        self._index.loadIndex()
        if xmlReader.state == XMLReadState.WAS_LEGACY:
            # Often, the index needs to be rebuilt when updating format
            self._index.rebuildIndex()

        self.updateWordCounts()
        self._projOpened = time()

        self._storage.writeLockFile()
        self.setProjectChanged(False)
        self.mainGui.setStatus(self.tr("Opened Project: {0}").format(self._data.name))

        return True

    def saveProject(self, autoSave=False):
        """Save the project main XML file. The saving command itself
        uses a temporary filename, and the file is replaced afterwards
        to make sure if the save fails, we're not left with a truncated
        file.
        """
        if not self._storage.isOpen():
            self.mainGui.makeAlert(self.tr(
                "There is no project open."
            ), nwAlert.ERROR)
            return False

        saveTime = time()

        logger.info("Saving project: %s", self._storage.storagePath)

        if autoSave:
            self._data.incAutoCount()
        else:
            self._data.incSaveCount()

        self.updateWordCounts()
        self.countStatus()

        xmlWriter = self._storage.getXmlWriter()
        if not isinstance(xmlWriter, ProjectXMLWriter):
            return False

        saveTime = time()
        editTime = int(self._data.editTime + saveTime - self._projOpened)
        content = self._tree.pack()
        if not xmlWriter.write(self._data, content, saveTime, editTime):
            self.mainGui.makeAlert(self.tr(
                "Failed to save project."
            ), nwAlert.ERROR, exception=xmlWriter.error)
            return False

        # Save other project data
        self._options.saveSettings()
        self._index.saveIndex()
        self._storage.runPostSaveTasks(autoSave=autoSave)

        # Update recent projects
        self.mainConf.recentProjects.update(
            self._storage.storagePath, self._data.name, sum(self._data.currCounts), saveTime
        )

        self._storage.writeLockFile()
        self.mainGui.setStatus(self.tr("Saved Project: {0}").format(self._data.name))
        self.setProjectChanged(False)

        return True

    def closeProject(self, idleTime=0.0):
        """Close the current project and clear all meta data.
        """
        logger.info("Closing project")
        self._options.saveSettings()
        self._tree.writeToCFile()
        self._appendSessionStats(idleTime)
        self._storage.clearLockFile()
        self._storage.closeSession()
        self.clearProject()
        self._lockedBy = None
        return True

    def backupProject(self, doNotify):
        """Create a zip file of the entire project.
        """
        if not self._storage.isOpen():
            logger.error("No project open")
            return False

        logger.info("Backing up project")
        self.mainGui.setStatus(self.tr("Backing up project ..."))

        backupPath = self.mainConf.backupPath()
        if not isinstance(backupPath, Path):
            self.mainGui.makeAlert(self.tr(
                "Cannot backup project because no valid backup path is set. "
                "Please set a valid backup location in Preferences."
            ), nwAlert.ERROR)
            return False

        if not self._data.name:
            self.mainGui.makeAlert(self.tr(
                "Cannot backup project because no project name is set. "
                "Please set a Project Name in Project Settings."
            ), nwAlert.ERROR)
            return False

        cleanName = makeFileNameSafe(self._data.name)
        baseDir = backupPath / cleanName
        try:
            baseDir.mkdir(exist_ok=True)
        except Exception as exc:
            self.mainGui.makeAlert(self.tr(
                "Could not create backup folder."
            ), nwAlert.ERROR, exception=exc)
            return False

        archName = baseDir / self.tr(
            "Backup from {0}"
        ).format(formatTimeStamp(time(), fileSafe=True) + ".zip")
        if self._storage.zipIt(archName, compression=2):
            if doNotify:
                self.mainGui.makeAlert(self.tr(
                    "Backup archive file written to: {0}"
                ).format(str(archName), nwAlert.INFO))
        else:
            self.mainGui.makeAlert(self.tr(
                "Could not write backup archive."
            ), nwAlert.ERROR)
            return False

        self.mainGui.setStatus(self.tr(
            "Project backed up to '{0}'"
        ).format(str(archName)))

        return True

    ##
    #  Setters
    ##

    def setDefaultStatusImport(self):
        """Set the default status and importance values.
        """
        self._data.itemStatus.write(None, self.tr("New"),      (100, 100, 100))
        self._data.itemStatus.write(None, self.tr("Note"),     (200, 50,  0))
        self._data.itemStatus.write(None, self.tr("Draft"),    (200, 150, 0))
        self._data.itemStatus.write(None, self.tr("Finished"), (50,  200, 0))
        self._data.itemImport.write(None, self.tr("New"),      (100, 100, 100))
        self._data.itemImport.write(None, self.tr("Minor"),    (200, 50,  0))
        self._data.itemImport.write(None, self.tr("Major"),    (200, 150, 0))
        self._data.itemImport.write(None, self.tr("Main"),     (50,  200, 0))
        return

    def setProjectLang(self, theLang):
        """Set the project-specific language.
        """
        theLang = checkStringNone(theLang, None)
        if self._data.language != theLang:
            self._data.setLanguage(theLang)
            self._loadProjectLocalisation()
            self.setProjectChanged(True)
        return True

    def setTreeOrder(self, newOrder):
        """A list representing the linear/flattened order of project
        items in the GUI project tree. The user can rearrange the order
        by drag-and-drop. Forwarded to the NWTree class.
        """
        if len(self._tree) != len(newOrder):
            logger.warning("Sizes of new and old tree order do not match")
        self._tree.setOrder(newOrder)
        self.setProjectChanged(True)
        return True

    def setStatusColours(self, newCols, delCols):
        """Update the list of novel file status flags.
        """
        return self._setStatusImport(newCols, delCols, self._data.itemStatus)

    def setImportColours(self, newCols, delCols):
        """Update the list of note file importance flags.
        """
        return self._setStatusImport(newCols, delCols, self._data.itemImport)

    def setProjectChanged(self, value):
        """Toggle the project changed flag, and propagate the
        information to the GUI statusbar.
        """
        if isinstance(value, bool):
            self._projChanged = value
            self.projectStatusChanged.emit(self._projChanged)
        return self._projChanged

    ##
    #  Getters
    ##

    def getLockStatus(self):
        """Return the project lock information for the project.
        """
        if isinstance(self._lockedBy, list) and len(self._lockedBy) == 4:
            return self._lockedBy
        return None

    def getCurrentEditTime(self):
        """Get the total project edit time, including the time spent in
        the current session.
        """
        return round(self._data.editTime + time() - self._projOpened)

    def getProjectItems(self):
        """This function ensures that the item tree loaded is sent to
        the GUI tree view in such a way that the tree can be built. That
        is, the parent item must be sent before its child. In principle,
        a proper XML file will already ensure that, but in the event the
        order has been altered, or a file is orphaned, this function is
        capable of handling it.
        """
        sentItems = []
        iterItems = self._tree.handles()
        n = 0
        nMax = min(len(iterItems), 10000)
        while n < nMax:
            tHandle = iterItems[n]
            tItem = self._tree[tHandle]
            n += 1
            if tItem is None:
                # Technically a bug since treeOrder is built from the
                # same data as _projTree
                continue
            elif tItem.itemParent is None:
                # Item is a root, or already been identified as an
                # orphaned item
                sentItems.append(tHandle)
                yield tItem
            elif tItem.itemParent in sentItems:
                # Item's parent has been sent, so all is fine
                sentItems.append(tHandle)
                yield tItem
            elif tItem.itemParent in iterItems:
                # Item's parent exists, but hasn't been sent yet, so add
                # it again to the end, but make sure this doesn't get
                # out hand, so we cap at 10000 items
                logger.warning("Item '%s' found before its parent", tHandle)
                iterItems.append(tHandle)
                nMax = min(len(iterItems), 10000)
            else:
                # Item is orphaned
                logger.error("Item '%s' has no parent in current tree", tHandle)
                tItem.setParent(None)
                yield tItem

    ##
    #  Class Methods
    ##

    def updateWordCounts(self):
        """Update the total word count values.
        """
        novel, notes = self._tree.sumWords()
        self._data.setCurrCounts(novel=novel, notes=notes)
        return

    def countStatus(self):
        """Count how many times the various status flags are used in the
        project tree. The counts themselves are kept in the NWStatus
        objects. This is essentially a refresh.
        """
        self._data.itemStatus.resetCounts()
        self._data.itemImport.resetCounts()
        for nwItem in self._tree:
            if nwItem.isNovelLike():
                self._data.itemStatus.increment(nwItem.itemStatus)
            else:
                self._data.itemImport.increment(nwItem.itemImport)
        return

    def localLookup(self, theWord):
        """Look up a word in the translation map for the project and
        return it. The variable is cast to a string before lookup. If
        the word does not exist, it returns itself.
        """
        return self._langData.get(str(theWord), str(theWord))

    ##
    #  Internal Functions
    ##

    def _setStatusImport(self, new, delete, target):
        """Update the list of novel file status or importance flags, and
        delete those that have been requested deleted.
        """
        if not (new or delete):
            return False

        order = []
        for entry in new:
            key = entry.get("key", None)
            name = entry.get("name", "")
            cols = entry.get("cols", (100, 100, 100))
            if name:
                order.append(target.write(key, name, cols))

        for key in delete:
            target.remove(key)

        target.reorder(order)

        return True

    def _loadProjectLocalisation(self):
        """Load the language data for the current project language.
        """
        if self._data.language is None or self.mainConf._nwLangPath is None:
            self._langData = {}
            return False

        langFile = Path(self.mainConf._nwLangPath) / f"project_{self._data.language}.json"
        if not langFile.is_file():
            langFile = Path(self.mainConf._nwLangPath) / "project_en_GB.json"

        try:
            with open(langFile, mode="r", encoding="utf-8") as inFile:
                self._langData = json.load(inFile)
            logger.debug("Loaded project language file: %s", langFile.name)

        except Exception:
            logger.error("Failed to project language file")
            logException()
            return False

        return True

    def _scanProjectFolder(self):
        """Scan the project folder and check that the files in it are
        also in the project XML file. If they aren't, import them as
        orphaned files so the user can either delete them, or put them
        back into the project tree.
        """
        contentPath = self._storage.contentPath
        if not isinstance(contentPath, Path):
            return False

        # Then check the files in the data folder
        logger.debug("Checking files in project content folder")
        orphanFiles = []
        self._projFiles = []

        for item in contentPath.iterdir():
            itemName = item.name
            if not itemName.endswith(".nwd"):
                logger.warning("Skipping file: %s", itemName)
                continue
            if len(itemName) != 17:
                logger.warning("Skipping file: %s", itemName)
                continue

            fHandle = itemName[:13]
            if not isHandle(fHandle):
                logger.warning("Skipping file: %s", itemName)
                continue

            if fHandle in self._tree:
                self._projFiles.append(fHandle)
                logger.debug("Checking file %s, handle '%s': OK", itemName, fHandle)
            else:
                logger.warning("Checking file %s, handle '%s': Orphaned", itemName, fHandle)
                orphanFiles.append(fHandle)

        # Report status
        if len(orphanFiles) > 0:
            self.mainGui.makeAlert(self.tr(
                "Found {0} orphaned file(s) in project folder."
            ).format(len(orphanFiles)), nwAlert.WARN)
        else:
            logger.debug("File check OK")
            return

        # Handle orphans
        nOrph = 0
        noWhere = False
        oPrefix = self.tr("Recovered")
        for oHandle in orphanFiles:

            # Look for meta data
            oName = ""
            oParent = None
            oClass = None
            oLayout = None

            aDoc = self._storage.getDocument(oHandle)
            if aDoc.readDocument(isOrphan=True) is not None:
                oName, oParent, oClass, oLayout = aDoc.getMeta()

            if oName:
                oName = self.tr("[{0}] {1}").format(
                    oPrefix, oName.replace("[%s]" % oPrefix, "").strip()
                )
            else:
                nOrph += 1
                oName = self.tr("Recovered File {0}").format(nOrph)

            # Recover file meta data
            if oClass is None:
                oClass = nwItemClass.NOVEL

            if oLayout is None:
                oLayout = nwItemLayout.NOTE

            if oParent is None or oParent not in self._tree:
                oParent = self._tree.findRoot(oClass)
                if oParent is None:
                    oParent = self._tree.findRoot(nwItemClass.NOVEL)

            # If the file still has no parent item, skip it
            if oParent is None:
                noWhere = True
                continue

            orphItem = NWItem(self)
            orphItem.setName(oName)
            orphItem.setType(nwItemType.FILE)
            orphItem.setClass(oClass)
            orphItem.setLayout(oLayout)
            self._tree.append(oHandle, oParent, orphItem)
            self._tree.updateItemData(orphItem.itemHandle)

        if noWhere:
            self.mainGui.makeAlert(self.tr(
                "One or more orphaned files could not be added back into the project. "
                "Make sure at least a Novel root folder exists."
            ), nwAlert.WARN)

        return True

    def _appendSessionStats(self, idleTime):
        """Append session statistics to the sessions log file.
        """
        sessionFile = self._storage.getMetaFile(nwFiles.SESS_STATS)
        if not isinstance(sessionFile, Path):
            return False

        nowTime = time()
        iNovel, iNotes = self._data.initCounts
        cNovel, cNotes = self._data.currCounts
        iTotal = iNovel + iNotes
        sessDiff = cNovel + cNotes - iTotal
        sessTime = nowTime - self._projOpened

        logger.info("The session lasted %d sec and added %d words", int(sessTime), sessDiff)
        if sessTime < 300 and sessDiff == 0:
            logger.info("Session too short, skipping log entry")
            return False

        try:
            isFile = sessionFile.exists()  # We must save the state before we open
            with open(sessionFile, mode="a+", encoding="utf-8") as outFile:
                if not isFile:
                    # It's a new file, so add a header
                    if iTotal > 0:
                        outFile.write("# Offset %d\n" % iTotal)
                    outFile.write("# %-17s  %-19s  %8s  %8s  %8s\n" % (
                        "Start Time", "End Time", "Novel", "Notes", "Idle"
                    ))

                outFile.write("%-19s  %-19s  %8d  %8d  %8d\n" % (
                    formatTimeStamp(self._projOpened),
                    formatTimeStamp(nowTime),
                    cNovel,
                    cNotes,
                    int(idleTime),
                ))

        except Exception:
            logger.error("Failed to write session stats file")
            logException()
            return False

        return True

# END Class NWProject
