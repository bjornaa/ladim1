Particle release
================

Particle release is controlled by a release file.
This is a text file with one row per release location
per time. The name of the release file is defined in the configuration file.

The format of the line is specified in the configuration by the list
``release_format``. If the type of the field is not the default  ``float``, it
should be specified under the ``particle_release`` heading in the configuration
file. Time is indicated by the type code ``time``.

There are seven reserved column names.

mult
  Number of particles. Optional, default = 1.

release_time
  Time of particle release with format ``yyyy-mm-ddThh:mm:ss`` or ``"yyyy-mm-dd hh:mm:ss"``. Mandatory.

X
  Grid X-coordinate of the release position

Y
  Grid Y-coordinate of the release position

lon
  Longitude of release position

lat
  Latitute of release position

Z
  Release depth in meters (positive downwards). Mandatory

.. note::
  It is essential that the release time is interpreted as a *single string*.
  This can be done by a "T" between date and clock parts or by enclosing it with double ticks. Time components can be dropped from the end with obvious defaults.

.. note::
  Either (X, Y) or (lon, lat) must be given, If both are present, the grid position (X, Y) is used.

.. note::
  Using (lon, lat) requires a ``ll2xy`` method in the :class:`gridforce.Grid`.

Additional variables should be specified in the configuration file. If their type is not
``float``, the type (``int``, ``bool``, ``time``) should be specified. [How about strings?]

Example:

Using the configuration:

.. code-block:: yaml

  particle_release:
      # release_type, discrete or continuous
      release_type: continuous
      release_frequency: [1, h]   # Hourly release
      variables: [mult, release_time, X, Y, Z, farmid, super]
      particle_variables: [release_time, farmid]
      # Converters (if not float)
      mult: int
      release_time: time   # np.datetime64[s]
      farmid: int

A typical line in the release file may look like this:

.. code-block:: none

  5 2015-07-06T12 379.12 539.23 5.0 10041 1243.2

This means that 5 particles are released at time ``2015-07-06 12:00:00``, at a
location with ``farmid``-label 10041, with grid coordinates (379.12, 539.23) at
5 meters depth. Each particle is a superindividual with weight 1243.2 so the
particle release corresponds to a total of 6216 individuals. The release is
repeated every hour until a later particle release anywhere (or the end of the
simulation).

.. warning::
  Strange things may happen if particle release is not aligned with the model
  time stepping. The user is presently responsible for synchronizing model and
  release times.

.. note::
  Entries with release_time before the start or after the stop time of LADiM
  are ignored. In particular, constant continuous release will not work if the
  release_time is before the model's start time. (still true?)

.. note::
  Entries in a release row after the configured fields are silently ignored.
  (at least should be, check).

.. note::
  Particles released outside the model grid are ignored. A warning is logged.

.. note::
  Particles released on land are retained in the simulation, but do not move.
  In particular check that particles released by longitude and latitude near
  the coast is in a sea cell. TODO: Provide a warning for particles initially on land.

.. seealso::
  Module :mod:`release`
    Documentation of the :mod:`release` module
