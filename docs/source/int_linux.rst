.. _a_setup_linux:

**************
Setup on Linux
**************

.. _GitHub: https://github.com/vkbo/novelWriter/releases
.. _main website: https://novelwriter.io

This is a brief guide to how you can get novelWriter running on a Linux computer. There are
currently no packaged version of novelWriter for Linux, so it is recommended that you just extract
the source to a practical location on your system and run the ``setup.py`` script.


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

You can install novelWriter to the correct location for Python packages with:

.. code-block:: console

   ./setup.py install

This is equivalent to what the ``pip`` installer does. It puts novelWriter in the location on your
system where Python packages are usually kept. This is not really the best suited location for a
GUI application like novelWriter, so you may instead copy the entire source to a suiteable location
yourself.

By default, this command installs novelWriter for the current user only. To install for all users,
run the script with the ``sudo`` command.

This should install novelWriter to either ``~/.local/bin/novelWriter`` if installed for local user
only, or to ``/usr/local/bin/novelWriter`` if installed for all users.


Step 3: Create Launcher Icons
-----------------------------

To set up the novelWriter desktop launcher, the icons, and the project file association, run:

.. code-block:: console

   ./setup.py xdg-install

By default, these commands install novelWriter and its icons for the current user only. To install
for all users, run the script with the ``sudo`` command.

.. tip::
   All options of the setup script can be listed with: ``./setup.py help``.
