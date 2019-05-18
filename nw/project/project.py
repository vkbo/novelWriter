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

from os              import path, mkdir, listdir
from lxml            import etree
from hashlib         import sha256
from datetime        import datetime
from time            import time

from nw.enum         import nwItemType, nwItemClass, nwItemLayout, nwAlert
from nw.common       import checkString, checkBool
from nw.project.item import NWItem

logger = logging.getLogger(__name__)

class NWProject():

    def __init__(self, theParent):

        # Internal
        self.theParent    = theParent
        self.mainConf     = self.theParent.mainConf
        self.projChanged  = None

        # Debug
        self.handleSeed   = None

        # Class Settings
        self.projTree     = None
        self.treeOrder    = None
        self.treeRoots    = None
        self.trashRoot    = None
        self.projPath     = None
        self.projMeta     = None
        self.projCache    = None
        self.projFile     = None

        # Project Meta
        self.projName     = None
        self.bookTitle    = None
        self.bookAuthors  = None

        # Project Settings
        self.spellCheck   = False
        self.statusCols   = None
        self.importCols   = None
        self.lastEdited   = None
        self.lastViewed   = None

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
        newItem = NWItem()
        newItem.setName(rootName)
        newItem.setType(nwItemType.ROOT)
        newItem.setClass(rootClass)
        self._appendItem(None,None,newItem)
        return newItem.itemHandle

    def newFolder(self, folderName, folderClass, pHandle):
        newItem = NWItem()
        newItem.setName(folderName)
        newItem.setType(nwItemType.FOLDER)
        newItem.setClass(folderClass)
        self._appendItem(None,pHandle,newItem)
        return newItem.itemHandle

    def newFile(self, fileName, fileClass, pHandle):
        newItem = NWItem()
        newItem.setName(fileName)
        newItem.setType(nwItemType.FILE)
        if fileClass == nwItemClass.NOVEL:
            newItem.setLayout(nwItemLayout.SCENE)
        else:
            newItem.setLayout(nwItemLayout.NOTE)
        newItem.setClass(fileClass)
        self._appendItem(None,pHandle,newItem)
        return newItem.itemHandle

    def addTrash(self):
        newItem = NWItem()
        newItem.setName("Trash")
        newItem.setType(nwItemType.TRASH)
        newItem.setClass(nwItemClass.TRASH)
        self._appendItem(None,None,newItem)
        return newItem.itemHandle

    ##
    #  Project Methods
    ##

    def newProject(self):

        self.clearProject()

        hNovel = self.newRoot("Novel",         nwItemClass.NOVEL)
        hChars = self.newRoot("Characters",    nwItemClass.CHARACTER)
        hWorld = self.newRoot("Plot",          nwItemClass.PLOT)
        hWorld = self.newRoot("World",         nwItemClass.WORLD)
        hChapt = self.newFolder("New Chapter", nwItemClass.NOVEL, hNovel)
        hScene = self.newFile("New Scene",     nwItemClass.NOVEL, hChapt)

        return True

    def clearProject(self):

        self.projChanged = None

        # Project Settings
        self.projTree    = {}
        self.treeOrder   = []
        self.treeRoots   = []
        self.trashRoot   = None
        self.projPath    = None
        self.projMeta    = None
        self.projCache   = None
        self.projFile    = "nwProject.nwx"
        self.projName    = ""
        self.bookTitle   = ""
        self.bookAuthors = []
        self.spellCheck  = False
        self.statusCols  = [
            ("New",     100,100,100),
            ("Note",    200, 50,  0),
            ("Draft",   200,150,  0),
            ("Finished", 50,200,  0),
        ]
        self.importCols  = [
            ("None",    100,100,100),
            ("Minor",   200, 50,  0),
            ("Major",   200,150,  0),
            ("Main",     50,200,  0),
        ]

        return

    def openProject(self, fileName):

        if not path.isfile(fileName):
            fileName = path.join(fileName, "nwProject.nwx")
            if not path.isfile(fileName):
                self.makeAlert("File not found: %s" % fileName, nwAlert.ERROR)
                return False

        self.clearProject()
        self.projPath = path.dirname(fileName)
        logger.debug("Opening project: %s" % self.projPath)

        self.projMeta  = path.join(self.projPath,"meta")
        self.projCache = path.join(self.projPath,"cache")

        if not self._checkFolder(self.projMeta):  return
        if not self._checkFolder(self.projCache): return

        nwXML = etree.parse(fileName)
        xRoot = nwXML.getroot()

        nwxRoot     = xRoot.tag
        appVersion  = xRoot.attrib["appVersion"]
        fileVersion = xRoot.attrib["fileVersion"]

        logger.verbose("XML root is %s" % nwxRoot)
        logger.verbose("File version is %s" % fileVersion)

        if not nwxRoot == "novelWriterXML" or not fileVersion == "1.0":
            self.makeAlert("Project file does not appear to be a novelWriterXML file version 1.0", nwAlert.ERROR)
            return False

        for xChild in xRoot:
            if xChild.tag == "project":
                logger.debug("Found project meta")
                for xItem in xChild:
                    if xItem.text is None: continue
                    if xItem.tag == "name":
                        logger.verbose("Working Title: '%s'" % xItem.text)
                        self.projName = xItem.text
                    elif xItem.tag == "title":
                        logger.verbose("Title is '%s'" % xItem.text)
                        self.bookTitle = xItem.text
                    elif xItem.tag == "author":
                        logger.verbose("Author: '%s'" % xItem.text)
                        self.bookAuthors.append(xItem.text)
            elif xChild.tag == "settings":
                logger.debug("Found project settings")
                for xItem in xChild:
                    if xItem.text is None: continue
                    if xItem.tag == "spellCheck":
                        self.spellCheck = checkBool(xItem.text,False)
                    if xItem.tag == "lastEdited":
                        self.lastEdited = checkString(xItem.text,None,True)
                    if xItem.tag == "lastViewed":
                        self.lastViewed = checkString(xItem.text,None,True)
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
                    nwItem = NWItem()
                    for xValue in xItem:
                        nwItem.setFromTag(xValue.tag,xValue.text)
                    self._appendItem(tHandle,pHandle,nwItem)

        self.mainConf.setRecent(self.projPath)
        self.theParent.setStatus("Opened Project: %s" % self.projName)

        self._scanProjectFolder()
        self.setProjectChanged(False)

        return True

    def saveProject(self):

        if self.projPath is None:
            self.makeAlert("Project path not set, cannot save.", nwAlert.ERROR)
            return False

        self.projMeta  = path.join(self.projPath,"meta")
        self.projCache = path.join(self.projPath,"cache")

        if not self._checkFolder(self.projPath):  return
        if not self._checkFolder(self.projMeta):  return
        if not self._checkFolder(self.projCache): return

        logger.debug("Saving project: %s" % self.projPath)

        # Root element and project details
        logger.debug("Writing project meta")
        nwXML = etree.Element("novelWriterXML",attrib={
            "fileVersion" : "1.0",
            "appVersion"  : str(nw.__version__),
            "timeStamp"   : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        # Save Project Meta
        xProject = etree.SubElement(nwXML,"project")
        self._saveProjectValue(xProject,"name",  self.projName,  True)
        self._saveProjectValue(xProject,"title", self.bookTitle, True)
        self._saveProjectValue(xProject,"author",self.bookAuthors)

        # Save Project Settings
        xSettings = etree.SubElement(nwXML,"settings")
        self._saveProjectValue(xSettings,"spellCheck",self.spellCheck)
        self._saveProjectValue(xSettings,"lastEdited",self.lastEdited)
        self._saveProjectValue(xSettings,"lastViewed",self.lastViewed)

        # Save Tree Content
        logger.debug("Writing project content")
        xContent = etree.SubElement(nwXML,"content",attrib={"count":str(len(self.treeOrder))})
        for tHandle in self.treeOrder:
            self.projTree[tHandle].packXML(xContent)

        # Write the xml tree to file
        saveFile = path.join(self.projPath,self.projFile)
        try:
            with open(saveFile,"wb") as outFile:
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

    ##
    #  Set Functions
    ##

    def setProjectPath(self, projPath):
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

    def setSpellCheck(self, theMode):
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
        self.lastEdited = tHandle
        self.setProjectChanged(True)
        return True

    def setLastViewed(self, tHandle):
        self.lastViewed = tHandle
        self.setProjectChanged(True)
        return True

    def setProjectChanged(self, bValue):
        self.projChanged = bValue
        self.theParent.setProjectStatus(self.projChanged)
        return self.projChanged

    ##
    #  Get Functions
    ##

    def getItem(self, tHandle):
        if tHandle in self.projTree:
            return self.projTree[tHandle]
        logger.error("No tree item with handle %s" % str(tHandle))
        return None

    def getProjectItems(self):
        """This function is called from the tree view when building the tree. Each item in the
        project is returned in the order saved in the project file, but first it checks that it has
        a parent item already sent to the tree.
        """
        sentItems = []
        iterItems = self.treeOrder.copy()
        n    = 0
        nMax = len(iterItems)
        while n < nMax:
            tHandle = iterItems[n]
            tItem   = self.getItem(tHandle)
            n += 1
            if tItem.parHandle is None:
                # Item is a root, or already been identified as an orphaned item
                sentItems.append(tHandle)
                yield tItem
            elif tItem.parHandle in sentItems:
                # Item's parent has been sent, so all is fine
                sentItems.append(tHandle)
                yield tItem
            elif tItem.parHandle in iterItems:
                # Item's parent exists, but hasn't been sent yet, so add it again to the end
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

    def findRootItem(self, theClass):
        for aRoot in self.treeRoots:
            if theClass == self.projTree[aRoot].itemClass:
                return self.projTree[aRoot].itemHandle
        return None

    def checkRootUnique(self, theClass):
        """Checks if there already is a root entry of class 'theClass' in the
        root of the project tree.
        """
        if theClass == nwItemClass.CUSTOM:
            return True
        for aRoot in self.treeRoots:
            if theClass == self.projTree[aRoot].itemClass:
                return False
        return True

    ##
    #  Internal Functions
    ##

    def _checkFolder(self, thePath):
        if not path.isdir(thePath):
            try:
                mkdir(thePath)
                logger.info("Created folder %s" % thePath)
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
            self.makeAlert("Found %d orphaned file(s) in project folder!" % len(orphanFiles), nwAlert.WARN)
        else:
            logger.debug("File check OK")
            return

        # Handle orphans
        nOrph = 0
        for oHandle in orphanFiles:
            nOrph += 1
            orItem = NWItem()
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

# END Class NWProject
