.. _postladim:

Post processing
===============

LADiM comes with a simple python package ``postladim`` that can be used for
visualisation and analysis of LADiM output. It is based on the ``xarray`` package
http://xarray.pydata.org/en/stable/.


Usage
-----

The basic class is ``ParticleFile`` giving access to the content
of a LADiM output file.

.. code-block:: python

    from postladim import ParticleFile
    pf = ParticleFile("output.nc")

The ``ds`` method shows the underlying xarray Dataset, which is useful for a quick
overview of the content and for more advenced data processing.

The time at a given time step n is given by:

.. code-block:: python

  pf.time[n]

The output may be a bit verbose, ``pf.time(n)`` is syntactic sugar for the more concise``pf.time[n].values``.

The number of particles at time step n is given by:

.. code-block:: python

  pf.count[n]

For use in indexing ``pf.count`` is an integer array instead of an xarray DataArray.
The DataArray is avaiable as ``pf.ds.particle_count``.

Following pandas and xarray, an instance variable, like X,  is given both by
attribute ``pf.X`` and item ``pf['X']`` notation. The NetCDF inspired notation
``pf.variables['X']`` is obsolete.

The most basic operation for an instance variable is to get the values at time step n as
a xarray DataArray:

.. code-block:: python

  pf.X[n]

An alternative notation is ``pf.X.isel(time=n)``. The time stamp can be used instead of
the time index:

.. code-block:: python

  pf.X.sel(time='2020-02-05 12')

The format is optimized for particle distributions at a given time. Trajectories and
other time series for a given particle may take longer time to extract. For the particle
with identifier `pid=p`, the X-coordinate of the trajectory is given
by:

.. code-block:: python

  pf.X.sel(pid=p)

If many trajectories are needed, it may be useful to turn the dataset into a full (i.e.
non-sparse) 2D DataArray, indexed by time and particle identifier.

.. code-block:: python

  pf.X.full()

Note that for long simulations with particles of limited life span, this array may
become much larger than the ParticleFile.



Reference
---------

ParticleFile
............

.. class:: ParticleFile(particle_file)

   Class for LADiM result files.

  .. attribute:: ds

     The underlying xarray Dataset.

  .. attribute:: num_times

     Number of time frames in the file.

.. attribute:: num_particles

    The number of distinct particles

  .. attribute:: count

     Integer numpy ndarray of particle counts at different time steps

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

     Tuple with position (X, Y) of particle-distribution at n-th time time,
     ``pf.position(n) = (pf.X[n], pf.Y[n])``

  .. method:: trajectory(pid)

     Returns a tuple of X and Y coordinates of the particle with identifier pid,
     ``trajectory(pid) = (pf.X.sel(pid=pid), pf.Y.sel(pid=pid))``.

  .. attribute:: variables

     Deprecated, dictionary of variables, ``pf.variables['X'] = pf['X'] = pf.X``.

  .. method:: time(n)

     Syntactic sugar, ``pf.time(n) = pf.time[n].values``

  .. method:: particle_count(n)

     Deprecated, ``pf.particle_count(n) = pf.count[n]``

InstanceVariable
................

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

    Select by time index, ``V.isel(time=n) = V[n]``.

  .. method:: sel(time=t, pid=p)

    Select by time value and/or pid value

    ``V.sel(time='2019-09-19 12')`` selects particles at that time value
    ``V.sel(pid=23)`` selects the time history of particle with that pid value
    ``V.sel(time='2019-09-19 12', pid=23)`` selects the unique particle instance

  .. method:: full()

     Return the full (non-sparse) 2D DataArray. May become vary large.



The InstanceVariable class support item notation:

.. code-block:: `python`

  V[n] = V.isel(time=n)
  V[n, p] = V.isel(time=n).sel(pid=p)

Note that ``V[n, p]`` may be different from ``V[n][p]`` if particles have been removed.

The `length` of an instance variable is the number of time steps,
``len(V) == len(V.time)``.

ParticleVariable
................

.. class:: ParticleVariable

This class represents a variable that depends on the particle, but is independent of
time.

  .. attribute:: da

  Underlying xarray DataArray

Supports item notation::

  ``V[p]`` is value of particle with ``pid = p``.
