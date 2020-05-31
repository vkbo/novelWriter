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
import configparser
import nw

from os import path, listdir

from PyQt5.QtCore import QSize
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QStyle, qApp

logger = logging.getLogger(__name__)

class GuiIcons:
    """The icon class manages the content of the assets/icons folder,
    and provides a simple interface for requesting icons. Only icons
    listed in the ICON_MAP are handled.

    Icons are loaded on first request, and then cached for further
    requests. Each icon key in the ICON_MAP has a series of fallbacks:
      * The first lookup is in the key-to-file map for the selected icon
        theme. The map is specified in the icons.conf file in the theme
        folder. The map makes it possible to preserve the original file
        name from the icon theme were the icons were extracted.
      * Second, if the icon does not exist in the theme map, the
        GuiIcons class will check if there is a QStyle icon specified in
        the ICON_MAP data tuple[0]. This will let Qt pull the closest
        system icon.
      * Third action is to look up the freedesktop icon theme name using
        the fromTheme Qt call. This generally produces the same results
        as the step above, but has more icons available in other cases.
      * Fourth, and finally, the icon is looked up in the fallback
        folder. Files in this folder must have the same file name as the
        novelWriter internal icon key, with '-dark' appended to it for
        the dark background version of the icon.
    """

    ICON_MAP = {
        # Project and GUI icons
        "cls_none"       : (QStyle.SP_DriveHDIcon,         "drive-harddisk"),
        "cls_novel"      : (QStyle.SP_DriveHDIcon,         "drive-harddisk"),
        "cls_plot"       : (QStyle.SP_DriveHDIcon,         "drive-harddisk"),
        "cls_character"  : (QStyle.SP_DriveHDIcon,         "drive-harddisk"),
        "cls_world"      : (QStyle.SP_DriveHDIcon,         "drive-harddisk"),
        "cls_timeline"   : (QStyle.SP_DriveHDIcon,         "drive-harddisk"),
        "cls_object"     : (QStyle.SP_DriveHDIcon,         "drive-harddisk"),
        "cls_entity"     : (QStyle.SP_DriveHDIcon,         "drive-harddisk"),
        "cls_custom"     : (QStyle.SP_DriveHDIcon,         "drive-harddisk"),
        "cls_trash"      : (QStyle.SP_DriveHDIcon,         "drive-harddisk"),
        "proj_document"  : (QStyle.SP_FileIcon,            "x-office-document"),
        "proj_folder"    : (QStyle.SP_DirIcon,             "folder"),
        "proj_nwx"       : (None,                          None),
        "status_lang"    : (None,                          None),
        "status_time"    : (None,                          None),
        "status_stats"   : (None,                          None),

        ## General Button Icons
        "folder-open"    : (QStyle.SP_DirOpenIcon,         "folder-open"),
        "delete"         : (QStyle.SP_DialogDiscardButton, "edit-delete"),
        "add"            : (None,                          "list-add"),
        "remove"         : (None,                          "list-remove"),
        "close"          : (QStyle.SP_DialogCloseButton,   "window-close"),
        "done"           : (QStyle.SP_DialogApplyButton,    None),
        "search"         : (None,                          "edit-find"),
        "search-replace" : (None,                          "edit-find-replace"),
        "clear"          : (QStyle.SP_LineEditClearButton, "clear_left"),
        "save"           : (QStyle.SP_DialogSaveButton,    "document-save"),
        "edit"           : (None,                          None),
        "check"          : (None,                          None),
        "cross"          : (None,                          None),

        ## Other Icons
        "warning"        : (QStyle.SP_MessageBoxWarning,   "dialog-warning"),
    }

    DECO_MAP = {
        "nwicon" : ["icons", "novelwriter.svg"],
    }

    def __init__(self, theParent):

        self.mainConf  = nw.CONFIG
        self.theParent = theParent

        # Storage
        self.qIcons    = {}
        self.themeMap  = {}
        self.themeList = []
        self.fbackName = "fallback"
        self.confName  = "icons.conf"

        # Icon Theme Path
        self.iconPath = None
        self.confFile = None

        # Icon Theme Meta
        self.themeName        = ""
        self.themeDescription = ""
        self.themeAuthor      = ""
        self.themeCredit      = ""
        self.themeUrl         = ""
        self.themeLicense     = ""
        self.themeLicenseUrl  = ""

        return

    ##
    #  Actions
    ##

    def updateTheme(self):
        """Update the theme map. This is more of an init, since many of
        the GUI icons cannot really be replaced without writing specific
        update functions for the classes where they're used.
        """

        logger.debug("Loading icon theme files")

        self.themeMap = {}
        checkPath = path.join(self.mainConf.iconPath, self.mainConf.guiIcons)
        if path.isdir(checkPath):
            logger.debug("Loading icon theme '%s'" % self.mainConf.guiIcons)
            self.iconPath = checkPath
            self.confFile = path.join(checkPath, self.confName)
        else:
            return False

        # Config File
        confParser = configparser.ConfigParser()
        try:
            confParser.read_file(open(self.confFile, mode="r", encoding="utf8"))
        except Exception as e:
            logger.error("Could not load icon theme settings from: %s" % self.confFile)
            return False

        ## Main
        cnfSec = "Main"
        if confParser.has_section(cnfSec):
            self.themeName        = self._parseLine( confParser, cnfSec, "name", "")
            self.themeDescription = self._parseLine( confParser, cnfSec, "description", "")
            self.themeAuthor      = self._parseLine( confParser, cnfSec, "author", "")
            self.themeCredit      = self._parseLine( confParser, cnfSec, "credit", "")
            self.themeUrl         = self._parseLine( confParser, cnfSec, "url", "")
            self.themeLicense     = self._parseLine( confParser, cnfSec, "license", "")
            self.themeLicenseUrl  = self._parseLine( confParser, cnfSec, "licenseurl", "")

        ## Palette
        cnfSec = "Map"
        if confParser.has_section(cnfSec):
            for iconName, iconFile in confParser.items(cnfSec):
                if iconName not in self.ICON_MAP:
                    logger.error("Unknown icon name '%s' in config file" % iconName)
                else:
                    iconPath = path.join(self.iconPath, iconFile)
                    if path.isfile(iconPath):
                        self.themeMap[iconName] = iconPath
                        logger.verbose("Icon slot '%s' using file '%s'" % (iconName, iconFile))
                    else:
                        logger.error("Icon file '%s' not in theme folder" % iconFile)

        logger.info("Loaded icon theme '%s'" % self.mainConf.guiIcons)

        return True

    ##
    #  Access Functions
    ##

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
        return, load it, and if it still doesn't exist, return an empty
        icon.
        """
        if iconKey in self.qIcons:
            return self.qIcons[iconKey]
        else:
            qIcon = self._loadIcon(iconKey)
            self.qIcons[iconKey] = qIcon
            return qIcon

    def getPixmap(self, iconKey, iconSize):
        """Return an icon from the icon buffer as a QPixmap. If it
        doesn't exist, return an empty QPixmap.
        """
        qIcon = self.getIcon(iconKey)
        return qIcon.pixmap(iconSize[0], iconSize[1], QIcon.Normal)

    def listThemes(self):
        """Scan the icons themes folder and list all themes.
        """
        if self.themeList:
            return self.themeList

        confParser = configparser.ConfigParser()
        for themeDir in listdir(self.mainConf.iconPath):
            themePath = path.join(self.mainConf.iconPath, themeDir)
            if not path.isdir(themePath) or themeDir == self.fbackName:
                continue
            themeConf = path.join(themePath, self.confName)
            logger.verbose("Checking icon theme config for '%s'" % themeDir)
            try:
                confParser.read_file(open(themeConf, mode="r", encoding="utf8"))
            except Exception as e:
                self.theParent.makeAlert(
                    ["Could not load theme config file.",str(e)], nwAlert.ERROR
                )
                continue
            themeName = ""
            if confParser.has_section("Main"):
                if confParser.has_option("Main", "name"):
                    themeName = confParser.get("Main", "name")
                    logger.verbose("Theme name is '%s'" % themeName)
            if themeName != "":
                self.themeList.append((themeDir, themeName))

        self.themeList = sorted(self.themeList, key=lambda x: x[1])

        return self.themeList

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
            logger.error("Requested unknown icon name '%s'" % iconKey)
            return QIcon()

        if iconKey in self.themeMap:
            logger.verbose("Loading: %s" % path.relpath(self.themeMap[iconKey]))
            return QIcon(self.themeMap[iconKey])

        # Next, we try to load the Qt style icons
        if self.ICON_MAP[iconKey][0] is not None:
            logger.verbose("Loading icon '%s' from Qt QStyle.standardIcon" % iconKey)
            return qApp.style().standardIcon(self.ICON_MAP[iconKey][0])

        # If we're still here, try to set from system theme
        if self.ICON_MAP[iconKey][1] is not None:
            logger.verbose("Loading icon '%s' from system theme" % iconKey)
            if QIcon().hasThemeIcon(self.ICON_MAP[iconKey][1]):
                return QIcon().fromTheme(self.ICON_MAP[iconKey][1])

        # Finally. we check if we have a fallback icon
        if self.mainConf.guiDark:
            fbackIcon = path.join(
                self.mainConf.iconPath, self.fbackName, "%s-dark.svg" % iconKey
            )
            if path.isfile(fbackIcon):
                logger.verbose("Loading icon '%s' from fallback theme" % iconKey)
                return QIcon(fbackIcon)
        fbackIcon = path.join(self.mainConf.iconPath, self.fbackName, "%s.svg" % iconKey)
        if path.isfile(fbackIcon):
            logger.verbose("Loading icon '%s' from fallback theme" % iconKey)
            return QIcon(fbackIcon)

        # Give up and return an empty icon
        logger.warning("Did not load an icon for '%s'" % iconKey)

        return QIcon()

    def _parseLine(self, confParser, cnfSec, cnfName, cnfDefault):
        """Simple wrapper for the config parser check for entry existing
        before arrempting to load.
        """
        if confParser.has_section(cnfSec):
            if confParser.has_option(cnfSec, cnfName):
                return confParser.get(cnfSec, cnfName)
        return cnfDefault

# END Class GuiIcons
