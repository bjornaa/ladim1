================
Example: restart
================

The purpose of this example is to demonstrate the restart mechanism.
There are three yaml files:

``unsplit.yaml``
  Runs the streak example unchanged, result in ``unsplit.yaml``

``split.yaml``
  Runs the streak example, splitting the output in half-day files
  each with 4 records, 3 hours apart. Files are named ``split_0001.nc``, ...

``restart.yaml``
  Restarts the split example from ``split_0001.nc``. File names are
  ``restart_0001.nc``, ...

The script ``make_release.py`` should be run initially to make the release
file. The example ``ladim split.yaml`` should be run before ``ladim
restart.yaml``.

The script ``plot_compare.py`` compares the results. The 6th record in
``unsplit.nc``, the second in ``split_0002.nc`` and ``restart_0001.nc`` should
agree.
