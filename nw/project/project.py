# -*- coding: utf-8 -*-
"""novelWriter Project Wrapper

 novelWriter – Project Wrapper
===============================
 Class holding a project

 File History:
 Created: 2018-09-29 [0.0.1]

"""

import logging
import nw

from os import path, mkdir, listdir
from shutil import copyfile
from lxml import etree
from hashlib import sha256
from datetime import datetime
from time import time

from nw.project.status import NWStatus
from nw.project.item import NWItem
from nw.common import checkString, checkBool, checkInt
from nw.constants import (
    nwFiles, nwConst, nwItemType, nwItemClass, nwItemLayout, nwAlert
)

logger = logging.getLogger(__name__)

class NWProject():

    def __init__(self, theParent):

        # Internal
        self.theParent   = theParent
        self.mainConf    = self.theParent.mainConf
        self.projOpened  = None # The time stamp of when the project file was opened
        self.projChanged = None # The project has unsaved changes
        self.projAltered = None # The project has been altered this session

        # Debug
        self.handleSeed = None

        # Class Settings
        self.projTree  = None # Holds all the items of the project
        self.treeOrder = None # The order of the tree items on the tree view
        self.treeRoots = None # The root items of the tree
        self.trashRoot = None # The handle of the trash root folder
        self.projPath  = None # The full path to where the currently open project is saved
        self.projMeta  = None # The full path to the project's meta data folder
        self.projCache = None # The full path to the project's cache folder
        self.projDict  = None # The spell check dictionary
        self.projFile  = None # The file name of the project main xml file

        # Project Meta
        self.projName    = None
        self.bookTitle   = None
        self.bookAuthors = None

        # Various
        self.autoReplace = None

        # Project Settings
        self.spellCheck  = False
        self.statusItems = None
        self.importItems = None
        self.lastEdited  = None
        self.lastViewed  = None
        self.lastWCount  = 0
        self.currWCount  = 0
        self.doBackup    = True

        # Set Defaults
        self.clearProject()

        # Internal Mapping
        self.makeAlert = self.theParent.makeAlert

        return

    ##
    #  Item Methods
    ##

    def newRoot(self, rootName, rootClass):
        if not self.checkRootUnique(rootClass):
            self.makeAlert("Duplicate root item detected!", nwAlert.ERROR)
            return None
        newItem = NWItem(self)
        newItem.setName(rootName)
        newItem.setType(nwItemType.ROOT)
        newItem.setClass(rootClass)
        newItem.setStatus(0)
        self._appendItem(None,None,newItem)
        return newItem.itemHandle

    def newFolder(self, folderName, folderClass, pHandle):
        newItem = NWItem(self)
        newItem.setName(folderName)
        newItem.setType(nwItemType.FOLDER)
        newItem.setClass(folderClass)
        newItem.setStatus(0)
        self._appendItem(None,pHandle,newItem)
        return newItem.itemHandle

    def newFile(self, fileName, fileClass, pHandle):
        newItem = NWItem(self)
        newItem.setName(fileName)
        newItem.setType(nwItemType.FILE)
        if fileClass == nwItemClass.NOVEL:
            newItem.setLayout(nwItemLayout.SCENE)
        else:
            newItem.setLayout(nwItemLayout.NOTE)
        newItem.setClass(fileClass)
        newItem.setStatus(0)
        self._appendItem(None,pHandle,newItem)
        return newItem.itemHandle

    def addTrash(self):
        newItem = NWItem(self)
        newItem.setName("Trash")
        newItem.setType(nwItemType.TRASH)
        newItem.setClass(nwItemClass.TRASH)
        self._appendItem(None,None,newItem)
        return newItem.itemHandle

    ##
    #  Project Methods
    ##

    def newProject(self):
        hNovel = self.newRoot("Novel",         nwItemClass.NOVEL)
        hChars = self.newRoot("Characters",    nwItemClass.CHARACTER)
        hWorld = self.newRoot("Plot",          nwItemClass.PLOT)
        hWorld = self.newRoot("World",         nwItemClass.WORLD)
        hChapt = self.newFolder("New Chapter", nwItemClass.NOVEL, hNovel)
        hScene = self.newFile("New Scene",     nwItemClass.NOVEL, hChapt)
        self.projOpened = time()
        self.setProjectChanged(True)
        return True

    def clearProject(self):

        self.projOpened  = None
        self.projChanged = None
        self.projAltered = False

        # Project Settings
        self.projTree    = {}
        self.treeOrder   = []
        self.treeRoots   = []
        self.trashRoot   = None
        self.projPath    = None
        self.projMeta    = None
        self.projCache   = None
        self.projDict    = None
        self.projFile    = nwFiles.PROJ_FILE
        self.projName    = ""
        self.bookTitle   = ""
        self.bookAuthors = []
        self.autoReplace = {}
        self.spellCheck  = False
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

        return

    def openProject(self, fileName):

        if not path.isfile(fileName):
            fileName = path.join(fileName, nwFiles.PROJ_FILE)
            if not path.isfile(fileName):
                self.makeAlert("File not found: %s" % fileName, nwAlert.ERROR)
                return False

        self.clearProject()
        self.projPath = path.dirname(fileName)
        logger.debug("Opening project: %s" % self.projPath)

        self.projMeta  = path.join(self.projPath,"meta")
        self.projCache = path.join(self.projPath,"cache")
        self.projDict  = path.join(self.projMeta, nwFiles.PROJ_DICT)

        if not self._checkFolder(self.projMeta):
            return
        if not self._checkFolder(self.projCache):
            return

        try:
            nwXML = etree.parse(fileName)
        except Exception as e:
            self.makeAlert(["Failed to parse project xml.",str(e)], nwAlert.ERROR)
            self.clearProject()
            return False

        xRoot   = nwXML.getroot()
        nwxRoot = xRoot.tag

        appVersion  = xRoot.attrib["appVersion"]
        fileVersion = xRoot.attrib["fileVersion"]

        logger.verbose("XML root is %s" % nwxRoot)
        logger.verbose("File version is %s" % fileVersion)

        if not nwxRoot == "novelWriterXML" or not fileVersion == "1.0":
            self.makeAlert(
                "Project file does not appear to be a novelWriterXML file version 1.0",
                nwAlert.ERROR
            )
            return False

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
                    elif xItem.tag == "backup":
                        self.doBackup = checkBool(xItem.text,False)
            elif xChild.tag == "settings":
                logger.debug("Found project settings")
                for xItem in xChild:
                    if xItem.text is None:
                        continue
                    if xItem.tag == "spellCheck":
                        self.spellCheck = checkBool(xItem.text,False)
                    elif xItem.tag == "lastEdited":
                        self.lastEdited = checkString(xItem.text,None,True)
                    elif xItem.tag == "lastViewed":
                        self.lastViewed = checkString(xItem.text,None,True)
                    elif xItem.tag == "lastWordCount":
                        self.lastWCount = checkInt(xItem.text,0,False)
                    elif xItem.tag == "status":
                        self.statusItems.unpackEntries(xItem)
                    elif xItem.tag == "importance":
                        self.importItems.unpackEntries(xItem)
                    elif xItem.tag == "autoReplace":
                        for xEntry in xItem:
                            self.autoReplace[xEntry.tag] = checkString(xEntry.text,None,False)
            elif xChild.tag == "content":
                logger.debug("Found project content")
                for xItem in xChild:
                    itemAttrib = xItem.attrib
                    if "handle" in xItem.attrib:
                        tHandle = itemAttrib["handle"]
                    else:
                        logger.error("Skipping entry missing handle")
                        continue
                    if "parent" in xItem.attrib:
                        pHandle = itemAttrib["parent"]
                    else:
                        pHandle = None
                    nwItem = NWItem(self)
                    for xValue in xItem:
                        nwItem.setFromTag(xValue.tag,xValue.text)
                    self._appendItem(tHandle,pHandle,nwItem)

        self.mainConf.setRecent(self.projPath)
        self.theParent.setStatus("Opened Project: %s" % self.projName)

        self._scanProjectFolder()
        self.setProjectChanged(False)
        self.projOpened = time()
        self.projAltered = False

        return True

    def saveProject(self, isAuto=False):

        if self.projPath is None:
            self.makeAlert("Project path not set, cannot save.", nwAlert.ERROR)
            return False

        self.projMeta  = path.join(self.projPath,"meta")
        self.projCache = path.join(self.projPath,"cache")

        if not self._checkFolder(self.projPath):  return
        if not self._checkFolder(self.projMeta):  return
        if not self._checkFolder(self.projCache): return

        logger.debug("Saving project: %s" % self.projPath)

        # Save a copy of the current file, just in case
        if not isAuto:
            self._maintainPrevious()

        # Root element and project details
        logger.debug("Writing project meta")
        nwXML = etree.Element("novelWriterXML",attrib={
            "appVersion"  : str(nw.__version__),
            "fileVersion" : "1.0",
            "timeStamp"   : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        # Save Project Meta
        xProject = etree.SubElement(nwXML, "project")
        self._saveProjectValue(xProject, "name", self.projName,  True)
        self._saveProjectValue(xProject, "title", self.bookTitle, True)
        self._saveProjectValue(xProject, "author", self.bookAuthors)
        self._saveProjectValue(xProject, "backup", self.doBackup)

        # Save Project Settings
        xSettings = etree.SubElement(nwXML, "settings")
        self._saveProjectValue(xSettings, "spellCheck", self.spellCheck)
        self._saveProjectValue(xSettings, "lastEdited", self.lastEdited)
        self._saveProjectValue(xSettings, "lastViewed", self.lastViewed)
        self._saveProjectValue(xSettings, "lastWordCount", self.currWCount)
        xAutoRep = etree.SubElement(xSettings, "autoReplace")
        for aKey, aValue in self.autoReplace.items():
            if len(aKey) > 0:
                self._saveProjectValue(xAutoRep,aKey,aValue)

        xStatus = etree.SubElement(xSettings,"status")
        self.statusItems.packEntries(xStatus)
        xStatus = etree.SubElement(xSettings,"importance")
        self.importItems.packEntries(xStatus)

        # Save Tree Content
        logger.debug("Writing project content")
        xContent = etree.SubElement(nwXML, "content", attrib={"count":str(len(self.treeOrder))})
        for tHandle in self.treeOrder:
            self.projTree[tHandle].packXML(xContent)

        # Write the xml tree to file
        saveFile = path.join(self.projPath,self.projFile)
        try:
            with open(saveFile,mode="wb") as outFile:
                outFile.write(etree.tostring(
                    nwXML,
                    pretty_print    = True,
                    encoding        = "utf-8",
                    xml_declaration = True
                ))
        except Exception as e:
            self.makeAlert(["Failed to save project.",str(e)], nwAlert.ERROR)
            return False

        self.mainConf.setRecent(self.projPath)
        self.theParent.setStatus("Saved Project: %s" % self.projName)
        self.setProjectChanged(False)

        return True

    def closeProject(self):
        self._appendSessionStats()
        self.clearProject()
        return True

    ##
    #  Set Functions
    ##

    def setProjectPath(self, projPath):
        if projPath is None or projPath == "":
            self.projPath = None
        else:
            if projPath.startswith("~"):
                projPath = path.expanduser(projPath)
            self.projPath = projPath
        self.setProjectChanged(True)
        return True

    def setProjectName(self, projName):
        self.projName = projName.strip()
        self.setProjectChanged(True)
        return True

    def setBookTitle(self, bookTitle):
        self.bookTitle = bookTitle.strip()
        self.setProjectChanged(True)
        return True

    def setBookAuthors(self, bookAuthors):
        self.bookAuthors = []
        for bookAuthor in bookAuthors.split("\n"):
            bookAuthor = bookAuthor.strip()
            if bookAuthor == "":
                continue
            self.bookAuthors.append(bookAuthor)
        self.setProjectChanged(True)
        return True

    def setProjBackup(self, doBackup):
        self.doBackup = False
        if doBackup:
            if not path.isdir(self.mainConf.backupPath):
                self.theParent.makeAlert((
                    "You must set a valid backup path in preferences to use "
                    "the automatic project backup feature."
                ), nwAlert.ERROR)
                return False
            if self.projName == "":
                self.theParent.makeAlert((
                    "You must set a valid project name in project settings to "
                    "use the automatic project backup feature."
                ), nwAlert.ERROR)
                return False
            self.doBackup = True
        return True

    def setSpellCheck(self, theMode):
        if self.spellCheck != theMode:
            self.spellCheck = theMode
            self.setProjectChanged(True)
        return True

    def setTreeOrder(self, newOrder):
        if len(self.treeOrder) != len(newOrder):
            logger.warning("Size of new and old tree order does not match")
        self.treeOrder = newOrder
        self.setProjectChanged(True)
        return True

    def setLastEdited(self, tHandle):
        if self.lastEdited != tHandle:
            self.lastEdited = tHandle
            self.setProjectChanged(True)
        return True

    def setLastViewed(self, tHandle):
        if self.lastViewed != tHandle:
            self.lastViewed = tHandle
            self.setProjectChanged(True)
        return True

    def setProjectWordCount(self, theCount):
        if self.currWCount != theCount:
            self.currWCount = theCount
            self.setProjectChanged(True)
        return True

    def getSessionWordCount(self):
        return self.currWCount - self.lastWCount

    def setStatusColours(self, newCols):
        replaceMap = self.statusItems.setNewEntries(newCols)
        if self.projTree is not None:
            for nwItem in self.projTree.values():
                if nwItem.itemClass == nwItemClass.NOVEL:
                    if nwItem.itemStatus in replaceMap.keys():
                        nwItem.setStatus(replaceMap[nwItem.itemStatus])
        self.setProjectChanged(True)
        return

    def setImportColours(self, newCols):
        replaceMap = self.importItems.setNewEntries(newCols)
        if self.projTree is not None:
            for nwItem in self.projTree.values():
                if nwItem.itemClass != nwItemClass.NOVEL:
                    if nwItem.itemStatus in replaceMap.keys():
                        nwItem.setStatus(replaceMap[nwItem.itemStatus])
        self.setProjectChanged(True)
        return

    def setAutoReplace(self, autoReplace):
        self.autoReplace = autoReplace
        return

    def setProjectChanged(self, bValue):
        self.projChanged = bValue
        self.theParent.setProjectStatus(self.projChanged)
        if bValue:
            # If we've changed the project at all, this should be True
            self.projAltered = True
        return self.projChanged

    ##
    #  Get Functions
    ##

    def getItem(self, tHandle):
        if tHandle in self.projTree:
            return self.projTree[tHandle]
        logger.error("No tree item with handle %s" % str(tHandle))
        return None

    def getRootItem(self, tHandle):
        """Iterate upwards in the tree until we find the item with
        parent None, the root item. We do this with a for loop with a
        maximum depth of 200 to make infinite loops impossible.
        """
        tItem = self.getItem(tHandle)
        if tItem is not None:
            for i in range(200):
                tHandle = tItem.parHandle
                tItem   = self.getItem(tHandle)
                if tItem is None:
                    return tHandle
        return None

    def getProjectItems(self):
        """This function is called from the tree view when building the
        tree. Each item in the project is returned in the order saved in
        the project file, but first it checks that it has a parent item
        already sent to the tree.
        """
        sentItems = []
        iterItems = self.treeOrder.copy()
        n    = 0
        nMax = len(iterItems)
        while n < nMax:
            tHandle = iterItems[n]
            tItem   = self.getItem(tHandle)
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

    def deleteItem(self, tHandle):
        """This only removes the item from the order list, but not from
        the project tree.
        """
        self.treeOrder.remove(tHandle)
        self.setProjectChanged(True)
        return True

    def findRootItem(self, theClass):
        for aRoot in self.treeRoots:
            if theClass == self.projTree[aRoot].itemClass:
                return self.projTree[aRoot].itemHandle
        return None

    def checkRootUnique(self, theClass):
        """Checks if there already is a root entry of class 'theClass'
        in the root of the project tree.
        """
        if theClass == nwItemClass.CUSTOM:
            return True
        for aRoot in self.treeRoots:
            if theClass == self.projTree[aRoot].itemClass:
                return False
        return True

    def countStatus(self):
        self.statusItems.resetCounts()
        self.importItems.resetCounts()
        for nwItem in self.projTree.values():
            if nwItem.itemClass == nwItemClass.NOVEL:
                self.statusItems.countEntry(nwItem.itemStatus)
            else:
                self.importItems.countEntry(nwItem.itemStatus)
        return

    ##
    #  Internal Functions
    ##

    def _checkFolder(self, thePath):
        if not path.isdir(thePath):
            try:
                mkdir(thePath)
                logger.debug("Created folder %s" % thePath)
            except Exception as e:
                self.makeAlert(["Could not create folder.",str(e)], nwAlert.ERROR)
                return False
        return True

    def _saveProjectValue(self, xParent, theName, theValue, allowNone=True):
        if not isinstance(theValue, list):
            theValue = [theValue]
        for aValue in theValue:
            if not isinstance(aValue, str):
                aValue = str(aValue)
            if aValue == "" and not allowNone: continue
            xItem = etree.SubElement(xParent,theName)
            xItem.text = aValue
        return

    def _scanProjectFolder(self):

        if self.projPath is None:
            return

        # First, scan the project data folders
        itemList = []
        for subItem in listdir(self.projPath):
            if subItem[:5] != "data_":
                continue
            dataDir = path.join(self.projPath,subItem)
            for subFile in listdir(dataDir):
                if subFile[-4:] == ".nwd":
                    newItem = path.join(subItem,subFile)
                    itemList.append(newItem)

        # Then check the valid files
        orphanFiles = []
        for fileItem in itemList:
            if len(fileItem) != 28:
                # Just to be safe, shouldn't happen
                logger.warning("Skipping file %s" % fileItem)
                continue
            fHandle = fileItem[5]+fileItem[7:19]
            if fHandle in self.treeOrder:
                logger.debug("Checking file %s, handle %s: OK" % (fileItem,fHandle))
            else:
                logger.debug("Checking file %s, handle %s: Orphaned" % (fileItem,fHandle))
                orphanFiles.append(fHandle)

        # Report status
        if len(orphanFiles) > 0:
            self.makeAlert(
                "Found %d orphaned file(s) in project folder!" % len(orphanFiles),
                nwAlert.WARN
            )
        else:
            logger.debug("File check OK")
            return

        # Handle orphans
        nOrph = 0
        for oHandle in orphanFiles:
            nOrph += 1
            orItem = NWItem(self)
            orItem.setName("Orphaned File %d" % nOrph)
            orItem.setType(nwItemType.FILE)
            orItem.setClass(nwItemClass.NO_CLASS)
            orItem.setLayout(nwItemLayout.NO_LAYOUT)
            self._appendItem(oHandle,None,orItem)

        return

    def _appendItem(self, tHandle, pHandle, nwItem):
        tHandle = checkString(tHandle,self._makeHandle(),False)
        pHandle = checkString(pHandle,None,True)
        logger.verbose("Adding entry %s with parent %s" % (str(tHandle),str(pHandle)))

        nwItem.setHandle(tHandle)
        nwItem.setParent(pHandle)

        self.projTree[tHandle] = nwItem
        self.treeOrder.append(tHandle)

        if nwItem.itemType == nwItemType.ROOT:
            logger.verbose("Entry %s is a root item" % str(tHandle))
            self.treeRoots.append(tHandle)

        if nwItem.itemType == nwItemType.TRASH:
            if self.trashRoot is None:
                logger.verbose("Entry %s is the trash folder" % str(tHandle))
                self.trashRoot = tHandle
            else:
                logger.error("Only one trash folder allowed")

        self.setProjectChanged(True)

        return

    def _appendSessionStats(self):

        if self.projMeta is None:
            return False

        sessionFile = path.join(self.projMeta, nwFiles.SESS_INFO)

        with open(sessionFile, mode="a+", encoding="utf8") as outFile:
            print((
                "Start: {opened:s}  "
                "End: {closed:s}  "
                "Words: {words:8d}"
            ).format(
                opened = datetime.fromtimestamp(self.projOpened).strftime(nwConst.tStampFmt),
                closed = datetime.now().strftime(nwConst.tStampFmt),
                words  = self.getSessionWordCount(),
            ), file=outFile)

        return True

    def _makeHandle(self, addSeed=""):
        if self.handleSeed is None:
            newSeed = str(time()) + addSeed
        else:
            # This is used for debugging
            newSeed = str(self.handleSeed)
            self.handleSeed += 1
        logger.verbose("Generating handle with seed '%s'" % newSeed)
        itemHandle = sha256(newSeed.encode()).hexdigest()[0:13]
        if itemHandle in self.projTree.keys():
            logger.warning("Duplicate handle encountered! Retrying ...")
            itemHandle = self._makeHandle(addSeed+"!")
        return itemHandle

    def _maintainPrevious(self):
        """This function will take the current project file and copy it
        into the project cache folder with an incremental file extension
        added. These serve as a backup in case the xml file gets
        corrupted.
        """

        countFile = path.join(self.projCache, nwFiles.PROJ_COUNT)
        projCount = 0

        if path.isfile(countFile):
            try:
                with open(countFile, mode="r") as inFile:
                    projCount = int(inFile.read())+1
            except:
                projCount = 0

        if projCount > 9:
            projCount = 0

        projBackup = "%s.%d" % (nwFiles.PROJ_FILE, projCount)

        try:
            copyfile(
                path.join(self.projPath, self.projFile),
                path.join(self.projCache, projBackup)
            )
        except:
            logger.error("Failed to write to file %s" % projBackup)

        try:
            with open(countFile, mode="w") as outFile:
                outFile.write(str(projCount))
        except:
            logger.error("Failed to write to file %s" % countFile)

        return

# END Class NWProject
