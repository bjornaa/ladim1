"""
Configuration module for ladim
"""

# ----------------------------------
# Bjørn Ådlandsvik <bjorn@imr.no>
# Institute of Marine Research
# 2017-01-17
# ----------------------------------

# import datetime
import logging
from typing import Dict, Any
import numpy as np
import yaml
import yaml.parser
from netCDF4 import Dataset, num2date

Config = Dict[str, Any]  # type of the config dictionary


def configure_ibm(conf: Dict[str, Any]) -> Config:
    """Configure the IBM module

    Input: Raw conf dictionary from configuration file

    Return: Dictionary with IBM configuration

    If an IBM is used, check that module name is present
    Special treatment for the variables item
    Other items are stored for the IBM module
    """

    logging.info("Configuration: IBM")
    if conf is None:  # No ibm section
        return {}
    D = conf.get("ibm")  # Empty ibm section
    if D is None:
        return {}

    # Mandatory: module name (or obsolete ibm_module)
    if "module" not in D:
        if "ibm_module" in D:
            D["module"] = D.pop("ibm_module")
        else:
            logging.error("No IBM module specified")
            raise SystemExit(1)
    logging.info(f'    {"module":15s}: {D["module"]}')

    # The variables item
    if "variables" not in D:
        if "ibm_variables" in D:
            D["variables"] = D.pop("ibm_variables")
        # ibm_variables may live under state (obsolete)
        elif "state" in conf and conf["state"] is not None:
            if "ibm_variables" in conf.get("state", dict()):
                D["variables"] = conf["state"]["ibm_variables"]
        else:
            D["variables"] = []

    for key in D:
        if key != "module":
            logging.info(f"    {key:15s}: {D[key]}")

    return D


def configure_gridforce(conf: Dict[str, Any]) -> Config:
    """Parse gridforce related info and pass on

    Input: raw conf dictionary from configuration file

    Return: dictionary with gridforce configuration

    """
    logging.info("Configuration: gridforce")
    if conf is None:
        logging.error("No gridforce section in configuration file")
        raise SystemExit(1)
    D = conf.get("gridforce")
    if D is None:
        logging.error("Empty gridforce section in configuration file")
        raise SystemExit(1)

    # module is the only mandatory field
    if "module" not in D:
        logging.error("No gridforce module specified")
        raise SystemExit(1)
    logging.info(f'    {"module":15s}: {D["module"]}')

    # Backwards compability (for ROMS.py)
    if "files" in conf and conf["files"] is not None:
        if "grid_file" in conf["files"]:
            # Give grid_file under gridforce highest priority
            if "grid_file" not in D:
                D["grid_file"] = conf["files"]["grid_file"]
        if "input_file" in conf["files"]:
            # Give input_file under gridforce highest priority
            if "input_file" not in D:
                D["input_file"] = conf["files"]["input_file"]

    for key in D:
        if key != "module":
            logging.info(f"    {key:15s}: {D[key]}")

    return D


def configure_time(conf: Dict[str, Any]) -> Config:
    """Parse time configuration"""

    # Times are returned with dtype M8[s]

    logging.info("Configuration: Time Control")

    D0 = conf.get("time_control")
    if D0 is None:
        logging.critical("No time_control section in configuration file")
        raise SystemExit(1)
    if len(D0) is None:
        logging.critical("Empty time_control section in configuration file")
        raise SystemExit(1)

    D = dict()
    for name in ["start_time", "stop_time"]:
        val = D0.get(name)
        if not val:
            logging.critical(f"No {name} in time_control")
            raise SystemExit(1)
        D[name] = np.datetime64(val).astype("M8[s]")
        logging.info(f"    {name.replace('_', ' '):15s}: {D[name]}")
    # reference_time, default = start_time
    D["reference_time"] = np.datetime64(
        D0.get("reference_time", D["start_time"])
    ).astype("M8[s]")
    logging.info(f'    {"reference time":15s}: {D["reference_time"]}')

    # D['simulation_time'] = D['start_time'] - D['stop_time']
    # D['simulation_time'] = int(sim_time / np.timedelta64(1, 's'))

    return D


