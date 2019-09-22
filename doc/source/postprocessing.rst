Post processing
===============

Tutorial
--------

LADiM comes with a simple python package ``postladim`` that can be used for
visualisation and analysis of LADiM output. It is based on the `xarray <http://xarray.pydata.org/en/stable>` package. The full API is desctibed in :mod:`postladim`.

Here we will look on the output in examples/line. Start by opening the output file::

  from postladim import ParticleFile
  pf = ParticleFile('line.nc')

We can get some overview of the file content