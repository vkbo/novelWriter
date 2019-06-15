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

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.guiPath    = "gui"
        self.syntaxPath = "syntax"
        self.cssName    = "styles.css"
        self.confName   = "theme.conf"
        self.themeList  = []
        self.syntaxList = []

        # Loaded Theme Settings

        ## Main
        self.themeName   = "No Name"

        ## Syntax
        self.colText     = [  0,  0,  0]
        self.colLink     = [  0,  0,  0]
        self.colHead     = [  0,  0,  0]
        self.colHeadH    = [  0,  0,  0]
        self.colEmph     = [  0,  0,  0]
        self.colDialN    = [  0,  0,  0]
        self.colDialD    = [  0,  0,  0]
        self.colDialS    = [  0,  0,  0]
        self.colComm     = [  0,  0,  0]
        self.colKey      = [  0,  0,  0]
        self.colVal      = [  0,  0,  0]
        self.colSpell    = [  0,  0,  0]
        self.colTagErr   = [  0,  0,  0]
        self.colRepTag   = [  0,  0,  0]

        ## GUI
        self.treeWCount  = [  0,  0,  0]
        self.statNone    = [120,120,120]
        self.statUnsaved = [120,120, 40]
        self.statSaved   = [ 40,120,  0]

        # Changeable Settings
        self.guiTheme    = None
        self.guiSyntax   = None
        self.themeRoot   = None
        self.cssFile     = None
        self.cssData     = ""

        self.updateTheme()

        return

    ##
    #  Actions
    ##

    def updateTheme(self):

        self.guiTheme   = self.mainConf.guiTheme
        self.guiSyntax  = self.mainConf.guiSyntax
        self.themeRoot  = self.mainConf.themeRoot
        self.themePath  = path.join(self.mainConf.themeRoot, self.guiPath, self.guiTheme)
        self.syntaxFile = path.join(self.themeRoot,self.syntaxPath,self.guiSyntax+".conf")
        self.confFile   = path.join(self.themePath,self.confName)
        self.cssFile    = path.join(self.themePath,self.cssName)

        print(self.guiSyntax)

        self.loadTheme()
        self.loadSyntax()

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

        return True

    def loadSyntax(self):

        confParser = configparser.ConfigParser()
        try:
            confParser.read_file(open(self.syntaxFile))
        except Exception as e:
            logger.error("Could not load syntax colours from: %s" % self.syntaxFile)
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

        ## GUI
        cnfSec = "GUI"
        if confParser.has_section(cnfSec):
            self.treeWCount  = self._loadColour(confParser,cnfSec,"treewordcount")
            self.statNone    = self._loadColour(confParser,cnfSec,"statusnone")
            self.statUnsaved = self._loadColour(confParser,cnfSec,"statusunsaved")
            self.statSaved   = self._loadColour(confParser,cnfSec,"statussaved")

        logger.info("Loaded syntax colour theme '%s'" % self.guiSyntax)

        return True

    def listThemes(self):

        if len(self.themeList) > 0:
            return self.themeList

        confParser = configparser.ConfigParser()
        for themeDir in listdir(path.join(self.mainConf.themeRoot, self.guiPath)):
            themeConf = path.join(self.mainConf.themeRoot, self.guiPath, themeDir, self.confName)
            logger.verbose("Checking theme config for '%s'" % themeDir)
            try:
                confParser.read_file(open(themeConf))
            except Exception as e:
                self.theParent.makeAlert(["Could not load theme config file",str(e)],nwAlert.ERROR)
                continue
            themeName = ""
            if confParser.has_section("Main"):
                themeName = confParser.get("Main","name")
                logger.verbose("Theme name is '%s'" % themeName)
            if themeName != "":
                self.themeList.append((themeDir, themeName))

        return self.themeList

    def listSyntax(self):

        if len(self.syntaxList) > 0:
            return self.syntaxList

        confParser = configparser.ConfigParser()
        syntaxDir  = path.join(self.mainConf.themeRoot, self.syntaxPath)
        for syntaxFile in listdir(syntaxDir):
            syntaxPath = path.join(syntaxDir, syntaxFile)
            if not path.isfile(syntaxPath):
                continue
            logger.verbose("Checking theme syntax for '%s'" % syntaxFile)
            try:
                confParser.read_file(open(syntaxPath))
            except Exception as e:
                self.theParent.makeAlert(["Could not load syntax file",str(e)],nwAlert.ERROR)
                return []
            syntaxName = ""
            if confParser.has_section("Main"):
                syntaxName = confParser.get("Main","name")
            if len(syntaxFile) > 5 and syntaxName != "":
                self.syntaxList.append((syntaxFile[:-5], syntaxName))
                logger.verbose("Syntax name is '%s'" % syntaxName)

        return self.syntaxList

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
