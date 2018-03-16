Post processing
===============

LADiM comes with a simple python package postladim that can be used
for visualisation and analysis of LADiM output.

The basic class is postladim.ParticleFile it is initiated
by the following lines::

  from postladim import ParticleFile
  ...
  pf = ParticleFile('ladim-output.nc')


.. class:: ParticleFile(particle_file)

   It has the following **attributes**:

  .. attribute:: nc

     The underlying netCDF4 Dataset.

  .. attribute:: num_times

     Number of time frames in the file.

  .. attribute:: variables

     Dictionary of variables

  .. attribute:: instance_variables

     List of particle instance variables

  .. attribute:: particle_variables

     List of particle variables.

  .. method:: time(n)

     Timestamp (yyyy-mm-hh hh:mm:ss) of the n-th time frame.

  .. method:: particle_count(n)

     Number of particles at n-th time frame.

  .. method:: position(n)

     Position (X and Y) of particle-distribution at n-th time time.
     pf.position(n) = (pf.variables['X'][n], pf.variables['Y'][n])

**Item notation** with pf as a ParticleFile instance:

- name = instance variable

  - pf.variables[name][n] returns values at time frame n

- name = particle variable

  - pf.variables[name][pid] returns the particle variable value
