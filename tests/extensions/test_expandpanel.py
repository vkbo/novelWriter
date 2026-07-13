"""
novelWriter – ExpandPanel Extension Tests
=========================================

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

from PyQt6.QtWidgets import QLabel, QVBoxLayout

from novelwriter.extensions.expandpanel import NExpandablePanel
from novelwriter.types import QtMouseLeft

from tests.helpers import SimpleDialog


@pytest.mark.gui
def testNExpandablePanel_Main(qtbot, mockGUI):
    """Test the NExpandablePanel class."""
    dialog = SimpleDialog()
    panel = NExpandablePanel(dialog)
    dialog.addWidget(panel)
    dialog.show()
    qtbot.addWidget(dialog)

    changes = []
    panel.expandedStateChanged.connect(changes.append)

    # Default state is expanded, with a default title
    assert panel.isExpanded() is True
    assert panel._ep_widget.isVisible() is True
    assert panel._ep_toggle.isChecked() is True
    assert panel._ep_label.text() == "Unnamed"

    # Set a title
    panel.setTitle("My Panel")
    assert panel._ep_label.text() == "My Panel"

    # Set the content layout
    content = QVBoxLayout()
    content.addWidget(QLabel("Some content", panel))
    panel.setContentLayout(content)
    assert panel._ep_widget.layout() is content

    # Click the toggle button to collapse the panel
    qtbot.mouseClick(panel._ep_toggle, QtMouseLeft)
    assert panel.isExpanded() is False
    assert panel._ep_widget.isVisible() is False
    assert panel._ep_toggle.isChecked() is False
    assert changes == [False]

    # Click the title label to expand the panel again
    qtbot.mouseClick(panel._ep_label, QtMouseLeft)
    assert panel.isExpanded() is True
    assert panel._ep_widget.isVisible() is True
    assert panel._ep_toggle.isChecked() is True
    assert changes == [False, True]

    # Set the expanded state directly, which must also update the toggle
    # button so its icon stays in sync with the actual state
    panel.setExpanded(False)
    assert panel.isExpanded() is False
    assert panel._ep_widget.isVisible() is False
    assert panel._ep_toggle.isChecked() is False
    assert changes == [False, True, False]

    panel.setExpanded(True)
    assert panel.isExpanded() is True
    assert panel._ep_widget.isVisible() is True
    assert panel._ep_toggle.isChecked() is True
    assert changes == [False, True, False, True]

    # Setting the same state again should not change anything, or emit
    panel.setExpanded(True)
    assert panel.isExpanded() is True
    assert panel._ep_widget.isVisible() is True
    assert changes == [False, True, False, True]

    # The internal slot itself also guards against a redundant state,
    # regardless of how it is invoked
    panel._toggleExpanded(True)
    assert panel.isExpanded() is True
    assert changes == [False, True, False, True]

    # Update the theme
    panel.updateTheme()
