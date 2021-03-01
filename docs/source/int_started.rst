.. _a_started:

***************
Getting Started
***************

.. _main website: https://novelwriter.io
.. _GitHub: https://github.com/vkbo/novelWriter/releases
.. _PyPi: https://pypi.org/project/novelWriter/

This section contains brief guides to how you can get novelWriter running on your computer. These
are the methods currently supported by the developer. Packages may also be available in other
package managers, but those are not managed by the developer. A Windows installer file is also
provided on the GitHub_ releases page and linked from the `main website`_.

As novelWriter matures, more options for how to install it and get it running will be added. For
non-Windows users the install process is at the present time best suited for people used to working
with the command line. But even if you're not, the install process is fairly straightforward.

The next pages have specific install instructions for the various operating systems novelWriter can
run on. The instructions below are supplementary information, instructions for alterbative methods,
and additional build options.

.. note::
   The text below assumes the command ``python`` corresponds to a Python 3 executable. For
   operating systems with both Python 2 and 3, the command ``python3`` may be needed instead. On
   Linux, the scripts can also be made executable and run without the ``python`` command. Likewise,
   ``pip`` may need to be replaced with ``pip3``.


.. _a_started_depend:

Dependencies
============

novelWriter has been designed to rely on as few dependencies as possible. Aside from the packages
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

If you install from PyPi, these dependencies should be installed automatically. If you install from
source, dependencies can still be installed from PyPi with:

.. code-block:: console

   pip install -r requirements.txt


.. _a_started_install:

Installing via PyPi
===================

The application is written in Python 3 using Qt5 via PyQt5. It is developed on Linux, but it should
in principle work fine on other operating systems as long as dependencies are met.

You can download the latest version of novelWriter from the source repository on GitHub_.
novelWriter is also hosted on PyPi_, and can be installed on all operating systems that support Qt5
and Python 3. It is regularly tested on Linux, Windows and macOS. The latest version of novelWriter
is |release|.

To install from PyPi you must first have the ``python`` and ``pip`` commands available on your
system. If you don't, see specific instructions for your operating system later in this document.
To install novelWriter from PyPi, use the following command:

.. code-block:: console

   pip install novelwriter

To upgrade an existing installation, use:

.. code-block:: console

   pip install --upgrade novelwriter

When installing via pip, novelWriter can be launched from command line with:

.. code-block:: console

   novelWriter

Make sure the install location for pip is in your PATH variable. This is not always the case by
default.


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
