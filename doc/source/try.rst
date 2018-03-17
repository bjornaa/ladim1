Try LADiM
=========

With LADiM installed, it is time to test it out.

Go to the examples directory, first examples/data and
follow the instructions in the README file to download
the file ocean_avg_0014.nc

Change to one of the other example directories, run::

  python make_release.py
  ladim

Look at the results by::

  python animate.py

Note, you may have to substitute python3 for python in the
examples above.

After browsing through the configuration and particle release chapters below,
you can copy the example directory anywhere and modify with other release
scenarios or perhaps a ROMS' history or average file of your own.
