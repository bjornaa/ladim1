=========================
Geographical coordinates
=========================

This is example demonstrates the use of geographical coordinates with
``LADiM``. A line of particles is released along the 59° parallel from Scotland
to Norway.

The ``make_release.py`` script uses the ROMS post-processing package,
``roppy``, to transfom longitude, latitude into the grid coordinates of the
example data file. The package ``roppy`` is available as
https://github.com/bjornaa/roppy. For demonstration, this step can be skipped
as the ``latlon.rls`` file is included. Future releases of ``LADiM`` may be
able to read longitude and latitude directly from the release file.

The ``ladim.yaml`` file shows how to get longitude and latitude of the
particles written into the output file. Basically, add "lon" and "lat" to the
list of output instance variables and make sure they have the necessary
arguments.

The plot scripts, ``plot_basemap.py`` and ``plot_cartopy.py``, demonstrates
ways of plotting the particle distributions in these mapping packages for
``matplotlib``.
