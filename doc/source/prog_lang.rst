Programming language
====================

The LADiM code is written in `python <https://www.python.org>`_, more
specifilly python 3. It has been tested with versions 3.5 and 3.6.

Dependencies
------------

In addition to the python standard library, the model is based on the numerical
package `numpy <http:www.numpy.org>`_ and the netcdf library `netcdf4-python
<http://unidata.github.io/netcdf4-python>`_. The yaml package
`pyyaml <http://pyyaml.org>`_ is used for the configuration, while the particle
release module depend on the data analysis package
`pandas <http://pandas.pydata.org>`_. All these packages are available in the
`anaconda <https://www.continuum.io/anaconda-overview>`_ bundle.

Testing is done using the `pytest <http://doc.pytest.org>`_-framework. The
examples use the plotting package `matplotlib <http://matplotlib.org>`_ for the
post processing.

This documentation uses the `Sphinx <http://www.sphinx-doc.org>`_
documentation system to generate html and pdf documentation. To produce the
pdf version a decent `LaTeX <https://www.latex-project.org>`_ implentation
is needed.