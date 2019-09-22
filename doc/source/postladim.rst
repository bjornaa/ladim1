Post processing
===============

Tutorial
--------

LADiM comes with a simple python package ``postladim`` that can be used for
visualisation and analysis of LADiM output. It is based on the ``xarray`` package
http://xarray.pydata.org/en/stable/.




Under reconstruction
--------------------



.. class:: InstanceVariable

  .. attribute:: da

    The underlying xarray DataArray

  .. attribute:: count

    Number of particles at given time

  .. attribute:: time

    The time steps

  .. attribute:: num_particles

    The number of distinct particles

  .. method:: isel(time=n)

    Select by time index, V.isel(time=n) = V[n]

  .. method:: sel(time=t, pid=p)

    Select by time value and/or pid value

    V.sel(time='2019-09-19 12') selects particles at that time value
    V.sel(pid=23) selects the time history of particle with that pid value
    V.sel(time='2019-09-19 12', pid=23) selects the unique particle instance

  .. method:: full()

     Return the full 2D DataArray. May become vary large.

The InstanceVariable class support item notation::

  V[n] = V.isel(time=n)
  V[n, p] = V.isel(time=n).sel(pid=p)

  len(V) == len(V.time) is the length of the time axis

Note that V[n, p] may be different from V[n][p] if particles have been removed.


.. class:: ParticleVariable

This class represents a variable that depends on the particle, but is independent of
time.

  .. attribute:: da

  Underlying xarray DataArray

Supports item notation::

  V[p] is value of particle with pid = p


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

  .. attribute:: count

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