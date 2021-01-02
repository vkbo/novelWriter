.. _a_started:

***************
Getting Started
***************

This is a brief guide to how you can get novelWriter running on your computer. These are the
methods currently supported by the developer. Packages may also be available in other package
managers, but those are not managed by the developer. A Windows installer file is also provided on
the GitHub page and main website.

As novelWriter matures, more options for how to install it and get it running will be added. For
non-Windows users the install process is at the present time best suited for people used to working
with the command line.

.. note::
   The text below assumes the command ``python`` corresponds to a Python 3 executable. For
   operating systems with both Python 2 and 3, the command ``python3`` may be needed instead. On
   Linux, the scripts can also be made executable and run without the ``python`` command.


.. _a_started_install:

Installation
============

You can download the latest version of novelWriter from the source repository on GitHub_. You can
also install it directly from PyPi with ``pip install novelwriter``, or download the packages
directly from the PyPi_ project page.

Latest version of novelWriter is |release|.

.. _GitHub: https://github.com/vkbo/novelWriter/releases
.. _PyPi: https://pypi.org/project/novelWriter/


.. _a_started_install_win:

Windows Installer
-----------------

You can run novelWriter directly from source on Windows, but a Windows installer is also provided
for 64-bit Windows on the `main website`_ and GitHub_ page. This installer bundles all that is
needed for novelWriter to run, including Python and the xml and Qt libraries.

.. _main website: https://novelwriter.io


.. _a_started_install_source:

Install from Source on Linux
----------------------------

For Linux systems, novelWriter can be installed from source with the provided ``setup.py`` script.
To install novelWriter into the system's default Python install locations, run:

.. code-block:: console

   python setup.py install

To set up the novelWriter desktop launcher, the icons and the project file association, run:

.. code-block:: console

   python setup.py xdg-install

By default, these commands installs novelWriter and its icons for the current user only. To install
for all users, run the script with the ``sudo`` command. Other options are also available. Run
``python setup.py help`` for a full list of install options.


.. _a_started_depend:

Dependencies
============

novelWriter has been designed to rely on as few dependencies as possible. Aside from the package(s)
needed to communicate with the Qt GUI libraries, only one package is required for handling the XML
format of the main project file. Everything else is handled with standard Python libraries.

Optionally, a package can be installed to interface with the Enchant spell checking libaries, but
this isn't strictly required. If no external spell checking library is available, novelWriter falls
back to using the internal ``difflib`` of Python to check spelling. This is a much slower approach,
and it is less sophisticated than full spell checking libaries, but if you only work with small
files, the performance loss is not noticeable.


.. _a_started_depend_packages:

Package Installation
--------------------

If you already have Python installed, all you need to do is install the dependencies. To do this,
you need to open your command line tool, find the folder where you extracted novelWriter, and run
the following command:

.. code-block:: console

   pip install -r requirements.txt

This will install all the dependencies and recommended packages.

The following Python packages are required to run novelWriter:

* ``pyqt5``, needed for connecting with the Qt5 libraries.
* ``lxml``, needed full XML support.

You can of course also install these packages from your operating system's package repository.

PyQt/Qt should be at least 5.2.1, but ideally 5.10 or higher for nearly all features to work.
Exporting to standard Markdown, for instance, requires PyQt/Qt 5.14. Searching using regular
expressions requires 5.3, and for full Unicode support, 5.13. There is no known minimum version
requirement for package ``lxml``, but the code was originally written with 4.2, which is therefore
set as the minimum. It may work on lower versions. You have to test it.

The spell checking extension is optional, but recommended:

* ``pyenchant``, needed for efficient spell checking.

The optional spell check library must be at least 3.0 to work with Windows. On Linux, 2.0 also
works fine.


.. _a_started_depend_docs:

Building the Documentation
--------------------------

If you installed novelWriter from a package, the documentation should be included. If you're
running novelWriter from the source code, a local copy of this documentation can be generated. It
requires the following Python packages on Debian and Ubuntu.

* ``python3-sphinx``
* ``python3-sphinxcontrib.qthelp``

Or from PyPi:

.. code-block:: console

   pip install sphinx sphinxcontrib-qthelp

The documentation can then be built from the ``docs`` folder in the source code by running:

.. code-block:: console

   make html

If successful, the documentation should then be available in the ``docs/build/html`` folder.

The documentation can also be built for the Qt Assistant. To build the help packages from the
documentation source, run the following from the root source folder:

.. code-block:: console

   python setup.py qthelp

The setup script will copy the generated files into the ``nw/assets/help`` folder, and novelWriter
will detect the presence of the files and redirect the menu help entry to open help locally instead
of sending the user to the website. Pressing the :kbd:`F1` key will in any case try to open help
locally first, then send you to the website as a fallback.

.. note::
   In order for the local version of help to work, the Qt Assistant must be installed on the local
   computer. If it isn't available, or novelWriter cannot find it, the help feature will fall back
   to redirecting you to the documentation website.


.. _a_started_running:

Running from Source
===================

If all the required dependencies are met, you can run novelWriter from the command line:

.. code-block:: console

   python novelWriter.py

A few switches are supported from the command line, mostly to assist in debugging if an error is
encountered. To list all options, run:

.. code-block:: console

   python novelWriter.py --help


.. _a_started_standalone:

Building a Standalone Executable
================================

A standalone executable can be built with ``pyinstaller``, using the provided python script
``make.py`` in the source folder. This script can install dependencies, build a standalone
executable of novelWriter, or build a ``setup.exe`` file with Inno Setup.

For a full list of the script's options, run ``python make.py help``.


.. _a_started_standalone_win:

Additional Instructions for Windows
-----------------------------------

If you don't have Python installed, you can download it from the python.org website. The installers
for Windows are available at https://www.python.org/downloads/windows/

novelWriter should work with Python 3.6 or higher, and the executable installer is the easiest to
install.

Also, make sure you select the "Add Python to PATH" option.

.. image:: images/python_win_install.png
   :width: 600

Once Python is set up and running, you can either run novelWriter from the folder where you
extracted it, or you can build an executable and run that from a desktop icon instead.
