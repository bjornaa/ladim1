Running LADiM
=============

Trying LADiM
------------

With LADiM installed, it is time to test it out.

Go to the examples directory, first :file:`examples/data` and
download an example data file :file:`ocean_avg_0014.nc` by the command::

  python download.py

Change to one of the other example directories, for instance :file:`examples/line` and run::

  python make_release.py
  ladim

Look at the results by::

  python animate.py

Note, depending on your python installation you may have to substitute python3
for python in the examples above.

After browsing through the configuration and particle release chapters below,
you can copy the example directory anywhere and modify with other release
scenarios or perhaps a ROMS' history or average file of your own.

The main ladim script
---------------------

Installing LADiM puts the main :program:`ladim` script on the PATH. It provides the command::

  ladim [-h] [-d] [-s] [config_file]

.. program:: ladim

The options are:

.. option:: -h, --help

   Show a help message and exit

.. option:: -d, --debug

   Show more logging information

.. option:: -s, --silent

   Show less logging information

.. option:: config_file

   Name of optional configuration file, default = :file:`ladim.yaml`

Running LADiM from python
-------------------------

LADiM can be run inside a python program. This is done by::

  import ladim
  #  ... more lines ...
  with open('ladim.yaml') as fid:
      ladim.main(config_stream=fid)

The main LADiM script, :file:`scripts/ladim`, uses this approach.The
:file:`jupyter` example shows how to use this with a triple quoted text string
for the configuration, using the standard module :mod:`StringIO`.