"""Main class ParticleFile for reading LADiM output

   Inspired by the general netcdf4 package, but
   adapted for ragged array indexing.

"""

# ---------------------------------
# Bjørn Ådlandsvik <bjorn@imr.no>
# Institute of Marine Research
# ---------------------------------

import numpy as np
from netCDF4 import Dataset, num2date


class InstanceVariable:
    """Particle instance variable

    parameters
    ----------
    particlefile : ParticleFile instance
    name : Variable name

    Example
    -------
    temp = pf.variables['temp'][n]
        Here pf is a ParticleFile instance
        Get array of particle temperatures at time frame n in the file

    """
    def __init__(self, particlefile, name):
        self._pf = particlefile
        self._name = name
        nc = particlefile.nc
        for v in nc.variables[name].ncattrs():
            setattr(self, v, getattr(nc.variables[name], v))

    def __getitem__(self, n):
        return self._pf._get_variable(self._name, n)


class ParticleVariable:
    """Particle variable

    parameters
    ----------
    particlefile : ParticleFile instance
    name : Variable name

    Example
    -------
    rtime = pf.variables['release_time'][pid]
        Here pf is a ParticleFile instance
        Get release time of particle with identifier = pid

    """
    def __init__(self, particlefile, name):
        self._pf = particlefile
        self._name = name
        nc = particlefile.nc
        for v in nc.variables[name].ncattrs():
            setattr(self, v, getattr(nc.variables[name], v))
        # self.__getitem__ = nc.variables[name].__getitem__

    def __getitem__(self, pid):
        return self._pf.nc.variables[self._name][pid]


class ParticleFile:
    """Dataset from a LADiM output file

    parameters
    ----------
    filename : Name of particle file

    """
    def __init__(self, filename):
        self.nc = Dataset(filename, mode='r')
        self.num_times = len(self.nc.dimensions['time'])
        self.variables = dict()
        self.instance_variables, self.particle_variables = [], []
        for key, var in self.nc.variables.items():
            if 'particle_instance' in var.dimensions:
                self.instance_variables.append(key)
                self.variables[key] = InstanceVariable(self, key)
            elif 'particle' in var.dimensions:
                self.particle_variables.append(key)
                self.variables[key] = ParticleVariable(self, key)
        self._count = self.nc.variables['particle_count'][:]
        self._start = np.concatenate(([0], np.cumsum(self._count[:-1])))

    def _get_variable(self, name, n):
        """Read an instance variable at given time"""
        # Må ha test, om name er variabel
        if isinstance(n, slice):
            start = self._start[n.start]
            count = sum(self._count[n])
        else:   # Integer
            start = self._start[n]
            count = self._count[n]
        return self.nc.variables[name][start:start+count]

    def time(self, n):
        """Get timestamp from a time frame"""
        tvar = self.nc.variables['time']
        return num2date(tvar[n], tvar.units)

    def particle_count(self, n):
        """Return number of particles at a time frame"""
        return self._count[n]

    def position(self, n):
        """Get particle positions at n-th time frame"""
        start = self._start[n]
        count = self._count[n]
        X = self.nc.variables['X'][start:start+count]
        Y = self.nc.variables['Y'][start:start+count]
        return X, Y

    def trajectory(self, p):
        """Get particle positions along a single track"""

        f = self.nc
        X, Y = [], []
        first_time = None
        last_time = self.num_times

        # After loop
        # particle is alive for n in [first_time:last_time]
        # or to the end if last_time == 0

        for n in range(self.num_times):
            start = self._start[n]
            count = self._count[n]
            pid = f.variables['pid'][start:start+count]

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

    def close(self):
        self.nc.close()


class Trajectory:
    """Single particle trajectory"""

    def __init__(self, times, X, Y):
        self.times = times
        self.X = X
        self.Y = Y

    def __len__(self):
        return len(self.times)
