.. _a_source:

*******************
Running from Source
*******************

.. _main website: https://novelwriter.io
.. _GitHub: https://github.com/vkbo/novelWriter/releases
.. _PyPi: https://pypi.org/project/novelWriter/
.. _Sphinx Docs: https://www.sphinx-doc.org/

This section describes various ways of running novelWriter directly from the source code, and how
to build the various components like the translation files and documentation.

.. note::
   The text below assumes the command ``python`` corresponds to a Python 3 executable. Python 2 is
   now deprecated, but many systems still have both Python 2 and 3. For such systems, the command
   ``python3`` may be needed instead. Likewise, ``pip`` may need to be replaced with ``pip3``.


.. _a_source_depend:

Dependencies
============

novelWriter has been designed to rely on as few dependencies as possible. Aside from the packages
needed to communicate with the Qt GUI libraries, only one package is required for handling the XML
format of the main project file. Everything else is handled with standard Python libraries.

The following Python packages are needed to run novelWriter:

* ``PyQt5`` – needed for connecting with the Qt5 libraries.
* ``lxml`` – needed for full XML support.
* ``PyEnchant`` – needed for spell checking (optional).

PyQt/Qt should be at least 5.10, but ideally 5.13 or higher for all features to work. For instance,
searching using regular expressions with full Unicode support requires 5.13. There is no known
minimum version requirement for package ``lxml``, but the code was originally written with 4.2,
which is therefore set as the minimum. It may work on lower versions. You have to test it.

If you want spell checking, you must install the ``PyEnchant`` package. The spell check library
must be at least 3.0 to work with Windows. On Linux, 2.0 also works fine.

If you install from PyPi, these dependencies should be installed automatically. If you install from
source, dependencies can still be installed from PyPi with:

.. code-block:: bash

   pip install -r requirements.txt

.. note::

   On Linux distros, the Qt library is usually split up into multiple packages. In some cases,
   secondary dependencies may not be installed automatically. For novelWriter, the library files
   for renderring the SVG icons may be left out and needs to be installed manually. This is the
   case on for instance Arch Linux.


.. _a_source_install:

Install from Source
===================

You can download the latest version of novelWriter from the source repository on GitHub_ and run
the setup manually. It is equivalent to what the ``pip install`` command does, and it installs
novelWriter to the default location for Python packages.

This step requires that you have ``setuptools`` installed on your system. If you don't have it
installed, it can usually be installed from your distro's repository. For Debian and Ubuntu this is
achieved with:

.. code-block:: bash

   sudo apt install python3-setuptools

The package is also available from PyPi:

.. code-block:: bash

   pip install --user setuptools

With ``setuptools`` in place, novelWriter can be installed to the user space with:

.. code-block:: bash

   python setup.py install --user

.. tip::

   The main setup script has a number of options that may be useful to you. You can list them by
   running ``python setup.py help``.


.. _a_source_i18n:

Building the Translation Files
==============================

If you installed novelWriter from a package, the translation files should be pre-built and
included. If you're running novelWriter from the source code, you will need to generate the files
yourself. The files you need will be written to the ``novelwriter/assets/i18n`` folder, and will
have the ``.qm`` file extension.

You can build the ``.qm`` files with:

.. code-block:: bash

   python setup.py qtlrelease

This requires that the Qt Linguist tool is installed on your system. On Ubuntu and Debian, the
needed package is called ``qttools5-dev-tools``.

.. note::
   If you want to improve novelWriter with translation files for another language, or update an
   existing translation, instructions for how to contribute can be found in the ``README.md`` file
   in the ``i18n`` folder of the source code.


.. _a_source_sample:

Building the Example Project
============================

In order to be able to create new projects from example files, you need a ``sample.zip`` file in
the ``assets`` folder of the source. This file can be built from setup script by running:

.. code-block:: bash

   python setup.py sample


.. _a_source_docs:

Building the Documentation
==========================

A local copy of this documentation can be generated as HTML. This requires the following Python
packages from PyPi:

.. code-block:: bash

   pip install furo sphinx

The documentation can then be built from the root folder in the source code by running:

.. code-block:: bash

   make -C docs html

If successful, the documentation should be available in the ``docs/build/html`` folder and you can
open the ``index.html`` file in your browser.

You can also build a PDF manual from the documentation using the setup script:

.. code-block:: bash

   python setup.py manual

This will build the documentation as a PDF using LaTeX. The file will then be copied into the
assets folder and made available in the :guilabel:`Help` menu in novelWriter. The Sphinx build
system has a few extra dependencies when building the PDF. Please check the `Sphinx Docs`_ for more
details.
