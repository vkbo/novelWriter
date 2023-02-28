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

from PyQt5.QtCore import QT_TRANSLATE_NOOP

logger = logging.getLogger(__name__)

# The Settings Template
# =====================
# Each entry contains a tuple on the form:
# (type, default, [min value, max value])

SETTINGS_TEMPLATE = {
    "headings.fmtTitle":      (str, "%title%"),
    "headings.fmtChapter":    (str, "%title%"),
    "headings.fmtUnnumbered": (str, "%title%"),
    "headings.fmtScene":      (str, "%title%"),
    "headings.fmtSection":    (str, "%title%"),
    "headings.hideScene":     (bool, False),
    "headings.hideSection":   (bool, False),
    "format.buildLang":       (str, "en_GB"),
    "format.textFont":        (str, ""),
    "format.textSize":        (str, ""),
    "format.lineHeight":      (float, 1.15, 0.75, 3.0),
    "format.justifyText":     (bool, False),
    "format.stripUnicode":    (bool, False),
    "odt.addColours":         (bool, True),
    "html.addStyles":         (bool, False),
}

FILTER_TEMPLATE = {
    "filter.includeSynopsis": (bool, False),
    "filter.includeComments": (bool, False),
    "filter.includeKeywords": (bool, False),
    "filter.includeBody":     (bool, True),
}

SETTINGS_LABELS = {
    "headings":               QT_TRANSLATE_NOOP("Builds", "Headings"),
    "headings.fmtTitle":      QT_TRANSLATE_NOOP("Builds", "Title Heading"),
    "headings.fmtChapter":    QT_TRANSLATE_NOOP("Builds", "Chapter Heading"),
    "headings.fmtUnnumbered": QT_TRANSLATE_NOOP("Builds", "Unnumbered Chapter"),
    "headings.fmtScene":      QT_TRANSLATE_NOOP("Builds", "Scene Heading"),
    "headings.fmtSection":    QT_TRANSLATE_NOOP("Builds", "Section Heading"),
    "headings.hideScene":     QT_TRANSLATE_NOOP("Builds", "Hide Scene"),
    "headings.hideSection":   QT_TRANSLATE_NOOP("Builds", "Hide Section"),

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

FILTER_LABELS = {
    "filter.includeSynopsis": QT_TRANSLATE_NOOP("Builds", "Synopsis"),
    "filter.includeComments": QT_TRANSLATE_NOOP("Builds", "Comments"),
    "filter.includeKeywords": QT_TRANSLATE_NOOP("Builds", "Keywords"),
    "filter.includeBody":     QT_TRANSLATE_NOOP("Builds", "Body Text"),
}


class BuildSettings:

    def __init__(self):

        self._data = {}

        self._excluded = set()
        self._included = set()

        self._loadTemplate()

        return

    def isIncluded(self, tHandle):
        return tHandle in self._included

    def isExcluded(self, tHandle):
        return tHandle in self._excluded

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

    ##
    #  Internal Functions
    ##

    def _loadTemplate(self):
        """Populate the data dictionary from the template.
        """
        return

# END Class BuildSettings
