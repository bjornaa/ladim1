"""Main class ParticleFile for reading LADiM output
"""

# ---------------------------------
# Bjørn Ådlandsvik <bjorn@imr.no>
# Institute of Marine Research
# ---------------------------------

from typing import Any, List, Dict, Union, Tuple
import numpy as np
from netCDF4 import Dataset, num2date


class InstanceVariable:
    """Particle instance variable, depending on particle and time
    """

    def __init__(self, particlefile: 'ParticleFile', varname: str) -> None:
        self.pf = particlefile
        self.name = varname
        # Copy the netcdf attributes
        nc = particlefile.nc
        for v in nc.variables[varname].ncattrs():
            setattr(self, v, getattr(nc.variables[varname], v))

    def __getitem__(self, n: int) -> Any:
        """Get values at time step = n
        """
        start = self.pf.start[n]
        end = self.pf.end[n]
        return self.pf.nc.variables[self.name][start:end]


class ParticleVariable:
    """Particle variable, time-independent
    """

    def __init__(self, particlefile: 'ParticleFile', varname: str) -> None:
        self.pf = particlefile
        self.name = varname
        # Copy the netcdf attributes
        nc = particlefile.nc
        for v in nc.variables[varname].ncattrs():
            setattr(self, v, getattr(nc.variables[varname], v))

    def __getitem__(self, p: int) -> Any:
        """Get the value of particle with pid = p
        """

        return self.pf.nc.variables[self.name][p]


# Variable type, for type hinting
Variable = Union[InstanceVariable, ParticleVariable]


class ParticleFile:
    """Dataset from a LADiM output fil
    """

    # Add reasonable exception if file not exist
    # or file is not a particle file
    def __init__(self, filename: str) -> None:
        try:
            self.nc = Dataset(filename, mode='r')
        except FileNotFoundError:
            raise SystemExit(f'Particlefile {filename} not found')
        except OSError:
            raise SystemExit(f'File {filename} is not a particle file')


        # Number of particles per time
        self.count = self.nc.variables['particle_count'][:]
        # End and start of segment with particles at a given time
        self.end = np.cumsum(self.count)
        self.start = np.concatenate(([0], self.end[:-1]))

        self.num_times = len(self.nc.dimensions['time'])

        # Extract instance and particle variables from the netCDF file
        self.instance_variables: List[InstanceVariable] = []
        self.particle_variables: List[ParticleVariable] = []
        self.variables: Dict[str, Variable] = {}
        for key, var in self.nc.variables.items():
            if 'particle_instance' in var.dimensions:
                self.instance_variables.append(key)
                self.variables[key] = InstanceVariable(self, key)
            elif 'particle' in var.dimensions:
                self.particle_variables.append(key)
                self.variables[key] = ParticleVariable(self, key)

    def time(self, n: int) -> str:
        """Get timestamp from a time frame"""
        tvar = self.nc.variables['time']
        return num2date(tvar[n], tvar.units)

    def particle_count(self, n: int) -> int:
        """Return number of particles at a time frame"""
        return self.count[n]

    def position(self, n: int) -> Tuple[np.ndarray, np.ndarray]:
        """Get particle positions at n-th time frame"""
        start = self.start[n]
        end = self.end[n]
        X = self.nc.variables['X'][start:end]
        Y = self.nc.variables['Y'][start:end]
        return X, Y

    # Allow simpler pf['X'] notation for pf.variables['X']
    def __getitem__(self, varname: str) -> Variable:
        return self.variables[varname]

    def trajectory(self, p: int) -> 'Trajectory':
        """Get particle positions along a single track"""

        f = self.nc
        X, Y = [], []
        first_time = None
        last_time = self.num_times

        # After loop
        # particle is alive for n in [first_time:last_time]
        # or to the end if last_time == 0

        for n in range(self.num_times):
            start = self.start[n]
            end = self.end[n]
            pid = f.variables['pid'][start:end]

            if pid[-1] < p:  # particle not released yet
                continue

            if first_time is None:
                first_time = n

            # index = sum(pid < p) # eller lignende
            index = pid.searchsorted(p)
            if pid[index] > p:  # p is missing
                last_time = n     #
                break             # No need for more cycles

            X.append(f.variables['X'][start + index])
            Y.append(f.variables['Y'][start + index])

        return Trajectory(range(first_time, last_time), X, Y)

    def close(self) -> None:
        self.nc.close()

    # Make ParticleFile a context manager
    def __enter__(self):
        return self

    def __exit__(self, atype, value, traceback):
        self.close()


class Trajectory:
    """Single particle trajectory"""

    # def __init__(self, times: List[int], X: np.ndarray, Y: np.ndarray) -> None:
    def __init__(self, times, X, Y) -> None:
        self.times = times
        self.X = X
        self.Y = Y

    def __len__(self):
        return len(self.times)
