"""
novelWriter – Shared Data Class
===============================

File History:
Created: 2023-08-10 [2.1b2]

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
from __future__ import annotations

import logging

from typing import TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain
    from novelwriter.gui.theme import GuiTheme
    from novelwriter.core.project import NWProject

logger = logging.getLogger(__name__)


class SharedData:

    def __init__(self) -> None:
        self._gui = None
        self._theme = None
        self._project = None
        return

    @property
    def mainGui(self) -> GuiMain:
        """Return the Main GUI instance."""
        if self._gui is None:
            raise Exception("UserData class not properly initialised")
        return self._gui

    @property
    def theme(self) -> GuiTheme:
        """Return the GUI Theme instance."""
        if self._theme is None:
            raise Exception("UserData class not properly initialised")
        return self._theme

    @property
    def project(self) -> NWProject:
        """Return the active NWProject instance."""
        if self._project is None:
            raise Exception("UserData class not properly initialised")
        return self._project

    @property
    def hasProject(self) -> bool:
        return self.project.isValid

    ##
    #  Methods
    ##

    def initSharedData(self, gui: GuiMain, theme: GuiTheme) -> None:
        """Initialise the UserData instance. This must be called as soon
        as the Main GUI is created to ensure the SHARED singleton has the
        properties needed for operation.
        """
        self._gui = gui
        self._theme = theme
        self._resetProject()
        logger.debug("SharedData instance initialised")
        return

    def openProject(self, path: str | Path) -> None:
        return

    def saveProject(self):
        return

    def closeProject(self, idleTime: float) -> None:
        self.project.closeProject(idleTime)
        return

    ##
    #  Internal Functions
    ##

    def _resetProject(self) -> None:
        """Create a new project instance."""
        from novelwriter.core.project import NWProject
        self._project = NWProject(self.mainGui)
        return

# END Class SharedData
