# Build and Install novelWriter

The root folder of the repository contains two scripts for setup and install:


## Script `setup.py`

The `setup.py` is a standard Python setup script with a couple of additional
options:

Some of the commands can be targeted towards a different OS than the host OS.
To target the command, add one of `--target-linux`, `--target-darwin` or
`--target-win`.

### General

`help` – Print the help message.

`pip` – Install all package dependencies for novelWriter using pip.

`clean` – Will attempt to delete the `build` and `dist` folders.

### Additional Builds

`qthelp` – Build the help documentation for use with the Qt Assistant. Run
before install to have local help enable in the the installed version

`qtlupdate` – Update the translation files for internationalisation.

`qtlrelease` – Build the language files for internationalisation.

`sample` – Build the sample project as a zip file. Run before install to enable
creating sample projects in the in-app New Project Wizard.

### Python Packaging

`minimal-zip` – Creates a minimal zip file of the core application without all
the other source files.

`pack-pyz` – Creates a pyz package in a folder with all dependencies using the
zipapp tool. On Windows, python embeddable is added to the folder.

`setup-pyz` – Build a Windows installer from a zipapp package using Inno Setup.

### System Install

`install` – Installs novelWriter to the system's Python install location. Run
as root or with sudo for system-wide install, or as user for single user
install.

`xdg-install` – Install launcher and icons for freedesktop systems. Run as root
or with sudo for system-wide install, or as user for single user install.
Running `xdg-uninstall` will remove the icons.

`win-install` – Install desktop and start menu icons for Windows systems.
Running `win-uninstall` will remove the icons.
