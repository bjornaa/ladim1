:mod:`IBM` --- Individual Based Module
======================================

.. module:: IBM
   :synopsis: Individual Based Module for particle behaviour

An IBM (Individual Based Model) for biological behaviour or similar
can be added to LADIM. As they may be very different, it is difficult to
be general enough.

The IBM variables are named by the configuration, and some get initial
values in the particle release. The rest must be initialized.
[This is not done properly yet, age = 0 initially so lakselus is OK,
need perhaps an append method, to be called by state.append]

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
