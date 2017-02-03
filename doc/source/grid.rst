Grid module
===========

[document module or class?]

The grid module defines the coordinate system and provide methods for
interfacing the grid.

Horizontal coordinate system
----------------------------

The coordinate system should be curvilinear orthogonal. Grids as used by
ROMS for instance are suitable. The coordinates should have integer values at
the grid cell centers. [Necessary, or a detail left to the implementation?]

The grid spacing is given by metric coefficients :math:`\Delta x` and
:math:`\Delta y`
(sjekk at de brukes rett). For a ROMS grid these can be read from a
grid file as the inverses of pm amd pn.
For a lon/lat grid on a sphere they are given as

.. math:: \Delta x = R \cos \phi \Delta\lambda, \quad \Delta y = R \Delta\phi

where :math:`R` is the earth radius, :math:`\lambda` and :math:`\phi` are the
longitude and latitude in radians.

Vertical coordinate system
--------------------------

The vertical coordinate system is simply the depth in meters, with positive
values downwards.

Grid class
----------

The grid is defined by a class having the following public attributes and methods.

- imax, jmax Number of grid cells in X and Y direction (needed outside?)
- H: the bathymetry [meters]
- M: sea mask (= 1 at sea, = 0 at land)

A set of methods, taking positional arrays X, Y as input

- sample_metric(X, Y):  returns :math:`Delta x` and  :math:`Delta y`
 at the positions
- sample_depth(X, Y):  returns the depth at the positions
- lonlat(X, Y): returns lon/lat of positions [degrees]
- ingrid(X, Y): returns True for positions inside the grid
- atsea(X, Y): returns True for positions at sea (not on land)
