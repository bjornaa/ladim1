#! /usr/bin/env python

"""Main program for running LADiM

Lagrangian Advection and Diffusion Model

"""

# ---------------------------------
# Bjørn Ådlandsvik <bjorn@imr.no>
# Institute of Marine Research
# ---------------------------------

import sys
import logging

import ladim1
from .configuration import configure
from .gridforce import Grid, Forcing
from .release import ParticleReleaser
from .state import State
from .output import OutPut


def main(config_stream, loglevel=logging.INFO):
    """Main function for LADiM"""

    # ==================
    # Initiate the model
    # ==================

    # Logging
    logging.getLogger().setLevel(loglevel)

    # --- Configuration ---
    config = configure(config_stream)

    # --- Initiate the grid and the forcing ---
    grid = Grid(config)
    forcing = Forcing(config, grid)

    # --- Initiate particle releaser ---
    releaser = ParticleReleaser(config, grid)

    #  --- Initiate the model state ---
    state = State(config, grid)

    # --- Initiate the output ---
    out = OutPut(config, releaser)
    # out.write_particle_variables(releaser)

    # ==============
    # Main time loop
    # ==============

    logging.info("Starting time loop")
    for step in range(config["numsteps"] + 1):


        # --- Particle release ---
        if step in releaser.steps:
            V = next(releaser)
            state.append(V, forcing)

        # --- Update forcing ---
        forcing.update(step)

        # --- Save to file ---
        # Save before or after update ???
        if step % config["output_period"] == 0:
            out.write(state, grid)

        # --- Update the model state ---
        state.update(grid, forcing)

    # ========
    # Clean up
    # ========

    # TODO: should also close the releaser
    forcing.close()
    # out.close()
