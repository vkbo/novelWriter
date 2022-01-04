"""
novelWriter – Main Init Tester
==============================

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
import pytest
import logging
import novelwriter

from mock import MockGuiMain


@pytest.mark.base
def testBaseInit_Launch(caplog, monkeypatch, tmpDir):
    """Check launching the main GUI.
    """
    monkeypatch.setattr("novelwriter.guimain.GuiMain", MockGuiMain)

    # TestMode Launch
    nwGUI = novelwriter.main(["--testmode", "--config=%s" % tmpDir, "--data=%s" % tmpDir])
    assert isinstance(nwGUI, MockGuiMain)

    # Darwin Launch
    caplog.clear()
    osDarwin = novelwriter.CONFIG.osDarwin
    novelwriter.CONFIG.osDarwin = True
    with monkeypatch.context() as mp:
        mp.setitem(sys.modules, "Foundation", None)
        nwGUI = novelwriter.main(["--testmode", "--config=%s" % tmpDir, "--data=%s" % tmpDir])
        assert isinstance(nwGUI, MockGuiMain)
        assert "Failed" in caplog.text

    novelwriter.CONFIG.osDarwin = osDarwin

    # Windows Launch
    caplog.clear()
    osWindows = novelwriter.CONFIG.osWindows
    novelwriter.CONFIG.osWindows = True
    with monkeypatch.context() as mp:
        mp.setitem(sys.modules, "ctypes", None)
        nwGUI = novelwriter.main(["--testmode", "--config=%s" % tmpDir, "--data=%s" % tmpDir])
        assert isinstance(nwGUI, MockGuiMain)
        if not sys.platform.startswith("darwin"):
            # For some reason, the test doesn't work on macOS
            assert "Failed" in caplog.text

    novelwriter.CONFIG.osWindows = osWindows

    # Normal Launch
    monkeypatch.setattr("PyQt5.QtWidgets.QApplication.__init__", lambda *a: None)
    monkeypatch.setattr("PyQt5.QtWidgets.QApplication.setApplicationName", lambda *a: None)
    monkeypatch.setattr("PyQt5.QtWidgets.QApplication.setApplicationVersion", lambda *a: None)
    monkeypatch.setattr("PyQt5.QtWidgets.QApplication.setWindowIcon", lambda *a: None)
    monkeypatch.setattr("PyQt5.QtWidgets.QApplication.setOrganizationDomain", lambda *a: None)
    monkeypatch.setattr("PyQt5.QtWidgets.QApplication.exec_", lambda *a: 0)
    with pytest.raises(SystemExit) as ex:
        novelwriter.main(["--config=%s" % tmpDir, "--data=%s" % tmpDir])
        assert ex.value.code == 0

# END Test testBaseInit_Launch


@pytest.mark.base
def testBaseInit_Options(monkeypatch, tmpDir):
    """Test command line options for logging level.
    """
    monkeypatch.setattr("novelwriter.guimain.GuiMain", MockGuiMain)
    monkeypatch.setattr(sys, "argv", [
        "novelWriter.py", "--testmode", "--config=%s" % tmpDir, "--data=%s" % tmpDir
    ])

    # Defaults w/None Args
    nwGUI = novelwriter.main()
    assert novelwriter.logger.getEffectiveLevel() == logging.WARNING
    assert nwGUI.closeMain() == "closeMain"

    # Defaults
    nwGUI = novelwriter.main(
        ["--testmode", "--config=%s" % tmpDir, "--data=%s" % tmpDir, "--style=Fusion"]
    )
    assert novelwriter.logger.getEffectiveLevel() == logging.WARNING
    assert nwGUI.closeMain() == "closeMain"

    # Log Levels
    nwGUI = novelwriter.main(
        ["--testmode", "--info", "--config=%s" % tmpDir, "--data=%s" % tmpDir]
    )
    assert novelwriter.logger.getEffectiveLevel() == logging.INFO
    assert nwGUI.closeMain() == "closeMain"

    nwGUI = novelwriter.main(
        ["--testmode", "--debug", "--config=%s" % tmpDir, "--data=%s" % tmpDir]
    )
    assert novelwriter.logger.getEffectiveLevel() == logging.DEBUG
    assert nwGUI.closeMain() == "closeMain"

    nwGUI = novelwriter.main(
        ["--testmode", "--verbose", "--config=%s" % tmpDir, "--data=%s" % tmpDir]
    )
    assert novelwriter.logger.getEffectiveLevel() == 5
    assert nwGUI.closeMain() == "closeMain"

    # Help and Version
    with pytest.raises(SystemExit) as ex:
        nwGUI = novelwriter.main(
            ["--testmode", "--help", "--config=%s" % tmpDir, "--data=%s" % tmpDir]
        )
    assert nwGUI.closeMain() == "closeMain"
    assert ex.value.code == 0

    with pytest.raises(SystemExit) as ex:
        nwGUI = novelwriter.main(
            ["--testmode", "--version", "--config=%s" % tmpDir, "--data=%s" % tmpDir]
        )
    assert nwGUI.closeMain() == "closeMain"
    assert ex.value.code == 0

    # Invalid options
    with pytest.raises(SystemExit) as ex:
        nwGUI = novelwriter.main(
            ["--testmode", "--invalid", "--config=%s" % tmpDir, "--data=%s" % tmpDir]
        )
    assert nwGUI.closeMain() == "closeMain"
    assert ex.value.code == 2

    # Project Path
    nwGUI = novelwriter.main(
        ["--testmode", "--config=%s" % tmpDir, "--data=%s" % tmpDir, "sample/"]
    )
    assert novelwriter.CONFIG.cmdOpen == "sample/"
    assert nwGUI.closeMain() == "closeMain"

# END Test testBaseInit_Options


@pytest.mark.base
def testBaseInit_Imports(caplog, monkeypatch, tmpDir):
    """Check import error handling.
    """
    monkeypatch.setattr("novelwriter.guimain.GuiMain", MockGuiMain)
    monkeypatch.setattr("PyQt5.QtWidgets.QApplication.__init__", lambda *a: None)
    monkeypatch.setattr("PyQt5.QtWidgets.QApplication.exec_", lambda *a: 0)
    monkeypatch.setattr("PyQt5.QtWidgets.QErrorMessage.__init__", lambda *a: None)
    monkeypatch.setattr("PyQt5.QtWidgets.QErrorMessage.resize", lambda *a: None)
    monkeypatch.setattr("PyQt5.QtWidgets.QErrorMessage.showMessage", lambda *a: None)
    monkeypatch.setitem(sys.modules, "lxml", None)
    monkeypatch.setattr("sys.hexversion", 0x0)
    monkeypatch.setattr("novelwriter.CONFIG.verQtValue", 50000)
    monkeypatch.setattr("novelwriter.CONFIG.verPyQtValue", 50000)

    with pytest.raises(SystemExit) as ex:
        _ = novelwriter.main(
            ["--testmode", "--config=%s" % tmpDir, "--data=%s" % tmpDir]
        )

    assert ex.value.code & 4 == 4    # Python version not satisfied
    assert ex.value.code & 8 == 8    # Qt version not satisfied
    assert ex.value.code & 16 == 16  # PyQt version not satisfied
    assert ex.value.code & 32 == 32  # lxml package missing

    assert "At least Python" in caplog.messages[0]
    assert "At least Qt5" in caplog.messages[1]
    assert "At least PyQt5" in caplog.messages[2]
    assert "lxml" in caplog.messages[3]

# END Test testBaseInit_Imports
