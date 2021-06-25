"""
novelWriter – Dialogs Init
==========================

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

from nw.dialogs.about import GuiAbout
from nw.dialogs.docmerge import GuiDocMerge
from nw.dialogs.docsplit import GuiDocSplit
from nw.dialogs.itemeditor import GuiItemEditor
from nw.dialogs.preferences import GuiPreferences
from nw.dialogs.projload import GuiProjectLoad
from nw.dialogs.projsettings import GuiProjectSettings
from nw.dialogs.quotes import GuiQuoteSelect
from nw.dialogs.wordlist import GuiWordList

__all__ = [
    "GuiAbout",
    "GuiDocMerge",
    "GuiDocSplit",
    "GuiItemEditor",
    "GuiPreferences",
    "GuiProjectLoad",
    "GuiProjectSettings",
    "GuiQuoteSelect",
    "GuiWordList",
]
