Release module
==============

During initialization, this class has the responsibility to
warn about any mismatches in timing between the simulation
and particle release.

The total number of particles that will be involved in the
simulation is computed up-front and exported to the configuration
as config.total_particle_count.

Public attributes are: [need only one of these]

  - release_steps: List of time steps with particle release.
  - release_times: Timestrings of particle release times

It is implemented as an iterator. The __next__ method,
returns a dictionary of release information to be used by
the State class' append method.
