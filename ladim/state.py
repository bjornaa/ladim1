# Classes for Particle and State variables

import sys
import os
import importlib
import logging
from ladim.trackpart import TrackPart
import numpy as np

# ------------------------


class State:
    """The model variables at a given time"""

    def __init__(self, config):

        logging.info("Initializing the model state")

        self.timestep = 0
        self.timestamp = config.start_time.astype('datetime64[s]')
        self.dt = np.timedelta64(config.dt, 's')
        self.position_variables = ['X', 'Y', 'Z']
        self.ibm_variables = config.ibm_variables
        self.instance_variables = self.position_variables + self.ibm_variables

        self.pid = np.array([], dtype=int)
        for name in self.instance_variables:
            setattr(self, name, np.array([], dtype=float))

        # Skal disse være her??, trenger ikke lagres,
        # oppdatere output etter hver release.
        # self.particle_variables = ['release_time', 'farmid']

        self.track = TrackPart(config)
        self.dt = config.dt

        if config.ibm_module:
            # Import the module
            logging.info("Initalizing the IBM")
            sys.path.insert(0, os.getcwd())
            ibm_module = importlib.import_module(config.ibm_module)
            # Initiate the IBM object
            self.ibm = ibm_module.IBM(config)
        else:
            self.ibm = None

    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, value):
        return setattr(self, name, value)

    def __len__(self):
        return len(getattr(self, 'X'))

    def append(self, new):
        """Append to the state"""
        nnew = len(new['pid'])
        self.pid = np.concatenate((self.pid, new['pid']))
        for name in self.instance_variables:
            if name in new:
                self[name] = np.concatenate((self[name], new[name]))
            else:   # Initialize to zero
                self[name] = np.concatenate((self[name], np.zeros(nnew)))
        # Only store new particle variable values
        # (trenger kanskje ikke lagres her i det hele tatt,
        #   gå rett til output)
        # for name in self.particle_variables:
        #    self[name] = new[name]

    def update(self, grid, forcing):
        self.timestep += 1
        self.timestamp += np.timedelta64(self.dt, 's')
        self.track.move_particles(grid, forcing, self)

        # From physics all particles are alive
        self.alive = np.ones(len(self), dtype='bool')

        # Update the IBM
        if self.ibm:
            self.ibm.update_ibm(grid, self, forcing)

        # Compactify by removing dead particles
        # Compactify
        # Could have a switch to avoid this if no deaths
        self.pid = self.pid[self.alive]
        for key in self.instance_variables:
            self[key] = self[key][self.alive]
