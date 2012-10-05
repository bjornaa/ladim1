Land treatment
==============

For this chapter it is assumed that the velocity is given on a
rectangular grid with (possible varying) grid size :math:`\Delta x` and
:math:`\Delta y`. Further it is assumed that we are on an Arakawa
C-grid, i.e. the velocities are given at the sides of the grid
rectangles. In the following :math:`x, y` are grid coordinates,
i.e. the center of grid cell (i,j) has coordinates :math:`x=i, y=j`.

Land is given by a mask, defining a grid cell to be either at land or
at sea. All velocity components to and from a land cell is assumed to
be zero.

Advection
---------

Suppose we are in a grid cell (i,j) and that grid cell (i+1,j) is
land. Then :math:`u_{i+1/2} = 0` and denote :math:`u = u_{i-1/2}`.
Define a local Courant number :math:`c = u\Delta t/\Delta x`.

Ta generelt u_{i+1/2} = 0 => partikler krysser ikke kysten

If the velocity is constant in time and linear interpolation is used
in space to estimate the velocity, then the differential equation is

.. math:: \dot{x} = \frac{u}{\Delta x}(i+1/2-x)
with solution

.. math:: x(t) = i + \frac{1}{2} 
      - \left( i + \frac{1}{2} - x_0 \right) e^{-\frac{u t}{\Delta x}} .


For the simplest case, use the Euler-forward method with linear
interpolation. Let :math:`q = i + 1/2 - x` be the relative distance
from land in the x-direction. This method gives the new x-position

.. math:: x^{+} = x + q c < x + q = i + \frac{1}{2} .
In particular, if :math:`c < 1`, the particle will not reach land
during the next time step. If the condition :math:`0 < c < 1`
continues to hold, the particle position will converge to the coast
:math:`x = i + 1/2`, but will never cross the boundary.

Higher order methods can be analyzed and will generally give better
results, as they used prediction velocities closer to zero.
[Sjekk Heun = 2order Runge-Kutta, sjekk 4th order]
[Bedre? Høyere orden kontra firste orden og kortere tidsteg]




