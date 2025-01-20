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

#ifndef UNICODE
#define UNICODE
#endif 

#include <windows.h>
#include <stdio.h>

int WINAPI wWinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, PWSTR pCmdLine, int nCmdShow) {

    STARTUPINFO si;
    PROCESS_INFORMATION pi;

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    wchar_t path[MAX_PATH];
    auto pathlen = GetModuleFileNameW(NULL, path, MAX_PATH);
    path[pathlen - 15] = 0;
    SetCurrentDirectory(path);

    wchar_t cmd[MAX_PATH] = L"pythonw.exe novelWriter.pyw";
    if (__argc > 1) {
        wcsncat_s(cmd, L" ", 1);
        wcsncat_s(cmd, __wargv[1], MAX_PATH-28);
    }

    CreateProcess(NULL, cmd, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi);

    return 0;
}
