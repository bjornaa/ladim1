:mod:`IBM` --- Individual Based Module
======================================

.. module:: IBM
   :synopsis: Individual Based Module for particle behaviour

An IBM (Individual Based Model) for biological behaviour or similar
can be added to LADiM. As they may be very different, it is difficult to
be general enough.

The IBM variables are named by the configuration. Initial values may be
provided by the particle release file. Alternatively values may
given or derived from the IBM forcing fields. If none of the above, the
values are initially set to zero. [Check if correct, may change to error
if uninitialized]

The IBM module has the responsibility for updating the required extra
forcing (besides velocity) by calling the ``forcing.field`` method.


Requirements for an IBM module:

.. class:: IBM(config)

   .. method:: update_ibm(self, grid, state, forcing)

   This method is supposed be called from the :meth:`State.update` method.

IBM support utilities
----------------------

A :mod:`light` module is available as ``ladim.ibms.light``, that can be used
to compute the surface light (without clouds). This is useful for modelling
diel vertical migration for many species. The module is based on the
paper by A. Skartveit & J.A. Olseth (1988). It is given as a function:

.. function:: surface_light(dtime, lon, lat)

   :arg numpy.datetime64 dtime: Time
   :arg float lon: Longitude [degrees]
   :arg float lat: Latitude [degrees]
