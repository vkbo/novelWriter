"""
novelWriter – Build Settings Class
==================================
A class to hold build settings for the build tool

File History:
Created: 2023-02-14 [2.1b1]

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

import logging

from enum import Enum

from PyQt5.QtCore import QT_TRANSLATE_NOOP

from novelwriter.core.item import NWItem
from novelwriter.core.project import NWProject

logger = logging.getLogger(__name__)

# The Settings Template
# =====================
# Each entry contains a tuple on the form:
# (type, default, [min value, max value])

SETTINGS_TEMPLATE = {
    "filter.includeNovel":    (bool, True),
    "filter.includeNotes":    (bool, False),
    "filter.includeInactive": (bool, False),
    "headings.fmtTitle":      (str, "%title%"),
    "headings.fmtChapter":    (str, "%title%"),
    "headings.fmtUnnumbered": (str, "%title%"),
    "headings.fmtScene":      (str, "%title%"),
    "headings.fmtSection":    (str, "%title%"),
    "headings.hideScene":     (bool, False),
    "headings.hideSection":   (bool, False),
    "text.includeSynopsis":   (bool, False),
    "text.includeComments":   (bool, False),
    "text.includeKeywords":   (bool, False),
    "text.includeBody":       (bool, True),
    "format.buildLang":       (str, "en_GB"),
    "format.textFont":        (str, ""),
    "format.textSize":        (str, ""),
    "format.lineHeight":      (float, 1.15, 0.75, 3.0),
    "format.justifyText":     (bool, False),
    "format.stripUnicode":    (bool, False),
    "odt.addColours":         (bool, True),
    "html.addStyles":         (bool, False),
}

SETTINGS_LABELS = {
    "filter":                 QT_TRANSLATE_NOOP("Builds", "Document Types"),
    "filter.includeNovel":    QT_TRANSLATE_NOOP("Builds", "Novel Documents"),
    "filter.includeNotes":    QT_TRANSLATE_NOOP("Builds", "Project Notes"),
    "filter.includeInactive": QT_TRANSLATE_NOOP("Builds", "Inactive Documents"),

    "headings":               QT_TRANSLATE_NOOP("Builds", "Headings"),
    "headings.fmtTitle":      QT_TRANSLATE_NOOP("Builds", "Title Heading"),
    "headings.fmtChapter":    QT_TRANSLATE_NOOP("Builds", "Chapter Heading"),
    "headings.fmtUnnumbered": QT_TRANSLATE_NOOP("Builds", "Unnumbered Chapter"),
    "headings.fmtScene":      QT_TRANSLATE_NOOP("Builds", "Scene Heading"),
    "headings.fmtSection":    QT_TRANSLATE_NOOP("Builds", "Section Heading"),
    "headings.hideScene":     QT_TRANSLATE_NOOP("Builds", "Hide Scene"),
    "headings.hideSection":   QT_TRANSLATE_NOOP("Builds", "Hide Section"),

    "text":                   QT_TRANSLATE_NOOP("Builds", "Text Content"),
    "text.includeSynopsis":   QT_TRANSLATE_NOOP("Builds", "Synopsis"),
    "text.includeComments":   QT_TRANSLATE_NOOP("Builds", "Comments"),
    "text.includeKeywords":   QT_TRANSLATE_NOOP("Builds", "Keywords"),
    "text.includeBody":       QT_TRANSLATE_NOOP("Builds", "Body Text"),

    "format":                 QT_TRANSLATE_NOOP("Builds", "Text Format"),
    "format.buildLang":       QT_TRANSLATE_NOOP("Builds", "Build Language"),
    "format.textFont":        QT_TRANSLATE_NOOP("Builds", "Font Family"),
    "format.textSize":        QT_TRANSLATE_NOOP("Builds", "Font Size"),
    "format.lineHeight":      QT_TRANSLATE_NOOP("Builds", "Line Height"),
    "format.justifyText":     QT_TRANSLATE_NOOP("Builds", "Justify Text Margins"),
    "format.stripUnicode":    QT_TRANSLATE_NOOP("Builds", "Replace Unicode Characters"),

    "odt":                    QT_TRANSLATE_NOOP("Builds", "Open Document"),
    "odt.addColours":         QT_TRANSLATE_NOOP("Builds", "Add Highlight Colours"),

    "html":                   QT_TRANSLATE_NOOP("Builds", "HTML"),
    "html.addStyles":         QT_TRANSLATE_NOOP("Builds", "Add CSS Styles"),
}


class FilterMode(Enum):

    UNKNOWN  = 0
    FILTERED = 1
    INCLUDED = 2
    EXCLUDED = 3
    SKIPPED  = 4

# END Enum FilterMode


class BuildSettings:

    def __init__(self):
        self._skiproot = set()
        self._excluded = set()
        self._included = set()
        self._settings = {k: v[1] for k, v in SETTINGS_TEMPLATE.items()}
        return

    def isFiltered(self, tHandle):
        return tHandle not in self._included and tHandle not in self._excluded

    def isIncluded(self, tHandle):
        return tHandle in self._included

    def isExcluded(self, tHandle):
        return tHandle in self._excluded

    def isRootAllowed(self, tHandle):
        return tHandle not in self._skiproot

    def setFiltered(self, tHandle):
        """Set an item as filtered.
        """
        self._excluded.discard(tHandle)
        self._included.discard(tHandle)
        return

    def setIncluded(self, tHandle):
        """Set an item as explicitly included.
        """
        self._excluded.discard(tHandle)
        self._included.add(tHandle)
        return

    def setExcluded(self, tHandle):
        """Set an item as explicitly excluded.
        """
        self._excluded.add(tHandle)
        self._included.discard(tHandle)
        return

    def setSkipRoot(self, tHandle, state):
        """Set a specific root folder as skipped or not.
        """
        if state is True:
            self._skiproot.discard(tHandle)
        elif state is False:
            self._skiproot.add(tHandle)
        return

    def setValue(self, key, value):
        """Set a specific value for a build setting.
        """
        if key not in SETTINGS_TEMPLATE:
            return False
        definition = SETTINGS_TEMPLATE[key]
        if not isinstance(value, definition[0]):
            return False
        if len(definition) == 4:
            value = min(max(value, definition[2]), definition[3])
        self._settings[key] = value
        logger.debug(f"Build Setting '{key}' set to: {value}")
        return True

    def getLabel(self, key):
        """Extract the label for a specific item.
        """
        return SETTINGS_LABELS.get(key, "ERROR")

    def getValue(self, key):
        """Get the value for a specific item, or return the default.
        """
        return self._settings.get(key, SETTINGS_TEMPLATE.get(key, (None, None)[1]))

    def checkItemFilter(self, project):
        """Return a dictionary of item handles with filter decissions
        applied.
        """
        result = {}
        if not isinstance(project, NWProject):
            return result

        incNovel = self.getValue("filter.includeNovel") or False
        incNotes = self.getValue("filter.includeNotes") or False
        incInactive = self.getValue("filter.includeInactive") or False

        for item in project.tree:
            tHandle = item.itemHandle
            if not isinstance(item, NWItem):
                result[tHandle] = (False, FilterMode.UNKNOWN)
                continue
            if item.isInactiveClass() or (item.itemRoot in self._skiproot):
                result[tHandle] = (False, FilterMode.SKIPPED)
                continue
            if not item.isFileType():
                result[tHandle] = (False, FilterMode.SKIPPED)
                continue
            if tHandle in self._included:
                result[tHandle] = (True, FilterMode.INCLUDED)
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

        return result

# END Class BuildSettings
