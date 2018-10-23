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

from os       import path, mkdir
from lxml     import etree
from datetime import datetime

logger = logging.getLogger(__name__)

class NWProject():

    def __init__(self):

        self.mainConf   = nw.CONFIG

        self.projFolder = None
        self.projTree   = []

        # Project Settings
        self.projPath    = None
        self.projFile    = "nwProject.nwx"
        self.bookTitle   = ""
        self.bookAuthors = []

        return

    def buildProjectTree(self):

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
        xBook = etree.SubElement(nwXML,"book")
        xBookTitle = etree.SubElement(xBook,"title")
        xBookTitle.text = self.bookTitle
        for bookAuthor in self.bookAuthors:
            if bookAuthor == "": continue
            xBookAuthor = etree.SubElement(xBook,"author")
            xBookAuthor.text = bookAuthor

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
        for bookAuthor in bookAuthors.split(","):
            self.bookAuthors.append(bookAuthor.strip())
        return True

# END Class NWProject
