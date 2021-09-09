.. _a_other:

*******************
Other Setup Methods
*******************

.. _main website: https://novelwriter.io
.. _GitHub: https://github.com/vkbo/novelWriter/releases
.. _PyPi: https://pypi.org/project/novelWriter/
.. _Sphinx Docs: https://www.sphinx-doc.org/

This section describes various other setup methods, and instructions for building needed files
when running novelWriter from the source code directly.

.. note::
   The text below assumes the command ``python`` corresponds to a Python 3 executable. Python 2 is
   now deprecated, but many systems still have both Python 2 and 3. For such systems, the command
   ``python3`` may be needed instead. On Linux, the scripts can also be made executable and run
   without the ``python`` command. Likewise, ``pip`` may need to be replaced with ``pip3``.


.. _a_other_depend:

Dependencies
============

novelWriter has been designed to rely on as few dependencies as possible. Aside from the packages
needed to communicate with the Qt GUI libraries, only one package is required for handling the XML
format of the main project file. Everything else is handled with standard Python libraries.

The following Python packages are needed to run novelWriter:

* ``PyQt5`` – needed for connecting with the Qt5 libraries.
* ``lxml`` – needed for full XML support.
* ``PyEnchant`` – needed for spell checking (optional).

PyQt/Qt should be at least 5.3, but ideally 5.10 or higher for nearly all features to work. For
instance, searching using regular expressions with full Unicode support requires 5.13. There is no
known minimum version requirement for package ``lxml``, but the code was originally written with
4.2, which is therefore set as the minimum. It may work on lower versions. You have to test it.

If you want spell checking, you must install the ``PyEnchant`` package. The spell check library
must be at least 3.0 to work with Windows. On Linux, 2.0 also works fine.

If you install from PyPi, these dependencies should be installed automatically. If you install from
source, dependencies can still be installed from PyPi with:

.. code-block:: console

   pip install -r requirements.txt


.. _a_other_pip:

Installing from PyPi
====================

novelWriter is available on the Python Package Index, or PyPi_.

To install from PyPi you must first have the ``python`` and ``pip`` commands available on your
system. If you don't, see specific instructions for your operating system in this documentation on
how to get the Python environment set up.

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


.. _a_other_source:

Installing from Source
======================

You can download the latest version of novelWriter from the source repository on GitHub_ and run
the setup manually. It is equivalent to what the ``pip install`` command does, and it installs
novelWriter to the default location for Python packages.

This step requires that you have ``setuptools`` installed on your system. If you don't have it
installed, it can usually be installed from your distro's repository. For Debian and Ubuntu this is
achieved with:

.. code-block:: console

   sudo apt install python3-setuptools

The package is also available from PyPi:

.. code-block:: console

   pip install --user setuptools

With ``setuptools`` in place, novelWriter can be installed to the user space with:

.. code-block:: console

   python setup.py install --user

.. tip::

   The main setup script has a number of options that may be useful to you. You can list them by
   running ``python setup.py --help``.


.. _a_other_i18n:

Building the Translation Files
==============================

If you installed novelWriter from a package, the translation files should be pre-built and
included. If you're running novelWriter from the source code, you will need to generate the files
yourself. The files you need will be written to the ``novelwriter/assets/i18n`` folder, and will
have the ``.qm`` file extension.

You can build the ``.qm`` files with:

.. code-block:: console

   python setup.py qtlrelease

This requires that the Qt Linguist tool is installed on your system. On Ubuntu and Debian, the
needed package is called `qttools5-dev-tools`.

.. note::
   If you want to improve novelWriter with translation files for another language, or update an
   existing translation, instructions for how to contribute can be found in the README.md file in
   the ``i18n`` folder of the source code.


.. _a_other_docs:

Building the Documentation
==========================

A local copy of this documentation can be generated as HTML. This requires the following Python
packages on Debian and Ubuntu.

* ``python3-sphinx``
* ``python3-sphinx-rtd-theme``

Or from PyPi:

.. code-block:: console

   pip install sphinx sphinx-rtd-theme

The documentation can then be built from the ``docs`` folder in the source code by running:

.. code-block:: console

   make html

If successful, the documentation should be available in the ``docs/build/html`` folder and you can
open the ``index.html`` file in your browser.

You can also build a PDF manual from the documentation using the setup script:

.. code-block:: console

   python setup.py manual

This will build the documentation as a PDF using LaTeX. The file will then be copied into the
assets folder and made available in the :guilabel:`Help` menu in novelWriter. The Sphinx build
system has a few extra dependencies when building the PDF. Please check the `Sphinx Docs`_ for more
details.
