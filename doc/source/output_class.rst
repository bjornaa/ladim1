Output module
=============

The output Class is responsible for the NetCDF output from the
simulation. It is used sequentually, saving the selected part of
the state at regular intervals.

Initially it defines the NetCDF output file.

It has two methods:

  - write(state): Writes the selected state variables to file
  - write_particle_variables(release): Writes particle variables

Here particle variables are things like, release time, release position,
that does not change with time.

Note that the pid is by definition a particle variable, but it is
used as a state variable to identify the particle of an instance.
It works as the index of the particle variables.
