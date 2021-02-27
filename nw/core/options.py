# -*- coding: utf-8 -*-
"""
novelWriter – Project Options Cache
===================================
Data class for user-defined GUI project options

File History:
Created:   2019-10-21 [0.3.1]
Rewritten: 2020-02-19 [0.4.5]

This file is a part of novelWriter
Copyright 2018–2021, Veronica Berglyd Olsen

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

import nw
import logging
import json
import os

from nw.constants import nwFiles

logger = logging.getLogger(__name__)

class OptionState():

    def __init__(self, theProject):

        self.theProject = theProject
        self.theState = {}
        self.validMap = {
            "GuiWritingStats": {
                "winWidth",
                "winHeight",
                "widthCol0",
                "widthCol1",
                "widthCol2",
                "widthCol3",
                "sortCol",
                "sortOrder",
                "incNovel",
                "incNotes",
                "hideZeros",
                "hideNegative",
                "groupByDay",
                "showIdleTime",
                "histMax",
            },
            "GuiDocSplit": {
                "spLevel",
            },
            "GuiBuildNovel": {
                "winWidth",
                "winHeight",
                "boxWidth",
                "docWidth",
                "addNovel",
                "addNotes",
                "ignoreFlag",
                "justifyText",
                "excludeBody",
                "textFont",
                "textSize",
                "lineHeight",
                "noStyling",
                "incSynopsis",
                "incComments",
                "incKeywords",
                "incBodyText",
                "replaceTabs",
                "replaceUCode",
            },
            "GuiOutline": {
                "headerOrder",
                "columnWidth",
                "columnHidden",
            },
            "GuiProjectSettings": {
                "winWidth",
                "winHeight",
                "replaceColW",
                "statusColW",
                "importColW",
            },
            "GuiProjectDetails": {
                "winWidth",
                "winHeight",
                "widthCol0",
                "widthCol1",
                "widthCol2",
                "widthCol3",
                "widthCol4",
                "wordsPerPage",
                "countFrom",
                "clearDouble",
            },
            "GuiWordList": {
                "winWidth",
                "winHeight",
            }
        }

        return

    ##
    #  Load and Save Cache
    ##

    def loadSettings(self):
        """Load the options dictionary from the project settings file.
        """
        if self.theProject.projMeta is None:
            return False

        stateFile = os.path.join(self.theProject.projMeta, nwFiles.OPTS_FILE)
        theState  = {}

        if os.path.isfile(stateFile):
            logger.debug("Loading GUI options file")
            try:
                with open(stateFile, mode="r", encoding="utf8") as inFile:
                    theState = json.load(inFile)
            except Exception:
                logger.error("Failed to load GUI options file")
                nw.logException()
                return False

        # Filter out unused variables
        for aGroup in theState:
            if aGroup in self.validMap:
                self.theState[aGroup] = {}
                for anOpt in theState[aGroup]:
                    if anOpt in self.validMap[aGroup]:
                        self.theState[aGroup][anOpt] = theState[aGroup][anOpt]

        return True

    def saveSettings(self):
        """Save the options dictionary to the project settings file.
        """
        if self.theProject.projMeta is None:
            return False

        stateFile = os.path.join(self.theProject.projMeta, nwFiles.OPTS_FILE)
        logger.debug("Saving GUI options file")

        try:
            with open(stateFile, mode="w+", encoding="utf8") as outFile:
                json.dump(self.theState, outFile, indent=2)
        except Exception:
            logger.error("Failed to save GUI options file")
            nw.logException()
            return False

        return True

    ##
    #  Setters
    ##

    def setValue(self, setGroup, setName, setValue):
        """Saves a value, with a given group and name.
        """
        if setGroup not in self.validMap:
            logger.error("Unknown option group '%s'" % setGroup)
            return False

        if setName not in self.validMap[setGroup]:
            logger.error("Unknown option name '%s'" % setName)
            return False

        if setGroup not in self.theState:
            self.theState[setGroup] = {}

        self.theState[setGroup][setName] = setValue

        return True

    ##
    #  Getters
    ##

    def getValue(self, getGroup, getName, defaultValue):
        """Return an arbitrary type value, if it exists. Otherwise,
        return the default value.
        """
        if getGroup in self.theState:
            if getName in self.theState[getGroup]:
                return self.theState[getGroup][getName]
        return defaultValue

    def getString(self, getGroup, getName, defaultValue):
        """Return the value as a string, if it exists. Otherwise, return
        the default value.
        """
        if getGroup in self.theState:
            if getName in self.theState[getGroup]:
                return str(self.theState[getGroup][getName])
        return defaultValue

    def getInt(self, getGroup, getName, defaultValue):
        """Return the value as an int, if it exists. Otherwise, return
        the default value.
        """
        if getGroup in self.theState:
            if getName in self.theState[getGroup]:
                try:
                    return int(self.theState[getGroup][getName])
                except Exception as e:
                    logger.warning(str(e))
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
                except Exception as e:
                    logger.warning(str(e))
                    return defaultValue
        return defaultValue

    def getBool(self, getGroup, getName, defaultValue):
        """Return the value as a bool, if it exists. Otherwise, return
        the default value.
        """
        if getGroup in self.theState:
            if getName in self.theState[getGroup]:
                return bool(self.theState[getGroup][getName])
        return defaultValue

    ##
    #  Validators
    ##

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
