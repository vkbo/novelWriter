"""
novelWriter – Main GUI i18n Tests
=================================

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

import sys
import novelwriter

import pytest

from PyQt5.QtWidgets import qApp, QMessageBox

LANG_DATA = {}
if sys.platform.startswith("linux"):
    try:
        from setup import buildQtI18n
        buildQtI18n()
        LANG_DATA = novelwriter.CONFIG.listLanguages(novelwriter.CONFIG.LANG_NW)
    except Exception:
        pass


@pytest.mark.gui
@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux Only")
@pytest.mark.skipif(not LANG_DATA, reason="No language data")
@pytest.mark.parametrize("language", [a for a, b in LANG_DATA])
def testI18n_Localisation(qtbot, monkeypatch, language, fncPath, fncConf):
    """test loading the gui with a specific language.
    """
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: QMessageBox.Ok)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Ok)
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Ok)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)

    # Set the test langauge
    monkeypatch.setattr("novelwriter.CONFIG", fncConf)
    fncConf.guiLocale = language
    fncConf.initLocalisation(qApp)

    nwGUI = novelwriter.main(["--testmode", f"--config={fncPath}", f"--data={fncPath}"])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.wait(20)
    nwGUI.closeMain()

    # Reset the app language
    fncConf.guiLocale = "en_GB"
    fncConf.initLocalisation(qApp)

# END Test testI18n_Localisation
