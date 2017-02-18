:mod:`tracker` --- Particle tracking
====================================

.. module:: tracker
  :synopsis: The particle tracking kernel

This is the physical particle tracking module for horizontal movement.
Vertical movement (except staying between bottom and surface) is the
responsibility of the IBM class.

.. class:: Tracker(config)

   It is controlled by configuration parameters: ``config.dt``,
   ``config.advection``, ``config.diffusion``, ``config.diffusion_coefficient``

   There are no public attributes

   One public method:

   .. method:: move_particles(grid, forcing, state)

   Advect and diffuse the particles horizontally, check for landing or
   particles out-of-area.
