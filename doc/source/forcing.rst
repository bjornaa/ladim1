Forcing module
==============

The forcing module provides the current and other fields from the
ocean model simulation that drives the particle tracking.

The forcing class
-----------------

The main element is a forcing class having the following external attributes and
methods.

- step: List of timesteps where forcing is available
        [needed externally?]

Methods for sampling the forcing.

- sample_velocity(X, Y, Z, [tstep]):
     is a fraction of the time step ahead, default = 0 (sample now)
     = 1 means next time step, = 0.5 midway between time steps

- sample_field(X, Y, Z, name):
     Sample a field, name is the name of the field in the state and ibm modules
     Examples: 'temp', 'salt', ...

- sample_W(X, Y, Z): Sample vertical velocity [Ikke implemntert ennå]
