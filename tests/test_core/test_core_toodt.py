# -*- coding: utf-8 -*-
"""
novelWriter – ToOdt Class Tester
=================================

This file is a part of novelWriter
Copyright 2018–2021, Veronica Berglyd Olsen

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

from nw.core import NWProject, NWIndex, ToOdt

@pytest.mark.core
def testCoreToOdt_Convert(dummyGUI):
    """Test the converter of the ToHtml class.
    """
    theProject = NWProject(dummyGUI)
    dummyGUI.theIndex = NWIndex(theProject, dummyGUI)
    theDoc = ToOdt(theProject, dummyGUI)

# END Test testCoreToOdt_Convert
