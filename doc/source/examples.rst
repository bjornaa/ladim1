Examples
========

LADiM comes with a set of examples that try to illustrate different features.
They are available in the directory :file:`ladim/examples`. Most examples use
an example NetCDF file :file:`ocean_avg_0014.nc` from ROMS to be put in
``ladim/examples/data``. This directory contains a script :file:`download.py`
that downloads the file from an ftp server at IMR.

Most of the examples are executed by the command sequence::

  python make_release.py
  ladim
  python animate.py

Alphabetic list of examples:

:file:`jupyter`
  The jupyter example shows how to wrap a LADiM session in a jupyter notebook,
  and how to animate the model results. It is a remake of the ``line`` example.

:file:`killer`
  This is a modified version of the ``streak`` example. It demonstrates how to
  include a simple Individual Based Model (IBM). Particles are released
  continuously from a point and are "killed" at the age of two days.

:file:`latlon`
  The latlon example shows how to release particles at positions given in
  geographical coordinates and how to get longitude and latitude into the
  output file. It also shows how to visualize the results on a map using the
  mapping extensions  :mod:`basemap` and :mod:`cartopy` to :mod:`matplotlib`.

:file:`line`
  This is the basic example. Particles are released instantaneously from a line
  across the North Sea from Scotland to Norway. The particle distribution is
  followed for a period twelve days.

:file:`logo`
  This example generates the LADiM logo. The text LADiM is written with
  particles in the North Sea and deformed by the current for six days.

:file:`nested`
  This examples shows how use two nested model grids and let particles move
  between them. This is done by a separate ``gridforce`` module that calls the
  gridforce for each of the two grids.

:file:`obstacle`
  This example shows how to include your own gridforce module, and how to run
  an analytically defined simulation. Here, flow around a semi-circular
  peninsula (classical inviscid flow around a cylinder).

:file:`restart`
  This example shows how to split the LADiM results into files of limited
  number of time frames, and how to restart a LADiM run from an output file.

:file:`station`
  This example demonstrates transport from a single location at different
  depths.

:file:`streak`
  This example demonstrates a streak line, continuous release of particles from
  a fixed location.