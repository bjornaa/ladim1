Example using multiple grids
============================

This example demonstrates how to use the object-oriented nature of LADiM to
work with nested grids. This is done by a separate gridforce module,
`nested_gridforce` calling the different gridforce modules.

The nesting module defines a "virtual" grid, and links to the real grids
involved. Methods must be included to transform from the virtual grid coordinates to the actual coordinates of the two grids. Here these functions are called xy2fine and xy2coarse.

The concept can easily be generalized to more than two grids. Also the grids may be totally independent of each other, possibly linked from a virtual grid
using longitude and latitude as coordinates.

The example
-----------

Two grids are defined, a "fine" covering the Skagerrak and a coarse covering the North Sea. The fine grid is a subgrid of the standard example grid while
the coarse is obtained by 3x3 blocks of the standard grid. The script
prepare.py generates the netCDF files defining the grids with forcing.
Note: The prepare script depends on the xarray package.

The script make_release.py set up release files for 1000 particles along a transect across the Skagerrak.

TODO: Make a plot of the different areas.

Four simulations are possible::

  ladim original.yaml    # The full original standard example grid
  ladim fine.yaml        # Fine grid only
  ladim coarse.yaml      # Coarse grid only
  ladim nested.yaml      # Nesting the fine grid into the coarse

The results can be animated by the scipts animate_xxx.py, where xxx is one of
original, fine, coarse, or nested .

# Note: bug in land treatment? visible in animate_coarse.py