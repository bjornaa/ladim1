LADIM aka LADIM3 aka pyladim 
============================

This is a developing new version of
the Lagrangian Advection and DIffusion Model.
It is an off-line particle tracking code using results
from the ocean model `ROMS <http://www.myroms.org/>`_ as input.

Try out pyladim
---------------

Presently the model depends on the package `roppy
<https://github.com/bjornaa/roppy>`_ for handling input from ROMS.

It also needs an example input data file. The example file used
is available::

  ftp://ftp.imr.no/bjorn/ladim-data/ocean_avg_0014.nc.gz

Gunzip and store it in ``ladim/input directory``-


Source code
-----------

The code is open source using the MIT License. It is available from
`github<https://github.com/bjornaa/ladim>`_

::

  Bjørn Ådlandsvik <bjorn@imr.no>
  Institute of Marine Research
  Bergen, Norway

