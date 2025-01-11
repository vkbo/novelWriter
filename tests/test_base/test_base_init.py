"""
novelWriter – Main Init Tester
==============================

This file is a part of novelWriter
Copyright (C) 2020 Veronica Berglyd Olsen and novelWriter contributors

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
import sys

import pytest

from novelwriter import CONFIG, logger, main

from tests.mocked import MockGuiMain


@pytest.mark.base
def testBaseInit_Launch(caplog, monkeypatch, fncPath):
    """Check launching the main GUI."""
    monkeypatch.setattr("novelwriter.guimain.GuiMain", MockGuiMain)

    # TestMode Launch
    nwGUI = main(["--testmode", f"--config={fncPath}", f"--data={fncPath}"])
    assert isinstance(nwGUI, MockGuiMain)

    # Darwin Launch
    caplog.clear()
    osDarwin = CONFIG.osDarwin
    CONFIG.osDarwin = True
    with monkeypatch.context() as mp:
        mp.setitem(sys.modules, "Foundation", None)
        nwGUI = main(["--testmode", f"--config={fncPath}", f"--data={fncPath}"])
        assert isinstance(nwGUI, MockGuiMain)

    CONFIG.osDarwin = osDarwin

    # Windows Launch
    caplog.clear()
    osWindows = CONFIG.osWindows
    CONFIG.osWindows = True
    with monkeypatch.context() as mp:
        mp.setitem(sys.modules, "ctypes", None)
        nwGUI = main(["--testmode", f"--config={fncPath}", f"--data={fncPath}"])
        assert isinstance(nwGUI, MockGuiMain)

    CONFIG.osWindows = osWindows

    # Normal Launch
    with monkeypatch.context() as mp:
        mp.setattr("PyQt6.QtWidgets.QApplication.__init__", lambda *a: None)
        mp.setattr("PyQt6.QtWidgets.QApplication.setApplicationName", lambda *a: None)
        mp.setattr("PyQt6.QtWidgets.QApplication.setApplicationVersion", lambda *a: None)
        mp.setattr("PyQt6.QtWidgets.QApplication.setWindowIcon", lambda *a: None)
        mp.setattr("PyQt6.QtWidgets.QApplication.setOrganizationDomain", lambda *a: None)
        mp.setattr("PyQt6.QtWidgets.QApplication.exec", lambda *a: 0)
        with pytest.raises(SystemExit) as ex:
            main([f"--config={fncPath}", f"--data={fncPath}"])
            assert ex.value.code == 0


@pytest.mark.base
def testBaseInit_Options(monkeypatch, fncPath):
    """Test command line options for logging level."""
    monkeypatch.setattr("novelwriter.guimain.GuiMain", MockGuiMain)
    monkeypatch.setattr(sys, "argv", [
        "novelWriter.py", "--testmode", "--meminfo", f"--config={fncPath}", f"--data={fncPath}"
    ])

    # Defaults w/None Args
    nwGUI = main()
    assert nwGUI is not None
    assert logger.getEffectiveLevel() == logging.WARNING
    assert nwGUI.closeMain() == "closeMain"

    # Defaults
    nwGUI = main(
        ["--testmode", f"--config={fncPath}", f"--data={fncPath}", "--style=Fusion"]
    )
    assert nwGUI is not None
    assert logger.getEffectiveLevel() == logging.WARNING
    assert nwGUI.closeMain() == "closeMain"

    # Log Levels w/Color
    nwGUI = main(
        ["--testmode", "--info", "--color", f"--config={fncPath}", f"--data={fncPath}"]
    )
    assert nwGUI is not None
    assert logger.getEffectiveLevel() == logging.INFO
    assert nwGUI.closeMain() == "closeMain"

    nwGUI = main(
        ["--testmode", "--debug", "--color", f"--config={fncPath}", f"--data={fncPath}"]
    )
    assert nwGUI is not None
    assert logger.getEffectiveLevel() == logging.DEBUG
    assert nwGUI.closeMain() == "closeMain"

    # Log Levels wo/Color
    nwGUI = main(
        ["--testmode", "--info", f"--config={fncPath}", f"--data={fncPath}"]
    )
    assert nwGUI is not None
    assert logger.getEffectiveLevel() == logging.INFO
    assert nwGUI.closeMain() == "closeMain"

    nwGUI = main(
        ["--testmode", "--debug", f"--config={fncPath}", f"--data={fncPath}"]
    )
    assert nwGUI is not None
    assert logger.getEffectiveLevel() == logging.DEBUG
    assert nwGUI.closeMain() == "closeMain"

    # Help and Version
    with pytest.raises(SystemExit) as ex:
        nwGUI = main(
            ["--testmode", "--help", f"--config={fncPath}", f"--data={fncPath}"]
        )
    assert nwGUI is not None
    assert nwGUI.closeMain() == "closeMain"
    assert ex.value.code == 0

    with pytest.raises(SystemExit) as ex:
        nwGUI = main(
            ["--testmode", "--version", f"--config={fncPath}", f"--data={fncPath}"]
        )
    assert nwGUI is not None
    assert nwGUI.closeMain() == "closeMain"
    assert ex.value.code == 0

    # Invalid options
    with pytest.raises(SystemExit) as ex:
        nwGUI = main(
            ["--testmode", "--invalid", f"--config={fncPath}", f"--data={fncPath}"]
        )
    assert nwGUI is not None
    assert nwGUI.closeMain() == "closeMain"
    assert ex.value.code == 2

    # Project Path
    nwGUI = main(
        ["--testmode", f"--config={fncPath}", f"--data={fncPath}", "sample/"]
    )
    assert nwGUI is not None
    assert nwGUI.closeMain() == "closeMain"


@pytest.mark.base
def testBaseInit_Imports(caplog, monkeypatch, fncPath):
    """Check import error handling."""
    monkeypatch.setattr("novelwriter.guimain.GuiMain", MockGuiMain)
    monkeypatch.setattr("PyQt6.QtWidgets.QApplication.__init__", lambda *a: None)
    monkeypatch.setattr("PyQt6.QtWidgets.QApplication.exec", lambda *a: 0)
    monkeypatch.setattr("PyQt6.QtWidgets.QErrorMessage.__init__", lambda *a: None)
    monkeypatch.setattr("PyQt6.QtWidgets.QErrorMessage.resize", lambda *a: None)
    monkeypatch.setattr("PyQt6.QtWidgets.QErrorMessage.showMessage", lambda *a: None)
    monkeypatch.setattr("sys.hexversion", 0x0)
    monkeypatch.setattr("novelwriter.CONFIG.verQtValue", 0x050000)
    monkeypatch.setattr("novelwriter.CONFIG.verPyQtValue", 0x050000)

    with pytest.raises(SystemExit) as ex:
        _ = main(
            ["--testmode", f"--config={fncPath}", f"--data={fncPath}"]
        )

    assert ex.value.code & 4 == 4    # Python version not satisfied  # type: ignore
    assert ex.value.code & 8 == 8    # Qt version not satisfied  # type: ignore
    assert ex.value.code & 16 == 16  # PyQt version not satisfied  # type: ignore

    assert "At least Python" in caplog.messages[0]
    assert "At least Qt6" in caplog.messages[1]
    assert "At least PyQt6" in caplog.messages[2]
