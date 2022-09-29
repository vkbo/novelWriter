"""
novelWriter – Project XML Read/Write
====================================
Classes for reading and writing the project XML file

File History:
Created: 2022-09-28 [1.7.b1]

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

import os
import logging

from enum import Enum
from lxml import etree

logger = logging.getLogger(__name__)


class XMLReadState(Enum):

    NO_ACTION     = 0
    NO_ERROR      = 1
    PARSED_BACKUP = 2
    CANNOT_PARSE  = 3

# END Class XMLReadState


class ProjectXMLReader:

    def __init__(self, path):

        self._path = path
        self._state = XMLReadState.NO_ACTION

        return

    def read(self):
        """
        """
        try:
            xml = etree.parse(self._path)
            self._state = XMLReadState.NO_ERROR

        except Exception as exc:
            # Trying to open backup file instead
            logger.error("Failed to parse project xml", exc_info=exc)
            self._state = XMLReadState.CANNOT_PARSE

            backFile = self._path[:-3]+"bak"
            if os.path.isfile(backFile):
                try:
                    xml = etree.parse(backFile)
                    self._state = XMLReadState.PARSED_BACKUP
                    logger.info("Backup project file parsed")
                except Exception as exc:
                    logger.error("Failed to parse backup project xml", exc_info=exc)
                    self._state = XMLReadState.CANNOT_PARSE
                    return False
            else:
                return False

        return True

    ##
    #  Internal Functions
    ##

# END Class ProjectXMLReader


class ProjectXMLWriter:

    def __init__(self, path):

        self._path = path
        self._error = None

        return

    def write(self):
        return

    ##
    #  Internal Functions
    ##

# END Class ProjectXMLWriter
