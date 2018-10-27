# -*- coding: utf-8 -*
"""novelWriter Config Class

 novelWriter – Config Class
============================
 This class reads and store the main preferences of the application

 File History:
 Created: 2018-0+-22 [0.1.0]

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
        self.appName    = nw.__package__
        self.appHandle  = nw.__package__.lower()
        self.showGUI    = True
        self.debugGUI   = False

        # Set Paths
        self.confPath   = user_config_dir(self.appHandle)
        self.confFile   = self.appHandle+".conf"
        self.homePath   = path.expanduser("~")
        self.appPath    = path.dirname(__file__)
        self.guiPath    = path.join(self.appPath,"gui")
        self.themePath  = path.join(self.appPath,"themes")
        self.recentList = [""]*10

        # If config folder does not exist, make it.
        # This assumes that the os config folder itself exists.
        # TODO: This does not work on Windows
        if not path.isdir(self.confPath):
            mkdir(self.confPath)

        # Set default values
        self.confChanged = False

        ## General
        self.winGeometry = [1600, 980]

        # Check if config file exists
        if path.isfile(path.join(self.confPath,self.confFile)):
            self.loadConfig()

        # Save a copy of the default config if no file exists
        if not path.isfile(path.join(self.confPath,self.confFile)):
            self.saveConfig()

        return

    ##
    #  Actions
    ##

    def loadConfig(self):

        logger.debug("Loading config file")
        confParser = configparser.ConfigParser()
        confParser.readfp(open(path.join(self.confPath,self.confFile)))

        # Get options

        ## Main
        cnfSec = "Main"
        if confParser.has_section(cnfSec):
            if confParser.has_option(cnfSec,"geometry"):
                self.winGeometry = self.unpackList(
                    confParser.get(cnfSec,"geometry"), 2, self.winGeometry
                )

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
        confParser.set(cnfSec,"geometry",  self.packList(self.winGeometry))

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

# End Class Config
