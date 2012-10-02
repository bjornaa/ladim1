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
an ocean domain, with a inner product or metric given by

.. math:: g = 
       \frac{1}{m^2} dx \otimes dx
     + \frac{1}{n^2} dy \otimes dy
The unit coordinate vectors are defined by

.. math:: 
   \vec{i} = \frac{1}{m} \nabla x = m \frac{\partial}{\partial x}, \quad
   \vec{j} = \frac{1}{n} \nabla y = n \frac{\partial}{\partial y}
Where vector fields has been identified with their directional
derivatives.

With a given velocity field :math:`\vec{U}` the components
:math:`u, v` are defined by

.. math:: 
    \vec U = u \vec i + v \vec{j}
or equivalently :math:`u = g(\vec{U},\vec{i})`, 
:math:`v = \langle \vec{U},\vec{j} \rangle`. These are *physical* components,
real velocities with units m/s. In contrast :math:`mu, nv` are the
time derivatives along a track in the :math:`x, y` system.

The gradient is given by

.. math:: 
  \nabla \phi = m \frac{\partial \phi}{\partial x} \vec{i}
              + n \frac{\partial \phi}{\partial y} \vec{j}
giving Eulerian advection equation

.. math::
  \frac{D\phi}{Dt}  
       = \frac{\partial \phi}{\partial t} 
             + \langle \vec{U}, \nabla \phi \rangle
       =  \frac{\partial \phi}{\partial t} 
             + m u \frac{\partial \phi}{\partial x}
             + n v \frac{\partial \phi}{\partial y}
      = 0

The Lagrangian advection is given by the system of ordinary
differential equations

.. math::
   \frac{d x}{d t} = m u = m(x(t),y(t)) u(x(t), y(t), z(t), t), \quad 
   \frac{d y}{d t} = n v = n(x(t),y(t)) v(x(t), y(t), z(t), t)
This is the characteristic equation of the Eulerian above.
[ikke nødvendigvis, men OK dersom f.eks. z = fast dyp]

lon-lat
+++++++

As an example, the longitude-latitude system is given by
longitude :math:`x = \lambda d` and latitude :math:`y = \phi d`,
where :math:`x, y` are given in degrees, :math:`\lambda, \phi` in
radians and :math:`d = 180/\pi` is the conversion factor.
This is an ortogonal system with metric terms

.. math:: m = \frac{d}{R \cos(y/d)}, \quad n = \frac{d}{R}
The particle tracking is given by 

.. math:: \dot{x} = m u, \quad \dot{y} = n v .
where :math:`u, v` are the east and north components of the current.

ROMS grid
+++++++++

ROMS uses orthogonal grids. Here :math:`x, y` are non-dimensional grid
coordinates (:math:`\xi, \eta` in ROMS terminology) and 
:math:`m, n` are given as the metric terms pm, pn. The velocity
components stored are the :math:`u, v` as defined above. Particle
tracking in grid coordinates then simply becomes

.. math:: 
   \frac{d x}{d t} = m u, \quad \frac{d y}{d t} = n v

If the grid is based on a polar stereographic projection with
parameters :math:`x_p, y_p, \lambda_0, dx` we have

.. math:: m = n = \frac{\sqrt{(x-x_p)^2 + (y-y_p)^2}}
                       {R \cos \phi(x,y)}
[sjekk om bedre formulering, delta x må inn]


