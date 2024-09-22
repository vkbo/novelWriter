"""
novelWriter – Text Pattern Functions
====================================

File History:
Created: 2024-06-01 [2.5ec1]

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

import re

from PyQt5.QtCore import QRegularExpression

from novelwriter import CONFIG
from novelwriter.constants import nwRegEx
from novelwriter.types import QRegExUnicode


class RegExPatterns:

    # Static RegExes
    _rxItalic  = re.compile(nwRegEx.FMT_EI, re.UNICODE)
    _rxBold    = re.compile(nwRegEx.FMT_EB, re.UNICODE)
    _rxStrike  = re.compile(nwRegEx.FMT_ST, re.UNICODE)
    _rxSCPlain = re.compile(nwRegEx.FMT_SC, re.UNICODE)
    _rxSCValue = re.compile(nwRegEx.FMT_SV, re.UNICODE)

    @property
    def markdownItalic(self) -> re.Pattern:
        """Markdown italic style."""
        return self._rxItalic

    @property
    def markdownBold(self) -> re.Pattern:
        """Markdown bold style."""
        return self._rxBold

    @property
    def markdownStrike(self) -> re.Pattern:
        """Markdown strikethrough style."""
        return self._rxStrike

    @property
    def shortcodePlain(self) -> re.Pattern:
        """Plain shortcode style."""
        return self._rxSCPlain

    @property
    def shortcodeValue(self) -> re.Pattern:
        """Plain shortcode style."""
        return self._rxSCValue

    @property
    def dialogStyle(self) -> QRegularExpression:
        """Dialogue detection rule based on user settings."""
        symO = ""
        symC = ""
        if CONFIG.dialogStyle in (1, 3):
            symO += CONFIG.fmtSQuoteOpen
            symC += CONFIG.fmtSQuoteClose
        if CONFIG.dialogStyle in (2, 3):
            symO += CONFIG.fmtDQuoteOpen
            symC += CONFIG.fmtDQuoteClose

        rxEnd = "|$" if CONFIG.allowOpenDial else ""
        rxRule = QRegularExpression(f"\\B[{symO}].*?(?:[{symC}]\\B{rxEnd})")
        rxRule.setPatternOptions(QRegExUnicode)
        return rxRule

    @property
    def dialogLine(self) -> QRegularExpression:
        """Dialogue line rule based on user settings."""
        sym = QRegularExpression.escape(CONFIG.dialogLine)
        rxRule = QRegularExpression(f"^{sym}.*?$")
        rxRule.setPatternOptions(QRegExUnicode)
        return rxRule

    @property
    def narratorBreak(self) -> QRegularExpression:
        """Dialogue narrator break rule based on user settings."""
        sym = QRegularExpression.escape(CONFIG.narratorBreak)
        rxRule = QRegularExpression(f"\\B{sym}\\S.*?\\S{sym}\\B")
        rxRule.setPatternOptions(QRegExUnicode)
        return rxRule

    @property
    def altDialogStyle(self) -> QRegularExpression:
        """Dialogue alternative rule based on user settings."""
        symO = QRegularExpression.escape(CONFIG.altDialogOpen)
        symC = QRegularExpression.escape(CONFIG.altDialogClose)
        rxRule = QRegularExpression(f"\\B{symO}.*?{symC}\\B")
        rxRule.setPatternOptions(QRegExUnicode)
        return rxRule


REGEX_PATTERNS = RegExPatterns()
