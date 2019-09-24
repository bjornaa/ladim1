"""
Configuration class for ladim
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


# ---------------------------------------


def configure(config_stream) -> Config:
    """The main configuration handling function

    Input: Name of configuration file in yaml format

    Returns: Configuration dictionary

    """

    config: Config = dict()

    # --- Read the configuration file ---
    # TODO: use logging.ERROR instead of print

    try:
        conf = yaml.safe_load(config_stream)
    except yaml.parser.ParserError:
        print("ERROR: ", f"Can not parse configuration")
        raise SystemExit(2)

    # ----------------
    # Time control
    # ----------------
    logging.info("Configuration: Time Control")
    for name in ["start_time", "stop_time"]:
        config[name] = np.datetime64(conf["time_control"][name]).astype("M8[s]")
        logging.info(f"    {name.replace('_', ' '):15s}: {config[name]}")
    # reference_time, default = start_time
    config["reference_time"] = np.datetime64(
        conf["time_control"].get("reference_time", config["start_time"])
    ).astype("M8[s]")
    logging.info(f'    {"reference time":15s}: {config["reference_time"]}')

    # -------------
    # Files
    # -------------
    logging.info("Configuration: Files")
    logging.info(f'    {"config_stream":15s}: {config_stream}')
    for name in ["particle_release_file", "output_file"]:
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
        config["start_time"] = warm_start_time
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
        config["stop_time"] - config["start_time"], "s"
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
    logging.info("Configuration: Particle Releaser")
    prelease = conf["particle_release"]
    try:
        config["release_type"] = prelease["release_type"]
    except KeyError:
        config["release_type"] = "discrete"
    logging.info(f'    {"release_type":15s}: {config["release_type"]}')
    if config["release_type"] == "continuous":
        config["release_frequency"] = np.timedelta64(
            *tuple(prelease["release_frequency"])
        )
        logging.info(
            f'    {"release_frequency":11s}: {str(config["release_frequency"])}'
        )
    config["release_format"] = conf["particle_release"]["variables"]
    config["release_dtype"] = dict()
    # Map from str to converter
    type_mapping = dict(int=int, float=float, time=np.datetime64, str=str)
    for name in config["release_format"]:
        config["release_dtype"][name] = type_mapping[
            conf["particle_release"].get(name, "float")
        ]
        logging.info(f'    {name:15s}: {config["release_dtype"][name]}')
    config["particle_variables"] = prelease["particle_variables"]

    # --- Model state ---
    # logging.info("Configuration: Model State Variables")

    # -----------------
    # Output control
    # -----------------
    logging.info("Configuration: Output Control")
    try:
        output_format = conf["output_variables"]["format"]
    except KeyError:
        output_format = "NETCDF3_64BIT_OFFSET"
    config["output_format"] = output_format
    logging.info(f'    {"output_format":15s}: {config["output_format"]}')

    # Skip output of initial state, useful for restart
    # with cold start the default is False
    # with warm start, the default is true
    try:
        skip_initial = conf["output_variables"]["skip_initial_output"]
    except KeyError:
        if config["start"] == "warm":
            skip_initial = True
        else:
            skip_initial = False
    config["skip_initial"] = skip_initial
    logging.info(f"    {'Skip inital output':15s}: {skip_initial}")

    try:
        numrec = conf["output_variables"]["numrec"]
    except KeyError:
        numrec = 0
    config["output_numrec"] = numrec
    logging.info(f'    {"output_numrec":15s}: {config["output_numrec"]}')

    outper = np.timedelta64(*tuple(conf["output_variables"]["outper"]))
    outper = outper.astype("m8[s]").astype("int") // config["dt"]
    config["output_period"] = outper
    logging.info(f'    {"output_period":15s}: {config["output_period"]} timesteps')
    config["num_output"] = 1 + config["numsteps"] // config["output_period"]
    logging.info(f'    {"numsteps":15s}: {config["numsteps"]}')
    config["output_particle"] = conf["output_variables"]["particle"]
    config["output_instance"] = conf["output_variables"]["instance"]
    config["nc_attributes"] = dict()
    for name in config["output_particle"] + config["output_instance"]:
        value = conf["output_variables"][name]
        if "units" in value:
            if value["units"] == "seconds since reference_time":
                timeref = str(config["reference_time"]).replace("T", " ")
                value["units"] = f"seconds since {timeref}"
        config["nc_attributes"][name] = conf["output_variables"][name]
    logging.info("    particle variables")
    for name in config["output_particle"]:
        logging.info(8 * " " + name)
        for item in config["nc_attributes"][name].items():
            logging.info(12 * " " + "{:11s}: {:s}".format(*item))
    logging.info("    particle instance variables")
    for name in config["output_instance"]:
        logging.info(8 * " " + name)
        for item in config["nc_attributes"][name].items():
            logging.info(12 * " " + "{:11s}: {:s}".format(*item))

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
