Installation
============

If you are lucky LADIM is already installed at your system.
This can be tested by writing ladim on the command line.
If it is installed you will get the reply::
  
  Starting LADIM
   --- pyladim configuration ----
  ERROR - Configuration file ladim.yaml not found

If it is not installed, or the system version is old, you can
make a private install under your oser.

TODO: Implement version information as ladim --version

Private LADIM installation
--------------------------

If you do not have system-wide permissions you can install LADIM
under your own user.

First make sure that you are using python 3.x, by typing python::

  Python 3.5.2 |Anaconda custom (64-bit)| (default, Jul  2 2016, 17:53:06)
  [GCC 4.4.7 20120313 (Red Hat 4.4.7-1)] on linux
  Type "help", "copyright", "credits" or "license" for more information.
   >>>

The python version is the first number. If it is 2.7.x or less you are
running legacy python. Try the command python3, or on an anaconda system you
can change to version 3 by source activate python3 or similar

LADIM is hosted on github, https://github.com/bjornaa/ladim download by the
command::

  git clone https://github.com/bjornaa/ladim.git

if you don't have git installed download the zip-file from the LADIM site above.

This makes a ladim directory under the present directory.

Now install LADIM locally::

  cd ladim
  python3 setup.py install --prefix=/home/user

Make sure /home/user/bin is in your PATH. If you want to override a system
LADIM it has to go before python's own bin directory (check: which python3).
Sjekk opp hva som gjøres med PYTHONPATH.

And you are ready to try out LADIM.
