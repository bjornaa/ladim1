IBM module
==========

An IBM (Individual Based Model) for biological behaviour or similar
can be added to LADIM. As they may be very different, it is difficult to
be general enough.


The IBM variables are named by the configuration, and some get initial
values in the particle release. The rest must be initialized.
[This is not done properly yet, age = 0 initially so lakselus is OK,
need perhaps an append method, to be called by state.append]

The IBM class should have an update method, to be called from
state.update.

Support utilities
-----------------

A light module is available as ladim.ibms.light, that can be used
to compute the surface light (without clouds).
