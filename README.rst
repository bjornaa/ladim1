LADiM aka LADIM3 aka pyladim
============================

This is a developing new version of the Lagrangian Advection and Diffusion
Model. It is an off-line particle tracking code. Presently  using results from
the ocean model `ROMS <http://www.myroms.org/>`_ as input.

Try out LADiM
-------------

The model is written in python and requires python 3.6 and some scientific packages. The anaconda python distribution is recommended.

Download the code from ``github`` and install by::

  python setup.py install.

Get a small example data set by running the download script in
``examples/data``. The different examples can be run by the sequence of
commands::

  python make_release.py
  ladim


Source code and documentation
-----------------------------

The code is open source using the MIT License. It is available from
`github <https://github.com/bjornaa/ladim>`_

The documentation is hosted on `readthedocs
<https://ladim.readthedocs.io/en/master>`_. A `pdf version
<https://media.readthedocs.org/pdf/ladim/master/ladim.pdf>`_ is also available.

::

  Bjørn Ådlandsvik <bjorn@imr.no>
  Institute of Marine Research
  Bergen, Norway
