:mod:`state` --- The model state
================================

.. module:: state
   :synopsis: The model state

This module keeps track of the model state, that is the values
of the state variables at a given time.

.. class:: State(config)

   Mandatory state variables:

   .. attribute:: pid

      Particle identifier

   .. attribute:: X, Y

      Horizontal position  [grid coordinates]

   .. attribute:: Z

      Vertical position [meters]

   IBM state variables may vary and are defined in the configuration.
   For example, for salmon lice these are ``age`` - the "age" in degree-days,
   and ``super`` - the number of individuals represented by a super-individual.
   These extra attributes can be accessed through their name as ``state['age']``
   for instance.

   In addition the state keeps record of time:

   .. attribute:: timestep

      The time step counter

   .. attribute:: timestring

      The present time in ISO 8601 format: "yyyy-mm-dd hh:mm:ss".

   The State class has methods:

   .. method:: update(grid, forcing)

      Advance the model to the next step.

   .. method:: append(new)

      Append new particles to the state,
      new is a dictionary of new particles and their state.
