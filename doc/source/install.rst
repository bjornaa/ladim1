.. index:: installation

.. _installation:

Installation
============

If you are lucky LADiM is already installed at your system. This can be tested
by writing :program:`ladim -h` on the command line. If it is installed, you
will get some help text. If it is not installed, or the system version is old,
you can make a private install under your user.

TODO: Implement version information as ``ladim --version``

Private LADiM installation
--------------------------

If you do not have system-wide permissions you can install LADiM under your own
user.

First make sure that you are using python 3.6 or more, by typing :program:`python`::

  Python 3.6.5 |Anaconda custom (64-bit)| (default, Mar 29 2018, 18:21:58)
  [GCC 7.2.0] on linux
  Type "help", "copyright", "credits" or "license" for more information.
  >>>

The python version is the first number. If it is 2.7.x or less you are running
legacy python. Try the command :program:`python3`, or on an anaconda system you
can change to version 3.6 by ``source activate py36`` or similar.

If you do not have python 3.6 on your machine, the `anaconda <https://www.anaconda.com/distribution/>`_ distribution is recommended.          |

LADiM is hosted on `github <https://github.com/bjornaa/ladim>`_, download by
the command::

  git clone https://github.com/bjornaa/ladim.git

if you don't have :program:`git` installed, download and unzip the zip-file
from the LADiM site above.

This makes a :file:`ladim` directory under the present directory.

Now install LADiM locally, user = your login name::

  cd ladim
  python setup.py install --prefix=/home/user

Make sure :file:`/home/user/bin` is in your :envvar:`PATH`. If you want to
override a system LADiM it has to go before python's own bin directory (check:
`which python[3]`). Also add :file:`/home/user/lib/python3.{x}/site-packages` to
the environment variable :envvar:`PYTHONPATH`, where :file:`{x}` is the minor python
version.

And you are ready to try out LADiM.
