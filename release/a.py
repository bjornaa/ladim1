# import os
import numpy as np
# import pytest
# import pandas as pd
from release_pandas import ParticleReleaser

# Testing the ParticleReleaser class
# Usage: py.test test_release.py

# TODO: Implement and test that we get error if no release in the
# time window
# TODO: Implement and test that input and description matches


class Container(object):
    """A simple class for emulating the Configuration"""
    pass


# Make a minimal config object
config = Container()
config.start_time = np.datetime64('2015-03-31 12')
# config.reference_time = config.start_time
config.stop_time = np.datetime64('2015-04-04')
config.dt = 3600
config.particle_release_file = 'test.rls'
config.release_format = ['mult', 'release_time', 'X']
config.release_dtype = dict(mult=int, release_time=np.datetime64,
                            X=float)
config.release_type = 'discrete'
config.particle_variables = []

# Make the ParticleReleaser object
release = ParticleReleaser(config)
# os.remove('test.rls')

# print("Hele filen")
# print(release.A)
# print("total = ", release.total_particle_count)


for t in release.times:
    V = next(release)
    print("\n", t)
    print(V)
