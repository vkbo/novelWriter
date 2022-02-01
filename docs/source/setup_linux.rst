.. _a_setup_linux:

**************
Setup on Linux
**************

.. _GitHub: https://github.com/vkbo/novelWriter/releases
.. _main website: https://novelwriter.io
.. _PPA: https://launchpad.net/~vkbo/+archive/ubuntu/novelwriter
.. _Pre-Release PPA: https://launchpad.net/~vkbo/+archive/ubuntu/novelwriter-pre

This is a brief guide to how you can get novelWriter running on a Linux computer.

There are currently install packages available for Ubuntu and Debian. For other distros it is
recommended that you download either the full source or the minimal package and extract it to a
practical location on your system and run the ``setup.py`` script.


Debian-Based Distros
====================

A general Debian package can be downloaded from the `main website`_. This package should work on
both Debian, Ubuntu and Linux Mint.

If you prefer, you can also add the novelWriter repository on Launchpad to your package manager.


Ubuntu and Mint
---------------

You can add the Ubuntu PPA_ and install novelWriter with the following commands.

.. code-block:: bash

   sudo add-apt-repository ppa:vkbo/novelwriter
   sudo apt update
   sudo apt install novelwriter


Debian
------

Since this is a pure Python package, the Launchpad PPA can in principle also be used on Debian.
However, the above command will fail to add the signing key.

Instead, run the following commands to add the repository and key:

.. code-block:: bash

   sudo gpg --no-default-keyring --keyring /usr/share/keyrings/novelwriter-ppa-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys F19F1FCE50043114
   echo "deb [signed-by=/usr/share/keyrings/novelwriter-ppa-keyring.gpg] http://ppa.launchpad.net/vkbo/novelwriter/ubuntu focal main" | sudo tee /etc/apt/sources.list.d/novelwriter.list

Then run the update and install commands as for Ubuntu:

.. code-block:: bash

   sudo apt update
   sudo apt install novelwriter

.. note::

   Please use the Ubuntu 20.04 packages for Debian. The newer Ubuntu packages use a different
   compression that Debian doesn't currently support.


Pre-Releases
------------

There is also a `Pre-Release PPA`_ available with beta releases and release candidates of
novelWriter. For Ubuntu, run the following commands:

.. code-block:: bash

   sudo add-apt-repository ppa:vkbo/novelwriter-pre
   sudo apt update
   sudo apt install novelwriter


Minimal Zip File
================

A minimal zip file is provided for Linux. You can download the latest zip file from the release
page on GitHub_, or from the `main website`_. This zip file contains only the files actually needed
to run novelWriter, and none of the additional source files for tests and documentation. You can
extract the file to wherever you want, and run the steps below.


Step 1: Installing Dependencies
-------------------------------

The dependencies of novelWriter are generally available from Linux distro repositories. For Debian
and Ubuntu, they can be installed with:

.. code-block:: bash

   sudo apt install python3-pyqt5 python3-lxml python3-enchant

If you prefer to install dependencies via PyPi, or the repository dependencies are out of date, you
can install them with:

.. code-block:: bash

   pip3 install --user -r requirements.txt


Step 2: Create Launcher Icons
-----------------------------

A standard desktop launcher can be installed via the main setup script. It will create the needed
desktop file and add it to the Applications menu. The necessary icons will also be installed, and a
file association with ``.nwx`` files added.

To set this up, run the following from inside the novelWriter folder at the final location:

.. code-block:: bash

   python3 setup.py xdg-install

This will only install the launcher and icons for the current user. To set up novelWriter for all
users, run:

.. code-block:: bash

   sudo python3 setup.py xdg-install


Uninstalling Icons
------------------

The steps taken by the ``xdg-install`` step can be reversed by running:

.. code-block:: bash

   python3 setup.py xdg-uninstall

This will remove the desktop launcher and icons from the system. As above, whether this is done on
the current user, or system wide, depends on whether this command is called with ``sudo`` or not.
