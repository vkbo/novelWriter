"""
novelWriter – GUI Theme and Icons Classes Tester
================================================

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

import nw
import pytest

from PyQt5.QtGui import QColor, QPixmap, QIcon
from PyQt5.QtWidgets import QStyle, QMessageBox

keyDelay = 2
typeDelay = 1
stepDelay = 20


@pytest.mark.gui
def testGuiTheme_Main(qtbot, monkeypatch, nwMinimal, tmpDir):
    """Test the theme and icon classes.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.Yes)

    nwGUI = nw.main(["--testmode", "--config=%s" % nwMinimal, "--data=%s" % tmpDir, nwMinimal])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(500)

    # Change Settings
    assert nw.CONFIG.confPath == nwMinimal
    nw.CONFIG.guiTheme = "default_dark"
    nw.CONFIG.guiSyntax = "tomorrow_night_eighties"
    nw.CONFIG.guiIcons = "typicons_colour_dark"
    nw.CONFIG.guiDark = True
    nw.CONFIG.guiFont = "Cantarell"
    nw.CONFIG.guiFontSize = 11
    nw.CONFIG.confChanged = True
    assert nw.CONFIG.saveConfig()

    nwGUI.closeMain()
    nwGUI.close()
    del nwGUI

    # Re-open
    assert nw.CONFIG.confPath == nwMinimal
    nwGUI = nw.main(["--testmode", "--config=%s" % nwMinimal, "--data=%s" % tmpDir, nwMinimal])
    assert nwGUI.mainConf.confPath == nwMinimal
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(500)

    assert nw.CONFIG.guiTheme == "default_dark"
    assert nw.CONFIG.guiSyntax == "tomorrow_night_eighties"
    assert nw.CONFIG.guiIcons == "typicons_colour_dark"
    assert nw.CONFIG.guiDark is True
    assert nw.CONFIG.guiFont == "Cantarell"
    assert nw.CONFIG.guiFontSize == 11

    # Check GUI Colours
    thePalette = nwGUI.palette()
    assert thePalette.window().color()          == QColor(54, 54, 54)
    assert thePalette.windowText().color()      == QColor(174, 174, 174)
    assert thePalette.base().color()            == QColor(62, 62, 62)
    assert thePalette.alternateBase().color()   == QColor(67, 67, 67)
    assert thePalette.text().color()            == QColor(174, 174, 174)
    assert thePalette.toolTipBase().color()     == QColor(255, 255, 192)
    assert thePalette.toolTipText().color()     == QColor(21, 21, 13)
    assert thePalette.button().color()          == QColor(62, 62, 62)
    assert thePalette.buttonText().color()      == QColor(174, 174, 174)
    assert thePalette.brightText().color()      == QColor(174, 174, 174)
    assert thePalette.highlight().color()       == QColor(44, 152, 247)
    assert thePalette.highlightedText().color() == QColor(255, 255, 255)
    assert thePalette.link().color()            == QColor(44, 152, 247)
    assert thePalette.linkVisited().color()     == QColor(44, 152, 247)

    assert nwGUI.theTheme.statNone    == [150, 152, 150]
    assert nwGUI.theTheme.statSaved   == [39, 135, 78]
    assert nwGUI.theTheme.statUnsaved == [138, 32, 32]

    # Check Syntax Colours
    assert nwGUI.theTheme.colBack   == [45, 45, 45]
    assert nwGUI.theTheme.colText   == [204, 204, 204]
    assert nwGUI.theTheme.colLink   == [102, 153, 204]
    assert nwGUI.theTheme.colHead   == [102, 153, 204]
    assert nwGUI.theTheme.colHeadH  == [102, 153, 204]
    assert nwGUI.theTheme.colEmph   == [249, 145, 57]
    assert nwGUI.theTheme.colDialN  == [242, 119, 122]
    assert nwGUI.theTheme.colDialD  == [153, 204, 153]
    assert nwGUI.theTheme.colDialS  == [255, 204, 102]
    assert nwGUI.theTheme.colHidden == [153, 153, 153]
    assert nwGUI.theTheme.colKey    == [242, 119, 122]
    assert nwGUI.theTheme.colVal    == [204, 153, 204]
    assert nwGUI.theTheme.colSpell  == [242, 119, 122]
    assert nwGUI.theTheme.colError  == [153, 204, 153]
    assert nwGUI.theTheme.colRepTag == [102, 204, 204]
    assert nwGUI.theTheme.colMod    == [249, 145, 57]

    # Test Icon class
    theIcons = nwGUI.theTheme.theIcons
    nw.CONFIG.guiIcons = "invalid"
    assert not theIcons.updateTheme()
    nw.CONFIG.guiIcons = "typicons_colour_dark"
    assert theIcons.updateTheme()

    # Ask for a non-existent key
    anImg = theIcons.loadDecoration("nonsense", 20, 20)
    assert isinstance(anImg, QPixmap)
    assert anImg.isNull()

    # Add a non-existent file and request it
    theIcons.DECO_MAP["nonsense"] = "nofile.jpg"
    anImg = theIcons.loadDecoration("nonsense", 20, 20)
    assert isinstance(anImg, QPixmap)
    assert anImg.isNull()

    # Get a real image, with different size parameters
    anImg = theIcons.loadDecoration("wiz-back", 20, None)
    assert isinstance(anImg, QPixmap)
    assert not anImg.isNull()
    assert anImg.width() == 20
    assert anImg.height() >= 56

    anImg = theIcons.loadDecoration("wiz-back", None, 70)
    assert isinstance(anImg, QPixmap)
    assert not anImg.isNull()
    assert anImg.height() == 70
    assert anImg.width() >= 24

    anImg = theIcons.loadDecoration("wiz-back", 30, 70)
    assert isinstance(anImg, QPixmap)
    assert not anImg.isNull()
    assert anImg.height() == 70
    assert anImg.width() == 30

    anImg = theIcons.loadDecoration("wiz-back", None, None)
    assert isinstance(anImg, QPixmap)
    assert not anImg.isNull()
    assert anImg.height() >= 1500
    assert anImg.width() >= 500

    # Load icons
    anIcon = theIcons.getIcon("nonsense")
    assert isinstance(anIcon, QIcon)
    assert anIcon.isNull()

    anIcon = theIcons.getIcon("novelwriter")
    assert isinstance(anIcon, QIcon)
    assert not anIcon.isNull()

    # Add test icons and test alternative load paths
    theIcons.ICON_MAP["testicon1"] = (QStyle.SP_DriveHDIcon, None)
    anIcon = theIcons.getIcon("testicon1")
    assert isinstance(anIcon, QIcon)
    assert not anIcon.isNull()

    theIcons.ICON_MAP["testicon2"] = (None, "folder")
    anIcon = theIcons.getIcon("testicon2")
    assert isinstance(anIcon, QIcon)

    theIcons.ICON_MAP["testicon3"] = (None, None)
    anIcon = theIcons.getIcon("testicon3")
    assert isinstance(anIcon, QIcon)
    assert anIcon.isNull()

    # qtbot.stopForInteraction()
    nwGUI.closeMain()
    nwGUI.close()

# END Test testGuiTheme_Main
