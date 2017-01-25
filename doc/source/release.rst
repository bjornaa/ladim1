Particle release
================

Particle release is controlled by a release file.
This is a text file with one row per release location
per time. The name of the release file is defined in the configuration file.

The line has the following format with whitespace as delimiter::

   mult release_time X Y Z + any additional fields

mult
  the number of particles released in the event.
release_time
   should have the format yyyy-mm-ddThh:mm:ss.
   The time format follows the `ISO 8601 standard <https://xkcd.com/1179>`_.
   The second and minutes can be dropped, but the `T` is essential.
   An alternative format, dropping the `T` is "yyyy-mm-dd hh:mm:ss"
   with double quotes.
X
  grid X-coordinate of the release position
Y
  grid Y-coordinate of the release position
Z
  release depth in meters (positive downwards)

The additional variables should be specified in the configuration file.
Unspecified data in the row is ignored (check)

Example::

  1 1989-05-24T12  68.117  94.989    5.0

Ta lakselus-eksempel med flere felt.


Additional fields such as the number of superindividuals,
an identifier for the release location, .... must be defined
in the configuration file.

Remarks:

For continuous release, every hour for instance, the file can be large.
A 42 days simulation with 1000 sources gives approximately 1 million rows.
It is recommended to use preprossing scripts to make these files.
Alternatively a better format might be developed.

For time the point is that the clock part should not be interpreted as
the X-coordinate. An alternative would be to use a comma-separated format (csv)
