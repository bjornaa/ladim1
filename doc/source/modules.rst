LADIM implementation
====================

This chapter describes briefly the present implementation
of LADIM. The code is modular and flexible with classes
that can be modified or replaced for different purposes.

The descriptions tries the requierements of the classes
from the rest of the system, hopefully being helpful for
developing alternative classes for use systems.

The code may be developed towards base classes, where alternatives
can inherit from a common base class. Presently, alternatives must
be written separately.

.. toctree::
   :maxdepth: 2

   configuration_module.rst
   grid.rst
   release_class.rst
   forcing.rst
   state.rst
   trackpart.rst
   IBM_class.rst
   output_class.rst
