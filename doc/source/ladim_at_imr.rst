Using LADiM at IMR
==================

This chapter is specific to the Institute of Marine Research (IMR) and shows
how to use LADiM on computing resources available to us.

Computer resources
------------------

The machines ``rhea``, ``dedun``, and ``demeter`` are available for running
LADiM. ``Rhea`` and ``dedun`` are common resources at IMR  with 32 cores each,
while ``demeter`` is a smaller machine dedicated for LADiM and in particular
the operational salmon lice simulations.

The machines have a data storage facility ``/gpfs/gpfs0``. Forcing data for
LADiM may be found under the ``/gpfs/gpfs0/osea/ROMS-archives`` directory.

Python environment
------------------

LADiM requires python 3.6 or higher. This is available with an (ana)conda
python installation. **First** time issue the command::

  /software/osea/anaconda/bin/conda init zsh

(substitute ``bash`` for ``zsh`` if this is your preferred shell). This modifies
your ``.zshrc`` (of ``.bashrc``) to use the correct python environment.

**IMPORTANT**. Add the following line to your ``.zshrc`` or ``.bashrc``
(preferably both)::

  export MKL_NUM_THREADS=1

This prevents the MKL (Intel's Math Kernel Library) used by python from
capturi ng all cores, effective blocking all other (including your own) activity
at the machine. You may get a slight speed-up with 2 instead of 1.

Exit the shell and log in again. The modified configuration is common for all three
machines.

Alternative LADiM versions
--------------------------

LADiM offers a high degree of flexibility by the ``yaml``-configuration and the
possibility of alternative ``gridforce`` and ``ibm`` modules. More flexibility
is possible by editing the rest of the code. To not mess up the operational
salmon lice runs, this has to be done in a separate git branch and used from a
separate conda environment. For instance, to use the ``beta`` development
branch issue the command::

  conda activate beta




LADiM at fram
-------------

It is possible to use LADiM at the HPC resource ``fram`` at the national
facility Sigma2. This is **not** recommended. We will have to pay for all
processors at a compute node without the benefit of parallell computing.