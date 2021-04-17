@echo off

:: Check for Python Installation
echo.
echo Looking for Python
python --version 2>NUL
if errorlevel 1 goto errorNoPython
echo Python found. OK.
echo.

if exist setup.py (
    echo setup.py found. OK.
) else (
    goto errorNoSetup
)

:: Install the PyQt5, lxml and pyenchant dependencies
python setup.py pip

:: Create the desktop and start menu icons
python setup.py win-install

pause
goto:eof

:errorNoPython
echo.
echo ERROR^: Python is not installed on your system, or cannot be found.
echo.
echo Please download and install it from https://www.python.org/downloads/
echo Also make sure the "Add Python to PATH" option is selected during installation.
echo.
goto:eof

:errorNoSetup
echo.
echo ERROR^: Could not find the setup.py script.
echo.
echo Make sure you run setup.py from the novelWriter root folder.
echo.

pause
