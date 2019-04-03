#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Extract a closed coast line

Extracts a coast line in lat-lon from GSHHS using
the advanced polygon handling features in Basemap

The polygons are saved to a npy-file

"""

# ----------------------------------
# Bjørn Ådlandsvik <bjorn@imr.no>
# Institute of Marine Research
# ----------------------------------

# ---------------
# Imports
# ---------------

import sys

import numpy as np

try:
    from mpl_toolkits.basemap import Basemap
except ImportError:
    print("Basemap is needed for makecoast")
    sys.exit(-1)


def main():
    """Main function if used as a script"""

    # -----------------
    # User settings
    # -----------------

    # Determine geographical extent
    # Use slightly larger latitudal range
    lon0, lon1 = -6, 12  # Longitude range
    lat0, lat1 = 54, 62.5  # Latitude range

    # Choose GSHHS resolution
    # 'f' = full, 'h' = high, 'i' = intermediate,
    # 'l' = low, 'c' = crude
    GSHHSres = "i"

    # Choose a list of GSHHS types
    # 1 = land, 2 = lake, 3 = island in lake, 4 = pond in island in lake
    GSHHStypes = [1]

    # Output coast file
    coastfile = "coast.npy"

    # --- End user settings ---

    makecoast(**locals())


def makecoast(lon0, lon1, lat0, lat1, GSHHSres, GSHHStypes, coastfile):
    """Make a lat/lon coast file

    Arguments:
    lon0, lon1 : Longitude limitation
    lat0, lat1 : Latitude limitation
    GSHHSres   : GSHHS resolution ('f','h','i','l','c')
    GSHHStypes : GSHHS types to be extracted (subset of {1,2,3,4})
    coastfile  : File name for output

    """

    # ------------------------------
    # Set up Basemap map projection
    # ------------------------------

    # Use the identity projection, x=lon, y=lat
    # This is called the cylindrical equidistand projection
    bmap = Basemap(
        projection="cyl",
        llcrnrlon=lon0,
        llcrnrlat=lat0,
        urcrnrlon=lon1,
        urcrnrlat=lat1,
        resolution=GSHHSres,
    )

    # ----------------------------
    # Get the coast polygon data
    # ----------------------------

    # Extract the polygons
    polygons = bmap.coastpolygons

    # Only use the selected polygon types
    polygons = [
        p for (p, t) in zip(polygons, bmap.coastpolygontypes) if t in GSHHStypes
    ]

    # --------------------
    # Save the coast data
    # --------------------

    np.save(coastfile, polygons)


if __name__ == "__main__":
    main()