def configure_output(
    conf: Dict[str, Any], time_config: Dict[str, np.datetime64]
) -> Config:
    """Parse output related info and pass on

    Input: conf = raw configuration dictionary
           time_config = parsed time_control configuration

    Return: D = output configuration dictionary

    NOTE: time_control should be parsed before output

    """

    logging.info("Configuration: Output Control")

    if conf is None:
        logging.error("No output section in configuration file")
        raise SystemExit(1)
    D0 = conf.get("output") or conf.get("output_variables")
    if D0 is None:
        logging.error("Empty output section in configuration file")
        raise SystemExit(1)

    D = {}
    # Set in defaults
    D["format"] = D0.get("format", "NETCDF3_64BIT_OFFSET")
    logging.info(f'    {"format":15s}: {D["format"]}')

    # Skip output of initial state, useful for restart
    # with cold start the default is False
    # with warm start, the default is true
    D["skip_initial"] = D0.get("skip_initial_output", bool(conf.get("warm_start_file")))
    logging.info(f"    {'Skip inital output':15s}: {D['skip_initial']}")

    D["numrec"] = D0.get("numrec", 0)
    logging.info(f'    {"numrec":15s}: {D["numrec"]}')

    # Time info
    dt = np.timedelta64(*(conf["numerics"]["dt"]))
    simulation_time = time_config["stop_time"] - time_config["start_time"]

    outper = np.timedelta64(*D0["outper"])  # raw output period
    logging.info(
        f'    {"output_period":15s}: {outper.item().total_seconds()/3600} hours'
    )

    D["num_output"] = 1 + simulation_time // outper  # Add 1 ??
    logging.info(f'    {"num_output":15s}: {D["num_output"]}')

    period, remainder = divmod(outper, dt)
    if remainder != np.timedelta64(0, "s"):
        logging.error("Output period not divisible by time step")
        raise SystemExit(1)
    D["output_period"] = period  # output period in timesteps

    D["particle"] = D0["particle"]
    D["instance"] = D0["instance"]
    D["variables"] = dict()
    for name in D["particle"] + D["instance"]:
        # value = D0[name]
        value = D0[name]
        if "units" in value:
            if value["units"] == "seconds since reference_time":
                value["units"] = f"seconds since {time_config['reference_time']}"
        D["variables"][name] = D0[name]
    logging.info("    particle variables")
    for name in D["particle"]:
        logging.info(8 * " " + name)
        for item in D["variables"][name].items():
            logging.info(12 * " " + "{:11s}: {:s}".format(*item))
    logging.info("    particle instance variables")
    for name in D["instance"]:
        logging.info(8 * " " + name)
        for item in D["variables"][name].items():
            logging.info(12 * " " + "{:11s}: {:s}".format(*item))

    return D


def configure_release(conf: Dict[str, Any]) -> Config:
    """Parse time configuration"""

    # Times are returned with dtype M8[s]

    logging.info("Configuration: Release")

    D0 = conf["particle_release"]
    D = dict()

    # Release file (may be in obsolete files section)
    D["release_file"] = (
        D0.get("particle_release_file") or conf["files"]["particle_release_file"]
    )

    # Default release type is discrete
    D["release_type"] = D0.get("release_type") or "discrete"
    logging.info(f'    {"release_type":15s}: {D["release_type"]}')

    if D["release_type"] == "continuous":
        D["release_frequency"] = np.timedelta64(*D0["release_frequency"])
        logging.info(f'    {"release_frequency":11s}: {str(D["release_frequency"])}')

    D["release_format"] = D0["variables"]
    D["release_dtype"] = dict()
    # Map from str to converter
    type_mapping = dict(int=int, float=float, time=np.datetime64, str=str)
    for name in D["release_format"]:
        D["release_dtype"][name] = type_mapping[D0.get(name, "float")]
        logging.info(f'    {name:15s}: {D["release_dtype"][name]}')
        D["particle_variables"] = D0["particle_variables"]

    return D


# ---------------------------------------


