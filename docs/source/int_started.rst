.. _a_started:

***************
Getting Started
***************

This is a brief guide to how you can get novelWriter running on your computer. These are the methods
currently supported by the developer. Packages may also be available in other package managers, but
those are not managed by me.

As novelWriter matures, more options for how to install it and get it running will be added. At the
present time, the process is best suited for people used to working with Python projects from command
line.


.. _a_started_install:

Installation
============

You can download the latest version of novelWriter from the source repository on GitHub_. You can
also install it directly from PyPi with ``pip install novelwriter``, or download the packages
directly from the PyPi_ project page.

Latest version of novelWriter is |release|.

.. _GitHub: https://github.com/vkbo/novelWriter/releases
.. _PyPi: https://pypi.org/project/novelWriter/


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
expressions requires 5.3, and for full Unicode support, 5.13.

There is no known minimum version requirement for package ``lxml``, but the code was originally
written with 4.2, which is therefore set as the minimum. It may work on lower versions. You have to
test it.

The spell checking extension is optional, but recommended:

* ``pyenchant``, needed for efficient spell checking.

The optional spell check library must be at least 3.0.0 to work with Windows. On Linux, 2.0.0 also
works fine.


.. _a_started_depend_docs:

Building the Documentation
--------------------------

If you installed novelWriter from a package, the documentation should be included. If you're running
novelWriter from the source code, a local copy of this documentation can be generated. It requires
the following Python packages on Debian and Ubuntu.

* ``python3-sphinx``
* ``python3-sphinxcontrib.qthelp``

Or from PyPi:

.. code-block:: console

   pip install sphinx sphinxcontrib-qthelp

To build the help packages from the documentation source, run

.. code-block:: console

   ./setup.py qthelp

from the root source folder.

The setup script will copy the generated files into the ``nw/assets/help`` folder, and novelWriter
will detect the presence of the files and redirect the menu help entry to open help locally instead
of sending the user to the website. Pressing the :kbd:`F1` key will in any case try to open help
locally first, then send you to the website as a fallback.

.. note::
   In order for the local version of help to work, the Qt Assistant must be installed on the local
   computer. If it isn't available, or novelWriter cannot find it, the help feature will fall back
   to redirecting you to the documentation website.


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

There are also a couple of install scripts in the setup folder which will assist in setting up a
launch icon and the novelWriter project file mimetype for Gnome desktops on Linux. Currently,
there's one script for Debian and one for Ubuntu.


.. _a_started_standalone:

Building a Standalone Executable
================================

A standalone executable can be built with ``pyinstaller``, using the provided python script
``install.py`` in the source folder. This script will automatically try to install all dependencies
and build the standalone executable of novelWriter. You can run the script by typing the following
into your command prompt:

.. code-block:: console

   python install.py

If successful, the executable will be in the "dist" folder.


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
