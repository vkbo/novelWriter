"""
novelWriter – Project Data Class
================================
Class for holding the project settings

File History:
Created: 2022-10-30 [2.0rc1]

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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

from novelwriter.common import (
    checkBool, checkInt, checkStringNone, simplified
)

logger = logging.getLogger(__name__)


class NWProjectData:

    def __init__(self):

        # Project Meta
        self._name = ""
        self._title = ""
        self._authors = []
        self._saveCount = 0
        self._autoCount = 0
        self._editTime = 0

        # Project Settings
        self._doBackup = True
        self._language = None
        self._spellCheck = False
        self._spellLang = None
        self._lastHandle = {}
        self._lastCount = {}

        # Internal
        self._changed = False

        return

    ##
    #  Properties
    ##

    @property
    def name(self):
        return self._name

    @property
    def title(self):
        return self._title

    @property
    def authors(self):
        return self._authors

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
    def changed(self):
        return self._changed

    ##
    #  Methods
    ##

    def addAuthor(self, value):
        self._authors.append(simplified(str(value)))
        self._changed = True
        return

    def incSaveCount(self):
        self._saveCount += 1
        self._changed = True
        return

    def incAutoCount(self):
        self._autoCount += 1
        self._changed = True
        return

    def resetProjectChanged(self):
        self._changed = False

    ##
    #  Getters
    ##

    def getLastHandle(self, component):
        return self._lastHandle.get(component, None)

    def getLastCount(self, type):
        return self._lastCount.get(type, 0)

    def getAuthors(self, trAnd="and"):
        """Return a formatted string of authors.
        """
        nAuth = len(self._authors)
        authors = ""

        if nAuth == 1:
            authors = self._authors[0]
        elif nAuth > 1:
            authors = "%s %s %s" % (
                ", ".join(self._authors[0:-1]), trAnd, self._authors[-1]
            )

        return authors

    ##
    #  Setters
    ##

    def setName(self, value):
        self._name = simplified(str(value))
        self._changed = True
        return

    def setTitle(self, value):
        self._title = simplified(str(value))
        self._changed = True
        return

    def setAuthors(self, value):
        self._authors = []
        self._changed = True
        if isinstance(value, str):
            for author in value.splitlines():
                author = simplified(author)
                if author:
                    self.addAuthor(author)
            self._changed = True
        elif isinstance(value, list):
            self._authors = value
        return

    def setSaveCount(self, value):
        self._saveCount = checkInt(value, 0)
        self._changed = True
        return

    def setAutoCount(self, value):
        self._autoCount = checkInt(value, 0)
        self._changed = True
        return

    def setEditTime(self, value):
        self._editTime = checkInt(value, 0)
        self._changed = True
        return

    def setDoBackup(self, value):
        self._doBackup = checkBool(value, False)
        self._changed = True
        return

    def setLanguage(self, value):
        self._language = checkStringNone(value, None)
        self._changed = True
        return

    def setSpellCheck(self, value):
        self._spellCheck = checkBool(value, False)
        self._changed = True
        return

    def setSpellLang(self, value):
        self._spellLang = checkStringNone(value, None)
        self._changed = True
        return

    def setLastHandle(self, value, component):
        self._lastHandle[component] = checkStringNone(value, None)
        self._changed = True
        return

    def setLastCount(self, value, type):
        self._lastCount[type] = checkInt(value, 0)
        self._changed = True
        return

# END Class NWProjectData
