# -*- coding: utf-8 -*-
"""novelWriter Error Tester
"""

import nw
import sys
import pytest

from PyQt5.QtWidgets import qApp

from nw.error import NWErrorMessage, exceptionHandler

@pytest.mark.error
def testErrorDialog(qtbot, nwFuncTemp, nwTemp):
    qApp.closeAllWindows()
    nwGUI = nw.main(["--testmode", "--config=%s" % nwFuncTemp, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)

    nwErr = NWErrorMessage(nwGUI)
    qtbot.addWidget(nwErr)
    nwErr.show()

    # Invalid Error
    nwErr.setMessage(Exception, "Faulty Error", 123)
    assert nwErr.msgBody.toPlainText() == "Failed to generate error report ..."

    # Valid Error
    nwErr.setMessage(Exception, "First Error", sys.last_traceback)
    theMessage = nwErr.msgBody.toPlainText()
    assert theMessage
    assert "First Error" in theMessage
    assert "Exception" in theMessage
    nwErr._doClose()
    nwErr.close()

    theMessage = exceptionHandler(Exception, "Second Error", sys.last_traceback, testMode=True)
    assert theMessage
    assert "Second Error" in theMessage
    assert "Exception" in theMessage

    nwGUI.closeMain()

    # qtbot.stopForInteraction()
