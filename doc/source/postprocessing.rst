Post processing
===============

LADIM comes with a simple python package postladim that can be used
for visulisation and analysis of LADIM output.

The basic class is postladim.particlefile.ParticleFile it is initiated
by the following lines::

  from postladim.particlefile import ParticleFile
  ...
  pf = ParticleFile('ladim-output.nc')

It has the following **attributes**:

nc
  The underlying netCDF4 Dataset
num_times
  Number of time frames in the file
variables
  List of instance variables
particle_variables
  List of particle variables

And **methods**:

time(n)
  Timestamp (yyyy-mm-hh hh:mm:ss) of the n-th time frame
particle_count(n)
  Number of particles at n-th time frame
position(n)
  Position (X and Y) of particle-distibution at n-th time time

**Item notation** with pf as a ParticleFile instance:

- name = instance variable

  - pf[name, time_idx] returns values at time frame time_idx

  - pf[name, time_idx, i] shorthand for pf[name, time_idx][i]

- name = particle variable

  - pf[name] returns all values

  - pf[name, pid] is shorthand for pf[name][pid]

For example: pf.position(4) returns the tuple (pf['X', 4], pf['Y', 4])
