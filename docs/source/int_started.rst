.. _a_started:

***************
Getting Started
***************

.. _main website: https://novelwriter.io
.. _GitHub: https://github.com/vkbo/novelWriter/releases
.. _PyPi: https://pypi.org/project/novelWriter/

This section contains brief guides to how you can get novelWriter running on your computer. These
are the methods currently supported by the developer. Packages may also be available in other
package managers, but those are not managed by the developer. No installers are provided at this
time, but it is fairly straightforward to set up novelWriter with the provided install scripts.

As novelWriter matures, more options for how to install it and get it running will be added. For
non-Windows users the install process is at the present time best suited for people used to working
with the command line. But even if you're not, the install process is fairly straightforward.

The next pages have specific install instructions for the various operating systems novelWriter can
run on. The instructions below are supplementary information, instructions for alterbative methods,
and additional build options.

.. note::
   The text below assumes the command ``python`` corresponds to a Python 3 executable. Python 2 is
   now deprecated, but many systems still have both Python 2 and 3. For such systems, the command
   ``python3`` may be needed instead. On Linux, the scripts can also be made executable and run
   without the ``python`` command. Likewise, ``pip`` may need to be replaced with ``pip3``.


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

PyQt/Qt should be at least 5.3, but ideally 5.10 or higher for nearly all features to work. For
instance, searching using regular expressions with full Unicode support requires 5.13. There is no
known minimum version requirement for package ``lxml``, but the code was originally written with
4.2, which is therefore set as the minimum. It may work on lower versions. You have to test it.

Optionally, a package can be installed to interface with the Enchant spell checking libaries, but
this isn't strictly required. If no external spell checking library is available, novelWriter falls
back to using the internal ``difflib`` of Python to check spelling. This is a slower and less
sophisticated spell checker than the full spell checking libaries. The spell check library must be
at least 3.0 to work with Windows. On Linux, 2.0 also works fine.

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
system. If you don't, see specific instructions for your operating system in this documentation.
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


.. _a_started_i18n:

Building the Translation Files
==============================

If you installed novelWriter from a package, the translation files should be pre-built and
included. If you're running novelWriter from the source code, you will need to generate the files
yourself. The files you need will be written to the ``i18n`` folder, and will have the ``.qm`` file
extension.

You can build the ``.qm`` files with:

.. code-block:: console

   python3 setup.py qtlrelease

This requires that the Python package ``pylupdate5`` to be installed.

.. note::
   If you want to improve novelWriter with translation files for another language, or update an
   existing translation, instructions for how to contribute can be found in the README file in the
   ``i18n`` folder of the source code.


.. _a_started_docs:

Building the Documentation
==========================

If you installed novelWriter from a package, the documentation should be bre-built and included. If
you're running novelWriter from the source code, a local copy of this documentation can be
generated. It requires the following Python packages on Debian and Ubuntu.

* ``python3-sphinx``
* ``python3-sphinx-rtd-theme``
* ``python3-sphinxcontrib.qthelp``

Or from PyPi:

.. code-block:: console

   pip install sphinx sphinx-rtd-theme sphinxcontrib-qthelp

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
