Post processing
===============

LADiM comes with a simple python package ``postladim`` that can be used
for visualisation and analysis of LADiM output. It is based on the ``xarray`` package http://xarray.pydata.org/en/stable/.

The basic class is ``postladim.ParticleFile``, it is initiated
by the following lines::

  from postladim import ParticleFile
  ...
  pf = ParticleFile('ladim-output.nc')


.. class:: ParticleFile(particle_file)

   It has the following **attributes**:

  .. attribute:: ds

     The underlying xarray Dataset.

  .. attribute:: num_times

     Number of time frames in the file.

  .. attribure:: count

     Numpy ndarray of particle counts at different time steps

  .. attribute:: start

     ndarray of start indices at different time step

  .. attribute:: end

     ndarray of end indices, short hand for  pf.start + pf.count

  .. attribute:: instance_variables

     List of particle instance variables

  .. attribute:: particle_variables

     List of particle variables.

  .. attribute:: time

     xarray DataArray of time stamps

  .. method:: position(n)

     Tuple with position (X and Y) of particle-distribution at n-th time time.
     pf.position(n) = (pf['X'][n], pf['Y'][n])

  .. method:: trajectory(pid)

     Returns a tuple of X and Y coordinates of the particle with identifier pid.
     trajectory(pid) = (pf['X'].sel(pid=pid), pf['Y'].sel(pid=pid))

  .. attribute:: variables

     Deprecated, dictionary of variables, pf.variables['X'] = pf['X'] = pf.X

  .. method:: time(n)

     Deprecated, pf.time(n) = pf.time[n].values

  .. method:: particle_count(n)

     Deprecated, pf.particle_count(n) = pf.count[n]


.. class InstanceVariable

.. class ParticleVariable