:mod:`release` --- Particle release
===================================

.. module:: release
   :synopsis: Release of new particles

During initialization, the :class:`ParticleRelease` class has the
responsibility to warn about any mismatches in timing between the simulation
and particle release.

.. class:: ParticleRelease(config)

   Public attributes are: [need only one of these]

  .. attribute:: steps

     List of time steps with particle release.

  .. attribute:: total_particle_count

     The total number of particles in the simulation

  .. attribute:: particle_variables

     Dictionary with particle variables and their values

It is implemented as an iterator. The :meth:`__next__` method,
returns a dictionary of release information to be used by
the State class' append method.