def configure(config_stream) -> Config:
    """The main configuration handling function

    Input: Name of configuration file in yaml format

    Returns: Configuration dictionary

    """

    config: Config = dict()

    # --- Read the configuration file ---
    try:
        conf = yaml.safe_load(config_stream)
    except yaml.parser.ParserError:
        logging.critical("Can not parse configuration")
        raise SystemExit(2)

    # ----------------
    # Time control
    # ----------------
    config["time_control"] = configure_time(conf)

    # -------------
    # Files
    # -------------
    logging.info("Configuration: Files")
    logging.info(f'    {"config_stream":15s}: {config_stream}')
    #for name in ["particle_release_file", "output_file"]:
    #    config[name] = conf["files"][name]
    #    logging.info(f"    {name:15s}: {config[name]}")
    for name in ["output_file"]:
        config[name] = conf["files"][name]
        logging.info(f"    {name:15s}: {config[name]}")

    try:
        config["warm_start_file"] = conf["files"]["warm_start_file"]
        config["start"] = "warm"
        logging.info(f'    {"Warm start from":15s}: {config["warm_start_file"]}')
    except KeyError:
        config["start"] = "cold"
        config["warm_start_file"] = ""

    # Override start time for warm start
    if config["start"] == "warm":
        try:
            nc = Dataset(config["warm_start_file"])
        except (FileNotFoundError, OSError):
            logging.error(f"Could not open warm start file,{config['warm_start_file']}")
            raise SystemExit(1)
        tvar = nc.variables["time"]
        # Use last record in restart file
        warm_start_time = np.datetime64(num2date(tvar[-1], tvar.units))
        warm_start_time = warm_start_time.astype("M8[s]")
        config["time_control"]["start_time"] = warm_start_time
        logging.info(f"    Warm start at {warm_start_time}")

        # Variables needed by restart, mightwarm_ be changed
        # default should be instance variables among release variables
        try:
            warm_start_variables = conf["state"]["warm_start_variables"]
        except KeyError:
            warm_start_variables = ["X", "Y", "Z"]
        config["warm_start_variables"] = warm_start_variables

    # --- Time stepping ---
    logging.info("Configuration: Time Stepping")
    # Read time step and convert to seconds
    dt = np.timedelta64(*tuple(conf["numerics"]["dt"]))
    config["dt"] = int(dt.astype("m8[s]").astype("int"))
    config["simulation_time"] = np.timedelta64(
        config["time_control"]["stop_time"] - config["time_control"]["start_time"], "s"
    ).astype("int")
    config["numsteps"] = config["simulation_time"] // config["dt"]
    logging.info(f'    {"dt":15s}: {config["dt"]} seconds')
    logging.info(
        f'    {"simulation time":15s}: {config["simulation_time"] // 3600} hours'
    )
    logging.info(f'    {"number of time steps":15s}: {config["numsteps"]}')

    #  --- Grid ---
    config["gridforce"] = configure_gridforce(conf)

    # --- Forcing ---
    try:
        config["ibm_forcing"] = conf["gridforce"]["ibm_forcing"]
    except (KeyError, TypeError):
        config["ibm_forcing"] = []
    logging.info(f'    {"ibm_forcing":15s}: {config["ibm_forcing"]}')

    # --- IBM ---

    config["ibm"] = configure_ibm(conf)
    # Make obsolete
    config["ibm_variables"] = config["ibm"].get("variables", [])
    config["ibm_module"] = config["ibm"].get("module")

    # --- Particle release ---
    config["release"] = configure_release(conf)


    # logging.info("Configuration: Particle Releaser")
    # prelease = conf["particle_release"]
    # try:
    #     config["release_type"] = prelease["release_type"]
    # except KeyError:
    #     config["release_type"] = "discrete"
    # logging.info(f'    {"release_type":15s}: {config["release_type"]}')
    # if config["release_type"] == "continuous":
    #     config["release_frequency"] = np.timedelta64(
    #         *tuple(prelease["release_frequency"])
    #     )
    #     logging.info(
    #         f'    {"release_frequency":11s}: {str(config["release_frequency"])}'
    #     )
    # config["release_format"] = conf["particle_release"]["variables"]
    # config["release_dtype"] = dict()
    # # Map from str to converter
    # type_mapping = dict(int=int, float=float, time=np.datetime64, str=str)
    # for name in config["release_format"]:
    #     config["release_dtype"][name] = type_mapping[
    #         conf["particle_release"].get(name, "float")
    #     ]
    #     logging.info(f'    {name:15s}: {config["release_dtype"][name]}')
    # config["particle_variables"] = prelease["particle_variables"]

    # --- Model state ---
    # logging.info("Configuration: Model State Variables")

    # -----------------
    # Output control
    # -----------------
    config["output"] = configure_output(conf, config["time_control"])

    # --- Numerics ---

    # dt belongs here, but is already read
    logging.info("Configuration: Numerics")
    try:
        config["advection"] = conf["numerics"]["advection"]
    except KeyError:
        config["advection"] = "RK4"
    logging.info(f'    {"advection":15s}: {config["advection"]}')
    try:
        diffusion = conf["numerics"]["diffusion"]
    except KeyError:
        diffusion = 0.0
    if diffusion > 0:
        config["diffusion"] = True
        config["diffusion_coefficient"] = diffusion
        logging.info(
            f'    {"diffusion coefficient":15s}: {config["diffusion_coefficient"]}'
        )
    else:
        config["diffusion"] = False
        logging.info("    no diffusion")

    return config
