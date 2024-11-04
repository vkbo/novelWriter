"""
novelWriter – Text Pattern Functions
====================================

File History:
Created: 2024-06-01 [2.5rc1] RegExPatterns
Created: 2024-11-04 [2.6b1]  DialogParser

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

from novelwriter import CONFIG
from novelwriter.common import compact, uniqueCompact
from novelwriter.constants import nwRegEx


class RegExPatterns:

    # Static RegExes
    _rxUrl     = re.compile(nwRegEx.URL, re.ASCII)
    _rxWords   = re.compile(nwRegEx.WORDS, re.UNICODE)
    _rxBreak   = re.compile(nwRegEx.BREAK, re.UNICODE)
    _rxItalic  = re.compile(nwRegEx.FMT_EI, re.UNICODE)
    _rxBold    = re.compile(nwRegEx.FMT_EB, re.UNICODE)
    _rxStrike  = re.compile(nwRegEx.FMT_ST, re.UNICODE)
    _rxSCPlain = re.compile(nwRegEx.FMT_SC, re.UNICODE)
    _rxSCValue = re.compile(nwRegEx.FMT_SV, re.UNICODE)

    @property
    def url(self) -> re.Pattern:
        """Find URLs."""
        return self._rxUrl

    @property
    def wordSplit(self) -> re.Pattern:
        """Split text into words."""
        return self._rxWords

    @property
    def lineBreak(self) -> re.Pattern:
        """Find forced line break."""
        return self._rxBreak

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
    def dialogStyle(self) -> re.Pattern | None:
        """Dialogue detection rule based on user settings."""
        if CONFIG.dialogStyle > 0:
            end = "|$" if CONFIG.allowOpenDial else ""
            rx = []
            if CONFIG.dialogStyle in (1, 3):
                qO = CONFIG.fmtSQuoteOpen.strip()[:1]
                qC = CONFIG.fmtSQuoteClose.strip()[:1]
                rx.append(f"(?:\\B{qO}.*?(?:{qC}\\B{end}))")
            if CONFIG.dialogStyle in (2, 3):
                qO = CONFIG.fmtDQuoteOpen.strip()[:1]
                qC = CONFIG.fmtDQuoteClose.strip()[:1]
                rx.append(f"(?:\\B{qO}.*?(?:{qC}\\B{end}))")
            return re.compile("|".join(rx), re.UNICODE)
        return None

    @property
    def altDialogStyle(self) -> re.Pattern | None:
        """Dialogue alternative rule based on user settings."""
        if CONFIG.altDialogOpen and CONFIG.altDialogClose:
            qO = re.escape(compact(CONFIG.altDialogOpen))
            qC = re.escape(compact(CONFIG.altDialogClose))
            return re.compile(f"\\B{qO}.*?{qC}\\B", re.UNICODE)
        return None


REGEX_PATTERNS = RegExPatterns()


class DialogParser:

    __slots__ = (
        "_quotes", "_dialog", "_alternate", "_enabled",
        "_narrator", "_breakD", "_breakQ", "_mode",
    )

    def __init__(self) -> None:
        self._quotes = None
        self._dialog = ""
        self._alternate = ""
        self._enabled = False
        self._narrator = ""
        self._breakD = None
        self._breakQ = None
        self._mode = ""
        return

    @property
    def enabled(self) -> bool:
        """Return True if there are any settings to parse."""
        return self._enabled

    def initParser(self) -> None:
        """Init parser settings. This method must also be called when
        the config changes.
        """
        self._quotes = REGEX_PATTERNS.dialogStyle
        self._dialog = uniqueCompact(CONFIG.dialogLine)
        self._alternate = CONFIG.narratorDialog.strip()[:1]

        # One of the three modes are needed for the class to have
        # anything to do
        self._enabled = bool(self._quotes or self._dialog or self._alternate)

        # Build narrator break RegExes
        if narrator := CONFIG.narratorBreak.strip()[:1]:
            punct = re.escape(".,:;!?")
            self._breakD = re.compile(f"{narrator}.*?(?:{narrator}[{punct}]?|$)", re.UNICODE)
            self._breakQ = re.compile(f"{narrator}.*?(?:{narrator}[{punct}]?)", re.UNICODE)
            self._narrator = narrator
            self._mode = f" {narrator}"

        return

    def __call__(self, text: str) -> list[tuple[int, int]]:
        """Caller wrapper for dialogue processing."""
        temp: list[int] = []
        result: list[tuple[int, int]] = []
        if text:
            plain = True
            if self._dialog and text[0] in self._dialog:
                # The whole line is dialogue
                plain = False
                temp.append(0)
                temp.append(len(text))
                if self._breakD:
                    # Process narrator breaks in the dialogue
                    for res in self._breakD.finditer(text, 1):
                        temp.append(res.start(0))
                        temp.append(res.end(0))
            elif self._quotes:
                # Quoted dialogue is enabled, so we look for them
                for res in self._quotes.finditer(text):
                    plain = False
                    temp.append(res.start(0))
                    temp.append(res.end(0))
                    if self._breakQ:
                        for sub in self._breakQ.finditer(text, res.start(0), res.end(0)):
                            temp.append(sub.start(0))
                            temp.append(sub.end(0))

            if plain and self._alternate:
                # The main rules found no dialogue, so we check for
                # alternating dialogue sections, if enabled
                pos = 0
                for num, bit in enumerate(text.split(self._alternate)):
                    length = len(bit) + (1 if num > 0 else 0)
                    if num%2:
                        temp.append(pos)
                        temp.append(pos + length)
                    pos += length

            if temp:
                # Sort unique edges in increasing order, and add them in pairs
                start = None
                for pos in sorted(set(temp)):
                    if start is None:
                        start = pos
                    else:
                        result.append((start, pos))
                        start = None

        return result
