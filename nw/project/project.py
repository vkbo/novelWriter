# -*- coding: utf-8 -*
"""novelWriter Project Wrapper

 novelWriter – Project Wrapper
===============================
 Class holding a project

 File History:
 Created: 2018-09-29 [0.1.0]

"""

import logging
import nw

from os          import path, mkdir
from lxml        import etree
from hashlib     import sha256
from datetime    import datetime, time

from nw.project.item import NWItem

logger = logging.getLogger(__name__)

class NWProject():

    def __init__(self):

        # Internal
        self.mainConf    = nw.CONFIG
        self.seedCount   = 0

        # Project Settings
        self.projTree    = {}
        self.treeOrder   = []
        self.projPath    = None
        self.projFile    = "nwProject.nwx"
        self.projName    = ""
        self.bookTitle   = ""
        self.bookAuthors = []

        return

    def buildProjectTree(self):
        return True

    def newRoot(self, rootName, rootType):
        newItem = NWItem()
        newItem.setName(rootName)
        newItem.setType(NWItem.TYPE_ROOT)
        newItem.setClass(rootType)
        self._appendItem(None,None,newItem)
        return newItem.itemHandle

    def newFolder(self, folderName, pHandle):
        newItem = NWItem()
        newItem.setName(folderName)
        newItem.setType(NWItem.TYPE_FOLDER)
        newItem.setClass(NWItem.CLASS_NONE)
        self._appendItem(None,pHandle,newItem)
        return newItem.itemHandle

    def newFile(self, fileName, pHandle):
        newItem = NWItem()
        newItem.setName(fileName)
        newItem.setType(NWItem.TYPE_FILE)
        newItem.setClass(NWItem.CLASS_NONE)
        self._appendItem(None,pHandle,newItem)
        return newItem.itemHandle

    def newProject(self):
        self.projTree    = {}
        self.treeOrder   - []
        self.projPath    = None
        self.projFile    = "nwProject.nwx"
        self.projName    = ""
        self.bookTitle   = ""
        self.bookAuthors = []
        hNovel = self.newRoot("Novel", NWItem.CLASS_NOVEL)
        hChars = self.newRoot("Characters",NWItem.CLASS_CHARACTER)
        hWorld = self.newRoot("World", NWItem.CLASS_WORLD)
        hChapt = self.newFolder("New Chapter", hNovel)
        hScene = self.newFile("New Scene", hChapt)
        return

    def openProject(self, fileName):

        if not path.isfile(fileName):
            fileName = path.join(fileName, "nwProject.nwx")
            if not path.isfile(fileName):
                logger.error("File not found: %s" % fileName)
                return False

        self.projPath = path.dirname(fileName)

        nwXML = etree.parse(fileName)
        xRoot = nwXML.getroot()

        nwxRoot     = xRoot.tag
        appVersion  = xRoot.attrib["appVersion"]
        fileVersion = xRoot.attrib["fileVersion"]

        logger.verbose("XML root is %s" % nwxRoot)
        logger.verbose("File version is %s" % fileVersion)

        if not nwxRoot == "novelWriterXML" or not fileVersion == "1.0":
            logger.error("Project file does not appear to be a novelWriterXML file version 1.0")
            return False

        for xChild in xRoot:
            if xChild.tag == "project":
                logger.debug("Found book data")
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

        self.mainConf.setRecent(self.projPath)

        return True

    def saveProject(self):

        if self.projPath is None:
            logger.error("Project path not set, cannot save.")
            return False

        if not path.isdir(self.projPath):
            logger.info("Created folder %s" % self.projPath)
            mkdir(self.projPath)

        # Root element and book details
        nwXML = etree.Element("novelWriterXML",attrib={
            "fileVersion" : "1.0",
            "appVersion"  : str(nw.__version__),
            "timeStamp"   : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        xProject        = etree.SubElement(nwXML,"project")
        xProjName       = etree.SubElement(xProject,"name")
        xProjName.text  = self.projName
        xBookTitle      = etree.SubElement(xProject,"title")
        xBookTitle.text = self.bookTitle
        for bookAuthor in self.bookAuthors:
            if bookAuthor == "": continue
            xBookAuthor      = etree.SubElement(xProject,"author")
            xBookAuthor.text = bookAuthor

        # Save Tree Content
        xContent = etree.SubElement(nwXML,"content",attrib={"count":str(len(self.projTree))})
        itemIdx  = 0
        for tHandle in self.projTree.keys():
            nwItem = self.projTree[tHandle]
            xItem  = etree.SubElement(xContent,"item",attrib={
                "handle" : str(tHandle),
                "parent" : str(nwItem.parHandle),
                "order"  : str(nwItem.itemOrder),
            })
            xItemName      = etree.SubElement(xItem,"name")
            xItemName.text = str(nwItem.itemName)
            xItemType      = etree.SubElement(xItem,"type")
            xItemType.text = str(nwItem.getType())
            if nwItem.getClass() is not "NONE":
                xItemClass      = etree.SubElement(xItem,"class")
                xItemClass.text = str(nwItem.getClass())

        # Write the xml tree to file
        with open(path.join(self.projPath,self.projFile),"wb") as outFile:
            outFile.write(etree.tostring(
                nwXML,
                pretty_print    = True,
                encoding        = "utf-8",
                xml_declaration = True
            ))

        self.mainConf.setRecent(self.projPath)

        return True

    #
    #  Set Functions
    #

    def setProjectPath(self, projPath):
        self.projPath = projPath
        return True

    def setProjectName(self, projName):
        self.projName = projName.strip()
        return True

    def setBookTitle(self, bookTitle):
        self.bookTitle = bookTitle.strip()
        return True

    def setBookAuthors(self, bookAuthors):
        self.bookAuthors = []
        for bookAuthor in bookAuthors.split("\n"):
            bookAuthor = bookAuthor.strip()
            if bookAuthor == "":
                continue
            self.bookAuthors.append(bookAuthor)
        return True

    def setTreeOrder(self, newOrder):
        if len(self.treeOrder) != len(newOrder):
            logger.warning("Size of new and old tree order does not match")
        self.treeOrder - newOrder
        return True

    #
    #  Internal Functions
    #

    def _appendItem(self, tHandle, pHandle, nwItem):
        tHandle = self._checkString(tHandle,self._makeHandle(),False)
        pHandle = self._checkString(pHandle,None,True)
        logger.verbose("Adding entry %s with parent %s" % (str(tHandle),str(pHandle)))
        nwItem.setHandle(tHandle)
        nwItem.setParent(pHandle)
        self.projTree[tHandle] = nwItem
        self.treeOrder.append(tHandle)
        return

    def _makeHandle(self, seed=""):
        seed += str(self.seedCount)
        self.seedCount += 1
        itemHandle = sha256((str(time())+seed).encode()).hexdigest()[0:13]
        if itemHandle in self.projTree.keys():
            logger.warning("Duplicate handle encountered! Retrying ...")
            itemHandle = self._makeHandle(seed+"!")
        return itemHandle

    def _checkString(self,checkValue,defaultValue,allowNone=False):
        if allowNone:
            if checkValue == None:   return None
            if checkValue == "None": return None
        if isinstance(checkValue,str): return str(checkValue)
        return defaultValue

    def _checkInt(self,checkValue,defaultValue,allowNone=False):
        if allowNone:
            if checkValue == None:   return None
            if checkValue == "None": return None
        try:
            return int(checkValue)
        except:
            return defaultValue

# END Class NWProject
