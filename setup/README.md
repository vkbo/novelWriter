# Build and Install novelWriter

The root folder of the repository contains two scripts for setup and install:


## Script `setup.py`

The `setup.py` is a standard Python setup script with a couple of additional options:

* `qthelp`: Will attempt to build a single file QtAssistand documentation file.
  This requires the Qt tools to be installed on the local system, as well as the sphinx build tools
  for the documentation.
* `sample`: Will create a `sample.zip` file in the `nw/assets` folder.
  This is the file the New Project Wizard uses to generate an example project.
  If novelWriter is run from source, this file is not needed.
* `xdg-install`: Will install novelWriter icons, mimetype, and desktop and menu launcher on Linux desktops.
  the application. This should work on standard Linux desktops.
  By default, this is installed for the current user. Run with `sudo` to install system-wide.

To install novelWriter as a local Python package, run:
```bash
sudo python setup.py install
```

## Script `make.py`

The `make.py` script provides a number of convenient options for building packages if novelWriter.

Usage:
```bash
python make.py [command]
```

It currently accept the following commands:

* `help`: Print the help message.
* `freeze`: Freeze the package and produces a folder of all dependencies using pyinstaller.
* `onefile`: Build a standalone executable with all dependencies bundled.
   Implies `freeze`, cannot be used with `setup`.
* `pip`: Run pip to install all package dependencies for novelWriter and this build tool.
* `setup`: Build a setup.exe installer for Windows.
   This option automaticall disables the `onefile` option.
* `clean`: This will attempt to delete the `build` and `dist` folders in the current folder.

For instance, to create a Windows installer, run:
```bash
python make.py freeze setup
```
