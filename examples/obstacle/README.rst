Flow around a semicircular island
=================================

This example is a recommended testcase in::

  Brickman et al., 2009, Particle tracking,
  in North, Gallego and Petitgas (eds)
  Manual of recommended practises for modelling
  physical-biological interactions during fih early life,
  ICES Cooperative Research Report, 295

The module ``gridforce_analytic`` returns the analytical value of the current
at the particle positions. The alternative module ``gridforce_discrete``
discretize the current to a 1 km grid and samples the grid for current and sea
mask.
