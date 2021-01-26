# -*- coding: utf-8 -*-
"""
novelWriter – ODT Text Converter
================================
Extends the Tokenizer class to generate ODT and FODT files

File History:
Created: 2021-01-26 [1.1rc1]

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

import logging

from nw.core.tokenizer import Tokenizer

logger = logging.getLogger(__name__)

class ToOdt(Tokenizer):

    def __init__(self, theProject, theParent):
        Tokenizer.__init__(self, theProject, theParent)

        return

    ##
    #  Class Methods
    ##

    def doConvert(self):
        """Convert the list of text tokens into a HTML document saved
        to theResult.
        """
        self.theResult = ""

        for tType, tLine, tText, tFormat, tStyle in self.theTokens:
            continue

        return

# END Class ToOdt
