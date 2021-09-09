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

from novelwriter.dialogs.about import GuiAbout
from novelwriter.dialogs.docmerge import GuiDocMerge
from novelwriter.dialogs.docsplit import GuiDocSplit
from novelwriter.dialogs.itemeditor import GuiItemEditor
from novelwriter.dialogs.preferences import GuiPreferences
from novelwriter.dialogs.projdetails import GuiProjectDetails
from novelwriter.dialogs.projload import GuiProjectLoad
from novelwriter.dialogs.projsettings import GuiProjectSettings
from novelwriter.dialogs.quotes import GuiQuoteSelect
from novelwriter.dialogs.updates import GuiUpdates
from novelwriter.dialogs.wordlist import GuiWordList

__all__ = [
    "GuiAbout",
    "GuiDocMerge",
    "GuiDocSplit",
    "GuiItemEditor",
    "GuiPreferences",
    "GuiProjectDetails",
    "GuiProjectLoad",
    "GuiProjectSettings",
    "GuiQuoteSelect",
    "GuiUpdates",
    "GuiWordList",
]
