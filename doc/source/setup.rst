==================
Setting up pyladim
==================


Installing pyladim
==================

Requirements
------------

To install and set up pyladim properly there are some software
requirements. First there must be a python installation with the numpy
package. This is typically installed or at least available in the
software repository of any decent linux distro. Presently the 2.x
series of python is used.

For NetCDF input and output, the package netcdf4-python byJeff
WHitaker is needed. This is typically not available in the standard
software repositories. It can be foud at
http://code.google.com/p/netcdf4-python/. It requires a not too old
working installation of the NetCDF library itself, typically found in
the software repositorries.

Presently, pyladim requires the roppy package (ROms Postprocessing
with PYthon).  This is available at
http://code.google.com/p/roppy/. This requirement may be removed later
by incorporating the necessary parts of roppy in pyladim.

