# -*- coding: utf-8 -*-
"""novelWriter Error Tester
"""

import nw
import pytest

from PyQt5.QtWidgets import qApp

from dummy import causeException

from nw.error import NWErrorMessage, exceptionHandler

@pytest.mark.base
def testBaseError_Dialog(qtbot, monkeypatch, fncDir, tmpDir):
    qApp.closeAllWindows()
    nwGUI = nw.main(["--testmode", "--config=%s" % fncDir, "--data=%s" % tmpDir])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)

    nwErr = NWErrorMessage(nwGUI)
    qtbot.addWidget(nwErr)
    nwErr.show()

    # Invalid Error Message
    nwErr.setMessage(Exception, "Faulty Error", 123)
    assert nwErr.msgBody.toPlainText() == "Failed to generate error report ..."

    # Valid Error Message
    nwErr.setMessage(Exception, "First Error", None)
    theMessage = nwErr.msgBody.toPlainText()
    assert theMessage
    assert "First Error" in theMessage
    assert "Exception" in theMessage
    nwErr._doClose()
    nwErr.close()

    # Valid Error
    monkeypatch.setattr("PyQt5.QtCore.QSysInfo.kernelVersion", lambda: "1.2.3")
    theMessage = exceptionHandler(Exception, "Second Error", None, testMode=True)
    assert theMessage
    assert "Second Error" in theMessage
    assert "Exception" in theMessage
    assert "(1.2.3)" in theMessage
    monkeypatch.undo()

    # No kernel version retrieved
    monkeypatch.setattr("PyQt5.QtCore.QSysInfo.kernelVersion", causeException)
    theMessage = exceptionHandler(Exception, "Third Error", None, testMode=True)
    assert theMessage
    assert "Third Error" in theMessage
    assert "Exception" in theMessage
    assert "(Unknown)" in theMessage
    monkeypatch.undo()

    # Normal shutdown, but not testmode
    monkeypatch.setattr("PyQt5.QtWidgets.qApp.exit", lambda x: None)
    nwGUI.mainConf.showGUI = True
    exceptionHandler(Exception, "Third Error", None, testMode=False)
    nwGUI.mainConf.showGUI = False
    monkeypatch.undo()

    # Disable blocking of GUI
    monkeypatch.setattr("PyQt5.QtWidgets.QDialog.exec_", lambda: None)
    exceptionHandler(Exception, "Third Error", None, testMode=True)
    monkeypatch.undo()

    # Should handle qApp failing
    monkeypatch.setattr("PyQt5.QtWidgets.qApp.topLevelWidgets", causeException)
    exceptionHandler(Exception, "Third Error", None, testMode=True)
    monkeypatch.undo()

    # Should handle failing to close main GUI
    monkeypatch.setattr(nwGUI, "closeMain", causeException)
    exceptionHandler(Exception, "Third Error", None, testMode=True)
    monkeypatch.undo()

    # Should not crash when no GUI is found
    nwGUI.setObjectName("Stuff")
    assert exceptionHandler(Exception, "Third Error", None, testMode=True) is None

    nwGUI.closeMain()

    # qtbot.stopForInteraction()

# END Test testBaseError_Dialog
