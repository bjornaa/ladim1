:mod:`output` --- NetCDF output of particle distributions
=========================================================

.. module:: output
   :synopsis: NetCDF output of particle distributions

The :class:`OutPut` class is responsible for the NetCDF output from the
simulation. Initially it defines the NetCDF output file. It is used
sequentially, saving the selected part of the state at regular intervals.

.. class:: OutPut(config)

   The class has two methods:

   .. method:: write(state)

      Saves the selected state variables.

   .. method:: write_particle_variables(release)

      Writes the selected particle variables.

Here particle variables are things like, ``release time``,
``release position``, that belongs to a particle and does not change with time.

Note that the ``pid`` is by definition a particle variable, but it is
used as an instance variable to identify the particle of an instance.
It works as the index of the particle variables.
