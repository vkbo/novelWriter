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

from os   import path, mkdir
from lxml import etree

logger = logging.getLogger(__name__)

class NWProject():

    def __init__(self):

        self.projFolder = None
        self.projTree   = []

        # Project Settings
        self.projPath    = ""
        self.projData    = ""
        self.projName    = ""
        self.bookTitle   = ""
        self.bookAuthors = []

        return

    def buildProjectTree(self):

        return True

    def saveProject(self):

        projDir  = path.dirname(self.projPath)
        projFile = path.basename(self.projPath)
        logger.vverbose("Project folder is %s" % projDir)
        logger.vverbose("Project file is %s" % projFile)

        if bookFile[-4:] == ".nwx":
            self.projData = path.join(projDir,projFile[:-4]+".nwd")
            if not path.isdir(self.projData):
                logger.info("Created folder %s" % self.projData)
                mkdir(self.projData)

        # Root element and book details
        nwXML = etree.Element("novelWriterXML",attrib={
            "fileVersion" : "1.0",
            "appVersion"  : str(nw.__version__),
            "timeStamp"   : getTimeStamp("-"),
        })
        xBook = etree.SubElement(nwXML,"book")
        xBookTitle = etree.SubElement(xBook,"title")
        xBookTitle.text = self.bookTitle
        for bookAuthor in self.bookAuthors:
            if bookAuthor == "": continue
            xBookAuthor = etree.SubElement(xBook,"author")
            xBookAuthor.text = bookAuthor

        # Write the xml tree to file
        with open(self.bookPath,"wb") as outFile:
            outFile.write(etree.tostring(
                nwXML,
                pretty_print    = True,
                encoding        = "utf-8",
                xml_declaration = True
            ))

        return True

    #
    #  Set Functions
    #

    def setProjectName(self, projName):
        self.projName = projName.strip()
        return True

    def setBookTitle(self, bookTitle):
        self.bookTitle = bookTitle.strip()
        return True

    def setBookAuthors(self, bookAuthors):
        self.bookAuthors = []
        for bookAuthor in bookAuthors.split(","):
            self.bookAuthors.append(bookAuthor.strip())
        return True

# END Class NWProject
