@echo off

:: Check for Python Installation
echo.
echo Looking for Python
python --version 2>NUL
if errorlevel 1 goto errorNoPython
echo Python found. OK.

if exist pkgutils.py (
    echo pkgutils.py found. OK.
) else (
    cd ..
    if exist pkgutils.py (
        echo pkgutils.py found. OK.
    ) else (
        goto errorNoSetup
    )
)
echo.

echo Ready to remove the novelWriter icons, registry keys, and package dependencies.
set /P c=Are you sure you want to continue [y/n]? 
if /I "%c%" EQU "y" goto doUninst
goto afterUninst

:doUninst

:: Remove the desktop and start menu icons
python pkgutils.py win-uninstall

:: Remove the PyQt5 and pyenchant dependencies
pip uninstall --yes -r requirements.txt

:afterUninst

echo.
pause
goto:eof

:errorNoPython
echo.
echo ERROR^: Python is not installed on your system, or cannot be found.
echo.
echo Please download and install it from https://www.python.org/downloads/
echo Also make sure the "Add Python to PATH" option is selected during installation.
echo.

pause
goto:eof

:errorNoSetup
echo.
echo ERROR^: Could not find the pkgutils.py script.
echo.
echo Make sure you run pkgutils.py from the novelWriter root folder.
echo.

pause
