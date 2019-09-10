#! /usr/bin/env python

# import argparse
import logging

# import datetime
# import os.path
from pathlib import Path

from .configuration import configure
from .gridforce import Grid, Forcing
from .release import ParticleReleaser
from .state import State
from .output import OutPut


def main(config_stream, loglevel=logging.INFO):
    # ==================
    # Initiate the model
    # ==================

    # --- Logging ---
    logging.basicConfig(
        # level=loglevel,
        level=logging.DEBUG,
        format="%(levelname)s:%(module)s - %(message)s",
    )

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

        # --- Update forcing ---
        forcing.update(step)

        # --- Particle release ---
        if step in releaser.steps:
            V = next(releaser)
            state.append(V)

        # --- Save to file ---
        # Save before or after update ???
        if step % config["output_period"] == 0:
            out.write(state, grid)

        # --- Update the model state ---
        state.update(grid, forcing)

    # ========
    # Clean up
    # ========

    # now = datetime.datetime.now().replace(microsecond=0)
    # logging.info(f'End of simulation, time={now}')

    # TODO: should also close the releaser
    forcing.close()
    # out.close()
