"""
novelWriter - Config File Parsers
=================================

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

import logging
import tomllib

from configparser import ConfigParser
from enum import Enum
from typing import TYPE_CHECKING, Any, TypeVar

from novelwriter.common import checkBool, checkFloat, checkInt, checkPath

if TYPE_CHECKING:
    from pathlib import Path
    from typing import IO

logger = logging.getLogger(__name__)

_T_Enum = TypeVar("_T_Enum", bound=Enum)


class NTomlParser:
    """Common: Adapted Toml Parser.

    This class mirrors the functionality of NConfigParser, but reads and
    writes the TOML format instead. Unlike the ini format, TOML has native
    support for the data types used here, so values are stored and
    returned as their native types rather than as strings. Only a flat
    structure of [section] tables containing key/value pairs is supported.
    """

    def __init__(self) -> None:
        self._data: dict[str, dict[str, Any]] = {}

    def __getitem__(self, section: str) -> dict[str, Any]:
        """Get the options of a section."""
        return self._data.setdefault(section, {})

    def __setitem__(self, section: str, values: dict[str, Any]) -> None:
        """Set the options of a section."""
        self._data[section] = dict(values)

    def has_option(self, section: str, option: str) -> bool:
        """Check if a section has a given option."""
        return option in self._data.get(section, {})

    def read_file(self, fileObj: IO[str]) -> None:
        """Read and parse TOML data from an open file."""
        data = tomllib.loads(fileObj.read())
        self._data = {k: v for k, v in data.items() if isinstance(v, dict)}

    def write(self, fileObj: IO[str]) -> None:
        """Write the data to an open file as TOML."""
        for section, values in self._data.items():
            fileObj.write(f"[{section}]\n")
            for key, value in values.items():
                fileObj.write(f"{key} = {self._dump(value)}\n")
            fileObj.write("\n")

    def getStr(self, section: str, option: str, default: str) -> str:
        """Read string value."""
        value = self._data.get(section, {}).get(option, default)
        return value if isinstance(value, str) else default

    def getInt(self, section: str, option: str, default: int) -> int:
        """Read integer value."""
        if self.has_option(section, option):
            return checkInt(self._data[section][option], default)
        return default

    def getFloat(self, section: str, option: str, default: float) -> float:
        """Read float value."""
        if self.has_option(section, option):
            return checkFloat(self._data[section][option], default)
        return default

    def getBool(self, section: str, option: str, default: bool) -> bool:
        """Read boolean value."""
        if self.has_option(section, option):
            return checkBool(self._data[section][option], default)
        return default

    def getPath(self, section: str, option: str, default: Path) -> Path:
        """Read a Path value."""
        value = self._data.get(section, {}).get(option, default)
        return checkPath(value, default)

    def getStrList(self, section: str, option: str, default: list[str]) -> list[str]:
        """Read string list."""
        result = default.copy() if isinstance(default, list) else []
        if self.has_option(section, option):
            data = self._data[section][option]
            if isinstance(data, list):
                for i in range(min(len(data), len(result))):
                    result[i] = str(data[i])
        return result

    def getIntList(self, section: str, option: str, default: list[int]) -> list[int]:
        """Read integer list."""
        result = default.copy() if isinstance(default, list) else []
        if self.has_option(section, option):
            data = self._data[section][option]
            if isinstance(data, list):
                for i in range(min(len(data), len(result))):
                    result[i] = checkInt(data[i], result[i])
        return result

    def getEnum(self, section: str, option: str, default: _T_Enum) -> _T_Enum:
        """Read enum value."""
        if self.has_option(section, option):
            data = self._data[section][option]
            if isinstance(data, str):
                return type(default).__members__.get(data.upper(), default)
        return default

    @staticmethod
    def _dump(value: Any) -> str:
        """Format a value as a TOML literal."""
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, (list, tuple)):
            return "[" + ", ".join(NTomlParser._dump(v) for v in value) + "]"
        return NTomlParser._dumpStr(str(value))

    @staticmethod
    def _dumpStr(value: str) -> str:
        """Format a string as a quoted TOML basic string."""
        escaped = (
            value
            .replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\t", "\\t")
            .replace("\n", "\\n")
            .replace("\r", "\\r")
        )
        return f'"{escaped}"'


class NConfigParser(ConfigParser):
    """Common: Adapted Config Parser.

    This is a subclass of the standard config parser that adds type safe
    helper functions, and support for lists. It also turns off
    interpolation, which would require % symbols to be escaped (#2455).
    """

    def __init__(self) -> None:
        super().__init__(interpolation=None)

    def getStr(self, section: str, option: str, default: str) -> str:
        """Read string value."""
        return self.get(section, option, fallback=default)

    def getInt(self, section: str, option: str, default: int) -> int:
        """Read integer value."""
        try:
            return self.getint(section, option, fallback=default)
        except ValueError:
            logger.error("Could not read '%s':'%s' from config", section, option)
        return default

    def getFloat(self, section: str, option: str, default: float) -> float:
        """Read float value."""
        try:
            return self.getfloat(section, option, fallback=default)
        except ValueError:
            logger.error("Could not read '%s':'%s' from config", section, option)
        return default

    def getBool(self, section: str, option: str, default: bool) -> bool:
        """Read boolean value."""
        try:
            return self.getboolean(section, option, fallback=default)
        except ValueError:
            logger.error("Could not read '%s':'%s' from config", section, option)
        return default

    def getPath(self, section: str, option: str, default: Path) -> Path:
        """Read a Path value."""
        return checkPath(self.get(section, option, fallback=default), default)

    def getStrList(self, section: str, option: str, default: list[str]) -> list[str]:
        """Read string list."""
        result = default.copy() if isinstance(default, list) else []
        if self.has_option(section, option):
            data = self.get(section, option, fallback="").split(",")
            for i in range(min(len(data), len(result))):
                result[i] = data[i].strip()
        return result

    def getIntList(self, section: str, option: str, default: list[int]) -> list[int]:
        """Read integer list."""
        result = default.copy() if isinstance(default, list) else []
        if self.has_option(section, option):
            data = self.get(section, option, fallback="").split(",")
            for i in range(min(len(data), len(result))):
                result[i] = checkInt(data[i].strip(), result[i])
        return result

    def getEnum(self, section: str, option: str, default: _T_Enum) -> _T_Enum:
        """Read enum value."""
        if self.has_option(section, option):
            data = self.get(section, option, fallback="")
            return type(default).__members__.get(data.upper(), default)
        return default
