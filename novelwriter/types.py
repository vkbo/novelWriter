"""
novelWriter – Types and Flags
=============================

File History:
Created: 2024-04-01 [2.4rc1]

This file is a part of novelWriter
Copyright (C) 2024 Veronica Berglyd Olsen and novelWriter contributors

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

from PyQt6.QtCore import Qt
from PyQt6.QtGui import (
    QColor, QFont, QPainter, QPalette, QTextCharFormat, QTextCursor,
    QTextFormat
)
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QHeaderView, QSizePolicy, QStyle

# Alignment Flags

QtAlignAbsolute = Qt.AlignmentFlag.AlignAbsolute
QtAlignCenter = Qt.AlignmentFlag.AlignCenter
QtAlignCenterTop = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
QtAlignJustify = Qt.AlignmentFlag.AlignJustify
QtAlignLeft = Qt.AlignmentFlag.AlignLeft
QtAlignLeftBase = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBaseline
QtAlignLeftMiddle = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
QtAlignLeftTop = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
QtAlignMiddle = Qt.AlignmentFlag.AlignVCenter
QtAlignRight = Qt.AlignmentFlag.AlignRight
QtAlignRightBase = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBaseline
QtAlignRightMiddle = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
QtAlignRightTop = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop
QtAlignTop = Qt.AlignmentFlag.AlignTop

QtVAlignNormal = QTextCharFormat.VerticalAlignment.AlignNormal
QtVAlignSub = QTextCharFormat.VerticalAlignment.AlignSubScript
QtVAlignSuper = QTextCharFormat.VerticalAlignment.AlignSuperScript

# Text Formats

QtPageBreakBefore = QTextFormat.PageBreakFlag.PageBreak_AlwaysBefore
QtPageBreakAfter = QTextFormat.PageBreakFlag.PageBreak_AlwaysAfter
QtPageBreakAuto = QTextFormat.PageBreakFlag.PageBreak_Auto

QtTextUserProperty = QTextFormat.Property.UserProperty

QtPropLineHeight = 1  # QTextBlockFormat.LineHeightTypes.ProportionalHeight

# Painter Types

QtTransparent = QColor(0, 0, 0, 0)
QtBlack = QColor(0, 0, 0)
QtNoBrush = Qt.BrushStyle.NoBrush
QtNoPen = Qt.PenStyle.NoPen
QtRoundCap = Qt.PenCapStyle.RoundCap
QtSolidLine = Qt.PenStyle.SolidLine
QtPaintAntiAlias = QPainter.RenderHint.Antialiasing
QtMouseOver = QStyle.StateFlag.State_MouseOver
QtSelected = QStyle.StateFlag.State_Selected

# Colour Types

QtHexRgb = QColor.NameFormat.HexRgb
QtHexArgb = QColor.NameFormat.HexArgb

QtColActive = QPalette.ColorGroup.Active
QtColInactive = QPalette.ColorGroup.Inactive
QtColDisabled = QPalette.ColorGroup.Disabled

# Qt Tree and Table Types

QtDecoration = Qt.ItemDataRole.DecorationRole
QtUserRole = Qt.ItemDataRole.UserRole

# Keyboard and Mouse Buttons

QtModCtrl = Qt.KeyboardModifier.ControlModifier
QtModNone = Qt.KeyboardModifier.NoModifier
QtModShift = Qt.KeyboardModifier.ShiftModifier
QtMouseLeft = Qt.MouseButton.LeftButton
QtMouseMiddle = Qt.MouseButton.MiddleButton

# Dialog Button Box Types

QtAccepted = QDialog.DialogCode.Accepted
QtRejected = QDialog.DialogCode.Rejected

QtRoleAccept = QDialogButtonBox.ButtonRole.AcceptRole
QtRoleAction = QDialogButtonBox.ButtonRole.ActionRole
QtRoleApply = QDialogButtonBox.ButtonRole.ApplyRole
QtRoleDestruct = QDialogButtonBox.ButtonRole.DestructiveRole
QtRoleReject = QDialogButtonBox.ButtonRole.RejectRole
QtRoleReset = QDialogButtonBox.ButtonRole.ResetRole

# Cursor Types

QtKeepAnchor = QTextCursor.MoveMode.KeepAnchor
QtMoveAnchor = QTextCursor.MoveMode.MoveAnchor

QtMoveLeft = QTextCursor.MoveOperation.Left
QtMoveRight = QTextCursor.MoveOperation.Right
QtMoveUp = QTextCursor.MoveOperation.Up
QtMoveDown = QTextCursor.MoveOperation.Down
QtMoveEndOfLine = QTextCursor.MoveOperation.EndOfLine
QtMoveStartOfLine = QTextCursor.MoveOperation.StartOfLine
QtMoveEnd = QTextCursor.MoveOperation.End
QtMoveStart = QTextCursor.MoveOperation.Start
QtMoveNextWord = QTextCursor.MoveOperation.NextWord
QtMovePreviousWord = QTextCursor.MoveOperation.PreviousWord
QtMoveEndOfWord = QTextCursor.MoveOperation.EndOfWord
QtMoveNextChar = QTextCursor.MoveOperation.NextCharacter

QtSelectWord = QTextCursor.SelectionType.WordUnderCursor
QtSelectLine = QTextCursor.SelectionType.LineUnderCursor
QtSelectBlock = QTextCursor.SelectionType.BlockUnderCursor
QtSelectDocument = QTextCursor.SelectionType.Document

QtImCursorRectangle = Qt.InputMethodQuery.ImCursorRectangle
QtImCurrentSelection = Qt.InputMethodQuery.ImCurrentSelection

# Size Policy

QtSizeExpanding = QSizePolicy.Policy.Expanding
QtSizeFixed = QSizePolicy.Policy.Fixed
QtSizeIgnored = QSizePolicy.Policy.Ignored
QtSizeMinimum = QSizePolicy.Policy.Minimum
QtSizeMinimumExpanding = QSizePolicy.Policy.MinimumExpanding

# Resize Mode

QtHeaderStretch = QHeaderView.ResizeMode.Stretch
QtHeaderToContents = QHeaderView.ResizeMode.ResizeToContents
QtHeaderFixed = QHeaderView.ResizeMode.Fixed

# Scroll Bar Policy

QtScrollAlwaysOn = Qt.ScrollBarPolicy.ScrollBarAlwaysOn
QtScrollAlwaysOff = Qt.ScrollBarPolicy.ScrollBarAlwaysOff
QtScrollAsNeeded = Qt.ScrollBarPolicy.ScrollBarAsNeeded

# Maps

FONT_WEIGHTS: dict[int, int] = {
    QFont.Weight.Thin:       100,
    QFont.Weight.ExtraLight: 200,
    QFont.Weight.Light:      300,
    QFont.Weight.Normal:     400,
    QFont.Weight.Medium:     500,
    QFont.Weight.DemiBold:   600,
    QFont.Weight.Bold:       700,
    QFont.Weight.ExtraBold:  800,
    QFont.Weight.Black:      900,
}

FONT_STYLE: dict[QFont.Style, str] = {
    QFont.Style.StyleNormal:  "normal",
    QFont.Style.StyleItalic:  "italic",
    QFont.Style.StyleOblique: "oblique",
}
