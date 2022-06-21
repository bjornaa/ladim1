"""
General utilities for LADiM
"""

from typing import Any, Dict, List
import numpy as np


def timestep2stamp(config: Dict[str, Any], n: int) -> np.datetime64:
    """Convert from time step number to timestamp"""
    timestamp = config["start_time"] + n * np.timedelta64(config["dt"], "s")
    return timestamp


def timestamp2step(config: Dict[str, Any], timestamp: np.datetime64) -> int:
    """Convert from timestamp to time step number"""
    # mtime = np.datetime64(timestamp)
    dtime = np.timedelta64(timestamp - config["start_time"], "s").astype(int)
    step = dtime // config["dt"]
    return step


# Utility function to test for position in grid
def ingrid(x: float, y: float, subgrid: List[int]) -> bool:
    """Check if position (x, y) is in a subgrid"""
    i0, i1, j0, j1 = subgrid
    return (i0 <= x) & (x <= i1 - 1) & (j0 <= y) & (y <= j1 - 1)
