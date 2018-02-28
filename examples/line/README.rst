=========================
Instantaneous line source
=========================

This is the most standard example. A line of particles are released
simultaneously at fixed depth.

After installing ladim, the example can be run as::

  python make_release.py

This produces the particle release file ``line.rst``. To do the particle
tracking write::

  ladim

The results can be shown as an animation by::

  python animate.py


Experiment with the settings in ``make_release.py`` to change the initial
condition and ``ladim.yaml`` for the simulation.

There are different visualizations, ``plot_distribution.py`` plots the particle
distribution at a given time, ``plot_cellcount.py`` counts particles in the
grid cell of the ocean model, while ``plot_trajectories.py`` plots a selection
of trajectories. These examples can be modified to suit different particle
tracking results.
