# -*- coding: utf-8 -*-
"""novelWriter Error Tester
"""

import nw
import sys
import pytest

from nwtools import getGuiItem

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import qApp, QDialogButtonBox

from nw.error import NWErrorMessage, exceptionHandler

@pytest.mark.error
def testErrorDialog(qtbot, nwFuncTemp, nwTemp):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwFuncTemp, "--data=%s" % nwTemp])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)

    nwErr = NWErrorMessage(nwGUI)
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
    del nwErr

    # Exception Handler
    def handleDialog():
        while not isinstance(nwGUI.activeDialog, NWErrorMessage):
            qApp.processEvents()

        nwErr = nwGUI.activeDialog
        theMessage = nwErr.msgBody.toPlainText()
        assert theMessage
        assert "Second Error" in theMessage
        assert "Exception" in theMessage
        btnClose = nwErr.btnBox.button(QDialogButtonBox.Close)
        qtbot.mouseClick(btnClose, Qt.LeftButton, delay=1)

    QTimer.singleShot(0, handleDialog)
    exceptionHandler(Exception, "Second Error", sys.last_traceback)

    nwGUI.closeMain()

    # qtbot.stopForInteraction()
