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


  
