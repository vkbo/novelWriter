.. _a_started:

**********************
Setup and Installation
**********************

.. _Enchant: http://rrthomas.github.io/enchant/
.. _GitHub: https://github.com/vkbo/novelWriter
.. _Downloads page: https://download.novelwriter.io
.. _PPA: https://launchpad.net/~vkbo/+archive/ubuntu/novelwriter
.. _Pre-Release PPA: https://launchpad.net/~vkbo/+archive/ubuntu/novelwriter-pre
.. _PyPi: https://pypi.org/project/novelWriter/
.. _python.org: https://www.python.org/downloads/
.. _Releases: https://github.com/vkbo/novelWriter/releases
.. _AppImage: https://appimage.org/

Ready-made packages and installers for novelWriter are available for all major platforms, including
Linux, Windows and MacOS, from the `Downloads page`_. See below for additional install instructions
for each platform.

You can also install novelWriter from the Python Package Index (PyPi_). See :ref:`a_started_pip`.
Installing from PyPi does not set up icon launchers, so you will either have to do this yourself,
or start novelWriter from the command line.

Spell checking in novelWriter is provided by a third party library called Enchant_. Generally, it
should pull dictionaries from your operating system automatically. However, on Windows they must be
installed manually. See :ref:`a_custom_dict` for more details.


.. _a_started_windows:

Installing on Windows
=====================

You can install novelWriter with both Python and library dependencies embedded using the Windows
Installer (setup.exe) file from the `Downloads page`_, or from the Releases_ page on GitHub_.
Installing it should be straightforward.

If you have any issues, try uninstalling the previous version and making a fresh install. If you
already had a version installed via a different method, you should uninstall that first as having
multiple installations has been known to cause problems.


.. _a_started_linux:

Installing on Linux
===================

A Debian package can be downloaded from the `Downloads page`_, or from the Releases_ page on
GitHub_. This package should work on both Debian, Ubuntu and Linux Mint, at least.

If you prefer, you can also add the novelWriter repository on Launchpad to your package manager.
The Launchpad packages `are signed by the author <https://launchpad.net/~vkbo>`__.


Ubuntu
------

You can add the Ubuntu PPA_ and install novelWriter with the following commands.

.. code-block:: bash

   sudo add-apt-repository ppa:vkbo/novelwriter
   sudo apt update
   sudo apt install novelwriter

If you want the `Pre-Release PPA`_ instead, add the ``ppa:vkbo/novelwriter-pre`` repository.


Debian and Mint
---------------

Since this is a pure Python package, the Launchpad PPA can in principle also be used on Debian or
Mint. However, the above command will fail to add the signing key, as it is Ubuntu-specific.

Instead, run the following commands to add the repository and key:

.. code-block:: bash

   sudo gpg --no-default-keyring --keyring /usr/share/keyrings/novelwriter-ppa-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys F19F1FCE50043114
   echo "deb [signed-by=/usr/share/keyrings/novelwriter-ppa-keyring.gpg] http://ppa.launchpad.net/vkbo/novelwriter/ubuntu noble main" | sudo tee /etc/apt/sources.list.d/novelwriter.list

Then run the update and install commands as for Ubuntu:

.. code-block:: bash

   sudo apt update
   sudo apt install novelwriter

.. tip::
   If you get an error message like ``gpg: failed to create temporary file`` when importing the key
   from the Ubuntu keyserver, try creating the folder it fails on, and import the key again:

   .. code-block:: bash

      sudo mkdir /root/.gnupg/


AppImage Releases
-----------------

For other Linux distros than the ones mentioned above, the primary option is AppImage_. These are
completely standalone images for the app that include the necessary environment to run novelWriter.
They can of course be run on any Linux distro, if you prefer this to native packages.

.. note::
   novelWriter generally doesn't support Python versions that have reached end of life. If your
   Linux distro still uses older Python versions and novelWriter won't run, you may want to try the
   AppImage instead.


.. _a_started_macos:

Installing on MacOS
===================

You can install novelWriter with both its Python and library dependencies embedded using the DMG
application image file from the `Downloads page`_, or from the Releases_ page on GitHub_.
Installing it should be straightforward.

* Download the DMG file and open it. Then drag the novelWriter icon to the :guilabel:`Applications`
  folder on the right. This will install it into your :guilabel:`Applications`.
* The first time you try to launch it, it will say that the bundle cannot be verified, simply press
  the :guilabel:`Open` button to add an exception.
* If you are not presented with an :guilabel:`Open` button in the dialog, launch the application
  again by right clicking on the application in Finder and selecting :guilabel:`Open` from the
  context menu.

The context menu can also be accessed by option-clicking if you have a one button mouse. This is
done by holding down the option key on your keyboard and clicking on the application in Finder.

.. note::
   The novelWriter DMG is not signed because Apple doesn't currently provide a way for non-profit
   open source projects to properly sign their installers. The novelWriter project doesn't have the
   funding to pay for a commercial software signing certificate.


.. _a_started_pip:

Installing from PyPi
====================

novelWriter is also available on the Python Package Index, or PyPi_. This install method works on
all supported operating systems with a suitable Python environment.

To install from PyPi you must first have the ``python`` and ``pip`` commands available on your
system. You can download Python from `python.org`_. It is recommended that you install the latest
version. If you are on Windows, also make sure to select the "Add Python to PATH" option during
installation.

To install novelWriter from PyPi, use the following command:

.. code-block:: bash

   pip install novelwriter

To upgrade an existing installation, use:

.. code-block:: bash

   pip install --upgrade novelwriter

When installing via pip, novelWriter can be launched from command line with:

.. code-block:: bash

   novelwriter

Make sure the install location for pip is in your PATH variable. This is not always the case by
default, and then you may get a "Not Found" error when running the ``novelwriter`` command.
