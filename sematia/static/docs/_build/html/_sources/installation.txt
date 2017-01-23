############
Installation
############

.. note::

   These instructions have only been tested on Mac OS X and Linux.

If you wish to install Sematia in a local environment, please follow these instructions. **For typical use, Sematia does not have to be installed but can be used on http://sematia.hum.helsinki.fi instead.**

Sematia is running on `Flask <http://flask.pocoo.org>`_, a Python microframework. To install Flask and Sematia, you need an up-to-date Python 3.5 installation (Sematia doesn't support Python 2). Sematia also requires a working MySQL (or MariaDB) installation.

First, create the virtual environment:

.. code-block:: shell

   $ virtualenv  ~/Virtualenvs/sematia

   $ source venv/bin/activate

The `Sematia source is available at GitHub <https://github.com/ezhenrik/sematia/>`_. Clone the repository and edit the config.py file according to your system configuration.

Then, start Sematia with the following command:

.. code-block:: shell

   $ python run.py

Sematia will now be running on http://localhost:5000.