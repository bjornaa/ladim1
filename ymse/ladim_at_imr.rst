==================
Using LADiM at IMR
==================

LADiM at ``rhea``
=================

The machine ``rhea`` is a common computing machine at IMR with
32 cores and 640 GB ram. The machine is unique at IMR because of the
``hexagon``-disk that mirrors a disk on the ``hexagon`` super-computer.

Python environment
------------------

LADiM requires python 3.6. This is available with the (ana)conda setup.
If not available from the .bashrc or .zshrc, activate it by the line::

    export PATH=/opt/anaconda/bin:$PATH

This gives the default python 2.7 environment. To change to python 3.6 give the command::

    source activate py36


Trying LADiM
------------

The main script ``ladim`` is installed on rhea. The command::

    ladim

is available but will normally fail du to missing configuration file.

The easiest is to test some of the examples. They can be copied from
/home/bjorn/ladim/examples or directly from github, https://github.com/bjornaa/ladim.

Copy one or more example directories and the data directory to a directory of
your own. This contains a setup file ``ladim.yaml`` and a script to make the
particle release file. The commands::

    python make_release.py
    ladim
    python animate.py

will make the release file, run LADiM and visualize the result.

Play around with the files ``ladim.yaml`` and ``make_release.py`` to get some
experience with the configuration system.

Run the salmon lice model
-------------------------

For a more realistic case, copy the directory ``/home/bjorn/ladim/models/salmon_lice``.
The same command sequence as above will generate the release file, run LADiM and show the results.

LADiM at ``hexagon``
====================

The machine ``hexagon``, more precisely ``hexagon.hpc.uib.no``, is a
super-computer at the University of Bergen. For information see
https://docs.hpc.uib.no/wiki/Main_Page

Python environment
------------------

Several versions of ``python`` is available on ``hexagon``. The default is
2.6.9, ``module load python`` gives 2.7.9, and 3.4.3 is available as another
module. Presently, the module system does not provide version 3.6 required by
``LADiM``. A separate minimal python installation by the ``conda`` system is
available at ``/shared/projects/imr/miniconda3``. This can be activated by
modying the ``PATH`` environment variable::

  export PATH=/shared/projects/imr/miniconda3/bin:$PATH

If the ``python`` module is already loaded, it must be unloaded::

  module unload python

This may be simplified if python 3.6 is installed in the module system.

Running LADiM
-------------

If python 3.6 is activated LADiM can simply be run by the command::

  ladim [configuration-file]

Without activation (and with no python module loaded) it can be run by the full
path::

  /shared/projects/imr/miniconda3/bin/ladim [configuration-file]

However, the python 3.6 environment must be activated before any pre- or
post-prosessing. [check to sea if they may work with other versions].

Here is an example ``sbatch`` run script::

  #!/bin/sh

  #SBATCH --time=1:00
  #SBATCH --ntasks=1

  WORK=/work/users/bjornaa
  BIN=/home/bjornaa/miniconda3/bin

  PYTHON=$BIN/python
  LADIM=$BIN/ladim
  LADIM_WORK=$WORK/myladim

  cd $LADIM_WORK

  # Make particle release file, if needed
  #aprun $PYTHON make_release.py

  # Run LADiM
  aprun $LADIM
