.. _a_setup_mac:

**************
Setup on macOS
**************

.. _GitHub: https://github.com/vkbo/novelWriter/releases
.. _main website: https://novelwriter.io
.. _brew docs: https://docs.brew.sh/Homebrew-and-Python

This is a brief guide to how you can get novelWriter running on macOS. There are currently no
install package of novelWriter for macOS, so it is recommended that you download either the full
source or minimal package and extract it to a practical location on your system and
run it.


Running from Source
===================

To run novelWriter from source, download the latest source package from the release page on
GitHub_ or the `main website`_, or if you have git running on your computer, you can also clone the
repository.


Step 1: Installing Dependencies
-------------------------------

These instructions assume you're using brew, and have Python and pip set up. If not, see the
`brew docs`_ for help. Main requirements are installed via the requirements file. You also need to
install the ``pyobjc`` package, so you should run:

.. code-block:: console

   pip3 install --user -r requirements.txt
   pip3 install --user pyobjc

For spell checking you may also need to install the enchant package. It comes with a lot of default
dictionaries.

.. code-block:: console

   brew install enchant

With the dependencies in place, you can launch the ``novelWriter.py`` script directly to run
novelWriter.


Step 2: Install Package (Optional)
----------------------------------

You can install novelWriter to the correct location for Python packages with:

.. code-block:: console

   ./setup.py install --user

This requires that the package ``setuptools`` is installed on your system. If not, it can be
installed with:

.. code-block:: console

   pip3 install --user setuptools

This is method of install is equivalent to what the ``pip`` installer does. It puts novelWriter in
the location on your system where Python packages are usually kept. This is not really the best
suited location for a GUI application like novelWriter, so you may instead copy the entire source
to a suiteable location yourself.

After this, you should be able to launch novelWriter by running ``novelWriter`` in a command line
window.

.. note::
   Right now there isn't a better integration with macOS available. Contributions from someone more
   familiar with macOS would be very much appreciated.
