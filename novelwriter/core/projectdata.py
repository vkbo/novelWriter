"""
novelWriter – Project Data Class
================================
Data class for novelWriter projects

File History:
Created: 2022-10-30 [2.0rc2]

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

from __future__ import annotations

import uuid
import logging

from novelwriter.common import (
    checkBool, checkInt, checkStringNone, checkUuid, isHandle, simplified
)
from novelwriter.core.status import NWStatus

logger = logging.getLogger(__name__)


class NWProjectData:

    def __init__(self, theProject):

        self.theProject = theProject

        # Project Meta
        self._uuid = ""
        self._name = ""
        self._title = ""
        self._author = ""
        self._saveCount = 0
        self._autoCount = 0
        self._editTime = 0

        # Project Settings
        self._doBackup = True
        self._language = None
        self._spellCheck = False
        self._spellLang = None

        # Project Dictionaries
        self._initCounts = [0, 0]
        self._currCounts = [0, 0]
        self._lastHandle: dict[str, str | None] = {
            "editor":    None,
            "viewer":    None,
            "novelTree": None,
            "outline":   None,
        }
        self._autoReplace: dict[str, str] = {}
        self._titleFormat: dict[str, str] = {
            "title":      "%title%",
            "chapter":    "%title%",
            "unnumbered": "%title%",
            "scene":      "* * *",
            "section":    "",
        }

        self._status = NWStatus(NWStatus.STATUS)
        self._import = NWStatus(NWStatus.IMPORT)

        return

    ##
    #  Properties
    ##

    @property
    def uuid(self):
        return self._uuid

    @property
    def name(self):
        return self._name

    @property
    def title(self):
        return self._title

    @property
    def author(self):
        return self._author

    @property
    def saveCount(self):
        return self._saveCount

    @property
    def autoCount(self):
        return self._autoCount

    @property
    def editTime(self):
        return self._editTime

    @property
    def doBackup(self):
        return self._doBackup

    @property
    def language(self):
        return self._language

    @property
    def spellCheck(self):
        return self._spellCheck

    @property
    def spellLang(self):
        return self._spellLang

    @property
    def initCounts(self):
        return tuple(self._initCounts)

    @property
    def currCounts(self):
        return tuple(self._currCounts)

    @property
    def lastHandle(self):
        return self._lastHandle

    @property
    def autoReplace(self):
        return self._autoReplace

    @property
    def titleFormat(self):
        return self._titleFormat

    @property
    def itemStatus(self):
        return self._status

    @property
    def itemImport(self):
        return self._import

    ##
    #  Methods
    ##

    def incSaveCount(self):
        """Increment the save count by one.
        """
        self._saveCount += 1
        self.theProject.setProjectChanged(True)
        return

    def incAutoCount(self):
        """Increment the auto save count by one.
        """
        self._autoCount += 1
        self.theProject.setProjectChanged(True)
        return

    ##
    #  Getters
    ##

    def getLastHandle(self, component):
        """Retrieve the last used handle for a given component.
        """
        return self._lastHandle.get(component, None)

    def getTitleFormat(self, kind):
        """Retrieve the title format string for a given kind of header.
        """
        return self._titleFormat.get(kind, "%title%")

    ##
    #  Setters
    ##

    def setUuid(self, value):
        """Set the project id.
        """
        value = checkUuid(value, "")
        if not value:
            self._uuid = str(uuid.uuid4())
        elif value != self._uuid:
            self._uuid = value
            self.theProject.setProjectChanged(True)
        return

    def setName(self, value):
        """Set a new project name.
        """
        if value != self._name:
            self._name = simplified(str(value))
            self.theProject.setProjectChanged(True)
        return

    def setTitle(self, value):
        """Set a new novel title.
        """
        if value != self._title:
            self._title = simplified(str(value))
            self.theProject.setProjectChanged(True)
        return

    def setAuthor(self, value):
        """Set the author value.
        """
        if value != self._title:
            self._author = simplified(str(value))
            self.theProject.setProjectChanged(True)
        return

    def setSaveCount(self, value):
        """Set the save count from last session.
        """
        self._saveCount = checkInt(value, 0)
        self.theProject.setProjectChanged(True)
        return

    def setAutoCount(self, value):
        """Set the auto save count from last session.
        """
        self._autoCount = checkInt(value, 0)
        self.theProject.setProjectChanged(True)
        return

    def setEditTime(self, value):
        """Set tyje edit time from last session.
        """
        self._editTime = checkInt(value, 0)
        self.theProject.setProjectChanged(True)
        return

    def setDoBackup(self, value):
        """Set the do write backup flag.
        """
        if value != self._doBackup:
            self._doBackup = checkBool(value, False)
            self.theProject.setProjectChanged(True)
        return

    def setLanguage(self, value):
        """Set the project language.
        """
        if value != self._language:
            self._language = checkStringNone(value, None)
            self.theProject.setProjectChanged(True)
        return

    def setSpellCheck(self, value):
        """Set the spell check flag.
        """
        if value != self._spellCheck:
            self._spellCheck = checkBool(value, False)
            self.theProject.setProjectChanged(True)
        return

    def setSpellLang(self, value):
        """Set the spell check language.
        """
        if value != self._spellLang:
            self._spellLang = checkStringNone(value, None)
            self.theProject.setProjectChanged(True)
        return

    def setLastHandle(self, value, component=None):
        """Set a last used handle into the handle registry. If component
        is None, the value is assumed to be the whole dictionary of
        values.
        """
        if isinstance(component, str):
            self._lastHandle[component] = checkStringNone(value, None)
            self.theProject.setProjectChanged(True)
        elif isinstance(value, dict):
            for key, entry in value.items():
                if key in self._lastHandle:
                    self._lastHandle[key] = str(entry) if isHandle(entry) else None
            self.theProject.setProjectChanged(True)
        return

    def setInitCounts(self, novel=None, notes=None):
        """Set the worc count totals for novel and note files.
        """
        if novel is not None:
            self._initCounts[0] = checkInt(novel, 0)
            self._currCounts[0] = checkInt(novel, 0)
        if notes is not None:
            self._initCounts[1] = checkInt(notes, 0)
            self._currCounts[1] = checkInt(notes, 0)
        return

    def setCurrCounts(self, novel=None, notes=None):
        """Set the worc count totals for novel and note files.
        """
        if novel is not None:
            self._currCounts[0] = checkInt(novel, 0)
        if notes is not None:
            self._currCounts[1] = checkInt(notes, 0)
        return

    def setAutoReplace(self, value):
        """Set the auto-replace dictionary.
        """
        if isinstance(value, dict):
            self._autoReplace = {}
            for key, entry in value.items():
                if isinstance(entry, str):
                    self._autoReplace[key] = simplified(entry)
            self.theProject.setProjectChanged(True)
        return

    def setTitleFormat(self, value):
        """Set the title formats.
        """
        if isinstance(value, dict):
            for key, entry in value.items():
                if key in self._titleFormat and isinstance(entry, str):
                    self._titleFormat[key] = simplified(entry)
            self.theProject.setProjectChanged(True)
        return

# END Class NWProjectData
