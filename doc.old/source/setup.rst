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
Whitaker is needed. This is typically not available in the standard
software repositories. It can be found at
http://code.google.com/p/netcdf4-python/. It requires a not too old
working installation of the NetCDF library itself, typically found in
the software repositories.

The git version control system is not necessary for running
pyladim. It is recommended for keeping the model up to date and for
  keeping tracks of model experiments performed.

Installing pyladim
------------------

The pyladim model may presently be downloaded from dropbox, contact
Bjørn.  It will be moved to a more central space soon. It will be
donladable as a tar ball in addition to the recommended git clone
availability.

To make the model easy to modify and adapt to new problems, it is not
installed centrally on the computer as a python package. Instead the
source code for an experiment is contained in the working directory.

A fresh install has the following directory structure. 

 - pyladim : the source code
  
 - input : Placeholder for input files, forcing from an ocean model
   and particle release file

 - output : Placeholder for output files

 - prepro : Pre-processing tools 

 - postpro : post-processing tools

 - test : unit tests for model components
 
 - examples : examples of model set-ups

The main directory has two essential files, `ladim` the model executable,
a link to `pyladim/ladim.py` and a set-up file (by default `ladim.sup`).
