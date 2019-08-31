from collections import namedtuple
from typing import List, Dict, Union
import numpy as np
import xarray as xr


class InstanceVariable:
    def __init__(self, data, pid, ptime, pcount):
        self.da = data
        self.pid = pid
        self.time = ptime
        self.count = pcount
        self.end = self.count.cumsum()
        self.start = self.end - self.count
        self.num_times = len(self.time)
        self.particles = np.unique(self.pid)
        self.num_particles = len(self.particles)  # Number of distinct particles

    def _sel_time_idx(self, n: int) -> xr.DataArray:
        """Select by time index, return xarray."""
        start = self.start[n]
        end = self.end[n]
        V = self.da[start:end]
        V = V.assign_coords(time=self.time[n])
        V = V.assign_coords(pid=self.pid[start:end])
        V = V.swap_dims({"particle_instance": "pid"})
        return V

    # # def _sel_time_idx2(self, n):
    #     # Glemmer strukturen og bygger opp på ny
    #     start = int(self.pf.start[n])
    #     end = int(self.pf.end[n])
    #     coords = {"time": self.pf.ds.time[n], "pid": self.pf.ds.pid[start:end].values}
    #     dims = ("pid",)
    #     return xr.DataArray(self.da[start:end].values, dims=dims, coords=coords)

    def _sel_time_slice_idx(self, tslice: slice) -> "InstanceVariable":
        """Take a time slice based on time indices"""
        n = self.num_times
        istart, istop, step = tslice.indices(n)
        if step != 1:
            raise IndexError("step > 1 is not allowed")
        start = self.start[istart]
        end = self.end[istop - 1]
        return InstanceVariable(
            data=self.da[start:end],
            pid=self.pid[start:end],
            ptime=self.time[tslice],
            pcount=self.count[tslice],
        )

    def _isel2(self, t_idx, pid_idx):
        """Value at time and pid index"""
        idx = int(self.pf.start[t_idx]) + pid_idx
        V = self.da[idx]
        V = V.assign_coords(time=self.pf.ds.time[t_idx])
        V = V.assign_coords(pid=self.pf.ds.pid[idx])
        # V = V.swap_dims({"particle_instance": "pid"})
        return V

    # Denne tar lengre tid,
    def _isel2b(self, t_idx, pid_idx):
        """Value at time and pid index"""
        return self._get_by_time(t_idx)[pid_idx]

    def _sel2(self, t_idx, pid):
        return self._get_by_time(t_idx).sel(pid=pid)

    def _sel_pid_value(self, pid):
        """Selection based on single pid value"""
        # Burde få en pid-koordinat også
        data = []
        times = []
        for t_idx in range(self.num_times):
            try:
                data.append(self._sel_time_idx(t_idx).sel(pid=pid))
                times.append(t_idx)
            except KeyError:
                pass
        # Bedre, på forhånd sjekk om pid > maximum
        if not data:
            raise KeyError(f"No such pid = {pid}")
        V = xr.DataArray(data, coords={"time": self.time[times]}, dims=("time",))
        V["pid"] = pid
        return V

    def _time_sel(self, time_label):
        time_idx = self.pf.time.indexes["time"].get_loc(time_label)
        return self._get_by_time(time_idx)

    def isel(self, *, pid=None, time=None):
        if pid is not None and time is None:
            pass
            # V = self._sel_pid_va(pid)
            # V["pid"] = pid
            # return V
        if time is not None and pid is None:
            return self._sel_time_idx(time)

    def sel(self, *, pid=None, time=None):
        if pid is not None and time is None:
            return self._sel_pid_value(pid)
        if time is not None and pid is None:
            return self._time_sel(time)

    def full(self):
        """Return a full DataArray"""
        data = np.empty((self.num_times, self.num_particles))
        data[:, :] = np.nan
        for n in range(self.num_times):
            # data[n, self.pid[n]] = self._sel_time_idx(n)
            data[n, self.pid[self.start[n] : self.end[n]]] = self._sel_time_idx(n)
        coords = dict(time=self.time, pid=self.particles)
        V = xr.DataArray(data=data, coords=coords, dims=("time", "pid"))
        return V

    def __getitem__(self, index):
        if isinstance(index, int):  # index = time_idx
            return self._sel_time_idx(index)
        if isinstance(index, slice):
            return self._sel_time_slice_idx(index)
        else:  # index = time_idx, pid
            time_idx, pid = index
            if 0 <= pid < self.num_particles:
                try:
                    v = self._sel_time_idx(time_idx).sel(pid=pid)
                except KeyError:
                    # Også håndtere v != floatpf.
                    v = np.nan
            else:
                raise IndexError(f"pid={pid} is out of bound={self.num_particles}")
            return v

    def __len__(self):
        return len(self.time)


# --------------------------------------------


Position = namedtuple("Position", "X Y")


class Trajectory(namedtuple("Trajectory", "X Y")):
    """Single particle trajectory"""

    @property
    def time(self):
        return self.X.time

    def __len__(self):
        return len(self.X.time)


# ---------------------------------------------


class Time:
    """Callable version of time DataArray

    For backwards compability, obsolete
    """

    def __init__(self, ptime):
        self._time = ptime

    def __call__(self, n):
        """Prettier version of self[n]"""
        return self._time[n].values.astype("M8[s]")

    def __getitem__(self, arg):
        return self._time[arg]

    def __repr__(self):
        return repr(self._time)

    def __str__(self):
        return repr(self._time)

    def __len__(self):
        return len(self._time)


# --------------------------------------


class ParticleFile:
    def __init__(self, filename: str):
        ds = xr.open_dataset(filename)
        self.ds = ds
        # End and start of segment with particles at a given time
        self.count = ds.particle_count.values
        self.end = self.count.cumsum()
        self.start = self.end - self.count
        self.num_times = len(self.count)
        self.time = Time(ds.time)
        self.num_particles = int(ds.pid.max()) + 1  # Number of particles

        # Extract instance and particle variables from the netCDF file
        self.instance_variables: List["InstanceVariable"] = []
        self.particle_variables: List["ParticleVariable"] = []
        self.variables: Dict[str, Union["InstanceVariable", "ParticleVariable"]] = {}
        for var in list(self.ds.variables):
            if "particle_instance" in self.ds[var].dims:
                self.instance_variables.append(var)
                self.variables[var] = InstanceVariable(
                    self.ds[var], self.ds.pid, self.ds.time, self.count
                )
            elif "particle" in self.ds[var].dims:
                self.particle_variables.append(var)
                # self.variables[key] = ParticleVariable(self, key)

    # For backwards compability
    # should it be a DataSet
    def position(self, n):
        return Position(self.X[n], self.Y[n])

    # For backwards compability
    # Could define ParticleDataset (from file)
    # This could slice and take trajectories og that
    # Could improve speed by computing X and Y at same time
    # def trajectory(self, pid):
    #     X = self["X"].sel(pid=pid)
    #     Y = self["Y"].sel(pid=pid)
    #     vars = {'X': X, 'Y': Y, 'time': X["time"]}
    #     return xr.Dataset(vars)
    def trajectory(self, pid):
        X = self["X"].sel(pid=pid)
        Y = self["Y"].sel(pid=pid)
        return Trajectory(X, Y)

    def __len__(self):
        return len(self.time)

    def __getattr__(self, var):
        return self.variables[var]
        # return InstanceVariable(self, self.ds[var])

    def __getitem__(self, var):
        return self.variables[var]

    def close(self) -> None:
        self.ds.close()

    # Make ParticleFile a context manager
    def __enter__(self):
        return self

    def __exit__(self, atype, value, traceback):
        self.close()
