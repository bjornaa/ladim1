import numpy as np
from netCDF4 import Dataset


class InstanceVariable:
    def __init__(self, particlefile, name):
        self._pf = particlefile
        self._name = name
        nc = particlefile.nc
        for v in nc.variables[name].ncattrs():
            setattr(self, v, getattr(nc.variables[name], v))

    def __getitem__(self, n):
        return self._pf._get_variable(self._name, n)


class ParticleVariable:
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
    def __init__(self, filename):
        self.nc = Dataset(filename, mode="r")
        self.num_times = len(self.nc.dimensions["time"])
        self.variables = dict()
        self.instance_variables, self.particle_variables = [], []
        for key, var in self.nc.variables.items():
            if "particle_instance" in var.dimensions:
                self.instance_variables.append(key)
                self.variables[key] = InstanceVariable(self, key)
            elif "particle" in var.dimensions:
                self.particle_variables.append(key)
                self.variables[key] = ParticleVariable(self, key)
        self._count = self.nc.variables["particle_count"][:]
        self._start = np.concatenate(([0], np.cumsum(self._count[:-1])))

    def _get_variable(self, name, n):
        """Read an instance variable at given time"""
        # Må ha test, om name er variabel
        start = self._start[n]
        count = self._count[n]
        return self.nc.variables[name][start : start + count]
