Particle release
================

Particle release is controlled by a release file.
This is a text file with one row per release location
per time. The name of the release file is defined in the configuration file.

The format of the line is specified in the configuration by the list
``release_format``. If the type of the field is not the default  ``float``, it
should be specified under the ``particle_release`` heading in the configuration
file. Time is indicated by the type code ``time``.

The line has the following mandatory fields:

release_time

   Should have the format yyyy-mm-ddThh:mm:ss or "yyyy-mm-dd hh:mm:ss".
   The time format follows the `ISO 8601 standard <https://xkcd.com/1179>`_.
   Time components can be dropped from the end with obvious defaults.
   It is essential that the time is interpreted as a **single string**, either
   by joining with a "T" or enclosing with double ticks.

X
  Grid X-coordinate of the release position
Y
  Grid Y-coordinate of the release position
Z
  Release depth in meters (positive downwards)

In addition the field ``mult`` is reserved. If present it gives the
multiplicity of the line, for release of several particles at the
same time and position. If ``mult`` is omitted, a default value of 1, single
particle, is used.

The additional variables should be specified in the configuration file.
Unspecified data in the row is ignored (check)

Example::

  3 1989-05-24T12  68.117  94.989    5.0

Ta lakselus-eksempel med flere felt.

Additional fields such as the number of superindividuals,
an identifier for the release location, .... must be defined
in the configuration file.

Remarks:

For continuous release, every hour for instance, the file can be large.
A 42 days simulation with 1000 sources gives approximately 1 million rows.
It is recommended to use preprocessing scripts to make these files.
Alternatively a better format might be developed.

For time the point is that the clock part should not be interpreted as
the X-coordinate. An alternative would be to use a comma-separated format (csv).

Entries with release_time before the start or after the stop time of LADiM are
ignorered. In particular, constant continuous release will not work if the
release_time is before the models start time. Strange things may happen if
particle release is not aligned with the model time stepping.
The user is presently responsible for syncronizing model and release times.


.. seealso::
  Module :mod:`release`
    Documentation of the :mod:`release` module
