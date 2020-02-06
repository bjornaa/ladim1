.. configuration:

:mod:`configuration` --- LADiM Configuration
============================================

.. module:: configuration
   :synopsis: LADiM configuration

LADiM's configuration system uses the :mod:`pyyaml` package to read the
configuration file. This allows comments, nested keywords,
and flexibility in the sequence of keywords, missing or extra keyword,

The configuration procedure makes a dictionary. It does not quite match the structure of
the yaml configuration file as some of the values are derived or default.
Presently the dictionary is somewhat inconsistent to provide backwards compatibility.
Future versions will continue to separate the configuration info into separate
directories for the gridforce, ibm and output modules.

start_time
  Start time for simulation,  [numpy.datetime64]
stop_time
  Stop time for simulation,   [numpy.datetime64]
reference_time
  Reference time for simulation,   [numpy.datetime64]
  Used in the units attribute in the netCDF output file
particle_release_file
  Name of particle release file
output_file
  Name of output file or template for sequence of output files
start
  Simulation start "cold" or "warm"
warm_start_file
  Name of warm start file (if needed)
dt
  Model time step in seconds [int]
simulation_time
  Simulation tile in seconds [int]
numsteps
  Number of time steps [int]
gridforce
  Gridforce module with configuration
  Dictionary of information to the gridforce module
input_file
  Name of input file or template for sequence of input files
ibm_forcing
  List of extra forcing variables beside velocity
ibm
  IBM module with configuration
ibm_variables:
  List of variables needed by the IBM module
ibm_module
  Path to the IBM module
release_type
  Type of particle release, "discrete" or "continuous".
release_format
  List of variables provided during particle release
release_dtype
  Dictionary with name -> type for the release variables
particle_variables
  Names of particle variables among the release variables
output_format
  NetCDF format for the output file
skip_initial
  Logical switch for skipping output of intitial field
output_numrec
  Number of time records per output file, zero means no output splitting
output_period
  Hours between output [int]
num_output
  Number of output time records
output_particle
  Particle variables included in output
output_instance
  Instance variables included in output
nc_attributes
  mapping: variable -> dictionary of netcdf attributes
advection
  Advection scheme, "EF" = Euler Forward, "RK2" = Runge-Kutta order 2,
  "RK4" = Runge-Kutta order 4
diffusion
  Logical switch for horizontal random walk diffusion
diffusion_coefficient
  Diffusion coefficient, constant [m/s**2]
