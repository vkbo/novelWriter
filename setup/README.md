# Build and Install novelWriter

The root folder of the repository contains a standard `setup.py` script. The `setup` folder
contains necessary files for the setup process, like icons and other files, and it also contains
additional scripts that are included in the minimal zip packages.

## Setup Script

The `setup.py` script in the root folder has all the necessary commands for generating packages,
installing icons, launcher, and file associations on Linux and Windows (no macOS support yet).

In addition, it is a wrapper for `setuptools` and accept all commands associated with this tool.

To list all custom package and install options in this script, run:
```
./setup.py help
```
## Windows Scripts

The `windows_install.bat` and `windows_uninstall.bat` are provided as convenience scripts for
Windows users who aren't used to running commands from command line. They are both located in the
`setup` folder in the source package, but in the minimal zip package for Windows, they can be
found in the root folder.

These scripts are designed to be double-clicked by the user, but can also be run from the command
line tool. In either case, they will check if Python is properly installed, and then run the
commands to install or uninstall the core dependencies of novelWriter, and then setup or remove the
desktop icon, start menu icon and registry entries.
