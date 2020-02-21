Stommel model of westwards intensification
==========================================

This example is based on the stationary 2D current field from an analytical ocean model
of wind-driven ocean currents on a beta-plane. The model is derived by Stommel (1948).
The gridforce module uses the same variable names as the Stommel paper.

Due to westwards intensification this current field strongly distorts advected patterns.
It is a tough test for Eulerian advection schemes (Hecht et al. 1995), and has been
suggested as a standard test for Lagrangrian advection (Fabbroni, 2009) and later (Lange
and van Sebille, 2017).

References
----------

N. Fabbroni, N.: Numerical simulations of passive tracers dispersion
in the sea, PhD thesis, Universita di Bologna, 2009

M.W. Hecht, W.R. Holland and P.J. Rasch, 1995. Upwind-weighted advection schemes for
ocean tracer transport: an evaluation in a passive tracer context. J. Geophys. Res. 100,
20763–20778.

M. Lange and E. van Sebille, 2017, Parcels v0.9: prototyping a Lagrangian ocean analysis
framework for the petascale age, Geosci. Model Dev., 10, 4175–4186.

H. Stommel, 1948, The westward intensification of wind-driven ocean currents, Trans.
Amer. Geophys. U., 29, 202–206.