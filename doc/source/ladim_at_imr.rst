Using LADiM at IMR
===================

Using LADiM at rhea
-------------------

Python environment
++++++++++++++++++


LADiM requires python 3.6. This is available with the (ana)conda setup.
If not available from the .bashrc or .zshrc, activate it by the line::

    export PATH=/opt/anaconda/bin:$PATH

To change to python 3.6 give the command::

    source activate py36

Trying LADiM
++++++++++++

The main script `ladim` is installed on rhea. The command::

    ladim

is available but will normally fail du to missing configuration file.

The easiest is to test some of the examples. They can be copied from
/home/bjorn/ladim/examples or directly from github, https://github.com/bjornaa/ladim.

Copy one or more example directories and the data directory to a directory of
your own. This contains a setup file ladim.yaml and a script to make the
particle release file. The commands::

    python make_release.py
    ladim
    python animate.py

will make the release file, run LADiM and visualize the result.

Play around with the files ladim.yaml and make_release.py to get some experience with the configuration.

Run the salmon lice model
+++++++++++++++++++++++++

For a more realistic case, copy the directory /home/bjorn/models/salmon_lice.
The same command sequence as above will generate the release file, run LADiM
and show the results. [**Sjekk at stier er satt korrekt**]

Using LADiM at hexagon
----------------------

Translate text from Norwegian