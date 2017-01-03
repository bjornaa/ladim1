#! /usr/bin/env python
# -*- coding: utf-8 -*-

# import numpy as np
from netCDF4 import num2date
from trackpart import Euler_Forward
from input import ROMS_input
from release import ParticleReleaser
from config import read_config, write_config
from state import ParticleVariables, State
from output import OutPut
from behaviour import behaviour

# ==================
# Initiate the model
# ==================

# Read the configuration file
# --------------------

config_file = 'ladim.sup'      # take from command line

print(" --- pyladim configuration ----")
setup = read_config('ladim.sup')
print("configuration file: ", config_file)
write_config(setup)
print(" --- end of configuration ---\n")

nsteps = setup.nsteps
dt = setup.dt


# State
state = State(setup)    # OBS: Navnekollisjon

# --------------------
# Input grid and files
# --------------------

inp = ROMS_input(setup)

tunits = inp.nc.variables['ocean_time'].units

# ----------------------
# Particle release file
# ----------------------

partini = ParticleReleaser(setup)

# ------------------
# Init output file
# -----------------

out = OutPut(setup)

# ==============
# Main time loop
# ==============

for i in range(nsteps+1):
    inp.update(i)

    # Read particles ?
    if i == partini.release_step:
        # Tips: Gjøre begge delet i read_particles
        partini.release_particles(setup, i)
        state.addstate(partini.state)

    # Save to file
    if i % setup.output_period == 0:
        print("i = ", i, num2date(i*dt,
              'seconds since %s' % str(setup.start_time)))
        out.write(state)

    # Only use surface forcing presently
    # Redundant to give both inp, and inp.U ...
    Euler_Forward(inp, inp.U, inp.V, state.X, state.Y, state.Z, dt=dt)

    # Behaviour
    behaviour(state)


# ========
# Clean up
# ========

inp.close()
out.close()
