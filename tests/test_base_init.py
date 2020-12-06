# -*- coding: utf-8 -*-
"""novelWriter Main Init Tester
"""

import nw
import pytest
import logging
import sys

@pytest.mark.base
def testBaseInit_Launch(qtbot, monkeypatch, fncDir, tmpDir):
    """Test the main __init__.py file.
    """
    # Defaults
    nwGUI = nw.main(
        ["--testmode", "--config=%s" % fncDir, "--data=%s" % tmpDir, "--style=Fusion"]
    )
    assert nw.logger.getEffectiveLevel() == logging.WARNING
    nwGUI.closeMain()
    nwGUI.close()

    # Log Levels
    nwGUI = nw.main(
        ["--testmode", "--info", "--config=%s" % fncDir, "--data=%s" % tmpDir]
    )
    assert nw.logger.getEffectiveLevel() == logging.INFO
    nwGUI.closeMain()
    nwGUI.close()

    nwGUI = nw.main(
        ["--testmode", "--debug", "--config=%s" % fncDir, "--data=%s" % tmpDir]
    )
    assert nw.logger.getEffectiveLevel() == logging.DEBUG
    nwGUI.closeMain()
    nwGUI.close()

    nwGUI = nw.main(
        ["--testmode", "--verbose", "--config=%s" % fncDir, "--data=%s" % tmpDir]
    )
    assert nw.logger.getEffectiveLevel() == 5
    nwGUI.closeMain()
    nwGUI.close()

    # Help and Version
    with pytest.raises(SystemExit) as ex:
        nwGUI = nw.main(
            ["--testmode", "--help", "--config=%s" % fncDir, "--data=%s" % tmpDir]
        )
    nwGUI.closeMain()
    nwGUI.close()
    assert ex.value.code == 0

    with pytest.raises(SystemExit) as ex:
        nwGUI = nw.main(
            ["--testmode", "--version", "--config=%s" % fncDir, "--data=%s" % tmpDir]
        )
    nwGUI.closeMain()
    nwGUI.close()
    assert ex.value.code == 0

    # Invalid options
    with pytest.raises(SystemExit) as ex:
        nwGUI = nw.main(
            ["--testmode", "--invalid", "--config=%s" % fncDir, "--data=%s" % tmpDir]
        )
    nwGUI.closeMain()
    nwGUI.close()
    assert ex.value.code == 2

    # Simulate import error
    monkeypatch.setitem(sys.modules, "lxml", None)
    monkeypatch.setattr("sys.hexversion", 0x0)
    monkeypatch.setattr("nw.CONFIG.verQtValue", 50000)
    monkeypatch.setattr("nw.CONFIG.verPyQtValue", 50000)
    with pytest.raises(SystemExit) as ex:
        nwGUI = nw.main(
            ["--testmode", "--config=%s" % fncDir, "--data=%s" % tmpDir]
        )
    nwGUI.closeMain()
    nwGUI.close()
    assert ex.value.code & 4 == 4   # Python version not satisfied
    assert ex.value.code & 8 == 8   # Qt version not satisfied
    assert ex.value.code & 16 == 16 # PyQt version not satisfied
    assert ex.value.code & 32 == 32 # lxml package missing
    monkeypatch.undo()

# END Test testBaseInit_Launch
