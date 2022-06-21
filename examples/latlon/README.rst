=========================
Geographical coordinates
=========================

This is example demonstrates the use of geographical coordinates with
``LADiM``. A line of particles is released along the 59° parallel from Scotland
to Norway.

To accept geographical coordinates in the release file, the configuration file
should use the reserved terms "lon" and "lat" instead of "X" and "Y" in the
variables list under the particle_release handle.

For output, the ``ladim1.yaml`` file shows how to write longitude and latitude.
Basically, add "lon" and "lat" to the list of output instance variables and
make sure they have the necessary arguments.

The plot scripts, ``plot_basemap.py`` and ``plot_cartopy.py``, demonstrates
ways of plotting the particle distributions in these mapping packages for
``matplotlib``.

The plotting above is slow. This is mainly due to the time used in handling the
intermediate resolution coast line. This may be speeded up several times by
using a pre-made coast line. The script ``make_coast.py`` uses ``basemap`` to
extract the coast line and saves it to ``coast.npy``. The new scripts
``plot2_basemap.py`` and ``plot2_cartopy.py`` are then several times faster.