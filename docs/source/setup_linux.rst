.. _a_setup_linux:

**************
Setup on Linux
**************

.. _GitHub: https://github.com/vkbo/novelWriter/releases
.. _main website: https://novelwriter.io

This is a brief guide to how you can get novelWriter running on a Linux computer. There are
currently no install package of novelWriter for Linux, so it is recommended that you download
either the full source or minimal package and extract it to a practical location on your system and
run the ``setup.py`` script.


Running from Source
===================

To run novelWriter from source, download the latest source package from the release page on
GitHub_ or the `main website`_, or if you have git running on your computer, you can also clone the
repository.


Step 1: Installing Dependencies
-------------------------------

The dependencies of novelWriter are generally available from Linux distro repositories. For Debian
and Ubuntu, they can be installed with:

.. code-block:: console

   sudo apt install python3-pyqt5 python3-lxml python3-enchant

If you prefer to install dependencies via PyPi, or the repository dependencies are out of date, you
can install them with:

.. code-block:: console

   pip3 install --user -r requirements.txt


Step 2: Install Package (Optional)
----------------------------------

You can install novelWriter to the default location for Python packages using ``setuptools``. This
step is optional as you can also just put the novelWriter program folder wherever you like
yourself. For instance in ``/opt/novelWriter``, and then run Step 3 to set up icons and launcher.

To install novelWriter to the default location requires that you have ``setuptools`` installed on
your system. If you don't have it installed, it can usually be installed from your distro's
repository. For Debian and Ubuntu this is achieved with:

.. code-block:: console

   sudo apt install python3-setuptools

The package is also available from PyPi:

.. code-block:: console

   pip3 install --user setuptools

With ``setuptools`` in place, novelWriter can be installed to the user space with:

.. code-block:: console

   ./setup.py install --user

This should install novelWriter as ``~/.local/bin/novelWriter``. If you instead want to install for
all users, i.e. as ``/usr/local/bin/novelWriter``, run:

.. code-block:: console

   sudo ./setup.py install

This is equivalent to what the ``pip`` installer does. It puts novelWriter in the location on your
system where Python packages are usually kept. This is not really the best suited location for a
GUI application like novelWriter, so you may instead copy the entire source to a suiteable location
yourself.


Step 3: Create Launcher Icons
-----------------------------

Regardless of where you extract or install the source files, you can set up a standard icon and a
launcher. To set up this desktop launcher, the needed icons, and the project file association,
run the following from inside the novelWriter folder at the installed or final location:

.. code-block:: console

   ./setup.py xdg-install

By default, this command installs the launcher and icons for the current user only. To install for
all users, run the script with the ``sudo`` command.

.. tip::
   All options of the setup script can be listed with: ``./setup.py help``.


Uninstalling Icons
==================

The steps taken by the ``xdg-install`` step can be reversed by running:

.. code-block:: console

   ./setup.py xdg-uninstall

This will remove the desktop launcher and icons from the system. As above, whether this is done on
the current user, or system wide, depends on whether this command is called with ``sudo`` or not.
