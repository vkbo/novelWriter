# -*- coding: utf-8 -*-
"""novelWriter Project Wrapper

 novelWriter – Project Wrapper
===============================
 Class wrapping the data of a novelWriter project

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
import json
import nw

from os import path, mkdir, listdir, unlink, rename, rmdir
from lxml import etree
from time import time
from shutil import make_archive

from PyQt5.QtWidgets import QMessageBox

from nw.core.tree import NWTree
from nw.core.item import NWItem
from nw.core.document import NWDoc
from nw.core.status import NWStatus
from nw.core.options import OptionState
from nw.common import checkString, checkBool, checkInt, formatTimeStamp
from nw.constants import (
    nwFiles, nwItemType, nwItemClass, nwItemLayout, nwAlert
)

logger = logging.getLogger(__name__)

class NWProject():

    def __init__(self, theParent):

        # Internal
        self.theParent = theParent
        self.mainConf  = nw.CONFIG

        # Core Elements
        self.optState = OptionState(self) # Project-specific GUI options
        self.projTree = NWTree(self)      # The project tree

        # Project Status
        self.projOpened  = 0     # The time stamp of when the project file was opened
        self.projChanged = False # The project has unsaved changes
        self.projAltered = False # The project has been altered this session
        self.lockedBy    = None  # Data on which computer has the project open
        self.saveCount   = 0     # Meta data: number of saves
        self.autoCount   = 0     # Meta data: number of automatic saves
        self.editTime    = 0     # The accumulated edit time read from the project file

        # Class Settings
        self.projPath    = None # The full path to where the currently open project is saved
        self.projMeta    = None # The full path to the project's meta data folder
        self.projCache   = None # The full path to the project's cache folder
        self.projContent = None # The full path to the project's content folder
        self.projDict    = None # The spell check dictionary
        self.projFile    = None # The file name of the project main XML file

        # Project Meta
        self.projName    = "" # Project name (working title)
        self.bookTitle   = "" # The final title; should only be used for exports
        self.bookAuthors = [] # A list of book authors

        # Project Settings
        self.autoReplace = {}    # Text to auto-replace on exports
        self.titleFormat = {}    # The formatting of titles for exports
        self.spellCheck  = False # Controls the spellcheck-as-you-type feature
        self.autoOutline = True  # If true, the Project Outline is updated automatically
        self.statusItems = None  # Novel file progress status values
        self.importItems = None  # Note file importance values
        self.lastEdited  = None  # The handle of the last file to be edited
        self.lastViewed  = None  # The handle of the last file to be viewed
        self.lastWCount  = 0     # The project word count from last session
        self.currWCount  = 0     # The project word count in current session
        self.novelWCount = 0     # Total number of words in novel files
        self.notesWCount = 0     # Total number of words in note files
        self.doBackup    = True  # Run project backup on exit

        # Set Defaults
        self.clearProject()

        # Internal Mapping
        self.makeAlert = self.theParent.makeAlert

        return

    ##
    #  Item Methods
    ##

    def newRoot(self, rootName, rootClass):
        """Add a new root item. These items are unique, except for item class
        CUSTOM, and always have parent handle set to None.
        """
        if not self.projTree.checkRootUnique(rootClass):
            self.makeAlert("Duplicate root item detected.", nwAlert.ERROR)
            return None
        newItem = NWItem(self)
        newItem.setName(rootName)
        newItem.setType(nwItemType.ROOT)
        newItem.setClass(rootClass)
        newItem.setStatus(0)
        self.projTree.append(None, None, newItem)
        return newItem.itemHandle

    def newFolder(self, folderName, folderClass, pHandle):
        """Add a new folder with a given name and class and parent item.
        """
        newItem = NWItem(self)
        newItem.setName(folderName)
        newItem.setType(nwItemType.FOLDER)
        newItem.setClass(folderClass)
        newItem.setStatus(0)
        self.projTree.append(None, pHandle, newItem)
        return newItem.itemHandle

    def newFile(self, fileName, fileClass, pHandle):
        """Add a new file with a given name and class, and set a default
        layout based on the class. SCENE for NOVEL, and otherwise NOTE.
        """
        newItem = NWItem(self)
        newItem.setName(fileName)
        newItem.setType(nwItemType.FILE)
        if fileClass == nwItemClass.NOVEL:
            newItem.setLayout(nwItemLayout.SCENE)
        else:
            newItem.setLayout(nwItemLayout.NOTE)
        newItem.setClass(fileClass)
        newItem.setStatus(0)
        self.projTree.append(None, pHandle, newItem)
        return newItem.itemHandle

    def trashFolder(self):
        """Add the special trash root folder to the project.
        """
        trashHandle = self.projTree.trashRoot()
        if trashHandle is None:
            newItem = NWItem(self)
            newItem.setName("Trash")
            newItem.setType(nwItemType.TRASH)
            newItem.setClass(nwItemClass.TRASH)
            self.projTree.append(None, None, newItem)
            return newItem.itemHandle

        return trashHandle

    ##
    #  Project Methods
    ##

    def newProject(self):
        """Create a new project by populating the project tree with a
        few starter items.
        """
        self.projName = "New Project"
        hNovel = self.newRoot("Novel",         nwItemClass.NOVEL)
        hChars = self.newRoot("Characters",    nwItemClass.CHARACTER)
        hWorld = self.newRoot("Plot",          nwItemClass.PLOT)
        hWorld = self.newRoot("World",         nwItemClass.WORLD)
        hChapt = self.newFolder("New Chapter", nwItemClass.NOVEL, hNovel)
        hScene = self.newFile("New Scene",     nwItemClass.NOVEL, hChapt)
        self.projOpened = time()
        self.setProjectChanged(True)
        self.saveProject(autoSave=True)
        return True

    def clearProject(self):
        """Clear the data for the current project, and set them to
        default values.
        """
        # Project Status
        self.projOpened  = 0
        self.projChanged = False
        self.projAltered = False
        self.saveCount   = 0
        self.autoCount   = 0

        # Project Tree
        self.projTree.clear()

        # Project Settings
        self.projPath    = None
        self.projMeta    = None
        self.projCache   = None
        self.projContent = None
        self.projDict    = None
        self.projFile    = nwFiles.PROJ_FILE
        self.projName    = ""
        self.bookTitle   = ""
        self.bookAuthors = []
        self.autoReplace = {}
        self.titleFormat = {
            "title"      : r"%title%",
            "chapter"    : r"Chapter %ch%: %title%",
            "unnumbered" : r"%title%",
            "scene"      : r"* * *",
            "section"    : r"",
        }
        self.spellCheck  = False
        self.autoOutline = True
        self.statusItems = NWStatus()
        self.statusItems.addEntry("New",     (100,100,100))
        self.statusItems.addEntry("Note",    (200, 50,  0))
        self.statusItems.addEntry("Draft",   (200,150,  0))
        self.statusItems.addEntry("Finished",( 50,200,  0))
        self.importItems = NWStatus()
        self.importItems.addEntry("New",     (100,100,100))
        self.importItems.addEntry("Minor",   (200, 50,  0))
        self.importItems.addEntry("Major",   (200,150,  0))
        self.importItems.addEntry("Main",    ( 50,200,  0))
        self.lastEdited = None
        self.lastViewed = None
        self.lastWCount = 0
        self.currWCount = 0
        self.novelWCount = 0
        self.notesWCount = 0

        return

    def openProject(self, fileName, overrideLock=False):
        """Open the project file provided, or if doesn't exist, assume
        it is a folder, and look for the file within it. If successful,
        parse the XML of the file and populate the project variables and
        build the tree of project items.
        """
        if not path.isfile(fileName):
            fileName = path.join(fileName, nwFiles.PROJ_FILE)
            if not path.isfile(fileName):
                self.makeAlert("File not found: %s" % fileName, nwAlert.ERROR)
                return False

        self.clearProject()
        self.projPath = path.abspath(path.dirname(fileName))
        logger.debug("Opening project: %s" % self.projPath)

        # Standard Folders and Files
        # ==========================

        if not self.ensureFolderStructure():
            return False

        self.projDict = path.join(self.projMeta, nwFiles.PROJ_DICT)

        # Check for Old Legacy Data
        # =========================

        errList = []
        for projItem in listdir(self.projPath):
            logger.verbose("Project contains: %s" % projItem)
            if projItem.startswith("data_"):
                errList = self._legacyDataFolder(projItem, errList)

        if errList:
            self.makeAlert(errList, nwAlert.ERROR)

        self._deprecatedFiles()

        # Project Lock
        # ============

        if overrideLock:
            self._clearLockFile()

        lockStatus = self._readLockFile()
        if len(lockStatus) > 0:
            if lockStatus[0] == "ERROR":
                logger.warning("Failed to check lock file")
            else:
                logger.error("Project is locked, so not opening")
                self.lockedBy = lockStatus
                self.clearProject()
                return False
        else:
            logger.verbose("Project is not locked")

        # Open The Project XML File
        # =========================

        try:
            nwXML = etree.parse(fileName)
        except Exception as e:
            self.makeAlert(["Failed to parse project xml.",str(e)], nwAlert.ERROR)

            # Trying to open backup file instead
            backFile = fileName[:-3]+"bak"
            if path.isfile(backFile):
                self.makeAlert("Attempting to open backup project file instead.", nwAlert.INFO)
                try:
                    nwXML = etree.parse(backFile)
                except Exception as e:
                    self.makeAlert(["Failed to parse project xml.",str(e)], nwAlert.ERROR)
                    self.clearProject()
                    return False
            else:
                self.clearProject()
                return False

        xRoot = nwXML.getroot()
        nwxRoot = xRoot.tag

        appVersion = "Unknown"
        hexVersion = "0x0"
        fileVersion = "Unknown"
        self.saveCount = 0
        self.autoCount = 0

        if "appVersion" in xRoot.attrib:
            appVersion = xRoot.attrib["appVersion"]
        if "hexVersion" in xRoot.attrib:
            hexVersion = xRoot.attrib["hexVersion"]
        if "fileVersion" in xRoot.attrib:
            fileVersion = xRoot.attrib["fileVersion"]

        # The following are deprecated and will be removed
        if "saveCount" in xRoot.attrib:
            self.saveCount = checkInt(xRoot.attrib["saveCount"], 0, False)
        if "autoCount" in xRoot.attrib:
            self.autoCount = checkInt(xRoot.attrib["autoCount"], 0, False)
        if "editTime" in xRoot.attrib:
            self.editTime = checkInt(xRoot.attrib["editTime"], 0, False)

        logger.verbose("XML root is %s" % nwxRoot)
        logger.verbose("File version is %s" % fileVersion)

        # Check File Type
        # ===============

        if not nwxRoot == "novelWriterXML":
            self.makeAlert(
                "Project file does not appear to be a novelWriterXML file.",
                nwAlert.ERROR
            )
            return False

        # Check Project Storage Version
        # =============================

        # Changes:
        # 1.0 : Original file format.
        # 1.1 : Changes the way documents are structure in the project
        #       folder from data_X, where X is the first hex value of
        #       the handle, to a single content folder.
        # 1.2 : Changes the way autoReplace entries are stored. The 1.1
        #       parser will lose the autoReplace settings if allowed to
        #       read the file. Introduced in version 0.10.

        if fileVersion == "1.0":
            msgBox = QMessageBox()
            msgRes = msgBox.question(self.theParent, "Old Project Version", (
                "The project file and data is created by a novelWriter version "
                "lower than 0.7. Do you want to upgrade the project to the "
                "most recent format?<br><br>Note that after the upgrade, you "
                "cannot open the project with an older version of novelWriter "
                "any more, so make sure you have a recent backup."
            ))
            if msgRes != QMessageBox.Yes:
                return False

        elif fileVersion != "1.1" and fileVersion != "1.2":
            self.makeAlert((
                "Unknown or unsupported novelWriter project file format. "
                "The project cannot be opened by this version of novelWriter. "
                "The file was saved with novelWriter version {vers:s}."
            ).format(
                vers = appVersion,
            ), nwAlert.ERROR)
            return False

        # Check novelWriter Version
        # =========================

        if int(hexVersion, 16) > int(nw.__hexversion__, 16) and self.mainConf.showGUI:
            msgBox = QMessageBox()
            msgRes = msgBox.question(self.theParent, "Version Conflict", (
                "This project was saved by a newer version of novelWriter, version %s. "
                "This is version %s. If you continue to open the project, some attributes "
                "and settings may not be preserved. Continue opening the project?"
            ) % (
                appVersion, nw.__version__
            ))
            if msgRes != QMessageBox.Yes:
                return False

        # Start Parsing XML
        # =================

        for xChild in xRoot:
            if xChild.tag == "project":
                logger.debug("Found project meta")
                for xItem in xChild:
                    if xItem.text is None:
                        continue
                    if xItem.tag == "name":
                        logger.verbose("Working Title: '%s'" % xItem.text)
                        self.projName = xItem.text
                    elif xItem.tag == "title":
                        logger.verbose("Title is '%s'" % xItem.text)
                        self.bookTitle = xItem.text
                    elif xItem.tag == "author":
                        logger.verbose("Author: '%s'" % xItem.text)
                        self.bookAuthors.append(xItem.text)
                    elif xItem.tag == "saveCount":
                        self.saveCount = checkInt(xItem.text, 0)
                    elif xItem.tag == "autoCount":
                        self.autoCount = checkInt(xItem.text, 0)
                    elif xItem.tag == "editTime":
                        self.editTime = checkInt(xItem.text, 0)

                    # The following is deprecated, and will be removed
                    elif xItem.tag == "backup":
                        self.doBackup = checkBool(xItem.text, False)

            elif xChild.tag == "settings":
                logger.debug("Found project settings")
                for xItem in xChild:
                    if xItem.text is None:
                        continue
                    if xItem.tag == "doBackup":
                        self.doBackup = checkBool(xItem.text, False)
                    elif xItem.tag == "spellCheck":
                        self.spellCheck = checkBool(xItem.text, False)
                    elif xItem.tag == "autoOutline":
                        self.autoOutline = checkBool(xItem.text, True)
                    elif xItem.tag == "lastEdited":
                        self.lastEdited = checkString(xItem.text, None, True)
                    elif xItem.tag == "lastViewed":
                        self.lastViewed = checkString(xItem.text, None, True)
                    elif xItem.tag == "lastWordCount":
                        self.lastWCount = checkInt(xItem.text, 0, False)
                    elif xItem.tag == "novelWordCount":
                        self.novelWCount = checkInt(xItem.text, 0, False)
                    elif xItem.tag == "notesWordCount":
                        self.notesWCount = checkInt(xItem.text, 0, False)
                    elif xItem.tag == "status":
                        self.statusItems.unpackEntries(xItem)
                    elif xItem.tag == "importance":
                        self.importItems.unpackEntries(xItem)
                    elif xItem.tag == "autoReplace":
                        for xEntry in xItem:
                            if xEntry.tag == "entry":
                                if "key" in xEntry.attrib:
                                    self.autoReplace[xEntry.attrib["key"]] = checkString(
                                        xEntry.text, None, False
                                    )
                            else: # Old format
                                self.autoReplace[xEntry.tag] = checkString(
                                    xEntry.text, None, False
                                )
                    elif xItem.tag == "titleFormat":
                        titleFormat = self.titleFormat.copy()
                        for xEntry in xItem:
                            titleFormat[xEntry.tag] = checkString(xEntry.text, "", False)
                        self.setTitleFormat(titleFormat)

            elif xChild.tag == "content":
                logger.debug("Found project content")
                self.projTree.unpackXML(xChild)

        self.optState.loadSettings()

        # Update recent projects
        self.mainConf.updateRecentCache(self.projPath, self.projName, self.lastWCount, time())
        self.mainConf.saveRecentCache()

        self.theParent.setStatus("Opened Project: %s" % self.projName)

        self._scanProjectFolder()
        self.setProjectChanged(False)
        self.projOpened = time()
        self.projAltered = False
        self._writeLockFile()

        return True

    def saveProject(self, autoSave=False):
        """Save the project main XML file. The saving command itself
        uses a temporary filename, and the file is renamed afterwards to
        make sure if the save fails, we're not left with a truncated
        file.
        """
        if self.projPath is None:
            self.makeAlert(
                "Project path not set, cannot save project.", nwAlert.ERROR
            )
            return False

        saveTime = time()
        if not self.ensureFolderStructure():
            return False

        logger.debug("Saving project: %s" % self.projPath)

        if autoSave:
            self.autoCount += 1
        else:
            self.saveCount += 1

        # Root element and project details
        logger.debug("Writing project meta")
        nwXML = etree.Element("novelWriterXML", attrib={
            "appVersion"  : str(nw.__version__),
            "hexVersion"  : str(nw.__hexversion__),
            "fileVersion" : "1.2",
            "timeStamp"   : formatTimeStamp(saveTime),
        })

        editTime = int(self.editTime + saveTime - self.projOpened)
        wcNovel, wcNotes = self.projTree.sumWords()
        self.novelWCount = wcNovel
        self.notesWCount = wcNotes
        self.setProjectWordCount(wcNovel + wcNotes)

        # Save Project Meta
        xProject = etree.SubElement(nwXML, "project")
        self._packProjectValue(xProject, "name", self.projName,  True)
        self._packProjectValue(xProject, "title", self.bookTitle, True)
        self._packProjectValue(xProject, "author", self.bookAuthors)
        self._packProjectValue(xProject, "saveCount", str(self.saveCount))
        self._packProjectValue(xProject, "autoCount", str(self.autoCount))
        self._packProjectValue(xProject, "editTime", str(editTime))

        # Save Project Settings
        xSettings = etree.SubElement(nwXML, "settings")
        self._packProjectValue(xSettings, "doBackup", self.doBackup)
        self._packProjectValue(xSettings, "spellCheck", self.spellCheck)
        self._packProjectValue(xSettings, "autoOutline", self.autoOutline)
        self._packProjectValue(xSettings, "lastEdited", self.lastEdited)
        self._packProjectValue(xSettings, "lastViewed", self.lastViewed)
        self._packProjectValue(xSettings, "lastWordCount", self.currWCount)
        self._packProjectValue(xSettings, "novelWordCount", wcNovel)
        self._packProjectValue(xSettings, "notesWordCount", wcNotes)
        self._packProjectKeyValue(xSettings, "autoReplace", self.autoReplace)

        xTitleFmt = etree.SubElement(xSettings, "titleFormat")
        for aKey, aValue in self.titleFormat.items():
            if len(aKey) > 0:
                self._packProjectValue(xTitleFmt, aKey, aValue)

        xStatus = etree.SubElement(xSettings,"status")
        self.statusItems.packEntries(xStatus)
        xStatus = etree.SubElement(xSettings,"importance")
        self.importItems.packEntries(xStatus)

        # Save Tree Content
        logger.debug("Writing project content")
        self.projTree.packXML(nwXML)

        # Write the xml tree to file
        tempFile = path.join(self.projPath, self.projFile+"~")
        saveFile = path.join(self.projPath, self.projFile)
        backFile = path.join(self.projPath, self.projFile[:-3]+"bak")
        try:
            with open(tempFile, mode="wb") as outFile:
                outFile.write(etree.tostring(
                    nwXML,
                    pretty_print    = True,
                    encoding        = "utf-8",
                    xml_declaration = True
                ))
        except Exception as e:
            self.makeAlert(["Failed to save project.", str(e)], nwAlert.ERROR)
            return False

        # If we're here, the file was successfully saved,
        # so let's sort out the temps and backups
        if path.isfile(backFile):
            unlink(backFile)
        if path.isfile(saveFile):
            rename(saveFile, backFile)
        rename(tempFile, saveFile)

        # Save project GUI options
        self.optState.saveSettings()

        # Update recent projects
        self.mainConf.updateRecentCache(self.projPath, self.projName, self.currWCount, saveTime)
        self.mainConf.saveRecentCache()

        self._writeLockFile()
        self.theParent.setStatus("Saved Project: %s" % self.projName)
        self.setProjectChanged(False)

        return True

    def closeProject(self):
        """Close the current project and clear all meta data.
        """
        self.optState.saveSettings()
        self.projTree.writeToCFiles()
        self._appendSessionStats()
        self._clearLockFile()
        self.clearProject()
        self.lockedBy = None
        return True

    def ensureFolderStructure(self):
        """Ensure that all necessary folders exist in the project
        folder.
        """
        if self.projPath is None or self.projPath == "":
            return False

        self.projMeta    = path.join(self.projPath, "meta")
        self.projCache   = path.join(self.projPath, "cache")
        self.projContent = path.join(self.projPath, "content")

        if not self._checkFolder(self.projMeta):
            return False
        if not self._checkFolder(self.projCache):
            return False
        if not self._checkFolder(self.projContent):
            return False

        return True

    ##
    #  Backup Project
    ##

    def zipIt(self, doNotify):
        """Create a zip file of the entire project.
        """
        logger.info("Backing up project")
        self.theParent.statusBar.setStatus("Backing up project ...")

        if self.mainConf.backupPath is None or self.mainConf.backupPath == "":
            self.theParent.makeAlert((
                "Cannot backup project because no backup path is set. "
                "Please set a valid backup location in Tools > Preferences."
            ), nwAlert.ERROR)
            return False

        if self.projName is None or self.projName == "":
            self.theParent.makeAlert((
                "Cannot backup project because no project name is set. "
                "Please set a Working Title in Project > Project Settings."
            ), nwAlert.ERROR)
            return False

        if not path.isdir(self.mainConf.backupPath):
            self.theParent.makeAlert((
                "Cannot backup project because the backup path does not exist. "
                "Please set a valid backup location in Tools > Preferences."
            ), nwAlert.ERROR)
            return False

        cleanName = self.getFileSafeProjectName()
        baseDir = path.abspath(path.join(self.mainConf.backupPath, cleanName))
        if not path.isdir(baseDir):
            try:
                mkdir(baseDir)
                logger.debug("Created folder %s" % baseDir)
            except Exception as e:
                self.theParent.makeAlert(
                    ["Could not create backup folder.",str(e)],
                    nwAlert.ERROR
                )
                return False

        if path.commonpath([self.projPath, baseDir]) == self.projPath:
            self.theParent.makeAlert((
                "Cannot backup project because the backup path is within the "
                "project folder to be backed up. Please choose a different "
                "backup path in Tools > Preferences."
            ), nwAlert.ERROR)
            return False

        archName = "Backup from %s" % formatTimeStamp(time(), fileSafe=True)
        baseName = path.join(baseDir, archName)

        try:
            self._clearLockFile()
            make_archive(baseName, "zip", self.projPath, ".")
            self._writeLockFile()
            if doNotify:
                self.theParent.makeAlert(
                    "Backup archive file written to: %s.zip" % path.join(cleanName, archName),
                    nwAlert.INFO
                )
            else:
                logger.info("Backup written to: %s" % archName)
        except Exception as e:
            self.theParent.makeAlert(
                ["Could not write backup archive.",str(e)],
                nwAlert.ERROR
            )
            return False

        self.theParent.statusBar.setStatus("Project backed up to '%s.zip'" % baseName)

        return True

    ##
    #  Setters
    ##

    def setProjectPath(self, projPath, newProject=False):
        """Set the project storage path, and also expand ~ to the user
        directory using the path library.
        """
        if projPath is None or projPath == "":
            self.projPath = None
        else:
            if projPath.startswith("~"):
                projPath = path.expanduser(projPath)
            self.projPath = path.abspath(projPath)

        if newProject and self.mainConf.showGUI:
            if listdir(self.projPath):
                self.theParent.makeAlert((
                    "New project folder is not empty. "
                    "Each project requires a dedicated project folder."
                ), nwAlert.ERROR)
                return False

        self.ensureFolderStructure()
        self.setProjectChanged(True)

        return True

    def setProjectName(self, projName):
        """Set the project name (working title), This is the the title
        used for backup files etc.
        """
        self.projName = projName.strip()
        self.setProjectChanged(True)
        return True

    def setBookTitle(self, bookTitle):
        """Set the boom title, that is, the title to include in exports.
        """
        self.bookTitle = bookTitle.strip()
        self.setProjectChanged(True)
        return True

    def setBookAuthors(self, bookAuthors):
        """A line separated list of book authors, parsed into an array.
        """
        self.bookAuthors = []
        for bookAuthor in bookAuthors.split("\n"):
            bookAuthor = bookAuthor.strip()
            if bookAuthor == "":
                continue
            self.bookAuthors.append(bookAuthor)
        self.setProjectChanged(True)
        return True

    def setProjBackup(self, doBackup):
        """Set whether projects should be backed up or not. The user
        will notified in case dependant settings are missing.
        """
        self.doBackup = doBackup
        if doBackup:
            if not path.isdir(self.mainConf.backupPath):
                self.theParent.makeAlert((
                    "You must set a valid backup path in preferences to use "
                    "the automatic project backup feature."
                ), nwAlert.WARN)
            if self.projName == "":
                self.theParent.makeAlert((
                    "You must set a valid project name in project settings to "
                    "use the automatic project backup feature."
                ), nwAlert.WARN)
        return True

    def setSpellCheck(self, theMode):
        """Enable/disable spell checking.
        """
        if self.spellCheck != theMode:
            self.spellCheck = theMode
            self.setProjectChanged(True)
        return True

    def setAutoOutline(self, theMode):
        """Enable/disable automatic update of project outline.
        """
        if self.autoOutline != theMode:
            self.autoOutline = theMode
            self.setProjectChanged(True)
        return True

    def setTreeOrder(self, newOrder):
        """A list representing the liner/flattened order of project
        items in the GUI project tree. The user can rearrange the order
        by drag-and-drop. Forwarded to the NWTree class.
        """
        if len(self.projTree) != len(newOrder):
            logger.warning("Size of new and old tree order do not match")
        self.projTree.setOrder(newOrder)
        self.setProjectChanged(True)
        return True

    def setLastEdited(self, tHandle):
        """Set last edited project item.
        """
        if self.lastEdited != tHandle:
            self.lastEdited = tHandle
            self.setProjectChanged(True)
        return True

    def setLastViewed(self, tHandle):
        """Set last viewed project item.
        """
        if self.lastViewed != tHandle:
            self.lastViewed = tHandle
            self.setProjectChanged(True)
        return True

    def setProjectWordCount(self, theCount):
        """Set the current project word count.
        """
        if self.currWCount != theCount:
            self.currWCount = theCount
            self.setProjectChanged(True)
        return True

    def setStatusColours(self, newCols):
        """Update the list of novel file status flags. Also iterate
        through the project and replace keys that have been renamed.
        """
        replaceMap = self.statusItems.setNewEntries(newCols)
        for nwItem in self.projTree:
            if nwItem.itemClass == nwItemClass.NOVEL:
                if nwItem.itemStatus in replaceMap.keys():
                    nwItem.setStatus(replaceMap[nwItem.itemStatus])
        self.setProjectChanged(True)
        return

    def setImportColours(self, newCols):
        """Update the list of note file importance flags. Also iterate
        through the project and replace keys that have been renamed.
        """
        replaceMap = self.importItems.setNewEntries(newCols)
        for nwItem in self.projTree:
            if nwItem.itemClass != nwItemClass.NOVEL:
                if nwItem.itemStatus in replaceMap.keys():
                    nwItem.setStatus(replaceMap[nwItem.itemStatus])
        self.setProjectChanged(True)
        return

    def setAutoReplace(self, autoReplace):
        """Update the auto-replace dictionary. This replaces the entire
        dictionary, so alterations have to be made in a copy.
        """
        self.autoReplace = autoReplace
        return

    def setTitleFormat(self, titleFormat):
        """Set the formatting of titles in the project.
        """
        for valKey, valEntry in titleFormat.items():
            if valKey in self.titleFormat:
                self.titleFormat[valKey] = checkString(valEntry, self.titleFormat[valKey], False)
        return

    def setProjectChanged(self, bValue):
        """Toggle the project changed flag, and propagate the
        information to the GUI statusbar.
        """
        self.projChanged = bValue
        self.theParent.setProjectStatus(self.projChanged)
        if bValue:
            # If we've changed the project at all, this should be True
            self.projAltered = True
        return self.projChanged

    ##
    #  Getters
    ##

    def getFileSafeProjectName(self):
        """Returns a filename safe version of the project name.
        """
        cleanName = ""
        for c in self.projName.strip():
            if c.isalpha() or c.isdigit() or c == " ":
                cleanName += c
        return cleanName

    def getSessionWordCount(self):
        """Returns the number of words added or removed this session.
        """
        return self.currWCount - self.lastWCount

    def getProjectItems(self):
        """This function ensures that the item tree loaded is sent to
        the GUI tree view in such a way that the tree can be built. That
        is, the parent item must be sent before its child. In principle,
        a proper XML file will already ensure that, but in the event the
        order has been altered, or a file is orphaned, this function is
        capable of handling it.
        """
        sentItems = []
        iterItems = self.projTree.handles()
        n = 0
        nMax = len(iterItems)
        while n < nMax:
            tHandle = iterItems[n]
            tItem   = self.projTree[tHandle]
            n += 1
            if n > 10000:
                return # Just in case
            if tItem is None:
                # Technically a bug since treeOrder is built from the
                # same data as projTree
                continue
            elif tItem.parHandle is None:
                # Item is a root, or already been identified as an
                # orphaned item
                sentItems.append(tHandle)
                yield tItem
            elif tItem.parHandle in sentItems:
                # Item's parent has been sent, so all is fine
                sentItems.append(tHandle)
                yield tItem
            elif tItem.parHandle in iterItems:
                # Item's parent exists, but hasn't been sent yet, so add
                # it again to the end
                logger.warning("Item %s found before its parent" % tHandle)
                iterItems.append(tHandle)
                nMax = len(iterItems)
            else:
                # Item is orphaned
                logger.error("Item %s has no parent in current tree" % tHandle)
                tItem.setParent(None)
                yield tItem

    ##
    #  Class Methods
    ##

    def countStatus(self):
        """Count how many times the various status flags are used in the
        project tree. The counts themselves are kept in the NWStatus
        objects. This is essentially a refresh.
        """
        self.statusItems.resetCounts()
        self.importItems.resetCounts()
        for nwItem in self.projTree:
            if nwItem.itemClass == nwItemClass.NOVEL:
                self.statusItems.countEntry(nwItem.itemStatus)
            else:
                self.importItems.countEntry(nwItem.itemStatus)
        return

    ##
    #  Internal Functions
    ##

    def _readLockFile(self):
        """Reads the lock file in the project folder.
        """
        if self.projPath is None:
            return ["ERROR"]

        lockFile = path.join(self.projPath, nwFiles.PROJ_LOCK)
        if not path.isfile(lockFile):
            return []

        try:
            with open(lockFile, mode="r", encoding="utf8") as inFile:
                theData = inFile.read()
                theLines = theData.splitlines()
                if len(theLines) == 4:
                    return theLines
                else:
                    return ["ERROR"]

        except Exception as e:
            logger.error("Failed to read project lockfile")
            logger.error(str(e))
            return ["ERROR"]

        return ["ERROR"]

    def _writeLockFile(self):
        """Writes a lock file to the project folder.
        """
        if self.projPath is None:
            return False

        lockFile = path.join(self.projPath, nwFiles.PROJ_LOCK)
        try:
            with open(lockFile, mode="w+", encoding="utf8") as outFile:
                outFile.write("%s\n" % self.mainConf.hostName)
                outFile.write("%s\n" % self.mainConf.osType)
                outFile.write("%s\n" % self.mainConf.kernelVer)
                outFile.write("%d\n" % time())

        except Exception as e:
            logger.error("Failed to write project lockfile")
            logger.error(str(e))
            return False

        return True

    def _clearLockFile(self):
        """Remove the lock file, if it exists.
        """
        if self.projPath is None:
            return False

        lockFile = path.join(self.projPath, nwFiles.PROJ_LOCK)
        if path.isfile(lockFile):
            try:
                unlink(lockFile)
                return True
            except Exception as e:
                logger.error("Failed to remove project lockfile")
                logger.error(str(e))
                return False

        return None

    def _checkFolder(self, thePath):
        """Check if a folder exists, and if it doesn't, create it.
        """
        if not path.isdir(thePath):
            try:
                mkdir(thePath)
                logger.debug("Created folder %s" % thePath)
            except Exception as e:
                self.makeAlert(["Could not create folder.",str(e)], nwAlert.ERROR)
                return False
        return True

    def _packProjectValue(self, xParent, theName, theValue, allowNone=True):
        """Pack a list of values into an xml element.
        """
        if not isinstance(theValue, list):
            theValue = [theValue]
        for aValue in theValue:
            if not isinstance(aValue, str):
                aValue = str(aValue)
            if aValue == "" and not allowNone: continue
            xItem = etree.SubElement(xParent, theName)
            xItem.text = aValue
        return

    def _packProjectKeyValue(self, xParent, theName, theDict):
        """Pack the entries in the auto-replace dictionary.
        """
        xAutoRep = etree.SubElement(xParent, theName)
        for aKey, aValue in theDict.items():
            if len(aKey) > 0:
                xEntry = etree.SubElement(xAutoRep, "entry", attrib={"key": aKey})
                xEntry.text = aValue
        return

    def _scanProjectFolder(self):
        """Scan the project folder and check that the files in it are
        also in the project XML file. If they aren't, import them as
        orphaned files so the user can either delete them, or put them
        back into the project tree.
        """
        if self.projPath is None:
            return

        # Then check the files in the data folder
        logger.debug("Checking files in project content folder")
        orphanFiles = []
        for fileItem in listdir(self.projContent):
            if not fileItem.endswith(".nwd"):
                logger.warning("Skipping file %s" % fileItem)
                continue
            if len(fileItem) != 17:
                logger.warning("Skipping file %s" % fileItem)
                continue
            fHandle = fileItem[:13]
            if fHandle in self.projTree:
                logger.debug("Checking file %s, handle %s: OK" % (fileItem, fHandle))
            else:
                logger.debug("Checking file %s, handle %s: Orphaned" % (fileItem, fHandle))
                orphanFiles.append(fHandle)

        # Report status
        if len(orphanFiles) > 0:
            self.makeAlert(
                "Found %d orphaned file(s) in project folder." % len(orphanFiles),
                nwAlert.WARN
            )
        else:
            logger.debug("File check OK")
            return

        # Handle orphans
        aDoc = NWDoc(self, self.theParent)
        nOrph = 0
        for oHandle in orphanFiles:

            # Look for meta data
            oName = ""
            if aDoc.openDocument(oHandle, showStatus=False, isOrphan=True):
                oName, oPath, oClass, oLayout = aDoc.getMeta()

            if oName == "":
                nOrph += 1
                oName = "Orphaned File %d" % nOrph

            if oClass is None:
                oClass = nwItemClass.NO_CLASS
            if oLayout is None:
                oLayout = nwItemLayout.NO_LAYOUT

            orphItem = NWItem(self)
            orphItem.setName(oName)
            orphItem.setType(nwItemType.FILE)
            orphItem.setClass(oClass)
            orphItem.setLayout(oLayout)
            self.projTree.append(oHandle, None, orphItem)

        return

    def _appendSessionStats(self):
        """Append session statistics to the sessions log file.
        """
        if not self.ensureFolderStructure():
            return False

        sessionFile = path.join(self.projMeta, nwFiles.SESS_STATS)
        isFile = path.isfile(sessionFile)

        with open(sessionFile, mode="a+", encoding="utf8") as outFile:
            if not isFile:
                # It's a new file, so add a header
                if self.lastWCount > 0:
                    outFile.write("# Offset %d\n" % self.lastWCount)
                outFile.write("# %-17s  %-19s  %8s  %8s\n" % (
                    "Start Time", "End Time", "Novel", "Notes"
                ))

            outFile.write("%-19s  %-19s  %8d  %8d\n" % (
                formatTimeStamp(self.projOpened),
                formatTimeStamp(time()),
                self.novelWCount,
                self.notesWCount,
            ))

        return True

    ##
    #  Legacy Data Structure Handlers
    ##

    def _legacyDataFolder(self, theFolder, errList):
        """Clean up legacy data folders.
        """
        theData = path.join(self.projPath, theFolder)
        if not path.isdir(theData):
            errList.append("Not a folder: %s" % theData)
            return errList

        logger.info("Old data folder %s found" % theFolder)

        # Move Documents to Content
        # =========================
        for dataItem in listdir(theData):
            theFile = path.join(theData, dataItem)
            if not path.isfile(theFile):
                theErr = self._moveUnknownItem(theData, dataItem)
                if theErr:
                    errList.append(theErr)
                continue

            if len(dataItem) == 21 and dataItem.endswith("_main.nwd"):
                tHandle = theFolder[-1]+dataItem[:12]
                newPath = path.join(self.projContent, tHandle+".nwd")
                try:
                    rename(theFile, newPath)
                    logger.info("Moved file: %s" % theFile)
                    logger.info("New location: %s" % newPath)
                except Exception as e:
                    logger.error(str(e))
                    errList.append("Could not move: %s" % theFile)

            elif len(dataItem) == 21 and dataItem.endswith("_main.bak"):
                try:
                    unlink(theFile)
                    logger.info("Deleted file: %s" % theFile)
                except Exception as e:
                    logger.error(str(e))
                    errList.append("Could not delete: %s" % theFile)

            else:
                theErr = self._moveUnknownItem(theData, dataItem)
                if theErr:
                    errList.append(theErr)

        # Remove Data Folder
        # ==================
        try:
            rmdir(theData)
            logger.info("Removed folder: %s" % theFolder)
        except:
            errList.append("Failed to remove: %s" % theFolder)

        return errList

    def _moveUnknownItem(self, theDir, theItem):
        """Move an item that doesn't belong in the project folder to
        a junk folder.
        """
        theJunk = path.join(self.projPath, "junk")
        if not self._checkFolder(theJunk):
            return "Could not make folder: %s" % theJunk

        theSrc = path.join(theDir, theItem)
        theDst = path.join(theJunk, theItem)

        try:
            rename(theSrc, theDst)
            logger.info("Moved to junk: %s" % theSrc)
        except Exception as e:
            logger.error(str(e))
            return "Could not move item %s to junk." % theSrc

        return ""

    def _deprecatedFiles(self):
        """Delete files that are no longer used by novelWriter.
        """
        rmList = []
        rmList.append(path.join(self.projCache, "nwProject.nwx.0"))
        rmList.append(path.join(self.projCache, "nwProject.nwx.1"))
        rmList.append(path.join(self.projCache, "nwProject.nwx.2"))
        rmList.append(path.join(self.projCache, "nwProject.nwx.3"))
        rmList.append(path.join(self.projCache, "nwProject.nwx.4"))
        rmList.append(path.join(self.projCache, "nwProject.nwx.5"))
        rmList.append(path.join(self.projCache, "nwProject.nwx.6"))
        rmList.append(path.join(self.projCache, "nwProject.nwx.7"))
        rmList.append(path.join(self.projCache, "nwProject.nwx.8"))
        rmList.append(path.join(self.projCache, "nwProject.nwx.9"))
        rmList.append(path.join(self.projMeta,  "mainOptions.json"))
        rmList.append(path.join(self.projMeta,  "exportOptions.json"))
        rmList.append(path.join(self.projMeta,  "outlineOptions.json"))
        rmList.append(path.join(self.projMeta,  "timelineOptions.json"))
        rmList.append(path.join(self.projMeta,  "docMergeOptions.json"))
        rmList.append(path.join(self.projMeta,  "sessionLogOptions.json"))

        for rmFile in rmList:
            if path.isfile(rmFile):
                logger.info("Deleting: %s" % rmFile)
                try:
                    unlink(rmFile)
                except Exception as e:
                    logger.error(str(e))

        return

# END Class NWProject
