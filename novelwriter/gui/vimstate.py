from __future__ import annotations
from enum import IntEnum

__all__ = ["Mode", "VimState"]


class Mode(IntEnum):
    NORMAL = 0
    INSERT = 1
    VISUAL = 2


class VimState:
    """Minimal Vim state machine."""
    __slots__ = (
        "mode",
        "command",
        "enabled",
        "pending_operator",
    )

    def __init__(self) -> None:
        self.enabled: bool = True
        self.mode: Mode = Mode.NORMAL
        self.command: str = ""
        self.pending_operator: str = ""   # stores first key of two-part commands (e.g. 'd' in 'dd')

    def reset_command(self) -> None:
        """Clear everything that makes up a single Vim command."""
        self.command = ""
        self.pending_operator = ""

    def set_mode(self, new_mode: Mode) -> None:
        self.mode = new_mode
        self.reset_command()
