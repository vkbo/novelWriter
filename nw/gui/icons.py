# -*- coding: utf-8 -*-
"""novelWriter Icons Class

 novelWriter – Icons Class
===========================
 This class manages the GUI icons

 File History:
 Created: 2019-11-08 [0.4.0]

 This file is a part of novelWriter
 Copyright 2020, Veronica Berglyd Olsen

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

import logging
import nw

from os import path

from PyQt5.QtCore import QSize
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtGui import QIcon, QPixmap

logger = logging.getLogger(__name__)

class GuiIcons:

    # Icon keys should either be a .svg or .png file under the gui
    # theme folder, or have a fallback that is either compatible with
    # QIcon.fromTheme, as specified here:
    # https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html
    # or, if there is no fallback, the variable should be None.
    ICON_MAP = {
        "root"     : "drive-harddisk",
        "folder"   : "folder",
        "document" : "x-office-document",
        "trash"    : "user-trash",
        "orphan"   : "dialog-warning",
        "save"     : "document-save",
        "add"      : "list-add",
        "remove"   : "list-remove",
        "close"    : "edit-delete",
        "search"   : "edit-find",
        "replace"  : "edit-find-replace",
        "time"     : None,
        "globe"    : None,
    }

    DECO_MAP = {
        "nwicon"   : ["icons", "novelWriter.svg"],
        "export"   : ["graphics", "export.svg"],
        "merge"    : ["graphics", "merge.svg"],
        "settings" : ["graphics", "gear.svg"],
        "split"    : ["graphics", "split.svg"],
    }

    def __init__(self, theParent):

        self.mainConf  = nw.CONFIG
        self.theParent = theParent

        # Storage
        self.qIcons = {}

        # Look for files in
        self.priPath  = ""    # The gui theme's icon folder
        self.secPath  = ""    # The main assets icon folder
        self.prefDark = False # Load dark icons, if available

        return

    def initIcons(self, priPath):
        """Load all icons listed in the icon map. Can be overridden by
        the selected theme.
        """

        self.priPath  = priPath
        self.secPath  = self.mainConf.iconPath
        self.prefDark = self.mainConf.guiDark

        for iconKey in self.ICON_MAP.keys():
            self.qIcons[iconKey] = self._loadIcon(iconKey)

        return

    def loadDecoration(self, decoKey, decoSize=None):
        """Load graphical decoration element based on the decoration
        map. This function always returns a QSwgWidget.
        """

        if decoKey not in self.DECO_MAP:
            logger.error("Decoration with name '%s' does not exist" % decoKey)
            return QSvgWidget()

        svgPath = path.join(
            self.mainConf.assetPath,
            self.DECO_MAP[decoKey][0],
            self.DECO_MAP[decoKey][1]
        )
        if not path.isfile(svgPath):
            logger.error("Decoration file '%s' not in assets folder" % self.DECO_MAP[decoKey])
            return QSvgWidget()

        svgDeco = QSvgWidget(svgPath)
        if decoSize is not None:
            svgDeco.setFixedSize(QSize(decoSize[0],decoSize[1]))

        return svgDeco

    def getIcon(self, iconKey, iconSize=None):
        """Return an icon from the icon buffer. If it doesn't exist,
        return an empty icon.
        """
        if iconKey in self.qIcons:
            return self.qIcons[iconKey]
        return QIcon()

    def getPixmap(self, iconKey, iconSize):
        """Return an icon from the icon buffer as a QPixmap. If it
        doesn't exist, return an empty QPixmap.
        """
        if iconKey in self.qIcons:
            return self.qIcons[iconKey].pixmap(iconSize[0], iconSize[1], QIcon.Normal)
        return QPixmap()

    ##
    #  Internal Functions
    ##

    def _loadIcon(self, iconKey):
        """Load an icon from the assets or theme folder, with a
        preference for dark/light icons depending on theme type, if such
        an icon exists. Prefer svg files over png files. Always returns
        a QIcon.
        """

        if iconKey not in self.ICON_MAP:
            logger.error("Icon with name '%s' does not exist" % iconKey)
            return QIcon()

        if self.prefDark:
            iconSuffix = "dark"
        else:
            iconSuffix = "light"

        iconNames = []
        iconNames.append("%s-%s.svg" % (iconKey, iconSuffix))
        iconNames.append("%s-%s.png" % (iconKey, iconSuffix))
        iconNames.append("%s.svg" % iconKey)
        iconNames.append("%s.png" % iconKey)

        # Check theme folder
        loadFrom = None
        for iconName in iconNames:
            checkPath = path.join(self.priPath, iconName)
            if path.isfile(checkPath):
                loadFrom = checkPath
                logger.verbose("Loading icon '%s' from theme" % iconName)
                break
        if loadFrom is not None:
            return QIcon(loadFrom)

        # Check assets folder
        for iconName in iconNames:
            checkPath = path.join(self.secPath, iconName)
            if path.isfile(checkPath):
                loadFrom = checkPath
                logger.verbose("Loading icon '%s' from assets" % iconName)
                break
        if loadFrom is not None:
            return QIcon(loadFrom)

        # If we're still here, try to set from system theme
        if self.ICON_MAP[iconKey] is not None:
            logger.verbose("Loading icon '%s' from system theme" % iconKey)
            return QIcon().fromTheme(self.ICON_MAP[iconKey])

        # Give up and return an empty icomn
        logger.warning("Did not load an icon for '%s'" % iconKey)

        return QIcon()

# END Class GuiIcons
