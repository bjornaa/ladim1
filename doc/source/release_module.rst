:mod:`release` --- Particle release
===================================

.. module:: release
   :synopsis: Release of new particles

During initialization, the :class:`ParticleRelease` class has the responsibility to
warn about any mismatches in timing between the simulation
and particle release.

The total number of particles that will be involved in the
simulation is computed up-front and exported to the configuration
as config.total_particle_count.
[Do something better]

.. class:: ParticleRelease(config)

   Public attributes are: [need only one of these]

  .. attribute:: release_steps

     List of time steps with particle release.

  .. attribute:: release_times

     Timestrings of particle release times

It is implemented as an iterator. The :meth:`__next__` method,
returns a dictionary of release information to be used by
the State class' append method.
