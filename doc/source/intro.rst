Introduction
============

``LADiM`` is the acronym of the Lagrangian Advection and DIffusion Model.

It is an offline ocean particle tracking model. Presently it takes
input from the `ROMS <http://www.myroms.org>`_ ocean model.

This is the third incarnation of the ``LADiM`` model at the `Institute of
Marine Research <http://www.imr.no>`_. The first worked with a version of the
``Feltfile`` format used with the `Princeton Ocean Model
<http://www.ccpo.odu.edu/POMWEB/>`_. The second version targeted `NetCDF
<https://www.unidata.ucar.edu/software/netcdf/>`_ output from the ROMS model.
Both these versions were written in `Fortran
<https://en.wikipedia.org/wiki/Fortran>`_. The new code is written in `python
<https://www.python.org>`_ (python 3 only). Parts of the code may in future be
rewritten in other languages for increased performance.

The old fortran codes had drifted apart without any kind of version control and
minimal documentation. Maintenance became increasingly more difficult. The
rationale for a new incarnation is to have a well-documented model system under
version control. The design should be modular so it can easily be extended to
other ocean models and applications.

The model code is available under the `MIT license
<https://opensource.org/licenses/MIT>`_, and is hosted on github,
`https://github.com/bjornaa/ladim <https://github.com/bjornaa/ladim>`_. This
documentation is hosted on `Read the Docs
<https://ladim1.readthedocs.io/en/master>`_. A `pdf version
<https://media.readthedocs.org/pdf/ladim/master/ladim1.pdf>`_ is also available.
