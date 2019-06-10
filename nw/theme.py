# -*- coding: utf-8 -*-
"""novelWriter Theme Class

 novelWriter – Theme Class
===========================
 This class reads and store the main theme

 File History:
 Created: 2019-05-18 [0.1.3]

"""

import logging
import configparser
import nw

from os import path, listdir

from nw.enum import nwAlert

logger = logging.getLogger(__name__)

class Theme:

    def __init__(self, theParent):

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.cssName   = "styles.css"
        self.confName  = "theme.conf"
        self.themeList = []

        # Loaded Theme Settings

        ## Main
        self.themeName = "No Name"

        ## Syntax
        self.colText   = [0,0,0]
        self.colLink   = [0,0,0]
        self.colHead   = [0,0,0]
        self.colHeadH  = [0,0,0]
        self.colEmph   = [0,0,0]
        self.colDialN  = [0,0,0]
        self.colDialD  = [0,0,0]
        self.colDialS  = [0,0,0]
        self.colComm   = [0,0,0]
        self.colKey    = [0,0,0]
        self.colVal    = [0,0,0]
        self.colSpell  = [0,0,0]
        self.colTagErr = [0,0,0]
        self.colRepTag = [0,0,0]

        # Changeable Settings
        self.guiTheme  = None
        self.themePath = None
        self.confFile  = None
        self.cssFile   = None
        self.cssData   = ""

        self.updateTheme()

        return

    ##
    #  Actions
    ##

    def updateTheme(self):
        self.guiTheme  = self.mainConf.guiTheme
        self.themePath = path.join(self.mainConf.themePath, self.guiTheme)
        self.confFile  = path.join(self.themePath,self.confName)
        self.cssFile   = path.join(self.themePath,self.cssName)
        return True

    def loadTheme(self):

        logger.debug("Loading theme files")

        # CSS File
        try:
            if path.isfile(self.cssFile):
                with open(self.cssFile,mode="r") as inFile:
                    self.cssData = inFile.read()
        except Exception as e:
            logger.error("Could not load theme css file")
            return False

        # Color Config
        confParser = configparser.ConfigParser()
        try:
            confParser.read_file(open(self.confFile))
        except Exception as e:
            logger.error("Could not load theme config file")
            return False

        ## Main
        cnfSec = "Main"
        if confParser.has_section(cnfSec):
            self.themeName = confParser.get(cnfSec,"name")

        ## Syntax
        cnfSec = "Syntax"
        if confParser.has_section(cnfSec):
            self.colText   = self._loadColour(confParser,cnfSec,"text")
            self.colLink   = self._loadColour(confParser,cnfSec,"link")
            self.colHead   = self._loadColour(confParser,cnfSec,"headertext")
            self.colHeadH  = self._loadColour(confParser,cnfSec,"headertag")
            self.colEmph   = self._loadColour(confParser,cnfSec,"emphasis")
            self.colDialN  = self._loadColour(confParser,cnfSec,"straightquotes")
            self.colDialD  = self._loadColour(confParser,cnfSec,"doublequotes")
            self.colDialS  = self._loadColour(confParser,cnfSec,"singlequotes")
            self.colComm   = self._loadColour(confParser,cnfSec,"hidden")
            self.colKey    = self._loadColour(confParser,cnfSec,"keyword")
            self.colVal    = self._loadColour(confParser,cnfSec,"value")
            self.colSpell  = self._loadColour(confParser,cnfSec,"spellcheckline")
            self.colTagErr = self._loadColour(confParser,cnfSec,"tagerror")
            self.colRepTag = self._loadColour(confParser,cnfSec,"replacetag")

        return True

    def listThemes(self):

        if len(self.themeList) > 0:
            return self.themeList

        confParser = configparser.ConfigParser()
        for themeDir in listdir(self.mainConf.themeRoot):
            themeConf = path.join(self.mainConf.themeRoot, themeDir, self.confName)
            logger.verbose("Checking theme config for '%s'" % themeDir)
            try:
                confParser.read_file(open(themeConf))
            except Exception as e:
                self.theParent.makeAlert(["Could not load theme config file",str(e)],nwAlert.ERROR)
                return []
            themeName = ""
            if confParser.has_section("Main"):
                themeName = confParser.get("Main","name")
                logger.verbose("Theme name is '%s'" % themeName)
            if themeName != "":
                self.themeList.append((themeDir, themeName))

        return self.themeList

    ##
    #  Internal Functions
    ##

    def _loadColour(self, confParser, cnfSec, cnfName):
        if confParser.has_option(cnfSec,cnfName):
            inData  = confParser.get(cnfSec,cnfName).split(",")
            outData = []
            try:
                outData.append(int(inData[0]))
                outData.append(int(inData[1]))
                outData.append(int(inData[2]))
            except:
                logger.error("Could not load theme colours for '%s' from config file" % cnfName)
                outData = [0,0,0]
        else:
            logger.warning("Could not find theme colours for '%s' in config file" % cnfName)
            outData = [0,0,0]
        return outData

# End Class Theme
