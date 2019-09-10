# Classes for Particle and State variables

import sys
import os
import importlib
import logging
from typing import Any, Dict, Sized  # mypy

import numpy as np
from netCDF4 import Dataset, num2date

from .tracker import Tracker
from .gridforce import Grid, Forcing

# ------------------------

Config = Dict[str, Any]


class State(Sized):
    """The model variables at a given time"""

    def __init__(self, config: Config, grid: Grid) -> None:

        logging.info("Initializing the model state")

        self.timestep = 0
        self.timestamp = config["start_time"].astype("datetime64[s]")
        self.dt = np.timedelta64(config["dt"], "s")
        self.position_variables = ["X", "Y", "Z"]
        if "ibm" in config and "variables" in config["ibm"]:
            self.ibm_variables = config["ibm"]["variables"]
        else:
            self.ibm_variables = []
        self.particle_variables = config["particle_variables"]
        self.instance_variables = self.position_variables + [
            var for var in self.ibm_variables if var not in self.particle_variables
        ]

        self.pid = np.array([], dtype=int)
        for name in self.instance_variables:
            setattr(self, name, np.array([], dtype=float))

        for name in self.particle_variables:
            setattr(self, name, np.array([], dtype=config["release_dtype"][name]))

        self.track = Tracker(config)
        self.dt = config["dt"]

        if config["ibm_module"]:
            # Import the module
            logging.info("Initializing the IBM")
            sys.path.insert(0, os.getcwd())
            ibm_module = importlib.import_module(config["ibm_module"])
            # Initiate the IBM object
            self.ibm = ibm_module.IBM(config)
        else:
            self.ibm = None

        # self.num_particles = len(self.X)
        self.nnew = 0  # Modify with warm start?

        if config["warm_start_file"]:
            self.warm_start(config, grid)

    def __getitem__(self, name: str) -> None:
        return getattr(self, name)

    def __setitem__(self, name: str, value: Any) -> None:
        return setattr(self, name, value)

    def __len__(self) -> int:
        return len(getattr(self, "X"))

    def append(self, new: Dict[str, Any]) -> None:
        """Append new particles to the model state"""
        nnew = len(new["pid"])
        self.pid = np.concatenate((self.pid, new["pid"]))
        for name in self.instance_variables:
            if name in new:
                self[name] = np.concatenate((self[name], new[name]))
            else:  # Initialize to zero
                self[name] = np.concatenate((self[name], np.zeros(nnew)))
        self.nnew = nnew

    def update(self, grid: Grid, forcing: Forcing) -> None:
        """Update the model state to the next timestep"""

        # From physics all particles are alive
        # self.alive = np.ones(len(self), dtype="bool")
        self.alive = grid.ingrid(self.X, self.Y)

        self.timestep += 1
        self.timestamp += np.timedelta64(self.dt, "s")
        self.track.move_particles(grid, forcing, self)
        # logging.info(
        #        "Model time = {}".format(self.timestamp.astype('M8[h]')))
        if self.timestamp.astype("int") % 3600 == 0:  # New hour
            logging.info("Model time = {}".format(self.timestamp.astype("M8[h]")))

        # Update the IBM
        if self.ibm:
            self.ibm.update_ibm(grid, self, forcing)

        # Surface/bottom boundary conditions
        #     Reflective  at surface
        I = self.Z < 0
        self.Z[I] = -self.Z[I]
        #     Keep just above bottom
        H = grid.sample_depth(self.X, self.Y)
        I = self.Z > H
        self.Z[I] = 0.99 * H[I]

        # Compactify by removing dead particles
        # Could have a switch to avoid this if no deaths
        self.pid = self.pid[self.alive]
        for key in self.instance_variables:
            self[key] = self[key][self.alive]

    def warm_start(self, config: Config, grid: Grid) -> None:
        """Perform a warm (re)start"""

        warm_start_file = config["warm_start_file"]
        try:
            f = Dataset(warm_start_file)
        except FileNotFoundError:
            logging.error("Can not open warm start file: " + warm_start_file)
            raise SystemExit(1)

        logging.info("Reading warm start file")
        # Using last record in file
        tvar = f.variables["time"]
        warm_start_time = np.datetime64(num2date(tvar[-1], tvar.units))
        # Not needed anymore, explicitly set in configuration
        # if warm_start_time != config['start_time']:
        #    print("warm start time = ", warm_start_time)
        #    print("start time      = ", config['start_time'])
        #    logging.error("Warm start time and start time differ")
        #    raise SystemExit(1)

        pstart = f.variables["particle_count"][:-1].sum()
        pcount = f.variables["particle_count"][-1]
        self.pid = f.variables["pid"][pstart : pstart + pcount]
        # Give error if variable not in restart file
        for var in config["warm_start_variables"]:
            logging.debug(f"Reading {var} from warm start file")
            self[var] = f.variables[var][pstart : pstart + pcount]

        # Remove particles near edge of grid
        I = grid.ingrid(self["X"], self["Y"])
        self.pid = self.pid[I]
        for var in config["warm_start_variables"]:
            self[var] = self[var][I]
