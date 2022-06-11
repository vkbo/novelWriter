"""
novelWriter – GUI Theme and Icons Classes Tester
================================================

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

import pytest
import novelwriter

from PyQt5.QtGui import QColor, QPixmap, QIcon
from PyQt5.QtWidgets import QMessageBox

keyDelay = 2
typeDelay = 1
stepDelay = 20


@pytest.mark.gui
def testGuiTheme_Main(qtbot, monkeypatch, nwMinimal, tmpDir):
    """Test the theme and icon classes.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: QMessageBox.Yes)

    nwGUI = novelwriter.main(
        ["--testmode", "--config=%s" % nwMinimal, "--data=%s" % tmpDir, nwMinimal]
    )
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.wait(stepDelay)

    # Change Settings
    assert novelwriter.CONFIG.confPath == nwMinimal
    novelwriter.CONFIG.guiTheme = "default_dark"
    novelwriter.CONFIG.guiSyntax = "tomorrow_night_eighties"
    novelwriter.CONFIG.guiIcons = "typicons_colour_dark"
    novelwriter.CONFIG.guiFont = "Cantarell"
    novelwriter.CONFIG.guiFontSize = 11
    novelwriter.CONFIG.confChanged = True
    assert novelwriter.CONFIG.saveConfig()

    nwGUI.closeMain()
    nwGUI.close()
    del nwGUI

    # Re-open
    assert novelwriter.CONFIG.confPath == nwMinimal
    nwGUI = novelwriter.main(
        ["--testmode", "--config=%s" % nwMinimal, "--data=%s" % tmpDir, nwMinimal]
    )
    assert nwGUI.mainConf.confPath == nwMinimal
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.wait(stepDelay)

    assert novelwriter.CONFIG.guiTheme == "default_dark"
    assert novelwriter.CONFIG.guiSyntax == "tomorrow_night_eighties"
    assert novelwriter.CONFIG.guiIcons == "typicons_dark"
    assert novelwriter.CONFIG.guiFont != ""
    assert novelwriter.CONFIG.guiFontSize > 0

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

    assert nwGUI.mainTheme.statNone    == [150, 152, 150]
    assert nwGUI.mainTheme.statSaved   == [39, 135, 78]
    assert nwGUI.mainTheme.statUnsaved == [138, 32, 32]

    # Check Syntax Colours
    assert nwGUI.mainTheme.colBack   == [45, 45, 45]
    assert nwGUI.mainTheme.colText   == [204, 204, 204]
    assert nwGUI.mainTheme.colLink   == [102, 153, 204]
    assert nwGUI.mainTheme.colHead   == [102, 153, 204]
    assert nwGUI.mainTheme.colHeadH  == [102, 153, 204]
    assert nwGUI.mainTheme.colEmph   == [249, 145, 57]
    assert nwGUI.mainTheme.colDialN  == [242, 119, 122]
    assert nwGUI.mainTheme.colDialD  == [153, 204, 153]
    assert nwGUI.mainTheme.colDialS  == [255, 204, 102]
    assert nwGUI.mainTheme.colHidden == [153, 153, 153]
    assert nwGUI.mainTheme.colKey    == [242, 119, 122]
    assert nwGUI.mainTheme.colVal    == [204, 153, 204]
    assert nwGUI.mainTheme.colSpell  == [242, 119, 122]
    assert nwGUI.mainTheme.colError  == [153, 204, 153]
    assert nwGUI.mainTheme.colRepTag == [102, 204, 204]
    assert nwGUI.mainTheme.colMod    == [249, 145, 57]

    # Test Icon class
    iconCache = nwGUI.mainTheme.iconCache
    novelwriter.CONFIG.guiIcons = "invalid"
    assert iconCache.updateTheme() is True
    assert novelwriter.CONFIG.guiIcons == "typicons_light"

    # Ask for a non-existent key
    anImg = iconCache.loadDecoration("nonsense", 20, 20)
    assert isinstance(anImg, QPixmap)
    assert anImg.isNull()

    # Add a non-existent file and request it
    iconCache.DECO_MAP["nonsense"] = "nofile.jpg"
    anImg = iconCache.loadDecoration("nonsense", 20, 20)
    assert isinstance(anImg, QPixmap)
    assert anImg.isNull()

    # Get a real image, with different size parameters
    anImg = iconCache.loadDecoration("wiz-back", 20, None)
    assert isinstance(anImg, QPixmap)
    assert not anImg.isNull()
    assert anImg.width() == 20
    assert anImg.height() >= 56

    anImg = iconCache.loadDecoration("wiz-back", None, 70)
    assert isinstance(anImg, QPixmap)
    assert not anImg.isNull()
    assert anImg.height() == 70
    assert anImg.width() >= 24

    anImg = iconCache.loadDecoration("wiz-back", 30, 70)
    assert isinstance(anImg, QPixmap)
    assert not anImg.isNull()
    assert anImg.height() == 70
    assert anImg.width() == 30

    anImg = iconCache.loadDecoration("wiz-back", None, None)
    assert isinstance(anImg, QPixmap)
    assert not anImg.isNull()
    assert anImg.height() >= 1500
    assert anImg.width() >= 500

    # Load icons
    anIcon = iconCache.getIcon("nonsense")
    assert isinstance(anIcon, QIcon)
    assert anIcon.isNull()

    anIcon = iconCache.getIcon("novelwriter")
    assert isinstance(anIcon, QIcon)
    assert not anIcon.isNull()

    # Check return empty icon if file not found
    iconCache.ICON_KEYS.add("testicon3")
    anIcon = iconCache.getIcon("testicon3")
    assert isinstance(anIcon, QIcon)
    assert anIcon.isNull()

    # qtbot.stopForInteraction()
    nwGUI.closeMain()
    nwGUI.close()

# END Test testGuiTheme_Main
