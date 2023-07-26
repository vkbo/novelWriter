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
from __future__ import annotations

import json
import logging

from time import time
from typing import TYPE_CHECKING, Iterator
from pathlib import Path
from functools import partial

from PyQt5.QtCore import QCoreApplication, QObject, pyqtSignal

from novelwriter import CONFIG, __version__, __hexversion__
from novelwriter.enum import nwItemType, nwItemClass, nwItemLayout, nwAlert
from novelwriter.error import logException
from novelwriter.constants import trConst, nwLabels
from novelwriter.core.tree import NWTree
from novelwriter.core.index import NWIndex
from novelwriter.core.options import OptionState
from novelwriter.core.storage import NWStorage
from novelwriter.core.sessions import NWSessionLog
from novelwriter.core.projectxml import ProjectXMLReader, ProjectXMLWriter, XMLReadState
from novelwriter.core.projectdata import NWProjectData
from novelwriter.common import (
    checkStringNone, formatInt, formatTimeStamp, hexToInt, makeFileNameSafe, minmax
)

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain
    from novelwriter.core.item import NWItem
    from novelwriter.core.status import NWStatus

logger = logging.getLogger(__name__)


class NWProject(QObject):

    projectStatusChanged = pyqtSignal(bool)

    def __init__(self, mainGui: GuiMain) -> None:
        super().__init__(parent=mainGui)

        # Internal
        self.mainGui = mainGui

        # Core Elements
        self._options = OptionState(self)    # Project-specific GUI options
        self._storage = NWStorage(self)      # The project storage handler
        self._data    = NWProjectData(self)  # The project settings
        self._tree    = NWTree(self)         # The project tree
        self._index   = NWIndex(self)        # The project index
        self._session = NWSessionLog(self)   # The session record

        # Project Status
        self._langData    = {}     # Localisation data
        self._projChanged = False  # The project has unsaved changes
        self._lockedBy    = None   # Data on which computer has the project open

        # Internal Mapping
        self.tr = partial(QCoreApplication.translate, "NWProject")

        return

    ##
    #  Properties
    ##

    @property
    def options(self) -> OptionState:
        return self._options

    @property
    def storage(self) -> NWStorage:
        return self._storage

    @property
    def data(self) -> NWProjectData:
        return self._data

    @property
    def tree(self) -> NWTree:
        return self._tree

    @property
    def index(self) -> NWIndex:
        return self._index

    @property
    def session(self) -> NWSessionLog:
        return self._session

    @property
    def projOpened(self) -> float:
        return self._session.start

    @property
    def projChanged(self) -> bool:
        return self._projChanged

    ##
    #  Item Methods
    ##

    def newRoot(self, itemClass: nwItemClass, label: str | None = None) -> str:
        """Add a new root folder to the project. If label is not set,
        use the class label.
        """
        label = label or trConst(nwLabels.CLASS_NAME[itemClass])
        return self._tree.create(label, None, nwItemType.ROOT, itemClass)

    def newFolder(self, label: str, parent: str) -> str | None:
        """Add a new folder with a given label and parent item."""
        return self._tree.create(label, parent, nwItemType.FOLDER)

    def newFile(self, label: str, parent: str) -> str | None:
        """Add a new file with a given label and parent item."""
        return self._tree.create(label, parent, nwItemType.FILE)

    def writeNewFile(self, tHandle: str, hLevel: int, isDocument: bool, addText: str = "") -> bool:
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

    def removeItem(self, tHandle: str) -> bool:
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

    def trashFolder(self) -> str:
        """Add the special trash root folder to the project."""
        trashHandle = self._tree.trashRoot()
        if trashHandle is None:
            label = trConst(nwLabels.CLASS_NAME[nwItemClass.TRASH])
            return self._tree.create(label, None, nwItemType.ROOT, nwItemClass.TRASH)
        return trashHandle

    ##
    #  Project Methods
    ##

    def clearProject(self) -> None:
        """Clear the data for the current project, and set them to
        default values.

        Note: Don't clear the lockedBy data here as it is needed after
        this function is called.
        """
        # Core Elements
        self._options = OptionState(self)
        self._storage.clear()
        self._data = NWProjectData(self)
        self._tree.clear()
        self._index.clearIndex()
        self._session = NWSessionLog(self)

        # Project Status
        self._langData = {}
        self._projChanged = False

        return

    def openProject(self, projPath: str | Path, overrideLock: bool = False) -> bool:
        """Open the project file provided. If it doesn't exist, assume
        it is a folder and look for the file within it. If successful,
        parse the XML of the file and populate the project variables and
        build the tree of project items.
        """
        self.clearProject()
        logger.info("Opening project: %s", projPath)
        if not self._storage.openProjectInPlace(projPath):
            self.mainGui.makeAlert(self.tr(
                "Could not open project with path: {0}"
            ).format(projPath), nwAlert.ERROR)
            return False

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

        if xmlReader.hexVersion > hexToInt(__hexversion__):
            msgYes = self.mainGui.askQuestion(
                self.tr("Version Conflict"),
                self.tr(
                    "This project was saved by a newer version of "
                    "novelWriter, version {0}. This is version {1}. If you "
                    "continue to open the project, some attributes and "
                    "settings may not be preserved, but the overall project "
                    "should be fine. Continue opening the project?"
                ).format(appVersion, __version__)
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
        CONFIG.recentProjects.update(
            self._storage.storagePath, self._data.name, sum(self._data.initCounts), time()
        )

        # Check the project tree consistency
        # This also handles any orphaned files found
        orphans, recovered = self._tree.checkConsistency(self.tr("Recovered"))
        if orphans > 0:
            self.mainGui.makeAlert(self.tr(
                "Found {0} orphaned file(s) in the project. {1} file(s) were recovered."
            ).format(orphans, recovered), nwAlert.WARN)

        self._index.loadIndex()
        if xmlReader.state == XMLReadState.WAS_LEGACY:
            # Often, the index needs to be rebuilt when updating format
            self._index.rebuildIndex()

        self.updateWordCounts()
        self._session.startSession()
        self._storage.writeLockFile()
        self.setProjectChanged(False)
        self.mainGui.setStatus(self.tr("Opened Project: {0}").format(self._data.name))

        return True

    def saveProject(self, autoSave: bool = False) -> bool:
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
        editTime = self._data.editTime + max(round(saveTime - self._session.start), 0)
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
        CONFIG.recentProjects.update(
            self._storage.storagePath, self._data.name, sum(self._data.currCounts), saveTime
        )

        self._storage.writeLockFile()
        self.mainGui.setStatus(self.tr("Saved Project: {0}").format(self._data.name))
        self.setProjectChanged(False)

        return True

    def closeProject(self, idleTime: float = 0.0) -> None:
        """Close the current project and clear all meta data."""
        logger.info("Closing project")
        self._options.saveSettings()
        self._tree.writeToCFile()
        self._session.appendSession(idleTime)
        self._storage.closeSession()
        self.clearProject()
        self._lockedBy = None
        return

    def backupProject(self, doNotify: bool) -> bool:
        """Create a zip file of the entire project."""
        if not self._storage.isOpen():
            logger.error("No project open")
            return False

        logger.info("Backing up project")
        self.mainGui.setStatus(self.tr("Backing up project ..."))

        backupPath = CONFIG.backupPath()
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

        timeStamp = formatTimeStamp(time(), fileSafe=True)
        archName = baseDir / f"{cleanName} {timeStamp}.zip"
        if self._storage.zipIt(archName, compression=2):
            size = archName.stat().st_size
            if doNotify:
                self.mainGui.makeAlert(self.tr(
                    "Backup archive file written to: {0} [{1}B]"
                ).format(str(archName), formatInt(size)), nwAlert.INFO)
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

    def setDefaultStatusImport(self) -> None:
        """Set the default status and importance values."""
        self._data.itemStatus.write(None, self.tr("New"),      (100, 100, 100))
        self._data.itemStatus.write(None, self.tr("Note"),     (200, 50,  0))
        self._data.itemStatus.write(None, self.tr("Draft"),    (200, 150, 0))
        self._data.itemStatus.write(None, self.tr("Finished"), (50,  200, 0))
        self._data.itemImport.write(None, self.tr("New"),      (100, 100, 100))
        self._data.itemImport.write(None, self.tr("Minor"),    (200, 50,  0))
        self._data.itemImport.write(None, self.tr("Major"),    (200, 150, 0))
        self._data.itemImport.write(None, self.tr("Main"),     (50,  200, 0))
        return

    def setProjectLang(self, language: str | None) -> None:
        """Set the project-specific language."""
        language = checkStringNone(language, None)
        if self._data.language != language:
            self._data.setLanguage(language)
            self._loadProjectLocalisation()
            self.setProjectChanged(True)
        return

    def setTreeOrder(self, order: list[str]) -> None:
        """A list representing the linear/flattened order of project
        items in the GUI project tree. The user can rearrange the order
        by drag-and-drop. Forwarded to the NWTree class.
        """
        if len(self._tree) != len(order):
            logger.warning("Sizes of new and old tree order do not match")
        self._tree.setOrder(order)
        self.setProjectChanged(True)
        return

    def setStatusColours(self, new: list[dict], deleted: list[str]) -> bool:
        """Update the list of novel file status flags."""
        return self._setStatusImport(new, deleted, self._data.itemStatus)

    def setImportColours(self, new: list[dict], deleted: list[str]) -> bool:
        """Update the list of note file importance flags."""
        return self._setStatusImport(new, deleted, self._data.itemImport)

    def setProjectChanged(self, status: bool) -> bool:
        """Toggle the project changed flag, and propagate the
        information to the GUI statusbar.
        """
        if isinstance(status, bool):
            self._projChanged = status
            self.projectStatusChanged.emit(self._projChanged)
        return self._projChanged

    ##
    #  Getters
    ##

    def getLockStatus(self) -> list | None:
        """Return the project lock information for the project."""
        if isinstance(self._lockedBy, list) and len(self._lockedBy) == 4:
            return self._lockedBy
        return None

    def getCurrentEditTime(self) -> int:
        """Get the total project edit time, including the time spent in
        the current session.
        """
        return self._data.editTime + round(time() - self._session.start)

    def getProjectItems(self) -> Iterator[NWItem]:
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
        return

    ##
    #  Class Methods
    ##

    def updateWordCounts(self) -> None:
        """Update the total word count values."""
        novel, notes = self._tree.sumWords()
        self._data.setCurrCounts(novel=novel, notes=notes)
        return

    def countStatus(self) -> None:
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

    def localLookup(self, word: str | int) -> str:
        """Look up a word or number in the translation map for the
        project and return it. The variable is cast to a string before
        lookup. If the word does not exist, it returns itself.
        """
        return self._langData.get(str(word), str(word))

    ##
    #  Internal Functions
    ##

    def _setStatusImport(self, new: list[dict], delete: list[str], target: NWStatus) -> bool:
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

    def _loadProjectLocalisation(self) -> bool:
        """Load the language data for the current project language."""
        if self._data.language is None or CONFIG._nwLangPath is None:
            self._langData = {}
            return False

        langFile = Path(CONFIG._nwLangPath) / f"project_{self._data.language}.json"
        if not langFile.is_file():
            langFile = Path(CONFIG._nwLangPath) / "project_en_GB.json"

        try:
            with open(langFile, mode="r", encoding="utf-8") as inFile:
                self._langData = json.load(inFile)
            logger.debug("Loaded project language file: %s", langFile.name)
        except Exception:
            logger.error("Failed to project language file")
            logException()
            return False

        return True

# END Class NWProject
