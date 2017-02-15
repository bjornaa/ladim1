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

    # Med dette virker pf['temp', 3]
    # Ønsker også pf['temp'] (hva er den)
    # og pf['temp', 3, 10] = pf['temp', 3][10]
    def __getitem__(self, v):
        print(v)
        name, *val = v
        print(name, val)
        if len(val) == 1:
            return self._get_variable(name, val)
        if len(val) == 2:
            return self.get_variables(name, val[0])[val[1]]

        # if name in self.variables:
            # n = time frame
        #    return self._get_variable(name, time)
        # elif name in self.particle_variables:
            # n = pid
        #    return self.nc.variables[name][n]

    # Alternativ: gi en default verdi om ikke aktiv
    #    Evt. raise exception
    # ha en separat sjekk på aktivitet
    # def get_particle_variable(self, p, n, vname):
        # """Get variable vname at time step n at particle p
        #
        # Returns value, active
        # where: active = 0  if particle is not released (yet)
        #               = -1 if particle has been active but is now closed
        #               = 1  if particle is active
        #        value = value at particle at time n, if active
        #              = ha en fill value if not active
        #
        # """
        #
        # pid = self.get_variable(n, 'pid')
        #
        # if pid[-1] < p:  # particle not released yet
        #     pass
        #     # active = 0
        #
        # index = pid.searchsorted(p)
        # if pid[index] < p:      # p is missing, but has been active
        #     pass
        #     # active = -1
        #
        # # A = self.get_variable(n, vname)
