# -*- coding: utf-8 -*-
"""novelWriter Options State

 novelWriter – Options State
=============================
 Class holding the last state of GUI options

 File History:
 Created: 2019-10-21 [0.3.1] - Original version meant to be sub classed
 Created: 2020-02-19 [0.4.5] - Rewritten from superclass to single file tool

 This file is a part of novelWriter
 Copyright 2020, Veronica Berglyd Olsen

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import json
import nw

from os import path

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
        if self.theProject.projMeta is None:
            return False

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
        if self.theProject.projMeta is None:
            return False

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

    def getValue(self, getGroup, getName, defaultValue):
        """Return an arbitrary type value, if it exists. Otherwise,
        return the default value.
        """
        if getGroup in self.theState:
            if getName in self.theState[getGroup]:
                try:
                    return self.theState[getGroup][getName]
                except:
                    return defaultValue
        return defaultValue

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

    def validIntRange(self, theValue, intA, intB, intDefault):
        """Check that an int is in a given range. If it isn't, return
        the default value.
        """
        if isinstance(theValue, int):
            if theValue >= intA and theValue <= intB:
                return theValue
        return intDefault

    def validIntTuple(self, theValue, theTuple, intDefault):
        """Check that an int is an element of a tuple. If it isn't,
        return the default value.
        """
        if isinstance(theValue, int):
            if theValue in theTuple:
                return theValue
        return intDefault

# END Class OptionState
