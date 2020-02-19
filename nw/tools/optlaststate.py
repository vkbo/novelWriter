# -*- coding: utf-8 -*-
"""novelWriter Options State

 novelWriter – Options State
=============================
 Class holding the last state of GUI options

 File History:
 Created: 2019-10-21 [0.3.1] - Original version meant to be sub classed
 Created: 2020-02-19 [0.4.5] - Rewritten from superclass to single file tool

"""

import logging
import json
import nw

from os import path

from nw.common import checkString, checkBool, checkInt
from nw.constants import nwFiles

logger = logging.getLogger(__name__)

class OptionState():

    def __init__(self, theProject):

        self.theProject = theProject
        self.theState   = {}
        self.stringOpt  = ()
        self.boolOpt    = ()
        self.intOpt     = ()

        return

    def loadSettings(self):
        """Load the options dictionary from the project settings file.
        """

        stateFile = path.join(self.theProject.projMeta, nwFiles.OPTS_FILE)
        theState  = {}

        if path.isfile(stateFile):
            logger.debug("Loading GUI options file")
            try:
                with open(stateFile,mode="r",encoding="utf8") as inFile:
                    theJson = inFile.read()
                theState = json.loads(theJson)
            except Exception as e:
                logger.error("Failed to load GUI options file")
                logger.error(str(e))
                return False
        for anOpt in theState:
            self.theState[anOpt] = theState[anOpt]

        return True

    def saveSettings(self):
        """Save the options dictionary to the project settings file.
        """

        stateFile = path.join(self.theProject.projMeta, nwFiles.OPTS_FILE)
        logger.debug("Saving GUI options file")

        try:
            with open(stateFile,mode="w+",encoding="utf8") as outFile:
                outFile.write(json.dumps(self.theState, indent=2))
        except Exception as e:
            logger.error("Failed to save GUI options file")
            logger.error(str(e))
            return False

        return True

    def setValue(self, setGroup, setName, setValue):
        """Saves a value, with a given group and name.
        """
        if not setGroup in self.theState:
            self.theState[setGroup] = {}
        self.theState[setGroup][setName] = setValue
        return True

    def getString(self, getGroup, getName, defaultValue):
        """Return the value as a string, if it exists. Otherwise, return
        the default value.
        """
        if getGroup in self.theState:
            if getName in self.theState[getGroup]:
                try:
                    return str(self.theState[getGroup][getName])
                except:
                    return defaultValue
        return defaultValue

    def getInt(self, getGroup, getName, defaultValue):
        """Return the value as an int, if it exists. Otherwise, return
        the default value.
        """
        if getGroup in self.theState:
            if getName in self.theState[getGroup]:
                try:
                    return int(self.theState[getGroup][getName])
                except:
                    return defaultValue
        return defaultValue

    def getFloat(self, getGroup, getName, defaultValue):
        """Return the value as a float, if it exists. Otherwise, return
        the default value.
        """
        if getGroup in self.theState:
            if getName in self.theState[getGroup]:
                try:
                    return float(self.theState[getGroup][getName])
                except:
                    return defaultValue
        return defaultValue

    def getBool(self, getGroup, getName, defaultValue):
        """Return the value as a bool, if it exists. Otherwise, return
        the default value.
        """
        if getGroup in self.theState:
            if getName in self.theState[getGroup]:
                try:
                    return bool(self.theState[getGroup][getName])
                except:
                    return defaultValue
        return defaultValue

# END Class OptionState

class OptLastState():

    def __init__(self, theProject, theFile):
        self.theProject = theProject
        self.theFile    = theFile
        self.theState   = {}
        self.stringOpt  = ()
        self.boolOpt    = ()
        self.intOpt     = ()
        return

    def loadSettings(self):
        stateFile = path.join(self.theProject.projMeta,self.theFile)
        theState  = {}
        if path.isfile(stateFile):
            logger.debug("Loading options file")
            try:
                with open(stateFile,mode="r",encoding="utf8") as inFile:
                    theJson = inFile.read()
                theState = json.loads(theJson)
            except Exception as e:
                logger.error("Failed to load options file")
                logger.error(str(e))
                return False
        for anOpt in theState:
            self.theState[anOpt] = theState[anOpt]
        return True

    def saveSettings(self):
        stateFile = path.join(self.theProject.projMeta,self.theFile)
        logger.debug("Saving options file")
        try:
            with open(stateFile,mode="w+",encoding="utf8") as outFile:
                outFile.write(json.dumps(self.theState, indent=2))
        except Exception as e:
            logger.error("Failed to save options file")
            logger.error(str(e))
            return False
        return True

    def setSetting(self, setName, setValue):
        if setName in self.theState:
            self.theState[setName] = setValue
        else:
            return False
        return True

    def getSetting(self, setName):
        if setName in self.stringOpt:
            return checkString(self.theState[setName],self.theState[setName],False)
        elif setName in self.boolOpt:
            return checkBool(self.theState[setName],self.theState[setName],False)
        elif setName in self.intOpt:
            return checkInt(self.theState[setName],self.theState[setName],False)
        return None

    def validIntRange(self, theValue, intA, intB, intDefault):
        if isinstance(theValue, int):
            if theValue >= intA and theValue <= intB:
                return theValue
        return intDefault

    def validIntTuple(self, theValue, theTuple, intDefault):
        if isinstance(theValue, int):
            if theValue in theTuple:
                return theValue
        return intDefault

# END Class OptLastState
