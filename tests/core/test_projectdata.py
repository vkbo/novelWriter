"""
novelWriter – Project Data Tests
================================

This file is a part of novelWriter
Copyright (C) 2026 Veronica Berglyd Olsen and novelWriter contributors

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
"""  # noqa

from __future__ import annotations

from datetime import date

import pytest

from novelwriter.core import projectdata
from novelwriter.core.projectdata import ProjectData


class MockProject:
    """Fake project object that just counts change notifications."""

    def __init__(self) -> None:
        self.changed = 0

    def setProjectChanged(self, state: bool) -> None:
        """Fake project method."""
        self.changed += 1 if state else 0


class _FakeDate(date):
    """A date subclass where 'today' can be pinned by a test so that
    the clock transition to a new day can be simulated.
    """

    _today = date(2026, 7, 20)

    @classmethod
    def today(cls) -> date:
        """Return the pinned 'today' value."""
        return cls._today


@pytest.mark.core
def testProjectData_Uuid(mockGUI):
    """Test the setUuid setter."""
    project = MockProject()
    data = ProjectData(project)  # type: ignore

    # An empty/invalid value generates a new uuid
    data.setUuid("not-a-uuid")
    assert data.uuid != ""
    firstUuid = data.uuid

    # Setting the same uuid again does nothing
    project.changed = 0
    data.setUuid(firstUuid)
    assert data.uuid == firstUuid
    assert project.changed == 0

    # Setting a new, valid uuid updates it and flags the change
    data.setUuid("d0f3fe10-c6e6-4310-8bfd-181eb4224eed")
    assert data.uuid == "d0f3fe10-c6e6-4310-8bfd-181eb4224eed"
    assert project.changed == 1


@pytest.mark.core
def testProjectData_Language(mockGUI):
    """Test the setLanguage setter."""
    project = MockProject()
    data = ProjectData(project)  # type: ignore

    data.setLanguage("en_GB")
    assert data.language == "en_GB"

    # Setting the same language again does nothing
    project.changed = 0
    data.setLanguage("en_GB")
    assert data.language == "en_GB"
    assert project.changed == 0


@pytest.mark.core
def testProjectData_LastHandle(mockGUI):
    """Test the setLastHandle and setLastHandles setters."""
    project = MockProject()
    data = ProjectData(project)  # type: ignore

    # Setting with a non-string component does nothing
    project.changed = 0
    data.setLastHandle("0123456789abc", None)  # type: ignore
    assert project.changed == 0

    # Setting with a valid component works
    data.setLastHandle("0123456789abc", "editor")
    assert data.getLastHandle("editor") == "0123456789abc"

    # setLastHandles requires a dict
    project.changed = 0
    data.setLastHandles(["not", "a", "dict"])  # type: ignore
    assert project.changed == 0

    # Unknown keys in the dict are skipped, known keys are updated
    data.setLastHandles({"unknownKey": "0123456789abc", "editor": "0123456789abd"})
    assert data.getLastHandle("editor") == "0123456789abd"


@pytest.mark.core
def testProjectData_CurrCounts(mockGUI):
    """Test the setCurrCounts setter."""
    project = MockProject()
    data = ProjectData(project)  # type: ignore

    data.setCurrCounts(1, 2, 3, 4)
    assert data.currCounts == (1, 2, 3, 4)

    # Only the given values are updated, others are left as-is
    data.setCurrCounts(wNovel=None, wNotes=None, cNovel=9, cNotes=None)
    assert data.currCounts == (1, 2, 9, 4)


@pytest.mark.core
def testProjectData_AutoReplace(mockGUI):
    """Test the setAutoReplace setter."""
    project = MockProject()
    data = ProjectData(project)  # type: ignore

    # Requires a dict
    project.changed = 0
    data.setAutoReplace(["not", "a", "dict"])  # type: ignore
    assert project.changed == 0
    assert data.autoReplace == {}

    # Non-string entries are skipped
    data.setAutoReplace({"A": "B", "C": 123})  # type: ignore
    assert data.autoReplace == {"A": "B"}


