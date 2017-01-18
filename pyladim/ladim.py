#! /usr/bin/env python
# -*- coding: utf-8 -*-

# import numpy as np
from netCDF4 import num2date
# from trackpart import Euler_Forward
from input import ROMS_input
from release import ParticleReleaser
from configuration import Configure
from ladim_state import State
from output import OutPut
from behaviour import behaviour

# ==================
# Initiate the model
# ==================

# Read the configuration file
# --------------------

config_file = 'ladim.yaml'      # take from command line

print(" --- pyladim configuration ----")
config = Configure(config_file)
# print(config.particle_variables)
# config.write()
print(" --- end of configuration ---\n")

numsteps = config.numsteps
dt = config.dt


# State
state = State(config)

# --------------------
# Input grid and files
# --------------------

inp = ROMS_input(config)

tunits = inp.nc.variables['ocean_time'].units

# ----------------------
# Particle release file
# ----------------------

partini = ParticleReleaser(config)
# partini.scan()   # Gjør dette til del av __init__

# ------------------
# Init output file
# -----------------

out = OutPut(config)
# Problem under, får ikke inn multiplisiteten
out.write_particle_variables(partini)

# ==============
# Main time loop
# ==============

for i in range(numsteps+1):
    inp.update(i)

    # Read particles ?
    if i in partini.release_steps:
        # Tips: Gjøre begge delet i read_particles
        V = next(partini)
        state.append(V)

    # Save to file
    if i % config.output_period == 0:
        print("Output: i = ", i, num2date(i*dt,
              'seconds since %s' % str(config.start_time)))
        out.write(state)

    # Only use surface forcing presently
    # Redundant to give both inp, and inp.U ...
    state.update(inp)

    # Behaviour
    behaviour(state)


# ========
# Clean up
# ========

inp.close()
out.close()
