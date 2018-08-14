Using LADiM at IMR
==================

This chapter is specific to the Institute of Marine Research (IMR) and shows
how to use LADiM on computing resources available to us.

LADiM at ``rhea``
-----------------

The machine ``rhea`` is a common computing machine at IMR with 32 cores and 640
GB ram. The machine is unique at IMR because of the hexagon-disk that mirrors a
disk on the ``hexagon`` super-computer.

Python environment
++++++++++++++++++

LADiM requires python 3.6 or higher. This is available with the (ana)conda
python installation. If not configured from :file:`.bashrc` or :file:`.zshrc`,
activate it by the lines::

  export PATH=/opt/anaconda/bin:$PATH
  source activate py36

Running LADiM
+++++++++++++

The main script :program:`ladim` is installed on rhea. The easiest way to get
started is to try some of the examples. They can be copied from
:file:`/home/bjorn/ladim/examples` or directly from github,
https://github.com/bjornaa/ladim. Copy one or more example directories.
The command sequence::

  python make_release.py
  ln -s /home/bjorn/ladim/examples/data/ocean_avg_0014.nc .
  ladim
  python animate.py
  [Få dette skikkelig til]

will make the release file, run LADiM and visualize the result. Play around
with the files :file:`ladim.yaml` and :file:`make_release.py` to get some
experience with the configuration system.

Run the salmon lice model
+++++++++++++++++++++++++

For a more realistic case, copy the directory
:file:`/home/bjorn/ladim/models/salmon_lice`.
The files are in different places on different machines, use the sequence below
to run the model on ``rhea``::

  python make_release.py
  ladim rhea.yaml
  python animate_rhea.py

LADiM at hexagon
----------------

The machine ``hexagon``, more precisely ``hexagon.hpc.uib.no``, is a super-computer at
the University of Bergen available for use at IMR. For information see
https://docs.hpc.uib.no/wiki/Main_Page

Python environment
++++++++++++++++++

Several versions of python are available on ``hexagon``. The default is 2.6.9
given by the command :command:`module load python`. A newer version, 3.4.3, is
available as an alternative module. Presently, the module system does not
provide version 3.6 required by LADiM. For the time being, a separate minimal
python installation by the conda system is available at
:file:`/shared/projects/imr/miniconda3`. This can be activated by modyfying the
PATH environment variable::

  export PATH=/shared/projects/imr/miniconda3/bin:$PATH

If an official python module is already loaded, it must be unloaded::

  module unload python

This may be simplified if python 3.6 is installed in the module system.

Running LADiM
+++++++++++++

If python 3.6 is activated as above, LADiM can simply be tested by the command::

  ladim [configuration-file]

Without activation (and with no python module loaded) it
can be tested by the full path::

  /shared/projects/imr/miniconda3/bin/ladim [configuration-file]

However, the python 3.6 environment must be activated before any pre- or post- prosessing. [check to see if they may work with other
versions].

For serious use, the job must be submitted to the ``sbatch`` queue system.
Here is an example ``sbatch`` run script:

.. code-block:: sh

  #!/bin/sh

  #SBATCH --time=1:00
  #SBATCH --ntasks=1

  WORK=/work/users/bjornaa
  BIN=/shared/projects/imr/miniconda3/bin
  PYTHON=$BIN/python
  LADIM=$BIN/ladim
  LADIM_WORK=$WORK/myladim

  cd $LADIM_WORK

  # Make particle release file, if needed
  # aprun $PYTHON make_release.py

  # Run LADiM
  aprun $LADIM
