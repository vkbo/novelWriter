# -*- coding: utf-8 -*-
"""novelWriter Config Class

 novelWriter – Config Class
============================
 This class reads and store the main preferences of the application

 File History:
 Created: 2018-09-22 [0.0.1]

"""

import logging
import configparser
import nw

from os       import path, mkdir, getcwd
from appdirs  import user_config_dir
from datetime import datetime

logger = logging.getLogger(__name__)

class Config:

    WIN_WIDTH  = 0
    WIN_HEIGHT = 1

    def __init__(self):

        # Set Application Variables
        self.appName   = nw.__package__
        self.appHandle = nw.__package__.lower()
        self.showGUI   = True
        self.debugGUI  = False

        # Set Paths
        self.confPath  = None
        self.confFile  = None
        self.homePath  = None
        self.appPath   = None
        self.guiPath   = None
        self.themePath = None

        # Set default values
        self.confChanged  = False

        ## General
        self.guiTheme     = "default"
        self.winGeometry  = [1100, 650]
        self.treeColWidth = [120, 30, 50]
        self.mainPanePos  = [300, 800]

        ## Project
        self.autoSaveProj = 60
        self.autoSaveDoc  = 30

        ## Text Editor
        self.textFixedW      = True
        self.textWidth       = 600
        self.textMargin      = [40, 40]
        self.textSize        = 13
        self.doJustify       = True
        self.autoSelect      = True
        self.doReplace       = True
        self.doReplaceSQuote = True
        self.doReplaceDQuote = True
        self.doReplaceDash   = True
        self.doReplaceDots   = True
        self.wordCountTimer  = 5.0
        
        self.fmtDoubleQuotes = ["“","”"]
        self.fmtSingleQuotes = ["‘","’"]
        self.fmtApostrophe   = "’"

        self.spellLanguage   = "en_GB"

        # Path
        self.recentList = [""]*10

        return

    ##
    #  Actions
    ##

    def initConfig(self, confPath=None):

        if confPath is None:
            self.confPath = user_config_dir(self.appHandle)
        else:
            self.confPath = confPath

        self.confFile  = self.appHandle+".conf"
        self.homePath  = path.expanduser("~")
        self.appPath   = path.dirname(__file__)
        self.guiPath   = path.join(self.appPath,"gui")
        self.themePath = path.join(self.appPath,"themes")

        # If config folder does not exist, make it.
        # This assumes that the os config folder itself exists.
        # TODO: This does not work on Windows
        if not path.isdir(self.confPath):
            mkdir(self.confPath)

        # Check if config file exists
        if path.isfile(path.join(self.confPath,self.confFile)):
            # If it exists, load it
            self.loadConfig()
        else:
            # If it does not exist, save a copy of the defaults
            self.saveConfig()

        return

    def loadConfig(self):

        logger.debug("Loading config file")
        confParser = configparser.ConfigParser()
        confParser.readfp(open(path.join(self.confPath,self.confFile)))

        # Get options

        ## Sizes
        cnfSec = "Sizes"
        if confParser.has_section(cnfSec):
            if confParser.has_option(cnfSec,"geometry"):
                self.winGeometry = self.unpackList(
                    confParser.get(cnfSec,"geometry"), 2, self.winGeometry
                )
            if confParser.has_option(cnfSec,"treecols"):
                self.treeColWidth = self.unpackList(
                    confParser.get(cnfSec,"treecols"), 3, self.treeColWidth
                )
            if confParser.has_option(cnfSec,"mainpane"):
                self.mainPanePos = self.unpackList(
                    confParser.get(cnfSec,"mainpane"), 2, self.mainPanePos
                )

        ## Project
        cnfSec = "Project"
        if confParser.has_section(cnfSec):
            if confParser.has_option(cnfSec,"autosaveproject"):
                self.autoSaveProj   = confParser.getint(cnfSec,"autosaveproject")
            if confParser.has_option(cnfSec,"autosavedoc"):
                self.autoSaveDoc    = confParser.getint(cnfSec,"autosavedoc")

        ## Editor
        cnfSec = "Editor"
        if confParser.has_section(cnfSec):
            if confParser.has_option(cnfSec,"fixedwidth"):
               self.textFixedW      = confParser.getboolean(cnfSec,"fixedwidth")
            if confParser.has_option(cnfSec,"width"):
                self.textWidth      = confParser.getint(cnfSec,"width")
            if confParser.has_option(cnfSec,"margins"):
                self.textMargin     = self.unpackList(
                    confParser.get(cnfSec,"margins"), 2, self.textMargin
                )
            if confParser.has_option(cnfSec,"textsize"):
                self.textSize       = confParser.getint(cnfSec,"textsize")
            if confParser.has_option(cnfSec,"justify"):
                self.doJustify      = confParser.getboolean(cnfSec,"justify")
            if confParser.has_option(cnfSec,"autoselect"):
                self.autoSelect     = confParser.getboolean(cnfSec,"autoselect")
            if confParser.has_option(cnfSec,"autoreplace"):
                self.doReplace      = confParser.getboolean(cnfSec,"autoreplace")
            if confParser.has_option(cnfSec,"repsquotes"):
                self.doReplaceSQuote  = confParser.getboolean(cnfSec,"repsquotes")
            if confParser.has_option(cnfSec,"repdquotes"):
                self.doReplaceDQuote = confParser.getboolean(cnfSec,"repdquotes")
            if confParser.has_option(cnfSec,"repdash"):
                self.doReplaceDash  = confParser.getboolean(cnfSec,"repdash")
            if confParser.has_option(cnfSec,"repdots"):
                self.doReplaceDots  = confParser.getboolean(cnfSec,"repdots")
            if confParser.has_option(cnfSec,"spellcheck"):
                self.spellLanguage  = confParser.get(cnfSec,"spellcheck")

        ## Path
        cnfSec = "Path"
        if confParser.has_section(cnfSec):
            for i in range(10):
                if confParser.has_option(cnfSec,"recent%d" % i):
                    self.recentList[i] = confParser.get(cnfSec,"recent%d" % i)

        return

    def saveConfig(self):

        logger.debug("Saving config file")
        confParser = configparser.ConfigParser()

        # Set options

        ## Main
        cnfSec = "Main"
        confParser.add_section(cnfSec)
        confParser.set(cnfSec,"timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        ## Sizes
        cnfSec = "Sizes"
        confParser.add_section(cnfSec)
        confParser.set(cnfSec,"geometry", self.packList(self.winGeometry))
        confParser.set(cnfSec,"treecols", self.packList(self.treeColWidth))
        confParser.set(cnfSec,"mainpane", self.packList(self.mainPanePos))

        ## Project
        cnfSec = "Project"
        confParser.add_section(cnfSec)
        confParser.set(cnfSec,"autosaveproject", str(self.autoSaveProj))
        confParser.set(cnfSec,"autosavedoc",     str(self.autoSaveDoc))

        ## Editor
        cnfSec = "Editor"
        confParser.add_section(cnfSec)
        confParser.set(cnfSec,"fixedwidth", str(self.textFixedW))
        confParser.set(cnfSec,"width",      str(self.textWidth))
        confParser.set(cnfSec,"margins",    self.packList(self.textMargin))
        confParser.set(cnfSec,"textsize",   str(self.textSize))
        confParser.set(cnfSec,"justify",    str(self.doJustify))
        confParser.set(cnfSec,"autoselect", str(self.autoSelect))
        confParser.set(cnfSec,"autoreplace",str(self.doReplace))
        confParser.set(cnfSec,"repsquotes", str(self.doReplaceSQuote))
        confParser.set(cnfSec,"repdquotes", str(self.doReplaceDQuote))
        confParser.set(cnfSec,"repdash",    str(self.doReplaceDash))
        confParser.set(cnfSec,"repdots",    str(self.doReplaceDots))
        confParser.set(cnfSec,"spellcheck", str(self.spellLanguage))

        ## Path
        cnfSec = "Path"
        confParser.add_section(cnfSec)
        for i in range(10):
            confParser.set(cnfSec,"recent%d" % i, str(self.recentList[i]))

        # Write config file
        confParser.write(open(path.join(self.confPath,self.confFile),"w"))
        self.confChanged = False

        return

    def unpackList(self, inStr, listLen, listDefault, castTo=int):
        inData  = inStr.split(",")
        outData = []
        for i in range(listLen):
            try:
                outData.append(castTo(inData[i]))
            except:
                outData.append(listDefault[i])
        return outData

    def packList(self, inData):
        return ", ".join(str(inVal) for inVal in inData)

    ##
    #  Setters
    ##

    def setRecent(self, recentPath):
        if recentPath == "": return
        if recentPath in self.recentList[0:10]:
            self.recentList.remove(recentPath)
        self.recentList.insert(0,recentPath)
        return

    def setConfPath(self, newPath):
        if newPath is None: return
        if not path.isfile(newPath):
            logger.error("Config: File not found. Using default config path instead.")
            return
        self.confPath = path.dirname(newPath)
        self.confFile = path.basename(newPath)
        return

    def setWinSize(self, newWidth, newHeight):
        if abs(self.winGeometry[self.WIN_WIDTH] - newWidth) >= 10:
            self.winGeometry[self.WIN_WIDTH] = newWidth
            self.confChanged = True
        if abs(self.winGeometry[self.WIN_HEIGHT] - newHeight) >= 10:
            self.winGeometry[self.WIN_HEIGHT] = newHeight
            self.confChanged = True
        return

    def setTreeColWidths(self, colWidths):
        self.treeColWidth = colWidths
        return

    def setMainPanePos(self, panePos):
        self.mainPanePos = panePos
        return

# End Class Config
