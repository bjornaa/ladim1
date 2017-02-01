State module
============

This module keeps the model state, that is the values
of the state variables at a given time.

Mandatory state variable attributes:

  - pid: Particle identifier
  - X, Y: Horizontal position  [grid coordinates]
  - Z: Vertical position [meters]

IBM state variables may vary and are defined in the configuration.
For example, for salmon lice these are age - the "age" in degree-days,
and super - the number of individuals represented by a super-individual.
These extra attributes can be accessed through their name as state['age']
for instance.

In addition the state keeps record of time:

  - timestep: The time step counter
  - timestring: The present time in ISO 8601 format: "yyyy-mm-dd hh:mm:ss".

The State class has methods:

  - update(grid, forcing): responsible for advancing the model to the next step.
  - append(new): appends new particles to the state, from the release class
  - compactify(): Remove "dead" particles [Not implemented yet]
