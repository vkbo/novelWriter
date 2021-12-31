"""
novelWriter – Error Handler Tester
==================================

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

from PyQt5.QtWidgets import QMessageBox, qApp

from mock import causeException

from novelwriter.error import NWErrorMessage, exceptionHandler


@pytest.mark.base
def testBaseError_Dialog(qtbot, monkeypatch, fncDir, tmpDir):
    """Test the error dialog.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: QMessageBox.Yes)

    qApp.closeAllWindows()
    nwGUI = novelwriter.main(["--testmode", "--config=%s" % fncDir, "--data=%s" % tmpDir])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.wait(20)

    nwErr = NWErrorMessage(nwGUI)
    qtbot.addWidget(nwErr)
    nwErr.show()

    # Invalid Error Message
    nwErr.setMessage(Exception, "Faulty Error", 123)
    assert nwErr.msgBody.toPlainText() == "Failed to generate error report ..."

    # Valid Error Message
    with monkeypatch.context() as mp:
        mp.setattr("PyQt5.QtCore.QSysInfo.kernelVersion", lambda: "1.2.3")
        nwErr.setMessage(Exception, "Fine Error", None)
        theMessage = nwErr.msgBody.toPlainText()
        assert theMessage != ""
        assert "Fine Error" in theMessage
        assert "Exception" in theMessage
        assert "(1.2.3)" in theMessage

    # No kernel version retrieved
    with monkeypatch.context() as mp:
        mp.setattr("PyQt5.QtCore.QSysInfo.kernelVersion", causeException)
        nwErr.setMessage(Exception, "Almost Fine Error", None)
        theMessage = nwErr.msgBody.toPlainText()
        assert theMessage != ""
        assert "(Unknown)" in theMessage

    nwErr._doClose()
    nwErr.close()
    nwGUI.closeMain()

# END Test testBaseError_Dialog


@pytest.mark.base
def testBaseError_Handler(qtbot, monkeypatch, fncDir, tmpDir):
    """Test the error handler. This test doesn'thave any asserts, but it
    checks that the error handler handles potential exceptions. The test
    will fail if excpetions are not handled.
    """
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: QMessageBox.Yes)

    qApp.closeAllWindows()
    nwGUI = novelwriter.main(["--testmode", "--config=%s" % fncDir, "--data=%s" % tmpDir])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.wait(20)

    # Normal shutdown
    with monkeypatch.context() as mp:
        mp.setattr(NWErrorMessage, "exec_", lambda *a: None)
        mp.setattr("PyQt5.QtWidgets.qApp.exit", lambda *a: None)
        exceptionHandler(Exception, "Error Message", None)

    # Should not crash when no GUI is found
    with monkeypatch.context() as mp:
        mp.setattr(NWErrorMessage, "exec_", lambda *a: None)
        mp.setattr("PyQt5.QtWidgets.qApp.exit", lambda *a: None)
        mp.setattr("PyQt5.QtWidgets.qApp.topLevelWidgets", lambda: [])
        exceptionHandler(Exception, "Error Message", None)

    # Should handle qApp failing
    with monkeypatch.context() as mp:
        mp.setattr(NWErrorMessage, "exec_", lambda *a: None)
        mp.setattr("PyQt5.QtWidgets.qApp.exit", lambda *a: None)
        mp.setattr("PyQt5.QtWidgets.qApp.topLevelWidgets", causeException)
        exceptionHandler(Exception, "Error Message", None)

    # Should handle failing to close main GUI
    with monkeypatch.context() as mp:
        mp.setattr(NWErrorMessage, "exec_", lambda *a: None)
        mp.setattr("PyQt5.QtWidgets.qApp.exit", lambda *a: None)
        mp.setattr(nwGUI, "closeMain", causeException)
        exceptionHandler(Exception, "Error Message", None)

    nwGUI.closeMain()

# END Test testBaseError_Handler
