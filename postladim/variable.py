import datetime
from typing import Any, List, Dict, Union, Optional
import numpy as np  # type: ignore
import xarray as xr  # type: ignore

Timetype = Union[str, np.datetime64, datetime.datetime]
Array = Union[np.ndarray, xr.DataArray]


class InstanceVariable:
    def __init__(
        self,
        data: xr.DataArray,
        pid: xr.DataArray,
        ptime: xr.DataArray,
        pcount: np.ndarray,
    ) -> None:
        self.da = data
        self.pid = pid
        self.time = ptime
        self.count = pcount
        self.end = self.count.cumsum()
        self.start = self.end - self.count
        self.num_times = len(self.time)
        self.particles = np.unique(self.pid)
        self.num_particles = len(self.particles)  # Number of distinct particles

    # @property
    # def end(self) -> np.ndarray:
    #    return self.count.cumsum()

    # @property
    # def start(self) -> np.ndarray:
    #    return self.end - self.count

    @property
    def values(self) -> np.ndarray:
        # Same as self.da.values
        return np.array(self.da)

    def _sel_time_index(self, n: int) -> xr.DataArray:
        """Select by time index, return xarray."""
        start = self.start[n]
        end = self.end[n]
        V = self.da[start:end]
        V = V.assign_coords(time=self.time[n])
        V = V.assign_coords(pid=self.pid[start:end])
        V = V.swap_dims({"particle_instance": "pid"})
        return V

    def _sel_time_slice_index(self, tslice: slice) -> "InstanceVariable":
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

    def _sel_time_value(self, time_val: Timetype) -> xr.DataArray:
        idx = self.time.get_index("time").get_loc(time_val)
        return self._sel_time_index(idx)

    def _sel_pid_value(self, pid: int) -> xr.DataArray:
        """Selection based on single pid value"""
        # Burde få en pid-koordinat også
        data = []
        times = []
        for t_idx in range(self.num_times):
            try:
                data.append(self._sel_time_index(t_idx).sel(pid=pid))
                times.append(t_idx)
            except KeyError:
                pass
        # Bedre, på forhånd sjekk om pid > maximum
        if not data:
            raise KeyError(f"No such pid = {pid}")
        V = xr.DataArray(data, coords={"time": self.time[times]}, dims=("time",))
        V["pid"] = pid
        return V

    # def isel(self, *, time: Optional[int] = None) -> xr.DataArray:
    #     if time is not None:
    #         return self._sel_time_index(time)
    #     else:
    #         raise ValueError("Need one argument")
    def isel(self, *, time: int) -> xr.DataArray:
        return self._sel_time_index(time)

    def sel(
        self, *, pid: Optional[int] = None, time: Optional[Timetype] = None
    ) -> xr.DataArray:
        """Select from InstanceVariable by value of pid or time or both"""
        if pid is not None and time is None:
            return self._sel_pid_value(pid)
        if time is not None and pid is None:
            return self._sel_time_value(time)
        if time is not None and pid is not None:
            return self._sel_time_value(time).sel(pid=pid)
        # No arguments
        raise ValueError("Need 1 or 2 arguments")

    # Do something like dask if the array gets to big
    def full(self) -> xr.DataArray:
        """Return a full DataArray"""
        data = np.empty((self.num_times, self.num_particles))
        data[:, :] = np.nan
        for n in range(self.num_times):
            data[n, self.pid[self.start[n] : self.end[n]]] = self._sel_time_index(n)
        # coords = dict(time=self.time, pid=self.particles)
        coords = [("time", self.time), ("pid", self.particles)]
        V = xr.DataArray(data=data, coords=coords, dims=("time", "pid"))
        return V

    # More complicated typing
    # def __getitem__(self, index: Union[int, slice]) -> xr.DataArray:
    def __getitem__(
        self, index: Union[int, slice]
    ) -> Union[xr.DataArray, "InstanceVariable"]:
        if isinstance(index, int):  # index = time_idx
            return self._sel_time_index(index)
        if isinstance(index, slice):
            return self._sel_time_slice_index(index)
        else:  # index = time_idx, pid
            time_idx, pid = index
            if 0 <= pid < self.num_particles:
                try:
                    v = self._sel_time_index(time_idx).sel(pid=pid)
                except KeyError:
                    # Også håndtere v != floatpf.
                    v = np.nan
            else:
                raise IndexError(f"pid={pid} is out of bound={self.num_particles}")
            return v

    def __array__(self) -> np.ndarray:
        return np.array(self.da)

    def __repr__(self) -> str:
        s = "<postladim.InstanceVariable>\n"
        s += f"num_times: {self.num_times}, particle_instance: {len(self.da)}\n"
        s += arraystr(self.da)
        return s

    def __len__(self) -> int:
        return len(self.time)


# --------------------------------------------

# Need this?, just use the DataArray
class ParticleVariable:
    """Particle variable, time-independent"""

    # def __init__(self, particlefile: "ParticleFile", varname: str) -> None:
    def __init__(self, data: xr.DataArray) -> None:
        self.da = data

    def __getitem__(self, p: int) -> Any:
        """Get the value of particle with pid = p
        """
        return self.da[p]

    def __array__(self) -> np.ndarray:
        return np.array(self.da)

    def __repr__(self) -> str:
        s = "<postladim.ParticleVariable>\n"
        s += f"particle: {len(self.da)}\n"
        s += arraystr(self.da)
        return s

    def __len__(self) -> int:
        return len(self.da)


def itemstr(v: Array) -> str:
    """Pretty print array item"""

    # Date
    if str(v.dtype).startswith("datetime64"):
        return str(v.__array__()).rstrip("0.:T")

    # Number
    return f"{v:g}"


def arraystr(A: Array) -> str:
    """Pretty print array"""
    B = np.asarray(A).ravel()
    if len(B) <= 3:
        return " ".join([itemstr(v) for v in B])
    return " ".join([itemstr(B[0]), itemstr(B[1]), "...", itemstr(B[-1])])
