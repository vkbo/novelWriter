"""
novelWriter – Core Init
=======================

This file is a part of novelWriter
Copyright 2018–2021, Veronica Berglyd Olsen

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

from novelwriter.core.document import NWDoc
from novelwriter.core.index import NWIndex, countWords
from novelwriter.core.project import NWProject
from novelwriter.core.spellcheck import NWSpellCheck, NWSpellEnchant, NWSpellSimple
from novelwriter.core.tohtml import ToHtml
from novelwriter.core.toodt import ToOdt
from novelwriter.core.tomd import ToMarkdown

__all__ = [
    "countWords",
    "NWDoc",
    "NWIndex",
    "NWProject",
    "NWSpellCheck",
    "NWSpellEnchant",
    "NWSpellSimple",
    "ToHtml",
    "ToOdt",
    "ToMarkdown",
]
