# -*- coding: utf-8 -*-
"""novelWriter Options Last State

 novelWriter – Options Last State
==================================
 Class holding the last state of GUI options

 File History:
 Created: 2019-10-21 [0.3.1]

"""

import logging
import json
import nw

from os import path

from nw.common import checkString, checkBool, checkInt

logger = logging.getLogger(__name__)

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
