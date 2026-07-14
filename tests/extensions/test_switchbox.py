"""
novelWriter – SwitchBox Extension Tests
=======================================

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

import pytest

from novelwriter.extensions.switch import NSwitch
from novelwriter.extensions.switchbox import NSwitchBox

from tests.helpers import SimpleDialog


@pytest.mark.gui
def testNSwitchBox_AddAndState(qtbot, mockGUIwithTheme):
    """Test adding labels, items and separators, and reading and
    writing the resulting switch state.
    """
    dialog = SimpleDialog()
    box = NSwitchBox(dialog, 20)
    dialog.addWidget(box)
    qtbot.addWidget(dialog)

    box.addLabel("Group")
    box.addItem("Alpha", "item:alpha", icon="filter", color="default", default=True)
    box.addItem("Beta", "item:beta", default=False)
    box.addSeparator()

    assert isinstance(box._switches["item:alpha"], NSwitch)
    assert isinstance(box._switches["item:beta"], NSwitch)
    assert box._labels["item:alpha"].text() == "Alpha"
    assert "item:alpha" in box._icons
    assert "item:beta" not in box._icons

    assert box.getSwitchState() == {"item:alpha": True, "item:beta": False}

    box.setSwitchState({"item:alpha": False, "item:beta": True, "item:missing": True})
    assert box.getSwitchState() == {"item:alpha": False, "item:beta": True}

    # Toggling a switch emits the identifier and the new state
    with qtbot.waitSignal(box.switchToggled, timeout=1000) as signal:
        box._switches["item:alpha"].setChecked(True)
    assert signal.args == ["item:alpha", True]

    # Updating the theme refreshes the icon pixmaps of items that have one
    box.updateTheme()


@pytest.mark.gui
def testNSwitchBox_UpdateInPlace(qtbot, mockGUIwithTheme):
    """Test that re-adding an existing identifier updates the entry in
    place rather than appending a duplicate, and keeps the current
    switch state instead of resetting it to the new default.
    """
    dialog = SimpleDialog()
    box = NSwitchBox(dialog, 20)
    dialog.addWidget(box)
    qtbot.addWidget(dialog)

    box.addItem("Original Name", "item:root", icon="filter", color="default", default=True)
    box.addItem("Other", "item:other", default=False)
    assert len(box._switches) == 2
    originalSwitch = box._switches["item:root"]

    # The user has since toggled the switch off
    originalSwitch.setChecked(False)

    # Re-adding the same identifier must not create a new row or switch,
    # must update the label text, and must not reset the switch state
    # even though a new default is provided
    box.addItem("Renamed", "item:root", icon="filter", color="suffix", default=True)
    assert len(box._switches) == 2
    assert box._switches["item:root"] is originalSwitch
    assert box._labels["item:root"].text() == "Renamed"
    assert originalSwitch.isChecked() is False

    # The same applies to an item that has no icon, where the icon branch
    # of the in-place update must simply be skipped
    otherSwitch = box._switches["item:other"]
    box.addItem("Other Renamed", "item:other", default=True)
    assert box._switches["item:other"] is otherSwitch
    assert box._labels["item:other"].text() == "Other Renamed"
    assert otherSwitch.isChecked() is False
    assert "item:other" not in box._icons


@pytest.mark.gui
def testNSwitchBox_RemoveItem(qtbot, mockGUIwithTheme):
    """Test removing items from the switch box, including items that
    were never added and items without an icon.
    """
    dialog = SimpleDialog()
    box = NSwitchBox(dialog, 20)
    dialog.addWidget(box)
    qtbot.addWidget(dialog)

    box.addItem("Alpha", "item:alpha", icon="filter", color="default", default=True)
    box.addItem("Beta", "item:beta", default=False)
    assert set(box._switches) == {"item:alpha", "item:beta"}

    # Removing an item drops it from every internal tracking dict
    box.removeItem("item:alpha")
    assert "item:alpha" not in box._switches
    assert "item:alpha" not in box._labels
    assert "item:alpha" not in box._pixmaps
    assert "item:alpha" not in box._icons
    assert box.getSwitchState() == {"item:beta": False}

    # Removing an item without an icon works the same way
    box.removeItem("item:beta")
    assert box.getSwitchState() == {}

    # Removing an identifier that was never added, or already removed,
    # is a no-op
    box.removeItem("item:alpha")
    box.removeItem("item:unknown")
    assert box.getSwitchState() == {}

    # The identifier can be reused afterwards, appending a fresh row
    box.addItem("Alpha Again", "item:alpha", icon="filter", color="default", default=True)
    assert box.getSwitchState() == {"item:alpha": True}


@pytest.mark.gui
def testNSwitchBox_Clear(qtbot, mockGUIwithTheme):
    """Test that clear() resets all internal tracking dicts, and that
    the widget remains usable afterwards.
    """
    dialog = SimpleDialog()
    box = NSwitchBox(dialog, 20)
    dialog.addWidget(box)
    qtbot.addWidget(dialog)

    box.addLabel("Group")
    box.addItem("Alpha", "item:alpha", icon="filter", color="default", default=True)
    assert box.getSwitchState() != {}

    box.clear()
    assert box._switches == {}
    assert box._labels == {}
    assert box._pixmaps == {}
    assert box._icons == {}
    assert box.getSwitchState() == {}

    box.addItem("Beta", "item:beta", default=True)
    assert box.getSwitchState() == {"item:beta": True}
