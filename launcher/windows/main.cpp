#include <windows.h>
#include <stdio.h>
#include <tchar.h>
#include <iostream>

void _tmain( int argc, TCHAR *argv[] ) {
    STARTUPINFO si;
    PROCESS_INFORMATION pi;

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    TCHAR fileName[MAX_PATH];
    auto pathlen = GetModuleFileName(NULL, fileName, MAX_PATH);
    fileName[pathlen - 15] = 0;
    SetCurrentDirectory(fileName);
    std::cout << "WorkDir: " << fileName << std::endl;

    TCHAR cmd[MAX_PATH] = "pythonw.exe novelWriter.pyw";
    if (argc > 1) {
        _tcscat_s(cmd, TEXT(" "));
        _tcscat_s(cmd, argv[1]);
    }
    std::cout << "Command: " << cmd << std::endl;

    CreateProcess(NULL, cmd, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi);

    return;
}
