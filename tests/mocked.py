"""
novelWriter – Test Suite Mocked Classes
=======================================

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

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget


class MockGuiMain(QWidget):

    def __init__(self):
        super().__init__()
        self.mainStatus = MockStatusBar()
        self.projPath = ""
        return

    def postLaunchTasks(self, cmdOpen):
        return

    def setStatus(self, message):
        return

    def openProject(self, projPath):
        self.projPath = projPath
        return

    def rebuildIndex(self):
        return

    def closeMain(self):
        return "closeMain"

    def close(self):
        return "close"


class MockStatusBar:

    def __init__(self):
        return

    def setStatus(self, text):
        return

    def updateProjectStatus(self, status):
        return


class MockTheme:

    def __init__(self):
        self.baseIconHeight = 20
        return

    def getPixmap(self, *a):
        return QPixmap()

    def getIcon(self, *a) -> QIcon:
        return QIcon()

    def getItemIcon(self, *a, **k) -> QIcon:
        return QIcon()


class MockApp:

    def __init__(self):
        return

    def installTranslator(self, language):
        return


# Error Functions
# ===============
# Mock functions that will raise errors instead.

def causeOSError(*args, **kwargs):
    raise OSError("Mock OSError")


def causeException(*args, **kwargs):
    raise Exception("Mock Exception")
