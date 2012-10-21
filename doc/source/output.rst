Output format
=============

The particle distributions are written to netCDF files.

**Litt diskusjon om ulik tankegang for partikkelfordelinger

Different formats may be available in the future
(in particular ROMS float format)


LADIM format
------------

This is a modfication of the LADIM 2 format.
It is not backwards compatible, but scripts should be
easy to modify. The change is done to follow the CF-standard
as far as possible, and to increase flexibility.

The format is close to the format of "Indexed ragged array
representation of trajectories" as described in appendic H.4.4 in the
CF-documentation version 1.6.
http://cf-pcmdi.llnl.gov/documents/cf-conventions/1.6/cf-conventions.html#idp8399648
There are however modifications, as we are more interested in the distribution of
the particles at a fixed time than to follow the individual trajectories.

The dimensions are `time` and  `particle`. NetCDF 3 format allows only one unlimited
dimension. As the duration and output frequency are known at the start of a ladim simulation,
the particle dimension may be unlimited.
