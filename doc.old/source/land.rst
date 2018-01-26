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

Ta generelt :math:`u_{i+1/2}` = 0 => partikler krysser ikke kysten

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

[Justere litt under, korrigere for q i stedet for x]
For the second order Runge-Kutta also known as the Heun method or the
trapezoidal method we have

.. math:: x^{*} = x + u(x) \Delta t, \quad 
          x^{+} = x + 0.5*(u(x) + u(x^{*})) \Delta t

if :math:`c < 1` then :math:`u(x^{*}) \Delta t = -x(1 - c)` giving

Euler Forward

.. math:: \lambda = 1 - c, \quad c < 1

Runge-Kutta 2nd order (Heun)

.. math:: \lambda = 1 - c + \frac{c^2}{2}, \quad c < 1 \\
          \lambda = 1 - \frac{c}{2},          \quad 1 < c < 2

Midpoint scheme (2 order)

.. math:: \lambda = 1 - c + \frac{c^2}{2}, \quad c < 1 \\
          \lambda = 1, \quad c > 1


Runge-Kutta 4th order

.. math:: \lambda = 1 - c + \frac{c^2}{2} - \frac{c^3}{6}
                       + \frac{c^4/24}, \quad c < c_0 \\
          \lambda = 1 - \frac{5}{6}c + \frac{c^2}{3} - \frac{c^3}{12},
                                      \quad c_0 < c < 2

Where :math:`c_0 \approx 1.2956` is the real root of the polynomial
:math:`4 - 4c + 2c^2 + c^3`.
