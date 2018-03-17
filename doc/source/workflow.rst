Workflow
========

This chapter describes various possible workflows with LADiM, from simple usage
to developing. Some terminology may be useful. An *installed* LADiM, has been
installed by ``python setup.py install`` in the LADiM root directory, either
*system-wide* by sudo or personal by using the ``--prefix``-option,
see :ref:`installation`. This is typical a working *stable* version in a
usable state.

Unmodified use
--------------

The simplest workflow is to simply use the installed LADiM. Use a work
directory, copy and modify a ``ladim.yaml`` file to point to your input files
and adjust the simulation time and other settings. Run the simulation by the
command ladim.

The configuration file can be renamed and saved to make the model simulation
reproducible. To run LADiM with a named configuration file, give the
file name as a command line argument to the ladim command.

Possible complication: if you are in a python2 environment ,,,

Modify the IBM
--------------

The IBM modules can be very different, with very configuration requirements.
The configuration system is therefore not able to configure all details of the
IBMs. Consequently, IBMs are the most likely modules where the code has to
be modified.

To modify an IBM, copy the file to your working directory. Modify the
``ibm -> ibm-module`` setting in the configuration file to point to the
local module. Thereafter, the installed ladim command should work properly.

A totally new IBM, for another species perhaps, can be developed locally in
the work directory and activated in the same way. The :mod:`IBM`
module description documents what an :class:`IBM` class should make available.
An example of this is the minimal IBM in the ``examples/killer`` directory.
As the new IBM matures, it should be included in the ``ladim/ibms`` directory.

Modify other modules
--------------------

The code of other modules may be modified in a slightly different way.
Copy the module to the working directory and modify it as above.
To activate it, copy the main ladim script ``script/ladim`` to the
working directory and modify the import statement to point to the
local module. To make sure that the correct script is executed, run the
simulation with the command ``./ladim``.

A common use case may be to develop new :mod:`gridforce` modules to work
with output from different ocean models or idealized settings. The
:mod:`gridforce` description specifies the necessary public attributes and
methods for the :class:`Grid`  and :class:`Forcing` classes.
The logo example, ``examples/logo``
has a minimal idealized :mod:`gridforce`-module.
In future, the LADiM distribution may contain a collection of different
gridforce modules and the choice be available by the configure mechanism
in the same manner as for the :mod:`IBM`.

The trick of using a local ``ladim``-script may be use for other modifications
of as well.

Maintenance and further development
-----------------------------------

For develop work on LADiM it is important to not mess up the stable installed
version. This can be done by virtualization. Use a separate ``git`` branch for
the development and a separate ``conda`` or ``virtualenv`` environment.
The conda solution is described below.

The ``git`` part is set up by::

  git clone https://github.com/bjornaa/ladim.git
  cd ladim
  git branch mydevelop
  git checkout mydevelop

Use ``conda env list`` to find the environments, find one with python 3, say
``py36`` and clone it locally, for instance in ``$HOME/conda/envs``::

  conda create  -p $HOME/myenv --clone py36
  source activate $HOME/myenv
  python setup.py install

This installs the developing version in the ``myenv``-environment.
Do a ``python setup install`` after every change before running LADiM.
To get back to the stable environment do::

  git add ...
  git commit ...
  git checkout master
  source deactivate

Instead of ``source deactivate`` it is enough to simply kill the working window.
The next time, it is easier. It is enough to write::

  git checkout mydevelop
  source activate $HOME/myenv

If the development is a general improvement or important addition to the
standard LADiM a pull request should be sent to github so that it can be
included in the stable version.
