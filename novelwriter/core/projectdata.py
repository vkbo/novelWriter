"""
novelWriter – Project Data Class
================================

File History:
Created: 2022-10-30 [2.0rc2] NWProjectData

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

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

import logging
import uuid

from typing import TYPE_CHECKING, Any

from novelwriter.common import (
    checkBool, checkInt, checkStringNone, checkUuid, isHandle, simplified
)
from novelwriter.core.status import NWStatus

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.core.project import NWProject

logger = logging.getLogger(__name__)


class NWProjectData:
    """Core: Project Data Class

    The class holds all project data from the main XML file, aside from
    the list of project items.
    """

    def __init__(self, project: NWProject) -> None:

        self._project = project

        # Project Meta
        self._uuid = ""
        self._name = ""
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
    def uuid(self) -> str:
        """Return the project ID."""
        return self._uuid

    @property
    def name(self) -> str:
        """Return the project name."""
        return self._name

    @property
    def author(self) -> str:
        """Return the project author."""
        return self._author

    @property
    def saveCount(self) -> int:
        """Return the count of project saves."""
        return self._saveCount

    @property
    def autoCount(self) -> int:
        """Return the count of project auto-saves."""
        return self._autoCount

    @property
    def editTime(self) -> int:
        """Return the number of seconds the project has been edited."""
        return self._editTime

    @property
    def doBackup(self) -> bool:
        """Return the backup setting."""
        return self._doBackup

    @property
    def language(self) -> str | None:
        """Return the project language setting."""
        return self._language

    @property
    def spellCheck(self) -> bool:
        """Return the spell check enabled setting."""
        return self._spellCheck

    @property
    def spellLang(self) -> str | None:
        """Return the spell check language."""
        return self._spellLang

    @property
    def initCounts(self) -> tuple[int, int]:
        """Return the initial count of words for novel and note
        documents.
        """
        return self._initCounts[0], self._initCounts[1]

    @property
    def currCounts(self) -> tuple[int, int]:
        """Return the current count of words for novel and note
        documents.
        """
        return self._currCounts[0], self._currCounts[1]

    @property
    def lastHandle(self) -> dict[str, str | None]:
        """Return the dictionary of last used handles for various
        components of the GUI.
        """
        return self._lastHandle

    @property
    def autoReplace(self) -> dict[str, str]:
        """Return the auto-replace dictionary."""
        return self._autoReplace

    @property
    def itemStatus(self) -> NWStatus:
        """Return the status settings object."""
        return self._status

    @property
    def itemImport(self) -> NWStatus:
        """Return the importance settings object."""
        return self._import

    ##
    #  Methods
    ##

    def incSaveCount(self) -> None:
        """Increment the save count by one."""
        self._saveCount += 1
        self._project.setProjectChanged(True)
        return

    def incAutoCount(self) -> None:
        """Increment the auto save count by one."""
        self._autoCount += 1
        self._project.setProjectChanged(True)
        return

    ##
    #  Getters
    ##

    def getLastHandle(self, component: str) -> str | None:
        """Retrieve the last used handle for a given component."""
        return self._lastHandle.get(component, None)

    ##
    #  Setters
    ##

    def setUuid(self, value: Any) -> None:
        """Set the project id."""
        value = checkUuid(value, "")
        if not value:
            self._uuid = str(uuid.uuid4())
        elif value != self._uuid:
            self._uuid = value
            self._project.setProjectChanged(True)
        return

    def setName(self, value: str | None) -> None:
        """Set a new project name."""
        if value != self._name:
            self._name = simplified(str(value or ""))
            self._project.setProjectChanged(True)
        return

    def setAuthor(self, value: str | None) -> None:
        """Set the author value."""
        if value != self._author:
            self._author = simplified(str(value or ""))
            self._project.setProjectChanged(True)
        return

    def setSaveCount(self, value: Any) -> None:
        """Set the save count from last session."""
        self._saveCount = checkInt(value, 0)
        self._project.setProjectChanged(True)
        return

    def setAutoCount(self, value: Any) -> None:
        """Set the auto save count from last session."""
        self._autoCount = checkInt(value, 0)
        self._project.setProjectChanged(True)
        return

    def setEditTime(self, value: Any) -> None:
        """Set the edit time from last session."""
        self._editTime = checkInt(value, 0)
        self._project.setProjectChanged(True)
        return

    def setDoBackup(self, value: Any) -> None:
        """Set the do write backup flag."""
        if value != self._doBackup:
            self._doBackup = checkBool(value, False)
            self._project.setProjectChanged(True)
        return

    def setLanguage(self, value: str | None) -> None:
        """Set the project language."""
        if value != self._language:
            self._language = checkStringNone(value, None)
            self._project.setProjectChanged(True)
        return

    def setSpellCheck(self, value: Any) -> None:
        """Set the spell check flag."""
        if value != self._spellCheck:
            self._spellCheck = checkBool(value, False)
            self._project.setProjectChanged(True)
        return

    def setSpellLang(self, value: str | None) -> None:
        """Set the spell check language."""
        if value != self._spellLang:
            self._spellLang = checkStringNone(value, None)
            self._project.setProjectChanged(True)
        return

    def setLastHandle(self, value: str | None, component: str) -> None:
        """Set a last used handle into the handle registry for a given
        component.
        """
        if isinstance(component, str):
            self._lastHandle[component] = checkStringNone(value, None)
            self._project.setProjectChanged(True)
        return

    def setLastHandles(self, value: dict) -> None:
        """Set the full last handles dictionary to a new set of values.
        This is intended to be used at project load.
        """
        if isinstance(value, dict):
            for key, entry in value.items():
                if key in self._lastHandle:
                    self._lastHandle[key] = str(entry) if isHandle(entry) else None
            self._project.setProjectChanged(True)
        return

    def setInitCounts(self, novel: Any = None, notes: Any = None) -> None:
        """Set the word count totals for novel and note files."""
        if novel is not None:
            self._initCounts[0] = checkInt(novel, 0)
            self._currCounts[0] = checkInt(novel, 0)
        if notes is not None:
            self._initCounts[1] = checkInt(notes, 0)
            self._currCounts[1] = checkInt(notes, 0)
        return

    def setCurrCounts(self, novel: Any = None, notes: Any = None) -> None:
        """Set the word count totals for novel and note files."""
        if novel is not None:
            self._currCounts[0] = checkInt(novel, 0)
        if notes is not None:
            self._currCounts[1] = checkInt(notes, 0)
        return

    def setAutoReplace(self, value: dict) -> None:
        """Set the auto-replace dictionary."""
        if isinstance(value, dict):
            self._autoReplace = {}
            for key, entry in value.items():
                if isinstance(entry, str):
                    self._autoReplace[key] = simplified(entry)
            self._project.setProjectChanged(True)
        return
