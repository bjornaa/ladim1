:mod:`gridforce` --- Ladim Module for Grid and Forcing
======================================================

.. module:: gridforce
   :synopsis: LADIM module for grid and forcing

.. default-domain:: py

This module describes the grid used for particle tracking and interfaces the
forcing from the ocean model. This is the only module in LADIM that depends
on the model. Interfacing other models is done by adding an alternative
gridforce module. The module :mod:`gridforce_ROMS` implements a ROMS interface.
The obstacle example shows how to make a simple gridforce module in idealized
cases.

Coordinate system in LADIM
--------------------------

The coordinate system should be curvilinear orthogonal. Grids as used by
ROMS for instance are suitable. The coordinates should have integer values at
the grid cell centers. [Necessary, or a detail left to the implementation?]
Particle release and movements is referred to this coordinate system.

The grid spacing is given by horizontal arrays of metric coefficients
:math:`\Delta x` and :math:`\Delta y`
(sjekk at de brukes rett).

The vertical coordinate system is simply the depth in meters, with positive
values downwards.

:class:`Grid`
-------------

.. class:: Grid(config)

   The argument config is a :class:`Configuration` object

   The grid is defined by the Grid class having the following public
   attributes:

   .. attribute:: imax

      The number of grid cells in X-direction.

   .. attribute:: jmax

      The number of grid cells in Y direction.

   And a set of methods, taking the particle positions as input:

   .. method:: metric(X, Y)

      Returns :math:`\Delta x` and  :math:`\Delta y` at the positions.

   .. method:: sample_depth(X, Y)

      Returns the depth at the positions.

   .. method:: lonlat(X, Y)

      Returns longitude and latitude at the positions [degrees].

   .. method:: ingrid(X, Y)

      Check if the particles are inside the grid.

   .. method:: atsea(X, Y)

      Check if the particles are at sea (not on land).



:class:`Forcing`
-----------------

The :class:`Forcing` class  provides the current from the
ocean model simulation that drives the particle tracking. It also includes
extra fields necessary for the (biological) behaviour (the IBMs).

.. class:: Forcing(config, grid)

   The arguments config and grid are :class:`Configuration` and :class:`Grid` objects.


   A forcing object should have the following public attributes and methods:

   .. attribute:: Forcing.step

       List of timesteps where forcing is available

   .. method:: Forcing.velocity(X, Y, Z, tstep=0)

      Returns velocity (U, V) in the particle positions.
      tstep is a fraction of the time step ahead,
      0 for present, 1 for next timestep, 0.5 for half way between.

   .. method:: Forcing.field(X, Y, Z, name)

      Sample a field, name is the name of the field in the state and ibm modules
      Examples: 'temp', 'salt', ...

   .. method:: Forcing.W(X, Y, Z)

      Vertical velocity at particle positions [Not implemented yet]
