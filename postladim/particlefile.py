import numpy as np
from netCDF4 import Dataset, num2date


class ParticleFile(object):
    """Reader class for LADIM output particle files

    Attributes:
      nc - The underlying netCDF4 Dataset
      num_times - Number of time frames in the file
      variables - List of instance variables
      particle_variables - List of particle variables

    Methods:
        time(n) - Time of the time frame
        particle_count(n) - Number of particles at each time frame
        position(n) - Position of time
        variables(name, n) - Value of the variable at time frame

    """

    def __init__(self, filename):
        self.nc = Dataset(filename)
        self.num_times = len(self.nc.dimensions['time'])
        self.variables, self.particle_variables = [], []
        for key, var in self.nc.variables.items():
            if 'particle_instance' in var.dimensions:
                self.variables.append(key)
            elif 'particle' in var.dimensions:
                self.particle_variables.append(key)
        self._count = self.nc.variables['particle_count'][:]
        self._start = np.concatenate(([0], np.cumsum(self._count[:-1])))

    def time(self, n):
        tvar = self.nc.variables['time']
        return num2date(tvar[n], tvar.units)

    def particle_count(self, n):
        return self._count[n]

    def position(self, n):
        """Get particle positions at n-th time times"""
        start = self._start[n]
        count = self._count[n]
        X = self.nc.variables['X'][start:start+count]
        Y = self.nc.variables['Y'][start:start+count]
        return X, Y

    def _get_variable(self, name, n):
        """Read an instance variable at given time"""
        # Må ha test, om name er variabel
        start = self._start[n]
        count = self._count[n]
        return self.nc.variables[name][start:start+count]

    # name = instance variable
    #   pf[name, time_idx] returns values at time frame time_idx
    #   pf[name, time_idx, i] shorthand for pf[name, time_idx][i]
    # name = particle variable
    #   pf[name] returns all values
    #   pf[name, pid] is shorthand for pf[name][pid]
    def __getitem__(self, v):
        nargs = len(v)
        if isinstance(v, str):
            name = v
            nargs = 1
        else:
            name = v[0]
        if name in self.variables:
            if nargs == 2:
                return self._get_variable(name, v[1])
            elif nargs == 3:
                return self._get_variable(name, v[1])[v[2]]
            else:
                raise KeyError('Must have 2 or 3 indices')
        elif name in self.particle_variables:
            if nargs == 1:
                return self.nc.variables[name][:]
            elif nargs == 2:
                return self.nc.variables[name][v[1]]
            else:
                raise KeyError('Must have 1 or 2 indices')
        else:
            raise KeyError(name)
