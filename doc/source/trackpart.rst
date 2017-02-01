TrackPart
=========

This is the physical particle tracking module for horizontal movement.
Vertical movement (except staying between bottom and surface) is the
responsibility of the IBM class.

It is controlled by configuration parameters: config.dt, config.advection,
config.diffusion, config.diffusion_coefficient

There are no public attributes

One public method:

 - move_particles(grid, forcing, state): advect and diffuse the particles
   horizontally, check for particles out-of-area or on land.
