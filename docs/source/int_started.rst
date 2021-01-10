.. _a_started:

***************
Getting Started
***************

This is a brief guide to how you can get novelWriter running on your computer. These are the
methods currently supported by the developer. Packages may also be available in other package
managers, but those are not managed by the developer. A Windows installer file is also provided on
the GitHub releases page and linked from the `main website`_.

As novelWriter matures, more options for how to install it and get it running will be added. For
non-Windows users the install process is at the present time best suited for people used to working
with the command line. But even if you're not, the install process is fairly straight forward.

.. note::
   The text below assumes the command ``python`` corresponds to a Python 3 executable. For
   operating systems with both Python 2 and 3, the command ``python3`` may be needed instead. On
   Linux, the scripts can also be made executable and run without the ``python`` command. Likewise,
   ``pip`` may need to be replaced with ``pip3``.

.. _main website: https://novelwriter.io


.. _a_started_install:

Installing and Running
======================

The application is written in Python 3 using Qt5 via PyQt5. It is developed on Linux, but it should
in principle work fine on other operating systems as long as dependencies are met.

You can download the latest version of novelWriter from the source repository on GitHub_.
novelWriter is also hosted on PyPi_, and can be installed on all operating systems that support Qt5
and Python 3. It is regularly tested on Linux, Windows and macOS.

To install from PyPi you must first have the ``python`` and ``pip`` commands available on your
system. If you don't, see specific instructions for your operating system later in this document.
To install novelWriter from PyPi, use the following command:

.. code-block:: console

   pip install novelwriter

To upgrade an existing installation, use:

.. code-block:: console

   pip install --upgrade novelwriter

The latest version of novelWriter is |release|.

.. _GitHub: https://github.com/vkbo/novelWriter/releases
.. _PyPi: https://pypi.org/project/novelWriter/


.. _a_started_depend:

Python Dependencies
-------------------

novelWriter has been designed to rely on as few dependencies as possible. Aside from the package(s)
needed to communicate with the Qt GUI libraries, only one package is required for handling the XML
format of the main project file. Everything else is handled with standard Python libraries.

The following Python packages are needed to run novelWriter:

* ``pyqt5`` – needed for connecting with the Qt5 libraries.
* ``lxml`` – needed for full XML support.
* ``pyenchant`` – needed for efficient spell checking (optional).

PyQt/Qt should be at least 5.2.1, but ideally 5.10 or higher for nearly all features to work.
Exporting to standard Markdown, for instance, requires PyQt/Qt 5.14. Searching using regular
expressions requires 5.3, and for full Unicode support, 5.13. There is no known minimum version
requirement for package ``lxml``, but the code was originally written with 4.2, which is therefore
set as the minimum. It may work on lower versions. You have to test it.

Optionally, a package can be installed to interface with the Enchant spell checking libaries, but
this isn't strictly required. If no external spell checking library is available, novelWriter falls
back to using the internal ``difflib`` of Python to check spelling. This is a much slower approach,
and it is less sophisticated than full spell checking libaries, but if you only work with small
files, the performance loss is not noticeable. The spell check library must be at least 3.0 to work
with Windows. On Linux, 2.0 also works fine.

If you install from PyPi, these dependencies should be installed automatically. They can be
manually installed with:

.. code-block:: console

   pip install -r requirements.txt


.. _a_started_running:

Running from Source
-------------------

If all the required dependencies are met, you can run novelWriter from the command line with:

.. code-block:: console

   python novelWriter.py

A few switches are supported from the command line, mostly to assist in debugging if an error is
encountered. To list all options, run:

.. code-block:: console

   python novelWriter.py --help


.. _a_started_linux:

Setup on Linux
==============

The dependencies of novelWriter are generally available from Linux distro repositories. For Debian
and Ubuntu, they can be installed with:

.. code-block:: console

   sudo apt install python3-pyqt5 python3-lxml python3-enchant

If you downloaded the source, you can use the provided ``setup.py`` script to install novelWriter
into the system's default Python install locations. If so, run:

.. code-block:: console

   python setup.py install

To set up the novelWriter desktop launcher, the icons, and the project file association, run:

.. code-block:: console

   python setup.py xdg-install

By default, these commands install novelWriter and its icons for the current user only. To install
for all users, run the script with the ``sudo`` command. Other options are also available. Run
``python setup.py help`` for a full list of install options.


.. _a_started_macos:

Setup on macOS
==============

These instructions assume you're using brew, and have Python and pip set up. If not, see the
`brew docs`_ for help. Main requirements are installed via the requirements file. You also need to
install the ``pyobjc`` package, so you must run:

.. code-block:: console

   pip3 install --user -r requirements.txt
   pip3 install --user pyobjc

For spell checking you may also need to install the enchant package. It comes with a lot of default
dictionaries.

.. code-block:: console

   brew install enchant

.. _brew docs: https://docs.brew.sh/Homebrew-and-Python


.. _a_started_windows:

Setup on Windows
================

On Windows, you have two options: You can either run from source, or install novelWriter via a
Windows installer.


.. _a_started_win_installer:

Windows Installer
-----------------

You can install novelWriter with the Windows installer for 64-bit Windows available on the
`main website`_ and GitHub_ page. This installer bundles all that is needed for novelWriter to run,
including Python and the XML and Qt libraries. When installing novelWriter this way, you don't need
to install any of the dependencies manually. The installer is made with pyinstaller and Inno Setup.


.. _a_started_win_source:

From Source
-----------

To run from source, you may first need to install Python. If you don't have it installed, you can
download it from the python.org_ website. novelWriter should work with Python 3.6 or higher, but it
is recommended that you install the latest version of Python.

Also, make sure you select the "Add Python to PATH" option during installation, otherwise the
``python`` command will not work in the command line window.

.. image:: images/python_win_install.png
   :width: 600

Once Python is set up and running, you can either run novelWriter from the folder where you
extracted it, or you can build an executable and run that from a desktop icon instead.

The PyPi installer should come bundled with the Python installation, so to install dependencies,
run:

.. code-block:: console

   pip install --user -r requirements.txt

.. tip::

   To create a desktop shortcut to launch novelWriter, you can right click the ``novelWriter.py``
   file, create a shortcut, then right click again, select "Properties" and change the target to
   your python executable followed by ``novelWriter.py``. It should look something like this:
   ``C:\...\AppData\Local\Programs\Python\Python38\python.exe novelWriter.py``

You can also run the ``make.py`` script to generate a single executable, or an installer.
See `Build and Install novelWriter`_ for more details or run: ``python make.py help``.

.. _python.org: https://www.python.org/downloads/windows/
.. _Build and Install novelWriter: https://github.com/vkbo/novelWriter/blob/main/setup/README.md


.. _a_started_docs:

Building the Documentation
==========================

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

If successful, the documentation should be available in the ``docs/build/html`` folder and you can
open the ``index.html`` file in your browser.

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
