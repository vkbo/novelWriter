"""
novelWriter – GUI Init
======================

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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

from novelwriter.gui.doceditor import GuiDocEditor
from novelwriter.gui.docviewer import GuiDocViewer, GuiDocViewDetails
from novelwriter.gui.itemdetails import GuiItemDetails
from novelwriter.gui.mainmenu import GuiMainMenu
from novelwriter.gui.noveltree import GuiNovelView
from novelwriter.gui.outline import GuiOutlineView
from novelwriter.gui.projtree import GuiProjectView
from novelwriter.gui.statusbar import GuiMainStatus
from novelwriter.gui.theme import GuiTheme
from novelwriter.gui.viewsbar import GuiViewsBar

__all__ = [
    "GuiDocEditor",
    "GuiDocViewDetails",
    "GuiDocViewer",
    "GuiItemDetails",
    "GuiMainMenu",
    "GuiMainStatus",
    "GuiNovelView",
    "GuiOutlineView",
    "GuiProjectView",
    "GuiTheme",
    "GuiViewsBar",
]
