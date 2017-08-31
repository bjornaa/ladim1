#! /ust/bin/env python

# Take a subgrid and subsample the grid
# to make forcing for nesting example.
#
# Uses xarray to simplify array operations
# and in particular writing netcdf-files.

import xarray as xr

romsfile = '../data/ocean_avg_0014.nc'
outfile1 = 'forcing_skagerrak.nc'
outfile2 = 'forcing_northsea.nc'

A0 = xr.open_dataset(romsfile)
imax = len(A0.xi_rho)
jmax = len(A0.eta_rho)

# -----------------------------------
# Make (fine) subgrid for Skagerrak
# ------------------------------------

# Subgrid specification
i0, i1 = 135, 172
j0, j1 = 42, 81
# Do not care about xi_psi and eta_psi (not used)
A1 = A0.isel(xi_rho=slice(i0, i1), eta_rho=slice(j0, j1),
             xi_u=slice(i0, i1-1), eta_u=slice(j0, j1),
             xi_v=slice(i0, i1), eta_v=slice(j0, j1-1))
A1.to_netcdf(outfile1)

# -----------------------
# Make a coarse grid
# -----------------------
#
# Subsampling to 3x3 grid cells using middle value from original grid
# As this is a demo, there is no clean up of land mask

A2 = A0.isel(xi_rho=slice(1, imax-1, 3), eta_rho=slice(1, jmax-1, 3),
             xi_u=slice(2, imax-3, 3), eta_u=slice(1, jmax-1, 3),
             xi_v=slice(1, imax-1, 3), eta_v=slice(2, jmax-3, 3))
# Adjust the inverse metric
A2['pm'] = A2['pm'] / 3
A2['pn'] = A2['pn'] / 3
A2.to_netcdf(outfile2)
