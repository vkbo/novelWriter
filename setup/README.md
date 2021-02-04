# Build and Install novelWriter

The root folder of the repository contains two scripts for setup and install:


## Script `setup.py`

The `setup.py` is a standard Python setup script with a couple of additional
options:

### General

`help` – Print the help message.

`pip` – Install all package dependencies for novelWriter using pip.

`clean` – Will attempt to delete the `build` and `dist` folders.

### Additional Builds

`qthelp` – Build the help documentation for use with the Qt Assistant. Run
before install to have local help enable in the the installed version

`sample` – Build the sample project as a zip file. Run before install to enable
creating sample projects in the in-app New Project Wizard.

### Python Packaging

`minimal-zip` – Creates a minimal zip file of the core application without all
the other source files.

`pack-pyz` – Creates a pyz package in a folder with all dependencies using the
zipapp tool. On Windows, python embeddable is added to the folder.

`freeze` – Freeze the package and produces a folder with all dependencies using
the pyinstaller tool. This option is not designed for a specific OS.

`onefile` – Build a standalone executable with all dependencies bundled using
the pyinstaller tool. Implies `freeze`, cannot be used with `setup-exe`.

### General Installers

`install` – Installs novelWriter to the system's Python install location. Run
as root or with sudo for system-wide install, or as user for single user
install.

`xdg-install` – Install launcher and icons for freedesktop systems. Run as root
or with sudo for system-wide install, or as user for single user install.

`win-install` – Install desktop and start menu icons for Windows systems.

### "Windows Installers

`setup-exe` – Build a Windows installer from a pyinstaller freeze package using
Inno Setup. This option automatically disables `onefile`.

`setup-pyz` – Build a Windows installer from a zipapp package using Inno Setup.
