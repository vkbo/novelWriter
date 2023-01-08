"""
novelWriter – Project Options Cache
===================================
Data class for user-defined GUI project options

File History:
Created:   2019-10-21 [0.3.1]
Rewritten: 2020-02-19 [0.4.5]

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

import json
import logging

from enum import Enum
from pathlib import Path

from novelwriter.error import logException
from novelwriter.common import checkBool, checkFloat, checkInt, checkString
from novelwriter.constants import nwFiles

logger = logging.getLogger(__name__)

VALID_MAP = {
    "GuiWritingStats": {
        "winWidth", "winHeight", "widthCol0", "widthCol1", "widthCol2",
        "widthCol3", "sortCol", "sortOrder", "incNovel", "incNotes",
        "hideZeros", "hideNegative", "groupByDay", "showIdleTime", "histMax",
    },
    "GuiDocSplit": {"spLevel", "intoFolder", "docHierarchy"},
    "GuiBuildNovel": {
        "winWidth", "winHeight", "boxWidth", "docWidth", "hideScene",
        "hideSection", "addNovel", "addNotes", "ignoreFlag", "justifyText",
        "excludeBody", "textFont", "textSize", "lineHeight", "noStyling",
        "incSynopsis", "incComments", "incKeywords", "incBodyText",
        "replaceTabs", "replaceUCode", "rootFilter",
    },
    "GuiOutline": {"headerOrder", "columnWidth", "columnHidden"},
    "GuiProjectSettings": {
        "winWidth", "winHeight", "replaceColW", "statusColW", "importColW",
    },
    "GuiProjectDetails": {
        "winWidth", "winHeight", "widthCol0", "widthCol1", "widthCol2",
        "widthCol3", "widthCol4", "wordsPerPage", "countFrom", "clearDouble",
    },
    "GuiWordList": {"winWidth", "winHeight"},
    "GuiNovelView": {"lastCol"},
}


class OptionState:

    def __init__(self, theProject):
        self.theProject = theProject
        self._theState = {}
        return

    ##
    #  Load and Save Cache
    ##

    def loadSettings(self):
        """Load the options dictionary from the project settings file.
        """
        stateFile = self.theProject.storage.getMetaFile(nwFiles.OPTS_FILE)
        if not isinstance(stateFile, Path):
            return False

        theState = {}
        if stateFile.exists():
            logger.debug("Loading GUI options file")
            try:
                with open(stateFile, mode="r", encoding="utf-8") as inFile:
                    theState = json.load(inFile)
            except Exception:
                logger.error("Failed to load GUI options file")
                logException()
                return False

        # Filter out unused variables
        for aGroup in theState:
            if aGroup in VALID_MAP:
                self._theState[aGroup] = {}
                for anOpt in theState[aGroup]:
                    if anOpt in VALID_MAP[aGroup]:
                        self._theState[aGroup][anOpt] = theState[aGroup][anOpt]

        return True

    def saveSettings(self):
        """Save the options dictionary to the project settings file.
        """
        stateFile = self.theProject.storage.getMetaFile(nwFiles.OPTS_FILE)
        if not isinstance(stateFile, Path):
            return False

        logger.debug("Saving GUI options file")
        try:
            with open(stateFile, mode="w+", encoding="utf-8") as outFile:
                json.dump(self._theState, outFile, indent=2)
        except Exception:
            logger.error("Failed to save GUI options file")
            logException()
            return False

        return True

    ##
    #  Setters
    ##

    def setValue(self, group, name, value):
        """Save a value, with a given group and name.
        """
        if group not in VALID_MAP:
            logger.error("Unknown option group '%s'", group)
            return False

        if name not in VALID_MAP[group]:
            logger.error("Unknown option name '%s'", name)
            return False

        if group not in self._theState:
            self._theState[group] = {}

        if isinstance(value, Enum):
            self._theState[group][name] = value.name
        else:
            self._theState[group][name] = value

        return True

    ##
    #  Getters
    ##

    def getValue(self, group, name, default):
        """Return an arbitrary type value, if it exists. Otherwise,
        return the default value.
        """
        if group in self._theState:
            return self._theState[group].get(name, default)
        return default

    def getString(self, group, name, default):
        """Return the value as a string, if it exists. Otherwise, return
        the default value.
        """
        if group in self._theState:
            return checkString(self._theState[group].get(name, default), default)
        return default

    def getInt(self, group, name, default):
        """Return the value as an int, if it exists. Otherwise, return
        the default value.
        """
        if group in self._theState:
            return checkInt(self._theState[group].get(name, default), default)
        return default

    def getFloat(self, group, name, default):
        """Return the value as a float, if it exists. Otherwise, return
        the default value.
        """
        if group in self._theState:
            return checkFloat(self._theState[group].get(name, default), default)
        return default

    def getBool(self, group, name, default):
        """Return the value as a bool, if it exists. Otherwise, return
        the default value.
        """
        if group in self._theState:
            return checkBool(self._theState[group].get(name, default), default)
        return default

    def getEnum(self, group, name, lookup, default):
        """Return the value mapped to an enum. Otherwise return the
        default value
        """
        if issubclass(lookup, Enum):
            if group in self._theState:
                if name in self._theState[group]:
                    value = self._theState[group][name]
                    if value in lookup.__members__:
                        return lookup[value]
        return default

# END Class OptionState
