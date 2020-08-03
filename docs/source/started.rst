.. _a_started:

***************
Getting Started
***************

Latest version of novelWriter is |version|.


.. _a_started_install:

Installation
============

You can download the latest version of novelWriter from the source repository on GitHub_. You can
also install it directly from PyPi with ``pip install novelwriter``, or download the packages
directly from the PyPi_ project page.

.. _GitHub: https://github.com/vkbo/novelWriter/releases
.. _PyPi: https://pypi.org/project/novelWriter/


.. _a_started_depend:

Dependencies
============

novelWriter has been designed to rely on as few dependencies as possible. Aside from the package(s)
needed to communicate with the Qt GUI libraries, only one package is required for handling the XML
format of the main project file. Everything else is handled with standard Python libraries.

Optionally, a package can be installed to interface with the Enchant spell checking libaries, but
this isn't required. If no external spell checking library is available, novelWriter falls back to
using the internal ``difflib`` of Python to check spelling. This is a much slower approach, and it
is less sophisticated than full spell checking libaries, but if you only work with small files, the
performance loss is not noticeable.


.. _a_started_depend_packages:

Package Installation
--------------------

If you already have Python installed, all you need to do is install the dependencies. To do this,
you need to open your command line tool, find the folder where you extracted novelWriter, and run
the following command:

.. code-block:: console

   python -m pip install -r requirements.txt

On some operating systems you need to use ``python3`` instead of ``python``.

The following Python packages are required to run novelWriter:

* ``pyqt5``, needed for connecting with the Qt5 libraries.
* ``lxml``, needed full XML support.

.. note::
   Sometimes the SVG graphics package for PyQt5 must be installed separately. It is usually called
   something like ``python3-pyqt5.qtsvg``.

PyQt/Qt should be at least 5.2.1, but ideally 5.10 or higher for nearly all features to work.
Exporting to standard Markdown, for instance, requires PyQt/Qt 5.14. Searching using regular
expressions requires 5.3, and for full Unicode support, 5.13.

There are no known minimum for package ``lxml``, but the code was originally written with 4.2,
which is therefore set as the minimum.

The spell checking extension is optional, but recommended:

* ``pyenchant``, needed for efficient spell checking.

The optional spell check library must be at least 3.0.0 to work with Windows. On Linux, 2.0.0 also
works fine.


.. _a_started_running:

Running novelWriter
===================

If all the required dependencies are met, you can run novelWriter from the command line in one of
the following ways:

.. code-block:: console

   python novelWriter.py
   python3 novelWriter.py
   ./novelWriter.py

A few switches are supported from the command line, mostly to assist in debugging if an error is
encountered. To list all options, run:

.. code-block:: console

   python novelWriter.py --help

There are also a couple of install scripts in the assets folder which will assist in setting up
launch icon and the novelWriter project file mimetype for Gnome desktops on Linux. Currently,
there's one script for Debian and one for Ubuntu.


.. _a_started_standalone:

Building a Standalone Executable
================================

A standalone executable can be built with pyinstaller, using the provided python script
``install.py`` in the source folder. This script will automatically try to install all dependencies
and build the standalone executable of novelWriter. You can run the script by typing the following
into your command prompt:

.. code-block:: console

   python install.py

If successful, the executable will be in the "dist" folder.


.. _a_started_standalone_win:

Additional Instructions for Windows
-----------------------------------

If you don't have Python installed, you can download it from the python.org website.
The installers for Windows are available at https://www.python.org/downloads/windows/

novelWriter should work with Python 3.6 or higher, and the executable installer is the easiest to
install.

Also, make sure you select the "Add Python to PATH" option.

.. image:: images/python_win_install.png
   :width: 600

Once Python is set up and running, you can either run novelWriter from the folder where you
extracted it, or you can build an executable and run that from a desktop icon instead.
