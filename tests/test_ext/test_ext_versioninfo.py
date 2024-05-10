"""
novelWriter – Version Info Widget Tester
========================================

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

from urllib.error import HTTPError

import pytest

from PyQt5.QtCore import QUrl

from novelwriter import SHARED
from novelwriter.constants import nwConst
from novelwriter.extensions.versioninfo import VersionInfoWidget, _Retriever, _RetrieverSignal

from tests.tools import SimpleDialog


class MockRetriever:
    signals = _RetrieverSignal()


class MockDesktopServices:

    url = None

    @staticmethod
    def openUrl(url):
        MockDesktopServices.url = url
        return


class MockData:
    def decode(self, *a):
        return '{"tag_name": "v1.0"}'


class MockPayload:

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return

    def read(self):
        data = MockData()
        return data


class MockHTTPError:

    def __enter__(self):
        raise HTTPError("http://example.com", 403, "Rate limit", None, None)  # type: ignore

    def __exit__(self, *args):
        return


class MockException:

    def __enter__(self):
        raise Exception("Oh noes!")

    def __exit__(self, *args):
        return


@pytest.mark.gui
def testExtVersionInfo_Main(qtbot, monkeypatch):
    """Test the VersionInfoWidget class."""
    version = VersionInfoWidget(None)  # type: ignore
    dialog = SimpleDialog(version)
    dialog.show()

    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.extensions.versioninfo.QDesktopServices", MockDesktopServices)
        version._processLink("#notes")
        assert MockDesktopServices.url == QUrl(nwConst.URL_RELEASES)

    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.extensions.versioninfo.QDesktopServices", MockDesktopServices)
        version._processLink("#website")
        assert MockDesktopServices.url == QUrl(nwConst.URL_WEB)

    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.extensions.versioninfo._Retriever", MockRetriever)
        mp.setattr(SHARED, "runInThreadPool", lambda *a: None)
        version._processLink("#update")
        assert version._lblRelease.text() == "Latest Version: Checking ..."

    version._updateReleaseInfo("v2.0", "")
    assert version._lblRelease.text() == (
        "Latest Version: 2.0 – Download from <a href='#website'>novelwriter.io</a>"
    )

    version._updateReleaseInfo("", "Error")
    assert version._lblRelease.text() == "Latest Version: Error"

    version._updateReleaseInfo("", "")
    assert version._lblRelease.text() == "Latest Version: Failed"

    dialog.close()
    # qtbot.stop()


@pytest.mark.gui
def testExtVersionInfo_Retriever(qtbot, monkeypatch):
    """Test the _Retriever class."""
    task = _Retriever()

    # Valid Data
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.extensions.versioninfo.urlopen", lambda *a, **k: MockPayload())
        with qtbot.waitSignal(task.signals.dataReady) as signal:
            task.run()
            assert signal.args == ["v1.0", ""]

    def httpErr():
        raise HTTPError("http://example.com", 403, "Rate limit")  # type: ignore

    # HTTP Error
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.extensions.versioninfo.urlopen", lambda *a, **k: MockHTTPError())
        with qtbot.waitSignal(task.signals.dataReady) as signal:
            task.run()
            assert signal.args == ["", "Rate limit (HTTP 403)"]

    # Other Error
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.extensions.versioninfo.urlopen", lambda *a, **k: MockException())
        with qtbot.waitSignal(task.signals.dataReady) as signal:
            task.run()
            assert signal.args == ["", "Oh noes!"]
