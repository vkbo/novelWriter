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

from PyQt5.QtCore import QRegularExpression

from novelwriter import CONFIG
from novelwriter.constants import nwRegEx
from novelwriter.types import QRegExUnicode


class RegExPatterns:

    @property
    def markdownItalic(self) -> QRegularExpression:
        """Markdown italic style."""
        rxRule = QRegularExpression(nwRegEx.FMT_EI)
        rxRule.setPatternOptions(QRegExUnicode)
        return rxRule

    @property
    def markdownBold(self) -> QRegularExpression:
        """Markdown bold style."""
        rxRule = QRegularExpression(nwRegEx.FMT_EB)
        rxRule.setPatternOptions(QRegExUnicode)
        return rxRule

    @property
    def markdownStrike(self) -> QRegularExpression:
        """Markdown strikethrough style."""
        rxRule = QRegularExpression(nwRegEx.FMT_ST)
        rxRule.setPatternOptions(QRegExUnicode)
        return rxRule

    @property
    def shortcodePlain(self) -> QRegularExpression:
        """Plain shortcode style."""
        rxRule = QRegularExpression(nwRegEx.FMT_SC)
        rxRule.setPatternOptions(QRegExUnicode)
        return rxRule

    @property
    def shortcodeValue(self) -> QRegularExpression:
        """Plain shortcode style."""
        rxRule = QRegularExpression(nwRegEx.FMT_SV)
        rxRule.setPatternOptions(QRegExUnicode)
        return rxRule

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
