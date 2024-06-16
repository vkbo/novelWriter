"""
novelWriter – Build Settings
============================

File History:
Created: 2023-02-14 [2.1b1] BuildSettings
Created: 2023-05-22 [2.1b1] BuildCollection

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

import json
import logging
import uuid

from collections.abc import Iterable
from enum import Enum
from pathlib import Path

from PyQt5.QtCore import QT_TRANSLATE_NOOP, QCoreApplication

from novelwriter import CONFIG
from novelwriter.common import checkUuid, isHandle, jsonEncode
from novelwriter.constants import nwFiles, nwHeadFmt
from novelwriter.core.project import NWProject
from novelwriter.enum import nwBuildFmt
from novelwriter.error import logException

logger = logging.getLogger(__name__)

# The Settings Template
# =====================
# Each entry contains a tuple on the form:
# (type, default, [min value, max value])

SETTINGS_TEMPLATE = {
    "filter.includeNovel":     (bool, True),
    "filter.includeNotes":     (bool, False),
    "filter.includeInactive":  (bool, False),
    "headings.fmtTitle":       (str, nwHeadFmt.TITLE),
    "headings.fmtChapter":     (str, nwHeadFmt.TITLE),
    "headings.fmtUnnumbered":  (str, nwHeadFmt.TITLE),
    "headings.fmtScene":       (str, "* * *"),
    "headings.fmtAltScene":    (str, ""),
    "headings.fmtSection":     (str, ""),
    "headings.hideTitle":      (bool, False),
    "headings.hideChapter":    (bool, False),
    "headings.hideUnnumbered": (bool, False),
    "headings.hideScene":      (bool, False),
    "headings.hideAltScene":   (bool, False),
    "headings.hideSection":    (bool, True),
    "headings.centerTitle":    (bool, True),
    "headings.centerChapter":  (bool, False),
    "headings.centerScene":    (bool, False),
    "headings.breakTitle":     (bool, True),
    "headings.breakChapter":   (bool, True),
    "headings.breakScene":     (bool, False),
    "text.includeSynopsis":    (bool, False),
    "text.includeComments":    (bool, False),
    "text.includeKeywords":    (bool, False),
    "text.includeBodyText":    (bool, True),
    "text.ignoredKeywords":    (str, ""),
    "text.addNoteHeadings":    (bool, True),
    "format.textFont":         (str, CONFIG.textFont.toString()),
    "format.lineHeight":       (float, 1.15, 0.75, 3.0),
    "format.justifyText":      (bool, False),
    "format.stripUnicode":     (bool, False),
    "format.replaceTabs":      (bool, False),
    "format.keepBreaks":       (bool, True),
    "format.showDialogue":     (bool, False),
    "format.firstLineIndent":  (bool, False),
    "format.firstIndentWidth": (float, 1.4),
    "format.indentFirstPar":   (bool, False),
    "format.pageUnit":         (str, "cm"),
    "format.pageSize":         (str, "A4"),
    "format.pageWidth":        (float, 21.0),
    "format.pageHeight":       (float, 29.7),
    "format.topMargin":        (float, 2.0),
    "format.bottomMargin":     (float, 2.0),
    "format.leftMargin":       (float, 2.0),
    "format.rightMargin":      (float, 2.0),
    "odt.addColours":          (bool, True),
    "odt.pageHeader":          (str, nwHeadFmt.ODT_AUTO),
    "odt.pageCountOffset":     (int, 0),
    "html.addStyles":          (bool, True),
    "html.preserveTabs":       (bool, False),
}

SETTINGS_LABELS = {
    "filter":                  QT_TRANSLATE_NOOP("Builds", "Document Filters"),
    "filter.includeNovel":     QT_TRANSLATE_NOOP("Builds", "Novel Documents"),
    "filter.includeNotes":     QT_TRANSLATE_NOOP("Builds", "Project Notes"),
    "filter.includeInactive":  QT_TRANSLATE_NOOP("Builds", "Inactive Documents"),

    "headings":                QT_TRANSLATE_NOOP("Builds", "Headings"),
    "headings.fmtTitle":       QT_TRANSLATE_NOOP("Builds", "Partition Format"),
    "headings.fmtChapter":     QT_TRANSLATE_NOOP("Builds", "Chapter Format"),
    "headings.fmtUnnumbered":  QT_TRANSLATE_NOOP("Builds", "Unnumbered Format"),
    "headings.fmtScene":       QT_TRANSLATE_NOOP("Builds", "Scene Format"),
    "headings.fmtAltScene":    QT_TRANSLATE_NOOP("Builds", "Alt. Scene Format"),
    "headings.fmtSection":     QT_TRANSLATE_NOOP("Builds", "Section Format"),

    "text.grpContent":         QT_TRANSLATE_NOOP("Builds", "Text Content"),
    "text.includeSynopsis":    QT_TRANSLATE_NOOP("Builds", "Include Synopsis"),
    "text.includeComments":    QT_TRANSLATE_NOOP("Builds", "Include Comments"),
    "text.includeKeywords":    QT_TRANSLATE_NOOP("Builds", "Include Keywords"),
    "text.includeBodyText":    QT_TRANSLATE_NOOP("Builds", "Include Body Text"),
    "text.ignoredKeywords":    QT_TRANSLATE_NOOP("Builds", "Ignore These Keywords"),
    "text.grpInsert":          QT_TRANSLATE_NOOP("Builds", "Insert Content"),
    "text.addNoteHeadings":    QT_TRANSLATE_NOOP("Builds", "Add Titles for Notes"),

    "format.grpFormat":        QT_TRANSLATE_NOOP("Builds", "Text Format"),
    "format.textFont":         QT_TRANSLATE_NOOP("Builds", "Text Font"),
    "format.lineHeight":       QT_TRANSLATE_NOOP("Builds", "Line Height"),
    "format.grpOptions":       QT_TRANSLATE_NOOP("Builds", "Text Options"),
    "format.justifyText":      QT_TRANSLATE_NOOP("Builds", "Justify Text Margins"),
    "format.stripUnicode":     QT_TRANSLATE_NOOP("Builds", "Replace Unicode Characters"),
    "format.replaceTabs":      QT_TRANSLATE_NOOP("Builds", "Replace Tabs with Spaces"),
    "format.keepBreaks":       QT_TRANSLATE_NOOP("Builds", "Preserve Hard Line Breaks"),
    "format.showDialogue":     QT_TRANSLATE_NOOP("Builds", "Apply Dialogue Highlighting"),

    "format.grpParIndent":     QT_TRANSLATE_NOOP("Builds", "First Line Indent"),
    "format.firstLineIndent":  QT_TRANSLATE_NOOP("Builds", "Enable Indent"),
    "format.firstIndentWidth": QT_TRANSLATE_NOOP("Builds", "Indent Width"),
    "format.indentFirstPar":   QT_TRANSLATE_NOOP("Builds", "Indent First Paragraph"),

    "format.grpPage":          QT_TRANSLATE_NOOP("Builds", "Page Layout"),
    "format.pageUnit":         QT_TRANSLATE_NOOP("Builds", "Unit"),
    "format.pageSize":         QT_TRANSLATE_NOOP("Builds", "Page Size"),
    "format.pageWidth":        QT_TRANSLATE_NOOP("Builds", "Page Width"),
    "format.pageHeight":       QT_TRANSLATE_NOOP("Builds", "Page Height"),
    "format.topMargin":        QT_TRANSLATE_NOOP("Builds", "Top Margin"),
    "format.bottomMargin":     QT_TRANSLATE_NOOP("Builds", "Bottom Margin"),
    "format.leftMargin":       QT_TRANSLATE_NOOP("Builds", "Left Margin"),
    "format.rightMargin":      QT_TRANSLATE_NOOP("Builds", "Right Margin"),

    "odt":                     QT_TRANSLATE_NOOP("Builds", "Open Document (.odt)"),
    "odt.addColours":          QT_TRANSLATE_NOOP("Builds", "Add Highlight Colours"),
    "odt.pageHeader":          QT_TRANSLATE_NOOP("Builds", "Page Header"),
    "odt.pageCountOffset":     QT_TRANSLATE_NOOP("Builds", "Page Counter Offset"),

    "html":                    QT_TRANSLATE_NOOP("Builds", "HTML (.html)"),
    "html.addStyles":          QT_TRANSLATE_NOOP("Builds", "Add CSS Styles"),
    "html.preserveTabs":       QT_TRANSLATE_NOOP("Builds", "Preserve Tab Characters"),
}


class FilterMode(Enum):
    """The decision reason for an item in a filtered project."""

    UNKNOWN  = 0
    FILTERED = 1
    INCLUDED = 2
    EXCLUDED = 3
    SKIPPED  = 4
    ROOT     = 5


class BuildSettings:
    """Core: Build Settings Class

    This class manages the build settings for a Manuscript build job.
    The settings can be packed/unpacked to/from a dictionary for JSON.
    """

    def __init__(self) -> None:
        self._name = ""
        self._uuid = str(uuid.uuid4())
        self._path = CONFIG.homePath()
        self._build = ""
        self._order = 0
        self._format = nwBuildFmt.ODT
        self._skipRoot = set()
        self._excluded = set()
        self._included = set()
        self._settings = {k: v[1] for k, v in SETTINGS_TEMPLATE.items()}
        self._changed = False
        return

    @classmethod
    def fromDict(cls, data: dict) -> BuildSettings:
        """Create a build settings object from a dict."""
        cls = BuildSettings()
        cls.unpack(data)
        return cls

    ##
    #  Properties
    ##

    @property
    def name(self) -> str:
        """Return the build name."""
        return self._name

    @property
    def buildID(self) -> str:
        """Return the build ID as a UUID."""
        return self._uuid

    @property
    def order(self) -> int:
        """Return the build order."""
        return self._order

    @property
    def lastBuildPath(self) -> Path:
        """The last used build path."""
        if self._path.is_dir():
            return self._path
        return CONFIG.homePath()

    @property
    def lastBuildName(self) -> str:
        """The last used build name."""
        return self._build

    @property
    def lastFormat(self) -> nwBuildFmt:
        """The last used build format."""
        return self._format

    @property
    def changed(self) -> bool:
        """The changed status of the build."""
        return self._changed

    ##
    #  Getters
    ##

    @staticmethod
    def getLabel(key: str) -> str:
        """Extract the GUI label for a specific setting."""
        return QCoreApplication.translate("Builds", SETTINGS_LABELS.get(key, "ERROR"))

    def getStr(self, key: str) -> str:
        """Type safe value access for strings."""
        value = self._settings.get(key, SETTINGS_TEMPLATE.get(key, (None, None))[1])
        return str(value)

    def getBool(self, key: str) -> bool:
        """Type safe value access for bools."""
        value = self._settings.get(key, SETTINGS_TEMPLATE.get(key, (None, None))[1])
        return bool(value)

    def getInt(self, key: str) -> int:
        """Type safe value access for integers."""
        value = self._settings.get(key, SETTINGS_TEMPLATE.get(key, (None, None))[1])
        return int(value) if isinstance(value, (int, float)) else 0

    def getFloat(self, key: str) -> float:
        """Type safe value access for floats."""
        value = self._settings.get(key, SETTINGS_TEMPLATE.get(key, (None, None))[1])
        return float(value) if isinstance(value, (int, float)) else 0.0

    ##
    #  Setters
    ##

    def setName(self, name: str) -> None:
        """Set the build setting display name."""
        self._name = str(name)
        return

    def setBuildID(self, value: str | uuid.UUID) -> None:
        """Set a UUID build ID."""
        value = checkUuid(value, "")
        if not value:
            self._uuid = str(uuid.uuid4())
        elif value != self._uuid:
            self._uuid = value
        return

    def setOrder(self, value: int) -> None:
        """Set the build order."""
        if isinstance(value, int):
            self._order = value
        return

    def setLastBuildPath(self, path: Path | str | None) -> None:
        """Set the last used build path."""
        if isinstance(path, str):
            path = Path(path)
        if isinstance(path, Path) and path.is_dir():
            self._path = path
        else:
            self._path = CONFIG.homePath()
        self._changed = True
        return

    def setLastBuildName(self, name: str) -> None:
        """Set the last used build name."""
        self._build = str(name).strip()
        self._changed = True
        return

    def setLastFormat(self, value: nwBuildFmt) -> None:
        """Set the last used build format."""
        if isinstance(value, nwBuildFmt):
            self._format = value
            self._changed = True
        return

    def setFiltered(self, tHandle: str) -> None:
        """Set an item as filtered."""
        self._excluded.discard(tHandle)
        self._included.discard(tHandle)
        self._changed = True
        return

    def setIncluded(self, tHandle: str) -> None:
        """Set an item as explicitly included."""
        self._excluded.discard(tHandle)
        self._included.add(tHandle)
        self._changed = True
        return

    def setExcluded(self, tHandle: str) -> None:
        """Set an item as explicitly excluded."""
        self._excluded.add(tHandle)
        self._included.discard(tHandle)
        self._changed = True
        return

    def setAllowRoot(self, tHandle: str, state: bool) -> None:
        """Set a specific root folder as allowed or not."""
        if state is True:
            self._skipRoot.discard(tHandle)
            self._changed = True
        elif state is False:
            self._skipRoot.add(tHandle)
            self._changed = True
        return

    def setValue(self, key: str, value: str | int | bool | float) -> bool:
        """Set a specific value for a build setting."""
        if key not in SETTINGS_TEMPLATE:
            return False
        definition = SETTINGS_TEMPLATE[key]
        if not isinstance(value, definition[0]):
            return False
        if len(definition) == 4 and isinstance(value, (int, float)):
            value = min(max(value, definition[2]), definition[3])
        self._changed = value != self._settings[key]
        self._settings[key] = value
        return True

    ##
    #  Methods
    ##

    def isRootAllowed(self, tHandle: str) -> bool:
        """Check if a root handle is allowed in the build."""
        return tHandle not in self._skipRoot

    def buildItemFilter(
        self, project: NWProject, withRoots: bool = False
    ) -> dict[str, tuple[bool, FilterMode]]:
        """Return a dictionary of item handles with filter decisions
        applied.
        """
        result: dict[str, tuple[bool, FilterMode]] = {}
        if not isinstance(project, NWProject):
            return result

        incNovel = bool(self.getBool("filter.includeNovel"))
        incNotes = bool(self.getBool("filter.includeNotes"))
        incInactive = bool(self.getBool("filter.includeInactive"))

        postponed = []

        def allowRoot(rHandle: str | None) -> None:
            if rHandle in postponed and rHandle in result and rHandle is not None:
                result[rHandle] = (True, FilterMode.ROOT)
                postponed.remove(rHandle)

        for item in project.tree:
            tHandle = item.itemHandle
            if item.isInactiveClass() or (item.itemRoot in self._skipRoot):
                result[tHandle] = (False, FilterMode.SKIPPED)
                continue
            if withRoots and item.isRootType():
                result[tHandle] = (False, FilterMode.SKIPPED)
                postponed.append(tHandle)
                continue
            if not item.isFileType():
                result[tHandle] = (False, FilterMode.SKIPPED)
                continue
            if tHandle in self._included:
                result[tHandle] = (True, FilterMode.INCLUDED)
                allowRoot(item.itemRoot)
                continue
            if tHandle in self._excluded:
                result[tHandle] = (False, FilterMode.EXCLUDED)
                continue

            isNote = item.isNoteLayout()
            isNovel = item.isDocumentLayout()
            isActive = item.isActive

            byActive = isActive or (not isActive and incInactive)
            byLayout = (isNote and incNotes) or (isNovel and incNovel)

            isAllowed = byActive and byLayout

            result[tHandle] = (isAllowed, FilterMode.FILTERED)
            if isAllowed:
                allowRoot(item.itemRoot)

        return result

    def resetChangedState(self) -> None:
        """Reset the changed status of the settings object. This must be
        called when the changes have been safely saved or passed on.
        """
        self._changed = False
        return

    def pack(self) -> dict:
        """Pack all content into a JSON compatible dictionary."""
        logger.debug("Collecting build setting for '%s'", self._name)
        return {
            "name": self._name,
            "uuid": self._uuid,
            "path": str(self._path),
            "build": self._build,
            "order": self._order,
            "format": self._format.name,
            "settings": self._settings.copy(),
            "content": {
                "included": list(self._included),
                "excluded": list(self._excluded),
                "skipRoot": list(self._skipRoot),
            }
        }

    def unpack(self, data: dict) -> None:
        """Unpack a dictionary and populate the class."""
        content = data.get("content", {})
        settings = data.get("settings", {})
        included = content.get("included", [])
        excluded = content.get("excluded", [])
        skipRoot = content.get("skipRoot", [])

        self.setName(data.get("name", ""))
        self.setBuildID(data.get("uuid", ""))
        self.setOrder(data.get("order", 0))
        self.setLastBuildPath(data.get("path", None))
        self.setLastBuildName(data.get("build", ""))

        buildFmt = str(data.get("format", ""))
        if buildFmt in nwBuildFmt.__members__:
            self.setLastFormat(nwBuildFmt[buildFmt])

        if isinstance(included, list):
            self._included = set([h for h in included if isHandle(h)])
        if isinstance(excluded, list):
            self._excluded = set([h for h in excluded if isHandle(h)])
        if isinstance(skipRoot, list):
            self._skipRoot = set([h for h in skipRoot if isHandle(h)])

        self._settings = {k: v[1] for k, v in SETTINGS_TEMPLATE.items()}
        if isinstance(settings, dict):
            for key, value in settings.items():
                self.setValue(key, value)

        self._changed = False

        return


class BuildCollection:
    """Core: Build Collection Class

    This object holds all the build setting objects defined by the given
    project. The build settings are saved as a single JSON file in the
    project folder.
    """

    def __init__(self, project: NWProject) -> None:
        self._project = project
        self._lastBuild = ""
        self._defaultBuild = ""
        self._builds: dict[str, BuildSettings] = {}
        self._loadCollection()
        return

    def __len__(self) -> int:
        """Return the number of builds."""
        return len(self._builds)

    ##
    #  Properties
    ##

    @property
    def lastBuild(self) -> str:
        """Return the last active build."""
        return self._lastBuild

    @property
    def defaultBuild(self) -> str:
        """Return the default build."""
        return self._defaultBuild

    ##
    #  Getters
    ##

    def getBuild(self, buildID: str) -> BuildSettings | None:
        """Get a specific build settings object."""
        return self._builds.get(buildID, None)

    ##
    #  Setters
    ##

    def setBuildsState(self, lastBuild: str, order: list[str]) -> None:
        """Set the last active build id."""
        for i, key in enumerate(order):
            if build := self._builds.get(key):
                build.setOrder(i)
        self._lastBuild = lastBuild
        self._saveCollection()
        return

    def setDefaultBuild(self, buildID: str) -> None:
        """Set the default build id."""
        if buildID != self._defaultBuild:
            self._defaultBuild = buildID
            self._saveCollection()
        return

    def setBuild(self, build: BuildSettings) -> None:
        """Set build settings data in the collection."""
        if isinstance(build, BuildSettings):
            self._builds[build.buildID] = build
            self._saveCollection()
        return

    ##
    #  Methods
    ##

    def removeBuild(self, buildID: str) -> None:
        """Remove a build from the collection."""
        self._builds.pop(buildID, None)
        self._saveCollection()
        return

    def builds(self) -> Iterable[tuple[str, str]]:
        """Iterate over all available builds."""
        for buildID, build in sorted(self._builds.items(), key=lambda x: x[1].order):
            yield buildID, build.name
        return

    ##
    #  Internal Functions
    ##

    def _loadCollection(self) -> bool:
        """Load build collections file."""
        buildsFile = self._project.storage.getMetaFile(nwFiles.BUILDS_FILE)
        if not isinstance(buildsFile, Path):
            return False

        data = {}
        if buildsFile.exists():
            logger.debug("Loading builds file")
            try:
                with open(buildsFile, mode="r", encoding="utf-8") as inFile:
                    data = json.load(inFile)
            except Exception:
                logger.error("Failed to load builds file")
                logException()
                return False

        if not isinstance(data, dict):
            logger.error("Builds file is not a JSON object")
            return False

        builds = data.get("novelWriter.builds", None)
        if not isinstance(builds, dict):
            logger.error("No novelWriter.builds in the builds file")
            return False

        for key, entry in builds.items():
            if key == "lastBuild":
                self._lastBuild = str(entry)
            elif key == "defaultBuild":
                self._defaultBuild = str(entry)
            elif isinstance(entry, dict):
                self._builds[key] = BuildSettings.fromDict(entry)

        return True

    def _saveCollection(self) -> bool:
        """Save build collections file."""
        buildsFile = self._project.storage.getMetaFile(nwFiles.BUILDS_FILE)
        if not isinstance(buildsFile, Path):
            return False

        logger.debug("Saving builds file")
        try:
            data: dict[str, str | dict] = {
                "lastBuild": self._lastBuild,
                "defaultBuild": self._defaultBuild,
            }
            data.update({k: b.pack() for k, b in self._builds.items()})
            with open(buildsFile, mode="w+", encoding="utf-8") as outFile:
                outFile.write(jsonEncode({"novelWriter.builds": data}, nmax=4))
        except Exception:
            logger.error("Failed to save builds file")
            logException()
            return False

        return True
