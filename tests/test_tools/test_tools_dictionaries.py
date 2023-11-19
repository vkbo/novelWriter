"""
novelWriter – Dictionary Downloader Tester
==========================================

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

import json
import pytest
import enchant

from pathlib import Path
from urllib.request import Request

from tools import getGuiItem
from mocked import causeException, causeOSError

from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QAction, QTreeWidgetItem

from novelwriter import SHARED
from novelwriter.tools import dictionaries
from novelwriter.tools.dictionaries import GuiDictionaries


class MockPayload:

    def __init__(self):
        self.request = ""
        self.response = b""
        return

    def read(self) -> bytes:
        return self.response


PAYLOAD = MockPayload()


def mockUrlopen(req: Request, timeout: int = 0) -> MockPayload:
    return PAYLOAD


@pytest.mark.gui
def testToolDictionaries_Main(qtbot, monkeypatch, nwGUI, fncPath):
    """Test the Dictionaries downloader tool."""
    monkeypatch.setattr(enchant, "get_user_config_dir", lambda *a: str(fncPath))
    monkeypatch.setattr(dictionaries, "urlopen", mockUrlopen)

    # Open the tool
    nwGUI.mainMenu.aNewDicts.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiDictionaries") is not None, timeout=1000)

    nwDicts = getGuiItem("GuiDictionaries")
    assert isinstance(nwDicts, GuiDictionaries)
    assert nwDicts.isVisible()
    assert nwDicts.pathBox.text() == str(fncPath)

    # Fail Re-Init
    with monkeypatch.context() as mp:
        mp.setattr(enchant, "get_user_config_dir", lambda *a: causeException)
        assert nwDicts.initDialog() is False

    # Allow Open Dir
    with monkeypatch.context() as mp:
        mp.setattr(QDesktopServices, "openUrl", lambda *a: None)
        nwDicts._openLocation()
        assert SHARED.alert is None

    # Fail Open Dir
    nwDicts.pathBox.setText("/foo/bar")
    nwDicts._openLocation()
    assert SHARED.alert is not None
    assert SHARED.alert.logMessage == "Path not found."
    nwDicts.pathBox.setText(str(fncPath))

    # Create Mock Dicts
    (fncPath / "hunspell").mkdir()
    (fncPath / "hunspell" / "en_US.aff").touch()
    (fncPath / "hunspell" / "en_US.dic").touch()
    nwDicts.initDialog()

    # List Dictionaries
    # =================
    PAYLOAD.response = json.dumps([{
        "name": "README.md",
        "type": "file",
    }, {
        "name": "en_GB",
        "type": "dir",
    }, {
        "name": "en_US",
        "type": "dir",
    }]).encode()

    nwDicts._loadDictionaries()
    assert nwDicts.listBox.topLevelItemCount() == 2

    item = nwDicts.listBox.topLevelItem(0)
    assert isinstance(item, QTreeWidgetItem)
    assert item.text(nwDicts.C_CODE) == "en_GB"
    assert item.text(nwDicts.C_NAME) == "English"
    assert item.text(nwDicts.C_STATE) == ""

    item = nwDicts.listBox.topLevelItem(1)
    assert isinstance(item, QTreeWidgetItem)
    assert item.text(nwDicts.C_CODE) == "en_US"
    assert item.text(nwDicts.C_NAME) == "English"
    assert item.text(nwDicts.C_STATE) == "Downloaded"

    # Download Dictionary
    # ===================
    PAYLOAD.response = json.dumps([{
        "name": "en_GB.aff",
        "type": "file",
        "download_url": "foo/bar",
    }, {
        "name": "en_GB.dic",
        "type": "file",
        "download_url": "foo/bar",
    }, {
        "name": "README.txt",
        "type": "file",
        "download_url": "foo/bar",
    }, {
        "name": "META-INF",
        "type": "dir",
        "download_url": None,
    }]).encode()

    # No Selection
    nwDicts.listBox.clearSelection()
    nwDicts._downloadDictionary()
    item = nwDicts.listBox.topLevelItem(0)
    assert isinstance(item, QTreeWidgetItem)
    assert item.text(nwDicts.C_CODE) == "en_GB"
    assert item.text(nwDicts.C_NAME) == "English"
    assert item.text(nwDicts.C_STATE) == ""

    # Select en_GB, fail mkdir
    with monkeypatch.context() as mp:
        mp.setattr(Path, "mkdir", causeOSError)
        item = nwDicts.listBox.topLevelItem(0)
        assert isinstance(item, QTreeWidgetItem)
        item.setSelected(True)
        nwDicts._downloadDictionary()
        assert item.text(nwDicts.C_CODE) == "en_GB"
        assert item.text(nwDicts.C_NAME) == "English"
        assert item.text(nwDicts.C_STATE) == ""

    # Succeed the download, but fail files check
    with monkeypatch.context() as mp:
        mp.setattr(nwDicts, "_downloadFile", lambda *a: True)
        item = nwDicts.listBox.topLevelItem(0)
        assert isinstance(item, QTreeWidgetItem)
        item.setSelected(True)
        nwDicts._downloadDictionary()
        assert item.text(nwDicts.C_CODE) == "en_GB"
        assert item.text(nwDicts.C_NAME) == "English"
        assert item.text(nwDicts.C_STATE) == "Failed"

    # Create the files and try again
    (fncPath / "hunspell" / "en_GB.aff").touch()
    (fncPath / "hunspell" / "en_GB.dic").touch()
    with monkeypatch.context() as mp:
        mp.setattr(nwDicts, "_downloadFile", lambda *a: True)
        item = nwDicts.listBox.topLevelItem(0)
        assert isinstance(item, QTreeWidgetItem)
        item.setSelected(True)
        nwDicts._downloadDictionary()
        assert item.text(nwDicts.C_CODE) == "en_GB"
        assert item.text(nwDicts.C_NAME) == "English"
        assert item.text(nwDicts.C_STATE) == "Downloaded"

    # Delete Dictionary
    # =================

    # No Selection
    nwDicts.listBox.clearSelection()
    nwDicts._deleteDictionary()
    item = nwDicts.listBox.topLevelItem(0)
    assert isinstance(item, QTreeWidgetItem)
    assert item.text(nwDicts.C_CODE) == "en_GB"
    assert item.text(nwDicts.C_NAME) == "English"
    assert item.text(nwDicts.C_STATE) == "Downloaded"
    assert (fncPath / "hunspell" / "en_GB.aff").is_file()
    assert (fncPath / "hunspell" / "en_GB.dic").is_file()

    # Fail the delete
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.unlink", causeOSError)
        item = nwDicts.listBox.topLevelItem(0)
        assert isinstance(item, QTreeWidgetItem)
        item.setSelected(True)
        nwDicts._deleteDictionary()
        assert item.text(nwDicts.C_CODE) == "en_GB"
        assert item.text(nwDicts.C_NAME) == "English"
        assert item.text(nwDicts.C_STATE) == "Downloaded"
        assert (fncPath / "hunspell" / "en_GB.aff").is_file()
        assert (fncPath / "hunspell" / "en_GB.dic").is_file()

    # Succeed delete
    item = nwDicts.listBox.topLevelItem(0)
    assert isinstance(item, QTreeWidgetItem)
    item.setSelected(True)
    nwDicts._deleteDictionary()
    assert item.text(nwDicts.C_CODE) == "en_GB"
    assert item.text(nwDicts.C_NAME) == "English"
    assert item.text(nwDicts.C_STATE) == ""
    assert not (fncPath / "hunspell" / "en_GB.aff").is_file()
    assert not (fncPath / "hunspell" / "en_GB.dic").is_file()

    # API Functions
    # =============

    # API Call
    PAYLOAD.response = b"foobar"
    assert nwDicts._callGitHubAPI("") == {}
    PAYLOAD.response = b"{\"foo\": \"bar\"}"
    assert nwDicts._callGitHubAPI("") == {"foo": "bar"}

    # Download File
    fooBar = fncPath / "foobar.txt"
    PAYLOAD.response = None  # type: ignore
    assert nwDicts._downloadFile("file:///foo/bar", fooBar) is False
    assert fooBar.read_bytes() == b""
    PAYLOAD.response = b"foobar"
    assert nwDicts._downloadFile("file:///foo/bar", fooBar) is True
    assert fooBar.read_bytes() == b"foobar"

    # Close
    nwDicts._doClose()
    # qtbot.stop()

# END Test testToolDictionaries_Main