@pytest.mark.core
def testProjectData_DailyProgress(monkeypatch, mockGUI):
    """Test the setDailyProgress setter. The daily progress and the
    remaining project word count must survive across sessions on the
    same day, and must be recalculated when the clock ticks over to a
    new day.
    """
    monkeypatch.setattr(projectdata, "date", _FakeDate)

    project = MockProject()
    data = ProjectData(project)  # type: ignore
    data.setProjectTarget(1000, None)
    data.setInitCounts(wNovel=500)

    # First update of a session with no prior daily record: the progress
    # is measured from the initial count, and the remaining word count is
    # the full target less what already existed at the start of the day
    data.setDailyProgress(500)
    assert data.dailyProgress == 0
    assert data._remainingWordCount == 500

    # As the session progresses, the progress grows, but the remaining
    # count for the day stays fixed at the start-of-day value
    data.setDailyProgress(560)
    assert data.dailyProgress == 60
    assert data._remainingWordCount == 500

    # A new session is opened later the same day. The project file was
    # saved with the 60 words from the previous session already included
    # in the initial count, and the daily record ("last") carries the
    # 60-word progress forward
    data = ProjectData(project)  # type: ignore
    data.setProjectTarget(1000, None)
    data.setInitCounts(wNovel=560)
    data.setDailyTargetCurrent(60, "2026-07-20")

    # No new typing yet, so progress should still read 60, and the
    # remaining count must match the earlier session, not be reduced by
    # the 60 words a second time
    data.setDailyProgress(560)
    assert data.dailyProgress == 60
    assert data._remainingWordCount == 500

    # More words are added in the second session
    data.setDailyProgress(600)
    assert data.dailyProgress == 100
    assert data._remainingWordCount == 500

    # The clock ticks over to the next day mid-session. Progress resets
    # for the new day, and the remaining count drops by the full amount
    # written the previous day (100 words)
    _FakeDate._today = date(2026, 7, 21)
    data.setDailyProgress(605)
    assert data.dailyProgress == 5
    assert data._remainingWordCount == 400
    assert data._dailyLastDate == date(2026, 7, 21)

    # Further typing on the new day accumulates from the new baseline
    data.setDailyProgress(615)
    assert data.dailyProgress == 15
    assert data._remainingWordCount == 400


@pytest.mark.core
def testProjectData_EffectiveDailyGoal(monkeypatch, mockGUI):
    """Test the getEffectiveDailyGoal getter. It must return the fixed
    daily goal unless automatic calculation is enabled, a deadline is
    set in the future, and there is a positive word count remaining.
    """
    monkeypatch.setattr(projectdata, "date", _FakeDate)
    _FakeDate._today = date(2026, 7, 20)

    project = MockProject()
    data = ProjectData(project)  # type: ignore
    data.setProjectTarget(1000, date(2026, 7, 24))
    data.setInitCounts(wNovel=400)
    data.setDailyProgress(400)
    assert data._remainingWordCount == 600

    # With automatic calculation off, the fixed goal is always returned
    data.setDailyTarget(50, False)
    assert data.getEffectiveDailyGoal() == 50

    # With automatic calculation on and four full days plus today left
    # until the deadline, the remaining count is spread across all of them
    data.setDailyTarget(50, True)
    assert data.getEffectiveDailyGoal() == 600 // 5

    # When the deadline is today, all the remaining words are due today
    data.setProjectTarget(1000, date(2026, 7, 20))
    data.setDailyProgress(400)
    assert data.getEffectiveDailyGoal() == 600

    # When the deadline has passed, fall back to the fixed daily goal
    data.setProjectTarget(1000, date(2026, 7, 19))
    data.setDailyProgress(400)
    assert data.getEffectiveDailyGoal() == 50

    # When the remaining word count isn't positive, also fall back
    data.setProjectTarget(400, date(2026, 7, 24))
    data.setDailyProgress(400)
    assert data._remainingWordCount == 0
    assert data.getEffectiveDailyGoal() == 50
