"""
novelWriter – Project XML Read/Write
====================================

File History:
Created: 2022-09-28 [2.0rc2] XMLReadState
Created: 2022-09-28 [2.0rc2] ProjectXMLReader
Created: 2022-10-31 [2.0rc2] ProjectXMLWriter

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

import logging
import xml.etree.ElementTree as ET

from enum import Enum
from time import time
from typing import TYPE_CHECKING
from pathlib import Path

from novelwriter import __version__, __hexversion__
from novelwriter.common import (
    checkBool, checkInt, checkString, checkStringNone, formatTimeStamp,
    hexToInt, simplified, xmlIndent, yesNo
)

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.core.status import NWStatus
    from novelwriter.core.projectdata import NWProjectData

logger = logging.getLogger(__name__)

FILE_VERSION = "1.5"  # The current project file format version
FILE_REVISION = "1"   # The current project file format revision
HEX_VERSION = 0x0105

NUM_VERSION = {
    "1.0": 0x0100,  # Up to 0.7
    "1.1": 0x0101,  # Up to 0.10
    "1.2": 0x0102,  # Up to 1.5
    "1.3": 0x0103,  # Up to 2.0 Beta 1
    "1.4": 0x0104,  # Up to 2.0 RC 2
    "1.5": 0x0105,  # Current
}


class XMLReadState(Enum):
    """The state of an XML read process."""

    NO_ACTION       = 0
    NO_ERROR        = 1
    PARSED_BACKUP   = 2
    CANNOT_PARSE    = 3
    NOT_NWX_FILE    = 4
    UNKNOWN_VERSION = 5
    PARSED_OK       = 6
    WAS_LEGACY      = 7

# END Class XMLReadState


class ProjectXMLReader:
    """Core: Project XML Reader

    All data is read into a NWProjectData instance, which must be
    provided.

    File Format Version Change History
    ==================================
    1.0 Original file format.

    1.1 Changes the way documents are structured in the project folder
        from data_X, where X is the first hex value of the handle, to a
        single content folder. Introduced in version 0.7.

    1.2 Changes the way autoReplace entries are stored. Introduced in
        version 0.10.

    1.3 Reduces the number of layouts to only two. One for novel
        documents and one for project notes. Introduced in version 1.5.

    1.4 Introduces a more compact format for storing items. All settings
        aside from name are now attributes. This format also changes the
        way status and importance labels are stored. This format was only
        a part of version 2.0 RC 1

    1.5 The actual format released for 2.0. It moves last used handles
        and title formats into a key/value format similar to auto-
        replace, status and importance. It adds the heading value to
        the content item meta entry. It also moves meta data related to
        the project or the content into their respective section nodes
        as attributes. The id attribute was also added to the project.

        Rev 1: Drops the titleFormat section of settings.
    """

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._state = XMLReadState.NO_ACTION
        self._root = ""
        self._version = 0x0
        self._revision = 0
        self._appVersion = ""
        self._hexVersion = 0x0
        self._timeStamp = ""
        return

    ##
    #  Properties
    ##

    @property
    def state(self) -> XMLReadState:
        """Return the parsing state."""
        return self._state

    @property
    def xmlRoot(self) -> str:
        """Return the root tag name of the XNL file."""
        return self._root

    @property
    def xmlVersion(self) -> int:
        """Return the project XML version number."""
        return self._version

    @property
    def xmlRevision(self) -> int:
        """Return the project XML revision number."""
        return self._revision

    @property
    def appVersion(self) -> str:
        """Return the version number who wrote the file."""
        return self._appVersion

    @property
    def hexVersion(self) -> int:
        """Return the version number who wrote the file as hex."""
        return self._hexVersion

    @property
    def timeStamp(self) -> str:
        """Return the date and time when the file was written."""
        return self._timeStamp

    ##
    #  Methods
    ##

    def read(self, data: NWProjectData, content: list) -> bool:
        """Read and parse the project XML file."""
        tStart = time()
        logger.debug("Reading project XML")
        try:
            xml = ET.parse(str(self._path))
            self._state = XMLReadState.NO_ERROR
        except Exception as exc:
            # Trying to open backup file instead
            logger.error("Failed to parse project XML", exc_info=exc)
            self._state = XMLReadState.CANNOT_PARSE

            backFile = self._path.with_suffix(".bak")
            if backFile.is_file():
                try:
                    xml = ET.parse(str(backFile))
                    self._state = XMLReadState.PARSED_BACKUP
                    logger.info("Backup project file parsed")
                except Exception as exc:
                    logger.error("Failed to parse backup project XML", exc_info=exc)
                    self._state = XMLReadState.CANNOT_PARSE
                    return False
            else:
                self._state = XMLReadState.CANNOT_PARSE
                return False

        xRoot = xml.getroot()
        self._root = str(xRoot.tag)
        if self._root != "novelWriterXML":
            self._state = XMLReadState.NOT_NWX_FILE
            return False

        fileVersion = str(xRoot.attrib.get("fileVersion", ""))
        if fileVersion in NUM_VERSION:
            self._version = NUM_VERSION[fileVersion]
        else:
            self._state = XMLReadState.UNKNOWN_VERSION
            return False

        logger.debug("XML is '%s' version '%s'", self._root, fileVersion)

        self._revision = checkInt(xRoot.attrib.get("fileRevision"), 0)
        self._appVersion = str(xRoot.attrib.get("appVersion", ""))
        self._hexVersion = hexToInt(xRoot.attrib.get("hexVersion", ""))
        self._timeStamp = str(xRoot.attrib.get("timeStamp", ""))

        for xSection in xRoot:
            if xSection.tag == "project":
                self._parseProjectMeta(xSection, data)
            elif xSection.tag == "settings":
                self._parseProjectSettings(xSection, data)
            elif xSection.tag == "content":
                if self._version >= 0x0104:
                    self._parseProjectContent(xSection, data, content)
                else:
                    self._parseProjectContentLegacy(xSection, data, content)
            else:
                logger.warning("Ignored <root/%s> in XML", xSection.tag)

        if self._version == HEX_VERSION:
            self._state = XMLReadState.PARSED_OK
        else:
            self._state = XMLReadState.WAS_LEGACY

        logger.debug("Project XML loaded in %.3f ms", (time() - tStart)*1000)

        return True

    ##
    #  Internal Functions
    ##

    def _parseProjectMeta(self, xSection: ET.Element, data: NWProjectData) -> None:
        """Parse the project section of the XML file."""
        logger.debug("Parsing <project> section")

        data.setUuid(xSection.attrib.get("id", None))           # Added in 1.5
        data.setSaveCount(xSection.attrib.get("saveCount", 0))  # Moved in 1.5
        data.setAutoCount(xSection.attrib.get("autoCount", 0))  # Moved in 1.5
        data.setEditTime(xSection.attrib.get("editTime", 0))    # Moved in 1.5

        for xItem in xSection:
            if xItem.tag == "name":
                data.setName(xItem.text)
            elif xItem.tag == "title":
                data.setTitle(xItem.text)
            elif xItem.tag == "author":
                data.setAuthor(xItem.text)
            else:
                logger.warning("Ignored <root/project/%s> in XML", xItem.tag)

        # Deprecated Nodes
        if self._version < HEX_VERSION:
            for xItem in xSection:
                if xItem.tag == "saveCount":  # Moved to attribute in 1.5
                    data.setSaveCount(xItem.text)
                elif xItem.tag == "autoCount":  # Moved to attribute in 1.5
                    data.setAutoCount(xItem.text)
                elif xItem.tag == "editTime":  # Moved to attribute in 1.5
                    data.setEditTime(xItem.text)

        return

    def _parseProjectSettings(self, xSection: ET.Element, data: NWProjectData) -> None:
        """Parse the settings section of the XML file."""
        logger.debug("Parsing <settings> section")

        for xItem in xSection:
            if xItem.tag == "doBackup":
                data.setDoBackup(xItem.text)
            elif xItem.tag == "language":
                data.setLanguage(xItem.text)
            elif xItem.tag == "spellChecking":
                data.setSpellLang(xItem.text)
                data.setSpellCheck(xItem.attrib.get("auto", False))
            elif xItem.tag == "status":
                self._parseStatusImport(xItem, data.itemStatus)
            elif xItem.tag == "importance":
                self._parseStatusImport(xItem, data.itemImport)
            elif xItem.tag == "lastHandle":
                data.setLastHandles(self._parseDictKeyText(xItem))
            elif xItem.tag == "autoReplace":
                if self._version >= 0x0102:
                    data.setAutoReplace(self._parseDictKeyText(xItem))
                else:  # Pre 1.2 format
                    data.setAutoReplace(self._parseDictTagText(xItem))
            else:
                logger.warning("Ignored <root/settings/%s> in XML", xItem.tag)

        # Deprecated Nodes
        if self._version < HEX_VERSION:
            for xItem in xSection:
                if xItem.tag == "spellCheck":  # Changed to spellChecking in 1.5
                    data.setSpellCheck(xItem.text)
                elif xItem.tag == "spellLang":  # Changed to spellChecking in 1.5
                    data.setSpellLang(xItem.text)
                elif xItem.tag == "novelWordCount":  # Moved to content attribute in 1.5
                    data.setInitCounts(novel=xItem.text)
                elif xItem.tag == "notesWordCount":  # Moved to content attribute in 1.5
                    data.setInitCounts(notes=xItem.text)

        return

    def _parseProjectContent(
        self, xSection: ET.Element, data: NWProjectData, content: list
    ) -> None:
        """Parse the content section of the XML file."""
        logger.debug("Parsing <content> section")

        data.setInitCounts(novel=xSection.attrib.get("novelWords", None))  # Moved in 1.5
        data.setInitCounts(notes=xSection.attrib.get("notesWords", None))  # Moved in 1.5

        for xItem in xSection:
            if xItem.tag != "item":
                logger.warning("Ignored item <root/content/%s> in XML", xItem.tag)
                continue

            item = {}
            meta = {}
            name = {}
            itemName = ""

            item["handle"] = checkStringNone(xItem.attrib.get("handle"), None)
            item["parent"] = checkStringNone(xItem.attrib.get("parent"), None)
            item["root"]   = checkStringNone(xItem.attrib.get("root"), None)
            item["order"]  = checkInt(xItem.attrib.get("order"), 0)
            item["type"]   = checkString(xItem.attrib.get("type"), "NO_TYPE")
            item["class"]  = checkString(xItem.attrib.get("class"), "NO_CLASS")
            item["layout"] = checkString(xItem.attrib.get("layout"), "NO_LAYOUT")
            for xVal in xItem:
                if xVal.tag == "meta":
                    meta["expanded"]  = checkBool(xVal.attrib.get("expanded"), False)
                    meta["heading"]   = checkString(xVal.attrib.get("heading"), "H0")
                    meta["charCount"] = checkInt(xVal.attrib.get("charCount"), 0)
                    meta["wordCount"] = checkInt(xVal.attrib.get("wordCount"), 0)
                    meta["paraCount"] = checkInt(xVal.attrib.get("paraCount"), 0)
                    meta["cursorPos"] = checkInt(xVal.attrib.get("cursorPos"), 0)
                elif xVal.tag == "name":
                    itemName = simplified(checkString(xVal.text, ""))
                    name["status"] = checkStringNone(xVal.attrib.get("status"), None)
                    name["import"] = checkStringNone(xVal.attrib.get("import"), None)
                    name["active"] = checkBool(xVal.attrib.get("active"), False)
                else:
                    logger.warning("Ignored <root/content/item/%s> in XML", xVal.tag)

            # Deprecated Nodes
            if self._version < HEX_VERSION:
                for xVal in xItem:
                    if xVal.tag == "name" and "exported" in xVal.attrib:
                        name["active"] = checkBool(xVal.attrib.get("exported"), False)

            content.append({
                "name": itemName,
                "itemAttr": item,
                "metaAttr": meta,
                "nameAttr": name,
            })

        return

    def _parseProjectContentLegacy(
        self, xSection: ET.Element, data: NWProjectData, content: list
    ) -> None:
        """Parse the content section of the XML file for older versions."""
        logger.debug("Parsing <content> section (legacy format)")

        # Create maps to look up name -> key for status and importance
        statusMap = {entry.get("name"): key for key, entry in data.itemStatus.items()}
        importMap = {entry.get("name"): key for key, entry in data.itemImport.items()}

        for xItem in xSection:
            if xItem.tag != "item":
                logger.warning("Ignored item <root/content/%s> in XML", xItem.tag)
                continue

            item = {}
            meta = {}
            name = {}
            itemName = ""

            item["handle"]  = checkStringNone(xItem.attrib.get("handle", None), None)
            item["parent"]  = checkStringNone(xItem.attrib.get("parent", None), None)
            item["root"]    = None  # Value was added in 1.4
            item["order"]   = checkInt(xItem.attrib.get("order", 0), 0)
            meta["heading"] = "H0"  # Value was added in 1.4

            tmpStatus = ""
            for xVal in xItem:
                if xVal.tag == "name":
                    itemName = simplified(checkString(xVal.text, ""))
                elif xVal.tag == "status":
                    tmpStatus = checkStringNone(xVal.text, None)
                elif xVal.tag == "type":
                    item["type"] = checkString(xVal.text, "")
                elif xVal.tag == "class":
                    item["class"] = checkString(xVal.text, "")
                elif xVal.tag == "layout":
                    item["layout"] = checkString(xVal.text, "")
                elif xVal.tag == "expanded":
                    meta["expanded"] = checkBool(xVal.text, False)
                elif xVal.tag == "exported":  # Renamed to active in 1.5
                    name["active"] = checkBool(xVal.text, False)
                elif xVal.tag == "charCount":
                    meta["charCount"] = checkInt(xVal.text, 0)
                elif xVal.tag == "wordCount":
                    meta["wordCount"] = checkInt(xVal.text, 0)
                elif xVal.tag == "paraCount":
                    meta["paraCount"] = checkInt(xVal.text, 0)
                elif xVal.tag == "cursorPos":
                    meta["cursorPos"] = checkInt(xVal.text, 0)
                else:
                    logger.warning("Ignored <root/content/item/%s> in XML", xVal.tag)

            # Status was split into separate status/import with a key in 1.4
            if item.get("class", "") in ("NOVEL", "ARCHIVE"):
                name["status"] = statusMap.get(tmpStatus, None)
            else:
                name["import"] = importMap.get(tmpStatus, None)

            # A number of layouts were removed in 1.3
            if item.get("layout", "") in (
                "TITLE", "PAGE", "BOOK", "PARTITION", "UNNUMBERED", "CHAPTER", "SCENE"
            ):
                item["layout"] = "DOCUMENT"

            # The trash type was removed in 1.4
            if item.get("type", "") == "TRASH":
                item["type"] = "ROOT"

            content.append({
                "name": itemName,
                "itemAttr": item,
                "metaAttr": meta,
                "nameAttr": name,
            })

        return

    def _parseStatusImport(self, xItem: ET.Element, sObject: NWStatus) -> None:
        """Parse a status or importance entry."""
        for xEntry in xItem:
            if xEntry.tag == "entry":
                key   = xEntry.attrib.get("key", None)
                red   = checkInt(xEntry.attrib.get("red", 0), 0)
                green = checkInt(xEntry.attrib.get("green", 0), 0)
                blue  = checkInt(xEntry.attrib.get("blue", 0), 0)
                count = checkInt(xEntry.attrib.get("count", 0), 0)
                sObject.write(key, xEntry.text or "", (red, green, blue), count)
        return

    def _parseDictKeyText(self, xItem: ET.Element) -> dict:
        """Parse a dictionary stored with key as an attribute and the
        value as the text property.
        """
        result = {}
        for xEntry in xItem:
            if xEntry.tag == "entry" and "key" in xEntry.attrib:
                result[xEntry.attrib["key"]] = checkString(xEntry.text, "")
        return result

    def _parseDictTagText(self, xItem) -> dict:
        """Parse a dictionary stored with key as the tag and the value
        as the text property.
        """
        return {xNode.tag: checkString(xNode.text, "") for xNode in xItem}

# END Class ProjectXMLReader


class ProjectXMLWriter:
    """Core: Project XML Writer

    The project writer class will only write a file according to the
    very latest spec.
    """

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._error = None
        return

    ##
    #  Properties
    ##

    @property
    def error(self) -> Exception | None:
        """Return the error status."""
        return self._error

    ##
    #  Methods
    ##

    def write(self, data: NWProjectData, content: list, saveTime: float, editTime: int) -> bool:
        """Write the project data and content to the XML files."""
        tStart = time()
        logger.debug("Writing project XML")

        xRoot = ET.Element("novelWriterXML", attrib={
            "appVersion": str(__version__),
            "hexVersion": str(__hexversion__),
            "fileVersion": FILE_VERSION,
            "fileRevision": FILE_REVISION,
            "timeStamp": formatTimeStamp(saveTime),
        })

        # Save Project Meta
        projAttr = {
            "id": data.uuid,
            "saveCount": str(data.saveCount),
            "autoCount": str(data.autoCount),
            "editTime": str(editTime),
        }

        xProject = ET.SubElement(xRoot, "project", attrib=projAttr)
        self._packSingleValue(xProject, "name", data.name)
        self._packSingleValue(xProject, "title", data.title)
        self._packSingleValue(xProject, "author", data.author)

        # Save Project Settings
        xSettings = ET.SubElement(xRoot, "settings")
        self._packSingleValue(xSettings, "doBackup", yesNo(data.doBackup))
        self._packSingleValue(xSettings, "language", data.language)
        self._packSingleValue(xSettings, "spellChecking", data.spellLang, attrib={
            "auto": yesNo(data.spellCheck)
        })
        self._packDictKeyValue(xSettings, "lastHandle", data.lastHandle)
        self._packDictKeyValue(xSettings, "autoReplace", data.autoReplace)

        # Save Status/Importance
        xStatus = ET.SubElement(xSettings, "status")
        for label, attrib in data.itemStatus.pack():
            self._packSingleValue(xStatus, "entry", label, attrib=attrib)

        xImport = ET.SubElement(xSettings, "importance")
        for label, attrib in data.itemImport.pack():
            self._packSingleValue(xImport, "entry", label, attrib=attrib)

        # Save Tree Content
        contAttr = {
            "items": str(len(content)),
            "novelWords": str(data.currCounts[0]),
            "notesWords": str(data.currCounts[1]),
        }

        xContent = ET.SubElement(xRoot, "content", attrib=contAttr)
        for item in content:
            xItem = ET.SubElement(xContent, "item", attrib=item.get("itemAttr", {}))
            ET.SubElement(xItem, "meta", attrib=item.get("metaAttr", {}))
            xName = ET.SubElement(xItem, "name", attrib=item.get("nameAttr", {}))
            xName.text = item["name"]

        # Write the XML tree to file
        tempFile = self._path.with_suffix(".tmp")
        backFile = self._path.with_suffix(".bak")
        try:
            xml = ET.ElementTree(xRoot)
            xmlIndent(xml)
            xml.write(tempFile, encoding="utf-8", xml_declaration=True)
        except Exception as exc:
            self._error = exc
            return False

        # If we're here, the file was successfully saved,
        # so let's sort out the temps and backups
        try:
            if self._path.exists():
                self._path.replace(backFile)
            tempFile.replace(self._path)
        except Exception as exc:
            self._error = exc
            return False

        logger.debug("Project XML saved in %.3f ms", (time() - tStart)*1000)

        return True

    ##
    #  Internal Functions
    ##

    def _packSingleValue(
        self, xParent: ET.Element, name: str, value: str | None, attrib: dict | None = None
    ) -> None:
        """Pack a single value into an XML element."""
        xItem = ET.SubElement(xParent, name, attrib=attrib or {})
        xItem.text = str(value) or ""
        return

    def _packDictKeyValue(self, xParent: ET.Element, name: str, data: dict) -> None:
        """Pack the entries of a dictionary into an XML element."""
        xItem = ET.SubElement(xParent, name)
        for key, value in data.items():
            if len(key) > 0:
                xEntry = ET.SubElement(xItem, "entry", attrib={"key": key})
                xEntry.text = str(value) or ""
        return

# END Class ProjectXMLWriter
