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

from novelwriter.common import (
    checkBool, checkInt, checkStringNone, minmax, simplified, checkString
)

logger = logging.getLogger(__name__)


NUM_VERSION = {
    "1.0": 0x0100,
    "1.1": 0x0101,
    "1.2": 0x0102,
    "1.3": 0x0103,
    "1.4": 0x0104,
}


class XMLReadState(Enum):

    NO_ACTION       = 0
    NO_ERROR        = 1
    PARSED_BACKUP   = 2
    CANNOT_PARSE    = 3
    NOT_NWX_FILE    = 4
    UNKNOWN_VERSION = 5
    PARSING_ERROR   = 6
    PARSED_OK       = 7
    WAS_LEGACY      = 8

# END Class XMLReadState


class ProjectXMLReader:

    def __init__(self, path):

        self._path = path
        self._state = XMLReadState.NO_ACTION

        self._data = {}
        self._version = 0x0000
        self._statusData = {}
        self._statusMap = {}

        return

    ##
    #  Properties
    ##

    @property
    def data(self):
        return self._data

    @property
    def state(self):
        return self._state

    ##
    #  Methods
    ##

    def read(self):
        """Read and parse the project XML file.
        """
        self._data = {}

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

        xRoot = xml.getroot()
        self._data["xmlRoot"] = str(xRoot.tag)
        if xRoot.tag != "novelWriterXML":
            self._state = XMLReadState.NOT_NWX_FILE
            return False

        # Changes:
        # 1.0 : Original file format.
        # 1.1 : Changes the way documents are structured in the project
        #       folder from data_X, where X is the first hex value of
        #       the handle, to a single content folder.
        # 1.2 : Changes the way autoReplace entries are stored. The 1.1
        #       parser will lose the autoReplace settings if allowed to
        #       read the file. Introduced in version 0.10.
        # 1.3 : Reduces the number of layouts to only two. One for novel
        #       documents and one for project notes. Introduced in
        #       version 1.5.
        # 1.4 : Introduces a more compact format for storing items. All
        #       settings aside from name are now attributes. This format
        #       also changes the way satus and importance labels are
        #       stored and handled. Introduced in version 1.7.

        fileVersion = str(xRoot.attrib.get("fileVersion", ""))
        if fileVersion in NUM_VERSION:
            self._version = NUM_VERSION[fileVersion]
        else:
            self._state = XMLReadState.UNKNOWN_VERSION
            return False

        self._data["xmlVersion"] = self._version
        self._data["appVersion"] = str(xRoot.attrib.get("appVersion", ""))
        self._data["hexVersion"] = str(xRoot.attrib.get("appVersion", ""))
        self._data["timeStamp"] = str(xRoot.attrib.get("timeStamp", ""))

        status = True
        for xSection in xRoot:
            if xSection.tag == "project":
                status &= self._parseProjectMeta(xSection)
            elif xSection.tag == "settings":
                status &= self._parseProjectSettings(xSection)
            elif xSection.tag == "content":
                if self._version >= 0x0104:
                    status &= self._parseProjectContent(xSection)
                else:
                    status &= self._parseProjectContentLegacy(xSection)
            else:
                logger.warning("Ignored <root/%s> in xml", xSection.tag)

        if not status:
            self._state = XMLReadState.PARSING_ERROR
            return False

        if self._version == 0x0104:
            self._state = XMLReadState.PARSED_OK
        else:
            self._state = XMLReadState.WAS_LEGACY

        return True

    ##
    #  Internal Functions
    ##

    def _parseProjectMeta(self, xSection):
        """Parse the project section of the XML file.
        """
        logger.debug("Parsing xml <root/project>")
        data = {}
        authors = []
        for xItem in xSection:
            if xItem.tag == "name":
                data["name"] = simplified(checkString(xItem.text, ""))
            elif xItem.tag == "title":
                data["title"] = simplified(checkString(xItem.text, ""))
            elif xItem.tag == "author":
                authors.append(simplified(checkString(xItem.text, "")))
            elif xItem.tag == "saveCount":
                data["saveCount"] = checkInt(xItem.text, 0)
            elif xItem.tag == "autoCount":
                data["autoCount"] = checkInt(xItem.text, 0)
            elif xItem.tag == "editTime":
                data["editTime"] = checkInt(xItem.text, 0)
            else:
                logger.warning("Ignored <root/project/%s> in xml", xItem.tag)

        data["authors"] = authors
        self._data["project"] = data

        return True

    def _parseProjectSettings(self, xSection):
        """Parse the settings section of the XML file.
        """
        logger.debug("Parsing xml <root/settings>")

        data = {}
        autoReplace = {}
        titleFormat = {}
        for xItem in xSection:
            if xItem.tag == "doBackup":
                data["doBackup"] = checkBool(xItem.text, False)
            elif xItem.tag == "language":
                data["language"] = checkStringNone(xItem.text, None)
            elif xItem.tag == "spellCheck":
                data["spellCheck"] = checkBool(xItem.text, False)
            elif xItem.tag == "spellLang":
                data["spellLang"] = checkStringNone(xItem.text, None)
            elif xItem.tag == "lastEdited":
                data["lastEdited"] = checkStringNone(xItem.text, None)
            elif xItem.tag == "lastViewed":
                data["lastViewed"] = checkStringNone(xItem.text, None)
            elif xItem.tag == "lastNovel":
                data["lastNovel"] = checkStringNone(xItem.text, None)
            elif xItem.tag == "lastOutline":
                data["lastOutline"] = checkStringNone(xItem.text, None)
            elif xItem.tag == "lastWordCount":
                data["lastWordCount"] = checkInt(xItem.text, 0)
            elif xItem.tag == "novelWordCount":
                data["novelWordCount"] = checkInt(xItem.text, 0)
            elif xItem.tag == "notesWordCount":
                data["notesWordCount"] = checkInt(xItem.text, 0)
            elif xItem.tag == "status":
                data["status"] = self._parseStatusImport(xItem, "status")
            elif xItem.tag in ("import", "importance"):
                data["import"] = self._parseStatusImport(xItem, "import")
            elif xItem.tag == "autoReplace":
                if self._version >= 0x0102:
                    for xEntry in xItem:
                        if xEntry.tag == "entry" and "key" in xEntry.attrib:
                            autoReplace[xEntry.attrib["key"]] = checkString(xEntry.text, "ERROR")
                else:  # Pre 1.2 format
                    for xEntry in xItem:
                        autoReplace[xEntry.tag] = checkString(xEntry.text, "ERROR")
            elif xItem.tag == "titleFormat":
                for xEntry in xItem:
                    titleFormat[xEntry.tag] = checkString(xEntry.text, "")
            else:
                logger.warning("Ignored <root/settings/%s> in xml", xItem.tag)

        data["autoReplace"] = autoReplace
        data["titleFormat"] = titleFormat
        self._data["settings"] = data

        return True

    def _parseProjectContent(self, xSection):
        """Parse the content section of the XML file.
        """
        logger.debug("Parsing xml <root/content>")

        data = []
        for xItem in xSection:
            if xItem.tag == "item":
                item = {}
                item["handle"] = xItem.attrib.get("handle", None)
                item["parent"] = xItem.attrib.get("parent", None)
                item["root"]   = xItem.attrib.get("root", None)
                item["order"]  = checkInt(xItem.attrib.get("order", 0), 0)
                item["type"]   = checkString(xItem.attrib.get("type", ""), "")
                item["class"]  = checkString(xItem.attrib.get("class", ""), "")
                item["layout"] = checkString(xItem.attrib.get("layout", ""), "")
                for xVal in xItem:
                    if xVal.tag == "meta":
                        item["expanded"]  = checkBool(xVal.attrib.get("expanded", False), False)
                        item["heading"]   = checkString(xVal.attrib.get("heading", "H0"), "H0")
                        item["charCount"] = checkInt(xVal.attrib.get("charCount", 0), 0)
                        item["wordCount"] = checkInt(xVal.attrib.get("wordCount", 0), 0)
                        item["paraCount"] = checkInt(xVal.attrib.get("paraCount", 0), 0)
                        item["cursorPos"] = checkInt(xVal.attrib.get("cursorPos", 0), 0)
                    elif xVal.tag == "name":
                        item["label"]  = simplified(checkString(xVal.text, ""))
                        item["status"] = checkStringNone(xVal.attrib.get("status", None), None)
                        item["import"] = checkStringNone(xVal.attrib.get("import", None), None)
                        item["active"] = checkBool(xVal.attrib.get("active", False), False)

                        # ToDo: Remove before 2.0 release. Only needed for 2.0 pre-releases.
                        if "exported" in xVal.attrib:
                            item["active"] = checkBool(xVal.attrib.get("exported", False), False)
                    else:
                        logger.warning("Ignored <root/content/item/%s> in xml", xVal.tag)
                data.append(item)
            else:
                logger.warning("Ignored item <root/content/%s> in xml", xItem.tag)

        self._data["content"] = data

        return True

    def _parseProjectContentLegacy(self, xSection):
        """Parse the content section of the XML file for version before 1.4.
        """
        logger.debug("Parsing xml <root/content> (legacy format)")
        depLayout = ("TITLE", "PAGE", "BOOK", "PARTITION", "UNNUMBERED", "CHAPTER", "SCENE")
        data = []
        for xItem in xSection:
            item = {}
            if xItem.tag == "item":
                item["handle"]  = xItem.attrib.get("handle", None)
                item["parent"]  = xItem.attrib.get("parent", None)
                item["root"]    = None  # Value was added in 1.4
                item["order"]   = checkInt(xItem.attrib.get("order", 0), 0)
                item["heading"] = "H0"  # Value was added in 1.4

                tmpStatus = ""
                for xVal in xItem:
                    if xVal.tag == "name":
                        item["label"] = simplified(checkString(xVal.text, ""))
                    elif xVal.tag == "status":
                        tmpStatus = checkStringNone(xVal.text, None)
                    elif xVal.tag == "type":
                        item["type"] = checkString(xVal.text, "")
                    elif xVal.tag == "class":
                        item["class"] = checkString(xVal.text, "")
                    elif xVal.tag == "layout":
                        item["layout"] = checkString(xVal.text, "")
                    elif xVal.tag == "expanded":
                        item["expanded"] = checkBool(xVal.text, False)
                    elif xVal.tag == "exported":  # Renamed to active in 1.4
                        item["active"] = checkBool(xVal.text, False)
                    elif xVal.tag == "charCount":
                        item["charCount"] = checkInt(xVal.text, 0)
                    elif xVal.tag == "wordCount":
                        item["wordCount"] = checkInt(xVal.text, 0)
                    elif xVal.tag == "paraCount":
                        item["paraCount"] = checkInt(xVal.text, 0)
                    elif xVal.tag == "cursorPos":
                        item["cursorPos"] = checkInt(xVal.text, 0)
                    else:
                        logger.warning("Ignored <root/content/item/%s> in xml", xVal.tag)

                # Status was split into separate status/import with a key in 1.4
                if item.get("class", "") in ("NOVEL", "ARCHIVE"):
                    item["status"] = self._getLegacyUnportStatus(tmpStatus, "status")
                else:
                    item["import"] = self._getLegacyUnportStatus(tmpStatus, "import")

                # A number of layouts were removed in 1.3
                if item.get("layout", "") in depLayout:
                    item["layout"] = "DOCUMENT"

                # The trast type was removed in 1.4
                if item.get("type", "") == "TRASH":
                    item["type"] = "ROOT"

                data.append(item)
            else:
                logger.warning("Ignored <root/content/%s> in xml", xItem.tag)

        self._data["content"] = data

        return True

    def _parseStatusImport(self, xItem, type):
        """Parse a status or importance entry.
        """
        data = self._statusData.get(type, {})
        for xEntry in xItem:
            if xEntry.tag == "entry":
                key = xEntry.attrib.get("key", f"{type[0]}{len(data):06x}")
                data[key] = {
                    "label": xEntry.text,
                    "count": checkInt(xEntry.attrib.get("count", 0), 0),
                    "colour": (
                        minmax(checkInt(xEntry.attrib.get("red", 0), 0), 0, 255),
                        minmax(checkInt(xEntry.attrib.get("green", 0), 0), 0, 255),
                        minmax(checkInt(xEntry.attrib.get("blue", 0), 0), 0, 255),
                    ),
                }
        self._statusData[type] = data

        return data

    def _getLegacyUnportStatus(self, label, type):
        """Look up the label in defined status or importance values.
        This is needed for file formats prior to 1.4 where the status
        was saved as the label, not the key.
        """
        if not self._statusMap.get(type):
            lookup = {}
            for key, entry in self._statusData.get(type, {}).items():
                lookup[entry.get("label", "")] = key
            self._statusMap[type] = lookup
            print(lookup)

        return self._statusMap.get(type, {}).get(label, None)

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
