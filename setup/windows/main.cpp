/*
** novelWriter - Windows Launcher
** ==============================
**
** This file is a part of novelWriter
** Copyright (C) 2025 Veronica Berglyd Olsen and novelWriter contributors
**
** This program is free software: you can redistribute it and/or modify
** it under the terms of the GNU General Public License as published by
** the Free Software Foundation, either version 3 of the License, or
** (at your option) any later version.
**
** This program is distributed in the hope that it will be useful, but
** WITHOUT ANY WARRANTY; without even the implied warranty of
** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
** General Public License for more details.
**
** You should have received a copy of the GNU General Public License
** along with this program. If not, see <https://www.gnu.org/licenses/>.
*/

#include <windows.h>
#include <stdio.h>
#include <tchar.h>
#include <iostream>

void _tmain(int argc, TCHAR *argv[]) {
    STARTUPINFO si;
    PROCESS_INFORMATION pi;

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    TCHAR path[MAX_PATH];
    auto pathlen = GetModuleFileName(NULL, path, MAX_PATH);
    path[pathlen - 15] = 0;
    SetCurrentDirectory(path);
    std::cout << "WorkDir: " << path << std::endl;

    TCHAR cmd[MAX_PATH] = TEXT("pythonw.exe novelWriter.pyw");
    if (argc > 1) {
        _tcscat_s(cmd, TEXT(" "));
        _tcscat_s(cmd, argv[1]);
    }
    std::cout << "Command: " << cmd << std::endl;

    std::cout << "Launching novelWriter GUI" << std::endl;
    CreateProcess(NULL, cmd, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi);

    return;
}
