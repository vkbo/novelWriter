"""
novelWriter – EPUB Converter
============================

File History:
Created: 2025-04-05 [2.7b1] ToEpub

This file is a part of novelWriter
Copyright (C) 2025 Veronica Berglyd Olsen and novelWriter contributors

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

from pathlib import Path

from novelwriter.core.project import NWProject
from novelwriter.formats.tokenizer import Tokenizer

logger = logging.getLogger(__name__)


class ToEPub(Tokenizer):

    def __init__(self, project: NWProject) -> None:
        super().__init__(project)
        return

    ##
    #  Class Methods
    ##

    def doConvert(self) -> None:
        return

    def closeDocument(self) -> None:
        return

    def saveDocument(self, path: Path) -> None:
        return
