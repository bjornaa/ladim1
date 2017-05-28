from typing import Dict, Any
import numpy as np


def timestep2stamp(config: Dict[str, Any], n: int) -> np.datetime64:
    """Convert from time step number to timestamp"""
    timestamp = config['start_time'] + n*np.timedelta64(config['dt'], 's')
    return timestamp


def timestamp2step(config: Dict[str, Any], timestamp: np.datetime64) -> int:
    # mtime = np.datetime64(timestamp)
    dtime = np.timedelta64(timestamp - config['start_time'], 's').astype(int)
    step = dtime // config['dt']
    return step
