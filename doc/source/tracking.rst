Particle tracking
=================

Advection
---------

Given a grid with coordinates x and y in the horizontal, z in the
vertical and a time-dependent velocity field 
given by :math:`U = U(x,y,z,t)` and :math:`V = V(x,y,z,t)`.

The Eulerian description of advection is the partial differential
equation

.. math:: \frac{\partial \phi}{\partial t} 
             + \frac{\partial(U \phi)}{\partial x} 
             + \frac{\partial(V \phi)}{\partial y} = 0

[Er konserveringsform mer korrekt for 2D hvor det kan være
konvergens??]

The Lagrangian particle description is the system of ordinary
differential equations

.. math:: \frac{d X}{d t} = U(X(t), Y(t), z, t) \quad
          \frac{d Y}{d t} = V(X(t), Y(t), z, t)

[characteristic curves]

Coordinate systems
------------------

Let :math:`x,  y` be an *orthogonal* curvilinear coordinate system for
an ocean domain, with a metric given as

.. math:: g = 
       \frac{1}{m^2} dx \otimes dx
     + \frac{1}{n^2} dy \otimes dy

With a given velocity field :math:`\vec{U}` with components
:math:`u, v`.



As an example, the longitude-latitude system is given by
longitude :math:`x = \lambda` and latitude :math:`y = \phi`
in radians. This is an ortogonal system with metric terms

.. math:: m = \frac{1}{R \cos \phi} \quad n = \frac{1}{R}

The particle tracking is given by

.. math:: \dot{x} = m u \quad \dot{y} = n v

Correction if given in degrees.

