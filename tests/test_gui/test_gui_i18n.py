"""
novelWriter – Main GUI i18n Tests
=================================

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

import sys
import pytest

from PyQt5.QtWidgets import qApp, QMessageBox

from novelwriter import CONFIG, main

LANG_DATA = CONFIG.listLanguages(CONFIG.LANG_NW)


@pytest.mark.gui
@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux Only")
@pytest.mark.skipif(not LANG_DATA, reason="No i18n Data")
@pytest.mark.parametrize("language", [a for a, b in LANG_DATA])
def testI18n_Localisation(qtbot, monkeypatch, language, fncPath):
    """Test loading the gui with a specific language."""
    monkeypatch.setattr(QMessageBox, "exec_", lambda *a: None)
    monkeypatch.setattr(QMessageBox, "result", lambda *a: QMessageBox.Yes)

    # Set the test langauge
    CONFIG.guiLocale = language
    CONFIG.initLocalisation(qApp)

    nwGUI = main(["--testmode", f"--config={fncPath}", f"--data={fncPath}"])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.wait(20)
    nwGUI.closeMain()

# END Test testI18n_Localisation
